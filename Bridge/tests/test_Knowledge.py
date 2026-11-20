import itertools

import numpy as np
import pytest

from ..Card import ALL_CARDS, Card
from ..Deck import Deck
from ..Hand import Hand
from ..Knowledge import Knowledge
from ..Position import Position
from ..Round import Round, countingHigh, simpleHigh
from ..Suit import Suit
from ..Table import Table
from ..Trick import Trick


def make_hand(codes):
    return Hand([Card.fromCode(c) for c in codes.split()])


HAND = 'As Ks 5s 2s Qh Jh 4h Kd 6d 3d 7c 5c Jc'


# ---------------------------------------------------------------------------------------------- Hand history
def test_hand_remembers_what_it_was_dealt_and_what_it_played():
    h = make_hand(HAND)
    original = tuple(h)
    assert h.original == original and h.played == []
    h.play(Card.fromCode('Ks'))
    h.play(Card.fromCode('5c'))
    assert h.played == [Card.fromCode('Ks'), Card.fromCode('5c')]
    assert len(h) == 11 and Card.fromCode('Ks') not in h
    assert h.original == original  # the deal does not change
    assert h.get_suit('spades') == [Card.fromCode('As'), Card.fromCode('5s'), Card.fromCode('2s')]


def test_remove_does_not_count_as_playing():
    h = make_hand(HAND)
    h.remove(Card.fromCode('Ks'))
    assert h.played == [] and len(h) == 12


def test_playing_a_card_that_is_not_there():
    h = make_hand(HAND)
    with pytest.raises(ValueError):
        h.play(Card.fromCode('2h'))
    assert h.played == [] and len(h) == 13


def test_a_new_hand_has_its_own_history():
    a, b = make_hand(HAND), make_hand(HAND)
    a.play(Card.fromCode('As'))
    assert b.played == [] and len(b.original) == 13


# ---------------------------------------------------------------------------------------------- Knowledge basics
def table_knowledge():
    """north's view with south as dummy, an unshuffled deck, so the hands are known"""
    hands = list(Deck().deal())
    return hands, Knowledge('north', hands[0])


def test_unseen_cards_start_as_everything_but_my_hand():
    hands, k = table_knowledge()
    assert len(k.unseen()) == 39
    assert not set(hands[0].original) & set(k.unseen())
    assert k.hidden_seats() == ['east', 'south', 'west']
    assert [k.cards_left(p) for p in Position.positions] == [13, 13, 13, 13]


def test_unseen_by_suit_highest_first():
    _, k = table_knowledge()
    hearts = k.unseen('hearts')
    assert [c.rank for c in hearts] == sorted([c.rank for c in hearts], reverse=True)
    assert all(c.suit == 'hearts' for c in hearts)
    assert k.unseen(Suit('hearts')) == hearts
    assert k.highest_unseen('hearts') == Card.fromCode('Ah')  # north (unshuffled) holds 2h 6h 0h AH? check below
    assert k.highest_unseen('hearts') in hearts


def test_observe_marks_cards_and_voids():
    hands, k = table_knowledge()
    east = hands[1][0]  # a card east holds
    k.observe('east', east)  # east leads it
    assert east not in k.unseen() and k.cards_left('east') == 12
    assert not k.is_void('east', east.suit)
    off_suit = next(c for c in hands[2] if c.suit != east.suit)
    k.observe('south', off_suit, east.suit)  # south does not follow suit
    assert k.is_void('south', east.suit) and k.is_void('south', east.suit.suit)
    on_suit = next(c for c in hands[3] if c.suit == east.suit)
    k.observe('west', on_suit, east.suit)  # west follows
    assert not k.is_void('west', east.suit)


def test_reveal_makes_a_hand_known():
    hands, k = table_knowledge()
    k.reveal('south', hands[2])
    assert len(k.unseen()) == 26 and k.hidden_seats() == ['east', 'west']
    assert not set(hands[2].original) & set(k.unseen())


def test_outstanding_includes_the_opponents_cards_on_the_table():
    hands, _ = table_knowledge()
    defender = Knowledge('east', hands[1])
    defender.reveal('north', hands[0])  # the dummy, an opponent of east
    mine = Knowledge('south', hands[2])
    mine.reveal('north', hands[0])  # south's own side
    spades_in_dummy = [c for c in hands[0] if c.suit == 'spades']
    assert all(c in defender.outstanding('spades') for c in spades_in_dummy)
    assert not any(c in mine.outstanding('spades') for c in spades_in_dummy)


def test_masters():
    k = Knowledge('north', make_hand('As 0s 9s 2s Ah 5h 6d 3d Kc 9c 8c 7c 4c'))
    assert k.is_master(Card.fromCode('As'))
    assert not k.is_master(Card.fromCode('0s'))  # the king, queen and jack of spades are still out
    assert not k.is_master(Card.fromCode('Kc'))  # the ace of clubs is out
    for seat, code in (('east', 'Ks'), ('south', 'Qs'), ('west', 'Js')):
        k.observe(seat, Card.fromCode(code))
    assert k.is_master(Card.fromCode('0s'))  # everything above the ten has been played
    k.observe('east', Card.fromCode('Ac'))
    assert k.is_master(Card.fromCode('Kc'))


# ---------------------------------------------------------------------------------------------- exact probabilities
def play_some_tricks(seed, n_tricks, declarer='south'):
    """a round of countingHigh in progress: (round, knowledge of every seat)"""
    hands = list(Deck(shuffle=3, rng=seed).deal())
    rnd = Round(Table(), hands, 'hearts', [countingHigh] * 4, declarer=declarer)
    leader = Position.index2pos(declarer, 1)
    for _ in range(n_tricks):
        leader = rnd.play_trick(leader)[1]
    return rnd


def brute_force(k, seat, card):
    """P(seat holds card) by listing every deal of the unseen cards to the two hidden hands"""
    a, b = k.hidden_seats()
    other = b if seat == a else a
    unseen = k.unseen()
    with_card = total = 0
    for chosen in itertools.combinations(range(len(unseen)), k.cards_left(seat)):
        mine = [unseen[i] for i in chosen]
        theirs = [c for i, c in enumerate(unseen) if i not in set(chosen)]
        if any(c.suit_index in k.voids[seat] for c in mine) or any(c.suit_index in k.voids[other] for c in theirs):
            continue
        total += 1
        with_card += card in mine
    return with_card / total


@pytest.mark.parametrize('seed', range(6))
def test_exact_probability_matches_every_possible_deal(seed):
    rnd = play_some_tricks(seed, 7)
    for k in rnd.knowledge:
        hidden = k.hidden_seats()
        assert len(hidden) == 2
        unseen = k.unseen()
        assert len(unseen) <= 14  # small enough to list every way to deal them
        for seat in hidden:
            total = 0.0
            for card in unseen:
                p = k.probability_holds(seat, card)
                assert p == pytest.approx(brute_force(k, seat, card))
                total += p
            assert total == pytest.approx(k.cards_left(seat))  # the expected number of unseen cards it holds
        for card in unseen:  # each unseen card is in exactly one hidden hand
            assert sum(k.probability_holds(s, card) for s in hidden) == pytest.approx(1.0)


def test_vacant_places():
    rnd = play_some_tricks(1, 7)
    for k in rnd.knowledge:
        a, b = k.hidden_seats()
        free = len(k.unseen()) - sum(  # the unseen cards that are not forced into one hand
            card.suit_index in k.voids[b] or card.suit_index in k.voids[a] for card in k.unseen())
        assert k.vacant_places(a) + k.vacant_places(b) == free


def test_early_in_the_play_every_unseen_card_is_equally_likely_in_either_hidden_hand():
    """declarer, before any card is played: partner's two opponents each hold a card with probability 1/2"""
    hands = list(Deck(shuffle=3, rng=3).deal())
    k = Knowledge('south', hands[2])
    k.reveal('north', hands[0])
    assert k.probability_holds('east', k.unseen()[0]) == pytest.approx(0.5)
    assert k.vacant_places('west') == 13


def test_a_void_makes_the_other_hand_certain():
    hands = list(Deck(shuffle=3, rng=3).deal())
    k = Knowledge('south', hands[2])
    k.reveal('north', hands[0])
    spade = k.unseen('spades')[0]
    k.voids['east'].add(spade.suit_index)  # east has shown out of spades
    assert k.probability_holds('west', spade) == 1.0 and k.probability_holds('east', spade) == 0.0


def test_probability_errors():
    hands = list(Deck(shuffle=3, rng=3).deal())
    k = Knowledge('south', hands[2])
    with pytest.raises(NotImplementedError):  # three hidden hands
        k.probability_holds('east', k.unseen()[0])
    with pytest.raises(NotImplementedError):
        k.vacant_places('east')
    k.reveal('north', hands[0])
    with pytest.raises(ValueError):  # north is not hidden
        k.probability_holds('north', k.unseen()[0])
    with pytest.raises(ValueError):  # one of my own cards
        k.probability_holds('east', hands[2][0])
    spade = k.unseen('spades')[0]
    k.voids['east'].add(spade.suit_index)
    k.voids['west'].add(spade.suit_index)  # nobody can hold it
    with pytest.raises(ValueError, match='inconsistent'):
        k.probability_holds('east', k.unseen('hearts')[0])
    k2 = Knowledge('south', hands[2])
    k2.reveal('north', hands[0])
    k2.played['east'].append(hands[2][0])  # east is said to have played one of south's own cards: 25 cards for 26 unseen
    with pytest.raises(ValueError, match='inconsistent'):
        k2.probability_holds('east', k2.unseen()[0])


# ---------------------------------------------------------------------------------------------- the round with counting
def test_a_round_with_counting_players_keeps_everyone_informed():
    hands = list(Deck(shuffle=3, rng=5).deal())
    rnd = Round(Table(), hands, 'spades', [countingHigh] * 4, declarer='south')
    assert rnd.dummy == 'north' and rnd.knowledge is not None
    assert all(logic.knowledge is k for logic, k in zip(rnd.logics, rnd.knowledge))
    rnd.play_trick('west')
    for seat, k in zip(Position.positions, rnd.knowledge):
        assert sum(len(v) for v in k.played.values()) == 4  # everyone saw the four cards
        assert k.cards_left(seat) == 12
    south, north, east = rnd.knowledge[2], rnd.knowledge[0], rnd.knowledge[1]
    assert 'north' in south.revealed and 'north' in east.revealed and 'north' not in north.revealed
    assert 'south' in north.revealed  # declarer and dummy see each other's hands
    assert 'north' in rnd.knowledge[3].revealed


def test_the_dummy_goes_down_after_the_opening_lead_not_before():
    hands = list(Deck(shuffle=3, rng=5).deal())
    rnd = Round(Table(), hands, 'spades', [countingHigh] * 4, declarer='south')
    assert rnd.knowledge[1].revealed == {}
    trick = Trick('west', 'spades')
    lead = rnd.logics[3].lead()  # west's opening lead is made with the dummy still hidden
    assert 'north' not in rnd.logics[3].knowledge.revealed and lead in hands[3]
    rnd.play_trick('west')
    assert 'north' in rnd.knowledge[1].revealed and trick.leader == 'west'


def test_default_leader_is_left_of_declarer_or_north():
    for declarer, first in (('north', 'east'), ('east', 'south'), ('south', 'west'), ('west', 'north')):
        rnd = Round(Table(), list(Deck(shuffle=3, rng=1).deal()), 'notrump', [simpleHigh] * 4, declarer=declarer)
        rnd.play()
        assert rnd.tricks[0].leader == first
    rnd = Round(Table(), list(Deck(shuffle=3, rng=1).deal()), 'notrump', [simpleHigh] * 4)
    rnd.play()
    assert rnd.tricks[0].leader == 'north' and rnd.declarer is None and rnd.dummy is None and rnd.knowledge is None


def test_counting_without_a_declarer_shows_no_dummy():
    rnd = Round(Table(), list(Deck(shuffle=3, rng=2).deal()), 'clubs', [countingHigh] * 4)
    rnd.play()
    assert all(k.revealed == {} for k in rnd.knowledge)


@pytest.mark.parametrize('trump', ['spades', 'hearts', 'diamonds', 'clubs', 'notrump'])
def test_a_full_round_of_counting_players(trump):
    for seed in range(5):
        hands = list(Deck(shuffle=3, rng=seed).deal())
        rnd = Round(Table(), hands, trump, [countingHigh] * 4, declarer='east')
        ns, ew = rnd.play()
        assert ns + ew == 13 and all(len(h) == 0 for h in hands)
        for hand in hands:
            assert sorted(c.code for c in hand.played) == sorted(c.code for c in hand.original)
        for k in rnd.knowledge:
            assert k.unseen() == [] and all(k.cards_left(s) == 0 for s in Position.positions)


def test_simplehigh_rounds_are_unchanged_by_the_history():
    """simpleHigh does not count, so no Knowledge is made and the rounds play as before"""
    rnd = Round(Table(), list(Deck(shuffle=3, rng=4).deal()), 'spades', [simpleHigh] * 4, declarer='north')
    assert rnd.knowledge is None and not simpleHigh.counts_cards and simpleHigh.knowledge is None
    assert rnd.play() == Round(Table(), list(Deck(shuffle=3, rng=4).deal()), 'spades', [simpleHigh] * 4).play('east')


# ---------------------------------------------------------------------------------------------- countingHigh decisions
def counting_logic(hand_codes, trump, played=(), revealed=None, seat='north'):
    hand = make_hand(hand_codes)
    k = Knowledge(seat, hand)
    for s, code in played:
        k.observe(s, Card.fromCode(code))
    if revealed:
        k.reveal(*revealed)
    logic = countingHigh(hand, trump)
    logic.knowledge = k
    return logic


def test_counting_leads_a_master_instead_of_its_highest_card():
    # the ace of spades is still out, so the king is not a master; the ace of hearts and king of clubs are
    # (the ace of clubs has gone) and nobody can trump a club: lead the master, not the highest card
    hand = 'Ks 5s 2s Ah Qh 4h 6d 3d Kc 9c 8c 7c 4c'
    plain = simpleHigh(make_hand(hand), 'notrump')
    logic = counting_logic(hand, 'notrump', played=[('east', 'Ac')])
    assert plain.lead() == Card.fromCode('Ah')  # its highest card
    assert logic.lead() == Card.fromCode('Ah')  # the ace of hearts is a master as well
    hand2 = 'Ks 5s 2s 9h Qh 4h 6d 3d Kc 9c 8c 7c 4c'
    plain2 = simpleHigh(make_hand(hand2), 'notrump')
    logic2 = counting_logic(hand2, 'notrump', played=[('east', 'Ac')])
    assert plain2.lead() == Card.fromCode('Ks')
    assert logic2.lead() == Card.fromCode('Kc')  # the king of clubs cannot be beaten now


def test_counting_does_not_lead_a_master_the_opponents_can_trump():
    hand2 = 'Ks 5s 2s 9h Qh 4h 6d 3d Kc 9c 8c 7c 4c'
    # hearts are trump and some are still out: the king of clubs could be ruffed, so no safe master
    logic = counting_logic(hand2, 'hearts', played=[('east', 'Ac')])
    assert logic.lead() == simpleHigh(make_hand(hand2), 'hearts').lead()
    # a master in the trump suit itself is fine
    hand3 = 'As 5s 2s Ah Kh 4h 6d 3d Kc 9c 8c 7c 4c'
    logic3 = counting_logic(hand3, 'hearts', played=[('east', 'Qh')])
    assert logic3.lead() == Card.fromCode('Ah')


def test_counting_without_a_knowledge_object_plays_like_simplehigh():
    hand = make_hand('Ks 5s 2s 9h Qh 4h 6d 3d Kc 9c 8c 7c 4c')
    assert countingHigh(hand, 'notrump').lead() == simpleHigh(hand, 'notrump').lead()


def test_counting_follows_like_simplehigh():
    hand = make_hand('Ks 5s 2s 9h Qh 4h 6d 3d Kc 9c 8c 7c 4c')
    t = Trick('east', 'notrump')
    t.nextCard(Card.fromCode('0s'))
    assert countingHigh(hand, 'notrump').follow(t) == simpleHigh(hand, 'notrump').follow(t) == Card.fromCode('Ks')


def test_a_player_cannot_see_the_hidden_hands():
    """
    The decisions of a player depend only on what that player knows: two deals that differ only in the
    cards of the hidden hands, and agree on everything declarer has seen, give the same play from dummy.
    """
    def deal(west_rest_seed):
        south = make_hand('As Ks Qs Js 0s 9s 8s 7s 6s 5s 4s 3s 2s')
        north = make_hand('Ah Kh Qh Jh 0h 9h 8h 7h 6h 5h 4h 3h 2h')
        rest = [c for c in ALL_CARDS if c not in set(south) | set(north)]
        order = np.random.default_rng(west_rest_seed).permutation(len(rest))
        shuffled = [rest[i] for i in order]
        lead = Card.fromCode('Ad')  # west's opening lead in both deals
        shuffled.remove(lead)
        west = Hand([lead] + shuffled[:12])
        east = Hand(shuffled[12:])
        return [north, east, south, west]

    plays = []
    for seed in (1, 2, 3, 4, 5):
        hands = deal(seed)
        assert (hands[1].original != deal(1)[1].original) or seed == 1  # east's hand really differs
        rnd = Round(Table(), hands, 'spades', [countingHigh] * 4, declarer='south')
        rnd.play_trick('west')
        plays.append(rnd.tricks[0][1])  # dummy (north) plays second, seeing only its hand, declarer's and the lead
    assert len(set(plays)) == 1


def test_counting_pays_off_in_notrump():
    """cashing sure winners first: a counting side beats simpleHigh opponents on the same deals"""
    def north_south_tricks(logics):
        rng = np.random.default_rng(7)
        total = 0
        n = 1200
        for i in range(n):
            hands = list(Deck(shuffle=3, rng=rng).deal())
            rnd = Round(Table(), hands, 'notrump', logics, declarer=Position.positions[i % 4])
            total += rnd.play()[0]
        return total / n

    base = north_south_tricks([simpleHigh] * 4)
    counting = north_south_tricks([countingHigh, simpleHigh, countingHigh, simpleHigh])
    assert base == pytest.approx(6.5, abs=0.15)
    assert counting > base + 0.25  # measured: about +0.44 tricks a deal over 3,000 deals

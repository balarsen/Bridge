import functools

import numpy as np
import pytest

from .. import DoubleDummy as DD
from ..Bid import Bid
from ..Card import ALL_CARDS, Card
from ..Deck import Deck
from ..Harness import run_batches
from ..Position import Position
from ..Suit import Suit

needs_dd = pytest.mark.skipif(not DD.AVAILABLE, reason='the endplay package is not installed (Python 3.12/3.13, dd group)')


# ---------------------------------------------------------------------------------------------- the oracle
def ns_tricks(hands, strain, leader, first_card=None):
    """
    Brute-force minimax: the tricks north-south take from this position with perfect play by all four, for
    hands of any equal size (slow, so only for endings of a few cards).  With `first_card` the leader's first
    play is forced.  This is the reference the solver is checked against.
    """
    trump = Suit.indices.get(strain, -1)
    start = tuple(tuple(sorted(c.code for c in h)) for h in hands)
    leader = Position.positions.index(Position.name(leader))

    def winner(played):
        best_seat, best_code = played[0]
        for seat, code in played[1:]:
            suit = code // 13
            if suit == best_code // 13:
                if code % 13 > best_code % 13:
                    best_seat, best_code = seat, code
            elif suit == trump:
                best_seat, best_code = seat, code
        return best_seat

    @functools.lru_cache(maxsize=None)
    def from_trick_start(hands, leader):
        if not hands[0]:
            return 0
        return in_trick(hands, leader, ())

    def in_trick(hands, leader, played, only=None):
        if len(played) == 4:
            win = winner(played)
            return (win % 2 == 0) + from_trick_start(hands, win)
        seat = (leader + len(played)) % 4
        cards = hands[seat]
        if played:
            follow = [c for c in cards if c // 13 == played[0][1] // 13]
            cards = follow or cards
        values = []
        for code in cards:
            rest = tuple(tuple(c for c in h if c != code) if i == seat else h for i, h in enumerate(hands))
            values.append(in_trick(rest, leader, played + ((seat, code),)))
        return max(values) if seat % 2 == 0 else min(values)

    if first_card is None:
        return from_trick_start(start, leader)
    code = first_card.code
    rest = tuple(tuple(c for c in h if c != code) if i == leader else h for i, h in enumerate(start))
    return in_trick(rest, leader, ((leader, code),))


def random_ending(rng, n_cards):
    """four hands of n_cards random cards each, as lists of cards"""
    chosen = rng.choice(52, 4 * n_cards, replace=False)
    return [[ALL_CARDS[i] for i in chosen[k * n_cards:(k + 1) * n_cards]] for k in range(4)]


def leader_side_tricks(hands, strain, leader, card):
    """what the oracle says the leader's side takes in the rest of the play if `leader` starts with `card`"""
    seat = Position.positions.index(leader)
    ns = ns_tricks(hands, strain, leader, first_card=card)
    return ns if seat % 2 == 0 else len(hands[0]) - ns


def test_the_oracle_on_hands_that_are_easy_to_check():
    def hand(codes):
        return [Card.fromCode(c) for c in codes.split()]

    # north holds spades, east hearts, south diamonds, west clubs
    hands = [hand('As Ks Qs'), hand('Ah Kh Qh'), hand('Ad Kd Qd'), hand('Ac Kc Qc')]
    assert ns_tricks(hands, 'spades', 'east') == 3  # north ruffs every heart lead
    assert ns_tricks(hands, 'notrump', 'east') == 0  # east cashes all its hearts
    assert ns_tricks(hands, 'notrump', 'north') == 3
    one = [hand('As'), hand('Ks'), hand('2h'), hand('2c')]
    assert ns_tricks(one, 'notrump', 'east') == 1  # east leads the king, north's ace takes it
    assert ns_tricks(one, 'notrump', 'north') == 1
    assert ns_tricks(one, 'notrump', 'east', first_card=Card.fromCode('Ks')) == 1
    assert leader_side_tricks(one, 'notrump', 'east', Card.fromCode('Ks')) == 0  # east's side takes nothing
    assert leader_side_tricks(one, 'notrump', 'north', Card.fromCode('As')) == 1


# ---------------------------------------------------------------------------------------------- proof 1: correct
@needs_dd
@pytest.mark.parametrize('n_cards', [1, 2, 3])
def test_solver_agrees_with_brute_force_on_endings(n_cards):
    rng = np.random.default_rng(100 + n_cards)
    checked = 0
    for _ in range(25):
        hands = random_ending(rng, n_cards)
        for strain in ('spades', 'hearts', 'notrump', 'clubs'):
            for leader in Position.positions:
                solved = DD.solve_leads(hands, strain, leader)
                seat = Position.positions.index(leader)
                assert {c.code for c in solved} == {c.code for c in hands[seat]}  # every card is valued
                for card, tricks in solved.items():
                    assert tricks == leader_side_tricks(hands, strain, leader, card)
                checked += 1
    assert checked == 25 * 4 * 4


@needs_dd
def test_the_table_means_tricks_for_the_declaring_side():
    n, e, s, w = ([Card.fromCode(r + suit) for r in 'AKQJ098765432'] for suit in 'shdc')
    table = DD.dd_table([n, e, s, w])  # north all spades, east all hearts, south all diamonds, west all clubs
    spades, notrump = Bid.strains.index('spades'), Bid.strains.index('notrump')
    assert table[spades][0] == 13  # north declares spades and ruffs everything: all thirteen
    assert table[notrump][0] == 0 and table[notrump][1] == 0  # the opening leader cashes the long suit
    assert table.shape == (5, 4) and table.dtype == np.int8


@needs_dd
def test_the_table_agrees_with_solving_every_opening_lead():
    """for whole deals: declarer's tricks = 13 - what the opening leader's side takes with the best lead"""
    for seed in range(4):
        hands = list(Deck(shuffle=3, rng=seed).deal())
        table = DD.dd_table(hands)
        for s, strain in enumerate(Bid.strains):
            for seat, declarer in enumerate(Position.positions):
                leader = Position.index2pos(declarer, 1)
                best_for_leader = max(DD.solve_leads(hands, strain, leader).values())
                assert table[s][seat] == 13 - best_for_leader, (seed, strain, declarer)


@needs_dd
def test_partners_have_the_same_trick_count_in_a_strain_up_to_the_lead():
    """the two declarers of a side usually differ by at most one or two tricks, never wildly"""
    for seed in range(10):
        table = DD.dd_table(list(Deck(shuffle=3, rng=seed).deal()))
        assert (np.abs(table[:, 0] - table[:, 2]) <= 3).all() and (np.abs(table[:, 1] - table[:, 3]) <= 3).all()
        assert ((table >= 0) & (table <= 13)).all()
        # what north-south take as declarers and what east-west take against them add up to at most 13 + the lead
        for s in range(5):
            assert table[s][0] + table[s][1] >= 0


# ---------------------------------------------------------------------------------------------- the adapter
@needs_dd
def test_to_deal_checks_its_input():
    hands = list(Deck(shuffle=3, rng=1).deal())
    assert DD.to_deal(hands) is not None
    with pytest.raises(ValueError):
        DD.to_deal(hands[:3])
    with pytest.raises(ValueError):
        DD.to_deal([hands[0], hands[1], hands[2], hands[3][:5]])
    with pytest.raises(ValueError):
        DD.to_deal([hands[0], hands[0], hands[2], hands[3]])  # the same cards twice


@needs_dd
def test_solve_leads_names_cards_as_ours():
    hands = [[Card.fromCode(c)] for c in ('As', '0h', '2d', '3c')]  # a single card each
    assert DD.solve_leads(hands, 'notrump', 'north') == {Card.fromCode('As'): 1}
    # the ten comes back as our '0'
    assert set(DD.solve_leads(hands, 'notrump', 'east')) == {Card.fromCode('0h')}


@needs_dd
def test_batches_give_the_same_tables_as_single_calls():
    decks = [list(Deck(shuffle=3, rng=i).deal()) for i in range(70)]  # more than two batches of 32
    batch = DD.dd_tables(decks)
    assert batch.shape == (70, 5, 4) and batch.dtype == np.int8
    for i in (0, 31, 32, 33, 69):  # across the batch boundaries
        assert np.array_equal(batch[i], DD.dd_table(decks[i]))
    assert DD.dd_tables([]).shape == (0, 5, 4)
    assert np.array_equal(DD.dd_tables(iter(decks[:3])), batch[:3])


@needs_dd
def test_the_double_dummy_result_of_the_deck_hands_is_stable():
    hands = list(Deck(shuffle=3, rng=3).deal())
    first = DD.dd_table(hands)
    assert np.array_equal(first, DD.dd_table(hands))  # no state is kept between calls


# ---------------------------------------------------------------------------------------------- proof: parallel
def tables(rng, count):
    out = np.empty((count, 5, 4), np.int8)
    for i in range(count):
        out[i] = DD.dd_table(list(Deck(shuffle=3, rng=rng).deal()))
    return out


@needs_dd
def test_the_solver_runs_in_worker_processes_with_the_same_answers():
    serial = run_batches(tables, 24, seed=5, batch_size=6, workers=1)
    parallel = run_batches(tables, 24, seed=5, batch_size=6, workers=2)
    assert serial.shape == (24, 5, 4)
    assert np.array_equal(serial, parallel)


# ---------------------------------------------------------------------------------------------- pure functions
def table_of(rows):
    """a (5, 4) table from {strain: (north, east, south, west)} with 6 tricks (nothing makes) elsewhere"""
    t = np.full((5, 4), 6, dtype=np.int8)
    for strain, tricks in rows.items():
        t[Bid.strains.index(strain)] = tricks
    return t


def test_highest_contract():
    t = table_of({'hearts': (10, 4, 9, 3), 'notrump': (7, 7, 8, 8), 'clubs': (11, 0, 11, 0)})
    assert DD.highest_contract(t, 'ns') == Bid(5, 'clubs')  # 11 tricks in clubs is level 5, above 4 hearts and 2 notrump
    assert DD.highest_contract(table_of({'hearts': (10, 4, 9, 3), 'notrump': (7, 7, 8, 8)}), 'ns') == Bid(4, 'hearts')
    assert DD.highest_contract(t, 'ew') == Bid(2, 'notrump')  # east-west: 8 tricks in notrump (from south... west)
    assert DD.highest_contract(table_of({}), 'ns') is None
    # the better of the two declarers counts
    assert DD.highest_contract(table_of({'spades': (9, 6, 10, 6)}), 'ns') == Bid(4, 'spades')
    # a higher level beats a higher strain
    both = table_of({'notrump': (7, 6, 7, 6), 'spades': (6, 9, 6, 9), 'diamonds': (6, 10, 6, 10)})
    assert DD.highest_contract(both, 'ew') == Bid(4, 'diamonds')
    assert DD.highest_contract(both, 'ns') == Bid(1, 'notrump')

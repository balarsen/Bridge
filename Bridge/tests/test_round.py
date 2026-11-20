import numpy as np
import pytest

from ..Card import Card
from ..Deck import Deck
from ..Hand import Hand
from ..Position import Position
from ..Round import Round, simpleHigh
from ..Table import Table
from ..Trick import Trick


def make_hand(codes):
    """build a hand from a string of 2 letter card codes, 'As Kd 0h ...' (0 is ten)"""
    return Hand([Card.fromCode(c) for c in codes.split()])


def make_trick(leader, trump, codes):
    t = Trick(leader, trump)
    for c in codes.split():
        t.nextCard(Card.fromCode(c))
    return t


# has diamonds and no hearts
HAND = make_hand('As Ks 5s 2s Qd Jd 4d Kc 6c 3c 7c 5c Jc')
# no clubs
VOID_CLUBS = make_hand('As Ks 5s 2s Qh Jh 4h Kd 6d 3d 9d 8d 7d')


class TestSimpleHigh:
    def test_lead_highest(self):
        assert simpleHigh(HAND, 'hearts').lead() == Card('A', 'spades')

    def test_lead_tie_goes_to_higher_suit(self):
        hand = make_hand('Ad Ah 2s 3s 4s 5s 6s 7s 8s 9s 3d 4d 5d')
        assert simpleHigh(hand, 'clubs').lead() == Card('A', 'hearts')

    def test_follow_suit_and_win(self):
        # king of clubs beats the ten led
        t = make_trick('north', 'hearts', '0c')
        assert simpleHigh(HAND, 'hearts').follow(t) == Card('K', 'clubs')

    def test_follow_suit_cannot_win(self):
        t = make_trick('north', 'hearts', 'Ac')
        assert simpleHigh(HAND, 'hearts').follow(t) == Card('3', 'clubs')

    def test_follow_suit_but_trumped(self):
        """a trump already in the trick can not be beaten by our higher card of the lead suit"""
        t = make_trick('north', 'hearts', '5c 2h')
        assert simpleHigh(HAND, 'hearts').follow(t) == Card('3', 'clubs')

    def test_follow_trump_lead(self):
        t = make_trick('north', 'spades', '0s')
        assert simpleHigh(HAND, 'spades').follow(t) == Card('A', 'spades')
        t = make_trick('north', 'spades', 'Qs')
        assert simpleHigh(HAND, 'spades').follow(t) == Card('A', 'spades')
        # can't beat the ace, so play our lowest spade
        hand = make_hand('Ks Qs 5s 2s Qd Jd 4d Kc 6c 3c 7c 5c Jc')
        t = make_trick('north', 'spades', 'As')
        assert simpleHigh(hand, 'spades').follow(t) == Card('2', 'spades')

    def test_void_plays_lowest_trump(self):
        t = make_trick('north', 'spades', '0c')
        assert simpleHigh(VOID_CLUBS, 'spades').follow(t) == Card('2', 'spades')

    def test_void_no_trump_discards_lowest(self):
        t = make_trick('north', 'notrump', '0c')
        assert simpleHigh(VOID_CLUBS, 'notrump').follow(t) == Card('2', 'spades')
        # trump suit we hold none of
        t = make_trick('north', 'clubs', '0h')
        hand = make_hand('As Ks 5s 2s 0d Jd 4d Kd 6d 3d 9d 8d 7d')
        assert simpleHigh(hand, 'clubs').follow(t) == Card('2', 'spades')

    def test_void_trump_led_discards_lowest(self):
        t = make_trick('north', 'clubs', '0c')
        assert simpleHigh(VOID_CLUBS, 'clubs').follow(t) == Card('2', 'spades')

    def test_hand_cards_get_trump_flag(self):
        hand = make_hand('As Ks 5s 2s Qd Jd 4d Kc 6c 3c 7c 5c Jc')
        simpleHigh(hand, 'clubs')
        assert all(c.trump == (c.suit == 'clubs') for c in hand)


def deal():
    d = Deck()
    d.shuffle(3)
    return list(d.deal())


class TestRound:
    def test_play_trick_respects_leader(self):
        np.random.seed(1)
        hands = deal()
        rnd = Round(Table(), hands, 'spades', [simpleHigh] * 4)
        expected_lead = rnd.logics[2].lead()  # south
        win = rnd.play_trick('south')
        trick = rnd.tricks[0]
        assert trick.leader == 'south'
        assert trick[0] == expected_lead
        assert trick.south == expected_lead
        assert win == trick.winner()
        assert rnd.winners == [win[1]]
        assert all(len(h) == 12 for h in hands)
        for seat, hand in zip(Position.positions, hands):
            assert trick.getCard(seat) not in hand

    def test_play_all_thirteen(self):
        np.random.seed(2)
        hands = deal()
        rnd = Round(Table(), hands, 'spades', [simpleHigh] * 4)
        ns, ew = rnd.play('west')
        assert ns + ew == 13
        assert len(rnd.tricks) == len(rnd.winners) == 13
        assert all(len(h) == 0 for h in hands)
        # the winner of each trick leads the next
        for prev, nxt in zip(rnd.winners, rnd.tricks[1:]):
            assert nxt.leader == prev
        assert rnd.tricks[0].leader == 'west'

    def test_no_card_played_twice(self):
        np.random.seed(3)
        rnd = Round(Table(), deal(), 'hearts', [simpleHigh] * 4)
        rnd.play()
        played = [c for t in rnd.tricks for c in t]
        assert len(set(played)) == 52

    @pytest.mark.parametrize('trump', ['spades', 'hearts', 'diamonds', 'clubs', 'notrump'])
    def test_every_trump_plays_out(self, trump):
        np.random.seed(4)
        for _ in range(20):
            ns, ew = Round(Table(), deal(), trump, [simpleHigh] * 4).play()
            assert ns + ew == 13

    def test_stats(self):
        """given a fixed trump and rotating leads both sides should win the same number of tricks"""
        np.random.seed(8675309)
        stats = []
        for lead in range(2000):
            rnd = Round(Table(), deal(), 'spades', [simpleHigh] * 4)
            stats.append(rnd.play(Position.positions[lead % 4]))
        ns, ew = np.mean(stats, axis=0)
        assert ns + ew == pytest.approx(13)
        assert ns == pytest.approx(6.5, abs=0.2)
        assert ew == pytest.approx(6.5, abs=0.2)

    def test_fixed_leader_is_not_an_advantage(self):
        """
        Findings.txt (2012) said a fixed leader wins 7 to 6.  That came from code where
        off-suit cards could win a trick and seat 0 always led.  With real trick rules
        leading the highest card (often an ace that gets ruffed) is slightly a handicap.
        """
        np.random.seed(8675309)
        stats = [Round(Table(), deal(), 'spades', [simpleHigh] * 4).play('north')
                 for _ in range(2000)]
        ns, ew = np.mean(stats, axis=0)
        assert ns + ew == pytest.approx(13)
        assert 5.5 < ns < 7.5

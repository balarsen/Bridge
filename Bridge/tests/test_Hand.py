import pytest

import numpy as np

from ..Card import Card
from ..Hand import Hand


def make_hand(codes):
    """build a hand from a string of 2 letter card codes, 'As Kd 0h ...' (0 is ten)"""
    return Hand([Card.fromCode(c) for c in codes.split()])


class TestHand:
    cards = (Card('K', 'spades'),
             Card('5', 'spades'),
             Card('2', 'spades'),
             Card('A', 'hearts'),
             Card('6', 'hearts'),
             Card('Q', 'diamonds'),
             Card('9', 'diamonds'),
             Card('6', 'diamonds'),
             Card('5', 'diamonds'),
             Card('4', 'diamonds'),
             Card('3', 'diamonds'),
             Card('4', 'clubs'),
             Card('2', 'clubs'),
             )

    def test_init(self):
        with pytest.raises(ValueError):
            h = Hand(TestHand.cards[:-2])
        h = Hand(TestHand.cards)
        assert len(h) == 13

    def test_str(self):
        h = Hand(TestHand.cards)
        s = str(h)
        assert s.startswith('K of spades')

    def test_get_suit(self):
        h = Hand(TestHand.cards)
        ans = (Card('K', 'spades'),
               Card('5', 'spades'),
               Card('2', 'spades'))
        np.testing.assert_array_equal(ans, h.get_suit('spades'))

    def test_get_suit_empty(self):
        h = Hand(TestHand.cards)
        del h[0]
        del h[0]
        del h[0]
        assert h.get_suit('spades') == []

    def test_highCard(self):
        h = Hand(TestHand.cards)
        assert h.highCard('spades') == Card('K', 'spades')

    def test_lowCard(self):
        h = Hand(TestHand.cards)
        assert h.lowCard('spades') == Card('2', 'spades')

    def test_distro(self):
        h = Hand(TestHand.cards)
        assert h.distro() == (('spades', 3),
                              ('hearts', 2),
                              ('diamonds', 6),
                              ('clubs', 2))

    def test_hcp(self):
        # K=3 A=4 Q=2
        assert Hand(TestHand.cards).hcp() == 9

    def test_longest(self):
        assert Hand(TestHand.cards).longest() == [('diamonds', 6), ('spades', 3),
                                                  ('hearts', 2), ('clubs', 2)]

    def test_strongest(self):
        # spades K, hearts A, diamonds Q, clubs nothing
        assert Hand(TestHand.cards).strongest() == [('hearts', 4), ('spades', 3),
                                                    ('diamonds', 2), ('clubs', 0)]

    def test_balanced(self):
        assert not Hand(TestHand.cards).balanced()  # 6322
        assert make_hand('As Ks 5s 2s Qh Jh 4h Kd 6d 3d 7c 5c Jc').balanced()  # 4333
        assert make_hand('As Ks 5s 2s Qh Jh 4h 3h Kd 6d 7c 5c Jc').balanced()  # 4432
        assert make_hand('As Ks 5s 2s 3s Qh Jh 4h Kd 6d 7c 5c Jc').balanced()  # 5332
        assert not make_hand('As Ks 5s 2s 3s Qh Jh 4h 3h Kd 6d 7c 5c').balanced()  # 5422

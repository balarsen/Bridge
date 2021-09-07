import pytest

import numpy as np

from ..Card import Card
from ..Hand import Hand


class TestHand:
    cards = (Card('K', 'spades'),
             Card(5, 'spades'),
             Card(2, 'spades'),
             Card('A', 'hearts'),
             Card(6, 'hearts'),
             Card('Q', 'diamonds'),
             Card(9, 'diamonds'),
             Card(6, 'diamonds'),
             Card(5, 'diamonds'),
             Card(4, 'diamonds'),
             Card(3, 'diamonds'),
             Card(4, 'clubs'),
             Card(2, 'clubs'),
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
             Card(5, 'spades'),
             Card(2, 'spades'))
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
        assert h.lowCard('spades') == Card(2, 'spades')

    def test_distro(self):
        h = Hand(TestHand.cards)
        assert h.distro() == (('spades', 3),
                              ('hearts', 2),
                              ('diamonds', 6),
                              ('clubs', 2))
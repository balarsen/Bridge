import itertools
import unittest

import numpy as np

import Round
import Table
import Deck
from __init__ import positions

class TestRound(unittest.TestCase):
    def test_stats(self):
        """test that the stats are 50/50 as they should be"""
        # given a fixed trump and rotating leads both sides should have the
        # save average number of tricks
        stats = []
        seats = ['North', 'East', 'South', 'West']
        st = itertools.cycle(seats)
        for i in range(2000):
            d1 = Deck.Deck()
            d1.shuffle(7)
            h1, h2, h3, h4 = d1.deal()
            rnd = Round.Round(Table.Table(),
                        [h1,h2,h3,h4],
                        'spades',
                        [Round.simpleHigh, Round.simpleHigh,
                         Round.simpleHigh, Round.simpleHigh])
            tricks = []
            win = rnd.play_trick(st.next())
            tricks.append(win[1])
            for i in range(12):
                win = rnd.play_trick(win[1])
                tricks.append(win[1])
            stats.append( (sum([1 for v in tricks if v in ['North', 'South']]),
                           sum([1 for v in tricks if v in ['East', 'West']])) )
        self.assertAlmostEqual( np.mean((zip(*stats)[0])),
                               np.mean((zip(*stats)[1])), places=0)


if __name__ == '__main__':
    unittest.main()



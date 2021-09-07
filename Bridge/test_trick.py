
import unittest

import Card
import Trick
from __init__ import positions

class TestTrick(unittest.TestCase):
    def test_init(self):
        """init does some checking"""
        self.assertRaises(ValueError, Trick.Trick, leader='badval')
        tck = Trick.Trick()
        self.assertEqual('North', tck.leader)
        self.assertTrue(tck.trump is None)
        tck = Trick.Trick(leader='South', trump='diamonds')
        self.assertEqual('South', tck.leader)
        self.assertEqual('diamonds', tck.trump)

    def test_nextCard(self):
        """should be able to add cards"""
        t = Trick.Trick(trump='hearts')
        t.nextCard(Card.Card(3,3))
        self.assertEqual(t.nCards, len(t))
        self.assertEqual(t.nCards, 1)
        t.nextCard(Card.Card(5,2))
        self.assertRaises(ValueError, t.nextCard, Card.Card(5,2))
        t.nextCard(Card.Card(7,3))
        t.nextCard(Card.Card(9,3))
        self.assertEqual(t.nCards, 4)
        self.assertRaises(IndexError, t.nextCard, Card.Card(10,3))
        self.assertFalse(t[0].trump)
        self.assertTrue( t[1].trump)
        self.assertFalse(t[2].trump)
        self.assertFalse(t[3].trump)

    def test_winner(self):
        """winner should be named correctly"""
        t = Trick.Trick(trump='hearts')
        t.nextCard(Card.Card(3,3))
        self.assertRaises(IndexError, t.winner)
        t.nextCard(Card.Card(5,2))
        t.nextCard(Card.Card(7,3))
        t.nextCard(Card.Card(9,3))
        self.assertEqual(t.winner(), (Card.Card(5,2), 'East'))

    def test_getCard(self):
        """should be able to get cards played"""
        t = Trick.Trick(trump='hearts')
        for p in positions:
            self.assertTrue(t.getCard(p) is None)
        t.nextCard(Card.Card(3,3))
        t.nextCard(Card.Card(4,3))
        t.nextCard(Card.Card(5,3))
        t.nextCard(Card.Card(6,3))
        self.assertEqual(t.north, Card.Card(3,3))
        self.assertEqual(t.east, Card.Card(4,3))
        self.assertEqual(t.south, Card.Card(5,3))
        self.assertEqual(t.west, Card.Card(6,3))

if __name__ == '__main__':
    unittest.main()



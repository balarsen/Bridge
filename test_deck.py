
import unittest

import deck
import hand

class TestDeck(unittest.TestCase):
    def test_cut(self):
        """cut should work"""
        d1 = deck.deck()
        d2 = deck.deck()
        d1.cut(1)
        self.assertEqual(d1[-1], d2[0])
        d1 = deck.deck()
        d1.cut(20)
        for i in range(52):
            self.assertNotEqual(d1[i], d2[i])
        d1 = deck.deck()
        d1.cut()       
        for i in range(52):
            self.assertNotEqual(d1[i], d2[i])

    def test_shuffle(self):
        d1 = deck.deck()
        d2 = deck.deck()
        d1.shuffle(2)
        self.assertNotEqual(d1, d2)

    def test_boolean(self):
        d1 = deck.deck()
        d2 = deck.deck()
        self.assertFalse(d1 != d2)
        self.assertEqual(d1, d2)
        d1.cut()
        self.assertNotEqual(d1, d2)
        
    def test_deal(self):
        d1 = deck.deck()
        h1, h2, h3, h4 = d1.deal()
        self.assertTrue(isinstance(h1, hand.hand))
        

if __name__ == '__main__':
    unittest.main()

import StringIO
import unittest

import card

class TestCard(unittest.TestCase):
    def test_init(self):
        """input checking"""
        self.assertRaises(ValueError, card.card, 15, 'hearts')
        self.assertRaises(ValueError, card.card, 'bad', 'hearts')
        self.assertRaises(ValueError, card.card, 12, 'bad')
        self.assertRaises(ValueError, card.card, 'ace', 'bad')
        self.assertEqual('two', card.card(2, 1).value)

    def test_bool(self):
        """test boolean ops (total_ordering)"""
        fourS = card.card(4,1)
        self.assertEqual(card.card(4,1), fourS)
        self.assertLess(card.card(3,1), fourS)
        self.assertNotEqual(card.card(3,1), fourS)
        self.assertGreater(card.card(5,1), fourS)
        self.assertFalse(card.card(4,1) != fourS)

    def test_bool_trump(self):
        fourS = card.card(4,1, trump=True)
        self.assertLess(card.card(10,3), fourS)
        self.assertLess(card.card(4,1), fourS)
        self.assertLess(card.card(4,1), card.card(4,2, True))
        self.assertFalse(card.card(4,1, True) < card.card(10,2, False))
        self.assertFalse(card.card(10,1, True) < card.card(4,1, True))

        self.assertGreater(fourS, card.card(10,3))
        self.assertGreater(fourS, card.card(4,1))
        self.assertGreater(card.card(4,2, True), card.card(4,1, False))
        self.assertTrue(card.card(4,1, True) > card.card(10,2, False))
        self.assertTrue(card.card(10,1, True) > card.card(4,1, True))
        self.assertFalse(card.card(4,1, True) > card.card(10,1, True))
        self.assertFalse(card.card(4,1, False) > card.card(10,2, True))

    def test_hc_points(self):
        ans = [0]*9 + [1,2,3,4]
        for i, value in enumerate(range(2, 15)):
            self.assertEqual(ans[i], card.card(value, 1)._hc_points()) 
    
    def test_str(self):
        c1 = card.card(12,1)
        self.assertEqual("queen of spades", c1.__str__())
        


if __name__ == '__main__':
    unittest.main()
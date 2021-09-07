
import unittest

import Card

class TestCard(unittest.TestCase):
    def test_init(self):
        """input checking"""
        self.assertRaises(ValueError, Card.Card, 15, 'hearts')
        self.assertRaises(ValueError, Card.Card, 'bad', 'hearts')
        self.assertRaises(ValueError, Card.Card, 4, 'notrump')
        self.assertRaises(ValueError, Card.Card, 12, 'bad')
        self.assertRaises(ValueError, Card.Card, 'ace', 'bad')
        self.assertEqual('two', Card.Card(2, 1).value)

    def test_bool(self):
        """test boolean ops (total_ordering)"""
        fourS = Card.Card(4,1)
        self.assertEqual(Card.Card(4,1), fourS)
        self.assertLess(Card.Card(3,1), fourS)
        self.assertNotEqual(Card.Card(3,1), fourS)
        self.assertGreater(Card.Card(5,1), fourS)
        self.assertFalse(Card.Card(4,1) != fourS)

    def test_bool_trump(self):
        fourS = Card.Card(4,1, trump=True)
        self.assertLess(Card.Card(10,3), fourS)
        self.assertLess(Card.Card(4,1), fourS)
        self.assertLess(Card.Card(4,1), Card.Card(4,2, True))
        self.assertFalse(Card.Card(4,1, True) < Card.Card(10,2, False))
        self.assertFalse(Card.Card(10,1, True) < Card.Card(4,1, True))

        self.assertGreater(fourS, Card.Card(10,3))
        self.assertGreater(fourS, Card.Card(4,1))
        self.assertGreater(Card.Card(4,2, True), Card.Card(4,1, False))
        self.assertTrue(Card.Card(4,1, True) > Card.Card(10,2, False))
        self.assertTrue(Card.Card(10,1, True) > Card.Card(4,1, True))
        self.assertFalse(Card.Card(4,1, True) > Card.Card(10,1, True))
        self.assertFalse(Card.Card(4,1, False) > Card.Card(10,2, True))

    def test_hc(self):
        ans = [0]*9 + [1,2,3,4]
        for i, value in enumerate(range(2, 15)):
            self.assertEqual(ans[i], Card.Card(value, 1).hc)

    def test_str(self):
        c1 = Card.Card(12,1)
        self.assertEqual("queen of spades", c1.__str__())



if __name__ == '__main__':
    unittest.main()


import unittest

from .. import Bid

class TestBid(unittest.TestCase):
    def setUp(self):
        super(TestBid, self).setUp()
        self.b1 = Bid.Bid(1, 'hearts')
        self.b2 = Bid.Bid(1, 'spades')
        self.b3 = Bid.Bid(1, 'clubs')
        self.b4 = Bid.Bid(1, 'notrump')
        self.b5 = Bid.Bid(4, 'hearts')

    def test_init(self):
        """input checking"""
        self.assertRaises(ValueError, Bid.Bid, 0, 'hearts')
        self.assertRaises(ValueError, Bid.Bid, 8, 'hearts')
        self.assertRaises(ValueError, Bid.Bid, 2, 'bad')
        self.assertEqual(3, Bid.Bid(3, 'hearts').value)
        self.assertEqual(2, Bid.Bid(3, 'hearts').suit)
        self.assertEqual('pass', Bid.Bid('pass', 'hearts').value)


    def test_eq_ne(self):
        self.assertTrue(self.b1 == self.b1)
        self.assertTrue(self.b3 == self.b3)
        self.assertTrue(self.b5 == self.b5)
        self.assertTrue(self.b1 != self.b3)
        self.assertTrue(self.b3 != self.b5)
        self.assertTrue(self.b5 != self.b1)
        self.assertFalse(self.b1 != self.b1)
        self.assertFalse(self.b3 != self.b3)
        self.assertFalse(self.b5 != self.b5)
        self.assertFalse(self.b1 == self.b3)
        self.assertFalse(self.b3 == self.b5)
        self.assertFalse(self.b5 == self.b1)

    def test_gt_lt(self):
        self.assertTrue(self.b1 > self.b3)
        self.assertTrue(self.b3 < self.b5)
        self.assertTrue(self.b5 > self.b1)
        self.assertFalse(self.b1 < self.b3)
        self.assertFalse(self.b3 > self.b5)
        self.assertFalse(self.b5 < self.b1)
        self.assertTrue(self.b1 < self.b2)

if __name__ == '__main__':
    unittest.main()
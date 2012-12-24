
import unittest

import Bid
import Bidding

class TestBidding(unittest.TestCase):
    def setUp(self):
        super(TestBidding, self).setUp()
        self.b = Bidding.Bidding(leader='north')

    def test_init(self):
        b = Bidding.Bidding(leader='south')
        self.assertEqual(['South', 'West', 'North', 'East', ], b._seats)
        self.assertEqual(0, b._passCount)
        self.assertEqual(b.leader, 'South')

    def test_addBid(self):
        self.b.addBid('North', Bid.Bid(2, 'hearts'))
        self.assertEqual(1, len(self.b))
        self.assertEqual(0, self.b._passCount)
        self.assertRaises(ValueError, self.b.addBid, 'East', Bid.Bid(1, 'hearts'))
        self.b.addBid('East', Bid.Bid('pass', 'hearts'))
        self.assertEqual(1, self.b._passCount)
        self.b.addBid('South', Bid.Bid('pass', 'hearts'))
        self.b.addBid('West', Bid.Bid('pass', 'hearts'))
        self.assertEqual(('North', Bid.Bid(2, 'hearts')),
                         self.b.addBid('North', Bid.Bid('pass', 'hearts')))
        self.assertRaises(ValueError, self.b.addBid, 'east', Bid.Bid(5, 'hearts'))

    def test_redeal(self):
        """if no one buds we need to redeal"""
        self.b.nextBid(Bid.Bid('pass', 'hearts'))
        self.b.nextBid(Bid.Bid('pass', 'hearts'))
        self.b.nextBid(Bid.Bid('pass', 'hearts'))
        self.assertRaises(Bidding.Redeal, self.b.nextBid, Bid.Bid('pass', 'hearts'))
        self.assertFalse(self.b.opened)

    def test_winningBid(self):
        self.b.addBid('north', Bid.Bid('pass', 'hearts'))
        self.assertTrue(self.b._winningBid() is None)
        self.b.addBid('north', Bid.Bid(2, 'hearts'))
        self.assertEqual(('north', Bid.Bid(2, 'hearts')), self.b._winningBid())

    def test_nextBid(self):
        self.b.nextBid(Bid.Bid(1, 'hearts'))
        self.assertEqual(('North', Bid.Bid(1, 'hearts')), self.b._winningBid())
        self.b.nextBid(Bid.Bid(1, 'spades'))
        self.assertEqual(('East', Bid.Bid(1, 'spades')), self.b._winningBid())


if __name__ == '__main__':
    unittest.main()

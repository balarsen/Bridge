
import unittest

import Bid
import Bidding

class TestBidding(unittest.TestCase):
    def setUp(self):
        super(TestBidding, self).setUp()
        self.b = Bidding.Bidding(leader='north')

    def test_init(self):
        b = Bidding.Bidding(leader='south')
        self.assertEqual(['south', 'west', 'north', 'east', ], b._seats)
        self.assertEqual(0, b._passCount)
        self.assertEqual(b.leader, 'south')

    def test_addBid(self):
        self.b.addBid('north', Bid.Bid(2, 'hearts'))
        self.assertEqual(1, len(self.b))
        self.assertEqual(0, self.b._passCount)
        self.assertRaises(ValueError, self.b.addBid, 'east', Bid.Bid(1, 'hearts'))
        self.b.addBid('east', Bid.Bid('pass', 'hearts'))
        self.assertEqual(1, self.b._passCount)
        self.b.addBid('south', Bid.Bid('pass', 'hearts'))
        self.b.addBid('west', Bid.Bid('pass', 'hearts'))
        self.assertEqual(('north', Bid.Bid(2, 'hearts')), self.b.addBid('north', Bid.Bid('pass', 'hearts')))
        self.assertRaises(ValueError, self.b.addBid, 'east', Bid.Bid(5, 'hearts'))

    def test_winningBid(self):
        self.b.addBid('north', Bid.Bid('pass', 'hearts'))
        self.assertTrue(self.b._winningBid() is None)
        self.b.addBid('north', Bid.Bid(2, 'hearts'))
        self.assertEqual(('north', Bid.Bid(2, 'hearts')), self.b._winningBid())

    def test_nextBid(self):
        self.b.nextBid(Bid.Bid(1, 'hearts'))
        self.assertEqual(('north', Bid.Bid(1, 'hearts')), self.b._winningBid())
        self.b.nextBid(Bid.Bid(1, 'spades'))
        self.assertEqual(('east', Bid.Bid(1, 'spades')), self.b._winningBid())


if __name__ == '__main__':
    unittest.main()
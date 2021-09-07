
import unittest
import random

from .. import BeginningBidder
from .. import Bid
# from .. import Bidding
from .. import Card
from .. import Deck
from .. import Hand

class TestBeginningBidder(unittest.TestCase):
    def setUp(self):
        super(TestBeginningBidder, self).setUp()
        random.seed(123)
        deck = Deck.Deck()
        deck.shuffle(7)
        self.hands = deck.deal()
        # make sure hands are as we expect
        self.assertEqual(self.hands[0].hc, 10)
        self.assertEqual(self.hands[1].hc, 17)
        self.assertEqual(self.hands[2].hc, 5)
        self.assertEqual(self.hands[3].hc, 8)

    def test_logic(self):
        bb = BeginningBidder.BeginningBidder(self.hands[0])
        self.assertEqual(bb.openBid(), Bid.Bid('pass', 1))
        bb = BeginningBidder.BeginningBidder(self.hands[1])
        self.assertEqual(bb.openBid(), Bid.Bid(1, 'hearts'))
        bb = BeginningBidder.BeginningBidder(self.hands[2])
        self.assertEqual(bb.openBid(), Bid.Bid('pass', 1))
        bb = BeginningBidder.BeginningBidder(self.hands[3])
        self.assertEqual(bb.openBid(), Bid.Bid('pass', 1))

    def test_14hcp(self):
        """passes without 14 hcp"""
        cards = [Card.Card(14,1), # 4 hcp
                 Card.Card(14,2), # 4 hcp
                 Card.Card(14,3), # 4 hcp
                 Card.Card(2,1),
                 Card.Card(2,2),
                 Card.Card(2,3),
                 Card.Card(2,4),
                 Card.Card(3,1),
                 Card.Card(3,2),
                 Card.Card(3,3),
                 Card.Card(3,4),
                 Card.Card(4,3),
                 Card.Card(4,4),] # 12 HCP TOTAL
        bb = BeginningBidder.BeginningBidder(Hand.Hand(cards))
        self.assertEqual(bb.openBid(), Bid.Bid('pass', 1))
        cards[-1] = Card.Card(12,1) # 13 HCP total
        bb = BeginningBidder.BeginningBidder(Hand.Hand(cards))
        self.assertEqual(bb.openBid(), Bid.Bid('pass', 1))
        cards[-2] = Card.Card(12,2) # 14 HCP total
        bb = BeginningBidder.BeginningBidder(Hand.Hand(cards))
        self.assertEqual(bb.openBid(), Bid.Bid(1, 'spades'))


if __name__ == '__main__':
    unittest.main()

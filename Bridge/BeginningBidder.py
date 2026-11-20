"""
class for a begining bridge player bidding

the player will not open with less than 14 high card points
 - the player opens in the strongest suit
"""

from .Bid import Bid
from .Bidding import Bidding_logic


class BeginningBidder(Bidding_logic):
    OPEN_HCP = 14

    def openBid(self):
        # this bidder does not have enough points, they pass
        if self.hand.hcp() < self.OPEN_HCP:
            return Bid('pass')
        strongest = self.hand.strongest()  # ties are in suit rank order, best first
        longest = self.hand.longest()
        strongSuit = [s for s, pts in strongest if pts == strongest[0][1]]
        longSuit = [s for s, n in longest if n == longest[0][1]]
        # if the strongest suit is also longest they bid that
        both = [s for s in strongSuit if s in longSuit]
        if both:
            return Bid(1, both[0])
        # the strongest suit is not longest, bid it if it is at least 5 long
        for s in strongSuit:
            if len(self.hand.get_suit(s)) >= 5:
                return Bid(1, s)
        # otherwise open the longest suit
        return Bid(1, longSuit[0])

    def raiseBid(self, bids=None):
        pass

    def jumpBid(self, bids=None):
        pass

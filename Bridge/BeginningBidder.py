
"""
class for a begining bridge player bidding

the player will not open with less than 15
 - the player opens in the strongest suit
"""

from . import Bid
from . import Bidding

class BeginningBidder(Bidding.Bidding_logic):
    def openBid(self):
        # this bidder does not have 14 HCP they pass
        if self.hand.hc <= 14:
            return Bid.Bid('pass', 1)
        else:
            strongSuit = [v[0] for v in self.hand.strongest if v[1] == self.hand.strongest[0][1]]
            longSuit = [v[0] for v in self.hand.longest if v[1] == self.hand.longest[0][1]]
            # if the strongest suit is longest they bid that
            if sum([v in longSuit for v in strongSuit]):
                return Bid.Bid(1, max([v for v in strongSuit if v in longSuit]))
            # if the longest is 5 and has at least a face card they bid that
            for s in strongSuit:
                if len(getattr(self.hand, s)) >= 5:
                    return Bid.Bid(1, s)
            # if we get here there is an issue
            raise(NotImplementedError("Reached a bid we don't know how to do"))

    def raiseBid(self):
        pass

    def jumpBid(self):
        pass



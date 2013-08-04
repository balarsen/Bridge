
"""
class for a begining bridge player bidding

the player will not open with less than 15
 - the player opens in the strongest suit
"""

import Bid
import Bidding

class BeginningBidder(Bidding.Bidding_logic):
    def openBid(self):
        if self.hand.hc <= 14:
            return Bid.Bid('pass', 1)
        else:
            if len(getattr(self.hand, self.hand.strongest)) > 3:
                return Bid.Bid(1, self.hand.strongest)
            elif len(getattr(self.hand, self.hand.longest)) > 3:
                return Bid.Bid(1, self.hand.longest)
            else:
                return Bid.Bid(1, self.hand.strongest)

    def raiseBid(self):
        pass

    def jumpBid(self):
        pass



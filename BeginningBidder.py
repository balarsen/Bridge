
"""
class for a begining bridge player bidding

the player will not open with less than 15
 - the player opens in the strongest suit
"""

import Bidding

class BeginningBidder(Bidding.Bidding_logic):
    def openBid(self):
        if self.hand.hc <= 14:
            return ('pass', 'spades')
        else:
            if len(getattr(self.hand, self.hand.strongest)) > 3:
                return (1, self.hand.strongest)
            elif len(getattr(self.hand, self.hand.longest)) > 3:
                return (1, self.hand.longest)
            else:
                return (1, self.hand.strongest)

    def raiseBid(self):
        pass

    def jumpBid(self):
        pass



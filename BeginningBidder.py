
"""
class for a begining bridge player bidding

the player will not open with less than 15
 - the player opens in the strongest suit
"""

import Bidding


class BeginningBidder(Bidding.Bidding_logic):
    def openBid(self):
        if self.hand.hc_points < 15:
            return ('pass', 'spades')
        # of they don't have 4 in the strongest don't lead that
        if len(self.strongest) >= 4:
            return (1, self.hand.strongest)
        

    def raiseBid(self):
        pass

    def jumpBid(self):
        pass



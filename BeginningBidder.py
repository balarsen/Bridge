
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
        else:


    @abstractmethod
    def raiseBid(self):
        pass

    @abstractmethod
    def jumpBid(self):
        pass



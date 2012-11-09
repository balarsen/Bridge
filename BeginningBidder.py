
"""
class for a begining bridge player bidding

the player will not open with less than 15
 - the player opens in the strongest suit
"""

import Bidding
import Bid

class BeginningBidder(Bidding.Bidding_logic):
    def openBid(self):
        if self.hand.hc < 14:
            return Bid.Bid('pass', 'spades')
        # of they don't have 4 in the strongest don't lead that
        if self.hand.strongest[0][1] >= 4:
            return Bid.Bid(1, self.hand.strongest[0][0])
        elif self.hand.strongest[1][1] >= 4:
            return Bid.Bid(1, self.hand.strongest[1][0])
        else:
            return Bid.Bid('pass', 'spades')
           
    def raiseBid(self):
        pass

    def jumpBid(self):
        pass


if __name__ == '__main__':
    import Deck
    d1 = Deck.Deck()
    d1.shuffle(7)
    h1, h2, h3, h4 = d1.deal()
    b1 = BeginningBidder(h1)
    b2 = BeginningBidder(h2)
    b3 = BeginningBidder(h3)
    b4 = BeginningBidder(h4)
    print h1.hc, h2.hc, h3.hc, h4.hc

    

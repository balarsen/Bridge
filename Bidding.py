
from abc import ABCMeta, abstractmethod
import numpy as np


"""
this module is quite complicated, it will need to both do the mechanics of bidding
but also allow for puggable "smarts" accordng to different conventions
"""

class Redeal(Exception):
    pass

class Bidding_logic(object):
    __metaclass__ = ABCMeta

    def __init__(self, hand): # create an instance per bidder
        self.hand = hand

    @abstractmethod
    def openBid(self):
        pass

    @abstractmethod
    def raiseBid(self, bids):
        pass

    @abstractmethod
    def jumpBid(self, bids):
        pass



class Bidding(list):
    def __init__(self, hands, logic, leader='north'):
        self.leader=leader
        _seats = ['north', 'east', 'south', 'west']
        leader_ind = _seats.index(self.leader)
        self._seats = np.roll(['north', 'east', 'south', 'west'], leader_ind).tolist()
        self._hands = hands
        self._passCount = 0
        self.logic = []
        for logic, hand in zip(logic, self._hands):
            self.logic.append(logic(hand))

    def addBid(self, seat, bid):
        if self._passCount >= 4:  # done
            raise(ValueError('Four passes have already occured'))
        if len(self) > 0: # new bid mist be larger than the old one
            try:
                old_winner = self._winningBid()[1]
            except TypeError:
                old_winner = None
            if old_winner is not None: # we have another bid
                if not bid > old_winner:
                    raise(ValueError('New bid must be higher than old bid'))
        if bid.value == 'pass':
            self._passCount += 1
        else:
            self._passCount = 0
        self.append( (seat, bid) )
        if self._passCount >= 4:  # done
            if not self.opened: # no one opened
                raise(Redeal("No one opened"))
            return self._winningBid()
        else:
            return None

    def _winningBid(self):
        """
        figure the winning bid
        """
        for seat, bid in reversed(self):
            if bid.value != 'pass':
                return (seat, bid)

    def nextBid(self):
        """
        subset of above, just goes in order
        """
        if not self.opened:
            return self.addBid(len(self)%4, self.logic[len(self)%4].openBid())
        else:
            return self.addBid(len(self)%4, self.logic[len(self)%4].raiseBid(self))
            

    @property
    def opened(self):
        """
        return True if someonehas opened, False otherwise
        """
        for bid in self:
            if bid[1].value != 'pass':
                return True
        return False
        

if __name__ == '__main__':
    import Deck
    import BeginningBidder
    d1 = Deck.Deck()
    d1.shuffle(7)
    h1, h2, h3, h4 = d1.deal()
    print h1.hc, h2.hc, h3.hc, h4.hc
    b = Bidding( [h1, h2, h3, h4],
                 [BeginningBidder.BeginningBidder,
                  BeginningBidder.BeginningBidder,
                  BeginningBidder.BeginningBidder,
                  BeginningBidder.BeginningBidder] )







from abc import ABCMeta, abstractmethod
import itertools

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
    def __init__(self, logics, hands, leader='North'):
        self.leader=leader
        _seats = ['North', 'East', 'South', 'West']
        leader_ind = _seats.index(self.leader)
        self._seats = np.roll(['North', 'East', 'South', 'West'], leader_ind).tolist()
        self.nextBidder = itertools.cycle(self._seats)
        self._passCount = 0
        self.hands = hands
        self.logics = []
        for ii, logi in enumerate(logics):
            self.logics.append(logi(self.hands[ii]))

    def nextBid(self):
        """
        add the next bid to the Bidding
        """
        if self._winningBid() is None: # open
            print self.nextBidder.next(), self.logics[len(self)%4].openBid()
            #self.nextBidder.next()

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






from abc import ABCMeta, abstractmethod
import numpy as np


"""
this module is quite complicated, it will need to both do the mechanics of bidding
but also allow for puggable "smarts" accordng to different conventions
"""

class Bidding_logic(object):
    __metaclass__ = ABCMeta

    def __init__(self, hand): # create an instance per bidder
        self.hand = hand

    @abstractmethod
    def openBid(self):
        pass

    @abstractmethod
    def raiseBid(self):
        pass

    @abstractmethod
    def jumpBid(self):
        pass



class Bidding(list):
    def __init__(self, leader='north'):
        self.leader=leader
        _seats = ['north', 'east', 'south', 'west']
        leader_ind = _seats.index(self.leader)
        self._seats = np.roll(['north', 'east', 'south', 'west'], leader_ind).tolist()
        self._passCount = 0

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

    def nextBid(self, bid):
        """
        subset of above, just goes in order
        """
        return self.addBid(self._seats[len(self)%4], bid)




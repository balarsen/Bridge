
import numpy as np

from __init__ import suits
import Bid

"""
this module is quite complicated, it will need to both do the mechanics of bidding
but also allow for puggable "smarts" accordng to different conventions
"""



class Bidding(list):
    def __init__(self, leader='north'):
        self.leader=leader
        _seats = ['north', 'east', 'south', 'west']
        leader_ind = _seats.index(self.leader)
        self._seats = np.roll(['north', 'east', 'south', 'west'], leader_ind).tolist()

    def addBid(self, seat, bid):
        if len(self) > 0: # new bid mist be larger than the old one
            if not bid > self[-1][1]:
                raise(ValueError('New bid must be higher than old bid'))
        self.append( (seat, bid) )

    def nextBid(self, bid):
        """
        subset of above, just goes in order
        """
        self.addBid(self._seats[len(self)%4], bid)




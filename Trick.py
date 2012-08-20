
import copy

import numpy as np

from __init__ import suits


class Trick(list):
    def __init__(self, leader='north', trump=None):
        self.leader=leader
        self.order = None
        if trump not in suits:
            raise(ValueError('invalid trump suit specified'))
        else:
            try:
                int(trump)
                self.trump = suits[trump]
            except ValueError:
                self.trump = trump
        _seats = ['north', 'east', 'south', 'west']
        leader_ind = _seats.index(self.leader)
        self._seats = np.roll(['north', 'east', 'south', 'west'], leader_ind).tolist()

    def nextCard(self, card):
        if len(self) >= 4:
            raise(IndexError('Tricks only have 4 cards'))
        if card.suit == self.trump:
            trump = True
        else:
            trump = False
        card.trump = trump
        self.append(card)

    @property
    def winner(self):
        if len(self) != 4:
            raise(IndexError('Must have 4 cards in the trick'))
        tmp = copy.copy(self)
        tmp.sort()
        winning_card = tmp[-1]
        return winning_card, self._seats[self.index(tmp[-1])]

    @property
    def north(self):
        return self.getCard('north')

    @property
    def south(self):
        return self.getCard('south')

    @property
    def east(self):
        return self.getCard('east')

    @property
    def west(self):
        return self.getCard('west')

    def getCard(self, position):
        ind = self._seats.index(position)
        return self[ind]

    @property
    def fancyRep(self):
        """do a fancy printout"""
        ew_len = len('{0}    {1}'.format(self.west, self.east))
        outStr = ('{0:^' + str(ew_len)+ '}\n').format(self.north)
        outStr += '{0}    '.format(self.west)
        outStr += '{0}\n'.format(self.east)
        outStr += ('{0:^' + str(ew_len)+ '}\n').format(self.south)
        return outStr



from Table import index2pos
from __init__ import positions


class Trick(list):
    def __init__(self, leader='North', trump=None):
        if leader not in positions:
            raise(ValueError('bad leader position: {0}'.format(leader)))
        self.leader = leader
        self.order  = None
        self.trump  = trump

    def nextCard(self, card):
        if self.nCards >= 4:
            raise(IndexError('Cannot have more than 4 cards in a trick'))
        if card in self:
            raise(ValueError('Cannot play the same card twice in a trick'))
        card.trump = card.suit==self.trump
        self.append(card)

    def winner(self):
        if len(self) != 4:
            raise(IndexError('Must have 4 cards in the trick'))
        # there are just 4 cards, look at the first then compare to the next
        #    the highest is the winner
        win = self[0]
        for c in self[1:]:
            if c > win:
                win = c
        # win is the winning card, where was it?
        ind = self.index(win)
        return win, index2pos(self.leader, ind)

    @property
    def nCards(self):
        return len(self)

    @property
    def north(self):
        return self.getCard('North')

    @property
    def south(self):
        return self.getCard('South')

    @property
    def east(self):
        return self.getCard('East')

    @property
    def west(self):
        return self.getCard('West')

    def getCard(self, position):
        ind = self.index(position)
        return self[ind]

    def __str__(self):
        return 'Trick'

    __repr__ = __str__

    def __repr__(self):
        """do a fancy printout"""
        ew_len = len('{0}    {1}'.format(self.west, self.east))
        outStr = ('{0:^' + str(ew_len)+ '}\n').format(self.north)
        outStr += '{0}    '.format(self.west)
        outStr += '{0}\n'.format(self.east)
        outStr += ('{0:^' + str(ew_len)+ '}\n').format(self.south)
        return outStr


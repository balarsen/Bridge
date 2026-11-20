from .Position import Position
from .Suit import Suit


def beats(card, other, trump=None):
    """
    Does `card` beat `other`, the card that is currently winning the trick?

    Trump is a suit (anything else, None or 'notrump', means no trump).  A card
    beats another of its own suit by value, and any trump beats a non-trump.  A
    card that is neither of the suit of `other` nor a trump can never win.
    """
    if card.suit_index == other.suit_index:
        return card.rank > other.rank
    return card.suit_index == Suit.indices.get(trump, -1)


class Trick(list):
    """
    The (up to) four cards played in one trick, in the order they were played.
    """
    def __init__(self, leader='north', trump=None):
        super().__init__()
        self.leader = Position.name(leader)  # ValueError if bad
        self.trump = trump

    @property
    def trump(self):
        return self._trump

    @trump.setter
    def trump(self, trump):
        self._trump = trump
        self._trump_index = Suit.indices.get(trump, -1)  # -1: no trump

    def nextCard(self, card):
        if self.nCards >= 4:
            raise(IndexError('Cannot have more than 4 cards in a trick'))
        code = card.code
        for c in self:
            if c.code == code:
                raise(ValueError('Cannot play the same card twice in a trick'))
        self.append(card)

    @property
    def leadSuit(self):
        """the suit that was led"""
        if not self:
            raise(IndexError('No cards have been played'))
        return self[0].suit

    def _winning(self):
        """(index in the trick, card) of the card that is winning so far"""
        if not self:
            raise(IndexError('No cards have been played'))
        trump = self._trump_index
        win_i = 0
        win = self[0]
        for i in range(1, len(self)):
            c = self[i]
            if c.suit_index == win.suit_index:
                if c.rank > win.rank:
                    win_i, win = i, c
            elif c.suit_index == trump:
                win_i, win = i, c
        return win_i, win

    def currentWinner(self):
        """
        the (card, position) that is winning with the cards played so far
        """
        win_i, win = self._winning()
        return win, Position.index2pos(self.leader, win_i)

    def wouldWin(self, card):
        """would `card`, played next, take the lead in the trick as it stands"""
        win = self._winning()[1]
        if card.suit_index == win.suit_index:
            return card.rank > win.rank
        return card.suit_index == self._trump_index

    def winner(self):
        if len(self) != 4:
            raise(IndexError('Must have 4 cards in the trick'))
        return self.currentWinner()

    @property
    def nCards(self):
        return len(self)

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
        """the card played by a seat, None if they have not played yet"""
        ind = Position.pos2index(self.leader, position)
        try:
            return self[ind]
        except IndexError:
            return None

    def __repr__(self):
        """do a fancy printout"""
        ew_len = len('{0}    {1}'.format(self.west, self.east))
        outStr = ('{0:^' + str(ew_len) + '}\n').format(str(self.north))
        outStr += '{0}    '.format(self.west)
        outStr += '{0}\n'.format(self.east)
        outStr += ('{0:^' + str(ew_len) + '}\n').format(str(self.south))
        return outStr

    def __str__(self):
        return 'Trick'

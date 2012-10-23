
from __init__ import suits
import collections #.Counter as Counter

class Hand(list):
    """
    needs to build from a deck, get cards, know how many there are and collect points
    """
    def __init__(self, c):
        if len(c) != 13:
            raise(ValueError('wrong number of cards in a hard'))
        super(Hand, self).__init__(c)
        # careful here only one hard per call
        self.n_cards = len(self)
        self.n_suits()
        self.balanced = None
        self.distro = None
        self.pps = collections.Counter() # points per suit
        self._pps()
        self.n_suits()
        self.is_balanced()
        # number of points per suit
        # TODO do we need a longest instance variable?

    def __str__(self):
        self.sort()
        lst = [val for val in self]
        return str(lst)

    __repr__ = __str__

    @property
    def clubs(self):
        """
        return all the clubs or ()
        """
        return tuple([v for v in self if v.suit == 'clubs'])

    @property
    def spades(self):
        """
        return all the spades or ()
        """
        return tuple([v for v in self if v.suit == 'spades'])

    @property
    def hearts(self):
        """
        return all the hearts or ()
        """
        return tuple([v for v in self if v.suit == 'hearts'])

    @property
    def diamonds(self):
        """
        return all the diamonds or ()
        """
        return tuple([v for v in self if v.suit == 'diamonds'])

    @property
    def highCard(self):
        """
        return the highest card in a hand
        """
        return max(self)

    @property
    def longest(self):
        """
        the longest suit
        """
        points = {}
        for suit in suits:
            points[suit] = sum([1 for val in self if val.suit == suit])
        return max(points)
                
    @property
    def strongest(self):
        """
        the strongest suit
        """
        points = {}
        for suit in suits:
            points[suit] = sum([val.hc for val in self if val.suit == suit])
        return max(points)
        
    @property
    def hc_points(self):
        tmp = sum([val.hc for val in self])
        return tmp

    @property
    def distro(self):
        suits = [val.suit for val in self]
        distro = {'spades':suits.count('spades'),
                  'hearts':suits.count('hearts'),
                  'diamonds':suits.count('diamonds'),
                  'clubs':suits.count('clubs')}
        return distro        

    @property
    def balanced(self):
        """
        count the number of each suit looking for balanced hands
        balanced hands are 4,3,3,3  5,3,3,2  4,4,3,2
        """
        tmp = self.distro.values()
        tmp.sort()
        bal = [tmp == [2,3,4,4],
               tmp == [2,3,3,5],
               tmp == [3,3,3,4]]
        if any(bal):
            return True
        else:
            return False








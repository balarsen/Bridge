
from __init__ import suits


class Hand(list):
    """
    needs to build from a deck, get cards, know how many there are and collect points
    """
    def __init__(self, c):
        if len(c) != 13:
            raise(ValueError('wrong number of cards in a hard'))
        self.cards = c
        # careful here only one hard per call
        self.n_cards = len(self)

    def __str__(self):
        self.sort()
        lst = [val for val in self.cards]
        return str(lst)

    __repr__ = __str__

    @property
    def longest(self):
        """
        the longest suit
        """
        points = {}
        for suit in suits:
            points[suit] = sum([1 for val in self.cards if val.suit == suit])
        max = (0, None)
        for key in points:
            if points[key] > max[0]:
                mx = (points[key], key)
        return mx[1]
                
    @property
    def strongest(self):
        """
        the strongest suit
        """
        points = {}
        for suit in suits:
            points[suit] = sum([val.hc for val in self.cards if val.suit == suit])
        max = (0, None)
        for key in points:
            if points[key] > max[0]:
                mx = (points[key], key)
        return mx[1]
        
    @property
    def hc_points(self):
        tmp = sum([val.hc for val in self.cards])
        return tmp

    @property
    def distro(self):
        suits = [val.suit for val in self.cards]
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








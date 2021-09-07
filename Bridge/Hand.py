
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
        return sorted(tuple([v for v in self if v.suit == 'clubs']), reverse=True)

    @property
    def spades(self):
        """
        return all the spades or ()
        """
        return sorted(tuple([v for v in self if v.suit == 'spades']), reverse=True)

    @property
    def hearts(self):
        """
        return all the hearts or ()
        """
        return sorted(tuple([v for v in self if v.suit == 'hearts']), reverse=True)

    @property
    def diamonds(self):
        """
        return all the diamonds or ()
        """
        return sorted(tuple([v for v in self if v.suit == 'diamonds']), reverse=True)

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
        TODO update this so that it returns a list of suits in order
        """
        cps = collections.Counter()
        for crd in self:
            cps += collections.Counter( {crd.suit} )
        return sorted(cps.items(), reverse=True, key=lambda x:x[1])

    @property
    def strongest(self):
        """
        the strongest suit
        TODO update this so that it returns a list of suits in order
        """
        pps = collections.Counter()
        for crd in self:
            pps += collections.Counter( {crd.suit:crd.hc} )
        return sorted(pps.items(), reverse=True, key=lambda x:x[1])
        
    @property
    def hc(self):
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
        bal = [tmp == [2, 3, 4, 4],
               tmp == [2, 3, 3, 5],
               tmp == [3, 3, 3, 4]]
        if any(bal):
            return True
        else:
            return False








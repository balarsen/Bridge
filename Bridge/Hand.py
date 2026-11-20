import functools

from .Scorers import SimpleHighCardValue
from .Suit import Suit


class Hand(list):
    """
    needs to build from a deck, get cards, know how many there are and collect points
    """

    def __init__(self, c):
        if len(c) != 13:
            raise (ValueError('wrong number of cards in a hand'))
        super(Hand, self).__init__(c)

    def __str__(self):
        # self.sort()
        lst = " ".join([str(val) for val in self])
        return lst

    def __repr__(self):
        return f"<hand object: {len(self)} cards>"

    def get_suit(self, suit):
        return sorted([v for v in self if v.suit == suit], reverse=True)

    clubs = functools.partialmethod(get_suit, suit='clubs')
    hearts = functools.partialmethod(get_suit, suit='hearts')
    diamonds = functools.partialmethod(get_suit, suit='diamonds')
    spades = functools.partialmethod(get_suit, suit='spades')

    def highCard(self, suit):
        """
        return the highest card in a suit
        """
        return max(self.get_suit(suit))

    def lowCard(self, suit):
        """
        return the lowest card in a suit
        """
        return min(self.get_suit(suit))

    def distro(self):
        """
        the distro of each suit
        """
        ans = []
        for s in Suit.suits:
            ans.append((s, len(self.get_suit(s))))
        return tuple(ans)

    def hcp(self):
        """
        high card points of the whole hand (A=4, K=3, Q=2, J=1)
        """
        return sum(SimpleHighCardValue.cardScorer(c) for c in self)

    def longest(self):
        """
        [(suit, length), ...] longest first.  Ties keep the bridge suit rank order,
        spades, hearts, diamonds, clubs
        """
        return sorted(((s, n) for s, n in self.distro()), key=lambda x: -x[1])

    def strongest(self):
        """
        [(suit, high card points), ...] strongest first.  Ties keep the bridge suit rank order,
        spades, hearts, diamonds, clubs
        """
        pts = ((s, sum(SimpleHighCardValue.cardScorer(c) for c in self.get_suit(s)))
               for s in Suit.suits)
        return sorted(pts, key=lambda x: -x[1])

    def balanced(self):
        """
        balanced hands are 4,3,3,3  4,4,3,2  5,3,3,2
        """
        shape = tuple(sorted((n for _, n in self.distro()), reverse=True))
        return shape in ((4, 3, 3, 3), (4, 4, 3, 2), (5, 3, 3, 2))

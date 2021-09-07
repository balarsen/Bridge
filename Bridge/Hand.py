import functools

from .Suit import Suit


class Hand(list):
    """
    needs to build from a deck, get cards, know how many there are and collect points
    """

    def __init__(self, c):
        if len(c) != 13:
            raise (ValueError('wrong number of cards in a hard'))
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

    # def balanced(self):
    #     """
    #     count the number of each suit looking for balanced hands
    #     balanced hands are 4,3,3,3  5,3,3,2  4,4,3,2
    #
    #     #TODO, likely this goes in a scoring class
    #     """
    #     dist = set([v[1] for v in self.distro()])
    #     if dist == set([2, 3, 4, 4]):
    #         return True
    #     elif dist == set([2, 3, 3, 5]):
    #         return True
    #     elif dist == set([3, 3, 3, 4]):
    #         return True
    #     else:
    #         return False

import functools

from .Scorers import SimpleHighCardValue
from .Suit import Suit


def _rank(card):
    return card.rank


def _invalidating(name):
    """a list method that changes which cards are in the hand: run it, then forget the per-suit cache"""
    base = getattr(list, name)

    def method(self, *args, **kwargs):
        result = base(self, *args, **kwargs)
        self._by_suit = None
        return result

    method.__name__ = name
    return method


class Hand(list):
    """
    needs to build from a deck, get cards, know how many there are and collect points

    It is a list of the cards still in the hand, in the order they were dealt.  `original` is the 13 cards
    as dealt and `played` the cards played from it so far, in order (the n-th card played in trick n);
    `play(card)` takes a card out of the hand and records it, while `remove` only takes it out.  Behind that
    it keeps the cards by suit, each suit
    sorted highest first, built the first time it is needed and kept up to date when a card is removed, so
    `get_suit`, `distro`, `longest`, ... are lookups instead of a filter and a sort over the 13 cards.  Any
    other change to the list (append, del, slice assignment, ...) just throws that cache away.
    """
    _by_suit = None

    def __init__(self, c):
        if len(c) != 13:
            raise (ValueError('wrong number of cards in a hand'))
        super(Hand, self).__init__(c)
        self.original = tuple(c)
        self.played = []

    def _suits(self):
        """the cards of each suit, highest first, indexed like Suit.suits"""
        by_suit = self._by_suit
        if by_suit is None:
            by_suit = [[], [], [], []]
            for card in self:
                by_suit[card.suit_index].append(card)
            for cards in by_suit:
                cards.sort(key=_rank, reverse=True)
            self._by_suit = by_suit
        return by_suit

    def remove(self, card):
        """remove the first card equal to `card`, like list.remove, but without calling Card.__eq__ on the way"""
        code = getattr(card, 'code', None)
        if code is None:  # not a Card: let list.remove say it is not in the hand
            return list.remove(self, card)
        for i, c in enumerate(self):
            if c.code == code:
                list.__delitem__(self, i)
                break
        else:
            raise ValueError('list.remove(x): x not in list')
        by_suit = self._by_suit
        if by_suit is not None:
            cards = by_suit[card.suit_index]
            for i, c in enumerate(cards):  # pragma: no branch  (the cache holds every card, so this always finds it)
                if c.code == code:
                    del cards[i]
                    break

    def play(self, card):
        """play a card: take it out of the hand and remember that it was played"""
        self.remove(card)
        self.played.append(card)

    def __str__(self):
        # self.sort()
        lst = " ".join([str(val) for val in self])
        return lst

    def __repr__(self):
        return f"<hand object: {len(self)} cards>"

    def get_suit(self, suit):
        """the cards of a suit (a name or a Suit), highest first, as a new list"""
        index = suit.index if type(suit) is Suit else Suit.indices.get(suit)
        if index is None:
            return []
        return list(self._suits()[index])

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
        by_suit = self._suits()
        return tuple((s, len(by_suit[i])) for i, s in enumerate(Suit.suits))

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
        return sorted(self.distro(), key=lambda x: -x[1])

    def strongest(self):
        """
        [(suit, high card points), ...] strongest first.  Ties keep the bridge suit rank order,
        spades, hearts, diamonds, clubs
        """
        by_suit = self._suits()
        pts = ((s, sum(SimpleHighCardValue.cardScorer(c) for c in by_suit[i]))
               for i, s in enumerate(Suit.suits))
        return sorted(pts, key=lambda x: -x[1])

    def balanced(self):
        """
        balanced hands are 4,3,3,3  4,4,3,2  5,3,3,2
        """
        shape = tuple(sorted((len(cards) for cards in self._suits()), reverse=True))
        return shape in ((4, 3, 3, 3), (4, 4, 3, 2), (5, 3, 3, 2))


# every other way of changing the cards in the hand invalidates the per-suit cache
for _name in ('append', 'extend', 'insert', 'pop', 'clear', '__setitem__', '__delitem__', '__iadd__', '__imul__'):
    setattr(Hand, _name, _invalidating(_name))

from .Suit import Suit
from .Value import Value


class Card(object):
    """
    A class to represent a Card

    Cards only know their own suit and value.  Which card wins a trick depends
    on the lead and the trump suit, that lives in Trick (see Trick.beats).

    A card is immutable.  `suit_index`, `rank` and `code` (`suit_index * 13 + rank`, the position
    in an unshuffled `Deck()`) are worked out once at creation so that comparing cards is integer
    arithmetic.  The 52 cards are created once, `ALL_CARDS`, and `Deck` and `Card.fromCode` hand out
    those shared objects, which is safe because they cannot change.
    """

    def __init__(self, value, suit):
        value = Value(value)  # raises ValueError for a bad value, returns a Value unchanged
        suit = Suit(suit)
        object.__setattr__(self, 'value', value)
        object.__setattr__(self, 'suit', suit)
        object.__setattr__(self, 'suit_index', suit.index)
        object.__setattr__(self, 'rank', value.rank)
        object.__setattr__(self, 'code', suit.index * 13 + value.rank)

    def __setattr__(self, name, value):
        raise AttributeError('a Card is immutable')

    def __delattr__(self, name):
        raise AttributeError('a Card is immutable')

    def __reduce__(self):
        return (Card, (self.value, self.suit))  # copying and pickling go through the constructor

    def __eq__(self, other):
        if other.__class__ is Card:
            return self.code == other.code
        if isinstance(other, Card):  # a subclass
            return self.code == other.code
        return NotImplemented

    def __ne__(self, other):
        if other.__class__ is Card:
            return self.code != other.code
        if isinstance(other, Card):
            return self.code != other.code
        return NotImplemented

    def __hash__(self):
        return self.code

    def __lt__(self, other):
        """
        Only cards of the same suit are ordered, comparing cards of different
        suits gives False for both < and >
        """
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit_index == other.suit_index and self.rank < other.rank

    def __gt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit_index == other.suit_index and self.rank > other.rank

    def __str__(self):
        return f"{self.value} of {self.suit}"

    def __repr__(self):
        return f"<{self.value} of {self.suit}>"

    def toCode(self):
        """
        encode a card into a 2 letter code <value|suit>
        """
        return str(self.value) + str(self.suit)[0]

    @staticmethod
    def fromCode(code):
        """
        return a card from the 2 letter code <value|suit>
        """
        card = _BY_CODE.get(code)
        if card is None:  # not one of the 52 codes, build it the long way (this raises for a bad one)
            return Card(code[0], Suit.letterToSuit(code[1]))
        return card


# the 52 cards in the order of an unshuffled deck: spades 2..A, hearts, diamonds, clubs
ALL_CARDS = tuple(Card(v, s) for s in Suit.suits for v in Value.values)
_BY_CODE = {c.toCode(): c for c in ALL_CARDS}

from .Suit import Suit
from .Value import Value


class Card(object):
    """
    A class to represent a Card
    """

    def __init__(self, value, suit, trump=False):
        self.trump = trump
        if isinstance(value, Value):
            self.value = value
        else:
            self.value = Value(value)
        if isinstance(suit, Suit):
            self.suit = suit
        else:
            self.suit = Suit(suit)

    def __eq__(self, other):
        return self.suit == other.suit and self.value == other.value

    def __ne__(self, other):
        return ~(self == other)

    def __lt__(self, other):
        if self.trump and other.trump:  # both are trump
            return self.value < other.value
        elif self.trump:  # self is trump
            return False
        elif other.trump:  # other is trump
            return True
        elif self.suit == other.suit:  # same suits
            return self.value < other.value
        else:  # different suit, can't compare
            return False

    def __gt__(self, other):
        if self.trump and other.trump:  # both are trump
            return self.value > other.value
        elif self.trump:  # self is trump
            return True
        elif other.trump:  # other is trump
            return False
        elif self.suit == other.suit:  # same suits
            return self.value > other.value
        else:  # different suit, can't compare
            return False

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
        return Card(code[0], Suit.letterToSuit(code[1]))

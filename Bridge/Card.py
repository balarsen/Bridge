from .Suit import Suit
from .Value import Value


class Card(object):
    """
    A class to represent a Card
    """

    def __init__(self, value, suit, trump=False):
        self.trump = trump
        self.value = Value(value)
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

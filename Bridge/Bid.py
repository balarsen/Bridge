
from . import suits


class Bid(object):
    def __init__(self, value, suit, trump=False):
        if not (value in list(range(1,8))+['pass']):
            raise(ValueError("Bid has bad value: {0}".format(value)))
        if not (suit in suits):
            raise(ValueError("Bid has bad suit: {0}".format(suit)))
        self.value = value
        self.suit  = suits[suit]

    def __eq__(self, other):
        if self.value == other.value and self.suit == other.suit:
            return True
        else:
            return False

    def __ne__(self, other):
        if self.value == other.value and self.suit == other.suit:
            return False
        else:
            return True

    def __gt__(self, other):
        if self.value > other.value:
            return True
        elif suits[self.suit] > suits[other.suit]:
            return True
        else:
            return False

    def __lt__(self, other):
        if self.value < other.value:
            return True
        elif suits[self.suit] < suits[other.suit]:
            return True
        else:
            return False

    def __repr__(self):
        if self.value == 'pass':
            return '{value}'.format(value=self.value, suit=suits[self.suit])
        elif self.value == 1:
            return '{value} {suit}'.format(value=self.value, suit=suits[self.suit][:-1])
        else:
            return '{value} {suit}'.format(value=self.value, suit=suits[self.suit])

    __str__ = __repr__




from __init__ import suits, values


class Card(object):
    __version__ = '0.0.1'
    __author__ = 'Brian Larsen'

    def __init__(self, v, s, trump=False):
        if not (v in values):
            raise(ValueError("Card has bad value"))
        if not (s in suits):
            raise(ValueError("Card has bad suit"))
        self.trump = trump
        self.value = values[v]
        self.suit  = suits[s]

    def __eq__(self, other):
        if self.suit == other.suit and self.value == other.value:
            return True
        else:
            return False

    def __ne__(self, other):
        if self == other:
            return False
        else:
            return True

    def __lt__(self, other):
        if self.trump == other.trump:
            if values[self.value] < values[other.value]:
                return True
            else:
                return False
        elif self.trump:
            return False
        else:
            return True

    def __gt__(self, other):
        if self.trump == other.trump:
            if values[self.value] > values[other.value]:
                return True
            else:
                return False
        elif self.trump:
            return True
        else:
            return False

    @property
    def hc(self):
        tmp = values[self.value] - 10
        if tmp > 0:
            return tmp
        else:
            return 0

    def __str__(self):
        return "%s of %s" % (self.value, self.suit)

    __repr__ = __str__

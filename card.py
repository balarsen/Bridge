

from value import value
from suit import suit

class card(suit, value):
    __version__ = '0.0.1'
    __author__ = 'Brian Larsen'

    def __init__(self, v, s):

        if not (v in value.values):
            raise(Exception("Card has bad value"))
        if not (s in suit.suits):
            raise(Exception("Card has bad suit"))
        self.value = value.values[v]
        self.suit  = suit.suits[s]
        self._hc = self._hc_points()

    def _valid(self):
        pass

    def _hc_points(self):
        tmp = value.values[self.value] - 10
        if tmp > 0:
            return tmp
        else:
            return 0

    def __str__(self):
        return "%s of %s" % (self.value, self.suit)

    __repr__ = __str__

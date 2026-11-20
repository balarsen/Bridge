import functools


@functools.total_ordering
class Bid(object):
    """
    A bid is a level (1-7) and a strain, or a pass.

    Bids order by level and then by strain, clubs < diamonds < hearts < spades < notrump.
    A pass has no strain and orders below every real bid.
    """
    strains = ('clubs', 'diamonds', 'hearts', 'spades', 'notrump')
    levels = tuple(range(1, 8))

    def __init__(self, value, suit=None):
        if value != 'pass' and value not in Bid.levels:
            raise(ValueError(f"Bid has bad value: {value!r}"))
        if value == 'pass':
            suit = None  # a pass has no strain, anything handed in is ignored
        elif suit not in Bid.strains:
            raise(ValueError(f"Bid has bad suit: {suit!r}, must be one of {Bid.strains}"))
        self.value = value
        self.suit = suit

    @property
    def isPass(self):
        return self.value == 'pass'

    def _key(self):
        if self.isPass:
            return (0, -1)
        return (self.value, Bid.strains.index(self.suit))

    def __eq__(self, other):
        if not isinstance(other, Bid):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other):
        if not isinstance(other, Bid):
            return NotImplemented
        return self._key() < other._key()

    def __hash__(self):
        return hash(self._key())

    def __repr__(self):
        if self.isPass:
            return 'pass'
        return f'{self.value} {self.suit}'

    __str__ = __repr__

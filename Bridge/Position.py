import itertools


class Position(object):
    """
    A seat at the table.  Positions are lower case strings, a Position
    compares equal to its string so 'north' and Position('north') interchange.
    """
    positions = ('north', 'east', 'south', 'west')
    positions_set = set(positions)

    def __init__(self, position):
        if isinstance(position, Position):
            position = position.position
        if position not in Position.positions_set:
            raise (ValueError(f'Bad position {position!r}, must be one of {Position.positions}'))
        self.position = position

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.position == other.position
        return self.position == other

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.position)

    def __str__(self):
        return f"{self.position}"

    def __repr__(self):
        return f"<{self.position}>"

    @staticmethod
    def name(position):
        """the lower case name of a seat given as a string or a Position, ValueError if it is not a seat"""
        return Position.positions[_index(position)]

    @staticmethod
    def cycle(dealer):
        """endless iterator of seat names starting at dealer and going clockwise"""
        start = _index(dealer)
        return itertools.cycle(Position.positions[start:] + Position.positions[:start])

    @staticmethod
    def index2pos(leader, index):
        """the seat `index` places clockwise of leader"""
        return Position.positions[(index + _index(leader)) % 4]

    @staticmethod
    def pos2index(leader, pos):
        """how many places clockwise of leader is pos (0 to 3)"""
        return (_index(pos) - _index(leader)) % 4

    @staticmethod
    def side(pos):
        """'ns' or 'ew'"""
        return 'ns' if _index(pos) % 2 == 0 else 'ew'


_INDEX = {p: i for i, p in enumerate(Position.positions)}


def _index(position):
    """0 to 3 for north, east, south, west, from a name or a Position (a dict lookup, no objects are built)"""
    try:
        return _INDEX[position]
    except KeyError:
        raise ValueError(f'Bad position {position!r}, must be one of {Position.positions}') from None

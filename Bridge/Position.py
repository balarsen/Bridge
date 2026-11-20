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
    def cycle(dealer):
        """endless iterator of seat names starting at dealer and going clockwise"""
        start = Position.positions.index(str(Position(dealer)))
        return itertools.cycle(Position.positions[start:] + Position.positions[:start])

    @staticmethod
    def index2pos(leader, index):
        """the seat `index` places clockwise of leader"""
        start = Position.positions.index(str(Position(leader)))
        return Position.positions[(index + start) % 4]

    @staticmethod
    def pos2index(leader, pos):
        """how many places clockwise of leader is pos (0 to 3)"""
        start = Position.positions.index(str(Position(leader)))
        return (Position.positions.index(str(Position(pos))) - start) % 4

    @staticmethod
    def side(pos):
        """'ns' or 'ew'"""
        return 'ns' if str(Position(pos)) in ('north', 'south') else 'ew'

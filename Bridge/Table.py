from .Position import Position


class Seat(object):
    """
    one seat at the table and the score it has accumulated
    """
    def __init__(self, pos):
        self.position = Position(pos)
        self.score = 0


class Table(object):
    """
    class to hold the table and keep the overall score
    """
    def __init__(self):
        self.north = Seat('north')
        self.east = Seat('east')
        self.south = Seat('south')
        self.west = Seat('west')

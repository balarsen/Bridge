import itertools

import numpy as np


class Position(object):
    positions = ('north', 'east', 'south', 'west')
    positions_set = set(positions)

    def __init__(self, position):
        if position not in Position.positions_set:
            raise (ValueError(f'Bad position {Position.positions}'))
        self.position = position

    def __eq__(self, other):
        return self.position == other.position

    def __ne__(self, other):
        return self.position != other.position

    def __str__(self):
        return f"{self.position}"

    def __repr__(self):
        return f"<{self.position}>"

    @staticmethod
    def cycle(dealer):
        Position(dealer)  # will error if a bad position
        return itertools.cycle(np.roll(Position.positions, -1 * Position.positions.index(dealer)))


_positions = ['North', 'East', 'South', 'West']

class position(object):
    def __init__(self, pos):
        if pos not in _positions:
            raise(ValueError('Bad position input: {0}, must be {1}'.format(pos, _positions)))
        self.poisition = pos
        self.score = 0

class Table(list):
    """
    class to hold the table and keep the overall score
    """
    def __init__(self):
        self.north = position('North')
        self.east  = position('East')
        self.south = position('South')
        self.west  = position('West')


def index2pos(leader, index):
    """
    given an index return the position of the winner
    """
    start = _positions.index(leader)
    ind = (index + start) % 4
    return _positions[ind]
    


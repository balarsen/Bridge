


class Trick(dict):
    def __init__(self, leader='north', trump=None):
        super(Trick, self).__init__(self)
        self.leader=leader
        self.sides = ['north', 'east', 'south', 'west', 'north', 'east', 'south', 'west']
        self.order = None
        self.nCards = 0
        self.trump = trump

    def setLeader(self, card):
        self[self.leader] = card
        self.order = self.sides[self.sides.index('south'):self.sides.index('south')+4]
        self.nCards += 1

    def nextCard(self, card):
        self[self.order[self.nCards]] = card
        self.nCards += 1

    def winner(self):
        if self.nCards != 4:
            raise(ValueError('Must have 4 cards in the trick'))
        tmp = [self['north'], self['south'], self['west'], self['east']]
        tmp.sort()
        winning_card = tmp[-1]

        for key, val in self.iteritems():
            if val == winning_card:
                print winning_card









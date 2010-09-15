

from card import card

class deck(object):
    def __init__(self):
        import numpy
        cards = []
        for i in range(2, 15):
            for j in range(1, 5):
                cards.append(card(i, j))
        self.cards = numpy.array(cards)

    def shuffle(self, num=1):
        import random
        for i in range(num):
            random.shuffle(self.cards)

    def cut(self, place=None):
        from numpy.random import randint
        import numpy
        if place == None:
            place = randint(1, 53)
        dtmp = self.cards[place:]
        dtmp = numpy.append(dtmp, self.cards[:place])
        self.cards = dtmp

    def deal(self):
        h1 = self.cards[range(0,52,4)]
        h2 = self.cards[range(1,52,4)]
        h3 = self.cards[range(2,52,4)]
        h4 = self.cards[range(3,52,4)]
        return h1, h2, h3, h4

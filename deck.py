import random

from card import card
from hand import hand

class deck(list):
    def __init__(self):
        cards = []
        for i in range(2, 15):
            for j in range(1, 5):
                cards.append(card(i, j))
        self.extend(cards)

    def shuffle(self, num=1):
        for i in range(num):
            random.shuffle(self.cards)

    def cut(self, place=None):
        if place == None:
            place = random.randint(1, 53)
        dtmp = self.cards[place:]
        dtmp.extend(self[:place])
        self.cards = dtmp

    def deal(self):
        h1 = self.cards[range(0,52,4)]
        h2 = self.cards[range(1,52,4)]
        h3 = self.cards[range(2,52,4)]
        h4 = self.cards[range(3,52,4)]
        return hand(h1), hand(h2), hand(h3), hand(h4)

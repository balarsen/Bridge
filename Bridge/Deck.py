import itertools
import random

from .Card import Card
from .Hand import Hand
from .Suit import Suit
from .Value import Value


class Deck(list):
    def __init__(self):
        for s, v in itertools.product(Suit.suits, Value.values):
            self.append(Card(v, s))

    def shuffle(self, num=1):
        for i in range(num):
            random.shuffle(self)

    def cut(self, place=None):
        if place == None:
            place = random.randint(1, 53)
        dtmp = self[place:]
        dtmp.extend(self[:place])
        self[:] = dtmp

    def deal(self):
        h1 = self[0::4]
        h2 = self[1::4]
        h3 = self[2::4]
        h4 = self[3::4]
        return Hand(h1), Hand(h2), Hand(h3), Hand(h4)

    def __eq__(self, other):
        """equal if cards in same order"""
        return tuple(self) == tuple(other)

    def __ne__(self, other):
        return tuple(self) != tuple(other)

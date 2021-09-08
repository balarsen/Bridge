import itertools
import random

from .Card import Card
from .Hand import Hand
from .Suit import Suit
from .Value import Value


class Deck(list):
    def __init__(self, indeck=None, shuffle=None):
        if indeck is None:
            for s, v in itertools.product(Suit.suits, Value.values):
                self.append(Card(v, s))
        else:
            for c in indeck:
                self.append(c)
        if shuffle is not None:
            self.shuffle(shuffle)

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

    def toCode(self):
        return ''.join(c.toCode() for c in self)

    @staticmethod
    def fromCode(inval):
        """
        take a strong encoded with stringRep and make a deck
        """
        cards = [Card(v, Suit.letterToSuit(s)) for v, s in zip(inval[::2], inval[1::2])]
        return Deck(cards)

"""
This class plays a Round of bridge
that is after trump and contrct is established plays all the hands

It needs to have pluggable playstyle for each player seperately
"""

from abc import ABC, abstractmethod
import itertools

from .Position import Position
from .Suit import Suit
from .Trick import Trick


class HandLogic(ABC):
    """
    this is the logic that is used to play a hand
    """
    def __init__(self, hand, trump):
        self.hand = hand
        self.trump = trump

    @abstractmethod
    def lead(self):
        """return the card to lead"""

    @abstractmethod
    def follow(self, trick):
        """return the card to play given the Trick so far, trick[0] is the lead"""


class simpleHigh(HandLogic):
    """
    this player leads their highest card, when following they win if they can
    otherwise play their lowest card
    """
    def lead(self):
        # highest value, ties go to the higher ranking suit
        return max(self.hand, key=lambda c: (c.value.rank, -Suit.suits.index(str(c.suit))))

    def follow(self, trick):
        in_suit = self.hand.get_suit(trick.leadSuit)

        if in_suit:  # we have some of what was led
            if trick.wouldWin(in_suit[0]):  # if we can beat it, do
                return in_suit[0]
            return in_suit[-1]  # otherwise play lowest card

        # void in the lead suit
        if self.trump in Suit.suits_set and trick.leadSuit != self.trump:
            trumps = self.hand.get_suit(self.trump)
            if trumps:
                return trumps[-1]  # play the smallest trump
        return min(self.hand, key=lambda c: c.value.rank)


class Round(object):
    def __init__(self, table, hands, trump, logics):
        """
        hands and logics are in table order, north, east, south, west
        trump is a suit or 'notrump'
        """
        self.table = table
        self.trump = trump
        self.hands = hands
        self.logics = [logi(self.hands[ii], self.trump) for ii, logi in enumerate(logics)]
        self.tricks = []
        self.winners = []

    def play_trick(self, leader):
        """play one trick, returns (winning card, winning position)"""
        trick = Trick(leader, self.trump)
        for ii, seat in enumerate(itertools.islice(Position.cycle(leader), 4)):
            ind = Position.positions.index(seat)
            logic = self.logics[ind]
            card = logic.lead() if ii == 0 else logic.follow(trick)
            trick.nextCard(card)
            self.hands[ind].remove(card)
        self.tricks.append(trick)
        win = trick.winner()
        self.winners.append(win[1])
        return win

    def play(self, leader='north'):
        """
        play all 13 tricks, the winner of a trick leads the next one
        returns the tricks won by (north-south, east-west)
        """
        for _ in range(13):
            leader = self.play_trick(leader)[1]
        return (sum(Position.side(w) == 'ns' for w in self.winners),
                sum(Position.side(w) == 'ew' for w in self.winners))

"""
This class plays a Round of bridge
that is after trump and contrct is established plays all the hands

It needs to have pluggable playstyle for each player seperately
"""

from abc import ABC, abstractmethod

from .Knowledge import Knowledge
from .Position import Position
from .Suit import Suit
from .Trick import Trick


class HandLogic(ABC):
    """
    this is the logic that is used to play a hand

    A strategy that counts cards sets `counts_cards = True`: `Round` then gives it a `Knowledge` object,
    `self.knowledge`, kept up to date as the cards are played.  (It is None otherwise, and when the
    strategy is used outside a `Round`.)
    """
    counts_cards = False
    knowledge = None

    def __init__(self, hand, trump):
        self.hand = hand
        self.trump = trump

    @abstractmethod
    def lead(self):
        """return the card to lead"""

    @abstractmethod
    def follow(self, trick):
        """return the card to play given the Trick so far, trick[0] is the lead"""


def _rank(card):
    return card.rank


def _lead_key(card):
    # highest value, ties go to the higher ranking suit (lower suit index): one integer instead of a tuple
    return card.rank * 4 - card.suit_index


class simpleHigh(HandLogic):
    """
    this player leads their highest card, when following they win if they can
    otherwise play their lowest card
    """
    def lead(self):
        # highest value, ties go to the higher ranking suit
        return max(self.hand, key=_lead_key)

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
        return min(self.hand, key=_rank)


class countingHigh(simpleHigh):
    """
    simpleHigh that counts cards: it leads a card that is certain to win (the highest card still out in its
    suit, so nobody can beat it, and nobody can trump it) before it falls back to its highest card.
    """
    counts_cards = True

    def lead(self):
        k = self.knowledge
        if k is not None:
            trump = Suit.indices.get(self.trump, -1)
            safe_from_trumps = trump < 0 or not k.outstanding(Suit.suits[trump])  # nobody can ruff
            masters = [c for c in self.hand
                       if k.is_master(c) and (c.suit_index == trump or safe_from_trumps)]
            if masters:
                return max(masters, key=_lead_key)
        return super().lead()


class Round(object):
    def __init__(self, table, hands, trump, logics, declarer=None):
        """
        hands and logics are in table order, north, east, south, west
        trump is a suit or 'notrump'
        declarer is the seat that plays the hand, if there is a contract: the opening lead is then made by
        the player on declarer's left, and after it the dummy (declarer's partner) puts their hand on the
        table, which the players that count cards see
        """
        self.table = table
        self.trump = trump
        self.hands = hands
        self.declarer = None if declarer is None else Position.name(declarer)
        self.logics = [logi(self.hands[ii], self.trump) for ii, logi in enumerate(logics)]
        self.tricks = []
        self.winners = []
        self.knowledge = None
        self._dummy_shown = False
        if any(logic.counts_cards for logic in self.logics):
            self.knowledge = [Knowledge(seat, hands[i]) for i, seat in enumerate(Position.positions)]
            for logic, k in zip(self.logics, self.knowledge):
                logic.knowledge = k

    @property
    def dummy(self):
        """the dummy's seat, None without a declarer"""
        return None if self.declarer is None else Position.index2pos(self.declarer, 2)

    def _show_dummy(self):
        """dummy's hand goes on the table; declarer and dummy are one mind and see each other's hands"""
        self._dummy_shown = True
        dummy, declarer = self.dummy, self.declarer
        for seat, k in zip(Position.positions, self.knowledge):
            if seat != dummy:
                k.reveal(dummy, self.hands[Position.positions.index(dummy)])
        self.knowledge[Position.positions.index(dummy)].reveal(declarer, self.hands[Position.positions.index(declarer)])

    def play_trick(self, leader):
        """play one trick, returns (winning card, winning position)"""
        trick = Trick(leader, self.trump)
        first = Position.pos2index('north', trick.leader)  # table index of the leader, hands and logics are in table order
        for ii in range(4):
            ind = (first + ii) % 4
            logic = self.logics[ind]
            card = logic.lead() if ii == 0 else logic.follow(trick)
            trick.nextCard(card)
            self.hands[ind].play(card)
            if self.knowledge is not None:
                lead = None if ii == 0 else trick[0].suit
                for k in self.knowledge:
                    k.observe(Position.positions[ind], card, lead)
                if ii == 0 and not self._dummy_shown and self.declarer is not None:
                    self._show_dummy()
        self.tricks.append(trick)
        win = trick.winner()
        self.winners.append(win[1])
        return win

    def play(self, leader=None):
        """
        play all 13 tricks, the winner of a trick leads the next one; the first lead is `leader`, by default
        the player on declarer's left, or north if there is no declarer
        returns the tricks won by (north-south, east-west)
        """
        if leader is None:
            leader = 'north' if self.declarer is None else Position.index2pos(self.declarer, 1)
        for _ in range(13):
            leader = self.play_trick(leader)[1]
        return (sum(Position.side(w) == 'ns' for w in self.winners),
                sum(Position.side(w) == 'ew' for w in self.winners))

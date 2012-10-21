


"""
This class plays a Round of bridge
that is after trump and contrct is established plays all the hands

It needs to have pluggable playstyle for each player seperately
"""

from abc import ABCMeta, abstractmethod
import itertools

class HandLogic(object):
    """
    this is the logic that is used to play a hand
    """
    __metaclass__ = ABCMeta
    def __init__(self, hand, trump):
        self.hand = hand
        self.trump = trump

    @abstractmethod
    def lead(self):
        pass
    
    @abstractmethod
    def follow(self):
        pass


class simpleHigh(HandLogic):
    """
    this player just always plays the highest card at all times, if can't win plays lowest
    """
    def lead(self):
        return self.hand.highCard

    def follow(self, cards):
        """
        cards are the cards already played.  The lead is cards[0]
        """
        in_suit = self.hand.__getattribute__(cards[0].suit)
        trumps = self.hand.__getattribute__(self.trump)

        if not(in_suit): # don't have any of the lead
            if cards[0].suit != self.trump: # and it was not trump
                if trumps: # do we have any trump cards?
                    return min(trumps) # play the smallest trump
            return min(self.hand)
            
        else: # we do have some of what was lead
            if max(in_suit) > max(cards): # if we can beat it, do
                return max(in_suit)
            return min(in_suit) # otherwise play lowest card
                



class Round(object):
    def __init__(self, table, hands, trump, logics):
        self.table = table
        self.trump = trump
        self.hands = hands
        self.logics = []
        for ii, logi in enumerate(logics):
            self.logics.append(logi(self.hands[ii], self.trump))

    def play_trick(self):
        cards = [self.logics[0].lead()]
        for pos in [1,2,3]:
            cards.append(self.logics[pos].follow(list(cards)))

        for ii, c in enumerate(cards):
            self.hands[ii].remove(c)
        print cards


if __name__ == '__main__':
    import Table
    import Deck
#    import simpleHigh
    d1 = Deck.Deck()
    d1.shuffle(7)
    h1, h2, h3, h4 = d1.deal()
    rnd = Round(Table.Table(),
                [h1,h2,h3,h4],
                'spades',
                [simpleHigh, simpleHigh, simpleHigh, simpleHigh])

    




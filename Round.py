


"""
This class plays a Round of bridge
that is after trump and contrct is established plays all the hands

It needs to have pluggable playstyle for each player seperately
"""


class HandLogic(object):
    """
    this is the logic that is used to play a hand
    """
    def __init__(self, hand, trump):
        self.hand = hand
        self.trump = trump

class simpleHigh(HandLogic):
    """
    this player just always plays the highest card at all times, if can't win plays lowest
    """
    def lead(self):
        return self.hand.high

    def follow(self, lead):
        """
        lead is the card that was lead
        """
        cards = self.hard.__getattribute__(lead.suit)





class Round(object):
    def __init__(self, table, leader, hands, trump):
        self.table = table
        self.leader = leader
        self.trump = trump

    def play_trick(self):
        




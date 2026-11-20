from abc import ABC, abstractmethod

from .Position import Position

"""
this module is quite complicated, it will need to both do the mechanics of bidding
but also allow for puggable "smarts" accordng to different conventions
"""


class Redeal(Exception):
    pass


class Bidding_logic(ABC):
    def __init__(self, hand):  # create an instance per bidder
        self.hand = hand

    @abstractmethod
    def openBid(self):
        """the Bid to open the auction with"""

    @abstractmethod
    def raiseBid(self, bids=None):
        """the Bid to raise partner's bid with"""

    @abstractmethod
    def jumpBid(self, bids=None):
        """the Bid to jump to"""


class Bidding(list):
    """
    The auction.  Each entry is a (seat, Bid).  The auction is over after three
    passes in a row once someone has bid, or after four passes if nobody has
    (that is a Redeal)
    """
    def __init__(self, leader='north'):
        super().__init__()
        self.leader = str(Position(leader))
        self._seats = list(Position.positions[Position.positions.index(self.leader):]
                           + Position.positions[:Position.positions.index(self.leader)])
        self._passCount = 0

    @property
    def complete(self):
        """True once the auction has ended"""
        return self._passCount >= (3 if self.opened else 4)

    def addBid(self, seat, bid):
        """
        add a bid by seat; returns None while bidding continues or the (seat, winning Bid)
        when the auction is over.  Raises Redeal if all four pass without a bid
        """
        seat = str(Position(seat))
        if self.complete:
            raise (ValueError('The auction is already over'))
        if not bid.isPass:  # a new bid must be larger than the old one
            old_winner = self._winningBid()
            if old_winner is not None and not bid > old_winner[1]:
                raise (ValueError('New bid must be higher than old bid'))
        if bid.isPass:
            self._passCount += 1
        else:
            self._passCount = 0
        self.append((seat, bid))
        if self.complete:
            if not self.opened:  # no one opened
                raise (Redeal("No one opened"))
            return self._winningBid()
        return None

    def _winningBid(self):
        """
        figure the winning bid
        """
        for seat, bid in reversed(self):
            if not bid.isPass:
                return (seat, bid)

    def nextBid(self, bid):
        """
        subset of above, just goes in order
        """
        return self.addBid(self._seats[len(self) % 4], bid)

    @property
    def opened(self):
        """
        return True if someone has opened, False otherwise
        """
        return any(not bid.isPass for _, bid in self)

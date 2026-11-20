from dataclasses import dataclass

from .Bid import Bid
from .Position import Position

SYMBOLS = {'clubs': '♣', 'diamonds': '♦', 'hearts': '♥', 'spades': '♠', 'notrump': 'NT'}


@dataclass(frozen=True)
class Contract:
    """
    What the auction decided: `declarer` (a seat) plays the hand and has to take `6 + level` tricks with
    `strain` (a suit or 'notrump') as trump.  `doubled` is 0, 1 (doubled) or 2 (redoubled).
    """
    level: int
    strain: str
    declarer: str
    doubled: int = 0

    def __post_init__(self):
        Bid(self.level, self.strain)  # ValueError for a bad level or strain
        object.__setattr__(self, 'declarer', Position.name(self.declarer))
        if self.doubled not in (0, 1, 2):
            raise ValueError('doubled must be 0, 1 or 2')

    @property
    def tricks_needed(self):
        """tricks declarer must take to make the contract"""
        return 6 + self.level

    @property
    def bid(self):
        return Bid(self.level, self.strain)

    @property
    def side(self):
        """'ns' or 'ew', the side that declares"""
        return Position.side(self.declarer)

    @property
    def dummy(self):
        return Position.index2pos(self.declarer, 2)

    @property
    def opening_leader(self):
        """the player on declarer's left makes the opening lead"""
        return Position.index2pos(self.declarer, 1)

    @property
    def trump(self):
        """the trump suit, or 'notrump'"""
        return self.strain

    def __str__(self):
        return f"{self.level}{SYMBOLS[self.strain]}{'X' * self.doubled} by {self.declarer}"

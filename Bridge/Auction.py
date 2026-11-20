from dataclasses import dataclass, field

from .Bid import Bid
from .Bidding import Bidding, Redeal
from .Contract import Contract
from .Position import Position
from .PointsAndFit import PointsAndFit

MAX_CALLS = 60  # far more than any auction needs, a guard against a system that never stops


@dataclass
class Call:
    """one call of the auction: who, what, why, and in which round of bidding (0 is the first)"""
    seat: str
    bid: Bid
    reason: str
    round: int


@dataclass
class AuctionResult:
    dealer: str
    calls: list = field(default_factory=list)
    contract: Contract = None  # None if everyone passed

    @property
    def passed_out(self):
        return self.contract is None

    def rounds(self):
        """
        the auction as rows of four calls, one row per round of bidding, in the order north, east, south,
        west, with None before the dealer's first call
        """
        offset = Position.positions.index(self.dealer)
        cells = [None] * offset + [c.bid for c in self.calls]
        while len(cells) % 4:
            cells.append(None)
        return [cells[i:i + 4] for i in range(0, len(cells), 4)]


def run_auction(hands, dealer='north', system=PointsAndFit, open_hcp=None):
    """
    Bid the four `hands` (in the order north, east, south, west) with `system`, one instance per player.
    Once one side has opened the bidding the other side does not compete and passes every time.  Returns an
    `AuctionResult` with every call and the reason for it, and the `Contract` (None if all four pass).
    """
    dealer = Position.name(dealer)
    options = {} if open_hcp is None else {'open_hcp': open_hcp}
    players = {seat: system(hands[i], seat, **options) for i, seat in enumerate(Position.positions)}
    bidding = Bidding(dealer)
    result = AuctionResult(dealer)
    opening_side = None
    winner = None
    for n in range(MAX_CALLS):
        seat = Position.index2pos(dealer, n)
        if opening_side is not None and Position.side(seat) != opening_side:
            bid, reason = Bid('pass'), 'the other side opened, no competition'
        else:
            bid = players[seat].call(bidding)
            reason = players[seat].reason
        if opening_side is None and not bid.isPass:
            opening_side = Position.side(seat)
        result.calls.append(Call(seat, bid, reason, n // 4))
        try:
            winner = bidding.nextBid(bid)
        except Redeal:
            return result  # all four passed
        if winner is not None:
            break
    else:  # pragma: no cover  (a safeguard, no system in the project gets here)
        raise RuntimeError('the auction did not end')
    last_seat, final = winner
    side = Position.side(last_seat)
    declarer = next(s for s, b in bidding if not b.isPass and b.suit == final.suit and Position.side(s) == side)
    result.contract = Contract(final.value, final.suit, declarer)
    return result

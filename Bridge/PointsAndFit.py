"""
A small natural bidding system built on two ideas: how many points the partnership holds between them,
and whether it has a fit.  It is meant to be simple enough to read in a minute, and good enough to reach
sensible contracts that can be judged against what the cards allow.

Points are high card points (A=4, K=3, Q=2, J=1).  A *fit* is a suit the partnership holds 8 or more
cards in; a major suit (spades, hearts) is preferred, then notrump, then a minor.

Opening (the first player to open decides who bids; the other side always passes)
    12 or more points opens, otherwise pass.
    balanced 15-17 points: 1NT.   balanced 20 or more points: 2NT.
    otherwise 1 of the longest major with 5+ cards (spades if equal), else 1 of the longer minor
    (diamonds if they are equal in length and 4+, otherwise clubs).

Responding to 1 of a suit (the opener has 12-21 points)
    5 points or fewer: pass.
    with support (3 cards for a major, 5 for a minor): 6-9 points raise to 2, 10-12 to 3, 13-16 to game
    (4 of a major, 3NT over a minor), 17 or more to slam.
    otherwise bid a new suit of 4+ cards, at the 1 level, or at the 2 level with 10+ points (forcing:
    the opener must bid again); otherwise notrump: 6-9 points 1NT, 10-12 2NT, 13-16 3NT, 17+ 6NT.

Responding to 1NT (15-17): pass with up to 7; with a 6-card major sign off in 2 (6-9 points) or bid game;
    8-9 points invite with 2NT (the opener bids 3NT with 16 or more); 10-15 3NT; 16 or more 6NT.
Responding to 2NT (20-21): pass with up to 3, 4-11 bid 3NT, 12 or more bid 6NT.

The opener's second call decides the contract.  Add the opener's points to the middle of the range the
response showed, and play at the level that total calls for in the best strain: the major the partnership
fits, else the opener's own 5+ card suit, else notrump.
    combined points  notrump  major  minor
    20-22              1       2      2
    23-25              2       3      3
    26-28              3       4      3NT
    29-32              3       4      5
    33-36              6       6      6
    37 or more         7       7      7
Pass if that is no more than the contract already reached.  After a forcing new suit the opener must bid
something and picks the cheapest bid in the chosen strain that is high enough.
Any later call is a slam raise: bid 6 in the strain reached if the two hands add up to 33 or more.
"""
from .Bid import Bid
from .Bidding import Bidding_logic
from .Position import Position
from .Suit import Suit

MAJORS = ('spades', 'hearts')
MINORS = ('diamonds', 'clubs')

# the points a response shows, over a suit opening, a 1NT and a 2NT opening
_RAISE = {2: (6, 9), 3: (10, 12), 4: (13, 16)}
_NT_OVER_SUIT = {1: (6, 9), 2: (10, 12), 3: (13, 16)}
_OVER_1NT = {2: (8, 9), 3: (10, 15), 4: (10, 15), 6: (16, 40)}
_OVER_2NT = {3: (4, 11), 6: (12, 40)}
_OPENING_RANGE = {'suit': (12, 21), 'nt1': (15, 17), 'nt2': (20, 21)}


def opening_range(bid):
    """the points an opening call shows"""
    if bid.suit == 'notrump':
        return _OPENING_RANGE['nt1' if bid.value == 1 else 'nt2']
    return _OPENING_RANGE['suit']


def response_range(opening, response):
    """the points the response `response` shows over the opening call `opening`"""
    if opening.suit == 'notrump':
        table = _OVER_1NT if opening.value == 1 else _OVER_2NT
        if response.suit != 'notrump' and opening.value == 1:
            return (6, 9) if response.value == 2 else (10, 15)
        return table.get(response.value, (17, 40))
    if response.suit == 'notrump':
        return _NT_OVER_SUIT.get(response.value, (17, 40))
    if response.suit == opening.suit:
        return _RAISE.get(response.value, (17, 40))
    return (6, 16) if response.value == 1 else (10, 16)  # a new suit


def target(combined, strain):
    """(level, strain) a partnership with `combined` points should play in, or None if it should not bid"""
    if combined >= 37:
        return 7, strain
    if combined >= 33:
        return 6, strain
    if strain == 'notrump':
        level = 3 if combined >= 26 else 2 if combined >= 23 else 1 if combined >= 20 else 0
    elif strain in MAJORS:
        level = 4 if combined >= 26 else 3 if combined >= 23 else 2 if combined >= 20 else 0
    else:  # a minor: game is 11 tricks, so play 3NT unless there are 29 points
        if combined >= 29:
            return 5, strain
        if combined >= 26:
            return 3, 'notrump'
        level = 3 if combined >= 23 else 2 if combined >= 20 else 0
    return (level, strain) if level else None


def cheapest(level, strain, highest):
    """the lowest bid in `strain` at `level` or more that is higher than `highest`, None above 7"""
    if highest is None:
        return Bid(level, strain)
    while level <= 7:
        bid = Bid(level, strain)
        if bid > highest:
            return bid
        level += 1
    return None


class PointsAndFit(Bidding_logic):
    """
    The system above for one player: `PointsAndFit(hand, seat)`, then `call(auction)` for the next call,
    where `auction` is the `Bidding` (or any list of (seat, Bid)) so far.  `reason` says why the last call was made.
    """
    OPEN_HCP = 12

    def __init__(self, hand, seat, open_hcp=None):
        super().__init__(hand)
        self.seat = Position.name(seat)
        self.open_hcp = self.OPEN_HCP if open_hcp is None else open_hcp
        self.hcp = hand.hcp()
        self.lengths = dict(hand.distro())
        self.balanced = hand.balanced()
        self.reason = ''

    # the abstract methods of Bidding_logic, as the three kinds of call
    def openBid(self):
        return self._open()

    def raiseBid(self, bids=None):
        return self.call(bids or [])

    def jumpBid(self, bids=None):
        return self.call(bids or [])

    # ------------------------------------------------------------------------------------ the dispatcher
    def call(self, auction):
        """the next call of this player"""
        partner = Position.index2pos(self.seat, 2)
        side = Position.side(self.seat)
        highest = next((b for _, b in reversed(auction) if not b.isPass), None)
        mine = [b for s, b in auction if s == self.seat and not b.isPass]
        partners = [b for s, b in auction if s == partner and not b.isPass]
        if any(not b.isPass for s, b in auction if Position.side(s) != side):
            return self._pass('the other side has bid, this system does not compete')
        if not mine and not partners:
            return self._open()
        if not mine:
            return self._respond(partners[0], highest)
        opened = self._opened(auction)
        if opened and len(mine) == 1 and len(partners) == 1:
            return self._rebid(mine[0], partners[0], highest)
        if opened:  # a later call of the opener: what did the partner's response show
            return self._later(response_range(mine[0], partners[0]) if partners else None, highest)
        return self._later(opening_range(partners[0]), highest)  # a later call of the responder

    def _opened(self, auction):
        first = next(s for s, b in auction if not b.isPass)
        return first == self.seat

    def _pass(self, reason):
        self.reason = reason
        return Bid('pass')

    def _bid(self, bid, reason):
        self.reason = reason
        return bid

    # ------------------------------------------------------------------------------------ opening
    def _open(self):
        h, n = self.hcp, self.lengths
        if h < self.open_hcp:
            return self._pass(f'{h} points, not enough to open ({self.open_hcp} needed)')
        if self.balanced and h >= 20:
            return self._bid(Bid(2, 'notrump'), f'{h} points, balanced')
        if self.balanced and 15 <= h <= 17:
            return self._bid(Bid(1, 'notrump'), f'{h} points, balanced')
        majors = [s for s in MAJORS if n[s] >= 5]
        if majors:
            suit = max(majors, key=lambda s: (n[s], -MAJORS.index(s)))
            return self._bid(Bid(1, suit), f'{h} points and {n[suit]} {suit}')
        suit = 'diamonds' if n['diamonds'] > n['clubs'] or (n['diamonds'] == n['clubs'] and n['diamonds'] >= 4) else 'clubs'
        return self._bid(Bid(1, suit), f'{h} points, the longer minor ({n[suit]} {suit})')

    # ------------------------------------------------------------------------------------ responding
    def _respond(self, opening, highest):
        if opening.suit == 'notrump':
            return self._respond_notrump(opening)
        return self._respond_suit(opening, highest)

    def _respond_notrump(self, opening):
        h, n = self.hcp, self.lengths
        if opening.value == 2:
            if h <= 3:
                return self._pass(f'{h} points, nothing to add to 2NT')
            if h >= 12:
                return self._bid(Bid(6, 'notrump'), f'{h} points opposite 20-21: slam')
            return self._bid(Bid(3, 'notrump'), f'{h} points opposite 20-21: game')
        for suit in MAJORS:  # a long major is played whatever the points, from 6 up
            if n[suit] >= 6 and h >= 6:
                if h <= 9:
                    return self._bid(Bid(2, suit), f'{h} points, a 6 card {suit} suit: sign off')
                return self._bid(Bid(4, suit), f'{h} points and 6 {suit}: game')
        if h <= 7:
            return self._pass(f'{h} points opposite 15-17, not enough for game')
        if h <= 9:
            return self._bid(Bid(2, 'notrump'), f'{h} points: invite to game')
        if h <= 15:
            return self._bid(Bid(3, 'notrump'), f'{h} points opposite 15-17: game')
        return self._bid(Bid(6, 'notrump'), f'{h} points opposite 15-17: slam')

    def _respond_suit(self, opening, highest):
        h, n = self.hcp, self.lengths
        x = opening.suit
        if h <= 5:
            return self._pass(f'{h} points, too few to respond')
        support = n[x] >= (3 if x in MAJORS else 5)
        if support:
            if x in MAJORS:
                level = 6 if h >= 17 else 4 if h >= 13 else 3 if h >= 10 else 2
                return self._bid(Bid(level, x), f'{h} points and {n[x]} {x}: support the opener\'s suit')
            level, strain = (6, 'notrump') if h >= 17 else (3, 'notrump') if h >= 13 else (3 if h >= 10 else 2, x)
            return self._bid(Bid(level, strain), f'{h} points and {n[x]} {x}: support the opener\'s minor')
        candidates = [s for s in Suit.suits if s != x and n[s] >= 4]
        candidates.sort(key=lambda s: (-n[s], 0 if Bid(1, s) > opening else 1, -Suit.suits.index(s)))
        for suit in candidates:
            level = 1 if Bid(1, suit) > opening else 2
            if level == 1 or h >= 10:
                return self._bid(Bid(level, suit), f'{h} points and {n[suit]} {suit}: a new suit')
        level = 1 if h <= 9 else 2 if h <= 12 else 3 if h <= 16 else 6
        return self._bid(Bid(level, 'notrump'), f'{h} points, no fit and no suit to bid: notrump')

    # ------------------------------------------------------------------------------------ the opener decides
    def _rebid(self, opening, response, highest):
        h, n = self.hcp, self.lengths
        lo, hi = response_range(opening, response)
        mid = (lo + hi) / 2
        combined = h + mid
        if opening.suit == 'notrump':
            if opening.value == 1 and response.suit == 'notrump' and response.value == 2:
                if h >= 16:
                    return self._bid(Bid(3, 'notrump'), f'{h} points accepts the invitation')
                return self._pass(f'{h} points declines the invitation')
            return self._pass(f'partner has chosen the contract ({response})')
        x, y = opening.suit, response.suit
        if y == x:
            strain = x
        elif y != 'notrump' and y in MAJORS and n[y] >= 4:
            strain = y
        elif y == 'notrump':
            strain = 'notrump'
        elif n[x] >= 6 or (n[x] >= 5 and not self.balanced):
            strain = x
        else:
            strain = 'notrump'
        goal = target(combined, strain)
        why = f'{h} points opposite {lo}-{hi}: about {combined:.0f} between us, play in {strain}'
        forcing = y not in (x, 'notrump') and response.value <= 2
        if goal is None:
            bid = cheapest(1, strain, highest) if forcing else None
        else:
            bid = cheapest(goal[0], goal[1], highest) if forcing else (
                Bid(*goal) if Bid(*goal) > highest else None)
        if bid is None:
            return self._pass(why + ' (already there)')
        return self._bid(bid, why)

    # ------------------------------------------------------------------------------------ later calls: slam
    def _later(self, partner_points, highest):
        """
        after the contract has been chosen: raise to slam if the two hands add up to 33 or more.
        `partner_points` is the (low, high) the partner has shown, None if the partner has not bid.
        """
        if partner_points is None:
            return self._pass('partner did not bid')
        if highest.value >= 6:
            return self._pass('the contract is set')
        mid = sum(partner_points) / 2
        if self.hcp + mid >= 33:
            return self._bid(Bid(6, highest.suit), f'{self.hcp} points and about {mid:.0f} opposite: slam')
        return self._pass('the contract is set')

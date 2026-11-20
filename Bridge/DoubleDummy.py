"""
Double-dummy results: what the cards allow when all four hands are visible and everyone plays perfectly.

This is an adapter around the DDS solver (through the `endplay` package).  It is an optional dependency, in
the `dd` dependency group, and has wheels for Python 3.12 and 3.13 only (none yet for 3.14); `AVAILABLE` says
whether it can be used.  Everything here takes and returns the project's own types.

A deal is four sequences of cards in the order north, east, south, west, all of the same length (13 for a
whole deal, fewer for an ending).  Strains are `Bid.strains` (clubs, diamonds, hearts, spades, notrump).
"""
import numpy as np

from .Bid import Bid
from .Card import Card
from .Position import Position
from .Value import Value

try:
    from endplay.dds import calc_all_tables, calc_dd_table, solve_board
    from endplay.types import Deal, Denom, Player
    AVAILABLE = True
except ImportError:  # pragma: no cover  (Python 3.14, or the dd group is not installed)
    AVAILABLE = False

_PBN_RANKS = {'0': 'T'}  # our ten is '0', DDS writes it T
_ENDPLAY_RANKS = {'T': '0'}


def _require():
    if not AVAILABLE:  # pragma: no cover
        raise ImportError('the double-dummy solver needs the endplay package (the dd dependency group, '
                          'available for Python 3.12 and 3.13)')


def _pbn_hand(cards):
    """one hand as spades.hearts.diamonds.clubs, highest card first in each suit, T for the ten"""
    suits = []
    for index in range(4):
        ranks = sorted((c.rank for c in cards if c.suit_index == index), reverse=True)
        suits.append(''.join(_PBN_RANKS.get(Value.values[r], Value.values[r]) for r in ranks))
    return '.'.join(suits)


def to_deal(hands):
    """an endplay Deal from four hands in the order north, east, south, west"""
    _require()
    sizes = {len(h) for h in hands}
    if len(hands) != 4 or len(sizes) != 1:
        raise ValueError('a deal is four hands with the same number of cards')
    codes = [c.code for h in hands for c in h]
    if len(set(codes)) != len(codes):
        raise ValueError('a card is in two hands')
    return Deal('N:' + ' '.join(_pbn_hand(h) for h in hands))


def _strain(strain):
    return Denom.nt if strain == 'notrump' else getattr(Denom, strain)


def dd_table(hands):
    """
    Tricks the declaring side takes with best play by everyone, for every strain and declarer (the player
    on declarer's left leads): an int array of shape (5, 4), indexed [strain, declarer] with the strains in
    the order of `Bid.strains` and the declarers in the order of `Position.positions`.  Whole deals only.
    """
    _require()
    return _as_array(calc_dd_table(to_deal(hands)))


_BATCH = 32  # DDS refuses more than a few dozen tables in one call


def _as_array(table):
    return np.array([[table[_strain(strain), Player(seat)] for seat in range(4)] for strain in Bid.strains],
                    dtype=np.int8)


def dd_tables(deals):
    """
    `dd_table` for many whole deals at once: an int array of shape (n, 5, 4).  DDS shares its set-up and
    works on all cores when it is given a batch, so this is about 2.4 times faster per deal than calling
    `dd_table` in a loop (34 ms against 82 ms on a 6 core machine; about 30 deals a second).
    """
    _require()
    deals = list(deals)
    out = np.empty((len(deals), 5, 4), dtype=np.int8)
    for start in range(0, len(deals), _BATCH):
        chunk = [to_deal(hands) for hands in deals[start:start + _BATCH]]
        for i, table in enumerate(calc_all_tables(chunk)):
            out[start + i] = _as_array(table)
    return out


def solve_leads(hands, strain, leader):
    """
    The value of every legal first card, with best play by everyone from then on: {card: tricks the leader's
    side takes in the rest of the play}.  `hands` may be an ending.
    """
    _require()
    deal = to_deal(hands)
    deal.trump = _strain(strain)
    deal.first = Player(Position.positions.index(Position.name(leader)))
    out = {}
    for card, tricks in solve_board(deal):
        out[Card.fromCode(_ENDPLAY_RANKS.get(card.rank.name[1], card.rank.name[1]) + card.suit.name[0])] = tricks
    return out


def highest_contract(table, side):
    """
    The highest bid that makes double-dummy for `side` ('ns' or 'ew'), chosen over every strain and over
    the side's two possible declarers, or None if no contract of level 1 makes.  `table` is a `dd_table`.
    """
    seats = (0, 2) if side == 'ns' else (1, 3)
    best = None
    for s, strain in enumerate(Bid.strains):
        level = int(max(table[s][seat] for seat in seats)) - 6
        if level >= 1:
            bid = Bid(level, strain)
            if best is None or bid > best:
                best = bid
    return best

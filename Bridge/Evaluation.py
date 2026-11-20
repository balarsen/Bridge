"""
Judging bids by what the cards allow.

For each deal: the auction (`PointsAndFit`), the double-dummy table (what every contract can make with
perfect play), the contract played by real strategies, and the score.  `evaluate` has the signature
`Harness.run_batches` expects, so `run_batches(evaluate, n, seed)` does many deals.

The *highest bid that is met* is the highest contract (by level, then strain) that makes double-dummy for the
side that bid; a bid reached above it is an **overbid**, below it an **underbid**, equal is correct.  This is
the hindsight view of the plan (all 52 cards known, perfect play), the first of the three levels.

Numbers in the result array, one row per deal, columns named in `COLUMNS` (-1 where there is none).
"""
import numpy as np

from . import DoubleDummy as DD
from .Auction import run_auction
from .Bid import Bid
from .Deck import Deck
from .Hand import Hand
from .Position import Position
from .Round import Round, countingHigh, simpleHigh
from .Scoring import score
from .Table import Table

COLUMNS = ('passed_out', 'level', 'strain', 'declarer', 'side', 'met_level', 'met_strain', 'dd_tricks',
           'tricks_simple', 'tricks_counting', 'score_simple', 'score_counting', 'score_dd', 'ns_hcp')
COL = {name: i for i, name in enumerate(COLUMNS)}
N_BIDS = 36  # pass / nothing, then the 35 bids 1 club ... 7 notrump

CATEGORIES = ('none', 'part score', 'game', 'small slam', 'grand slam')


def bid_index(level, strain_index):
    """0 for no bid, else 1 (1 club) to 35 (7 notrump), the order of `Bid`"""
    return 0 if level <= 0 else (level - 1) * 5 + strain_index + 1


def bid_of_index(index):
    """the Bid for an index from `bid_index`, None for 0"""
    if index == 0:
        return None
    return Bid((index - 1) // 5 + 1, Bid.strains[(index - 1) % 5])


def category(level, strain_index):
    """0 none, 1 part score, 2 game, 3 small slam, 4 grand slam"""
    if level <= 0:
        return 0
    if level == 7:
        return 4
    if level == 6:
        return 3
    strain = Bid.strains[strain_index]
    game = 3 if strain == 'notrump' else 4 if strain in ('hearts', 'spades') else 5
    return 2 if level >= game else 1


def _fresh(hands):
    """new hands with the same 13 cards, since playing a round uses a hand up"""
    return [Hand(h.original) for h in hands]


def _play(contract, hands, strategy):
    ns, ew = Round(Table(), _fresh(hands), contract.trump, [strategy] * 4, declarer=contract.declarer).play()
    return ns if contract.side == 'ns' else ew


def evaluate(rng, count, open_hcp=None, vulnerable=False):
    """
    `count` random deals through auction, double-dummy solution, play and scoring; an int array of shape
    (count, len(COLUMNS)).  The dealer rotates from deal to deal.  Needs the double-dummy solver.
    """
    decks = [Deck(shuffle=3, rng=rng) for _ in range(count)]
    deals = [list(d.deal()) for d in decks]
    tables = DD.dd_tables(deals)  # before any hand is played from
    out = np.full((count, len(COLUMNS)), -1, dtype=np.int16)
    for i, hands in enumerate(deals):
        dealer = Position.positions[i % 4]
        auction = run_auction(hands, dealer, open_hcp=open_hcp)
        row = out[i]
        row[COL['ns_hcp']] = hands[0].hcp() + hands[2].hcp()
        met = {side: DD.highest_contract(tables[i], side) for side in ('ns', 'ew')}
        if auction.contract is None:
            row[COL['passed_out']] = 1
            best = max((b for b in met.values() if b is not None), default=None)  # either side
        else:
            contract = auction.contract
            row[COL['passed_out']] = 0
            row[COL['level']] = contract.level
            row[COL['strain']] = Bid.strains.index(contract.strain)
            row[COL['declarer']] = Position.positions.index(contract.declarer)
            row[COL['side']] = 0 if contract.side == 'ns' else 1
            best = met[contract.side]
            dd = int(tables[i][Bid.strains.index(contract.strain)][Position.positions.index(contract.declarer)])
            row[COL['dd_tricks']] = dd
            for name, strategy in (('simple', simpleHigh), ('counting', countingHigh)):
                tricks = _play(contract, hands, strategy)
                row[COL['tricks_' + name]] = tricks
                row[COL['score_' + name]] = score(contract, tricks, vulnerable)
            row[COL['score_dd']] = score(contract, dd, vulnerable)
        if best is not None:
            row[COL['met_level']] = best.value
            row[COL['met_strain']] = Bid.strains.index(best.suit)
    return out


def _indices(rows):
    reached = np.array([bid_index(max(r[COL['level']], 0), max(r[COL['strain']], 0)) for r in rows])
    met = np.array([bid_index(max(r[COL['met_level']], 0), max(r[COL['met_strain']], 0)) for r in rows])
    return reached, met


def confusion_matrix(rows):
    """
    counts[reached, met] over the 36 bid indices: rows the bid reached (0 if every player passed), columns
    the highest bid that makes double-dummy (0 if nothing does).  The diagonal is correct, below it
    (reached < met) are underbids, above it overbids.
    """
    reached, met = _indices(rows)
    counts = np.zeros((N_BIDS, N_BIDS), dtype=np.int64)
    np.add.at(counts, (reached, met), 1)
    return counts


def category_matrix(rows):
    """the same counts by kind of contract: none, part score, game, small slam, grand slam"""
    counts = np.zeros((5, 5), dtype=np.int64)
    for r in rows:
        counts[category(max(r[COL['level']], 0), max(r[COL['strain']], 0)),
               category(max(r[COL['met_level']], 0), max(r[COL['met_strain']], 0))] += 1
    return counts


def over_under(rows):
    """{'correct', 'overbid', 'underbid'} counts: the bid reached against the highest bid that makes"""
    reached, met = _indices(rows)
    return {'correct': int((reached == met).sum()), 'overbid': int((reached > met).sum()),
            'underbid': int((reached < met).sum())}

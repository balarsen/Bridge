"""
Fast bulk dealing for statistics.

`Deck`/`Hand` objects are the right tool for playing a hand but far too slow to
look at millions of deals.  `deal_summaries` shuffles and deals n decks with a
numba kernel (multi-threaded) and keeps only what hand statistics need, per deal,
per seat and per suit:

    lengths  how many cards of the suit the seat holds
    honors   which of J, Q, K, A it holds, as bits  J=1 Q=2 K=4 A=8

Everything else (high card points, aces, shapes, ...) is derived from those.

Conventions are the same as the rest of the package: the seat axis is
`Position.positions` (north, east, south, west) and deck position i goes to
seat i % 4 (as `Deck.deal`), the suit axis is `Suit.suits` (spades, hearts,
diamonds, clubs).  A card is numbered suit * 13 + `Value.rank`.

Each deal is shuffled from its own random stream, derived from (seed, deal
number), so the result depends only on the seed, never on the number of
threads, and `deal_summaries(n)` is a prefix of `deal_summaries(m)` for n < m.
The streams come from the splitmix64 generator rather than numpy's, which keeps
the kernel simple to compile; it is a well tested generator, and it is not
`np.random`, so these decks are not the decks `Deck(rng=seed)` produces.
"""
import numpy as np
from numba import njit, prange

from .Position import Position
from .Suit import Suit
from .Value import Value

SEATS = Position.positions
SUITS = Suit.suits

_GAMMA = np.uint64(0x9E3779B97F4A7C15)
_M1 = np.uint64(0xBF58476D1CE4E5B9)
_M2 = np.uint64(0x94D049BB133111EB)
_S11 = np.uint64(11)
_S27 = np.uint64(27)
_S30 = np.uint64(30)
_S31 = np.uint64(31)
_S53 = np.uint64(53)

# The kernels below are compiled by numba, so coverage can not see into them (hence the
# "pragma: no cover" on their definitions); tests/test_Simulation.py checks them against the
# Deck / Hand classes instead.
_J_RANK = Value.values.index('J')  # honors are the ranks J, Q, K, A
_BLOCK = 4096  # deals per parallel work item


def _mix(z):  # pragma: no cover
    """the splitmix64 finalizer, a bijection on 64 bit integers"""
    z = (z ^ (z >> _S30)) * _M1
    z = (z ^ (z >> _S27)) * _M2
    return z ^ (z >> _S31)


_mix_jit = njit(_mix, cache=True)


def _summarize_deck(deck, lengths, honors):  # pragma: no cover
    """fill lengths[4, 4] and honors[4, 4] for one deck, an array of card numbers in deal order"""
    for h in range(4):
        for s in range(4):
            lengths[h, s] = 0
            honors[h, s] = 0
    for i in range(52):
        card = deck[i]
        h = i & 3
        s = card // 13
        r = card % 13
        lengths[h, s] += 1
        if r >= _J_RANK:
            honors[h, s] |= 1 << (r - _J_RANK)


_summarize_deck_jit = njit(_summarize_deck, cache=True)


def _deal_one(seed, i, deck, lengths, honors):  # pragma: no cover
    """shuffle (Fisher-Yates) and summarize deal number i"""
    # two rounds of mixing so that neighbouring deal numbers start far apart in the cycle
    state = _mix_jit(_mix_jit(np.uint64(i) + _GAMMA) ^ np.uint64(seed))
    for k in range(52):
        deck[k] = k
    for k in range(51, 0, -1):
        state += _GAMMA
        r = _mix_jit(state)
        # uniform on 0..k; the bias is below 52 / 2**53
        j = np.int64(((r >> _S11) * np.uint64(k + 1)) >> _S53)
        tmp = deck[k]
        deck[k] = deck[j]
        deck[j] = tmp
    _summarize_deck_jit(deck, lengths, honors)


_deal_one_jit = njit(_deal_one, cache=True)


def _deal_all(n, seed, lengths, honors):  # pragma: no cover
    # threads take whole blocks of deals and reuse one scratch deck per block, allocating
    # inside a per-deal parallel loop made the threads slower than a single one
    nblocks = (n + _BLOCK - 1) // _BLOCK
    for b in prange(nblocks):
        deck = np.empty(52, np.int64)
        for i in range(b * _BLOCK, min((b + 1) * _BLOCK, n)):
            _deal_one_jit(seed, i, deck, lengths[i], honors[i])


_deal_all_serial = njit(_deal_all, cache=True)
_deal_all_parallel = njit(_deal_all, parallel=True, cache=True)


def _summarize_decks(decks, lengths, honors):  # pragma: no cover
    for i in range(decks.shape[0]):
        _summarize_deck_jit(decks[i], lengths[i], honors[i])


_summarize_decks_jit = njit(_summarize_decks, cache=True)


class Deals(object):
    """
    The summaries of n deals.  Arrays are indexed [deal, seat, suit].
    """
    def __init__(self, lengths, honors):
        self.lengths = lengths
        self.honors = honors

    def __len__(self):
        return len(self.lengths)

    @property
    def points(self):
        """high card points (A4 K3 Q2 J1) of each seat in each suit"""
        h = self.honors
        return (4 * ((h >> 3) & 1) + 3 * ((h >> 2) & 1) + 2 * ((h >> 1) & 1) + (h & 1)).astype(np.int8)

    @property
    def hcp(self):
        """high card points of each seat, [deal, seat]"""
        return self.points.sum(axis=2, dtype=np.int8)

    @property
    def aces(self):
        """number of aces each seat holds, [deal, seat]"""
        return ((self.honors >> 3) & 1).sum(axis=2, dtype=np.int8)

    @property
    def shapes(self):
        """suit lengths of each seat sorted longest first, [deal, seat, 4]"""
        return -np.sort(-self.lengths, axis=2)


def deal_summaries(n, seed=0, parallel=True):
    """
    Deal n random decks and summarize them, see the module docstring.
    parallel=False runs on one thread, with identical results.
    """
    if n < 0 or seed < 0:
        raise ValueError('n and seed must not be negative')
    lengths = np.empty((n, 4, 4), np.int8)
    honors = np.empty((n, 4, 4), np.uint8)
    (_deal_all_parallel if parallel else _deal_all_serial)(n, seed, lengths, honors)
    return Deals(lengths, honors)


def summarize_decks(decks):
    """
    Summarize existing Deck objects (in the order they are dealt) the same way,
    mostly to check the conventions against `Deck.deal` and `Hand`.
    """
    numbers = np.array([[SUITS.index(str(c.suit)) * 13 + c.value.rank for c in d] for d in decks],
                       dtype=np.int64).reshape(len(decks), 52)
    lengths = np.empty((len(decks), 4, 4), np.int8)
    honors = np.empty((len(decks), 4, 4), np.uint8)
    _summarize_decks_jit(numbers, lengths, honors)
    return Deals(lengths, honors)

"""
Exact probabilities for dealt bridge hands, from counting rather than simulation.

These are the ground truth the simulations (`Bridge.Simulation`) and any fitted
model can be checked against.  Everything is pure combinatorics: a hand is a
uniformly random 13 card subset of the deck, and a partnership's 26 cards are a
uniformly random 26 card subset.

High card points are A=4, K=3, Q=2, J=1 as in `Scorers.SimpleHighCardValue`.
"""
import math
from collections import Counter

import numpy as np

_COUNTS = None


def _suit_ways():
    """ways[c, p]: number of ways to pick c cards of one suit worth p points"""
    ways = np.zeros((14, 11), dtype=np.int64)
    ways[0, 0] = 1
    for pts in (4, 3, 2, 1) + (0,) * 9:  # the 13 cards of a suit
        new = ways.copy()
        new[1:, pts:] += ways[:-1, :ways.shape[1] - pts]
        ways = new
    return ways


def _convolve(a, b):
    out = np.zeros((a.shape[0] + b.shape[0] - 1, a.shape[1] + b.shape[1] - 1), dtype=np.int64)
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            if a[i, j]:
                out[i:i + b.shape[0], j:j + b.shape[1]] += a[i, j] * b
    return out


def _all_counts():
    """counts[c, p]: number of c card subsets of the whole deck worth p points"""
    global _COUNTS
    if _COUNTS is None:
        ways = _suit_ways()
        total = ways
        for _ in range(3):
            total = _convolve(total, ways)
        _COUNTS = total
    return _COUNTS


def hcp_counts(n_cards=13):
    """number of n_cards card subsets with 0, 1, 2, ... 40 high card points"""
    if not 0 <= n_cards <= 52:
        raise ValueError('n_cards must be between 0 and 52')
    return _all_counts()[n_cards].copy()


def hcp_pmf(n_cards=13):
    """
    P(high card points == 0, 1, ... 40) for n_cards cards dealt at random, 13 is a hand and
    26 is a partnership.  Index is the points.
    """
    return hcp_counts(n_cards) / math.comb(52, n_cards)


def hcp_pmf_from_pool(aces, kings, queens, jacks, blanks, n_cards=13):
    """
    P(points = 0, 1, ... 40) for n_cards cards drawn at random from a pool holding the given number of aces,
    kings, queens, jacks and blank cards (a full deck is 4, 4, 4, 4, 36).  The closed form: the counts drawn
    (a, k, q, j, blanks) are multivariate hypergeometric,

        C(aces,a) C(kings,k) C(queens,q) C(jacks,j) C(blanks, n-a-k-q-j) / C(pool, n),

    and the points are 4a + 3k + 2q + j, so P(points = h) sums those over every (a, k, q, j) that make h.
    """
    pool = aces + kings + queens + jacks + blanks
    if not 0 <= n_cards <= pool:
        raise ValueError('n_cards must be between 0 and the size of the pool')
    counts = [0] * 41
    for a in range(aces + 1):
        for k in range(kings + 1):
            for q in range(queens + 1):
                for j in range(jacks + 1):
                    drawn_blanks = n_cards - a - k - q - j
                    if 0 <= drawn_blanks <= blanks:
                        counts[4 * a + 3 * k + 2 * q + j] += (math.comb(aces, a) * math.comb(kings, k) * math.comb(queens, q)
                                                              * math.comb(jacks, j) * math.comb(blanks, drawn_blanks))
    return np.array(counts) / math.comb(pool, n_cards)


def hcp_pmf_multivariate_hypergeometric(n_cards=13):
    """
    The same distribution as `hcp_pmf`, from the closed form instead of the dynamic program: n_cards cards from a
    full deck (4 each of aces, kings, queens and jacks, 36 blanks), see `hcp_pmf_from_pool`.  There is no single
    named family because of the weights 4, 3, 2, 1 (the *number* of honors alone is exactly hypergeometric).
    Slower than `hcp_pmf`, kept as an independent check.
    """
    if not 0 <= n_cards <= 52:
        raise ValueError('n_cards must be between 0 and 52')
    return hcp_pmf_from_pool(4, 4, 4, 4, 36, n_cards)


def partner_hcp_pmf(hand):
    """
    P(partner holds 0, 1, ... 40 points) given my 13 cards: partner's 13 cards are a random draw from the 39 I
    can not see, so this is `hcp_pmf_from_pool` on what is left of the honors.  `hand` is any 13 cards with
    `.value` (as `Hand` or a list of `Card`).
    """
    cards = list(hand)
    if len(cards) != 13:
        raise ValueError('a hand has 13 cards')
    held = {v: 0 for v in 'AKQJ'}
    for card in cards:
        key = str(card.value)
        if key in held:
            held[key] += 1
    blanks_held = 13 - sum(held.values())
    return hcp_pmf_from_pool(4 - held['A'], 4 - held['K'], 4 - held['Q'], 4 - held['J'], 36 - blanks_held, 13)


def honor_count_pmf(n_cards=13):
    """
    P(0, 1, ... 16 honors (A, K, Q or J) among n_cards cards): exactly hypergeometric,
    C(16, m) C(36, n-m) / C(52, n)
    """
    if not 0 <= n_cards <= 52:
        raise ValueError('n_cards must be between 0 and 52')
    return np.array([math.comb(16, m) * math.comb(36, n_cards - m) if 0 <= n_cards - m else 0
                     for m in range(17)]) / math.comb(52, n_cards)


def pmf_moments(pmf):
    """(mean, variance) of a pmf over 0, 1, 2, ..."""
    x = np.arange(len(pmf))
    mean = float((x * pmf).sum())
    return mean, float(((x - mean) ** 2 * pmf).sum())


def shape_probabilities():
    """
    {(a, b, c, d): probability} of each hand pattern, suit lengths longest first, so
    (4, 3, 3, 3) is every hand with a 4-3-3-3 split whichever suits they are.
    """
    total = math.comb(52, 13)
    out = {}
    for a in range(13, -1, -1):
        for b in range(min(a, 13 - a), -1, -1):
            for c in range(min(b, 13 - a - b), -1, -1):
                d = 13 - a - b - c
                if d > c:
                    continue
                orderings = 24
                for multiplicity in Counter((a, b, c, d)).values():
                    orderings //= math.factorial(multiplicity)
                ways = orderings * math.comb(13, a) * math.comb(13, b) * math.comb(13, c) * math.comb(13, d)
                out[(a, b, c, d)] = ways / total
    return out


def suit_length_pmf():
    """P(a hand holds 0, 1, ... 13 cards of a given suit)"""
    return np.array([math.comb(13, k) * math.comb(39, 13 - k) for k in range(14)]) / math.comb(52, 13)


def partner_suit_length_pmf(my_length):
    """
    P(partner holds 0, 1, ... 13 cards of a suit | I hold my_length of it).  The 39 cards I
    can not see are dealt at random, so this is hypergeometric.
    """
    if not 0 <= my_length <= 13:
        raise ValueError('my_length must be between 0 and 13')
    out_there = 13 - my_length
    return np.array([math.comb(out_there, j) * math.comb(39 - out_there, 13 - j)
                     for j in range(14)]) / math.comb(39, 13)


def combined_suit_length_pmf():
    """P(a partnership holds 0, 1, ... 13 cards of a given suit between them)"""
    return np.array([math.comb(13, k) * math.comb(39, 26 - k) for k in range(14)]) / math.comb(52, 26)


def partner_aces_pmf(my_aces):
    """P(partner holds 0, 1, ... 4 aces | I hold my_aces)"""
    if not 0 <= my_aces <= 4:
        raise ValueError('my_aces must be between 0 and 4')
    out_there = 4 - my_aces
    return np.array([math.comb(out_there, j) * math.comb(39 - out_there, 13 - j)
                     for j in range(5)]) / math.comb(39, 13)


def opponent_split_probabilities(partnership_length):
    """
    {(longer, shorter): probability} of how the opponents' cards in a suit divide between them
    when we hold partnership_length of the suit.  An 8 card fit leaves 5 out, 3-2 is the
    usual split.
    """
    if not 0 <= partnership_length <= 13:
        raise ValueError('partnership_length must be between 0 and 13')
    out_there = 13 - partnership_length
    probs = {}
    for j in range(out_there + 1):  # cards held by the left hand opponent
        p = math.comb(out_there, j) * math.comb(26 - out_there, 13 - j) / math.comb(26, 13)
        key = (max(j, out_there - j), min(j, out_there - j))
        probs[key] = probs.get(key, 0.0) + p
    return probs

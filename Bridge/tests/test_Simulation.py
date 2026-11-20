import numba
import numpy as np
import pytest

from .. import Probability as P
from ..Deck import Deck
from ..Position import Position
from ..Simulation import Deals, deal_summaries, summarize_decks
from ..Suit import Suit

HONOR_BITS = {'J': 1, 'Q': 2, 'K': 4, 'A': 8}


def test_conventions_match_deck_and_hand():
    """summaries of real Deck objects agree with Hand.distro / hcp for every seat and suit"""
    decks = [Deck(shuffle=3, rng=i) for i in range(50)]
    deals = summarize_decks(decks)
    assert len(deals) == 50
    for i, deck in enumerate(decks):
        for s, hand in enumerate(deck.deal()):  # north, east, south, west
            assert tuple(deals.lengths[i, s]) == tuple(n for _, n in hand.distro())
            assert deals.hcp[i, s] == hand.hcp()
            assert deals.aces[i, s] == sum(str(c.value) == 'A' for c in hand)
            for t, suit in enumerate(Suit.suits):
                bits = sum(HONOR_BITS[str(c.value)] for c in hand.get_suit(suit) if str(c.value) in HONOR_BITS)
                assert deals.honors[i, s, t] == bits


def test_seat_and_suit_axes_are_the_packages_order():
    # the unshuffled deck: spades 2..A, hearts..., north gets every 4th card
    deals = summarize_decks([Deck()])
    assert deals.lengths.shape == (1, 4, 4)
    assert tuple(deals.lengths[0, 0]) == tuple(n for _, n in next(iter(Deck().deal())).distro())
    assert Position.positions == ('north', 'east', 'south', 'west')


def test_invariants():
    d = deal_summaries(20_000, seed=1)
    assert d.lengths.shape == (20_000, 4, 4) and d.honors.shape == (20_000, 4, 4)
    assert (d.lengths.sum(axis=2) == 13).all()  # every seat holds 13 cards
    assert (d.lengths.sum(axis=1) == 13).all()  # every suit is 13 cards in all
    assert (d.hcp.sum(axis=1) == 40).all()  # 40 points in the deck
    assert (d.aces.sum(axis=1) == 4).all()
    assert (d.points.sum(axis=(1, 2)) == 40).all()
    assert d.honors.max() <= 15
    # each honor is held by exactly one seat
    for bit in (1, 2, 4, 8):
        assert (((d.honors >> (bit.bit_length() - 1)) & 1).sum(axis=1) == 1).all()


def test_shapes_sorted():
    d = deal_summaries(1000, seed=2)
    shapes = d.shapes
    assert shapes.shape == (1000, 4, 4)
    assert (np.diff(shapes, axis=2) <= 0).all()  # longest first
    assert (shapes.sum(axis=2) == 13).all()


def test_reproducible_and_seed_dependent():
    a, b, c = deal_summaries(5000, 11), deal_summaries(5000, 11), deal_summaries(5000, 12)
    assert np.array_equal(a.lengths, b.lengths) and np.array_equal(a.honors, b.honors)
    assert not np.array_equal(a.honors, c.honors)


def test_prefix_property():
    small, big = deal_summaries(1000, 3), deal_summaries(10_000, 3)
    assert np.array_equal(small.honors, big.honors[:1000])
    assert np.array_equal(small.lengths, big.lengths[:1000])


def test_parallel_equals_serial_and_thread_count_does_not_matter():
    n = 3 * 4096 + 17  # several blocks and a ragged last one
    serial = deal_summaries(n, 4, parallel=False)
    parallel = deal_summaries(n, 4)
    assert np.array_equal(serial.honors, parallel.honors)
    assert np.array_equal(serial.lengths, parallel.lengths)
    before = numba.get_num_threads()
    try:
        numba.set_num_threads(1)
        one = deal_summaries(n, 4)
    finally:
        numba.set_num_threads(before)
    assert np.array_equal(serial.honors, one.honors)


def test_empty_and_bad_arguments():
    assert len(deal_summaries(0)) == 0
    assert isinstance(deal_summaries(1), Deals)
    with pytest.raises(ValueError):
        deal_summaries(-1)
    with pytest.raises(ValueError):
        deal_summaries(10, seed=-1)


def test_matches_exact_probabilities():
    """a large seeded sample against the exact combinatorial answers"""
    n = 200_000
    d = deal_summaries(n, seed=20261120)
    hcp = d.hcp[:, 0].astype(int)  # one seat, the others are the same distribution
    pmf = np.bincount(hcp, minlength=41) / n
    assert np.abs(pmf - P.hcp_pmf(13)).max() < 0.003
    assert abs(hcp.mean() - 10) < 0.05
    assert abs(hcp.var(ddof=1) - 17.0588) < 0.25
    # all four seats together, for 4 times the sample
    all_hcp = np.bincount(d.hcp.ravel().astype(int), minlength=41) / (4 * n)
    assert np.abs(all_hcp - P.hcp_pmf(13)).max() < 0.0015
    # hand patterns
    shape_codes = d.shapes[:, 0]
    exact = P.shape_probabilities()
    for pattern in ((4, 4, 3, 2), (5, 3, 3, 2), (4, 3, 3, 3), (5, 4, 3, 1)):
        observed = (shape_codes == pattern).all(axis=1).mean()
        assert abs(observed - exact[pattern]) < 0.005, pattern
    # partner's holding in spades given mine is hypergeometric
    mine, partner = d.lengths[:, 0, 0], d.lengths[:, 2, 0]
    sel = mine == 4
    observed = np.bincount(partner[sel], minlength=14) / sel.sum()
    assert np.abs(observed - P.partner_suit_length_pmf(4)).max() < 0.01
    # correlation of the points in two hands is exactly -13 / 39 = -1/3
    assert np.corrcoef(d.hcp[:, 0], d.hcp[:, 2])[0, 1] == pytest.approx(-1 / 3, abs=0.01)

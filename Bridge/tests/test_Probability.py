import math

import numpy as np
import pytest

from .. import Probability as P


def test_hcp_counts_total():
    for n in (0, 1, 13, 26, 52):
        assert P.hcp_counts(n).sum() == math.comb(52, n)


def test_hcp_counts_extremes():
    c = P.hcp_counts(13)
    assert len(c) == 41
    assert c[0] == math.comb(36, 13)  # no honor cards at all
    assert c[37] == 4  # all 4 aces, kings, queens and one jack
    assert c[38:].sum() == 0
    assert P.hcp_counts(52)[40] == 1
    assert P.hcp_counts(0)[0] == 1


def test_hcp_counts_is_a_copy():
    P.hcp_counts(13)[0] = -1
    assert P.hcp_counts(13)[0] == math.comb(36, 13)


def test_hcp_counts_bad_input():
    with pytest.raises(ValueError):
        P.hcp_counts(53)
    with pytest.raises(ValueError):
        P.hcp_counts(-1)


def test_hcp_moments_match_sampling_without_replacement():
    """mean n*40/52 and the finite population variance of drawing n cards"""
    card_var = 120 / 52 - (40 / 52) ** 2  # points of one random card, 4 each of 4+3+2+1 and 36 zeros
    for n in (13, 26):
        mean, var = P.pmf_moments(P.hcp_pmf(n))
        assert mean == pytest.approx(n * 40 / 52)
        assert var == pytest.approx(n * card_var * (52 - n) / 51)
    assert P.pmf_moments(P.hcp_pmf(13))[0] == pytest.approx(10)


def test_closed_form_matches_dynamic_program():
    """two independent exact methods for the same distribution"""
    for n in (0, 1, 2, 13, 26, 40, 52):
        assert P.hcp_pmf_multivariate_hypergeometric(n) == pytest.approx(P.hcp_pmf(n), abs=1e-15, rel=1e-12)
    assert P.hcp_pmf_multivariate_hypergeometric(13).sum() == pytest.approx(1)
    with pytest.raises(ValueError):
        P.hcp_pmf_multivariate_hypergeometric(53)


def test_pool_version_with_a_full_deck_is_the_same_distribution():
    assert P.hcp_pmf_from_pool(4, 4, 4, 4, 36, 13) == pytest.approx(P.hcp_pmf(13), abs=1e-15, rel=1e-12)
    assert P.hcp_pmf_from_pool(4, 4, 4, 4, 36, 26) == pytest.approx(P.hcp_pmf(26), abs=1e-15, rel=1e-12)


def test_pool_version_against_listing_every_draw_of_a_small_pool():
    """2 aces, 1 king, 1 queen, 1 jack and 3 blanks: every way to draw 3 of the 8 cards"""
    import itertools
    pool_points = [4, 4, 3, 2, 1, 0, 0, 0]
    expected = np.zeros(41)
    draws = list(itertools.combinations(range(8), 3))
    for d in draws:
        expected[sum(pool_points[i] for i in d)] += 1 / len(draws)
    assert P.hcp_pmf_from_pool(2, 1, 1, 1, 3, 3) == pytest.approx(expected, abs=1e-15)
    assert P.hcp_pmf_from_pool(0, 0, 0, 0, 5, 2)[0] == 1.0  # nothing but blanks
    with pytest.raises(ValueError):
        P.hcp_pmf_from_pool(1, 1, 1, 1, 1, 6)


def test_partner_hcp_pmf():
    from ..Card import Card
    south = [Card.fromCode(c) for c in 'As Ks 0s 9s 7s 4s 2s Ah 4h 9d Ac 9c 3c'.split()]  # 15 points, 7-2-1-3
    pmf = P.partner_hcp_pmf(south)
    assert pmf.sum() == pytest.approx(1) and len(pmf) == 41
    mean, var = P.pmf_moments(pmf)
    assert mean == pytest.approx(13 * 25 / 39)  # a third of the 25 points left
    # what is left: 1 ace, 3 kings, 4 queens, 4 jacks (25 points, 63 points squared) among 39 cards
    card_var = 63 / 39 - (25 / 39) ** 2
    assert var == pytest.approx(13 * card_var * (39 - 13) / 38)  # finite population variance of 13 drawn of 39
    assert pmf[26:].sum() == 0  # only 25 points are left
    # partner's 13 cards out of 39: the same total as the whole table of what is left (25 points among 12 honors)
    assert P.partner_hcp_pmf(list(south)) == pytest.approx(pmf)
    with pytest.raises(ValueError):
        P.partner_hcp_pmf(south[:12])


def test_honor_count_is_hypergeometric():
    for n in (1, 13, 26):
        p = P.honor_count_pmf(n)
        assert len(p) == 17 and p.sum() == pytest.approx(1)
        assert np.arange(17) @ p == pytest.approx(n * 16 / 52)  # hypergeometric mean n K / N
        mean = n * 16 / 52
        var = n * (16 / 52) * (36 / 52) * (52 - n) / 51  # hypergeometric variance
        assert np.arange(17) ** 2 @ p - mean ** 2 == pytest.approx(var)
    with pytest.raises(ValueError):
        P.honor_count_pmf(-1)


def test_hcp_is_overdispersed_but_any_hypergeometric_is_underdispersed():
    """why no plain hypergeometric fits: its variance is below its mean, the points' is above"""
    mean, var = P.pmf_moments(P.hcp_pmf(13))
    assert var / mean == pytest.approx(1.7059, abs=1e-4)
    for n in (5, 13, 26):  # honor count: variance below mean
        m, v = P.pmf_moments(P.honor_count_pmf(n))
        assert v < m


def test_hcp_pmf_known_value():
    assert P.hcp_pmf(13)[0] == pytest.approx(0.003639, abs=1e-6)
    assert P.hcp_pmf(13).sum() == pytest.approx(1)


def test_shape_probabilities():
    s = P.shape_probabilities()
    assert len(s) == 39  # the 39 hand patterns
    assert sum(s.values()) == pytest.approx(1)
    assert all(a >= b >= c >= d and a + b + c + d == 13 for a, b, c, d in s)
    # textbook values
    assert s[(4, 4, 3, 2)] == pytest.approx(0.2155, abs=5e-5)
    assert s[(5, 3, 3, 2)] == pytest.approx(0.1552, abs=5e-5)
    assert s[(5, 4, 3, 1)] == pytest.approx(0.1293, abs=5e-5)
    assert s[(5, 4, 2, 2)] == pytest.approx(0.1058, abs=5e-5)
    assert s[(4, 3, 3, 3)] == pytest.approx(0.1054, abs=5e-5)
    assert s[(6, 3, 2, 2)] == pytest.approx(0.0564, abs=5e-5)
    assert s[(13, 0, 0, 0)] == pytest.approx(4 / math.comb(52, 13))
    # balanced hands, which Hand.balanced counts
    assert s[(4, 3, 3, 3)] + s[(4, 4, 3, 2)] + s[(5, 3, 3, 2)] == pytest.approx(0.47604, abs=5e-6)


def test_suit_length_pmf():
    p = P.suit_length_pmf()
    assert p.sum() == pytest.approx(1)
    assert np.arange(14) @ p == pytest.approx(13 / 4)  # a suit has 3.25 cards on average
    assert p.argmax() == 3  # 3 cards is the most likely length of a suit
    assert p[4] == pytest.approx(0.23861, abs=5e-6)  # cross-checked with scipy.stats.hypergeom


def test_partner_suit_length_pmf():
    for k in range(14):
        p = P.partner_suit_length_pmf(k)
        assert p.sum() == pytest.approx(1)
        assert np.arange(14) @ p == pytest.approx((13 - k) / 3)  # a third of what is left
        assert p[13 - k + 1:].sum() == 0  # can not hold more than are out
    assert P.partner_suit_length_pmf(13)[0] == pytest.approx(1)
    # with 4 spades the 9 outstanding are dealt 13 of 39 to partner (cross-checked with scipy.stats.hypergeom)
    assert P.partner_suit_length_pmf(4)[3] == pytest.approx(0.310718, abs=5e-7)
    with pytest.raises(ValueError):
        P.partner_suit_length_pmf(14)


def test_combined_suit_length_pmf():
    p = P.combined_suit_length_pmf()
    assert p.sum() == pytest.approx(1)
    assert np.arange(14) @ p == pytest.approx(6.5)
    # the chance of an 8+ card fit in one given suit (cross-checked with scipy.stats.hypergeom)
    assert p[8:].sum() == pytest.approx(0.261509, abs=5e-7)


def test_partner_aces_pmf():
    for k in range(5):
        p = P.partner_aces_pmf(k)
        assert p.sum() == pytest.approx(1)
        assert np.arange(5) @ p == pytest.approx((4 - k) / 3)
    assert P.partner_aces_pmf(4)[0] == pytest.approx(1)
    with pytest.raises(ValueError):
        P.partner_aces_pmf(5)


def test_opponent_splits_textbook():
    s5 = P.opponent_split_probabilities(8)  # 5 cards out
    assert s5[(3, 2)] == pytest.approx(0.6783, abs=5e-4)
    assert s5[(4, 1)] == pytest.approx(0.2826, abs=5e-4)
    assert s5[(5, 0)] == pytest.approx(0.0391, abs=5e-4)
    s4 = P.opponent_split_probabilities(9)  # 4 cards out
    assert s4[(2, 2)] == pytest.approx(0.4068, abs=5e-4)
    assert s4[(3, 1)] == pytest.approx(0.4975, abs=5e-4)
    assert s4[(4, 0)] == pytest.approx(0.0957, abs=5e-4)
    for n in range(14):
        assert sum(P.opponent_split_probabilities(n).values()) == pytest.approx(1)
    assert P.opponent_split_probabilities(13) == {(0, 0): pytest.approx(1)}
    with pytest.raises(ValueError):
        P.opponent_split_probabilities(14)

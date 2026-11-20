import numpy as np
import pytest

from .. import FastRound
from ..Deck import Deck
from ..Position import Position
from ..Round import Round, simpleHigh
from ..Suit import Suit
from ..Table import Table

TRUMPS = list(Suit.suits) + ['notrump']


def reference(deck, trump, leader):
    """the readable implementation: Round with simpleHigh at every seat"""
    return Round(Table(), list(deck.deal()), trump, [simpleHigh] * 4).play(leader)


def test_deck_to_ints_is_the_unshuffled_order():
    assert FastRound.deck_to_ints(Deck()) == list(range(52))
    assert sorted(FastRound.deck_to_ints(Deck(shuffle=3, rng=1))) == list(range(52))


@pytest.mark.parametrize('trump', TRUMPS)
def test_identical_to_round_with_simplehigh(trump):
    """every deck, every leader: the same tricks as the object-based Round"""
    for i in range(40):
        deck = Deck(shuffle=3, rng=100 + i)
        ints = FastRound.deck_to_ints(deck)
        for leader in Position.positions:
            assert FastRound.play_deck(ints, trump, leader) == reference(deck, trump, leader)


def test_identical_when_trump_is_none_or_a_suit_object():
    deck = Deck(shuffle=3, rng=7)
    ints = FastRound.deck_to_ints(deck)
    assert FastRound.play_deck(ints, None) == reference(deck, 'notrump', 'north')
    assert FastRound.play_deck(ints, Suit('hearts'), Position('west')) == reference(deck, 'hearts', 'west')


def test_unshuffled_deck():
    deck = Deck()
    ints = FastRound.deck_to_ints(deck)
    for trump in TRUMPS:
        assert FastRound.play_deck(ints, trump) == reference(deck, trump, 'north')


def test_every_round_has_13_tricks():
    rng = np.random.default_rng(3)
    for _ in range(200):
        ns, ew = FastRound.play_round(rng, 'hearts', 'south')
        assert ns + ew == 13 and 0 <= ns <= 13


def test_play_deck_accepts_any_sequence_and_does_not_change_it():
    ints = FastRound.deck_to_ints(Deck(shuffle=3, rng=2))
    before = list(ints)
    assert FastRound.play_deck(tuple(ints)) == FastRound.play_deck(np.array(ints))
    FastRound.play_deck(ints)
    assert ints == before


def test_bad_arguments():
    ints = list(range(52))
    with pytest.raises(ValueError):
        FastRound.play_deck(ints[:51])
    with pytest.raises(ValueError):
        FastRound.play_deck(ints, trump='bad')
    with pytest.raises(ValueError):
        FastRound.play_deck(ints, leader='North')
    with pytest.raises(ValueError):
        FastRound.simulate(np.random.default_rng(0), 3, leader='middle')
    with pytest.raises(ValueError):
        FastRound.play_round(np.random.default_rng(0), trump=7)


def test_shuffled_deck_is_a_permutation_and_reproducible():
    a = FastRound.shuffled_deck(np.random.default_rng(5))
    assert sorted(a) == list(range(52))
    assert a == FastRound.shuffled_deck(np.random.default_rng(5))
    assert a != FastRound.shuffled_deck(np.random.default_rng(6))


def test_simulate_shape_and_reproducibility():
    a = FastRound.simulate(np.random.default_rng(1), 300)
    assert a.shape == (300, 2) and a.dtype == np.int8
    assert (a.sum(axis=1) == 13).all()
    assert np.array_equal(a, FastRound.simulate(np.random.default_rng(1), 300))
    assert not np.array_equal(a, FastRound.simulate(np.random.default_rng(2), 300))
    assert FastRound.simulate(np.random.default_rng(1), 0).shape == (0, 2)


def test_simulate_matches_play_round():
    """with a fixed leader simulate is just play_round repeated"""
    a = FastRound.simulate(np.random.default_rng(8), 50, 'clubs', 'east')
    rng = np.random.default_rng(8)
    assert [tuple(r) for r in a] == [FastRound.play_round(rng, 'clubs', 'east') for _ in range(50)]


def test_rotating_leader_rotates():
    n = 8
    rotating = FastRound.simulate(np.random.default_rng(4), n)
    rng = np.random.default_rng(4)
    expected = [FastRound.play_round(rng, 'spades', Position.positions[i % 4]) for i in range(n)]
    assert [tuple(r) for r in rotating] == expected


def test_both_sides_win_equally_with_a_rotating_leader():
    """the statistics of the notebook and of test_round: 6.5 tricks a side"""
    out = FastRound.simulate(np.random.default_rng(8675309), 20_000)
    assert out.mean(axis=0) == pytest.approx([6.5, 6.5], abs=0.05)

import copy

import numpy as np
import pytest

from ..Deck import Deck
from ..Hand import Hand


def test_deck():
    d = Deck()
    assert len(d) == 52


def test_from_cards():
    d1 = Deck()
    d2 = Deck(list(d1)[:10])
    assert len(d2) == 10
    assert d2 == Deck(d1[:10])


def test_shuffle():
    d1 = Deck()
    d2 = copy.deepcopy(d1)
    d2.shuffle(num=2)
    assert len(d2) == 52
    assert d1 != d2


def test_shuffle_on_creation():
    d = Deck(shuffle=3)
    assert len(d) == 52
    assert d != Deck()
    assert sorted(d.toCode()[i:i + 2] for i in range(0, 104, 2)) == \
        sorted(Deck().toCode()[i:i + 2] for i in range(0, 104, 2))


def test_same_seed_same_deck():
    assert Deck(shuffle=2, rng=5) == Deck(shuffle=2, rng=5)
    assert Deck(shuffle=2, rng=5) != Deck(shuffle=2, rng=6)


def test_rng_can_be_a_generator():
    """a shared Generator gives a reproducible sequence of decks"""
    rng1 = np.random.default_rng(42)
    rng2 = np.random.default_rng(42)
    decks1 = [Deck(shuffle=2, rng=rng1) for _ in range(3)]
    decks2 = [Deck(shuffle=2, rng=rng2) for _ in range(3)]
    assert decks1 == decks2
    assert decks1[0] != decks1[1]


def test_default_rng_is_random():
    assert Deck(shuffle=2) != Deck(shuffle=2)


def test_deepcopy_keeps_working():
    d1 = Deck(rng=7)
    d2 = copy.deepcopy(d1)
    d1.shuffle()
    d2.shuffle()
    assert d1 == d2  # same generator state, same shuffle


def test_cut():
    d1 = Deck()
    d2 = copy.deepcopy(d1)
    d1.cut(10)
    assert d1[0] == d2[10]
    assert len(d1) == 52
    # a random cut always moves the deck
    for i in range(200):
        d1 = Deck(rng=i)
        d1.cut()
        assert d1[0] != d2[0]
        assert len(d1) == 52


def test_cut_is_reproducible():
    d1, d2 = Deck(rng=3), Deck(rng=3)
    d1.cut()
    d2.cut()
    assert d1 == d2


def test_eq():
    d1 = Deck()
    d2 = Deck()
    assert d1 == d2


def test_deal():
    d1 = Deck()
    h1, h2, h3, h4 = d1.deal()
    assert len(h1) == len(h2) == len(h3) == len(h4)
    assert h1 == Hand(d1[::4])


def test_toCode():
    d1 = Deck()
    ans = '2s3s4s5s6s7s8s9s0sJsQsKsAs2h3h4h5h6h7h8h9h0hJhQhKhAh2d3d4d5d6d7d8d9d0dJdQdKdAd2c3c4c5c6c7c8c9c0cJcQcKcAc'
    assert d1.toCode() == ans


def test_fromCode():
    d1 = Deck()
    ans = '2s3s4s5s6s7s8s9s0sJsQsKsAs2h3h4h5h6h7h8h9h0hJhQhKhAh2d3d4d5d6d7d8d9d0dJdQdKdAd2c3c4c5c6c7c8c9c0cJcQcKcAc'
    d2 = Deck.fromCode(ans)
    assert d1 == d2


def test_fromCode_takes_rng():
    code = Deck().toCode()
    assert Deck.fromCode(code, rng=9).rng is not Deck.fromCode(code).rng
    a, b = Deck.fromCode(code, rng=9), Deck.fromCode(code, rng=9)
    a.shuffle()
    b.shuffle()
    assert a == b

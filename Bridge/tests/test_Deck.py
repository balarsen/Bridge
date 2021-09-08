import copy

import numpy as np

from ..Deck import Deck
from ..Hand import Hand


def test_deck():
    d = Deck()
    assert len(d) == 52


def test_shuffle():
    d1 = Deck()
    d2 = copy.deepcopy(d1)
    d2.shuffle(num=2)
    assert len(d2) == 52
    assert d1 != d2


def test_cut():
    np.random.default_rng(8675309)
    d1 = Deck()
    d2 = copy.deepcopy(d1)
    d1.cut(10)
    assert d1[0] == d2[10]
    d1 = Deck()
    d1.cut()
    assert d1[0] != d2[0]


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



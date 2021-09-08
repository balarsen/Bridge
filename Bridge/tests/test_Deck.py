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

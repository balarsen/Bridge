import pytest

from ..Suit import Suit


def test_ValueError():
    with pytest.raises(ValueError):
        Suit('bad')


def test_eq():
    a = Suit('spades')
    b = Suit('spades')
    assert a == b


def test_ne():
    a = Suit('spades')
    b = Suit('hearts')
    assert a != b


def test_str():
    assert str(Suit('spades')) == 'spades'


def test_repr():
    assert repr(Suit('spades')) == '<spades>'

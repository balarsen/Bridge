import pytest

from ..Suit import Suit


def test_ValueError():
    with pytest.raises(ValueError):
        Suit('bad')


def test_eq():
    a = Suit('spades')
    b = Suit('spades')
    assert a == b
    assert a == 'spades'


def test_ne():
    a = Suit('spades')
    b = Suit('hearts')
    assert a != b
    assert a != 'clubs'


def test_ne_equal_suits():
    """equal suits must not be !="""
    assert (Suit('spades') != Suit('spades')) is False
    assert (Suit('spades') != 'spades') is False
    assert (Suit('spades') != Suit('hearts')) is True


def test_hash():
    assert len({Suit('spades'), Suit('spades'), Suit('hearts')}) == 2


def test_str():
    assert str(Suit('spades')) == 'spades'


def test_repr():
    assert repr(Suit('spades')) == '<spades>'


def test_letterToSuit():
    ans = ['diamonds', 'clubs', 'hearts', 'hearts']
    tst = Suit.letterToSuit('dchh')
    assert tst == ans


def test_letterToSuit_1letter():
    assert Suit.letterToSuit('d') == 'diamonds'

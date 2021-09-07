import pytest

from ..Card import Card


def test_init():
    """input checking"""
    with pytest.raises(ValueError):
        Card(15, 'hearts')
    with pytest.raises(ValueError):
        Card('bad', 'hearts')
    with pytest.raises(ValueError):
        Card(2, 'bad')


def test_eq():
    fourS = Card(4, 'spades')
    fourS2 = Card(4, 'spades')
    assert fourS2 == fourS


def test_ne():
    fourS = Card(4, 'spades')
    fourH = Card(4, 'hearts')
    assert fourH != fourS
    twoH = Card(2, 'hearts')
    assert twoH != fourS
    assert twoH != fourH


def test_gt():
    fourS = Card(4, 'spades')
    fourH = Card(4, 'hearts')
    twoH = Card(2, 'hearts')
    assert fourH > twoH
    assert (fourH > fourS) is False


def test_gt_trump():
    fourS = Card(4, 'spades', trump=True)
    twoS = Card(2, 'spades', trump=True)
    fourH = Card(4, 'hearts')
    twoH = Card(2, 'hearts')
    assert fourS > fourH
    assert (fourH > fourS) is False
    assert fourS > twoS


def test_lt():
    fourS = Card(4, 'spades')
    fourH = Card(4, 'hearts')
    twoH = Card(2, 'hearts')
    assert twoH < fourH
    assert (fourH < fourS) is False


def test_lt_trump():
    fourS = Card(4, 'spades', trump=True)
    twoS = Card(2, 'spades', trump=True)
    fourH = Card(4, 'hearts')
    twoH = Card(2, 'hearts')
    assert fourH < fourS
    assert (fourS < fourH) is False
    assert twoS < fourS


def test_str():
    assert str(Card('Q', 'spades')) == 'Q of spades'


def test_repr():
    assert repr(Card('Q', 'spades')) == '<Q of spades>'

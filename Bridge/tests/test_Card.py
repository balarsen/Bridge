import pytest

from ..Card import Card
from ..Suit import Suit
from ..Value import Value


def test_init():
    """input checking"""
    with pytest.raises(ValueError):
        Card(15, 'hearts')
    with pytest.raises(ValueError):
        Card('bad', 'hearts')
    with pytest.raises(ValueError):
        Card('2', 'bad')


def test_init_from_instances():
    c = Card(Value('Q'), Suit('hearts'))
    assert c == Card('Q', 'hearts')
    assert c.value == Value('Q')
    assert c.suit == 'hearts'


def test_no_trump_state():
    """whether a card is trump is a property of the trick, not the card"""
    assert not hasattr(Card('4', 'spades'), 'trump')
    with pytest.raises(TypeError):
        Card('4', 'spades', trump=True)


def test_eq():
    fourS = Card('4', 'spades')
    fourS2 = Card('4', 'spades')
    assert fourS2 == fourS


def test_ne_equal_cards():
    """equal cards must not be !="""
    assert (Card('4', 'spades') != Card('4', 'spades')) is False
    assert (Card('4', 'spades') != Card('4', 'hearts')) is True


def test_hash():
    assert len({Card('4', 'spades'), Card('4', 'spades'), Card('4', 'hearts')}) == 2


def test_eq_other_types():
    assert Card('4', 'spades') != '4s'
    assert not Card('4', 'spades') == '4s'


def test_ne():
    fourS = Card('4', 'spades')
    fourH = Card('4', 'hearts')
    assert fourH != fourS
    twoH = Card('2', 'hearts')
    assert twoH != fourS
    assert twoH != fourH


def test_gt():
    fourS = Card('4', 'spades')
    fourH = Card('4', 'hearts')
    twoH = Card('2', 'hearts')
    assert fourH > twoH
    assert (twoH > fourH) is False
    assert (fourH > fourS) is False


def test_lt():
    fourS = Card('4', 'spades')
    fourH = Card('4', 'hearts')
    twoH = Card('2', 'hearts')
    assert twoH < fourH
    assert (fourH < twoH) is False
    assert (fourH < fourS) is False


def test_different_suits_do_not_compare():
    """across suits both < and > are False, trump is decided by the Trick"""
    aceS = Card('A', 'spades')
    twoH = Card('2', 'hearts')
    assert (aceS > twoH) is False
    assert (aceS < twoH) is False
    assert (twoH > aceS) is False
    assert (twoH < aceS) is False


def test_compare_other_types():
    with pytest.raises(TypeError):
        Card('4', 'spades') < 4
    with pytest.raises(TypeError):
        Card('4', 'spades') > 4


def test_str():
    assert str(Card('Q', 'spades')) == 'Q of spades'


def test_repr():
    assert repr(Card('Q', 'spades')) == '<Q of spades>'


def test_toCode():
    fourS = Card('4', 'spades')
    twoS = Card('2', 'spades')
    fourH = Card('4', 'hearts')
    twoH = Card('2', 'hearts')
    assert fourS.toCode() == '4s'
    assert twoS.toCode() == '2s'
    assert fourH.toCode() == '4h'
    assert twoH.toCode() == '2h'


def test_fromCode():
    assert Card.fromCode('4s') == Card('4', 'spades')
    assert Card.fromCode('2s') == Card('2', 'spades')
    assert Card.fromCode('4h') == Card('4', 'hearts')
    assert Card.fromCode('2h') == Card('2', 'hearts')

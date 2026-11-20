import pytest

from ..Card import Card
from ..Position import Position
from ..Trick import Trick, beats


def make_trick(leader, trump, codes):
    t = Trick(leader, trump)
    for c in codes.split():
        t.nextCard(Card.fromCode(c))
    return t


def test_init():
    """init does some checking"""
    with pytest.raises(ValueError):
        Trick(leader='badval')
    tck = Trick()
    assert tck.leader == 'north'
    assert tck.trump is None
    tck = Trick(leader='south', trump='diamonds')
    assert tck.leader == 'south'
    assert tck.trump == 'diamonds'


def test_nextCard():
    """should be able to add cards"""
    t = Trick(trump='hearts')
    t.nextCard(Card.fromCode('3d'))
    assert t.nCards == len(t) == 1
    t.nextCard(Card.fromCode('5h'))
    with pytest.raises(ValueError):
        t.nextCard(Card.fromCode('5h'))
    t.nextCard(Card.fromCode('7d'))
    t.nextCard(Card.fromCode('9d'))
    assert t.nCards == 4
    with pytest.raises(IndexError):
        t.nextCard(Card.fromCode('0d'))


def test_nextCard_does_not_change_the_card():
    card = Card.fromCode('5h')
    before = dict(vars(card))
    Trick(trump='hearts').nextCard(card)
    assert vars(card) == before


def test_beats_same_suit():
    assert beats(Card.fromCode('Kd'), Card.fromCode('5d'))
    assert not beats(Card.fromCode('5d'), Card.fromCode('Kd'))
    assert not beats(Card.fromCode('5d'), Card.fromCode('5d'))  # can't beat itself


def test_beats_trump():
    assert beats(Card.fromCode('2s'), Card.fromCode('Ad'), trump='spades')
    assert not beats(Card.fromCode('Ad'), Card.fromCode('2s'), trump='spades')
    # two trumps go by value
    assert beats(Card.fromCode('3s'), Card.fromCode('2s'), trump='spades')
    assert not beats(Card.fromCode('2s'), Card.fromCode('3s'), trump='spades')


def test_beats_off_suit_never_wins():
    assert not beats(Card.fromCode('Ah'), Card.fromCode('2d'), trump='spades')
    assert not beats(Card.fromCode('Ah'), Card.fromCode('2d'))


@pytest.mark.parametrize('trump', [None, 'notrump'])
def test_beats_no_trump(trump):
    assert not beats(Card.fromCode('2s'), Card.fromCode('Ad'), trump=trump)
    assert beats(Card.fromCode('Ad'), Card.fromCode('2d'), trump=trump)


def test_wouldWin():
    t = make_trick('north', 'spades', '5d')
    assert t.wouldWin(Card.fromCode('6d'))
    assert not t.wouldWin(Card.fromCode('4d'))
    assert t.wouldWin(Card.fromCode('2s'))
    assert not t.wouldWin(Card.fromCode('Ah'))
    t.nextCard(Card.fromCode('2s'))
    assert not t.wouldWin(Card.fromCode('Ad'))  # a trump is winning
    assert t.wouldWin(Card.fromCode('3s'))
    with pytest.raises(IndexError):
        Trick().wouldWin(Card.fromCode('3s'))


def test_winner():
    """winner should be named correctly"""
    t = Trick(trump='hearts')
    t.nextCard(Card.fromCode('3d'))
    with pytest.raises(IndexError):
        t.winner()
    t.nextCard(Card.fromCode('5h'))
    t.nextCard(Card.fromCode('7d'))
    t.nextCard(Card.fromCode('9d'))
    assert t.winner() == (Card('5', 'hearts'), 'east')


def test_winner_no_trump():
    t = Trick(leader='west')
    for c in ('3d', 'Ah', '9d', '5s'):  # off suit cards never win
        t.nextCard(Card.fromCode(c))
    assert t.winner() == (Card('9', 'diamonds'), 'east')  # west, north, east, south
    t = Trick(leader='west', trump='notrump')
    for c in ('3d', 'Ah', '9d', '5s'):
        t.nextCard(Card.fromCode(c))
    assert t.winner() == (Card('9', 'diamonds'), 'east')  # west, north, east, south


def test_leadSuit_currentWinner():
    t = Trick(leader='east', trump='spades')
    with pytest.raises(IndexError):
        t.leadSuit
    with pytest.raises(IndexError):
        t.currentWinner()
    t.nextCard(Card.fromCode('5d'))
    assert t.leadSuit == 'diamonds'
    assert t.currentWinner() == (Card('5', 'diamonds'), 'east')
    t.nextCard(Card.fromCode('Kd'))
    assert t.currentWinner() == (Card('K', 'diamonds'), 'south')
    t.nextCard(Card.fromCode('2s'))
    assert t.currentWinner() == (Card('2', 'spades'), 'west')


def test_getCard():
    """should be able to get cards played"""
    t = Trick(trump='hearts')
    for p in Position.positions:
        assert t.getCard(p) is None
    for c in ('3d', '4d', '5d', '6d'):
        t.nextCard(Card.fromCode(c))
    assert t.north == Card.fromCode('3d')
    assert t.east == Card.fromCode('4d')
    assert t.south == Card.fromCode('5d')
    assert t.west == Card.fromCode('6d')


def test_getCard_leader_not_north():
    """cards are indexed by who played them, not by trick order"""
    t = Trick(leader='south')
    for c in ('3d', '4d', '5d', '6d'):
        t.nextCard(Card.fromCode(c))
    assert t.south == Card.fromCode('3d')
    assert t.west == Card.fromCode('4d')
    assert t.north == Card.fromCode('5d')
    assert t.east == Card.fromCode('6d')


def test_repr_partial_trick():
    t = Trick()
    t.nextCard(Card.fromCode('3d'))
    s = repr(t)  # unplayed seats must not blow up the printout
    assert '3 of diamonds' in s
    assert str(t) == 'Trick'

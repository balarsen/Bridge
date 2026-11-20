import pytest

from ..Bid import Bid


@pytest.fixture
def bids():
    return dict(h1=Bid(1, 'hearts'),
                s1=Bid(1, 'spades'),
                c1=Bid(1, 'clubs'),
                nt1=Bid(1, 'notrump'),
                h4=Bid(4, 'hearts'))


def test_init():
    """input checking"""
    with pytest.raises(ValueError):
        Bid(0, 'hearts')
    with pytest.raises(ValueError):
        Bid(8, 'hearts')
    with pytest.raises(ValueError):
        Bid('1', 'hearts')
    with pytest.raises(ValueError):
        Bid(2, 'bad')
    with pytest.raises(ValueError):
        Bid(2)  # needs a strain
    assert Bid(3, 'hearts').value == 3
    assert Bid(3, 'hearts').suit == 'hearts'


def test_pass():
    assert Bid('pass').value == 'pass'
    assert Bid('pass').isPass
    assert not Bid(1, 'clubs').isPass
    # a suit handed to a pass is ignored
    assert Bid('pass', 'hearts') == Bid('pass')
    assert Bid('pass', 1) == Bid('pass')
    assert Bid('pass').suit is None


def test_eq_ne(bids):
    assert bids['h1'] == Bid(1, 'hearts')
    assert bids['h1'] == bids['h1']
    assert bids['h1'] != bids['c1']
    assert bids['c1'] != bids['h4']
    assert not (bids['h1'] != Bid(1, 'hearts'))
    assert not (bids['h1'] == bids['c1'])
    assert bids['h1'] != 'hearts'


def test_hash(bids):
    assert len({bids['h1'], Bid(1, 'hearts'), bids['c1']}) == 2


def test_gt_lt(bids):
    assert bids['h1'] > bids['c1']
    assert bids['c1'] < bids['h4']
    assert bids['h4'] > bids['h1']
    assert not bids['h1'] < bids['c1']
    assert not bids['c1'] > bids['h4']
    assert not bids['h4'] < bids['h1']
    assert bids['h1'] < bids['s1']


def test_ordering_is_level_then_strain():
    ordered = [Bid(lev, s) for lev in range(1, 8)
               for s in ('clubs', 'diamonds', 'hearts', 'spades', 'notrump')]
    assert sorted(reversed(ordered)) == ordered
    # a higher level always beats a higher strain
    assert Bid(2, 'clubs') > Bid(1, 'notrump')
    assert Bid(1, 'notrump') > Bid(1, 'spades')


def test_pass_is_lowest():
    assert Bid('pass') < Bid(1, 'clubs')
    assert not Bid('pass') > Bid(7, 'notrump')
    assert not Bid('pass') < Bid('pass')


def test_str():
    assert str(Bid('pass')) == 'pass'
    assert str(Bid(2, 'hearts')) == '2 hearts'
    assert repr(Bid(1, 'notrump')) == '1 notrump'

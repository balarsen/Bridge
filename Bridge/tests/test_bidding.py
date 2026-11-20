import pytest

from .. import Bidding
from ..Bid import Bid

PASS = Bid('pass')


@pytest.fixture
def bidding():
    return Bidding.Bidding(leader='north')


def test_init():
    b = Bidding.Bidding(leader='south')
    assert b._seats == ['south', 'west', 'north', 'east']
    assert b._passCount == 0
    assert b.leader == 'south'
    with pytest.raises(ValueError):
        Bidding.Bidding(leader='bad')


def test_addBid(bidding):
    assert bidding.addBid('north', Bid(2, 'hearts')) is None
    assert len(bidding) == 1
    assert bidding._passCount == 0
    with pytest.raises(ValueError):
        bidding.addBid('east', Bid(1, 'hearts'))  # too low
    assert bidding.addBid('east', PASS) is None
    assert bidding._passCount == 1
    assert bidding.addBid('south', PASS) is None
    # three passes after a bid end the auction
    assert bidding.addBid('west', PASS) == ('north', Bid(2, 'hearts'))
    assert bidding.complete
    with pytest.raises(ValueError):
        bidding.addBid('north', Bid(5, 'hearts'))  # the auction is over


def test_addBid_bad_seat(bidding):
    with pytest.raises(ValueError):
        bidding.addBid('North', Bid(1, 'hearts'))


def test_bid_resets_pass_count(bidding):
    bidding.addBid('north', Bid(1, 'clubs'))
    bidding.addBid('east', PASS)
    bidding.addBid('south', PASS)
    bidding.addBid('west', Bid(1, 'hearts'))
    assert bidding._passCount == 0
    assert not bidding.complete


def test_pass_after_bid_is_allowed(bidding):
    """a pass is never "lower than" the standing bid"""
    bidding.addBid('north', Bid(7, 'notrump'))
    bidding.addBid('east', PASS)
    assert bidding._passCount == 1


def test_open_in_third_seat(bidding):
    """passes before the opening bid do not count towards ending the auction"""
    for _ in range(3):
        bidding.nextBid(PASS)
    assert not bidding.complete
    assert bidding.nextBid(Bid(1, 'spades')) is None
    assert bidding.opened


def test_redeal(bidding):
    """if no one bids we need to redeal"""
    bidding.nextBid(PASS)
    bidding.nextBid(PASS)
    bidding.nextBid(PASS)
    with pytest.raises(Bidding.Redeal):
        bidding.nextBid(PASS)
    assert not bidding.opened


def test_winningBid(bidding):
    bidding.addBid('north', PASS)
    assert bidding._winningBid() is None
    bidding.addBid('north', Bid(2, 'hearts'))
    assert bidding._winningBid() == ('north', Bid(2, 'hearts'))


def test_nextBid(bidding):
    bidding.nextBid(Bid(1, 'hearts'))
    assert bidding._winningBid() == ('north', Bid(1, 'hearts'))
    bidding.nextBid(Bid(1, 'spades'))
    assert bidding._winningBid() == ('east', Bid(1, 'spades'))


def test_nextBid_follows_leader():
    b = Bidding.Bidding(leader='west')
    b.nextBid(Bid(1, 'clubs'))
    b.nextBid(Bid(1, 'diamonds'))
    assert [s for s, _ in b] == ['west', 'north']


def test_logic_is_abstract():
    with pytest.raises(TypeError):
        Bidding.Bidding_logic(None)

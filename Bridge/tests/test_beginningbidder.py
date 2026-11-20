import pytest

from ..BeginningBidder import BeginningBidder
from ..Bid import Bid
from ..Card import Card
from ..Hand import Hand


def make_hand(codes):
    """build a hand from a string of 2 letter card codes, 'As Kd 0h ...' (0 is ten)"""
    return Hand([Card.fromCode(c) for c in codes.split()])


# 14 HCP, 4333, spades are longest and strongest
OPEN14 = 'As Ks 5s 2s Qh Jh 4h Kd 6d 3d 7c 5c Jc'
# 13 HCP, the same hand with the club jack made a four
PASS13 = 'As Ks 5s 2s Qh Jh 4h Kd 6d 3d 7c 5c 4c'
# 16 HCP, long weak spades, the strongest suit is a 5 card heart suit
STRONG_HEARTS = '8s 7s 6s 5s 3s 2s Ah Kh Qh 5h 3h Ad Kd'
# 14 HCP, the strongest suit is only 3 cards, the longest is spades
SHORT_STRONG = '9s 8s 7s 6s Ah Kh Qh Ad 5d 3d Jc 4c 2c'
# 3 HCP
WEAK = '9s 8s 7s 6s 4h 3h 2h Jd 5d 3d Qc 4c 2c'


def test_hcp_of_test_hands():
    assert make_hand(OPEN14).hcp() == 14
    assert make_hand(PASS13).hcp() == 13
    assert make_hand(STRONG_HEARTS).hcp() == 16
    assert make_hand(SHORT_STRONG).hcp() == 14
    assert make_hand(WEAK).hcp() == 3


def test_pass_with_few_points():
    assert BeginningBidder(make_hand(WEAK)).openBid() == Bid('pass')
    assert BeginningBidder(make_hand(PASS13)).openBid() == Bid('pass')


def test_14hcp_opens():
    assert BeginningBidder(make_hand(OPEN14)).openBid() == Bid(1, 'spades')


def test_strongest_suit_is_longest():
    bb = BeginningBidder(make_hand(OPEN14))
    assert bb.openBid() == Bid(1, 'spades')


def test_strongest_suit_not_longest_but_five_cards():
    bb = BeginningBidder(make_hand(STRONG_HEARTS))
    assert bb.openBid() == Bid(1, 'hearts')


def test_strongest_suit_short_opens_longest():
    bb = BeginningBidder(make_hand(SHORT_STRONG))
    assert bb.openBid() == Bid(1, 'spades')


def test_tied_longest_suits_open_higher_ranking():
    # spades and hearts are both 4 long, the strongest suit (diamonds) is only 3 long
    hand = make_hand('Ks 6s 5s 2s Kh 6h 5h 2h Ad Kd 5d Ac 3c')
    assert hand.hcp() == 17
    assert BeginningBidder(hand).openBid() == Bid(1, 'spades')


def test_tied_strongest_and_longest_open_higher_ranking():
    # hearts and diamonds are both 4 long with 6 HCP, both strongest and longest
    hand = make_hand('Qs 3s 2s Ah Qh 5h 2h Kd Qd Jd 2d 4c 3c')
    assert hand.hcp() == 14
    assert hand.strongest()[:2] == [('hearts', 6), ('diamonds', 6)]
    assert hand.longest()[:2] == [('hearts', 4), ('diamonds', 4)]
    assert BeginningBidder(hand).openBid() == Bid(1, 'hearts')


def test_raise_and_jump_not_implemented_yet():
    bb = BeginningBidder(make_hand(OPEN14))
    assert bb.raiseBid() is None
    assert bb.jumpBid() is None

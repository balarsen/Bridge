import pytest

from ..Auction import MAX_CALLS, AuctionResult, run_auction
from ..Bid import Bid
from ..Card import Card
from ..Contract import Contract
from ..Deck import Deck
from ..Hand import Hand
from ..Position import Position
from ..PointsAndFit import PointsAndFit, cheapest, opening_range, response_range, target

PASS = Bid('pass')


def H(spades, hearts, diamonds, clubs, hcp, shape=None):
    """
    A hand from the ranks held in each suit ('AK52', ten is '0'), checked: 13 cards, the stated high card
    points, and the stated shape (spades, hearts, diamonds, clubs) if given.
    """
    cards = [Card.fromCode(r + suit) for suit, ranks in zip('shdc', (spades, hearts, diamonds, clubs)) for r in ranks]
    h = Hand(cards)
    assert h.hcp() == hcp, f'{spades}.{hearts}.{diamonds}.{clubs} has {h.hcp()} points, not {hcp}'
    if shape is not None:
        assert tuple(n for _, n in h.distro()) == shape
    return h


def call(hand, seat, auction):
    bot = PointsAndFit(hand, seat)
    return bot.call(auction), bot


def A(*calls):
    """an auction: ('n', 1, 'hearts') or ('e', 'p')"""
    seats = {'n': 'north', 'e': 'east', 's': 'south', 'w': 'west'}
    return [(seats[c[0]], PASS if c[1] == 'p' else Bid(c[1], c[2])) for c in calls]


BAL16 = H('AK52', 'QJ4', 'KJ3', 'Q52', 16, (4, 3, 3, 3))
BAL22 = H('AKQ4', 'AK4', 'QJ3', 'K52', 22, (4, 3, 3, 3))
WEAK = H('K976', '643', '853', 'J74', 4)


# ---------------------------------------------------------------------------------------------- the tables
def test_target_levels():
    assert target(19, 'notrump') is None and target(20, 'notrump') == (1, 'notrump')
    assert target(23, 'notrump') == (2, 'notrump') and target(26, 'notrump') == (3, 'notrump')
    assert target(20, 'hearts') == (2, 'hearts') and target(23, 'hearts') == (3, 'hearts')
    assert target(26, 'spades') == (4, 'spades') and target(32, 'spades') == (4, 'spades')
    assert target(25, 'clubs') == (3, 'clubs') and target(26, 'clubs') == (3, 'notrump')
    assert target(28, 'diamonds') == (3, 'notrump') and target(29, 'diamonds') == (5, 'diamonds')
    assert target(20, 'clubs') == (2, 'clubs') and target(19, 'clubs') is None
    for strain in ('notrump', 'hearts', 'clubs'):
        assert target(33, strain) == (6, strain) and target(36.5, strain) == (6, strain)
        assert target(37, strain) == (7, strain)


def test_cheapest_legal_bid():
    assert cheapest(2, 'hearts', None) == Bid(2, 'hearts')
    assert cheapest(1, 'hearts', Bid(1, 'spades')) == Bid(2, 'hearts')  # 1H is below 1S
    assert cheapest(1, 'notrump', Bid(1, 'spades')) == Bid(1, 'notrump')
    assert cheapest(2, 'clubs', Bid(2, 'spades')) == Bid(3, 'clubs')
    assert cheapest(7, 'clubs', Bid(7, 'spades')) is None


def test_ranges_the_calls_show():
    assert opening_range(Bid(1, 'notrump')) == (15, 17) and opening_range(Bid(2, 'notrump')) == (20, 21)
    assert opening_range(Bid(1, 'hearts')) == (12, 21)
    one_heart, one_nt, two_nt = Bid(1, 'hearts'), Bid(1, 'notrump'), Bid(2, 'notrump')
    assert [response_range(one_heart, Bid(level, 'hearts')) for level in (2, 3, 4, 6)] == [(6, 9), (10, 12), (13, 16), (17, 40)]
    assert response_range(one_heart, Bid(1, 'spades')) == (6, 16)
    assert response_range(one_heart, Bid(2, 'clubs')) == (10, 16)
    assert response_range(one_heart, Bid(1, 'notrump')) == (6, 9)
    assert response_range(one_heart, Bid(3, 'notrump')) == (13, 16)
    assert response_range(one_heart, Bid(6, 'notrump')) == (17, 40)
    assert response_range(one_nt, Bid(2, 'notrump')) == (8, 9)
    assert response_range(one_nt, Bid(3, 'notrump')) == (10, 15)
    assert response_range(one_nt, Bid(6, 'notrump')) == (16, 40)
    assert response_range(one_nt, Bid(2, 'spades')) == (6, 9)
    assert response_range(one_nt, Bid(4, 'spades')) == (10, 15)
    assert response_range(two_nt, Bid(3, 'notrump')) == (4, 11)
    assert response_range(two_nt, Bid(6, 'notrump')) == (12, 40)


# ---------------------------------------------------------------------------------------------- opening
@pytest.mark.parametrize('hand, expected', [
    (BAL16, Bid(1, 'notrump')),
    (BAL22, Bid(2, 'notrump')),
    (WEAK, PASS),
    (H('AKQ42', 'J4', 'K53', '942', 13, (5, 2, 3, 3)), Bid(1, 'spades')),            # five spades, 5-3-3-2 but only 13
    (H('K4', 'AQJ752', '85', 'Q32', 12, (2, 6, 2, 3)), Bid(1, 'hearts')),
    (H('AKQ72', 'K9852', '4', '32', 12, (5, 5, 1, 2)), Bid(1, 'spades')),            # equal majors: spades
    (H('AK52', 'AQ9876', '4', '32', 13, (4, 6, 1, 2)), Bid(1, 'hearts')),            # the longer major
    (H('AK4', 'Q4', 'KJ8542', 'Q5', 15, (3, 2, 6, 2)), Bid(1, 'diamonds')),          # the longer minor
    (H('AK4', 'Q4', 'KJ', 'Q95432', 15, (3, 2, 2, 6)), Bid(1, 'clubs')),
    (H('A94', 'Q4', 'KJ85', 'Q952', 12, (3, 2, 4, 4)), Bid(1, 'diamonds')),          # 4-4 in the minors: diamonds
    (H('AK94', 'Q72', 'J85', 'Q52', 12, (4, 3, 3, 3)), Bid(1, 'clubs')),              # 3-3 in the minors: clubs
])
def test_opening_calls(hand, expected):
    bid, bot = call(hand, 'north', [])
    assert bid == expected and bot.reason


def test_the_open_threshold_can_be_changed():
    thirteen = H('AKQ42', 'J4', 'K53', '942', 13)
    assert PointsAndFit(thirteen, 'north', open_hcp=14).call([]).isPass
    assert PointsAndFit(thirteen, 'north', open_hcp=13).call([]) == Bid(1, 'spades')
    assert PointsAndFit(thirteen, 'north').open_hcp == PointsAndFit.OPEN_HCP == 12


def test_the_interface_methods_of_bidding_logic():
    bot = PointsAndFit(BAL16, 'north')
    assert bot.openBid() == Bid(1, 'notrump')
    assert bot.raiseBid([]) == bot.raiseBid() == bot.jumpBid() == bot.jumpBid([]) == Bid(1, 'notrump')


def test_no_competition_over_the_other_sides_opening():
    bid, bot = call(BAL22, 'east', A(('n', 1, 'hearts')))  # east has 22 points but the other side opened
    assert bid == PASS and 'other side' in bot.reason


# ---------------------------------------------------------------------------------------------- responding to a suit
def respond(hand, opening=Bid(1, 'hearts')):
    return call(hand, 'south', [('north', opening), ('east', PASS)])


def test_responder_passes_with_five_points_or_less():
    bid, bot = respond(WEAK)
    assert bid == PASS and 'too few' in bot.reason


def test_raising_the_openers_major_by_strength():
    for hand, expected in [(H('9876', 'Q53', 'K5', 'J432', 6, (4, 3, 2, 4)), Bid(2, 'hearts')),
                           (H('A876', 'Q53', 'K5', 'J432', 10), Bid(3, 'hearts')),
                           (H('AK76', 'Q53', 'K5', 'J432', 13), Bid(4, 'hearts')),
                           (H('AK76', 'KQ3', 'K5', 'QJ32', 18), Bid(6, 'hearts'))]:
        bid, bot = respond(hand)
        assert bid == expected and 'support' in bot.reason


def test_raising_a_minor_needs_five_card_support():
    opening = Bid(1, 'clubs')
    assert respond(H('K43', '54', 'J52', 'Q9876', 6, (3, 2, 3, 5)), opening)[0] == Bid(2, 'clubs')
    assert respond(H('AK3', '54', 'J52', 'Q9876', 10), opening)[0] == Bid(3, 'clubs')
    assert respond(H('AK3', 'K4', 'J52', 'Q9876', 13), opening)[0] == Bid(3, 'notrump')
    assert respond(H('AK3', 'AK', 'J52', 'Q9876', 17), opening)[0] == Bid(6, 'notrump')
    # four clubs are not enough support: a different call
    four = H('K432', '54', 'J52', 'Q987', 6, (4, 2, 3, 4))
    assert respond(four, opening)[0] == Bid(1, 'spades')


def test_a_new_suit_at_the_one_level():
    bid, bot = respond(H('KQ76', '54', 'J52', '9876', 6, (4, 2, 3, 4)))
    assert bid == Bid(1, 'spades') and '4 spades' in bot.reason


def test_a_new_suit_at_the_two_level_needs_ten_points():
    assert respond(H('K43', '54', 'A52', 'KQ876', 12, (3, 2, 3, 5)))[0] == Bid(2, 'clubs')
    # 8 points: the club suit would be at the two level, so notrump instead
    assert respond(H('K43', '54', '852', 'KQ876', 8))[0] == Bid(1, 'notrump')


def test_the_longer_suit_first_and_the_cheaper_one_when_equal():
    # 5 hearts and 4 diamonds over 1 club: the longer suit, hearts
    assert respond(H('K4', 'Q9876', 'AJ75', '32', 10, (2, 5, 4, 2)), Bid(1, 'clubs'))[0] == Bid(1, 'hearts')
    # 4 hearts and 4 spades over 1 diamond: hearts first, up the line
    assert respond(H('KJ76', 'Q954', '52', 'J32', 7, (4, 4, 2, 3)), Bid(1, 'diamonds'))[0] == Bid(1, 'hearts')


def test_notrump_responses_by_strength():
    opening = Bid(1, 'clubs')
    for hand, expected in [(H('Q76', 'K54', 'J52', '9876', 6, (3, 3, 3, 4)), Bid(1, 'notrump')),
                           (H('AQ6', 'K54', 'J52', '9876', 10), Bid(2, 'notrump')),
                           (H('AQ6', 'KJ4', 'KJ2', '9876', 14), Bid(3, 'notrump')),
                           (H('AK6', 'KQ4', 'AJ2', '9876', 17), Bid(6, 'notrump'))]:
        bid, bot = respond(hand, opening)
        assert bid == expected and 'notrump' in bot.reason


# ---------------------------------------------------------------------------------------------- responding to notrump
def over(hand, nt_level):
    return call(hand, 'south', [('north', Bid(nt_level, 'notrump')), ('east', PASS)])


def test_responses_to_1nt():
    assert over(WEAK, 1)[0] == PASS
    assert over(H('A976', '643', 'Q53', 'J74', 7), 1)[0] == PASS
    bid, bot = over(H('AK76', '643', 'Q53', '742', 9), 1)
    assert bid == Bid(2, 'notrump') and 'invite' in bot.reason
    assert over(H('AK76', '643', 'QJ3', 'Q42', 12), 1)[0] == Bid(3, 'notrump')
    assert over(H('AK76', 'AQ3', 'QJ3', 'Q42', 18), 1)[0] == Bid(6, 'notrump')


def test_a_six_card_major_over_1nt():
    bid, bot = over(H('KQ9765', '43', '532', 'J2', 6, (6, 2, 3, 2)), 1)
    assert bid == Bid(2, 'spades') and 'sign off' in bot.reason
    assert over(H('AKQ976', '43', '532', 'J2', 10), 1)[0] == Bid(4, 'spades')
    assert over(H('43', 'KQ9764', '532', 'J2', 6), 1)[0] == Bid(2, 'hearts')


def test_responses_to_2nt():
    assert over(H('K976', '643', '853', '742', 3), 2)[0] == PASS
    assert over(H('KQ76', '643', '853', '742', 5), 2)[0] == Bid(3, 'notrump')
    assert over(H('AKJ6', 'Q43', 'J53', 'Q42', 13), 2)[0] == Bid(6, 'notrump')


# ---------------------------------------------------------------------------------------------- the opener decides
def rebid(hand, opening, response):
    return call(hand, 'north', [('north', opening), ('east', PASS), ('south', response), ('west', PASS)])


def test_opener_over_responses_to_1nt():
    one_nt = Bid(1, 'notrump')
    bid, bot = rebid(BAL16, one_nt, Bid(2, 'notrump'))
    assert bid == Bid(3, 'notrump') and 'accepts' in bot.reason
    bid, bot = rebid(H('AK52', 'QJ4', 'K83', 'Q52', 15), one_nt, Bid(2, 'notrump'))
    assert bid == PASS and 'declines' in bot.reason
    assert rebid(BAL16, one_nt, Bid(3, 'notrump'))[0] == PASS  # partner chose the contract
    assert rebid(BAL16, Bid(2, 'notrump'), Bid(3, 'notrump'))[0] == PASS


def test_opener_over_a_raise_of_the_suit():
    hearts = Bid(1, 'hearts')
    two = Bid(2, 'hearts')
    assert rebid(H('AK4', 'AKQ952', '4', '542', 16, (3, 6, 1, 3)), hearts, two)[0] == Bid(3, 'hearts')   # 16 + 7.5
    assert rebid(H('AK4', 'AKQJ52', '4', 'A42', 21), hearts, two)[0] == Bid(4, 'hearts')                   # 28.5
    bid, bot = rebid(H('K4', 'AQ9752', '85', 'Q32', 11), hearts, two)                                     # 18.5
    assert bid == PASS and 'already there' in bot.reason


def test_opener_over_a_game_raise_passes_or_goes_to_slam():
    hearts, game = Bid(1, 'hearts'), Bid(4, 'hearts')
    assert rebid(H('K4', 'AQ9752', '85', 'Q32', 11), hearts, game)[0] == PASS           # 25.5: three hearts would do
    bid, bot = rebid(H('AK4', 'AKQ952', '4', 'A42', 20), hearts, game)                  # 34.5: slam
    assert bid == Bid(6, 'hearts')


def test_opener_over_a_forcing_new_suit_must_bid():
    hearts, one_spade = Bid(1, 'hearts'), Bid(1, 'spades')
    # four spades: support them, game with 27
    assert rebid(H('AK52', 'AQ952', '4', 'K32', 16), hearts, one_spade)[0] == Bid(4, 'spades')
    # a long suit of my own: rebid it at the cheapest level that is high enough
    bid, bot = rebid(H('4', 'AKQ9752', 'K3', 'Q32', 14), hearts, one_spade)
    assert bid == Bid(3, 'hearts')
    # balanced, no fit: notrump
    assert rebid(H('K4', 'AQ952', 'Q83', 'K32', 14, (2, 5, 3, 3)), hearts, one_spade)[0] == Bid(2, 'notrump')
    # too weak for a contract but the bid is forcing: the cheapest rebid of the suit
    assert rebid(H('K4', 'Q9752', '85', 'Q432', 7, (2, 5, 2, 4)), hearts, one_spade)[0] == Bid(2, 'hearts')


def test_opener_over_a_notrump_response_to_a_suit():
    hearts, one_nt = Bid(1, 'hearts'), Bid(1, 'notrump')
    assert rebid(H('K4', 'AQ9752', '85', 'Q32', 11), hearts, one_nt)[0] == PASS          # 18.5 between us
    assert rebid(H('AK4', 'AKQ952', '4', 'K42', 19), hearts, one_nt)[0] == Bid(3, 'notrump')  # 26.5


def test_opener_over_a_raise_of_a_minor():
    bid, _ = rebid(H('AK4', 'KQ4', 'AJ9852', '4', 17, (3, 3, 6, 1)), Bid(1, 'diamonds'), Bid(2, 'diamonds'))
    assert bid == Bid(3, 'diamonds')  # 24.5 between us


# ---------------------------------------------------------------------------------------------- later calls: slam
SLAM_AUCTION = A(('n', 1, 'spades'), ('e', 'p'), ('s', 2, 'clubs'), ('w', 'p'), ('n', 3, 'clubs'), ('e', 'p'))


def test_responder_raises_to_slam_when_the_hands_add_up():
    great = H('K43', 'AK', 'A52', 'KQ876', 19, (3, 2, 3, 5))  # 19 + 16.5 >= 33
    bid, bot = call(great, 'south', SLAM_AUCTION)
    assert bid == Bid(6, 'clubs') and 'slam' in bot.reason
    bid, bot = call(H('K43', '54', 'J52', 'KQ876', 9), 'south', SLAM_AUCTION)
    assert bid == PASS and 'set' in bot.reason
    # a slam has been bid: pass
    bid, bot = call(BAL22, 'north', SLAM_AUCTION[:5] + A(('s', 6, 'clubs'), ('w', 'p')))
    assert bid == PASS and 'set' in bot.reason


def test_the_opener_can_also_raise_to_slam_later():
    auction = A(('n', 1, 'hearts'), ('e', 'p'), ('s', 1, 'spades'), ('w', 'p'), ('n', 2, 'hearts'), ('e', 'p'),
                ('s', 3, 'hearts'), ('w', 'p'))
    bid, bot = call(H('AK4', 'AKQJ52', '4', 'AK2', 24), 'north', auction)  # 24 + 11 (what 1 spade showed)
    assert bid == Bid(6, 'hearts') and 'slam' in bot.reason
    assert call(H('AK4', 'AKQ952', '4', '542', 16), 'north', auction)[0] == PASS


def test_an_opener_whose_partner_did_not_bid():
    bid, bot = call(BAL16, 'north', A(('n', 1, 'notrump'), ('e', 'p'), ('s', 'p'), ('w', 'p')))
    assert bid == PASS and 'did not bid' in bot.reason


# ---------------------------------------------------------------------------------------------- the auction runner
def test_a_whole_auction_by_hand():
    south = H('A976', '643', 'Q53', 'J74', 7)
    result = run_auction([BAL16, WEAK, south, WEAK], 'north')
    assert isinstance(result, AuctionResult)
    assert result.contract == Contract(1, 'notrump', 'north') and not result.passed_out
    assert [(c.seat, str(c.bid)) for c in result.calls] == [('north', '1 notrump'), ('east', 'pass'),
                                                              ('south', 'pass'), ('west', 'pass')]
    assert all(c.reason for c in result.calls) and {c.round for c in result.calls} == {0}


def test_a_longer_auction_and_the_rounds_it_takes():
    north = H('AK4', 'AKQ952', '4', 'A42', 20)
    south = H('9876', 'Q53', 'K5', 'J432', 6)
    result = run_auction([north, WEAK, south, WEAK], 'north')
    # one heart, a raise to two (6-9 points), then 20 + 7.5 between the hands is game
    assert [str(c.bid) for c in result.calls if not c.bid.isPass] == ['1 hearts', '2 hearts', '4 hearts']
    assert result.contract == Contract(4, 'hearts', 'north')
    assert [c.round for c in result.calls][:5] == [0, 0, 0, 0, 1]
    assert result.rounds()[1][0] == Bid(4, 'hearts')


def test_passed_out_when_nobody_opens():
    result = run_auction([WEAK] * 4, 'east')  # the same hand four times: the runner only looks at the points
    assert result.passed_out and result.contract is None and len(result.calls) == 4
    assert [c.seat for c in result.calls] == ['east', 'south', 'west', 'north']
    assert result.rounds() == [[None, PASS, PASS, PASS], [PASS, None, None, None]]


def test_the_rows_of_an_auction():
    result = run_auction([BAL16, WEAK, WEAK, WEAK], 'north')
    assert result.rounds() == [[Bid(1, 'notrump'), PASS, PASS, PASS]]
    result = run_auction([WEAK, BAL16, WEAK, WEAK], 'east')  # east deals and opens
    assert result.rounds()[0][:2] == [None, Bid(1, 'notrump')]


def test_declarer_is_the_first_of_the_side_to_bid_the_strain():
    south = H('K4', 'AQJ752', '85', 'Q32', 12)  # opens one heart
    north = H('9876', 'Q53', 'K5', 'J432', 6)   # raises
    result = run_auction([north, WEAK, south, WEAK], 'south')
    assert [c.seat for c in result.calls[:3]] == ['south', 'west', 'north']
    assert result.contract == Contract(2, 'hearts', 'south')


# ---------------------------------------------------------------------------------------------- over many deals
def test_every_auction_over_many_deals_is_legal_and_finishes():
    contracts = set()
    passed_out = 0
    for seed in range(800):
        hands = list(Deck(shuffle=3, rng=seed).deal())
        result = run_auction(hands, Position.positions[seed % 4])  # raises if a bid is illegal or it never ends
        assert len(result.calls) <= MAX_CALLS
        bids = [c.bid for c in result.calls if not c.bid.isPass]
        assert bids == sorted(bids) and len(set(bids)) == len(bids)  # each bid higher than the last
        if result.contract is None:
            passed_out += 1
            assert not bids and len(result.calls) == 4
            continue
        contract = result.contract
        assert contract.bid == bids[-1] and contract.level <= 7
        opener_side = Position.side(next(c.seat for c in result.calls if not c.bid.isPass))
        assert contract.side == opener_side
        assert all(c.bid.isPass for c in result.calls if Position.side(c.seat) != opener_side)
        assert all(c.bid.isPass for c in result.calls[-3:])  # the auction ends with three passes
        contracts.add((contract.level, contract.strain))
    assert 0 < passed_out < 160  # a few deals in a hundred are passed out
    assert len(contracts) > 15  # a wide spread of contracts is reached


def test_the_defenders_hands_cannot_change_the_bidding_side_calls():
    """the other side only passes, so swapping its two hands changes nothing about how the first side bids"""
    opener = lambda r: next(c.seat for c in r.calls if not c.bid.isPass)
    checked = 0
    for seed in range(80):
        hands = list(Deck(shuffle=3, rng=seed).deal())
        first = run_auction(hands, 'north')
        if first.contract is None:
            continue
        others = [i for i, s in enumerate(Position.positions) if Position.side(s) != first.contract.side]
        swapped = list(hands)
        swapped[others[0]], swapped[others[1]] = hands[others[1]], hands[others[0]]
        again = run_auction(swapped, 'north')
        if again.contract is None or opener(again) != opener(first):
            continue  # the swap gave a defender an opening hand before the opener's turn
        mine = lambda r: [str(c.bid) for c in r.calls if Position.side(c.seat) == first.contract.side]
        assert mine(again) == mine(first)
        checked += 1
    assert checked > 30

import pytest

from ..Contract import Contract
from ..Scoring import ns_score, score, trick_points, undertrick_penalty


def C(level, strain, doubled=0, declarer='south'):
    return Contract(level, strain, declarer, doubled)


def test_contract():
    c = Contract(4, 'spades', 'south')
    assert c.tricks_needed == 10 and c.side == 'ns' and c.dummy == 'north' and c.opening_leader == 'west'
    assert c.bid.value == 4 and c.bid.suit == 'spades' and c.trump == 'spades'
    assert str(c) == '4♠ by south'
    assert str(Contract(3, 'notrump', 'east', 1)) == '3NT' + 'X by east'
    assert str(Contract(6, 'hearts', 'west', 2)) == '6♥XX by west'
    assert Contract(1, 'clubs', 'east').side == 'ew' and Contract(1, 'clubs', 'east').opening_leader == 'south'
    assert Contract(2, 'diamonds', 'north') == Contract(2, 'diamonds', 'north')  # a value type
    with pytest.raises(ValueError):
        Contract(0, 'clubs', 'north')
    with pytest.raises(ValueError):
        Contract(1, 'stars', 'north')
    with pytest.raises(ValueError):
        Contract(1, 'clubs', 'middle')
    with pytest.raises(ValueError):
        Contract(1, 'clubs', 'north', 3)


def test_trick_points():
    assert trick_points('clubs', 3) == 60 and trick_points('hearts', 4) == 120
    assert trick_points('notrump', 1) == 40 and trick_points('notrump', 3) == 100
    assert trick_points('spades', 0) == 0 and trick_points('spades', -2) == 0


# Published duplicate scores.  (non-vulnerable, vulnerable)
@pytest.mark.parametrize('level, strain, tricks, nonvul, vul', [
    (1, 'clubs', 7, 70, 70),            # 20 + 50 part score
    (1, 'notrump', 7, 90, 90),          # 40 + 50
    (2, 'hearts', 8, 110, 110),         # 60 + 50
    (3, 'notrump', 9, 400, 600),        # 100 + game bonus
    (3, 'notrump', 10, 430, 630),       # one overtrick, 30
    (4, 'spades', 10, 420, 620),        # 120 + game bonus
    (4, 'hearts', 11, 450, 650),        # + 30
    (5, 'clubs', 11, 400, 600),         # 100 + game bonus
    (5, 'diamonds', 12, 420, 620),      # overtrick in a minor is 20
    (6, 'spades', 12, 980, 1430),       # 180 + 300 + 500 slam (750 vul), 180 + 500 + 750
    (6, 'notrump', 12, 990, 1440),      # 190 + game + slam
    (7, 'notrump', 13, 1520, 2220),     # 220 + game + 1000 (1500 vul)
    (7, 'hearts', 13, 1510, 2210),      # 210 + game + grand slam
    (1, 'notrump', 9, 150, 150),        # two overtricks: 40 + 60 + 50
    (2, 'spades', 7, -50, -100),        # down one
    (4, 'spades', 8, -100, -200),       # down two
    (3, 'notrump', 0, -450, -900),      # down nine
])
def test_undoubled_scores(level, strain, tricks, nonvul, vul):
    assert score(C(level, strain), tricks, vulnerable=False) == nonvul
    assert score(C(level, strain), tricks, vulnerable=True) == vul


@pytest.mark.parametrize('level, strain, doubled, tricks, nonvul, vul', [
    (2, 'hearts', 1, 8, 470, 670),       # 120 doubled -> game, + 300 (500) + 50 insult
    (4, 'hearts', 1, 10, 590, 790),      # 240 + 300 (500) + 50
    (4, 'hearts', 1, 11, 690, 990),      # one doubled overtrick: 100 (200)
    (1, 'notrump', 1, 7, 180, 180),      # 80 is a part score either way: + 50 + 50 insult
    (2, 'clubs', 2, 8, 560, 760),        # 160 redoubled is game: 160 + 300 (500) + 100 insult
    (4, 'spades', 2, 11, 1080, 1480),    # 480 + 300 (500) + 100 + one overtrick 200 (400)
    (3, 'notrump', 1, 6, -500, -800),    # down three doubled
    (3, 'notrump', 1, 8, -100, -200),    # down one doubled
    (4, 'spades', 1, 7, -500, -800),     # down three
    (4, 'spades', 1, 6, -800, -1100),    # down four: 100+200+200+300, 200+300*3
    (4, 'spades', 2, 8, -600, -1000),    # down two redoubled: (100+200)*2, (200+300)*2
])
def test_doubled_and_redoubled_scores(level, strain, doubled, tricks, nonvul, vul):
    assert score(C(level, strain, doubled), tricks, False) == nonvul
    assert score(C(level, strain, doubled), tricks, True) == vul


def test_undertrick_penalties_directly():
    assert [undertrick_penalty(d, False, 0) for d in (1, 2, 3)] == [50, 100, 150]
    assert [undertrick_penalty(d, True, 0) for d in (1, 2, 3)] == [100, 200, 300]
    assert [undertrick_penalty(d, False, 1) for d in (1, 2, 3, 4, 5)] == [100, 300, 500, 800, 1100]
    assert [undertrick_penalty(d, True, 1) for d in (1, 2, 3, 4)] == [200, 500, 800, 1100]
    assert undertrick_penalty(3, False, 2) == 1000


def test_the_game_bonus_starts_at_100_contract_points():
    assert score(C(4, 'clubs'), 10) == 80 + 50  # 80 contract points is a part score
    assert score(C(5, 'clubs'), 11) == 100 + 300
    assert score(C(2, 'spades'), 8) == 60 + 50
    assert score(C(3, 'spades'), 9) == 90 + 50  # 90 points is still a part score
    assert score(C(2, 'notrump'), 8) == 70 + 50
    assert score(C(3, 'diamonds'), 9) == 60 + 50


def test_ns_score_changes_sign_for_east_west():
    assert ns_score(C(4, 'spades', declarer='south'), 10) == 420
    assert ns_score(C(4, 'spades', declarer='east'), 10) == -420
    assert ns_score(C(4, 'spades', declarer='west'), 8) == 100


def test_score_errors():
    with pytest.raises(ValueError):
        score(C(1, 'clubs'), 14)
    with pytest.raises(ValueError):
        score(C(1, 'clubs'), -1)
    with pytest.raises(TypeError):
        score('3NT', 9)

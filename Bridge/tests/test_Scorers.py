from ..Card import Card
from ..Deck import Deck
from ..Hand import Hand
from ..Scorers import SimpleHighCardValue


def test_scores():
    d = Deck()
    assert [10, 10, 10, 10] == SimpleHighCardValue.getScores(d)


def test_scores_from_hands():
    """hands can be scored without a deck"""
    hands = Deck().deal()
    assert SimpleHighCardValue(hands=hands).scores == [10, 10, 10, 10]


def test_scores_shuffled_deck_total_forty():
    """every deal hands out 4+3+2+1 points in each of the 4 suits"""
    for seed in range(20):
        assert sum(SimpleHighCardValue.getScores(Deck(shuffle=2, rng=seed))) == 40


def test_cardScorer():
    assert [SimpleHighCardValue.cardScorer(Card.fromCode(c)) for c in ('As', 'Kh', 'Qd', 'Jc', '0s', '2s')] \
        == [4, 3, 2, 1, 0, 0]


def test_scores_single_hand():
    h = Hand([Card.fromCode(c) for c in 'As Ks Qs Js 0s 9s 8s 7s 6s 5s 4s 3s 2s'.split()])
    assert SimpleHighCardValue(hands=[h]).scores == [10]

from ..Scorers import SimpleHighCardValue
from ..Deck import Deck


def test_scores():
    d = Deck()
    assert [10, 10, 10, 10] == SimpleHighCardValue.getScores(d)

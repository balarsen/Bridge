from .Card import Card


class SimpleHighCardValue:
    """
    Score hands by simple high card logic

    j=1
    q=2
    k=3
    a=4
    no length or any other bonus
    """

    def __init__(self, deck=None, hands=None):
        """
        if deck is set it is dealt then scored, if hands is a 4 element list-like they are just scored
        """
        scores = []
        if deck is not None:
            hands = deck.deal()
        for h in hands:
            vals = [SimpleHighCardValue.cardScorer(c) for c in h]
            scores.append(sum(vals))
        self.scores = scores

    @staticmethod
    def cardScorer(card):
        scores = {'J': 1,
                  'Q': 2,
                  'K': 3,
                  'A': 4}
        return scores.get(str(card.value), 0)

    @staticmethod
    def getScores(inval):
        return SimpleHighCardValue(inval).scores

class Suit(object):
    suits = ('spades', 'hearts', 'diamonds', 'clubs')
    suits_set = set(suits)

    def __init__(self, suit):
        if suit not in Suit.suits_set:
            raise(ValueError(f'Bad suit {Suit.suits}'))
        self.suit = suit

    def __eq__(self, other):
        if self.suit == other.suit:
            return True
        else:
            return False

    def __ne__(self, other):
        return ~(self == other)

    def __str__(self):
        return f"{self.suit}"

    def __repr__(self):
        return f"<{self.suit}>"

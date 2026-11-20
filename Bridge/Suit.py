class Suit(object):
    """
    A suit.  There is exactly one `Suit` object per suit (`Suit('spades') is Suit('spades')`), it is immutable,
    equal to its name, and `index` is its position in `Suit.suits`, the order spades, hearts, diamonds, clubs.
    """
    suits = ('spades', 'hearts', 'diamonds', 'clubs')
    suits_set = set(suits)
    indices = {s: i for i, s in enumerate(suits)}  # suit name or Suit -> index, for fast lookups
    _instances = {}

    def __new__(cls, suit):
        if isinstance(suit, Suit):
            return suit
        instance = cls._instances.get(suit)
        if instance is None:
            if suit not in Suit.suits_set:
                raise(ValueError(f'Bad suit {Suit.suits}'))
            instance = object.__new__(cls)
            object.__setattr__(instance, 'suit', suit)
            object.__setattr__(instance, 'index', Suit.indices[suit])
            cls._instances[suit] = instance
        return instance

    def __setattr__(self, name, value):
        raise AttributeError('a Suit is immutable')

    def __delattr__(self, name):
        raise AttributeError('a Suit is immutable')

    def __reduce__(self):
        return (Suit, (self.suit,))  # copying and pickling give back the one instance

    def __eq__(self, other):
        if other is self:
            return True
        if isinstance(other, Suit):
            return self.suit == other.suit
        else:  # assume it is a string
            return self.suit == other

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.suit)

    def __str__(self):
        return f"{self.suit}"

    def __repr__(self):
        return f"<{self.suit}>"

    @staticmethod
    def letterToSuit(letter):
        mapping = {'s':'spades',
                   'h':'hearts',
                   'd':'diamonds',
                   'c':'clubs'}
        ans = [mapping[v] for v in letter]
        if len(letter) == 1:
            return ans[0]
        else:
            return ans


for _suit in Suit.suits:  # create the four instances up front
    Suit(_suit)

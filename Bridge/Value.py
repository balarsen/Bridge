class Value(object):
    values = ('2', '3', '4', '5', '6', '7', '8', '9', '0', 'J', 'Q', 'K', 'A')  # 0 is 10
    values_set = set(values)

    def __init__(self, value):
        if value not in Value.values_set:
            raise (ValueError(f'Bad value, {value}, {Value.values}'))
        self.value = value

    @property
    def rank(self):
        """0 for a deuce up to 12 for an ace"""
        return Value.values.index(self.value)

    def __eq__(self, other):
        if not isinstance(other, Value):
            return NotImplemented
        return self.value == other.value

    def __ne__(self, other):
        if not isinstance(other, Value):
            return NotImplemented
        return self.value != other.value

    def __hash__(self):
        return hash(self.value)

    def __gt__(self, other):
        return self.rank > other.rank

    def __lt__(self, other):
        return self.rank < other.rank

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return f"<{self.value}>"

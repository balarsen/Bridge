class Value(object):
    values = (2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A')
    values_set = set(values)

    def __init__(self, value):
        if value not in Value.values_set:
            raise (ValueError(f'Bad value {Value.values}'))
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __gt__(self, other):
        return self.values.index(self.value) > self.values.index(other.value)

    def __lt__(self, other):
        return self.values.index(self.value) < self.values.index(other.value)

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return f"<{self.value}>"

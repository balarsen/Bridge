class Value(object):
    """
    A card value.  There is exactly one `Value` object per value (`Value('A') is Value('A')`), it is immutable,
    and `rank` is its position in `Value.values`, 0 for a deuce up to 12 for the ace.
    """
    values = ('2', '3', '4', '5', '6', '7', '8', '9', '0', 'J', 'Q', 'K', 'A')  # 0 is 10
    values_set = set(values)
    ranks = {v: i for i, v in enumerate(values)}
    _instances = {}

    def __new__(cls, value):
        if isinstance(value, Value):
            return value
        instance = cls._instances.get(value)
        if instance is None:
            if value not in Value.values_set:
                raise (ValueError(f'Bad value, {value}, {Value.values}'))
            instance = object.__new__(cls)
            object.__setattr__(instance, 'value', value)
            object.__setattr__(instance, 'rank', Value.ranks[value])
            cls._instances[value] = instance
        return instance

    def __setattr__(self, name, value):
        raise AttributeError('a Value is immutable')

    def __delattr__(self, name):
        raise AttributeError('a Value is immutable')

    def __reduce__(self):
        return (Value, (self.value,))  # copying and pickling give back the one instance

    def __eq__(self, other):
        if other is self:
            return True
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


for _value in Value.values:  # create the thirteen instances up front
    Value(_value)

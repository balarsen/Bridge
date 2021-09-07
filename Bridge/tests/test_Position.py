import pytest

from ..Position import Position


def test_init():
    with pytest.raises(ValueError):
        Position('bad')
    Position('north')

def test_eq():
    p1 = Position('north')
    p2 = Position('north')
    assert p1==p2

def test_ne():
    p1 = Position('north')
    p2 = Position('south')
    assert p1 != p2

def test_str():
    assert str(Position('north')) == 'north'

def test_repr():
    assert repr(Position('north')) == '<north>'

def test_cycle():
    # can start anywhere, may need a few
    ans = ('north', 'east', 'south', 'west', 'north', 'east', 'south', 'west')
    for a, c in zip(ans, Position.cycle('north')):
        assert a == c
    ans = ('south', 'west', 'north', 'east', 'south', 'west', 'north', 'east')
    for a, c in zip(ans, Position.cycle('south')):
        assert a == c



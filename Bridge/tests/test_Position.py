import pytest

from ..Position import Position


def test_init():
    with pytest.raises(ValueError):
        Position('bad')
    with pytest.raises(ValueError):
        Position('North')  # lower case only
    Position('north')
    assert Position(Position('north')) == Position('north')


def test_eq():
    p1 = Position('north')
    p2 = Position('north')
    assert p1 == p2
    assert p1 == 'north'
    assert not p1 == 'south'


def test_ne():
    p1 = Position('north')
    p2 = Position('south')
    assert p1 != p2
    assert p1 != 'south'
    assert not (p1 != Position('north'))
    assert not (p1 != 'north')


def test_hash():
    assert len({Position('north'), Position('north'), Position('south')}) == 2
    assert {Position('north'): 1}['north'] == 1


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
    with pytest.raises(ValueError):
        Position.cycle('bad')


def test_pos2index():
    assert Position.pos2index('north', 'north') == 0
    assert Position.pos2index('north', 'east') == 1
    assert Position.pos2index('north', 'south') == 2
    assert Position.pos2index('north', 'west') == 3
    assert Position.pos2index('south', 'north') == 2
    assert Position.pos2index('west', 'north') == 1


def test_index2pos():
    assert Position.index2pos('north', 1) == 'east'
    assert Position.index2pos('west', 1) == 'north'
    assert Position.index2pos('south', 3) == 'east'
    # they are the inverse of each other
    for leader in Position.positions:
        for pos in Position.positions:
            assert Position.index2pos(leader, Position.pos2index(leader, pos)) == pos


def test_side():
    assert Position.side('north') == Position.side('south') == 'ns'
    assert Position.side('east') == Position.side('west') == 'ew'

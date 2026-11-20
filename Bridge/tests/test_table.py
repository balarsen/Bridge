import pytest

from ..Position import Position
from ..Table import Seat, Table


def test_seat():
    with pytest.raises(ValueError):
        Seat('badval')
    assert Seat('north').position == 'north'
    assert Seat('north').position == Position('north')
    assert Seat('north').score == 0


def test_Table():
    t = Table()
    assert t.north.position == Position('north')
    assert t.east.position == 'east'
    assert t.south.position == 'south'
    assert t.west.position == 'west'
    assert t.north.score == 0

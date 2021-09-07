import pytest

from ..Value import Value


def test_ValueError():
    with pytest.raises(ValueError):
        Value('bad')


def test_eq():
    a = Value(2)
    b = Value(2)
    assert a == b


def test_ne():
    a = Value(2)
    b = Value(3)
    assert a != b


def test_gt():
    a = Value(2)
    b = Value(3)
    assert b > a
    b = Value('Q')
    assert b > a


def test_lt():
    a = Value(2)
    b = Value(3)
    assert a < b


def test_str():
    assert str(Value('Q')) == 'Q'


def test_repr():
    assert repr(Value('Q')) == '<Q>'

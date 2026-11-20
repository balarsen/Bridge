"""
Suit, Value and Card are interned or shared and immutable, and Hand keeps a per-suit cache.  These tests
pin down the behaviour that has to stay the same as before (equality, ordering, list behaviour) while
the representation underneath is cheap.
"""
import copy
import pickle

import pytest

from ..Card import ALL_CARDS, Card
from ..Deck import Deck
from ..Hand import Hand
from ..Position import Position
from ..Suit import Suit
from ..Trick import Trick, beats
from ..Value import Value


def make_hand(codes):
    return Hand([Card.fromCode(c) for c in codes.split()])


def reference_suit(hand, suit):
    """what get_suit used to compute on every call: filter and sort the 13 cards"""
    return sorted([c for c in hand if c.suit == suit], reverse=True)


HAND = 'As Ks 5s 2s Qh Jh 4h Kd 6d 3d 7c 5c Jc'


# ---------------------------------------------------------------------------------------------- Suit, Value
def test_suits_and_values_are_interned():
    assert Suit('spades') is Suit('spades')
    assert Value('A') is Value('A')
    assert Suit(Suit('hearts')) is Suit('hearts')
    assert Value(Value('K')) is Value('K')
    assert [Suit(s).index for s in Suit.suits] == [0, 1, 2, 3]
    assert [Value(v).rank for v in Value.values] == list(range(13))
    assert Suit.indices == {'spades': 0, 'hearts': 1, 'diamonds': 2, 'clubs': 3}
    assert Value.ranks['A'] == 12


def test_suit_and_value_lookups_work_with_names_and_objects():
    """a Suit hashes and compares like its name, so it finds the same dictionary entry"""
    assert Suit.indices[Suit('clubs')] == 3
    assert Suit.indices.get(Suit('clubs')) == Suit.indices.get('clubs')
    assert Suit('clubs') == 'clubs' and 'clubs' == Suit('clubs')


def test_suit_and_value_are_immutable():
    for obj, attr in ((Suit('spades'), 'suit'), (Value('A'), 'value'), (Suit('spades'), 'index'), (Value('A'), 'rank')):
        with pytest.raises(AttributeError):
            setattr(obj, attr, 'x')
        with pytest.raises(AttributeError):
            delattr(obj, attr)
    assert Suit('spades').suit == 'spades' and Value('A').rank == 12


def test_copy_and_pickle_give_back_the_one_instance():
    for obj in (Suit('hearts'), Value('Q')):
        assert copy.copy(obj) is obj
        assert copy.deepcopy(obj) is obj
        assert pickle.loads(pickle.dumps(obj)) is obj


def test_value_comparisons_with_other_types():
    assert Value('2').__eq__('2') is NotImplemented
    assert Value('2').__ne__('2') is NotImplemented
    assert Value('2') == Value('2') and not Value('2') != Value('2')
    assert Value('2') != Value('3') and not Value('2') == Value('3')


# ---------------------------------------------------------------------------------------------- Card
def test_card_has_precomputed_ints():
    c = Card('K', 'hearts')
    assert (c.suit_index, c.rank, c.code) == (1, 11, 1 * 13 + 11)
    assert hash(c) == c.code
    assert [c.code for c in ALL_CARDS] == list(range(52))


def test_card_is_immutable():
    c = Card('K', 'hearts')
    for attr in ('value', 'suit', 'suit_index', 'rank', 'code', 'trump'):
        with pytest.raises(AttributeError):
            setattr(c, attr, 1)
    with pytest.raises(AttributeError):
        del c.value
    assert c == Card('K', 'hearts')


def test_copy_and_pickle_keep_cards_equal_and_values_shared():
    c = Card('K', 'hearts')
    for other in (copy.copy(c), copy.deepcopy(c), pickle.loads(pickle.dumps(c))):
        assert other == c and hash(other) == hash(c)
        assert other.value is c.value and other.suit is c.suit


def test_the_52_cards_are_shared():
    assert len(ALL_CARDS) == len(set(ALL_CARDS)) == 52
    assert Deck()[0] is ALL_CARDS[0] and Deck()[51] is ALL_CARDS[51]
    assert Deck()[7] is Deck()[7]
    assert Card.fromCode('As') is Card.fromCode('As')
    assert Card.fromCode('As') is ALL_CARDS[12]
    assert Deck.fromCode(Deck().toCode())[20] is ALL_CARDS[20]
    # an equal card made by hand is a different object but equal in every way
    assert Card('A', 'spades') is not Card.fromCode('As') and Card('A', 'spades') == Card.fromCode('As')


def test_fromCode_for_codes_that_are_not_one_of_the_52():
    assert Card.fromCode('As ') == Card('A', 'spades')  # extra characters were always ignored
    assert Card.fromCode('As ') is not Card.fromCode('As')
    with pytest.raises(ValueError):
        Card.fromCode('1s')
    with pytest.raises(KeyError):
        Card.fromCode('Ax')


def test_card_equality_with_subclasses_and_other_types():
    class Sub(Card):
        pass

    class Other(Card):
        pass

    assert Sub('A', 'spades') == Card('A', 'spades') and Card('A', 'spades') == Sub('A', 'spades')
    assert not Sub('A', 'spades') != Card('A', 'spades')
    assert Sub('A', 'spades') != Card('K', 'spades')
    # two different subclasses, neither is exactly Card
    assert Sub('A', 'spades') == Other('A', 'spades')
    assert not Sub('A', 'spades') != Other('A', 'spades')
    assert Sub('A', 'spades') != Other('K', 'spades')
    assert Card('A', 'spades').__eq__(12) is NotImplemented
    assert Card('A', 'spades').__ne__(12) is NotImplemented


# ---------------------------------------------------------------------------------------------- Hand cache
def test_get_suit_takes_names_and_suit_objects_and_returns_a_new_list():
    h = make_hand(HAND)
    assert h.get_suit('spades') == h.get_suit(Suit('spades')) == reference_suit(h, 'spades')
    got = h.get_suit('hearts')
    got.clear()  # changing the answer must not change the hand
    assert h.get_suit('hearts') == reference_suit(h, 'hearts') != []
    assert h.get_suit('stars') == []
    assert h.get_suit(None) == []


def test_every_suit_matches_the_old_filter_and_sort():
    for i in range(20):
        h = Hand(list(Deck(shuffle=3, rng=i).deal()[0]))
        for suit in Suit.suits:
            assert h.get_suit(suit) == reference_suit(h, suit)
        assert h.distro() == tuple((s, len(reference_suit(h, s))) for s in Suit.suits)


def test_remove_keeps_the_cache_right_and_matches_list_remove():
    h = make_hand(HAND)
    h.get_suit('spades')  # build the cache
    h.remove(Card.fromCode('Ks'))
    h.remove(Card('J', 'clubs'))  # an equal card that is not the same object
    for suit in Suit.suits:
        assert h.get_suit(suit) == reference_suit(h, suit)
    assert len(h) == 11 and Card.fromCode('Ks') not in h
    assert h.distro() == (('spades', 3), ('hearts', 3), ('diamonds', 3), ('clubs', 2))
    # without a cache built yet
    h2 = make_hand(HAND)
    h2.remove(Card.fromCode('As'))
    assert h2.get_suit('spades') == reference_suit(h2, 'spades')


def test_remove_errors():
    h = make_hand(HAND)
    with pytest.raises(ValueError):
        h.remove(Card.fromCode('2h'))  # a card that is not in the hand
    with pytest.raises(ValueError):
        h.remove('As')  # not a card at all
    with pytest.raises(ValueError):
        h.get_suit('spades') and h.remove(Card.fromCode('9d'))
    assert len(h) == 13  # nothing was removed


def test_remove_takes_the_first_equal_card_like_list_remove():
    h = make_hand(HAND)
    h.append(Card.fromCode('As'))  # a duplicate, 14 cards
    h.get_suit('spades')
    h.remove(Card.fromCode('As'))
    assert h.get_suit('spades') == reference_suit(h, 'spades')
    assert sum(c == Card.fromCode('As') for c in h) == 1


@pytest.mark.parametrize('mutate', [
    lambda h: h.append(Card.fromCode('2c')),
    lambda h: h.extend([Card.fromCode('2c'), Card.fromCode('3c')]),
    lambda h: h.insert(0, Card.fromCode('2c')),
    lambda h: h.pop(),
    lambda h: h.pop(0),
    lambda h: h.__delitem__(0),
    lambda h: h.__delitem__(slice(0, 3)),
    lambda h: h.__setitem__(0, Card.fromCode('2c')),
    lambda h: h.__setitem__(slice(0, 2), [Card.fromCode('2c')]),
    lambda h: h.__iadd__([Card.fromCode('2c')]),
    lambda h: h.__imul__(2),
    lambda h: h.clear(),
], ids=['append', 'extend', 'insert', 'pop', 'pop0', 'delitem', 'delslice', 'setitem', 'setslice', 'iadd', 'imul', 'clear'])
def test_any_change_to_the_list_is_seen_by_get_suit(mutate):
    h = make_hand(HAND)
    h.get_suit('spades')  # build the cache first
    mutate(h)
    for suit in Suit.suits:
        assert h.get_suit(suit) == reference_suit(h, suit)
    assert h.distro() == tuple((s, len(reference_suit(h, s))) for s in Suit.suits)


def test_list_operators_still_work_on_a_hand():
    h = make_hand(HAND)
    h += [Card.fromCode('2c')]
    assert len(h) == 14 and h.get_suit('clubs')[-1] == Card.fromCode('2c')
    assert h.pop() == Card.fromCode('2c')
    h.sort(key=lambda c: c.code)
    h.reverse()  # reordering does not change which cards are in the hand
    assert [h.get_suit(s) for s in Suit.suits] == [reference_suit(h, s) for s in Suit.suits]
    assert isinstance(h, list) and h[0] in h and h.index(h[3]) == 3


def test_copies_of_a_hand_have_their_own_cache():
    h = make_hand(HAND)
    h.get_suit('spades')
    for other in (copy.copy(h), copy.deepcopy(h), pickle.loads(pickle.dumps(h))):
        assert list(other) == list(h)
        other.remove(Card.fromCode('As'))
        assert other.get_suit('spades') == reference_suit(other, 'spades')
        assert h.get_suit('spades') == reference_suit(h, 'spades') and len(h) == 13


def test_highCard_and_lowCard_of_an_empty_suit_still_raise():
    h = make_hand('As Ks Qs Js 0s 9s 8s 7s 6s 5s 4s 3s 2s')
    assert h.highCard('spades') == Card.fromCode('As') and h.lowCard('spades') == Card.fromCode('2s')
    with pytest.raises(ValueError):
        h.highCard('hearts')
    with pytest.raises(ValueError):
        h.lowCard('hearts')


# ---------------------------------------------------------------------------------------------- Position, Trick
def test_position_name_and_lookups():
    assert Position.name('east') == 'east' and Position.name(Position('west')) == 'west'
    assert type(Position.name(Position('west'))) is str
    for bad in ('North', 'bad', '', None):
        with pytest.raises(ValueError):
            Position.name(bad)
        with pytest.raises(ValueError):
            Position.pos2index('north', bad)
        with pytest.raises(ValueError):
            Position.cycle(bad)
    assert Position.pos2index(Position('south'), Position('north')) == 2
    assert Position.index2pos(Position('west'), 1) == 'north'


def test_trick_trump_can_be_changed_and_is_used():
    t = Trick('north', 'hearts')
    for c in ('3d', '5h', '7d', '9d'):
        t.nextCard(Card.fromCode(c))
    assert t.winner()[1] == 'east'  # the 5 of hearts is trump
    t.trump = None
    assert t.trump is None and t.winner()[1] == 'west'  # no trump: the 9 of diamonds, played by west
    t.trump = 'diamonds'
    assert t.trump == 'diamonds' and t.winner()[1] == 'west'
    t.trump = Suit('hearts')
    assert t.winner()[1] == 'east'
    assert Trick(Position('south')).leader == 'south'


def test_beats_takes_trump_as_a_name_a_suit_or_nothing():
    two_s, ace_d = Card.fromCode('2s'), Card.fromCode('Ad')
    assert beats(two_s, ace_d, 'spades') and beats(two_s, ace_d, Suit('spades'))
    assert not beats(two_s, ace_d) and not beats(two_s, ace_d, 'notrump') and not beats(two_s, ace_d, 'hearts')


def test_a_trick_refuses_the_same_card_twice_even_if_it_is_another_object():
    t = Trick()
    t.nextCard(Card.fromCode('5h'))
    with pytest.raises(ValueError):
        t.nextCard(Card('5', 'hearts'))

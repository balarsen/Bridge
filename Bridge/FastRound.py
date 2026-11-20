"""
Integer-card engine: play many rounds of `simpleHigh` against `simpleHigh` quickly.

`Round` with `Deck`/`Hand`/`Card` objects is the readable reference and takes strategies as plugins,
but most of its time goes to Python object overhead (method calls for every suit comparison, a sort
on every `get_suit`, validation of seats).  This module plays the same game with plain integers and no
objects, about 14 times faster, for the one strategy it implements: all four seats play `simpleHigh`.
`tests/test_FastRound.py` checks it against `Round` on hundreds of decks, trumps and leaders.

A card is the integer `suit * 13 + rank`, `suit` indexing `Suit.suits` (spades, hearts, diamonds,
clubs) and `rank` being `Value.rank` (0 for a deuce up to 12 for the ace), which is the order of an
unshuffled `Deck()`.  A deck is a list of 52 such integers in deal order, so deck position `i` goes to
the seat `i % 4` (north, east, south, west), as `Deck.deal`.  The rules played are those of
`simpleHigh`: lead the highest card (ties to the higher ranking suit); follow suit with the highest
card if it wins the trick so far, else the lowest; when void play the lowest trump (unless trump was
led), else discard the lowest card (ties to the card dealt first).
"""
import numpy as np

from .Position import Position
from .Suit import Suit

_SUIT_INDEX = {s: i for i, s in enumerate(Suit.suits)}
_SEAT_INDEX = {p: i for i, p in enumerate(Position.positions)}


def _trump_index(trump):
    """suit index of the trump, -1 for no trump"""
    if trump is None or str(trump) == 'notrump':
        return -1
    try:
        return _SUIT_INDEX[str(trump)]
    except KeyError:
        raise ValueError(f'bad trump {trump!r}, must be one of {Suit.suits}, "notrump" or None') from None


def _seat_index(seat):
    try:
        return _SEAT_INDEX[str(seat)]
    except KeyError:
        raise ValueError(f'bad seat {seat!r}, must be one of {Position.positions}') from None


def deck_to_ints(deck):
    """the integer form of a `Deck` of `Card` objects, in deal order"""
    return [Suit.suits.index(str(c.suit)) * 13 + c.value.rank for c in deck]


def shuffled_deck(rng):
    """a uniformly shuffled deck of 52 integers, `rng` is a numpy Generator"""
    return rng.permutation(52).tolist()


def _play(deck, trump, leader):
    """play 13 tricks, returns (north-south tricks, east-west tricks)"""
    hands = [[[], [], [], []] for _ in range(4)]  # seat -> suit -> ranks, highest first
    for i, card in enumerate(deck):
        hands[i & 3][card // 13].append(card % 13)
    for hand in hands:
        for suit in hand:
            suit.sort(reverse=True)
    ns = 0
    for _ in range(13):
        hand = hands[leader]
        lead_suit, lead_rank = -1, -1
        for s in range(4):
            if hand[s] and hand[s][0] > lead_rank:
                lead_suit, lead_rank = s, hand[s][0]
        hand[lead_suit].pop(0)
        win_seat, win_suit, win_rank = leader, lead_suit, lead_rank
        seat = leader
        for _ in range(3):
            seat = (seat + 1) & 3
            hand = hands[seat]
            cards = hand[lead_suit]
            if cards:
                suit = lead_suit
                if win_suit == lead_suit and cards[0] > win_rank:
                    rank = cards.pop(0)  # win the trick with the highest card
                else:
                    rank = cards.pop()  # or play the lowest
            elif trump >= 0 and lead_suit != trump and hand[trump]:
                suit, rank = trump, hand[trump].pop()  # void: the lowest trump
            else:  # void and no trump to play: discard the lowest card, ties to the one dealt first
                best = None
                for s in range(4):
                    if hand[s]:
                        r = hand[s][-1]
                        key = (r, deck.index(s * 13 + r))
                        if best is None or key < best[0]:
                            best = (key, s)
                suit = best[1]
                rank = hand[suit].pop()
            if suit == win_suit:
                if rank > win_rank:
                    win_seat, win_rank = seat, rank
            elif suit == trump:
                win_seat, win_suit, win_rank = seat, suit, rank
        leader = win_seat
        ns += (win_seat & 1) == 0
    return ns, 13 - ns


def play_deck(deck, trump='spades', leader='north'):
    """
    Play a deck (52 integers in deal order) with `simpleHigh` at every seat and return the tricks won as
    (north-south, east-west).  `trump` is a suit name, "notrump" or None, `leader` the seat that leads
    the first trick.
    """
    deck = list(deck)
    if len(deck) != 52:
        raise ValueError('a deck has 52 cards')
    return _play(deck, _trump_index(trump), _seat_index(leader))


def play_round(rng, trump='spades', leader='north'):
    """deal a fresh uniformly shuffled deck from `rng` and play it, see `play_deck`"""
    return _play(shuffled_deck(rng), _trump_index(trump), _seat_index(leader))


def simulate(rng, n, trump='spades', leader='rotate'):
    """
    Play n rounds, each with a fresh deck from `rng`.  `leader` is a seat name, or "rotate" to let north,
    east, south, west lead in turn (which makes both sides equally likely to win a round).  Returns an
    int array of shape (n, 2) with the tricks won by (north-south, east-west) in each round.

    This has the signature `Harness.run_batches` expects of a task, so
    `run_batches(simulate, n, seed, trump=...)` plays the rounds on all cores.
    """
    t = _trump_index(trump)
    rotate = leader == 'rotate'
    first = 0 if rotate else _seat_index(leader)
    out = np.empty((n, 2), dtype=np.int8)
    for i in range(n):
        out[i] = _play(shuffled_deck(rng), t, (i & 3) if rotate else first)
    return out

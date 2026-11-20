"""
Card counting: what one player knows about the cards, and exact probabilities from it.

A player sees their own hand, every card as it is played, and any hand that is on the table (the dummy).
From that a player knows which cards are *unseen* (so held by the hidden players), how many cards each
hidden player still holds, and who has shown out of which suit.

When two players are hidden (a declarer or a defender once the dummy is down, or any player late in the
play), the chance that a given unseen card is in a given hand is exact and needs no sampling: every way of
dealing the unseen cards to the two hands, respecting how many cards each holds and the suits each has
shown out of, is equally likely.  Cards in a suit that one hand is out of must be in the other hand; the
rest are interchangeable, so a hand with `n` cards of which `f` are already forced has `n - f` *vacant
places* to share between the `F` free cards, and each free card is there with probability `(n - f) / F`.
"""
from .Card import ALL_CARDS
from .Position import Position
from .Suit import Suit


class Knowledge(object):
    """
    What `seat` knows, given their own `hand` (a `Hand`).  Feed it every card played with `observe` and
    every hand that is put on the table with `reveal`.
    """
    def __init__(self, seat, hand):
        self.seat = Position.name(seat)
        self.hand = hand
        self.revealed = {}  # seat -> Hand, the hands on the table (their cards left are known)
        self.played = {p: [] for p in Position.positions}  # cards each seat has played, in order
        self.voids = {p: set() for p in Position.positions}  # suit indices each seat has shown out of

    # ---------------------------------------------------------------------------------- what is fed in
    def reveal(self, seat, hand):
        """`hand` is on the table: its cards are known (the dummy)"""
        self.revealed[Position.name(seat)] = hand

    def observe(self, seat, card, lead_suit=None):
        """
        `seat` played `card`.  `lead_suit` is the suit that was led, or None if this card is the lead; playing
        another suit shows that `seat` is out of the suit that was led.
        """
        seat = Position.name(seat)
        self.played[seat].append(card)
        if lead_suit is not None:
            lead_index = lead_suit.index if type(lead_suit) is Suit else Suit.indices[lead_suit]
            if card.suit_index != lead_index:
                self.voids[seat].add(lead_index)

    # ---------------------------------------------------------------------------------- what is known
    def _known_codes(self):
        codes = {c.code for c in self.hand.original}
        for hand in self.revealed.values():
            codes.update(c.code for c in hand.original)
        for cards in self.played.values():
            codes.update(c.code for c in cards)
        return codes

    def unseen(self, suit=None):
        """
        the cards whose place is not known (held by the hidden players), highest first within a suit;
        only one suit if `suit` is given
        """
        known = self._known_codes()
        cards = [c for c in ALL_CARDS if c.code not in known]
        if suit is not None:
            index = suit.index if type(suit) is Suit else Suit.indices[suit]
            cards = [c for c in cards if c.suit_index == index]
        cards.sort(key=lambda c: (c.suit_index, -c.rank))
        return cards

    def cards_left(self, seat):
        """how many cards `seat` still holds"""
        return 13 - len(self.played[Position.name(seat)])

    def is_void(self, seat, suit):
        """has `seat` shown out of `suit`"""
        index = suit.index if type(suit) is Suit else Suit.indices[suit]
        return index in self.voids[Position.name(seat)]

    def hidden_seats(self):
        """the seats whose hands are not known to this player"""
        return [p for p in Position.positions if p != self.seat and p not in self.revealed]

    def outstanding(self, suit):
        """
        the cards of `suit` that could beat or be beaten by this player's side from the other side: the
        unseen cards, and the cards left in a hand on the table that belongs to the opponents (a dummy seen
        from the defence).  Highest first.
        """
        index = suit.index if type(suit) is Suit else Suit.indices[suit]
        cards = self.unseen(suit)
        for seat, hand in self.revealed.items():
            if Position.side(seat) != Position.side(self.seat):
                cards.extend(c for c in hand if c.suit_index == index)
        cards.sort(key=lambda c: -c.rank)
        return cards

    def is_master(self, card):
        """is `card` higher than every card of its suit that the opponents could still hold"""
        return all(c.rank < card.rank for c in self.outstanding(card.suit))

    def highest_unseen(self, suit):
        """the highest unseen card of `suit`, or None"""
        cards = self.unseen(suit)
        return cards[0] if cards else None

    # ---------------------------------------------------------------------------------- exact probabilities
    def _split(self, seat):
        """
        (hidden seat, other hidden seat, number of unseen cards forced into `seat`, forced into the other,
        number of free cards); exactly two seats must be hidden
        """
        seat = Position.name(seat)
        hidden = self.hidden_seats()
        if len(hidden) != 2:
            raise NotImplementedError('exact probabilities need exactly two hidden hands, there are %d' % len(hidden))
        if seat not in hidden:
            raise ValueError(f'{seat} is not a hidden hand for {self.seat}')
        other = hidden[0] if hidden[1] == seat else hidden[1]
        forced_here = forced_other = free = 0
        for card in self.unseen():
            out_here = card.suit_index in self.voids[seat]
            out_there = card.suit_index in self.voids[other]
            if out_here and out_there:
                raise ValueError(f'inconsistent: both hidden hands are out of {card.suit}')
            if out_there:
                forced_here += 1
            elif out_here:
                forced_other += 1
            else:
                free += 1
        places = self.cards_left(seat) - forced_here
        if not 0 <= places <= free or self.cards_left(other) - forced_other != free - places:
            raise ValueError('inconsistent: the unseen cards do not fit in the hidden hands')
        return seat, other, forced_here, forced_other, free

    def vacant_places(self, seat):
        """
        the places in `seat`'s hand that can still be filled by a free unseen card: the cards it holds minus
        the unseen cards that can only be in its hand
        """
        _, _, forced_here, _, _ = self._split(seat)
        return self.cards_left(seat) - forced_here

    def probability_holds(self, seat, card):
        """
        the exact probability that the hidden `seat` holds the unseen `card`, given the cards each hidden
        hand holds and the suits they have shown out of
        """
        seat, other, forced_here, forced_other, free = self._split(seat)
        if card.code not in {c.code for c in self.unseen()}:
            raise ValueError(f'{card} is not an unseen card')
        if card.suit_index in self.voids[other]:
            return 1.0
        if card.suit_index in self.voids[seat]:
            return 0.0
        return (self.cards_left(seat) - forced_here) / free

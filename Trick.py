


class Trick(list):
    def __init__(self, leader='north', trump=None):
        self.leader=leader
        self.order = None
        self.trump = trump

    def nextCard(self, card):
        self.append(card)

    def winner(self):
        if len(self) != 4:
            raise(ValueError('Must have 4 cards in the trick'))
        tmp = self
        tmp.sort()
        winning_card = tmp[-1]

        print winning_card




if __name__ == "__main__":
    import Card
    t = Trick(trump='hearts')
    print t
    t.nextCard(Card.Card(3,3))
    print t
    t.nextCard(Card.Card(5,2, True))
    print t
    t.nextCard(Card.Card(7,3))
    print t
    t.nextCard(Card.Card(9,3))
    print t
    t.winner()



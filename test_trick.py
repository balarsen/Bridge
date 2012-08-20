
import unittest

import Card
import Trick

class TestTrick(unittest.TestCase):
    def setUp(self):
        super(TestTrick, self).setUp()
        self.t_n = Trick.Trick(trump='hearts', leader='north')
        self.t_s = Trick.Trick(trump='hearts', leader='south')
        self.t_e = Trick.Trick(trump='hearts', leader='east')
        self.t_w = Trick.Trick(trump='hearts', leader='west')

    def test_adding(self):
        self.t_n.nextCard(Card.Card(3,3)) # north
        self.assertEqual(len(self.t_n), 1)
        self.t_n.nextCard(Card.Card(5,2)) # east
        self.assertEqual(len(self.t_n), 2)
        self.t_n.nextCard(Card.Card(7,3)) # south
        self.assertEqual(len(self.t_n), 3)
        self.t_n.nextCard(Card.Card(9,3)) # west
        self.assertEqual(len(self.t_n), 4)
        self.assertRaises(IndexError, self.t_n.nextCard, Card.Card(9,3))

        self.t_s.nextCard(Card.Card(3,3)) # north
        self.t_s.nextCard(Card.Card(5,2)) # east
        self.t_s.nextCard(Card.Card(7,3)) # south
        self.t_s.nextCard(Card.Card(9,3)) # west

        self.t_e.nextCard(Card.Card(3,3)) # north
        self.t_e.nextCard(Card.Card(5,2)) # east
        self.t_e.nextCard(Card.Card(7,3)) # south
        self.t_e.nextCard(Card.Card(9,3)) # west

        self.t_w.nextCard(Card.Card(3,3)) # north
        self.t_w.nextCard(Card.Card(5,2)) # east
        self.t_w.nextCard(Card.Card(7,3)) # south
        self.t_w.nextCard(Card.Card(9,3)) # west

    def test_init(self):
        self.assertRaises(ValueError, Trick.Trick, trump='bad')
        t = Trick.Trick(trump='hearts', leader='north')
        self.assertEqual(t.trump, 'hearts')
        t = Trick.Trick(trump=2, leader='north')
        self.assertEqual(t.trump, 'hearts')
        self.assertEqual(['north', 'east', 'south', 'west'], t._seats)
        t = Trick.Trick(trump=2, leader='south')
        self.assertEqual([ 'south', 'west', 'north', 'east',], t._seats)

    def test_getCard(self):
        self.t_n.nextCard(Card.Card(3,3)) # north
        self.t_n.nextCard(Card.Card(5,2)) # east
        self.t_n.nextCard(Card.Card(7,3)) # south
        self.t_n.nextCard(Card.Card(9,3)) # west

        self.assertEqual(Card.Card(3,3), self.t_n.getCard('north'))
        self.assertEqual(Card.Card(5,2), self.t_n.getCard('east'))
        self.assertEqual(Card.Card(7,3), self.t_n.getCard('south'))
        self.assertEqual(Card.Card(9,3), self.t_n.getCard('west'))

        self.t_s.nextCard(Card.Card(3,3)) # south
        self.t_s.nextCard(Card.Card(5,2)) # west
        self.t_s.nextCard(Card.Card(7,3)) # north
        self.t_s.nextCard(Card.Card(9,3)) # east

        self.assertEqual(Card.Card(3,3), self.t_s.getCard('south'))
        self.assertEqual(Card.Card(5,2), self.t_s.getCard('west'))
        self.assertEqual(Card.Card(7,3), self.t_s.getCard('north'))
        self.assertEqual(Card.Card(9,3), self.t_s.getCard('east'))

    def test_nsew(self):
        self.t_s.nextCard(Card.Card(3,3)) # north
        self.t_s.nextCard(Card.Card(5,2)) # east
        self.t_s.nextCard(Card.Card(7,3)) # south
        self.t_s.nextCard(Card.Card(9,3)) # west
        self.assertEqual(Card.Card(3,3), self.t_s.south)
        self.assertEqual(Card.Card(5,2), self.t_s.west)
        self.assertEqual(Card.Card(7,3), self.t_s.north)
        self.assertEqual(Card.Card(9,3), self.t_s.east)

    def test_winner(self):
        self.t_n.nextCard(Card.Card(3,3)) # north
        self.t_n.nextCard(Card.Card(5,2)) # east
        self.t_n.nextCard(Card.Card(7,3)) # south
        self.t_n.nextCard(Card.Card(9,3)) # west
        self.assertEqual((Card.Card(5,2), 'east'), self.t_n.winner)



if __name__ == '__main__':
    unittest.main()
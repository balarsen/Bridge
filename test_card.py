

import unittest

import card

class TestCard(unittest.TestCase):
    def test_init(self):
        """input checking"""
        self.assertRaises(ValueError, card.card, 15, 'hearts')
        self.assertRaises(ValueError, card.card, 'bad', 'hearts')
        self.assertRaises(ValueError, card.card, 12, 'bad')
        self.assertRaises(ValueError, card.card, 'ace', 'bad')
        self.assertEqual('two', card.card(2, 1).value)

    def test_bool(self):
        """test boolean ops (total_ordering)"""
        expected = card.card(4,1)
        self.assertEqual(card.card(4,1), expected)
        self.assertLessEqual(card.card(4,1), expected)
        self.assertLessEqual(card.card(3,1), expected)


if __name__ == '__main__':
    unittest.main()
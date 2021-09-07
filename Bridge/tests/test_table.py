
import unittest

from .. import Table

class TestTable(unittest.TestCase):
    def setUp(self):
        super(TestTable, self).setUp()

    def test_position(self):
        """position"""
        self.assertRaises(ValueError, Table.position, 'badval')
        self.assertEqual('North', Table.position('North').position)
        self.assertEqual(0, Table.position('North').score)

    def test_Table(self):
        """test Table class"""
        self.assertEqual(Table.Table().north.position, Table.position('North').position)

    def test_pos2index(self):
        """pos2index"""
        self.assertEqual(0, Table.pos2index('North', 'North'))
        self.assertEqual(1, Table.pos2index('North', 'East'))
        self.assertEqual(2, Table.pos2index('North', 'South'))
        self.assertEqual(3, Table.pos2index('North', 'West'))

  
        

if __name__ == '__main__':
    unittest.main()

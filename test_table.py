
import unittest

import Table

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
        

if __name__ == '__main__':
    unittest.main()

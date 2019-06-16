import unittest
from GraphParser import GraphParser

class ParserTest (unittest.TestCase):

    def test_initParser(self):
        parser = GraphParser("Tests/graph.json");
        G = parser.G
        self.assertEqual(G['R1'].availablity,)


if __name__ == '__main__':
    unittest.main()

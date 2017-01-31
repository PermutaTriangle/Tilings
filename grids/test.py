import unittest
from Tiling import *

class TestTilingRank(unittest.TestCase):
    
    def test_empty(self):
        self.assertEqual(Tiling({}).rank(), 0)

    def test_points_no_clash(self):
        self.assertEqual(Tiling({(0,0): Block.point}).rank(), 1)
        self.assertEqual(Tiling({(0,0): Block.point, (1,1): Block.point, (2,2): Block.point}).rank(), 1)

    def test_sets_no_clash(self):
        self.assertEqual(Tiling({(0,0): Block.decreasing, (1,1): Block.point, (3,4): Block.increasing}).rank(), 2)

    def test_point_point_clash(self):
        self.assertEqual(Tiling({(0,0): Block.point, (1,0): Block.point}).rank(), 3)

    def test_set_point_clash(self):
        self.assertEqual(Tiling({(0,0): Block.point, (0,1): Block.decreasing}).rank(), 4)

    def test_point_L_clash(self):
        self.assertEqual(Tiling({(0,0): Block.point, (0,1): Block.point, (1,0): Block.point}).rank(), 5)

    def test_set_set_clash(self):
        self.assertEqual(Tiling({(0,0): Block.decreasing, (1,0): Block.increasing}).rank(), 6)

    def test_other_clashes(self):
        self.assertEqual(Tiling({(0,0): Block.decreasing, (1,1): Block.increasing, (1,2): Block.point, (2,1): Block.decreasing}).rank(), 7)
        self.assertEqual(Tiling({(0,0): Block.decreasing, (0,1): Block.increasing, (1,0): Block.increasing, (1,1): Block.decreasing}).rank(), 7)
        self.assertEqual(Tiling({(0,0): Block.decreasing, (0,1): Block.increasing, (1,0): Block.increasing}).rank(), 7)
        self.assertEqual(Tiling({(0,0): Block.point, (0,1): Block.increasing, (1,0): Block.increasing}).rank(), 7)
        self.assertEqual(Tiling({(0,0): Block.decreasing, (0,1): Block.point, (1,0): Block.increasing}).rank(), 7)
        self.assertEqual(Tiling({(0,0): Block.decreasing, (0,1): Block.increasing, (1,0): Block.point}).rank(), 7)
        self.assertEqual(Tiling({(0,0): Block.point, (0,1): Block.increasing, (1,0): Block.point}).rank(), 7)
        self.assertEqual(Tiling({(0,0): Block.decreasing, (0,1): Block.point, (1,0): Block.point}).rank(), 7)
        self.assertEqual(Tiling({(0,0): Block.point, (0,1): Block.point, (1,0): Block.decreasing}).rank(), 7)



if __name__ == '__main__':
    unittest.main()

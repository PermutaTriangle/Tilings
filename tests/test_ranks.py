import pytest
from grids import Block, Tiling

    
def test_empty():
    assert(Tiling({}).rank() == 0)

def test_points_no_clash():
    assert(Tiling({(0,0): Block.point}).rank() == 1)
    assert(Tiling({(0,0): Block.point, (1,1): Block.point, (2,2): Block.point}).rank() == 1)

def test_sets_no_clash():
    assert(Tiling({(0,0): Block.decreasing, (1,1): Block.point, (3,4): Block.increasing}).rank() == 2)

def test_point_point_clash():
    assert(Tiling({(0,0): Block.point, (1,0): Block.point}).rank() == 3)

def test_set_point_clash():
    assert(Tiling({(0,0): Block.point, (0,1): Block.decreasing}).rank() == 4)

def test_point_L_clash():
    assert(Tiling({(0,0): Block.point, (0,1): Block.point, (1,0): Block.point}).rank() == 5)

def test_point_set_L_clash():
    assert(Tiling({(0,0): Block.point, (0,1): Block.increasing, (1,0): Block.point}).rank() == 6)
    assert(Tiling({(0,0): Block.decreasing, (0,1): Block.point, (1,0): Block.point}).rank() == 6)
    assert(Tiling({(0,0): Block.point, (0,1): Block.point, (1,0): Block.decreasing}).rank() == 6)
    assert(Tiling({(0,0): Block.point, (0,1): Block.increasing, (1,0): Block.increasing}).rank() == 6)

def test_set_set_clash():
    assert(Tiling({(0,0): Block.decreasing, (1,0): Block.increasing}).rank() == 7)
    assert(Tiling({(0,0): Block.decreasing, (1,1): Block.increasing, (1,2): Block.point, (2,1): Block.decreasing}).rank() == 7)
    assert(Tiling({(0,0): Block.decreasing, (0,1): Block.point, (1,0): Block.increasing}).rank() == 7)
    assert(Tiling({(0,0): Block.decreasing, (0,1): Block.increasing, (1,0): Block.point}).rank() == 7)

def test_set_L_clash():
    assert(Tiling({(0,0): Block.decreasing, (0,1): Block.increasing, (1,0): Block.increasing}).rank() == 8)

def test_set_square_clash():
    assert(Tiling({(0,0): Block.decreasing, (0,1): Block.increasing, (1,0): Block.increasing, (1,1): Block.decreasing}).rank() == 9)


if __name__ == '__main__':
    unittest.main()

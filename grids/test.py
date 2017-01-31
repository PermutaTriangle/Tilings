import pytest
from Tiling import *

    
def test_empty():
    assert(Tiling({}).rank() == 0)

def test_points_no_clash():
    assert(Tiling({(0,0): Tile.P}).rank() == 1)
    assert(Tiling({(0,0): Tile.P, (1,1): Tile.P, (2,2): Tile.P}).rank() == 1)

def test_sets_no_clash():
    assert(Tiling({(0,0): Tile.DECREASING, (1,1): Tile.P, (3,4): Tile.INCREASING}).rank() == 2)

def test_point_point_clash():
    assert(Tiling({(0,0): Tile.P, (1,0): Tile.P}).rank() == 3)

def test_set_point_clash():
    assert(Tiling({(0,0): Tile.P, (0,1): Tile.DECREASING}).rank() == 4)

def test_point_L_clash():
    assert(Tiling({(0,0): Tile.P, (0,1): Tile.P, (1,0): Tile.P}).rank() == 5)

def test_point_set_L_clash():
    assert(Tiling({(0,0): Tile.P, (0,1): Tile.INCREASING, (1,0): Tile.P}).rank() == 6)
    assert(Tiling({(0,0): Tile.DECREASING, (0,1): Tile.P, (1,0): Tile.P}).rank() == 6)
    assert(Tiling({(0,0): Tile.P, (0,1): Tile.P, (1,0): Tile.DECREASING}).rank() == 6)
    assert(Tiling({(0,0): Tile.P, (0,1): Tile.INCREASING, (1,0): Tile.INCREASING}).rank() == 6)

def test_set_set_clash():
    assert(Tiling({(0,0): Tile.DECREASING, (1,0): Tile.INCREASING}).rank() == 7)
    assert(Tiling({(0,0): Tile.DECREASING, (1,1): Tile.INCREASING, (1,2): Tile.P, (2,1): Tile.DECREASING}).rank() == 7)
    assert(Tiling({(0,0): Tile.DECREASING, (0,1): Tile.P, (1,0): Tile.INCREASING}).rank() == 7)
    assert(Tiling({(0,0): Tile.DECREASING, (0,1): Tile.INCREASING, (1,0): Tile.P}).rank() == 7)

def test_set_L_clash():
    assert(Tiling({(0,0): Tile.DECREASING, (0,1): Tile.INCREASING, (1,0): Tile.INCREASING}).rank() == 8)

def test_set_square_clash():
    assert(Tiling({(0,0): Tile.DECREASING, (0,1): Tile.INCREASING, (1,0): Tile.INCREASING, (1,1): Tile.DECREASING}).rank() == 9)


if __name__ == '__main__':
    unittest.main()

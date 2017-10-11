import pytest

from grids_two import Obstruction, Tiling
from permuta import Perm


def test_compression():
    tiling = Tiling(
        positive_cells=frozenset({(2, 0), (1, 0), (3, 1)}),
        possibly_empty=frozenset({(3, 0)}),
        obstructions=[
            Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
            Obstruction(Perm((0, 1)), ((1, 0), (2, 0))),
            Obstruction(Perm((0, 1)), ((1, 0), (3, 0))),
            Obstruction(Perm((0, 1)), ((2, 0), (2, 0))),
            Obstruction(Perm((0, 1)), ((2, 0), (3, 0))),
            Obstruction(Perm((0, 1)), ((3, 1), (3, 1))),
            Obstruction(Perm((1, 0)), ((3, 0), (3, 0))),
            Obstruction(Perm((1, 0)), ((3, 1), (3, 0))),
            Obstruction(Perm((1, 0)), ((3, 1), (3, 1))),
            Obstruction(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 0))),
            Obstruction(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 1))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (1, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (3, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (2, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (2, 0), (3, 0))),
            Obstruction(Perm((2, 1, 0)), ((2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((2, 0), (2, 0), (3, 0)))])

    assert tiling == Tiling.decompress(tiling.compress())


@pytest.fixture
def smallrotatetil():
    return Tiling(
        point_cells=frozenset({(4, 0)}),
        positive_cells=frozenset({(1, 1)}),
        possibly_empty=frozenset({(1, 3), (3, 2)}),
        obstructions=[Obstruction(Perm((0, 2, 1)),
                                  ((1, 1), (1, 3), (3, 2)))])


@pytest.fixture
def rotatetil():
    return Tiling(
        point_cells=frozenset({(4, 0)}),
        positive_cells=frozenset({(0, 0), (1, 2)}),
        possibly_empty=frozenset({(2, 3), (3, 2)}),
        obstructions=[Obstruction(Perm((0, 2, 1, 3)),
                                  [(0, 0), (1, 2), (2, 1), (3, 2)])])


def test_rotate(rotatetil, smallrotatetil):
    assert smallrotatetil.rotate90() == Tiling(
        point_cells=frozenset({(0, 0)}),
        positive_cells=frozenset({(1, 2)}),
        possibly_empty=frozenset({(2, 1), (3, 2)}),
        obstructions=[Obstruction(Perm((2, 0, 1)),
                                  ((1, 2), (2, 1), (3, 2)))])
    print(rotatetil.rotate90())
    assert rotatetil.rotate90() == Tiling(
        point_cells=frozenset({(0, 0)}),
        positive_cells=frozenset({(0, 4), (2, 3)}),
        possibly_empty=frozenset({(1, 2), (3, 1)}),
        obstructions=[Obstruction(Perm((3, 1, 2, 0)),
                                  ((0, 4), (1, 2), (2, 3), (3, 1)))])
    assert rotatetil.rotate180() == rotatetil.rotate90().rotate90()

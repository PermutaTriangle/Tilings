import pytest

from grids_two import Obstruction, Requirement, Tiling
from permuta import Perm


def test_compression_noreq():
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


def test_compression():
    tiling = Tiling(
        positive_cells=frozenset({(2, 0), (1, 0), (3, 1)}),
        possibly_empty=frozenset({(3, 0), (2, 2), (2, 3), (0, 1)}),
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
            Obstruction(Perm((2, 1, 0)), ((2, 0), (2, 0), (3, 0)))],
        requirements=[
            [Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 2))),
             Requirement(Perm((1, 0, 2)), ((0, 0), (1, 0), (2, 2))),
             Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 3))),
             Requirement(Perm((0, 1, 2)), ((0, 1), (1, 0), (2, 2)))],
            [Requirement(Perm((0, 1, 2)), ((2, 2), (2, 2), (2, 2))),
             Requirement(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0))),
             Requirement(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 0)))],
            [Requirement(Perm((0, 1)), ((1, 0), (3, 0))),
             Requirement(Perm((0, 1)), ((2, 0), (2, 0))),
             Requirement(Perm((0, 1)), ((2, 0), (3, 0)))],
            [Requirement(Perm((1, 0)), ((3, 1), (3, 0))),
             Requirement(Perm((1, 0)), ((3, 1), (3, 1)))]])

    assert tiling == Tiling.decompress(tiling.compress())


@pytest.fixture
def christian_til():
    return Tiling(point_cells=[(1, 0), (2, 1)],
                  positive_cells=[(2, 0)],
                  possibly_empty=[(0, 0), (1, 1)],
                  obstructions=[Obstruction(Perm((0, 2, 3, 1)),
                                            [(0, 0), (1, 1), (1, 1), (2, 0)])])


def test_symmetries(christian_til):
    rotate90til = Tiling(
        point_cells=[(0, 1), (1, 0)],
        positive_cells=[(0, 0)],
        possibly_empty=[(0, 2), (1, 1)],
        obstructions=[Obstruction(Perm((3, 0, 2, 1)),
                                  [(0, 2), (0, 0), (1, 1), (1, 1)])])
    assert rotate90til == christian_til.rotate90()

    rotate180til = Tiling(
        point_cells=[(0, 0), (1, 1)],
        positive_cells=[(0, 1)],
        possibly_empty=[(1, 0), (2, 1)],
        obstructions=[Obstruction(Perm((2, 0, 1, 3)),
                                  [(0, 1), (1, 0), (1, 0), (2, 1)])])
    assert rotate180til == christian_til.rotate180()

    rotate270til = Tiling(
        point_cells=[(0, 2), (1, 1)],
        positive_cells=[(1, 2)],
        possibly_empty=[(0, 1), (1, 0)],
        obstructions=[Obstruction(Perm((2, 1, 3, 0)),
                                  [(0, 1), (0, 1), (1, 2), (1, 0)])])
    assert rotate270til == christian_til.rotate270()

    invtil = Tiling(
        point_cells=[(0, 1), (1, 2)],
        positive_cells=[(0, 2)],
        possibly_empty=[(0, 0), (1, 1)],
        obstructions=[Obstruction(Perm((0, 3, 1, 2)),
                                  [(0, 0), (0, 2), (1, 1), (1, 1)])])
    assert invtil == christian_til.inverse()

    revtil = Tiling(
        point_cells=[(0, 1), (1, 0)],
        positive_cells=[(0, 0)],
        possibly_empty=[(1, 1), (2, 0)],
        obstructions=[Obstruction(Perm((1, 3, 2, 0)),
                                  [(0, 0), (1, 1), (1, 1), (2, 0)])])
    assert revtil == christian_til.reverse()

    comtil = Tiling(
        point_cells=[(1, 1), (2, 0)],
        positive_cells=[(2, 1)],
        possibly_empty=[(0, 1), (1, 0)],
        obstructions=[Obstruction(Perm((3, 1, 0, 2)),
                                  [(0, 1), (1, 0), (1, 0), (2, 1)])])
    assert comtil == christian_til.complement()

    aditil = Tiling(
        point_cells=[(0, 0), (1, 1)],
        positive_cells=[(1, 0)],
        possibly_empty=[(0, 1), (1, 2)],
        obstructions=[Obstruction(Perm((1, 2, 0, 3)),
                                  [(0, 1), (0, 1), (1, 0), (1, 2)])])
    assert aditil == christian_til.antidiagonal()

import json

import pytest

from grids_three import Obstruction, Requirement, Tiling
from permuta import Perm


@pytest.fixture
def compresstil():
    return Tiling(
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


@pytest.fixture
def typical_redundant_obstructions():
    """Returns a very typical list of obstructions clustered together in a
    corner of a tiling.  """
    return [
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
        Obstruction(Perm((2, 1, 0)), ((2, 0), (2, 0), (3, 0))),
        Obstruction(Perm((3, 2, 1, 0)), ((1, 1), (2, 0), (2, 0), (2, 0))),
        Obstruction(Perm((3, 2, 1, 0)), ((2, 1), (2, 1), (3, 0), (3, 0)))
    ]


def test_constructor_no_requirements(typical_redundant_obstructions):
    """Tests the constructor of Tiling, thereby the minimization methods used
    in the constructor with different options for remove_empty and
    assume_empty. Proper update of the dimensions of the tiling and proper
    computation of empty and active cells.

    Tests without any requirements.
    """
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty=False, assume_empty=False)
    assert len(tiling._obstructions) == 18
    assert len(tiling._requirements) == 0
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 2

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty=False, assume_empty=True)

    assert len(tiling._obstructions) == 22
    assert len(tiling._requirements) == 0
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 2
    assert tiling.empty_cells == {(0, 0), (0, 1), (1, 1), (2, 1)}
    assert tiling.active_cells == {(1, 0), (2, 0), (3, 0), (3, 1)}

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty=True, assume_empty=True)

    (i, j) = tiling.dimensions
    assert i == 3
    assert j == 2
    assert tiling.empty_cells == {(0, 1), (1, 1)}
    assert tiling.active_cells == {(1, 0), (2, 0), (3, 0), (3, 1)}
    assert len(tiling._obstructions) == 20
    assert len(tiling._requirements) == 0

    tiling2 = Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
            Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
            Obstruction(Perm((0, 1)), ((0, 0), (2, 0))),
            Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
            Obstruction(Perm((0, 1)), ((1, 0), (2, 0))),
            Obstruction(Perm((0, 1)), ((2, 1), (2, 1))),
            Obstruction(Perm((1, 0)), ((2, 0), (2, 0))),
            Obstruction(Perm((1, 0)), ((2, 1), (2, 0))),
            Obstruction(Perm((1, 0)), ((2, 1), (2, 1))),
            Obstruction(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 1))),
            Obstruction(Perm((2, 1, 0)), ((0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((2, 1, 0)), ((0, 0), (0, 0), (1, 0))),
            Obstruction(Perm((2, 1, 0)), ((0, 0), (0, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((0, 0), (1, 0), (1, 0))),
            Obstruction(Perm((2, 1, 0)), ((0, 0), (1, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (1, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (2, 0))),
        ],
        remove_empty=True, assume_empty=True)

    assert tiling == tiling2


def test_compression_noreq():
    tiling = Tiling(
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
        remove_empty=False, assume_empty=True)

    assert tiling == Tiling.decompress(tiling.compress(),
                                       remove_empty=False,
                                       assume_empty=False)


@pytest.mark.skip
def test_compression(compresstil):
    assert compresstil == Tiling.decompress(compresstil.compress())


@pytest.mark.skip
def test_json(compresstil):
    assert compresstil == Tiling.from_json(
        json.dumps(compresstil.to_jsonable()))


# @pytest.fixture
def christian_til():
    return Tiling(point_cells=[(1, 0), (2, 1)],
                  positive_cells=[(2, 0)],
                  possibly_empty=[(0, 0), (1, 1)],
                  obstructions=[Obstruction(Perm((0, 2, 3, 1)),
                                            [(0, 0), (1, 1), (1, 1), (2, 0)])])


@pytest.mark.skip
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

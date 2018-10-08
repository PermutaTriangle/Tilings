import json
from itertools import chain

import pytest

from grids_three import GriddedPerm, Obstruction, Requirement, Tiling
from permuta import Perm


@pytest.fixture
def compresstil():
    """Returns a tiling that has both obstructions and requirements. For
    testing compression and json."""
    return Tiling(obstructions=(
                    Obstruction(Perm((0,)), ((1, 0),)),
                    Obstruction(Perm((0,)), ((2, 1),)),
                    Obstruction(Perm((0, 1)), ((1, 1), (1, 1))),
                    Obstruction(Perm((0, 1)), ((2, 0), (2, 0))),
                    Obstruction(Perm((1, 0)), ((1, 1), (1, 1))),
                    Obstruction(Perm((1, 0)), ((1, 1), (2, 0))),
                    Obstruction(Perm((1, 0)), ((2, 0), (2, 0))),
                    Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 1))),
                    Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (2, 0))),
                    Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 1), (0, 1))),
                    Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 1), (1, 1))),
                    Obstruction(Perm((0, 2, 1)), ((0, 0), (0, 0), (0, 0))),
                    Obstruction(Perm((0, 2, 1)), ((0, 0), (0, 0), (2, 0))),
                    Obstruction(Perm((1, 0, 2)), ((0, 1), (0, 0), (1, 1))),
                    Obstruction(Perm((2, 0, 1)), ((0, 0), (0, 0), (0, 0))),
                    Obstruction(Perm((0, 1, 3, 2)),
                                ((0, 1), (0, 1), (0, 1), (0, 1))),
                    Obstruction(Perm((0, 1, 3, 2)),
                                ((0, 1), (0, 1), (0, 1), (1, 1))),
                    Obstruction(Perm((0, 2, 1, 3)),
                                ((0, 1), (0, 1), (0, 1), (0, 1))),
                    Obstruction(Perm((0, 2, 1, 3)),
                                ((0, 1), (0, 1), (0, 1), (1, 1))),
                    Obstruction(Perm((0, 2, 3, 1)),
                                ((0, 1), (0, 1), (0, 1), (0, 1))),
                    Obstruction(Perm((0, 2, 3, 1)),
                                ((0, 1), (0, 1), (0, 1), (1, 1))),
                    Obstruction(Perm((2, 0, 1, 3)),
                                ((0, 1), (0, 1), (0, 1), (0, 1))),
                    Obstruction(Perm((2, 0, 1, 3)),
                                ((0, 1), (0, 1), (0, 1), (1, 1)))),
                  requirements=(
                    (Requirement(Perm((0,)), ((1, 1),)),
                     Requirement(Perm((0,)), ((2, 0),))),
                    (Requirement(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0))),)))


@pytest.fixture
def empty_tiling():
    return Tiling(obstructions=(Obstruction(Perm((0, 1)), ((0, 0), (0, 1))),
                                Obstruction(Perm((1, 0)), ((0, 1), (0, 0)))),
                  requirements=((Requirement(Perm((0,)), ((0, 0),)),),
                                (Requirement(Perm((0,)), ((0, 1),)),)))


@pytest.fixture
def finite_tiling():
    return Tiling(obstructions=(
                        Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
                        Obstruction(Perm((0, 1)), ((0, 1), (0, 1))),
                        Obstruction(Perm((2, 1, 0)), ((0, 0), (0, 0), (0, 0))),
                        Obstruction(Perm((2, 1, 0)), ((0, 1), (0, 1), (0, 1))),
                        Obstruction(Perm((3, 2, 1, 0)),
                                    ((0, 1), (0, 1), (0, 0), (0, 0)))),
                  requirements=((Requirement(Perm((0,)), ((0, 0),)),),))


@pytest.fixture
def factorable_tiling():
    return Tiling(obstructions=[
                        Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))),
                        Obstruction(Perm((0, 2, 1)), ((1, 0), (1, 0), (1, 0))),
                        Obstruction(Perm((2, 1, 0)), ((2, 2), (2, 2), (2, 2))),
                        Obstruction(Perm((2, 0, 1)), ((2, 3), (2, 3), (2, 3))),
                        Obstruction(Perm((1, 0, 2)), ((5, 4), (5, 4), (5, 4))),
                        Obstruction(Perm((2, 0, 1)), ((5, 4), (5, 4), (5, 4))),
                        Obstruction(Perm((1, 2, 0)), ((4, 6), (4, 6), (4, 6))),
                        Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (2, 2))),
                        Obstruction(Perm((0, 2, 1, 3)),
                                    ((2, 2), (2, 2), (2, 3), (2, 3))),
                        Obstruction(Perm((0, 1)), ((6, 4), (6, 4))),
                        Obstruction(Perm((1, 0)), ((6, 4), (6, 4))),
                        Obstruction(Perm((0, 1)), ((7, 7), (7, 7)))],
                  requirements=[[Requirement(Perm((0, 1)), ((0, 0), (0, 0))),
                                 Requirement(Perm((1, 0)), ((4, 6), (4, 6)))],
                                [Requirement(Perm((0,)), ((6, 4),))]])


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


@pytest.fixture
def typical_redundant_requirements():
    """Returns a very typical list of requirements of a tiling.  """
    return [
        [Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 3))),
         Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 4))),
         Requirement(Perm((1, 0, 2)), ((0, 0), (1, 0), (2, 3))),
         Requirement(Perm((1, 0, 2)), ((0, 1), (1, 0), (2, 3)))],
        [Requirement(Perm((0, 1, 2)), ((2, 3), (2, 3), (2, 3))),
         Requirement(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0))),
         Requirement(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 0)))],
        [Requirement(Perm((0, 1)), ((1, 0), (3, 0))),
         Requirement(Perm((0, 1)), ((2, 0), (2, 0))),
         Requirement(Perm((0, 1)), ((2, 0), (3, 0))),
         Requirement(Perm((0, 1)), ((2, 0), (3, 1)))],
        [Requirement(Perm((1, 0)), ((3, 3), (3, 1))),
         Requirement(Perm((1, 0)), ((3, 1), (3, 1))),
         Requirement(Perm((1, 0)), ((3, 1), (3, 0)))]]


@pytest.mark.filterwarnings('ignore::UserWarning')
def test_constructor_no_requirements(typical_redundant_obstructions):
    """Tests the constructor of Tiling, thereby the minimization methods used
    in the constructor with different options for remove_empty and
    derive_empty. Proper update of the dimensions of the tiling and proper
    computation of empty and active cells.

    Tests without any requirements.
    """
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty=False, derive_empty=False, minimize=False)
    assert len(tiling._obstructions) == 20
    assert len(tiling._requirements) == 0
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 2

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty=False, derive_empty=False, minimize=True)
    assert len(tiling._obstructions) == 18
    assert len(tiling._requirements) == 0
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 2

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty=False, derive_empty=True, minimize=False)

    assert len(tiling._obstructions) == 22
    assert len(tiling._requirements) == 0
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 2
    assert tiling.empty_cells == {(0, 0), (0, 1)}
    assert tiling.active_cells == {(1, 0), (1, 1), (2, 0),
                                   (2, 1), (3, 0), (3, 1)}

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty=False, derive_empty=True, minimize=True)

    assert len(tiling._obstructions) == 22
    assert len(tiling._requirements) == 0
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 2
    assert tiling.empty_cells == {(0, 0), (0, 1), (1, 1), (2, 1)}
    assert tiling.active_cells == {(1, 0), (2, 0), (3, 0), (3, 1)}

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty=True, derive_empty=True, minimize=False)

    (i, j) = tiling.dimensions
    assert i == 3
    assert j == 2
    assert tiling.empty_cells == set()
    assert tiling.active_cells == {(0, 0), (0, 1), (1, 0),
                                   (1, 1), (2, 0), (2, 1)}
    assert len(tiling._obstructions) == 20
    assert len(tiling._requirements) == 0

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty=True, derive_empty=True, minimize=True)

    (i, j) = tiling.dimensions
    assert i == 3
    assert j == 2
    assert tiling.empty_cells == {(0, 1), (1, 1)}
    assert tiling.active_cells == {(0, 0), (1, 0), (2, 0), (2, 1)}
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
        remove_empty=True, derive_empty=True, minimize=True)

    assert tiling == tiling2


def test_constructor_with_requirements(typical_redundant_obstructions,
                                       typical_redundant_requirements):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
        remove_empty=False, derive_empty=False)
    assert len(tiling._obstructions) == 18
    assert len(tiling._requirements) == 4
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 5

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
        remove_empty=False, derive_empty=True)

    assert len(tiling._obstructions) == 29
    assert len(tiling._requirements) == 4
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 5
    assert tiling.empty_cells == {(0, 2), (0, 3), (0, 4), (1, 1), (1, 2),
                                  (1, 3), (1, 4), (2, 1), (2, 2), (3, 2),
                                  (3, 4)}
    assert tiling.active_cells == {(0, 0), (0, 1), (1, 0), (2, 0), (2, 3),
                                   (2, 4), (3, 0), (3, 1), (3, 3)}

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
        remove_empty=True, derive_empty=True)

    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 4
    assert tiling.empty_cells == {(0, 2), (0, 3), (1, 1), (1, 2), (1, 3),
                                  (2, 1), (3, 3)}
    assert tiling.active_cells == {(0, 0), (0, 1), (1, 0), (2, 0), (2, 2),
                                   (2, 3), (3, 0), (3, 1), (3, 2)}
    assert len(tiling._obstructions) == 25
    assert len(tiling._requirements) == 4

    tiling2 = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=[
            [Requirement(Perm((0, 1)), [(2, 0), (3, 1)])],
            [Requirement(Perm((1, 0)), [(3, 2), (3, 1)])],
            [Requirement(Perm((0, 1, 2)), [(0, 0), (1, 0), (2, 2)]),
             Requirement(Perm((0, 1, 2)), [(0, 0), (1, 0), (2, 3)]),
             Requirement(Perm((1, 0, 2)), [(0, 0), (1, 0), (2, 2)]),
             Requirement(Perm((1, 0, 2)), [(0, 1), (1, 0), (2, 2)])],
            [Requirement(Perm((0, 1, 2)), [(2, 2), (2, 2), (2, 2)]),
             Requirement(Perm((1, 0, 2)), [(0, 0), (0, 0), (0, 0)])]],
        remove_empty=True, derive_empty=True)
    assert tiling == tiling2


@pytest.mark.filterwarnings('ignore::UserWarning')
def test_compression_noreq(typical_redundant_obstructions):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty=False, derive_empty=False)

    assert tiling == Tiling.decompress(tiling.compress(),
                                       remove_empty=False,
                                       derive_empty=False)

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty=False, derive_empty=True)

    assert tiling == Tiling.decompress(tiling.compress(),
                                       remove_empty=False,
                                       derive_empty=True)

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty=True, derive_empty=True)
    assert tiling == Tiling.decompress(tiling.compress(),
                                       remove_empty=True,
                                       derive_empty=True)


def test_from_string():
    string = "123_231_45321"
    assert (Tiling.from_string(string) ==
            Tiling([Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))),
                    Obstruction(Perm((1, 2, 0)), ((0, 0), (0, 0), (0, 0))),
                    Obstruction(Perm((3, 4, 2, 1, 0)),
                                ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)))]))
    string = "3201_1032"
    assert (Tiling.from_string(string) ==
            Tiling([Obstruction(Perm((3, 2, 0, 1)),
                                ((0, 0), (0, 0), (0, 0), (0, 0))),
                    Obstruction(Perm((1, 0, 3, 2)),
                                ((0, 0), (0, 0), (0, 0), (0, 0)))]))
    string = "3142"
    assert (Tiling.from_string(string) ==
            Tiling([Obstruction(Perm((2, 0, 3, 1)),
                                ((0, 0), (0, 0), (0, 0), (0, 0)))]))


def test_compression(compresstil):
    assert compresstil == Tiling.decompress(compresstil.compress())
    assert compresstil.compress() == compresstil.compress()
    assert (compresstil.compress() ==
            Tiling(compresstil.obstructions,
                   compresstil.requirements).compress())


def test_json(compresstil):
    assert compresstil == Tiling.from_json(
        json.dumps(compresstil.to_jsonable()))


def test_cell_within_bounds(typical_redundant_obstructions,
                            typical_redundant_requirements):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
        remove_empty=False, derive_empty=False)
    for i in range(4):
        for j in range(5):
            assert tiling.cell_within_bounds((i, j))
    for i in chain(range(-10, 0), range(5, 10)):
        for j in range(-10, 10):
            assert not tiling.cell_within_bounds((i, j))

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
        remove_empty=True, derive_empty=True)

    for i in range(4):
        for j in range(4):
            assert tiling.cell_within_bounds((i, j))
    for i in chain(range(-10, 0), range(4, 10)):
        for j in range(-10, 10):
            assert not tiling.cell_within_bounds((i, j))


def test_empty_cell(typical_redundant_obstructions,
                    typical_redundant_requirements):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements)

    tiling1 = tiling.empty_cell((3, 0))
    tiling2 = Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
            Obstruction(Perm((0, 1)), ((1, 0), (2, 0))),
            Obstruction(Perm((0, 1)), ((2, 0), (2, 0))),
            Obstruction(Perm((0, 1)), ((3, 1), (3, 1))),
            Obstruction(Perm((1, 0)), ((3, 1), (3, 1))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (1, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (2, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((3, 2, 1, 0)), ((1, 1), (2, 0), (2, 0), (2, 0)))
        ],
        requirements=[
            [Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 3))),
             Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 4))),
             Requirement(Perm((1, 0, 2)), ((0, 0), (1, 0), (2, 3))),
             Requirement(Perm((1, 0, 2)), ((0, 1), (1, 0), (2, 3)))],
            [Requirement(Perm((0, 1, 2)), ((2, 3), (2, 3), (2, 3))),
             Requirement(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0)))],
            [Requirement(Perm((0, 1)), ((2, 0), (2, 0))),
             Requirement(Perm((0, 1)), ((2, 0), (3, 1)))],
            [Requirement(Perm((1, 0)), ((3, 3), (3, 1)))]])
    assert tiling1 == tiling2


def test_insert_cell(typical_redundant_obstructions,
                     typical_redundant_requirements):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements)
    assert tiling.insert_cell((3, 1)) == tiling

    assert (tiling.insert_cell((1, 1)).obstructions[0] ==
            Obstruction(Perm(tuple()), []))

    requirements = typical_redundant_requirements + [[
        Requirement(Perm((0, 1)), [(2, 0), (2, 1)]),
        Requirement(Perm((0, 1)), [(1, 1), (1, 2)])]]
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=requirements)
    tiling1 = tiling.insert_cell((2, 1))
    assert tiling1 == Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=requirements + [[Requirement(Perm((0,)), [(2, 1)])]])


def test_add_obstruction():
    pass


def test_add_requirement():
    pass


def test_add_single_cell_obstruction(typical_redundant_obstructions,
                                     typical_redundant_requirements):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements)
    assert tiling.add_single_cell_obstruction(
        Perm((0,)), (0, 2)) == tiling
    assert tiling.add_single_cell_obstruction(
        Perm((0, 1, 2)), (3, 0)) == tiling
    assert tiling.add_single_cell_obstruction(
        Perm((2, 1, 0)), (2, 0)) == tiling

    tiling1 = Tiling(
        requirements=typical_redundant_requirements,
        obstructions=[
            Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
            Obstruction(Perm((0, 1)), ((1, 0), (2, 0))),
            Obstruction(Perm((0, 1)), ((1, 0), (3, 0))),
            Obstruction(Perm((0, 1)), ((2, 0), (2, 0))),
            Obstruction(Perm((0, 1)), ((2, 0), (3, 0))),
            Obstruction(Perm((0, 1)), ((3, 0), (3, 0))),
            Obstruction(Perm((0, 1)), ((3, 1), (3, 1))),
            Obstruction(Perm((1, 0)), ((3, 0), (3, 0))),
            Obstruction(Perm((1, 0)), ((3, 1), (3, 0))),
            Obstruction(Perm((1, 0)), ((3, 1), (3, 1))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (1, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (3, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (2, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (2, 0), (3, 0))),
            Obstruction(Perm((2, 1, 0)), ((2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((2, 0), (2, 0), (3, 0))),
            Obstruction(Perm((3, 2, 1, 0)), ((1, 1), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((3, 2, 1, 0)), ((2, 1), (2, 1), (3, 0), (3, 0)))])
    assert tiling.add_single_cell_obstruction(
        Perm((0, 1)), (3, 0)) == tiling1


def test_add_single_cell_requirement(typical_redundant_obstructions,
                                     typical_redundant_requirements):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements)
    assert tiling.add_single_cell_requirement(
        Perm((0, 1)), (1, 0)).obstructions[0] == Obstruction(Perm(tuple()), [])
    tiling1 = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=[
            [Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 3))),
             Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 4))),
             Requirement(Perm((1, 0, 2)), ((0, 0), (1, 0), (2, 3))),
             Requirement(Perm((1, 0, 2)), ((0, 1), (1, 0), (2, 3)))],
            [Requirement(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0)))],
            [Requirement(Perm((0, 1)), ((1, 0), (3, 0))),
             Requirement(Perm((0, 1)), ((2, 0), (2, 0))),
             Requirement(Perm((0, 1)), ((2, 0), (3, 0))),
             Requirement(Perm((0, 1)), ((2, 0), (3, 1)))],
            [Requirement(Perm((1, 0)), ((3, 3), (3, 1))),
             Requirement(Perm((1, 0)), ((3, 1), (3, 1))),
             Requirement(Perm((1, 0)), ((3, 1), (3, 0)))]])
    assert (tiling.add_single_cell_requirement(Perm((1, 0, 2)), (0, 0)) ==
            tiling1)
    tiling2 = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=(typical_redundant_requirements +
                      [[Requirement.single_cell(Perm((0, 1, 2)), (0, 0))]]))
    assert (tiling.add_single_cell_requirement(Perm((0, 1, 2)), (0, 0)) ==
            tiling2)


@pytest.fixture
def isolated_tiling():
    return Tiling(
        obstructions=[
          Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (1, 2))),
          Obstruction(Perm((0, 1, 3, 2)), ((0, 0), (0, 0), (1, 2), (2, 1))),
          Obstruction(Perm((0, 2, 1, 3)), ((0, 0), (0, 0), (0, 0), (1, 2)))],
        requirements=[
          [Requirement(Perm((0, )), ((2, 1),)),
           Requirement(Perm((1, 0)), ((1, 2), (1, 2)))],
          [Requirement(Perm((1, 2, 0)), ((1, 2), (1, 2), (2, 1)))]]
    )


def test_fully_isolated(typical_redundant_obstructions,
                        typical_redundant_requirements,
                        isolated_tiling):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements)

    assert not tiling.fully_isolated()
    assert isolated_tiling.fully_isolated()


def test_only_positive_in_row_and_col(typical_redundant_obstructions,
                                      typical_redundant_requirements):
    tiling = Tiling(
        requirements=[[Requirement.single_cell(Perm((0,)), (0, 0))]])
    assert tiling.only_positive_in_row((0, 0))
    assert tiling.only_positive_in_col((0, 0))
    assert tiling.only_positive_in_row_and_col((0, 0))

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=(typical_redundant_requirements +
                      [[Requirement.single_cell(Perm((0,)), (1, 4))]]))
    assert tiling.only_positive_in_row((1, 3))
    assert not tiling.only_positive_in_row((2, 3))
    assert not tiling.only_positive_in_col((2, 3))
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=(typical_redundant_requirements +
                      [[Requirement.single_cell(Perm((0,)), (0, 4))]]))
    assert tiling.only_positive_in_row((0, 3))
    assert tiling.only_positive_in_col((0, 3))
    assert tiling.only_positive_in_row_and_col((0, 3))

    assert tiling.only_positive_in_row((3, 2))
    assert not tiling.only_positive_in_col((3, 2))

    assert not tiling.only_positive_in_col((0, 2))
    assert not tiling.only_positive_in_row((0, 2))


def test_only_cell_in_row_or_col(typical_redundant_obstructions,
                                 typical_redundant_requirements):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements)
    assert tiling.only_cell_in_col((1, 0))
    assert tiling.only_cell_in_row((2, 3))
    assert not tiling.only_cell_in_row((3, 1))
    assert not tiling.only_cell_in_col((3, 1))


def test_cells_in_row_col(typical_redundant_obstructions,
                          typical_redundant_requirements):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements)

    row_1 = tiling.cells_in_row(-1)
    row0 = tiling.cells_in_row(0)
    row1 = tiling.cells_in_row(1)
    row2 = tiling.cells_in_row(2)
    row3 = tiling.cells_in_row(3)
    row4 = tiling.cells_in_row(4)

    assert row_1 == set()
    assert row0 == set((x, 0) for x in range(4))
    assert row1 == {(0, 1), (3, 1)}
    assert row2 == {(2, 2), (3, 2)}
    assert row3 == {(2, 3)}
    assert row4 == set()

    col_1 = tiling.cells_in_col(-1)
    col0 = tiling.cells_in_col(0)
    col1 = tiling.cells_in_col(1)
    col2 = tiling.cells_in_col(2)
    col3 = tiling.cells_in_col(3)
    col4 = tiling.cells_in_col(4)

    assert col_1 == set()
    assert col0 == {(0, 0), (0, 1)}
    assert col1 == {(1, 0)}
    assert col2 == {(2, 0), (2, 2), (2, 3)}
    assert col3 == {(3, 0), (3, 1), (3, 2)}
    assert col4 == set()


def test_cell_basis(typical_redundant_obstructions,
                    typical_redundant_requirements):
    tiling = Tiling(
        obstructions=[Obstruction(Perm((0, 2, 1)), [(0, 0), (0, 0), (0, 0)]),
                      Obstruction(Perm((0, 2, 1)), [(0, 0), (0, 1), (1, 1)]),
                      Obstruction(Perm((0, 2, 1)), [(0, 0), (1, 1), (1, 0)]),
                      Obstruction(Perm((0, 2, 1)), [(1, 1), (1, 1), (1, 1)]),
                      Obstruction(Perm((1, 0)), [(1, 0), (1, 0)]),
                      Obstruction(Perm((2, 0, 1)), [(0, 1), (0, 1), (0, 1)])])
    bdict = tiling.cell_basis()
    assert len(bdict) == 4
    basis = bdict[(0, 0)]
    assert len(basis[1]) == 0
    assert set(basis[0]) == {Perm((0, 2, 1))}
    basis = bdict[(0, 1)]
    assert len(basis[1]) == 0
    assert set(basis[0]) == {Perm((2, 0, 1))}
    basis = bdict[(1, 0)]
    assert len(basis[1]) == 0
    assert set(basis[0]) == {Perm((1, 0))}
    basis = bdict[(1, 1)]
    assert len(basis[1]) == 0
    assert set(basis[0]) == {Perm((0, 2, 1))}
    basis = bdict[(3, 3)]
    assert len(basis) == 2
    assert basis[0] == []
    assert basis[1] == []


def test_cell_graph():
    pass


def test_sort_requirements():
    pass


def test_gridded_perms():
    tiling = Tiling()
    assert len(list(tiling.gridded_perms())) == 1

    tiling = Tiling(requirements=[[Requirement(Perm((0,)), [(0, 0)])]])
    assert len(list(tiling.gridded_perms(maxlen=3))) == 9

    tiling = Tiling(requirements=[[Requirement(Perm((0, 1)),
                                               [(0, 0), (1, 0)])]])
    griddable01 = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable01 == sorted([
        GriddedPerm(Perm((0, 1)), [(0, 0), (1, 0)]),
        GriddedPerm(Perm((0, 1, 2)), [(0, 0), (0, 0), (1, 0)]),
        GriddedPerm(Perm((0, 1, 2)), [(0, 0), (1, 0), (1, 0)]),
        GriddedPerm(Perm((0, 2, 1)), [(0, 0), (0, 0), (1, 0)]),
        GriddedPerm(Perm((0, 2, 1)), [(0, 0), (1, 0), (1, 0)]),
        GriddedPerm(Perm((1, 0, 2)), [(0, 0), (0, 0), (1, 0)]),
        GriddedPerm(Perm((1, 0, 2)), [(0, 0), (1, 0), (1, 0)]),
        GriddedPerm(Perm((1, 2, 0)), [(0, 0), (1, 0), (1, 0)]),
        GriddedPerm(Perm((2, 0, 1)), [(0, 0), (0, 0), (1, 0)])])

    tiling = Tiling(requirements=[[Requirement(Perm((1, 0)),
                                               [(0, 0), (1, 0)])]])
    griddable10 = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable10 == sorted([
        GriddedPerm(Perm((1, 0)), [(0, 0), (1, 0)]),
        GriddedPerm(Perm((0, 2, 1)), [(0, 0), (0, 0), (1, 0)]),
        GriddedPerm(Perm((1, 2, 0)), [(0, 0), (0, 0), (1, 0)]),
        GriddedPerm(Perm((1, 2, 0)), [(0, 0), (1, 0), (1, 0)]),
        GriddedPerm(Perm((2, 1, 0)), [(0, 0), (0, 0), (1, 0)]),
        GriddedPerm(Perm((2, 1, 0)), [(0, 0), (1, 0), (1, 0)]),
        GriddedPerm(Perm((2, 0, 1)), [(0, 0), (0, 0), (1, 0)]),
        GriddedPerm(Perm((2, 0, 1)), [(0, 0), (1, 0), (1, 0)]),
        GriddedPerm(Perm((1, 0, 2)), [(0, 0), (1, 0), (1, 0)])])

    tiling = Tiling(requirements=[[Requirement(Perm((0, 1)),
                                               [(0, 0), (0, 1)])]])
    griddable = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable == sorted([
        GriddedPerm(Perm((0, 1)), [(0, 0), (0, 1)]),
        GriddedPerm(Perm((0, 1, 2)), [(0, 0), (0, 0), (0, 1)]),
        GriddedPerm(Perm((0, 1, 2)), [(0, 0), (0, 1), (0, 1)]),
        GriddedPerm(Perm((0, 2, 1)), [(0, 0), (0, 1), (0, 0)]),
        GriddedPerm(Perm((0, 2, 1)), [(0, 0), (0, 1), (0, 1)]),
        GriddedPerm(Perm((1, 0, 2)), [(0, 0), (0, 0), (0, 1)]),
        GriddedPerm(Perm((1, 0, 2)), [(0, 1), (0, 0), (0, 1)]),
        GriddedPerm(Perm((1, 2, 0)), [(0, 0), (0, 1), (0, 0)]),
        GriddedPerm(Perm((2, 0, 1)), [(0, 1), (0, 0), (0, 1)])])

    tiling = Tiling(
        requirements=[[Requirement(Perm((0, 1)), [(0, 0), (1, 0)])],
                      [Requirement(Perm((1, 0)), [(0, 0), (1, 0)])]])
    griddable = sorted(list(tiling.gridded_perms(maxlen=2)))
    assert len(griddable) == 0
    griddable = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable == sorted([
        GriddedPerm(Perm((1, 2, 0)), [(0, 0), (1, 0), (1, 0)]),
        GriddedPerm(Perm((1, 0, 2)), [(0, 0), (1, 0), (1, 0)]),
        GriddedPerm(Perm((0, 2, 1)), [(0, 0), (0, 0), (1, 0)]),
        GriddedPerm(Perm((2, 0, 1)), [(0, 0), (0, 0), (1, 0)])])

    tiling = Tiling(
        requirements=[[Requirement(Perm((0, 1)), [(0, 0), (1, 0)]),
                       Requirement(Perm((1, 0)), [(0, 0), (1, 0)])]])
    griddable = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable == sorted(list(set(griddable01) | set(griddable10)))

    tiling = Tiling(
        obstructions=[Obstruction(Perm((1, 0)), [(0, 0), (1, 0)])],
        requirements=[[Requirement(Perm((0, 1)), [(0, 0), (1, 0)])]])
    griddable = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable == sorted(list(set(griddable01) - set(griddable10)))

    tiling = Tiling(
        obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (1, 0)])],
        requirements=[[Requirement(Perm((1, 0)), [(0, 0), (1, 0)])]])
    griddable = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable == sorted(list(set(griddable10) - set(griddable01)))

    tiling = Tiling(
        obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
                      Obstruction(Perm((1, 0)), [(0, 0), (1, 0)])],
        requirements=[[Requirement(Perm((0,)), [(0, 0)])],
                      [Requirement(Perm((0,)), [(1, 0)])]])
    assert len(list(tiling.gridded_perms(maxlen=5))) == 0
    assert tiling.is_empty()

    tiling = Tiling(
        obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
                      Obstruction(Perm((1, 0)), [(0, 0), (1, 0)])])
    griddable = sorted(list(tiling.gridded_perms(maxlen=2)))
    assert griddable == [
        GriddedPerm(Perm(), []),
        GriddedPerm(Perm((0,)), [(0, 0)]),
        GriddedPerm(Perm((0,)), [(1, 0)]),
        GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)]),
        GriddedPerm(Perm((0, 1)), [(1, 0), (1, 0)]),
        GriddedPerm(Perm((1, 0)), [(0, 0), (0, 0)]),
        GriddedPerm(Perm((1, 0)), [(1, 0), (1, 0)])]


@pytest.fixture
def christian_til():
    return Tiling(
        obstructions=[Obstruction(Perm((0, 2, 3, 1)),
                                  [(0, 0), (1, 1), (1, 1), (2, 0)]),
                      Obstruction(Perm((0, 1)), [(1, 0), (1, 0)]),
                      Obstruction(Perm((1, 0)), [(1, 0), (1, 0)]),
                      Obstruction(Perm((0, 1)), [(2, 1), (2, 1)]),
                      Obstruction(Perm((1, 0)), [(2, 1), (2, 1)])],
        requirements=[[Requirement(Perm((0, 2, 1)), [(0, 1), (0, 2), (1, 2)]),
                       Requirement(Perm((1, 0)), [(0, 2), (0, 1)])],
                      [Requirement(Perm((0,)), [(1, 0)])],
                      [Requirement(Perm((0,)), [(2, 0)])],
                      [Requirement(Perm((0,)), [(2, 1)])]
                      ])


def test_symmetries(christian_til):
    rotate90til = Tiling(
        obstructions=[Obstruction(Perm((3, 0, 2, 1)),
                                  [(0, 2), (0, 0), (1, 1), (1, 1)]),
                      Obstruction(Perm((0, 1)), [(0, 1), (0, 1)]),
                      Obstruction(Perm((1, 0)), [(0, 1), (0, 1)]),
                      Obstruction(Perm((0, 1)), [(1, 0), (1, 0)]),
                      Obstruction(Perm((1, 0)), [(1, 0), (1, 0)])],
        requirements=[[Requirement(Perm((2, 0, 1)), [(1, 2), (2, 1), (2, 2)]),
                       Requirement(Perm((0, 1)), [(1, 2), (2, 2)])],
                      [Requirement(Perm((0,)), [(0, 0)])],
                      [Requirement(Perm((0,)), [(0, 1)])],
                      [Requirement(Perm((0,)), [(1, 0)])]])
    assert christian_til.rotate90() == rotate90til
    assert rotate90til.rotate90().rotate90().rotate90() == christian_til
    assert rotate90til.rotate180().rotate90() == christian_til
    assert rotate90til.rotate270() == christian_til
    assert rotate90til.rotate90() == christian_til.rotate180()
    assert rotate90til.rotate180() == christian_til.rotate270()

    rotate270til = Tiling(
        obstructions=[Obstruction(Perm((2, 1, 3, 0)),
                                  [(1, 1), (1, 1), (2, 2), (2, 0)]),
                      Obstruction(Perm((0, 1)), [(1, 2), (1, 2)]),
                      Obstruction(Perm((1, 0)), [(1, 2), (1, 2)]),
                      Obstruction(Perm((0, 1)), [(2, 1), (2, 1)]),
                      Obstruction(Perm((1, 0)), [(2, 1), (2, 1)])],
        requirements=[[Requirement(Perm((1, 2, 0)), [(0, 0), (0, 1), (1, 0)]),
                       Requirement(Perm((0, 1)), [(0, 0), (1, 0)])],
                      [Requirement(Perm((0,)), [(1, 2)])],
                      [Requirement(Perm((0,)), [(2, 1)])],
                      [Requirement(Perm((0,)), [(2, 2)])]])
    assert (christian_til.rotate90().rotate90().rotate90() ==
            christian_til.rotate270() == rotate270til)

    assert christian_til.rotate180().rotate180() == christian_til

    revtil = Tiling(
        obstructions=[Obstruction(Perm((1, 3, 2, 0)),
                                  [(0, 0), (1, 1), (1, 1), (2, 0)]),
                      Obstruction(Perm((0, 1)), [(0, 1), (0, 1)]),
                      Obstruction(Perm((1, 0)), [(0, 1), (0, 1)]),
                      Obstruction(Perm((0, 1)), [(1, 0), (1, 0)]),
                      Obstruction(Perm((1, 0)), [(1, 0), (1, 0)])],
        requirements=[[Requirement(Perm((1, 2, 0)), [(1, 2), (2, 2), (2, 1)]),
                       Requirement(Perm((0, 1)), [(2, 1), (2, 2)])],
                      [Requirement(Perm((0,)), [(0, 0)])],
                      [Requirement(Perm((0,)), [(0, 1)])],
                      [Requirement(Perm((0,)), [(1, 0)])]])
    assert christian_til.reverse() == revtil
    assert christian_til.reverse().reverse() == christian_til

    assert christian_til.rotate270().reverse() == christian_til.inverse()
    assert christian_til.reverse().rotate270() == christian_til.antidiagonal()
    assert christian_til.inverse() == christian_til.inverse()

    assert christian_til.rotate180().reverse() == christian_til.complement()
    assert christian_til.rotate90().reverse() == christian_til.antidiagonal()


def test_is_empty(compresstil, empty_tiling, finite_tiling):
    assert not compresstil.is_empty()
    assert not finite_tiling.is_empty()
    assert empty_tiling.is_empty()


def test_is_finite(compresstil, empty_tiling, finite_tiling):
    assert not compresstil.is_finite()
    assert finite_tiling.is_finite()


def test_merge(compresstil, finite_tiling, empty_tiling):
    assert finite_tiling.merge() == finite_tiling
    print(compresstil.merge().requirements)
    assert (compresstil.merge() ==
            Tiling(obstructions=compresstil.obstructions,
                   requirements=(
                       (Requirement(Perm((1, 0, 2, 3)),
                                    ((0, 0), (0, 0), (0, 0), (1, 1))),
                        Requirement(Perm((1, 0, 2, 3)),
                                    ((0, 0), (0, 0), (0, 0), (2, 0))),
                        Requirement(Perm((1, 0, 3, 2)),
                                    ((0, 0), (0, 0), (0, 0), (2, 0))),
                        Requirement(Perm((2, 0, 3, 1)),
                                    ((0, 0), (0, 0), (0, 0), (2, 0))),
                        Requirement(Perm((2, 1, 3, 0)),
                                    ((0, 0), (0, 0), (0, 0), (2, 0)))),)))
    assert empty_tiling.merge() == Tiling((Obstruction(Perm(()), ()),))


def test_point_cells(compresstil, finite_tiling, empty_tiling, christian_til,
                     typical_redundant_obstructions,
                     typical_redundant_requirements):
    assert Tiling(typical_redundant_obstructions,
                  typical_redundant_requirements).point_cells == set([(3, 1)])
    assert compresstil.point_cells == set()
    assert finite_tiling.point_cells == set()
    assert empty_tiling.point_cells == set()
    tiling = compresstil.add_single_cell_requirement(Perm((0, )), (1, 1))
    assert tiling.point_cells == set([(1, 1)])
    tiling = compresstil.add_single_cell_requirement(Perm((0, )), (2, 0))
    assert tiling.point_cells == set([(1, 0)])
    assert christian_til.point_cells == set([(1, 0), (2, 1)])


def test_positive_cells(compresstil, empty_tiling, finite_tiling,
                        christian_til):
    assert compresstil.positive_cells == set([(0, 0)])
    assert finite_tiling.positive_cells == set([(0, 0)])
    assert empty_tiling.positive_cells == set([(0, 0), (0, 1)])
    assert christian_til.positive_cells == set([(1, 0), (0, 2), (0, 1),
                                                (2, 0), (2, 1)])


def test_dimensions(compresstil, empty_tiling, finite_tiling, christian_til):
    assert empty_tiling.dimensions == (1, 2)
    assert finite_tiling.dimensions == (1, 2)
    assert compresstil.dimensions == (3, 2)
    assert christian_til.dimensions == (3, 3)


def test_find_factors(compresstil, factorable_tiling):
    factors = compresstil.find_factors()
    assert len(factors) == 1
    assert factors[0] == compresstil

    factors = factorable_tiling.find_factors()

    actual_factors = [
        Tiling(obstructions=[
                Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))),
                Obstruction(Perm((0, 2, 1)), ((1, 0), (1, 0), (1, 0))),
                Obstruction(Perm((2, 1, 0)), ((2, 1), (2, 1), (2, 1))),
                Obstruction(Perm((2, 0, 1)), ((2, 2), (2, 2), (2, 2))),
                Obstruction(Perm((1, 2, 0)), ((3, 3), (3, 3), (3, 3))),
                Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (2, 1))),
                Obstruction(Perm((0, 2, 1, 3)),
                            ((2, 1), (2, 1), (2, 2), (2, 2)))],
               requirements=[[Requirement(Perm((0, 1)), ((0, 0), (0, 0))),
                              Requirement(Perm((1, 0)), ((3, 3), (3, 3)))]]),
        Tiling(obstructions=[Obstruction(Perm((1, 0, 2)),
                                         ((0, 0), (0, 0), (0, 0))),
                             Obstruction(Perm((2, 0, 1)),
                                         ((0, 0), (0, 0), (0, 0))),
                             Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
                             Obstruction(Perm((1, 0)), ((1, 0), (1, 0)))],
               requirements=[[Requirement(Perm((0,)), ((1, 0),))]]),
        Tiling(obstructions=[Obstruction(Perm((0, 1)), ((0, 0), (0, 0)))])]

    assert len(factors) == len(actual_factors)
    assert all(f in factors for f in actual_factors)

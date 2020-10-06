import json
from collections import Counter
from itertools import chain, product

import pytest
import sympy

from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.exception import InvalidOperationError


@pytest.fixture
def compresstil():
    """Returns a tiling that has both obstructions and requirements. For
    testing compression and json."""
    return Tiling(
        obstructions=(
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((1, 0), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((1, 1), (2, 0))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 1))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 1))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (1, 1))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((1, 0, 2), ((0, 1), (0, 0), (1, 1))),
            GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (1, 1))),
            GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 1), (0, 1), (1, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 1), (1, 1))),
            GriddedPerm((2, 0, 1, 3), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((2, 0, 1, 3), ((0, 1), (0, 1), (0, 1), (1, 1))),
        ),
        requirements=(
            (GriddedPerm((0,), ((1, 1),)), GriddedPerm((0,), ((2, 0),))),
            (GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),),
        ),
    )


@pytest.fixture
def empty_tiling():
    return Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 1))),
            GriddedPerm((1, 0), ((0, 1), (0, 0))),
        ),
        requirements=(
            (GriddedPerm((0,), ((0, 0),)),),
            (GriddedPerm((0,), ((0, 1),)),),
        ),
    )


@pytest.fixture
def finite_tiling():
    return Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 1), (0, 1))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 1, 0), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((3, 2, 1, 0), ((0, 1), (0, 1), (0, 0), (0, 0))),
        ),
        requirements=((GriddedPerm((0,), ((0, 0),)),),),
    )


@pytest.fixture
def factorable_tiling():
    return Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((2, 1, 0), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((2, 0, 1), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm((1, 0, 2), ((5, 4), (5, 4), (5, 4))),
            GriddedPerm((2, 0, 1), ((5, 4), (5, 4), (5, 4))),
            GriddedPerm((1, 2, 0), ((4, 6), (4, 6), (4, 6))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 2))),
            GriddedPerm((0, 1, 2, 3), ((2, 2), (2, 2), (2, 3), (2, 3))),
            GriddedPerm((0, 1), ((6, 4), (6, 4))),
            GriddedPerm((1, 0), ((6, 4), (6, 4))),
            GriddedPerm((0, 1), ((7, 7), (7, 7))),
        ],
        requirements=[
            [
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((4, 6), (4, 6))),
            ],
            [GriddedPerm((0,), ((6, 4),))],
        ],
    )


@pytest.fixture
def obs_inf_til():
    return Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 1), (0, 1))),
            GriddedPerm((1, 0), ((0, 0), (0, 0))),
            GriddedPerm((1, 0), ((0, 1), (0, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 1), (0, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 0), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 0), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 1), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
        ],
        requirements=[[GriddedPerm((1, 0), ((0, 1), (0, 0)))]],
    )


@pytest.fixture
def typical_redundant_obstructions():
    """Returns a very typical list of obstructions clustered together in a
    corner of a tiling."""
    return [
        GriddedPerm((0, 1), ((1, 0), (1, 0))),
        GriddedPerm((0, 1), ((1, 0), (2, 0))),
        GriddedPerm((0, 1), ((1, 0), (3, 0))),
        GriddedPerm((0, 1), ((2, 0), (2, 0))),
        GriddedPerm((0, 1), ((2, 0), (3, 0))),
        GriddedPerm((0, 1), ((3, 1), (3, 1))),
        GriddedPerm((1, 0), ((3, 0), (3, 0))),
        GriddedPerm((1, 0), ((3, 1), (3, 0))),
        GriddedPerm((1, 0), ((3, 1), (3, 1))),
        GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (3, 1))),
        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (3, 0))),
        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (3, 0))),
        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (3, 0))),
        GriddedPerm((3, 2, 1, 0), ((1, 1), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((3, 2, 1, 0), ((2, 1), (2, 1), (3, 0), (3, 0))),
    ]


@pytest.fixture
def typical_redundant_requirements():
    """Returns a very typical list of requirements of a tiling.  """
    return [
        [
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 3))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 4))),
            GriddedPerm((1, 0, 2), ((0, 0), (1, 0), (2, 3))),
            GriddedPerm((1, 0, 2), ((0, 1), (1, 0), (2, 3))),
        ],
        [
            GriddedPerm((0, 1, 2), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
        ],
        [
            GriddedPerm((0, 1), ((1, 0), (3, 0))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((0, 1), ((2, 0), (3, 0))),
            GriddedPerm((0, 1), ((2, 0), (3, 1))),
        ],
        [
            GriddedPerm((1, 0), ((3, 3), (3, 1))),
            GriddedPerm((1, 0), ((3, 1), (3, 1))),
            GriddedPerm((1, 0), ((3, 1), (3, 0))),
        ],
    ]


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_constructor_no_requirements(typical_redundant_obstructions):
    """Tests the constructor of Tiling, thereby the minimization methods used
    in the constructor with different options for remove_empty_rows_and_cols and
    derive_empty. Proper update of the dimensions of the tiling and proper
    computation of empty and active cells.

    Tests without any requirements.
    """
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty_rows_and_cols=False,
        derive_empty=False,
        simplify=False,
    )
    assert len(tiling._obstructions) == 20
    assert len(tiling._requirements) == 0
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 2

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty_rows_and_cols=False,
        derive_empty=False,
        simplify=True,
    )
    assert len(tiling._obstructions) == 18
    assert len(tiling._requirements) == 0
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 2

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty_rows_and_cols=False,
        derive_empty=True,
        simplify=False,
    )

    assert len(tiling._obstructions) == 22
    assert len(tiling._requirements) == 0
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 2
    assert tiling.empty_cells == {(0, 0), (0, 1)}
    assert tiling.active_cells == {(1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1)}

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty_rows_and_cols=False,
        derive_empty=True,
        simplify=True,
    )

    assert len(tiling._obstructions) == 22
    assert len(tiling._requirements) == 0
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 2
    assert tiling.empty_cells == {(0, 0), (0, 1), (1, 1), (2, 1)}
    assert tiling.active_cells == {(1, 0), (2, 0), (3, 0), (3, 1)}

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty_rows_and_cols=True,
        derive_empty=True,
        simplify=False,
    )

    (i, j) = tiling.dimensions
    assert i == 3
    assert j == 2
    assert tiling.empty_cells == set()
    assert tiling.active_cells == {(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)}
    assert len(tiling._obstructions) == 20
    assert len(tiling._requirements) == 0

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty_rows_and_cols=True,
        derive_empty=True,
        simplify=True,
    )

    (i, j) = tiling.dimensions
    assert i == 3
    assert j == 2
    assert tiling.empty_cells == {(0, 1), (1, 1)}
    assert tiling.active_cells == {(0, 0), (1, 0), (2, 0), (2, 1)}
    assert len(tiling._obstructions) == 20
    assert len(tiling._requirements) == 0

    tiling2 = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 1), ((0, 0), (2, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (2, 0))),
            GriddedPerm((0, 1), ((2, 1), (2, 1))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((1, 0), ((2, 1), (2, 0))),
            GriddedPerm((1, 0), ((2, 1), (2, 1))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 1))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (1, 0), (2, 0))),
            GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
        ],
        remove_empty_rows_and_cols=True,
        derive_empty=True,
        simplify=True,
    )

    assert tiling == tiling2


def test_constructor_with_requirements(
    typical_redundant_obstructions, typical_redundant_requirements
):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
        remove_empty_rows_and_cols=False,
        derive_empty=False,
    )
    assert len(tiling._obstructions) == 18
    assert len(tiling._requirements) == 4
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 5

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
        remove_empty_rows_and_cols=False,
        derive_empty=True,
    )

    assert len(tiling._obstructions) == 29
    assert len(tiling._requirements) == 4
    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 5
    assert tiling.empty_cells == {
        (0, 2),
        (0, 3),
        (0, 4),
        (1, 1),
        (1, 2),
        (1, 3),
        (1, 4),
        (2, 1),
        (2, 2),
        (3, 2),
        (3, 4),
    }
    assert tiling.active_cells == {
        (0, 0),
        (0, 1),
        (1, 0),
        (2, 0),
        (2, 3),
        (2, 4),
        (3, 0),
        (3, 1),
        (3, 3),
    }

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
        remove_empty_rows_and_cols=True,
        derive_empty=True,
    )

    (i, j) = tiling.dimensions
    assert i == 4
    assert j == 4
    assert tiling.empty_cells == {
        (0, 2),
        (0, 3),
        (1, 1),
        (1, 2),
        (1, 3),
        (2, 1),
        (3, 3),
    }
    assert tiling.active_cells == {
        (0, 0),
        (0, 1),
        (1, 0),
        (2, 0),
        (2, 2),
        (2, 3),
        (3, 0),
        (3, 1),
        (3, 2),
    }
    assert len(tiling._obstructions) == 25
    assert len(tiling._requirements) == 4

    tiling2 = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=[
            [GriddedPerm((0, 1), [(2, 0), (3, 1)])],
            [GriddedPerm((1, 0), [(3, 2), (3, 1)])],
            [
                GriddedPerm((0, 1, 2), [(0, 0), (1, 0), (2, 2)]),
                GriddedPerm((0, 1, 2), [(0, 0), (1, 0), (2, 3)]),
                GriddedPerm((1, 0, 2), [(0, 0), (1, 0), (2, 2)]),
                GriddedPerm((1, 0, 2), [(0, 1), (1, 0), (2, 2)]),
            ],
            [
                GriddedPerm((0, 1, 2), [(2, 2), (2, 2), (2, 2)]),
                GriddedPerm((1, 0, 2), [(0, 0), (0, 0), (0, 0)]),
            ],
        ],
        remove_empty_rows_and_cols=True,
        derive_empty=True,
    )
    assert tiling == tiling2


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_bytes_noreq(typical_redundant_obstructions):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty_rows_and_cols=False,
        derive_empty=False,
    )

    assert tiling == Tiling.from_bytes(tiling.to_bytes())

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty_rows_and_cols=False,
        derive_empty=True,
    )

    assert tiling == Tiling.from_bytes(tiling.to_bytes())

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        remove_empty_rows_and_cols=True,
        derive_empty=True,
    )
    assert tiling == Tiling.from_bytes(tiling.to_bytes())


def test_from_string():
    string = "123_231_45321"
    assert Tiling.from_string(string) == Tiling(
        [
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((3, 4, 2, 1, 0), ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0))),
        ]
    )
    string = "3201_1032"
    assert Tiling.from_string(string) == Tiling(
        [
            GriddedPerm((3, 2, 0, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((1, 0, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
        ]
    )
    string = "3142"
    assert Tiling.from_string(string) == Tiling(
        [GriddedPerm((2, 0, 3, 1), ((0, 0), (0, 0), (0, 0), (0, 0)))]
    )


def test_from_perms():
    t = Tiling.from_perms(
        [Perm((0, 1, 2)), Perm((0, 2, 1, 3))], [[Perm((0, 1)), Perm((1, 0))]]
    )
    assert t == Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((0, 0),) * 3),
            GriddedPerm((0, 2, 1, 3), ((0, 0),) * 4),
        ],
        requirements=[
            [
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((1, 0), ((0, 0),) * 2),
            ]
        ],
    )


def test_bytes(compresstil):
    assert compresstil == Tiling.from_bytes(compresstil.to_bytes())
    assert compresstil.to_bytes() == compresstil.to_bytes()
    assert (
        compresstil.to_bytes()
        == Tiling(compresstil.obstructions, compresstil.requirements).to_bytes()
    )


def test_json(compresstil):
    assert compresstil == Tiling.from_json(json.dumps(compresstil.to_jsonable()))
    # For backward compatibility make sure we can load from json that don't have
    # the assumptions field
    d = compresstil.to_jsonable()
    d.pop("assumptions")
    assert compresstil == Tiling.from_json(json.dumps(d))


def test_cell_within_bounds(
    typical_redundant_obstructions, typical_redundant_requirements
):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
        remove_empty_rows_and_cols=False,
        derive_empty=False,
    )
    for i in range(4):
        for j in range(5):
            assert tiling.cell_within_bounds((i, j))
    for i in chain(range(-10, 0), range(5, 10)):
        for j in range(-10, 10):
            assert not tiling.cell_within_bounds((i, j))

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
        remove_empty_rows_and_cols=True,
        derive_empty=True,
    )

    for i in range(4):
        for j in range(4):
            assert tiling.cell_within_bounds((i, j))
    for i in chain(range(-10, 0), range(4, 10)):
        for j in range(-10, 10):
            assert not tiling.cell_within_bounds((i, j))


def test_empty_cell(typical_redundant_obstructions, typical_redundant_requirements):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
    )

    tiling1 = tiling.empty_cell((3, 0))
    tiling2 = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (2, 0))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((0, 1), ((3, 1), (3, 1))),
            GriddedPerm((1, 0), ((3, 1), (3, 1))),
            GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
            GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
            GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm((3, 2, 1, 0), ((1, 1), (2, 0), (2, 0), (2, 0))),
        ],
        requirements=[
            [
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 3))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 4))),
                GriddedPerm((1, 0, 2), ((0, 0), (1, 0), (2, 3))),
                GriddedPerm((1, 0, 2), ((0, 1), (1, 0), (2, 3))),
            ],
            [
                GriddedPerm((0, 1, 2), ((2, 3), (2, 3), (2, 3))),
                GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),
            ],
            [
                GriddedPerm((0, 1), ((2, 0), (2, 0))),
                GriddedPerm((0, 1), ((2, 0), (3, 1))),
            ],
            [GriddedPerm((1, 0), ((3, 3), (3, 1)))],
        ],
    )
    assert tiling1 == tiling2


def test_insert_cell(typical_redundant_obstructions, typical_redundant_requirements):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
    )
    assert tiling.insert_cell((3, 1)) == tiling

    assert tiling.insert_cell((1, 1)).obstructions[0] == GriddedPerm(tuple(), [])

    requirements = typical_redundant_requirements + [
        [
            GriddedPerm((0, 1), [(2, 0), (2, 1)]),
            GriddedPerm((0, 1), [(1, 1), (1, 2)]),
        ]
    ]
    tiling = Tiling(
        obstructions=typical_redundant_obstructions, requirements=requirements
    )
    tiling1 = tiling.insert_cell((2, 1))
    assert tiling1 == Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=requirements + [[GriddedPerm((0,), [(2, 1)])]],
    )


def test_add_obstruction(compresstil):
    assert compresstil.add_obstruction(Perm((0, 1)), ((0, 0), (0, 1))) == Tiling(
        obstructions=(
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0, 1), ((0, 0), (0, 1))),
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((1, 0), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((1, 1), (2, 0))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((1, 0, 2), ((0, 1), (0, 0), (1, 1))),
            GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (1, 1))),
            GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 1), (0, 1), (1, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 1), (1, 1))),
            GriddedPerm((2, 0, 1, 3), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((2, 0, 1, 3), ((0, 1), (0, 1), (0, 1), (1, 1))),
        ),
        requirements=(
            (GriddedPerm((0,), ((1, 1),)), GriddedPerm((0,), ((2, 0),))),
            (GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),),
        ),
    )
    assert (
        compresstil.add_obstruction(Perm((1, 0, 2)), ((0, 1), (0, 0), (1, 1)))
        == compresstil
    )


def test_add_list_requirement(finite_tiling):
    list_req = [
        GriddedPerm((1, 0), ((0, 0), (0, 0))),
        GriddedPerm((1, 0), ((0, 1), (0, 1))),
    ]
    assert finite_tiling.add_list_requirement(list_req) == Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 1), (0, 1))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 1, 0), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((3, 2, 1, 0), ((0, 1),) * 2 + ((0, 0),) * 2),
        ),
        requirements=(
            (GriddedPerm((0,), ((0, 0),)),),
            (
                GriddedPerm((1, 0), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((0, 1), (0, 1))),
            ),
        ),
    )


def test_add_requirement(compresstil, factorable_tiling):
    assert compresstil.add_requirement(Perm((1, 0)), ((1, 1), (2, 0))) == Tiling(
        obstructions=(GriddedPerm((), ()),)
    )
    assert factorable_tiling.add_requirement(Perm((0, 1)), ((0, 0), (5, 3))) == Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((2, 1, 0), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((2, 0, 1), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm((1, 0, 2), ((5, 4), (5, 4), (5, 4))),
            GriddedPerm((2, 0, 1), ((5, 4), (5, 4), (5, 4))),
            GriddedPerm((1, 2, 0), ((4, 6), (4, 6), (4, 6))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 2))),
            GriddedPerm((0, 1, 2, 3), ((2, 2), (2, 2), (2, 3), (2, 3))),
            GriddedPerm((0, 1), ((6, 4), (6, 4))),
            GriddedPerm((1, 0), ((6, 4), (6, 4))),
            GriddedPerm((0, 1), ((7, 7), (7, 7))),
        ],
        requirements=[
            [GriddedPerm((0, 1), ((0, 0), (6, 4)))],
            [
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((4, 6), (4, 6))),
            ],
            [GriddedPerm((0,), ((6, 4),))],
        ],
    )


def test_add_single_cell_obstruction(
    typical_redundant_obstructions, typical_redundant_requirements
):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
    )
    assert tiling.add_single_cell_obstruction(Perm((0,)), (0, 2)) == tiling
    assert tiling.add_single_cell_obstruction(Perm((0, 1, 2)), (3, 0)) == tiling
    assert tiling.add_single_cell_obstruction(Perm((2, 1, 0)), (2, 0)) == tiling

    tiling1 = Tiling(
        requirements=typical_redundant_requirements,
        obstructions=[
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (2, 0))),
            GriddedPerm((0, 1), ((1, 0), (3, 0))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((0, 1), ((2, 0), (3, 0))),
            GriddedPerm((0, 1), ((3, 0), (3, 0))),
            GriddedPerm((0, 1), ((3, 1), (3, 1))),
            GriddedPerm((1, 0), ((3, 0), (3, 0))),
            GriddedPerm((1, 0), ((3, 1), (3, 0))),
            GriddedPerm((1, 0), ((3, 1), (3, 1))),
            GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
            GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (3, 0))),
            GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
            GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (3, 0))),
            GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (3, 0))),
            GriddedPerm((3, 2, 1, 0), ((1, 1), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((3, 2, 1, 0), ((2, 1), (2, 1), (3, 0), (3, 0))),
        ],
    )
    assert tiling.add_single_cell_obstruction(Perm((0, 1)), (3, 0)) == tiling1


def test_add_single_cell_requirement(
    typical_redundant_obstructions, typical_redundant_requirements
):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
    )
    assert tiling.add_single_cell_requirement(Perm((0, 1)), (1, 0)).obstructions[
        0
    ] == GriddedPerm(tuple(), [])
    tiling1 = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=[
            [
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 3))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 4))),
                GriddedPerm((1, 0, 2), ((0, 0), (1, 0), (2, 3))),
                GriddedPerm((1, 0, 2), ((0, 1), (1, 0), (2, 3))),
            ],
            [GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0)))],
            [
                GriddedPerm((0, 1), ((1, 0), (3, 0))),
                GriddedPerm((0, 1), ((2, 0), (2, 0))),
                GriddedPerm((0, 1), ((2, 0), (3, 0))),
                GriddedPerm((0, 1), ((2, 0), (3, 1))),
            ],
            [
                GriddedPerm((1, 0), ((3, 3), (3, 1))),
                GriddedPerm((1, 0), ((3, 1), (3, 1))),
                GriddedPerm((1, 0), ((3, 1), (3, 0))),
            ],
        ],
    )
    assert tiling.add_single_cell_requirement(Perm((1, 0, 2)), (0, 0)) == tiling1
    tiling2 = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=(
            typical_redundant_requirements
            + [[GriddedPerm.single_cell((0, 1, 2), (0, 0))]]
        ),
    )
    assert tiling.add_single_cell_requirement(Perm((0, 1, 2)), (0, 0)) == tiling2


@pytest.fixture
def isolated_tiling():
    return Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 2))),
            GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 2), (2, 1))),
            GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 0), (0, 0), (1, 2))),
        ],
        requirements=[
            [
                GriddedPerm((0,), ((2, 1),)),
                GriddedPerm((1, 0), ((1, 2), (1, 2))),
            ],
            [GriddedPerm((1, 2, 0), ((1, 2), (1, 2), (2, 1)))],
        ],
    )


def test_fully_isolated(
    typical_redundant_obstructions, typical_redundant_requirements, isolated_tiling
):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
    )

    assert not tiling.fully_isolated()
    assert isolated_tiling.fully_isolated()


def test_only_positive_in_row_and_col(
    typical_redundant_obstructions, typical_redundant_requirements
):
    tiling = Tiling(requirements=[[GriddedPerm.single_cell((0,), (0, 0))]])
    assert tiling.only_positive_in_row((0, 0))
    assert tiling.only_positive_in_col((0, 0))
    assert tiling.only_positive_in_row_and_col((0, 0))

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=(
            typical_redundant_requirements + [[GriddedPerm.single_cell((0,), (1, 4))]]
        ),
    )
    assert tiling.only_positive_in_row((1, 3))
    assert not tiling.only_positive_in_row((2, 3))
    assert not tiling.only_positive_in_col((2, 3))
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=(
            typical_redundant_requirements + [[GriddedPerm.single_cell((0,), (0, 4))]]
        ),
    )
    assert tiling.only_positive_in_row((0, 3))
    assert tiling.only_positive_in_col((0, 3))
    assert tiling.only_positive_in_row_and_col((0, 3))

    assert tiling.only_positive_in_row((3, 2))
    assert not tiling.only_positive_in_col((3, 2))

    assert not tiling.only_positive_in_col((0, 2))
    assert not tiling.only_positive_in_row((0, 2))


def test_only_cell_in_row_or_col(
    typical_redundant_obstructions, typical_redundant_requirements
):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
    )
    assert tiling.only_cell_in_col((1, 0))
    assert tiling.only_cell_in_row((2, 3))
    assert not tiling.only_cell_in_row((3, 1))
    assert not tiling.only_cell_in_col((3, 1))


def test_cells_in_row_col(
    typical_redundant_obstructions, typical_redundant_requirements
):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
    )

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


def test_cell_basis(factorable_tiling):
    tiling = Tiling(
        obstructions=[
            GriddedPerm((0, 2, 1), [(0, 0), (0, 0), (0, 0)]),
            GriddedPerm((0, 2, 1), [(0, 0), (0, 1), (1, 1)]),
            GriddedPerm((0, 2, 1), [(0, 0), (1, 1), (1, 0)]),
            GriddedPerm((0, 2, 1), [(1, 1), (1, 1), (1, 1)]),
            GriddedPerm((1, 0), [(1, 0), (1, 0)]),
            GriddedPerm((2, 0, 1), [(0, 1), (0, 1), (0, 1)]),
        ]
    )
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
    # Basis for a non active cell
    bdict = factorable_tiling.cell_basis()
    assert bdict[(0, 1)] == ([Perm((0,))], [])
    assert bdict[(5, 3)] == ([Perm((0, 1)), Perm((1, 0))], [Perm((0,))])
    tiling2 = Tiling([], [[GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 1)))]])
    bdict2 = tiling2.cell_basis()
    assert bdict2[(0, 0)] == ([], [Perm((0, 1))])
    assert bdict2[(0, 1)] == ([], [Perm((0,))])
    tiling3 = Tiling(
        [],
        [
            [
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 1))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 1))),
            ]
        ],
    )
    bdict3 = tiling3.cell_basis()
    assert bdict3[(0, 0)] == ([], [Perm((0,))])
    assert bdict3[(0, 1)] == ([], [Perm((0,))])
    # Check that all cell have a basis
    dim = factorable_tiling.dimensions
    for cell in product(range(dim[0]), range(dim[1])):
        assert cell in bdict
        assert len(bdict[cell][0]) >= 1
    assert dim + (1, 0) not in bdict


def test_cell_graph(factorable_tiling, compresstil, typical_redundant_obstructions):
    cell_graph = factorable_tiling.cell_graph()
    assert list(sorted(cell_graph)) == [
        ((0, 0), (1, 0)),
        ((2, 1), (2, 2)),
        ((4, 3), (5, 3)),
    ]
    cell_graph = compresstil.cell_graph()
    assert list(sorted(cell_graph)) == [
        ((0, 0), (0, 1)),
        ((0, 0), (2, 0)),
        ((0, 1), (1, 1)),
    ]
    tiling = Tiling(typical_redundant_obstructions)
    cell_graph = tiling.cell_graph()
    assert list(sorted(cell_graph)) == [
        ((0, 0), (1, 0)),
        ((1, 0), (2, 0)),
        ((2, 0), (2, 1)),
    ]


def test_sort_requirements(typical_redundant_requirements):
    assert Tiling.sort_requirements(typical_redundant_requirements) == (
        (
            GriddedPerm((0, 1), ((1, 0), (3, 0))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((0, 1), ((2, 0), (3, 0))),
            GriddedPerm((0, 1), ((2, 0), (3, 1))),
        ),
        (
            GriddedPerm((1, 0), ((3, 1), (3, 0))),
            GriddedPerm((1, 0), ((3, 1), (3, 1))),
            GriddedPerm((1, 0), ((3, 3), (3, 1))),
        ),
        (
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 3))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 4))),
            GriddedPerm((1, 0, 2), ((0, 0), (1, 0), (2, 3))),
            GriddedPerm((1, 0, 2), ((0, 1), (1, 0), (2, 3))),
        ),
        (
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),
        ),
    )


def test_gridded_perms():
    tiling = Tiling()
    assert len(list(tiling.gridded_perms())) == 1

    tiling = Tiling([GriddedPerm(tuple(), tuple())], [])
    assert len(list(tiling.gridded_perms(maxlen=3))) == 0

    tiling = Tiling(requirements=[[GriddedPerm((0,), [(0, 0)])]])
    assert len(list(tiling.gridded_perms(maxlen=3))) == 9

    tiling = Tiling(requirements=[[GriddedPerm((0, 1), [(0, 0), (1, 0)])]])
    griddable01 = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable01 == sorted(
        [
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((0, 1, 2), [(0, 0), (0, 0), (1, 0)]),
            GriddedPerm((0, 1, 2), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm((0, 2, 1), [(0, 0), (0, 0), (1, 0)]),
            GriddedPerm((0, 2, 1), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm((1, 0, 2), [(0, 0), (0, 0), (1, 0)]),
            GriddedPerm((1, 0, 2), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm((1, 2, 0), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm((2, 0, 1), [(0, 0), (0, 0), (1, 0)]),
        ]
    )

    tiling = Tiling(requirements=[[GriddedPerm((1, 0), [(0, 0), (1, 0)])]])
    griddable10 = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable10 == sorted(
        [
            GriddedPerm((1, 0), [(0, 0), (1, 0)]),
            GriddedPerm((0, 2, 1), [(0, 0), (0, 0), (1, 0)]),
            GriddedPerm((1, 2, 0), [(0, 0), (0, 0), (1, 0)]),
            GriddedPerm((1, 2, 0), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm((2, 1, 0), [(0, 0), (0, 0), (1, 0)]),
            GriddedPerm((2, 1, 0), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm((2, 0, 1), [(0, 0), (0, 0), (1, 0)]),
            GriddedPerm((2, 0, 1), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm((1, 0, 2), [(0, 0), (1, 0), (1, 0)]),
        ]
    )

    tiling = Tiling(requirements=[[GriddedPerm((0, 1), [(0, 0), (0, 1)])]])
    griddable = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable == sorted(
        [
            GriddedPerm((0, 1), [(0, 0), (0, 1)]),
            GriddedPerm((0, 1, 2), [(0, 0), (0, 0), (0, 1)]),
            GriddedPerm((0, 1, 2), [(0, 0), (0, 1), (0, 1)]),
            GriddedPerm((0, 2, 1), [(0, 0), (0, 1), (0, 0)]),
            GriddedPerm((0, 2, 1), [(0, 0), (0, 1), (0, 1)]),
            GriddedPerm((1, 0, 2), [(0, 0), (0, 0), (0, 1)]),
            GriddedPerm((1, 0, 2), [(0, 1), (0, 0), (0, 1)]),
            GriddedPerm((1, 2, 0), [(0, 0), (0, 1), (0, 0)]),
            GriddedPerm((2, 0, 1), [(0, 1), (0, 0), (0, 1)]),
        ]
    )

    tiling = Tiling(
        requirements=[
            [GriddedPerm((0, 1), [(0, 0), (1, 0)])],
            [GriddedPerm((1, 0), [(0, 0), (1, 0)])],
        ]
    )
    griddable = sorted(list(tiling.gridded_perms(maxlen=2)))
    assert len(griddable) == 0
    griddable = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable == sorted(
        [
            GriddedPerm((1, 2, 0), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm((1, 0, 2), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm((0, 2, 1), [(0, 0), (0, 0), (1, 0)]),
            GriddedPerm((2, 0, 1), [(0, 0), (0, 0), (1, 0)]),
        ]
    )

    tiling = Tiling(
        requirements=[
            [
                GriddedPerm((0, 1), [(0, 0), (1, 0)]),
                GriddedPerm((1, 0), [(0, 0), (1, 0)]),
            ]
        ]
    )
    griddable = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable == sorted(list(set(griddable01) | set(griddable10)))

    tiling = Tiling(
        obstructions=[GriddedPerm((1, 0), [(0, 0), (1, 0)])],
        requirements=[[GriddedPerm((0, 1), [(0, 0), (1, 0)])]],
    )
    griddable = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable == sorted(list(set(griddable01) - set(griddable10)))

    tiling = Tiling(
        obstructions=[GriddedPerm((0, 1), [(0, 0), (1, 0)])],
        requirements=[[GriddedPerm((1, 0), [(0, 0), (1, 0)])]],
    )
    griddable = sorted(list(tiling.gridded_perms(maxlen=3)))
    assert griddable == sorted(list(set(griddable10) - set(griddable01)))

    tiling = Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((1, 0), [(0, 0), (1, 0)]),
        ],
        requirements=[
            [GriddedPerm((0,), [(0, 0)])],
            [GriddedPerm((0,), [(1, 0)])],
        ],
    )
    assert len(list(tiling.gridded_perms(maxlen=5))) == 0
    assert tiling.is_empty()

    tiling = Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((1, 0), [(0, 0), (1, 0)]),
        ]
    )
    griddable = sorted(list(tiling.gridded_perms(maxlen=2)))
    assert griddable == [
        GriddedPerm((), []),
        GriddedPerm((0,), [(0, 0)]),
        GriddedPerm((0,), [(1, 0)]),
        GriddedPerm((0, 1), [(0, 0), (0, 0)]),
        GriddedPerm((0, 1), [(1, 0), (1, 0)]),
        GriddedPerm((1, 0), [(0, 0), (0, 0)]),
        GriddedPerm((1, 0), [(1, 0), (1, 0)]),
    ]


@pytest.fixture
def christian_til():
    return Tiling(
        obstructions=[
            GriddedPerm((0, 2, 3, 1), [(0, 0), (1, 1), (1, 1), (2, 0)]),
            GriddedPerm((0, 1), [(1, 0), (1, 0)]),
            GriddedPerm((1, 0), [(1, 0), (1, 0)]),
            GriddedPerm((0, 1), [(2, 1), (2, 1)]),
            GriddedPerm((1, 0), [(2, 1), (2, 1)]),
        ],
        requirements=[
            [
                GriddedPerm((0, 2, 1), [(0, 1), (0, 2), (1, 2)]),
                GriddedPerm((1, 0), [(0, 2), (0, 1)]),
            ],
            [GriddedPerm((0,), [(1, 0)])],
            [GriddedPerm((0,), [(2, 0)])],
            [GriddedPerm((0,), [(2, 1)])],
        ],
    )


def test_symmetries(christian_til):
    rotate90til = Tiling(
        obstructions=[
            GriddedPerm((3, 0, 2, 1), [(0, 2), (0, 0), (1, 1), (1, 1)]),
            GriddedPerm((0, 1), [(0, 1), (0, 1)]),
            GriddedPerm((1, 0), [(0, 1), (0, 1)]),
            GriddedPerm((0, 1), [(1, 0), (1, 0)]),
            GriddedPerm((1, 0), [(1, 0), (1, 0)]),
        ],
        requirements=[
            [
                GriddedPerm((2, 0, 1), [(1, 2), (2, 1), (2, 2)]),
                GriddedPerm((0, 1), [(1, 2), (2, 2)]),
            ],
            [GriddedPerm((0,), [(0, 0)])],
            [GriddedPerm((0,), [(0, 1)])],
            [GriddedPerm((0,), [(1, 0)])],
        ],
    )
    assert christian_til.rotate90() == rotate90til
    assert rotate90til.rotate90().rotate90().rotate90() == christian_til
    assert rotate90til.rotate180().rotate90() == christian_til
    assert rotate90til.rotate270() == christian_til
    assert rotate90til.rotate90() == christian_til.rotate180()
    assert rotate90til.rotate180() == christian_til.rotate270()

    rotate270til = Tiling(
        obstructions=[
            GriddedPerm((2, 1, 3, 0), [(1, 1), (1, 1), (2, 2), (2, 0)]),
            GriddedPerm((0, 1), [(1, 2), (1, 2)]),
            GriddedPerm((1, 0), [(1, 2), (1, 2)]),
            GriddedPerm((0, 1), [(2, 1), (2, 1)]),
            GriddedPerm((1, 0), [(2, 1), (2, 1)]),
        ],
        requirements=[
            [
                GriddedPerm((1, 2, 0), [(0, 0), (0, 1), (1, 0)]),
                GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            ],
            [GriddedPerm((0,), [(1, 2)])],
            [GriddedPerm((0,), [(2, 1)])],
            [GriddedPerm((0,), [(2, 2)])],
        ],
    )
    assert (
        christian_til.rotate90().rotate90().rotate90()
        == christian_til.rotate270()
        == rotate270til
    )

    assert christian_til.rotate180().rotate180() == christian_til

    revtil = Tiling(
        obstructions=[
            GriddedPerm((1, 3, 2, 0), [(0, 0), (1, 1), (1, 1), (2, 0)]),
            GriddedPerm((0, 1), [(0, 1), (0, 1)]),
            GriddedPerm((1, 0), [(0, 1), (0, 1)]),
            GriddedPerm((0, 1), [(1, 0), (1, 0)]),
            GriddedPerm((1, 0), [(1, 0), (1, 0)]),
        ],
        requirements=[
            [
                GriddedPerm((1, 2, 0), [(1, 2), (2, 2), (2, 1)]),
                GriddedPerm((0, 1), [(2, 1), (2, 2)]),
            ],
            [GriddedPerm((0,), [(0, 0)])],
            [GriddedPerm((0,), [(0, 1)])],
            [GriddedPerm((0,), [(1, 0)])],
        ],
    )
    assert christian_til.reverse() == revtil
    assert christian_til.reverse().reverse() == christian_til

    assert christian_til.rotate270().reverse() == christian_til.inverse()
    assert christian_til.reverse().rotate270() == christian_til.antidiagonal()
    assert christian_til.inverse() == christian_til.inverse()

    assert christian_til.rotate180().reverse() == christian_til.complement()
    assert christian_til.rotate90().reverse() == christian_til.antidiagonal()


def test_all_symmetries():
    t = Tiling.from_string("123")
    assert len(t.all_symmetries()) == 2
    t = Tiling.from_string("1")
    assert len(t.all_symmetries()) == 1
    t = Tiling.from_string("1243")
    assert len(t.all_symmetries()) == 4
    t = Tiling.from_string("1342")
    assert len(t.all_symmetries()) == 8


def test_is_empty(compresstil, empty_tiling, finite_tiling):
    assert not compresstil.is_empty()
    assert not finite_tiling.is_empty()
    assert empty_tiling.is_empty()


def test_is_finite(compresstil, empty_tiling, finite_tiling):
    assert not compresstil.is_finite()
    assert finite_tiling.is_finite()


def test_merge(compresstil, finite_tiling, empty_tiling):
    assert finite_tiling.merge() == finite_tiling
    print(compresstil)
    print(compresstil.merge().requirements)
    assert compresstil.merge() == Tiling(
        obstructions=compresstil.obstructions,
        requirements=(
            (
                GriddedPerm((1, 0, 2, 3), ((0, 0), (0, 0), (0, 0), (1, 1))),
                GriddedPerm((1, 0, 2, 3), ((0, 0), (0, 0), (0, 0), (2, 0))),
                GriddedPerm((1, 0, 3, 2), ((0, 0), (0, 0), (0, 0), (2, 0))),
                GriddedPerm((2, 0, 3, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
                GriddedPerm((2, 1, 3, 0), ((0, 0), (0, 0), (0, 0), (2, 0))),
            ),
        ),
    )
    assert empty_tiling.merge() == Tiling([GriddedPerm.empty_perm()])


def test_point_cells(
    compresstil,
    finite_tiling,
    empty_tiling,
    christian_til,
    typical_redundant_obstructions,
    typical_redundant_requirements,
):
    assert Tiling(
        typical_redundant_obstructions, typical_redundant_requirements
    ).point_cells == set([(3, 1)])
    assert compresstil.point_cells == set()
    assert finite_tiling.point_cells == set()
    assert empty_tiling.point_cells == set()
    tiling = compresstil.add_single_cell_requirement(Perm((0,)), (1, 1))
    assert tiling.point_cells == set([(1, 1)])
    tiling = compresstil.add_single_cell_requirement(Perm((0,)), (2, 0))
    assert tiling.point_cells == set([(1, 0)])
    assert christian_til.point_cells == set([(1, 0), (2, 1)])


def test_positive_cells(compresstil, empty_tiling, finite_tiling, christian_til):
    assert compresstil.positive_cells == set([(0, 0)])
    assert finite_tiling.positive_cells == set([(0, 0)])
    assert empty_tiling.positive_cells == set([(0, 0), (0, 1)])
    assert christian_til.positive_cells == set([(1, 0), (0, 2), (0, 1), (2, 0), (2, 1)])


def test_dimensions(compresstil, empty_tiling, finite_tiling, christian_til):
    assert empty_tiling.dimensions == (1, 2)
    assert finite_tiling.dimensions == (1, 2)
    assert compresstil.dimensions == (3, 2)
    assert christian_til.dimensions == (3, 3)


def test_add_obstruction_in_all_ways():
    initial_tiling = Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((0, 3),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0,), ((2, 2),)),
            GriddedPerm((0,), ((2, 3),)),
            GriddedPerm((0,), ((3, 0),)),
            GriddedPerm((0,), ((3, 2),)),
            GriddedPerm((0, 1), ((0, 2), (0, 2))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((1, 0), ((0, 2), (0, 2))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((3, 0, 2, 4, 1), ((1, 3), (1, 3), (1, 3), (1, 3), (1, 3))),
            GriddedPerm((3, 0, 2, 4, 1), ((3, 1), (3, 1), (3, 1), (3, 1), (3, 1))),
            GriddedPerm((3, 0, 2, 4, 1), ((3, 3), (3, 3), (3, 3), (3, 3), (3, 3))),
        ),
        requirements=(
            (GriddedPerm((0,), ((0, 2),)),),
            (GriddedPerm((0,), ((2, 0),)),),
        ),
    )
    final_tiling = Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((0, 3),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0,), ((2, 2),)),
            GriddedPerm((0,), ((2, 3),)),
            GriddedPerm((0,), ((3, 0),)),
            GriddedPerm((0,), ((3, 2),)),
            GriddedPerm((0, 1), ((0, 2), (0, 2))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((1, 0), ((0, 2), (0, 2))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((1, 2, 0), ((3, 1), (3, 3), (3, 1))),
            GriddedPerm((2, 1, 3, 0), ((1, 3), (3, 3), (3, 3), (3, 1))),
            GriddedPerm((2, 1, 3, 0), ((1, 3), (3, 3), (3, 3), (3, 3))),
            GriddedPerm((3, 0, 2, 4, 1), ((1, 3), (1, 3), (1, 3), (1, 3), (1, 3))),
            GriddedPerm((3, 0, 2, 4, 1), ((1, 3), (1, 3), (1, 3), (1, 3), (3, 3))),
            GriddedPerm((3, 0, 2, 4, 1), ((1, 3), (1, 3), (1, 3), (3, 3), (3, 3))),
            GriddedPerm((3, 0, 2, 4, 1), ((3, 1), (3, 1), (3, 1), (3, 1), (3, 1))),
            GriddedPerm((3, 0, 2, 4, 1), ((3, 3), (3, 1), (3, 3), (3, 3), (3, 1))),
            GriddedPerm((3, 0, 2, 4, 1), ((3, 3), (3, 1), (3, 3), (3, 3), (3, 3))),
            GriddedPerm((3, 0, 2, 4, 1), ((3, 3), (3, 3), (3, 3), (3, 3), (3, 3))),
        ),
        requirements=(
            (GriddedPerm((0,), ((0, 2),)),),
            (GriddedPerm((0,), ((2, 0),)),),
        ),
    )
    patt = Perm.to_standard((4, 1, 3, 5, 2))
    assert initial_tiling.add_obstruction_in_all_ways(patt) == final_tiling


def test_sum_decomposition():
    obs = [
        GriddedPerm.single_cell((0, 1), (0, 0)),
        GriddedPerm.single_cell((0, 1), (1, 2)),
        GriddedPerm.single_cell((0, 1), (2, 1)),
        GriddedPerm.single_cell((0, 1), (3, 2)),
        GriddedPerm.single_cell((0, 1), (4, 4)),
        GriddedPerm.single_cell((0, 1), (5, 3)),
    ]
    reqs = []

    t = Tiling(obs, reqs)
    assert t.sum_decomposition() == [
        [(0, 0)],
        [(1, 2), (2, 1), (3, 2)],
        [(4, 4), (5, 3)],
    ]
    assert t.skew_decomposition() == [[(0, 0), (1, 2), (2, 1), (3, 2), (4, 4), (5, 3)]]
    assert len(t.reverse().sum_decomposition()) == 1
    assert len(t.reverse().skew_decomposition()) == 3


def test_is_empty_cell(isolated_tiling):
    assert isolated_tiling.is_empty_cell((0, 1))
    assert not isolated_tiling.is_empty_cell((0, 0))
    assert not isolated_tiling.is_empty_cell((2, 1))


def test_is_monotone_cell(isolated_tiling):
    assert isolated_tiling.is_monotone_cell((0, 0))
    assert isolated_tiling.is_monotone_cell((1, 0))
    assert not isolated_tiling.is_monotone_cell((2, 1))
    t = Tiling.from_string("123")
    assert not t.is_monotone_cell((0, 0))


def test_repr(factorable_tiling, empty_tiling):
    assert factorable_tiling == eval(repr(factorable_tiling))
    assert empty_tiling == eval(repr(empty_tiling))
    assert repr(Tiling()) == "Tiling(obstructions=(), requirements=(), assumptions=())"


def test_initial_conditions(empty_tiling, finite_tiling):
    assert empty_tiling.initial_conditions(4) == [0, 0, 0, 0, 0]
    assert finite_tiling.initial_conditions(6) == [0, 1, 3, 6, 5, 0, 0]
    with_ass = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0),) * 2),
            GriddedPerm((0, 1), ((0, 1),) * 2),
        ],
        assumptions=[TrackingAssumption([GriddedPerm((0,), ((0, 1),))])],
    )
    assert with_ass.initial_conditions(5) == [
        1,
        sympy.sympify("1+k_0"),
        sympy.sympify("1+2*k_0+k_0**2"),
        sympy.sympify("k_0**3 + 3*k_0**2 + 3*k_0 + 1"),
        sympy.sympify("k_0**4 + 4*k_0**3 + 6*k_0**2 + 4*k_0 + 1"),
        sympy.sympify("k_0**5 + 5*k_0**4 + 10*k_0**3 + 10*k_0**2 + 5*k_0 + 1"),
    ]


# ------------------------------------------------------------
# Test for algorithms
# ------------------------------------------------------------


def test_fusion():
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
        ]
    )
    with pytest.raises(AssertionError):
        t.fusion()
    with pytest.raises(AssertionError):
        t.fusion(row=0, col=1)
    with pytest.raises(InvalidOperationError):
        t.fusion(row=1)
    with pytest.raises(InvalidOperationError):
        t.fusion(col=3)
    with pytest.raises(InvalidOperationError):
        t.fusion(col=1)
    assert t.fusion(col=0) == Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
        ]
    )


def test_component_fusion():
    t = Tiling(
        obstructions=[
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0, 1), ((0, 0), (0, 1))),
            GriddedPerm((0, 1), ((0, 0), (0, 2))),
            GriddedPerm((0, 1), ((0, 0), (1, 3))),
            GriddedPerm((0, 1), ((0, 1), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 3))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 3))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (1, 3))),
            GriddedPerm((0, 1, 2), ((0, 2), (0, 2), (0, 3))),
            GriddedPerm((0, 1, 2), ((0, 2), (0, 2), (1, 3))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1), ((1, 3), (1, 3), (1, 3))),
            GriddedPerm((1, 0, 2), ((1, 3), (1, 3), (1, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 3), (0, 3), (1, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 3), (1, 3), (1, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 3), (0, 3), (1, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 3), (1, 3), (1, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 3), (0, 3), (0, 3), (1, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 3), (0, 3), (1, 3), (1, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 3), (0, 3), (1, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 3), (1, 3), (1, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 3), (0, 3), (1, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 3), (1, 3), (1, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 3), (0, 3), (0, 3), (1, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 3), (0, 3), (1, 3), (1, 3))),
        ]
    )
    assert t.component_fusion(row=1) == Tiling(
        obstructions=[
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0, 1), ((0, 0), (0, 1))),
            GriddedPerm((0, 1), ((0, 0), (1, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (1, 2))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1), ((1, 2), (1, 2), (1, 2))),
            GriddedPerm((1, 0, 2), ((1, 2), (1, 2), (1, 2))),
            GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 2), (0, 2), (1, 2))),
            GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 2), (1, 2), (1, 2))),
            GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (0, 2), (1, 2))),
            GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (1, 2), (1, 2))),
            GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 2), (0, 2), (1, 2))),
            GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 2), (1, 2), (1, 2))),
            GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 2), (0, 2), (1, 2))),
            GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 2), (1, 2), (1, 2))),
        ]
    )
    with pytest.raises(AssertionError):
        t.fusion()
    with pytest.raises(AssertionError):
        t.fusion(row=0, col=1)
    with pytest.raises(InvalidOperationError):
        t.fusion(row=5)
    with pytest.raises(InvalidOperationError):
        t.fusion(col=3)
    with pytest.raises(InvalidOperationError):
        t.fusion(col=1)


def test_find_factors(compresstil, factorable_tiling):
    factors = compresstil.find_factors()
    assert len(factors) == 1
    assert factors[0] == compresstil

    factors = factorable_tiling.find_factors(interleaving="none")
    actual_factors = [
        Tiling(
            obstructions=[
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (2, 1))),
                GriddedPerm((2, 0, 1), ((2, 2), (2, 2), (2, 2))),
                GriddedPerm((1, 2, 0), ((3, 3), (3, 3), (3, 3))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 1))),
                GriddedPerm((0, 1, 2, 3), ((2, 1), (2, 1), (2, 2), (2, 2))),
            ],
            requirements=[
                [
                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((3, 3), (3, 3))),
                ]
            ],
        ),
        Tiling(
            obstructions=[
                GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((1, 0), ((1, 0), (1, 0))),
            ],
            requirements=[[GriddedPerm((0,), ((1, 0),))]],
        ),
        Tiling(obstructions=[GriddedPerm((0, 1), ((0, 0), (0, 0)))]),
    ]
    assert len(factors) == len(actual_factors)
    assert all(f in factors for f in actual_factors)

    mon_int_factors = factorable_tiling.find_factors(interleaving="monotone")
    actual_mon_int_factors = [
        Tiling(
            obstructions=[
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (2, 1))),
                GriddedPerm((2, 0, 1), ((2, 2), (2, 2), (2, 2))),
                GriddedPerm((1, 2, 0), ((3, 3), (3, 3), (3, 3))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 1))),
                GriddedPerm((0, 1, 2, 3), ((2, 1), (2, 1), (2, 2), (2, 2))),
            ],
            requirements=[
                [
                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((3, 3), (3, 3))),
                ]
            ],
        ),
        Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((1, 0), ((1, 0), (1, 0))),
            ],
            requirements=[[GriddedPerm((0,), ((1, 0),))]],
        ),
        Tiling(
            obstructions=[
                GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0))),
            ]
        ),
        Tiling(obstructions=[GriddedPerm((0, 1), ((0, 0), (0, 0)))]),
    ]
    assert len(mon_int_factors) == len(actual_mon_int_factors)
    assert all(f in mon_int_factors for f in actual_mon_int_factors)

    int_factors = factorable_tiling.find_factors(interleaving="any")
    actual_int_factors = [
        Tiling(
            obstructions=[
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((2, 1, 0), ((1, 1), (1, 1), (1, 1))),
                GriddedPerm((2, 0, 1), ((1, 2), (1, 2), (1, 2))),
                GriddedPerm((1, 2, 0), ((2, 3), (2, 3), (2, 3))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 1))),
                GriddedPerm((0, 1, 2, 3), ((1, 1), (1, 1), (1, 2), (1, 2))),
            ],
            requirements=[
                [
                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((2, 3), (2, 3))),
                ]
            ],
        ),
        Tiling(obstructions=[GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0)))]),
        Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((1, 0), ((1, 0), (1, 0))),
            ],
            requirements=[[GriddedPerm((0,), ((1, 0),))]],
        ),
        Tiling(
            obstructions=[
                GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0))),
            ]
        ),
        Tiling(obstructions=[GriddedPerm((0, 1), ((0, 0), (0, 0)))]),
    ]
    for f in int_factors:
        print(f)
    print("-" * 50)
    for f in actual_int_factors:
        print(f)
    assert len(int_factors) == len(actual_int_factors)
    assert all(f in int_factors for f in actual_int_factors)

    with pytest.raises(InvalidOperationError):
        factors = compresstil.find_factors(interleaving="magic")


def test_row_and_column_separation():
    separable_t = Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((0, 0),) * 3),
            GriddedPerm((0, 1, 2), ((0, 1),) * 3),
            GriddedPerm((0, 1, 2), ((0, 2),) * 3),
            GriddedPerm((0, 1), ((0, 0), (0, 1))),
            GriddedPerm((0, 1), ((0, 0), (0, 2))),
        ]
    )
    assert separable_t.row_and_column_separation() == Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((1, 0),) * 3),
            GriddedPerm((0, 1, 2), ((0, 1),) * 3),
            GriddedPerm((0, 1, 2), ((0, 2),) * 3),
        ]
    )
    not_sep_t = Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((0, 0),) * 3),
            GriddedPerm((0, 1, 2), ((0, 1),) * 3),
            GriddedPerm((0, 1, 2), ((0, 2),) * 3),
            GriddedPerm((0, 1), ((0, 0), (0, 1))),
            GriddedPerm((0, 1), ((0, 1), (0, 2))),
        ]
    )
    assert not_sep_t.row_and_column_separation() == not_sep_t
    need_two_sep_t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 1),) * 2),
            GriddedPerm((1, 0), ((0, 1), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0),) * 3),
            GriddedPerm((0, 1, 2), ((1, 0),) * 3),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 1), (1, 0))),
        ],
        requirements=[[GriddedPerm((0,), ((0, 1),))]],
    )
    assert need_two_sep_t.row_and_column_separation() == Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((1, 2),) * 2),
            GriddedPerm((0, 1, 2), ((0, 1),) * 3),
            GriddedPerm((0, 1, 2), ((2, 0),) * 3),
        ],
        requirements=[[GriddedPerm((0,), ((1, 2),))]],
    )


def test_obstruction_transitivity():
    t1 = Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((0, 1), [(1, 0), (2, 0)]),
        ],
        requirements=[[GriddedPerm((0,), [(1, 0)])]],
    )
    assert t1.obstruction_transitivity() == Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((0, 1), [(1, 0), (2, 0)]),
            GriddedPerm((0, 1), [(0, 0), (2, 0)]),
        ],
        requirements=[[GriddedPerm((0,), [(1, 0)])]],
    )
    # Tiling with no new obstruction
    t2 = Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (0, 1)]),
            GriddedPerm((0, 1), [(0, 1), (0, 2)]),
        ],
    )
    assert t2.obstruction_transitivity() == t2


def test_subobstruction_inferral(obs_inf_til):
    assert obs_inf_til.subobstruction_inferral() == Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 1), (0, 1))),
            GriddedPerm((1, 0), ((0, 0), (0, 0))),
            GriddedPerm((1, 0), ((0, 1), (0, 1))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 2), (0, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 0), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 0), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 1), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
        ],
        requirements=[[GriddedPerm((1, 0), ((0, 1), (0, 0)))]],
    )


def test_all_obstruction_inferral(obs_inf_til):
    assert obs_inf_til.all_obstruction_inferral(3) == Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 1), (0, 1))),
            GriddedPerm((1, 0), ((0, 0), (0, 0))),
            GriddedPerm((1, 0), ((0, 1), (0, 1))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 2), (0, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 0), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 0), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 1), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
        ],
        requirements=[[GriddedPerm((1, 0), ((0, 1), (0, 0)))]],
    )


def test_empty_cell_inferral():
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((1, 0), (3, 0))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((0, 1), ((2, 0), (3, 0))),
            GriddedPerm((0, 1), ((3, 0), (3, 0))),
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((1, 0), (2, 0))),
            GriddedPerm((1, 0), ((1, 0), (3, 0))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((1, 0), ((2, 0), (3, 0))),
            GriddedPerm((1, 0), ((3, 0), (3, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (3, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
            GriddedPerm((3, 2, 1, 0), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((3, 2, 1, 0), ((0, 0), (0, 0), (0, 0), (1, 0))),
            GriddedPerm((3, 2, 1, 0), ((0, 0), (0, 0), (0, 0), (2, 0))),
            GriddedPerm((3, 2, 1, 0), ((0, 0), (0, 0), (0, 0), (3, 0))),
        ],
        requirements=[[GriddedPerm((0, 1), ((1, 0), (2, 0)))]],
    )
    assert t.empty_cell_inferral() == Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((1, 0), (2, 0))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
            GriddedPerm((3, 2, 1, 0), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((3, 2, 1, 0), ((0, 0), (0, 0), (0, 0), (1, 0))),
            GriddedPerm((3, 2, 1, 0), ((0, 0), (0, 0), (0, 0), (2, 0))),
        ],
        requirements=[[GriddedPerm((0, 1), ((1, 0), (2, 0)))]],
    )


def place_point_in_cell(obs_inf_til):
    assert obs_inf_til.place_point_in_cell((0, 1), 0) == Tiling(
        obstructions=[
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((0, 0), (0, 0))),
            GriddedPerm((1, 0), ((0, 0), (2, 0))),
            GriddedPerm((1, 0), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 2), (2, 0))),
            GriddedPerm((0, 2, 1), ((0, 2), (2, 2), (2, 2))),
            GriddedPerm((0, 2, 1), ((2, 0), (2, 2), (2, 2))),
            GriddedPerm((2, 1, 0), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (2, 2), (2, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (2, 2), (2, 2), (2, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (2, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 0), (0, 2), (2, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (2, 2))),
            GriddedPerm((1, 0, 3, 2), ((2, 2), (2, 2), (2, 2), (2, 2))),
        ],
        requirements=(
            (GriddedPerm((0,), ((1, 1),)),),
            (GriddedPerm((0,), ((2, 0),)),),
        ),
    )


def test_place_point_of_gridded_permutation(obs_inf_til):
    gp = GriddedPerm((1, 0), ((0, 1), (0, 0)))
    assert obs_inf_til.place_point_of_gridded_permutation(gp, 1, 2) == Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((0, 2),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0,), ((1, 3),)),
            GriddedPerm((0,), ((1, 4),)),
            GriddedPerm((0,), ((2, 0),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0, 1), ((0, 3), (0, 3))),
            GriddedPerm((0, 1), ((0, 3), (2, 3))),
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
            GriddedPerm((0, 1), ((2, 3), (2, 3))),
            GriddedPerm((1, 0), ((0, 0), (0, 0))),
            GriddedPerm((1, 0), ((0, 3), (0, 0))),
            GriddedPerm((1, 0), ((0, 3), (0, 3))),
            GriddedPerm((1, 0), ((0, 3), (2, 3))),
            GriddedPerm((1, 0), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((2, 2), (2, 2))),
            GriddedPerm((1, 0), ((2, 3), (2, 3))),
            GriddedPerm((1, 0), ((2, 4), (2, 4))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 4), (0, 3))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 4), (0, 4))),
            GriddedPerm((2, 1, 0), ((2, 4), (2, 3), (2, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 4), (2, 3), (2, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 4), (2, 4), (2, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 4), (2, 4), (2, 3))),
            GriddedPerm((0, 3, 2, 1), ((0, 3), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((0, 3, 2, 1), ((0, 3), (0, 4), (0, 4), (2, 4))),
            GriddedPerm((0, 3, 2, 1), ((0, 4), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((0, 3, 2, 1), ((0, 4), (0, 4), (0, 4), (2, 4))),
            GriddedPerm((1, 0, 3, 2), ((0, 4), (0, 0), (0, 4), (2, 4))),
            GriddedPerm((1, 0, 3, 2), ((0, 4), (0, 3), (0, 4), (0, 4))),
            GriddedPerm((1, 0, 3, 2), ((0, 4), (0, 3), (0, 4), (2, 4))),
            GriddedPerm((1, 0, 3, 2), ((0, 4), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((1, 0, 3, 2), ((0, 4), (0, 4), (0, 4), (2, 4))),
        ),
        requirements=(
            (GriddedPerm((0,), ((0, 3),)),),
            (GriddedPerm((0,), ((1, 1),)),),
        ),
    )


def test_place_row(obs_inf_til):
    assert set(obs_inf_til.place_row(2, 1)) == set(
        [
            Tiling(
                obstructions=(
                    GriddedPerm((0,), ((0, 3),)),
                    GriddedPerm((0,), ((1, 0),)),
                    GriddedPerm((0,), ((1, 1),)),
                    GriddedPerm((0,), ((1, 2),)),
                    GriddedPerm((0,), ((2, 3),)),
                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                    GriddedPerm((0, 1), ((0, 1), (2, 1))),
                    GriddedPerm((0, 1), ((1, 3), (1, 3))),
                    GriddedPerm((0, 1), ((2, 1), (2, 1))),
                    GriddedPerm((1, 0), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((0, 0), (2, 0))),
                    GriddedPerm((1, 0), ((0, 1), (0, 1))),
                    GriddedPerm((1, 0), ((0, 1), (2, 1))),
                    GriddedPerm((1, 0), ((1, 3), (1, 3))),
                    GriddedPerm((1, 0), ((2, 0), (2, 0))),
                    GriddedPerm((1, 0), ((2, 1), (2, 1))),
                    GriddedPerm((0, 2, 1), ((0, 0), (2, 1), (2, 0))),
                    GriddedPerm((0, 2, 1), ((0, 0), (2, 2), (2, 0))),
                    GriddedPerm((0, 2, 1), ((0, 0), (2, 2), (2, 1))),
                    GriddedPerm((0, 2, 1), ((0, 0), (2, 2), (2, 2))),
                    GriddedPerm((0, 2, 1), ((0, 1), (2, 2), (2, 2))),
                    GriddedPerm((0, 2, 1), ((0, 2), (2, 2), (2, 2))),
                    GriddedPerm((1, 0, 2), ((0, 1), (0, 0), (2, 2))),
                    GriddedPerm((1, 0, 2), ((0, 2), (0, 0), (2, 2))),
                    GriddedPerm((1, 0, 2), ((0, 2), (0, 1), (2, 2))),
                    GriddedPerm((1, 0, 2), ((0, 2), (0, 2), (2, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 1), (0, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 1), (2, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 1))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (2, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (2, 1))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (2, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 2), (0, 2), (2, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (2, 2))),
                    GriddedPerm((0, 3, 2, 1), ((2, 0), (2, 2), (2, 1), (2, 0))),
                    GriddedPerm((0, 3, 2, 1), ((2, 0), (2, 2), (2, 2), (2, 0))),
                    GriddedPerm((0, 3, 2, 1), ((2, 0), (2, 2), (2, 2), (2, 1))),
                    GriddedPerm((0, 3, 2, 1), ((2, 0), (2, 2), (2, 2), (2, 2))),
                    GriddedPerm((0, 3, 2, 1), ((2, 1), (2, 2), (2, 2), (2, 2))),
                    GriddedPerm((0, 3, 2, 1), ((2, 2), (2, 2), (2, 2), (2, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 0), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 0), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 1), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((2, 1), (2, 0), (2, 2), (2, 2))),
                    GriddedPerm((1, 0, 3, 2), ((2, 2), (2, 0), (2, 2), (2, 2))),
                    GriddedPerm((1, 0, 3, 2), ((2, 2), (2, 1), (2, 2), (2, 2))),
                    GriddedPerm((1, 0, 3, 2), ((2, 2), (2, 2), (2, 2), (2, 2))),
                ),
                requirements=(
                    (GriddedPerm((0,), ((1, 3),)),),
                    (
                        GriddedPerm((1, 0), ((0, 1), (0, 0))),
                        GriddedPerm((1, 0), ((0, 1), (2, 0))),
                        GriddedPerm((1, 0), ((2, 1), (2, 0))),
                    ),
                ),
            )
        ]
    )


def test_place_col(obs_inf_til):
    assert set(obs_inf_til.place_col(0, 2)) == set(
        [
            Tiling(
                obstructions=(
                    GriddedPerm((0,), ((0, 0),)),
                    GriddedPerm((0,), ((0, 2),)),
                    GriddedPerm((0,), ((1, 1),)),
                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                    GriddedPerm((1, 0), ((0, 1), (0, 1))),
                    GriddedPerm((1, 0), ((1, 0), (1, 0))),
                    GriddedPerm((0, 2, 1), ((1, 0), (1, 2), (1, 2))),
                    GriddedPerm((2, 1, 0), ((1, 2), (1, 2), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((1, 2), (1, 2), (1, 2), (1, 2))),
                ),
                requirements=(
                    (GriddedPerm((0,), ((0, 1),)),),
                    (GriddedPerm((0,), ((1, 0),)),),
                ),
            ),
            Tiling(
                obstructions=(
                    GriddedPerm((0,), ((0, 1),)),
                    GriddedPerm((0,), ((0, 2),)),
                    GriddedPerm((0,), ((0, 3),)),
                    GriddedPerm((0,), ((1, 0),)),
                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                    GriddedPerm((0, 1), ((1, 2), (1, 2))),
                    GriddedPerm((1, 0), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((1, 1), (1, 1))),
                    GriddedPerm((1, 0), ((1, 2), (1, 2))),
                    GriddedPerm((2, 1, 0), ((1, 3), (1, 2), (1, 1))),
                    GriddedPerm((2, 1, 0), ((1, 3), (1, 3), (1, 1))),
                    GriddedPerm((2, 1, 0), ((1, 3), (1, 3), (1, 2))),
                    GriddedPerm((2, 1, 0), ((1, 3), (1, 3), (1, 3))),
                    GriddedPerm((1, 0, 3, 2), ((1, 2), (1, 1), (1, 3), (1, 3))),
                    GriddedPerm((1, 0, 3, 2), ((1, 3), (1, 1), (1, 3), (1, 3))),
                    GriddedPerm((1, 0, 3, 2), ((1, 3), (1, 2), (1, 3), (1, 3))),
                    GriddedPerm((1, 0, 3, 2), ((1, 3), (1, 3), (1, 3), (1, 3))),
                ),
                requirements=(
                    (GriddedPerm((0,), ((0, 0),)),),
                    (GriddedPerm((1, 0), ((1, 2), (1, 1))),),
                ),
            ),
            Tiling(
                obstructions=(
                    GriddedPerm((0,), ((0, 0),)),
                    GriddedPerm((0,), ((0, 1),)),
                    GriddedPerm((0,), ((0, 2),)),
                    GriddedPerm((0,), ((0, 4),)),
                    GriddedPerm((0,), ((1, 3),)),
                    GriddedPerm((0, 1), ((0, 3), (0, 3))),
                    GriddedPerm((0, 1), ((1, 1), (1, 1))),
                    GriddedPerm((1, 0), ((0, 3), (0, 3))),
                    GriddedPerm((1, 0), ((1, 0), (1, 0))),
                    GriddedPerm((1, 0), ((1, 1), (1, 1))),
                    GriddedPerm((0, 2, 1), ((1, 0), (1, 4), (1, 4))),
                    GriddedPerm((0, 2, 1), ((1, 1), (1, 4), (1, 4))),
                    GriddedPerm((0, 2, 1), ((1, 2), (1, 4), (1, 4))),
                    GriddedPerm((2, 1, 0), ((1, 4), (1, 4), (1, 4))),
                    GriddedPerm((0, 3, 2, 1), ((1, 0), (1, 2), (1, 1), (1, 0))),
                    GriddedPerm((0, 3, 2, 1), ((1, 0), (1, 2), (1, 2), (1, 0))),
                    GriddedPerm((0, 3, 2, 1), ((1, 0), (1, 2), (1, 2), (1, 1))),
                    GriddedPerm((0, 3, 2, 1), ((1, 0), (1, 2), (1, 2), (1, 2))),
                    GriddedPerm((0, 3, 2, 1), ((1, 0), (1, 4), (1, 1), (1, 0))),
                    GriddedPerm((0, 3, 2, 1), ((1, 0), (1, 4), (1, 2), (1, 0))),
                    GriddedPerm((0, 3, 2, 1), ((1, 0), (1, 4), (1, 2), (1, 1))),
                    GriddedPerm((0, 3, 2, 1), ((1, 0), (1, 4), (1, 2), (1, 2))),
                    GriddedPerm((0, 3, 2, 1), ((1, 1), (1, 2), (1, 2), (1, 2))),
                    GriddedPerm((0, 3, 2, 1), ((1, 1), (1, 4), (1, 2), (1, 2))),
                    GriddedPerm((0, 3, 2, 1), ((1, 2), (1, 2), (1, 2), (1, 2))),
                    GriddedPerm((0, 3, 2, 1), ((1, 2), (1, 4), (1, 2), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((1, 1), (1, 0), (1, 2), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((1, 1), (1, 0), (1, 4), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((1, 2), (1, 0), (1, 2), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((1, 2), (1, 0), (1, 4), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((1, 2), (1, 1), (1, 2), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((1, 2), (1, 1), (1, 4), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((1, 2), (1, 2), (1, 2), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((1, 2), (1, 2), (1, 4), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((1, 4), (1, 4), (1, 4), (1, 4))),
                ),
                requirements=(
                    (GriddedPerm((0,), ((0, 3),)),),
                    (GriddedPerm((1, 0), ((1, 1), (1, 0))),),
                ),
            ),
        ]
    )


def test_partial_place_point_in_cell(obs_inf_til):
    assert obs_inf_til.partial_place_point_in_cell((0, 0), 0) == Tiling(
        obstructions=(
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0,), ((2, 0),)),
            GriddedPerm((0, 1), ((0, 1), (0, 1))),
            GriddedPerm((0, 1), ((0, 1), (2, 1))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1), ((2, 1), (2, 1))),
            GriddedPerm((1, 0), ((0, 0), (0, 0))),
            GriddedPerm((1, 0), ((0, 0), (1, 0))),
            GriddedPerm((1, 0), ((0, 1), (0, 1))),
            GriddedPerm((1, 0), ((0, 1), (2, 1))),
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((2, 1), (2, 1))),
            GriddedPerm((1, 0), ((2, 2), (2, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 1), (0, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 1), (1, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (1, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (2, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (2, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (2, 2), (2, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 2), (0, 2), (2, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (2, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 0), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 0), (0, 2), (2, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 0), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 0), (0, 2), (2, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 1), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 1), (0, 2), (2, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (2, 2))),
        ),
        requirements=(
            (GriddedPerm((0,), ((0, 1),)),),
            (GriddedPerm((0,), ((1, 0),)),),
        ),
    )


def test_partial_place_point_of_gridded_permutation(obs_inf_til):
    gp = GriddedPerm((1, 0), ((0, 1), (0, 0)))
    placed = obs_inf_til.partial_place_point_of_gridded_permutation(gp, 1, 1)
    assert placed == Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 1), (0, 1))),
            GriddedPerm((0, 1), ((0, 3), (0, 3))),
            GriddedPerm((1, 0), ((0, 0), (0, 0))),
            GriddedPerm((1, 0), ((0, 1), (0, 0))),
            GriddedPerm((1, 0), ((0, 1), (0, 1))),
            GriddedPerm((1, 0), ((0, 2), (0, 0))),
            GriddedPerm((1, 0), ((0, 2), (0, 1))),
            GriddedPerm((1, 0), ((0, 2), (0, 2))),
            GriddedPerm((1, 0), ((0, 3), (0, 2))),
            GriddedPerm((1, 0), ((0, 3), (0, 3))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 4), (0, 3), (0, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 4), (0, 3), (0, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 4), (0, 4), (0, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 4), (0, 4), (0, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 4), (0, 4), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 4), (0, 4), (0, 3))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 4), (0, 4), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 4), (0, 4), (0, 3))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 4), (0, 4), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 4), (0, 4), (0, 3))),
            GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((0, 3, 2, 1), ((0, 3), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((0, 3, 2, 1), ((0, 4), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((1, 0, 3, 2), ((0, 3), (0, 0), (0, 4), (0, 4))),
            GriddedPerm((1, 0, 3, 2), ((0, 3), (0, 1), (0, 4), (0, 4))),
            GriddedPerm((1, 0, 3, 2), ((0, 4), (0, 0), (0, 4), (0, 4))),
            GriddedPerm((1, 0, 3, 2), ((0, 4), (0, 1), (0, 4), (0, 4))),
            GriddedPerm((1, 0, 3, 2), ((0, 4), (0, 2), (0, 4), (0, 4))),
            GriddedPerm((1, 0, 3, 2), ((0, 4), (0, 3), (0, 4), (0, 4))),
            GriddedPerm((1, 0, 3, 2), ((0, 4), (0, 4), (0, 4), (0, 4))),
        ),
        requirements=((GriddedPerm((1, 0), ((0, 3), (0, 1))),),),
    )


def test_partial_place_row(obs_inf_til):
    assert set(obs_inf_til.partial_place_row(2, 3)) == set(
        [
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                    GriddedPerm((0, 1), ((0, 2), (0, 2))),
                    GriddedPerm((1, 0), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((0, 1), (0, 1))),
                    GriddedPerm((1, 0), ((0, 2), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 1), (0, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 3), (0, 1), (0, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 3), (0, 2), (0, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 3), (0, 2), (0, 1))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 3), (0, 3), (0, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 3), (0, 3), (0, 1))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 3), (0, 3), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 3), (0, 3), (0, 3))),
                    GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 3), (0, 3), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 3), (0, 3), (0, 3))),
                    GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 3), (0, 3), (0, 3))),
                    GriddedPerm((0, 3, 2, 1), ((0, 3), (0, 3), (0, 3), (0, 3))),
                    GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 0), (0, 3), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 0), (0, 3), (0, 3))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 0), (0, 3), (0, 3))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 1), (0, 3), (0, 3))),
                    GriddedPerm((1, 0, 3, 2), ((0, 3), (0, 0), (0, 3), (0, 3))),
                    GriddedPerm((1, 0, 3, 2), ((0, 3), (0, 1), (0, 3), (0, 3))),
                    GriddedPerm((1, 0, 3, 2), ((0, 3), (0, 2), (0, 3), (0, 3))),
                    GriddedPerm((1, 0, 3, 2), ((0, 3), (0, 3), (0, 3), (0, 3))),
                ),
                requirements=(
                    (GriddedPerm((0,), ((0, 2),)),),
                    (GriddedPerm((1, 0), ((0, 1), (0, 0))),),
                ),
            )
        ]
    )


def test_partial_place_col(obs_inf_til):
    assert set(obs_inf_til.partial_place_col(0, 0)) == set(
        [
            Tiling(
                obstructions=(
                    GriddedPerm((0,), ((1, 0),)),
                    GriddedPerm((0,), ((1, 2),)),
                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                    GriddedPerm((0, 1), ((0, 1), (1, 1))),
                    GriddedPerm((0, 1), ((1, 1), (1, 1))),
                    GriddedPerm((1, 0), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((0, 1), (0, 1))),
                    GriddedPerm((1, 0), ((0, 1), (1, 1))),
                    GriddedPerm((1, 0), ((1, 1), (1, 1))),
                    GriddedPerm((0, 2, 1), ((0, 0), (0, 2), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 1), (0, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 1), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
                ),
                requirements=(
                    (GriddedPerm((0,), ((1, 1),)),),
                    (GriddedPerm((1, 0), ((0, 1), (0, 0))),),
                ),
            ),
            Tiling(
                obstructions=(
                    GriddedPerm((0,), ((1, 1),)),
                    GriddedPerm((0,), ((1, 2),)),
                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                    GriddedPerm((1, 0), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((0, 0), (1, 0))),
                    GriddedPerm((1, 0), ((0, 1), (0, 1))),
                    GriddedPerm((1, 0), ((1, 0), (1, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 1), (0, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 1), (1, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 1))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (1, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 0), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 0), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 1), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
                ),
                requirements=(
                    (GriddedPerm((0,), ((0, 1),)),),
                    (GriddedPerm((0,), ((1, 0),)),),
                ),
            ),
            Tiling(
                obstructions=(
                    GriddedPerm((0,), ((1, 0),)),
                    GriddedPerm((0,), ((1, 1),)),
                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                    GriddedPerm((0, 1), ((1, 2), (1, 2))),
                    GriddedPerm((1, 0), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((0, 1), (0, 1))),
                    GriddedPerm((1, 0), ((1, 2), (1, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 1), (0, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 1))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 2), (0, 2), (1, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 2), (0, 2), (1, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 0), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 0), (0, 2), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 0), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 0), (0, 2), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 1), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 1), (0, 2), (1, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (1, 2))),
                ),
                requirements=(
                    (GriddedPerm((0,), ((1, 2),)),),
                    (GriddedPerm((1, 0), ((0, 1), (0, 0))),),
                ),
            ),
        ]
    )


def test_empty_obstruction():
    t = Tiling((GriddedPerm.empty_perm(),))
    assert t.forward_cell_map == {}
    assert t.obstructions == (GriddedPerm.empty_perm(),)


def test_point_obstruction():
    t = Tiling((GriddedPerm((0,), ((0, 0),)),))
    assert t.forward_cell_map == {}
    assert t.obstructions == (GriddedPerm((0,), ((0, 0),)),)


class TestGetGenf:
    """
    Group all the test regarding getting the generating function for a tiling.
    """

    def test_empty_tiling(self):
        t = Tiling(
            [GriddedPerm((0, 1), [(0, 0), (0, 0)])],
            [[GriddedPerm((0, 1), [(0, 0), (0, 0)])]],
        )
        assert t.get_genf() == sympy.sympify("0")

    def test_monotone_cell(self):
        t = Tiling([GriddedPerm((0, 1), ((0, 0), (0, 0)))])
        assert sympy.simplify(t.get_genf() - sympy.sympify("1/(1-x)")) == 0

    def test_with_req(self):
        t = Tiling(
            [GriddedPerm((0, 1), ((0, 0), (0, 0)))],
            [[GriddedPerm((0,), ((0, 0),))]],
        )
        assert sympy.simplify(t.get_genf() - sympy.sympify("x/(1-x)")) == 0

    def test_adjacent_monotone(self):
        t = Tiling(
            [
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
            ]
        )
        assert sympy.simplify(t.get_genf() - sympy.sympify("1/(1-2*x)")) == 0

    def test_with_list_req(self):
        t = Tiling(
            [
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((1, 1), (1, 1))),
            ],
            [
                [GriddedPerm((0,), ((1, 1),))],
                [GriddedPerm((0,), ((0, 0),))],
            ],
        )
        assert sympy.simplify(t.get_genf() - sympy.sympify("(x/(1-x))**2")) == 0

    def test_locally_factorable(self):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0), (1, 1))),
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((0, 1),) * 2),
                GriddedPerm((0, 1), ((1, 1),) * 2),
            ]
        )
        assert (
            sympy.simplify(t.get_genf() - sympy.sympify("1 / (2*x**2 - 3*x + 1)")) == 0
        )

    def test_not_enumerable(self):
        t = Tiling.from_string("1324")
        with pytest.raises(NotImplementedError):
            t.get_genf()


def test_enmerate_gp_up_to():
    assert (
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 2), (1, 2))),
                GriddedPerm((1, 0), ((1, 2), (1, 2))),
                GriddedPerm((0, 2, 1), ((0, 1), (0, 1), (0, 1))),
                GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),
            ),
            requirements=((GriddedPerm((0,), ((1, 2),)),),),
            assumptions=(),
        ).enmerate_gp_up_to(8)
        == [0, 1, 2, 5, 14, 42, 132, 429, 1430]
    )


def test_column_reverse():
    assert Tiling(
        obstructions=(
            GriddedPerm((0, 3, 1, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 2), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((1, 1), (1, 1))),
        ),
        requirements=(
            (GriddedPerm((0,), ((1, 1),)),),
            (GriddedPerm((1, 0), ((0, 2), (0, 0))),),
        ),
        assumptions=(),
    ).column_reverse(0) == Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((1, 1), (1, 1))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 2), (0, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 1, 3, 0), ((0, 2), (0, 2), (0, 2), (0, 2))),
        ),
        requirements=(
            (GriddedPerm((0,), ((1, 1),)),),
            (GriddedPerm((0, 1), ((0, 0), (0, 2))),),
        ),
        assumptions=(),
    )
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 1), (0, 1))),
            GriddedPerm((0, 1), ((1, 2), (1, 2))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((1, 0), ((0, 1), (0, 1))),
            GriddedPerm((1, 0), ((1, 2), (1, 2))),
            GriddedPerm((1, 0), ((1, 2), (2, 0))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((1, 2, 0), ((0, 1), (0, 2), (2, 0))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (2, 0))),
            GriddedPerm((2, 0, 1), ((0, 2), (0, 1), (0, 2))),
            GriddedPerm((2, 0, 1), ((0, 2), (0, 1), (1, 2))),
            GriddedPerm((2, 0, 1), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((2, 0, 1), ((0, 2), (0, 2), (1, 2))),
        ),
        requirements=(
            (GriddedPerm((0,), ((0, 1),)),),
            (GriddedPerm((0,), ((1, 2),)), GriddedPerm((0,), ((2, 0),))),
        ),
        assumptions=(),
    )
    assert (
        Counter(len(gp) for gp in t.gridded_perms(7))
        == Counter(len(gp) for gp in t.column_reverse(0).gridded_perms(7))
        == Counter(len(gp) for gp in t.column_reverse(1).gridded_perms(7))
        == Counter(len(gp) for gp in t.column_reverse(2).gridded_perms(7))
    )


def test_row_complement():
    assert Tiling(
        obstructions=(
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (1, 1))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
        ),
        requirements=((GriddedPerm((2, 1, 0), ((1, 1), (1, 0), (1, 0))),),),
        assumptions=(),
    ).row_complement(0) == Tiling(
        obstructions=(
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (1, 1))),
            GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 0, 1), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
        ),
        requirements=((GriddedPerm((2, 0, 1), ((1, 1), (1, 0), (1, 0))),),),
        assumptions=(),
    )
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 1), (0, 1))),
            GriddedPerm((0, 1), ((1, 2), (1, 2))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((1, 0), ((0, 1), (0, 1))),
            GriddedPerm((1, 0), ((1, 2), (1, 2))),
            GriddedPerm((1, 0), ((1, 2), (2, 0))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((1, 2, 0), ((0, 1), (0, 2), (2, 0))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (2, 0))),
            GriddedPerm((2, 0, 1), ((0, 2), (0, 1), (0, 2))),
            GriddedPerm((2, 0, 1), ((0, 2), (0, 1), (1, 2))),
            GriddedPerm((2, 0, 1), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((2, 0, 1), ((0, 2), (0, 2), (1, 2))),
        ),
        requirements=(
            (GriddedPerm((0,), ((0, 1),)),),
            (GriddedPerm((0,), ((1, 2),)), GriddedPerm((0,), ((2, 0),))),
        ),
        assumptions=(),
    )
    assert (
        Counter(len(gp) for gp in t.gridded_perms(7))
        == Counter(len(gp) for gp in t.row_complement(0).gridded_perms(7))
        == Counter(len(gp) for gp in t.row_complement(1).gridded_perms(7))
        == Counter(len(gp) for gp in t.row_complement(2).gridded_perms(7))
    )


def test_permute_columns():
    assert Tiling(
        obstructions=(
            GriddedPerm((1, 0), ((1, 1), (2, 0))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 1))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 0, 1, 3), ((0, 1), (0, 1), (0, 1), (1, 2))),
        ),
        requirements=((GriddedPerm((1, 0), ((0, 2), (0, 0))),),),
        assumptions=(),
    ).permute_columns((2, 0, 1)) == Tiling(
        obstructions=(
            GriddedPerm((1, 0), ((0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 1))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 1), (1, 1))),
            GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1), ((0, 0), (2, 1))),
            GriddedPerm((2, 0, 1, 3), ((1, 1), (1, 1), (1, 1), (2, 2))),
        ),
        requirements=((GriddedPerm((1, 0), ((1, 2), (1, 0))),),),
        assumptions=(),
    )


def test_permute_rows():
    assert Tiling(
        obstructions=(
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((2, 0, 1), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 2), (1, 1))),
            GriddedPerm((0, 2, 1), ((0, 0), (1, 2), (1, 0))),
            GriddedPerm((0, 2, 1), ((1, 1), (1, 2), (1, 1))),
        ),
        requirements=(),
        assumptions=(),
    ).permute_rows((1, 2, 0)) == Tiling(
        obstructions=(
            GriddedPerm((1, 0), ((1, 2), (1, 2))),
            GriddedPerm((0, 2, 1), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 1, 0), ((0, 2), (0, 1), (1, 0))),
            GriddedPerm((1, 0, 2), ((0, 2), (1, 1), (1, 2))),
            GriddedPerm((0, 2, 1), ((1, 0), (1, 1), (1, 0))),
        ),
        requirements=(),
        assumptions=(),
    )


def test_apply_perm_map_to_cell():
    assert Tiling(
        obstructions=(
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((2, 1), (2, 1))),
            GriddedPerm((0, 2, 1), ((0, 2), (2, 2), (2, 2))),
            GriddedPerm((0, 2, 1), ((2, 1), (2, 2), (2, 2))),
            GriddedPerm((2, 1, 0), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 2, 1), ((0, 2), (0, 2), (0, 2), (2, 2))),
            GriddedPerm((0, 3, 2, 1), ((1, 0), (2, 2), (2, 2), (2, 1))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (2, 2))),
            GriddedPerm((1, 0, 3, 2), ((2, 2), (2, 2), (2, 2), (2, 2))),
        ),
        requirements=((GriddedPerm((0,), ((2, 1),)),),),
        assumptions=(),
    ).apply_perm_map_to_cell(lambda p: p.complement(), (0, 2)) == Tiling(
        obstructions=(
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((2, 1), (2, 1))),
            GriddedPerm((0, 2, 1), ((0, 2), (2, 2), (2, 2))),
            GriddedPerm((0, 2, 1), ((2, 1), (2, 2), (2, 2))),
            GriddedPerm((2, 1, 0), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((0, 3, 2, 1), ((1, 0), (2, 2), (2, 2), (2, 1))),
            GriddedPerm((1, 0, 3, 2), ((2, 2), (2, 2), (2, 2), (2, 2))),
            GriddedPerm((1, 3, 0, 2), ((0, 2), (0, 2), (0, 2), (2, 2))),
            GriddedPerm(
                Perm((0, 3, 2, 1)).complement(), ((0, 2), (0, 2), (0, 2), (0, 2))
            ),
            GriddedPerm(
                Perm((1, 0, 3, 2)).complement(), ((0, 2), (0, 2), (0, 2), (0, 2))
            ),
            GriddedPerm((3, 0, 2, 1), ((0, 2), (0, 2), (0, 2), (2, 2))),
        ),
        requirements=((GriddedPerm((0,), ((2, 1),)),),),
        assumptions=(),
    )


def test_contains_all_patterns_locally_for_crossing():
    t = Tiling(obstructions=(), requirements=(), assumptions=())
    assert t.contains_all_patterns_locally_for_crossing((0, 0))
    t = Tiling(
        obstructions=(GriddedPerm((0,), ((0, 0),)),),
        requirements=(),
        assumptions=(),
    )
    assert t.contains_all_patterns_locally_for_crossing((0, 0))
    t = Tiling(
        obstructions=(GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),),
        requirements=(),
        assumptions=(),
    )
    assert all(t.contains_all_patterns_locally_for_crossing((i, 0)) for i in range(3))
    t = Tiling(
        obstructions=(GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (1, 0), (2, 0))),),
        requirements=(),
        assumptions=(),
    )
    assert not t.contains_all_patterns_locally_for_crossing((1, 0))
    assert all(t.contains_all_patterns_locally_for_crossing((i, 0)) for i in (0, 2))
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 2, 1, 3), ((0, 0), (1, 0), (1, 0), (2, 0))),
        ),
        requirements=(),
        assumptions=(),
    )
    assert all(t.contains_all_patterns_locally_for_crossing((i, 0)) for i in range(3))
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1, 2, 4, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 1, 4, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 4, 1, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
        ),
        requirements=(),
        assumptions=(),
    )
    assert not t.contains_all_patterns_locally_for_crossing((1, 0))
    assert all(t.contains_all_patterns_locally_for_crossing((i, 0)) for i in (0, 2))
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1, 2, 4, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 1, 4, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 4, 1, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 4, 2, 1, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
        ),
        requirements=(),
        assumptions=(),
    )
    assert all(t.contains_all_patterns_locally_for_crossing((i, 0)) for i in range(3))
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1, 2, 4, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 1, 4, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 4, 1, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 4, 2, 1, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm(
                (0, 1, 2, 3, 4, 5), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0), (2, 0))
            ),
        ),
        requirements=(),
        assumptions=(),
    )
    assert t.contains_all_patterns_locally_for_crossing((0, 0))
    assert not any(t.contains_all_patterns_locally_for_crossing((i, 0)) for i in (1, 2))
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1, 2, 4, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 1, 4, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 4, 1, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 4, 2, 1, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm(
                (0, 3, 1, 2, 4, 6, 7),
                ((0, 0), (0, 0), (1, 0), (1, 0), (2, 0), (2, 0), (2, 0)),
            ),
            GriddedPerm(
                (0, 3, 2, 1, 4, 6, 7),
                ((0, 0), (0, 0), (1, 0), (1, 0), (2, 0), (2, 0), (2, 0)),
            ),
        ),
        requirements=(),
        assumptions=(),
    )
    assert t.contains_all_patterns_locally_for_crossing((1, 0))
    assert not any(t.contains_all_patterns_locally_for_crossing((i, 0)) for i in (0, 2))
    t = Tiling(
        obstructions=(GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),),
        requirements=((GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (1, 0))),),),
        assumptions=(),
    )
    assert not t.contains_all_patterns_locally_for_crossing((1, 0))
    assert all(t.contains_all_patterns_locally_for_crossing((i, 0)) for i in (0, 2))
    t = Tiling(
        obstructions=(GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (1, 0))),),
        requirements=((GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),),),
        assumptions=(),
    )
    assert not t.contains_all_patterns_locally_for_crossing((1, 0))
    assert all(t.contains_all_patterns_locally_for_crossing((i, 0)) for i in (0, 2))
    t = Tiling(
        obstructions=(GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (2, 0))),),
        requirements=(
            (
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (1, 0))),
            ),
        ),
        assumptions=(),
    )
    assert all(t.contains_all_patterns_locally_for_crossing((i, 0)) for i in range(3))


@pytest.mark.slow
def test_generate_known_equinumerous_tilings():
    check_up_to = 5
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((1, 0, 2), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((2, 1, 0, 3), ((0, 0), (1, 0), (1, 0), (2, 0))),
            GriddedPerm((2, 0, 1, 3), ((0, 0), (1, 0), (1, 0), (2, 0))),
        ),
        requirements=(),
    )
    expected = t.enmerate_gp_up_to(check_up_to)
    assert all(
        til.enmerate_gp_up_to(check_up_to) == expected
        for til in t.generate_known_equinumerous_tilings()
    )

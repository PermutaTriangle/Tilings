import pytest

from permuta import Perm
from tilings import Obstruction, Requirement, Tiling


@pytest.fixture
def simple_trans_row():
    return Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
        ],
        requirements=[[Requirement(Perm((0,)), [(1, 0)])]],
    )


@pytest.fixture
def simple_trans_col():
    return Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (0, 1)]),
            Obstruction(Perm((0, 1)), [(0, 1), (0, 2)]),
        ],
        requirements=[[Requirement(Perm((0,)), [(0, 1)])]],
    )


@pytest.fixture
def simple_trans_row_len2():
    return Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
            Obstruction(Perm((0, 1)), [(2, 0), (3, 0)]),
        ],
        requirements=[
            [Requirement(Perm((0,)), [(1, 0)])],
            [Requirement(Perm((0,)), [(2, 0)])],
        ],
    )


@pytest.fixture
def simple_trans_row_len3():
    return Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
            Obstruction(Perm((0, 1)), [(2, 0), (3, 0)]),
            Obstruction(Perm((0, 1)), [(3, 0), (4, 0)]),
        ],
        requirements=[
            [Requirement(Perm((0,)), [(1, 0)])],
            [Requirement(Perm((0,)), [(2, 0)])],
            [Requirement(Perm((0,)), [(3, 0)])],
        ],
    )

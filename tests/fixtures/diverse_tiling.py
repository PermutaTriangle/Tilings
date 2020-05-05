import pytest

from permuta import Perm
from tilings import GriddedPerm, Requirement, Tiling


@pytest.fixture
def diverse_tiling():
    """Returns a simple, but diverse tiling.

    The tiling has positive, possibly empty and empty cells and also few
    requirements and a long obstructions."""
    return Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 2, 3, 1)), [(0, 0), (1, 1), (1, 1), (2, 0)]),
            GriddedPerm(Perm((0, 1)), [(1, 0), (1, 0)]),
            GriddedPerm(Perm((1, 0)), [(1, 0), (1, 0)]),
            GriddedPerm(Perm((0, 1)), [(2, 1), (2, 1)]),
            GriddedPerm(Perm((1, 0)), [(2, 1), (2, 1)]),
        ],
        requirements=[
            [
                Requirement(Perm((0, 2, 1)), [(0, 1), (0, 2), (1, 2)]),
                Requirement(Perm((1, 0)), [(0, 2), (0, 1)]),
            ],
            [Requirement(Perm((0,)), [(1, 0)])],
            [Requirement(Perm((0,)), [(2, 0)])],
            [Requirement(Perm((0,)), [(2, 1)])],
        ],
    )

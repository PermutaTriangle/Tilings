import pytest

from permuta import Perm
from tilings import GriddedPerm, Tiling


@pytest.fixture
def no_point_tiling():
    """Returns a simple tiling with length of all obs and reqs at least 2. """
    return Tiling(
        obstructions=[
            GriddedPerm(Perm((1, 0)), [(0, 1), (0, 1)]),
            GriddedPerm(Perm((0, 1, 2)), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm(Perm((0, 1, 2)), [(1, 0), (1, 0), (2, 0)]),
            GriddedPerm(Perm((0, 2, 1)), [(0, 2), (0, 2), (1, 2)]),
            GriddedPerm(Perm((0, 2, 1)), [(0, 2), (1, 2), (1, 2)]),
        ],
        requirements=[
            [
                GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)]),
                GriddedPerm(Perm((0, 1)), [(0, 0), (2, 0)]),
            ],
            [GriddedPerm(Perm((0, 2, 1)), [(0, 1), (1, 1), (1, 1)])],
            [
                GriddedPerm(Perm((0, 1)), [(1, 1), (2, 1)]),
                GriddedPerm(Perm((0, 1)), [(1, 1), (2, 2)]),
            ],
        ],
    )

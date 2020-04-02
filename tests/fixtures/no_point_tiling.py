import pytest

from permuta import Perm
from tilings import Obstruction, Requirement, Tiling


@pytest.fixture
def no_point_tiling():
    """Returns a simple tiling with length of all obs and reqs at least 2. """
    return Tiling(
        obstructions=[
            Obstruction(Perm((1, 0)), [(0, 1), (0, 1)]),
            Obstruction(Perm((0, 1, 2)), [(0, 0), (1, 0), (1, 0)]),
            Obstruction(Perm((0, 1, 2)), [(1, 0), (1, 0), (2, 0)]),
            Obstruction(Perm((0, 2, 1)), [(0, 2), (0, 2), (1, 2)]),
            Obstruction(Perm((0, 2, 1)), [(0, 2), (1, 2), (1, 2)]),
        ],
        requirements=[
            [
                Requirement(Perm((0, 1)), [(0, 0), (0, 0)]),
                Requirement(Perm((0, 1)), [(0, 0), (2, 0)]),
            ],
            [Requirement(Perm((0, 2, 1)), [(0, 1), (1, 1), (1, 1)])],
            [
                Requirement(Perm((0, 1)), [(1, 1), (2, 1)]),
                Requirement(Perm((0, 1)), [(1, 1), (2, 2)]),
            ],
        ],
    )

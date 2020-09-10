import pytest

from tilings import GriddedPerm, Tiling


@pytest.fixture
def no_point_tiling():
    """Returns a simple tiling with length of all obs and reqs at least 2. """
    return Tiling(
        obstructions=[
            GriddedPerm((1, 0), [(0, 1), (0, 1)]),
            GriddedPerm((0, 1, 2), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm((0, 1, 2), [(1, 0), (1, 0), (2, 0)]),
            GriddedPerm((0, 2, 1), [(0, 2), (0, 2), (1, 2)]),
            GriddedPerm((0, 2, 1), [(0, 2), (1, 2), (1, 2)]),
        ],
        requirements=[
            [
                GriddedPerm((0, 1), [(0, 0), (0, 0)]),
                GriddedPerm((0, 1), [(0, 0), (2, 0)]),
            ],
            [GriddedPerm((0, 2, 1), [(0, 1), (1, 1), (1, 1)])],
            [
                GriddedPerm((0, 1), [(1, 1), (2, 1)]),
                GriddedPerm((0, 1), [(1, 1), (2, 2)]),
            ],
        ],
    )

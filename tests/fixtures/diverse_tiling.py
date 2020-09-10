import pytest

from tilings import GriddedPerm, Tiling


@pytest.fixture
def diverse_tiling():
    """Returns a simple, but diverse tiling.

    The tiling has positive, possibly empty and empty cells and also few
    requirements and a long obstructions."""
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

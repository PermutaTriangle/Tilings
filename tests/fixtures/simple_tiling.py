import pytest

from tilings import GriddedPerm, Tiling


@pytest.fixture
def simple_tiling():
    return Tiling(
        obstructions=[GriddedPerm((1, 0), [(0, 1), (1, 0)])],
        requirements=[
            [
                GriddedPerm((0, 1), [(0, 0), (1, 0)]),
                GriddedPerm((0, 1), [(0, 0), (1, 1)]),
            ]
        ],
    )

import pytest

from permuta import Perm
from tilings import GriddedPerm, Tiling


@pytest.fixture
def simple_tiling():
    return Tiling(
        obstructions=[GriddedPerm(Perm((1, 0)), [(0, 1), (1, 0)])],
        requirements=[
            [
                GriddedPerm(Perm((0, 1)), [(0, 0), (1, 0)]),
                GriddedPerm(Perm((0, 1)), [(0, 0), (1, 1)]),
            ]
        ],
    )

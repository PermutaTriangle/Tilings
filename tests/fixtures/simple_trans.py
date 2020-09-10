import pytest

from tilings import GriddedPerm, Tiling


@pytest.fixture
def simple_trans_row():
    return Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((0, 1), [(1, 0), (2, 0)]),
        ],
        requirements=[[GriddedPerm((0,), [(1, 0)])]],
    )


@pytest.fixture
def simple_trans_col():
    return Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (0, 1)]),
            GriddedPerm((0, 1), [(0, 1), (0, 2)]),
        ],
        requirements=[[GriddedPerm((0,), [(0, 1)])]],
    )


@pytest.fixture
def simple_trans_row_len2():
    return Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((0, 1), [(1, 0), (2, 0)]),
            GriddedPerm((0, 1), [(2, 0), (3, 0)]),
        ],
        requirements=[
            [GriddedPerm((0,), [(1, 0)])],
            [GriddedPerm((0,), [(2, 0)])],
        ],
    )


@pytest.fixture
def simple_trans_row_len3():
    return Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((0, 1), [(1, 0), (2, 0)]),
            GriddedPerm((0, 1), [(2, 0), (3, 0)]),
            GriddedPerm((0, 1), [(3, 0), (4, 0)]),
        ],
        requirements=[
            [GriddedPerm((0,), [(1, 0)])],
            [GriddedPerm((0,), [(2, 0)])],
            [GriddedPerm((0,), [(3, 0)])],
        ],
    )

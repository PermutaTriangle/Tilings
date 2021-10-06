import pytest

from tilings import GriddedPerm, Tiling
from tilings.map import RowColMap


@pytest.fixture
def double_row_map():
    return RowColMap(row_map={0: 0, 1: 0}, col_map={0: 0})


@pytest.fixture
def double_col_map():
    return RowColMap(col_map={0: 0, 1: 0}, row_map={0: 0})


@pytest.fixture
def double_all_map():
    return RowColMap(col_map={0: 0, 1: 0}, row_map={0: 0, 1: 0})


def test_preimage_row(double_row_map, double_col_map, double_all_map):
    assert sorted(double_row_map.preimage_row(0)) == [0, 1]
    assert sorted(double_col_map.preimage_row(0)) == [0]
    assert sorted(double_all_map.preimage_row(0)) == [0, 1]


def test_preimage_col(double_row_map, double_col_map, double_all_map):
    assert sorted(double_row_map.preimage_col(0)) == [0]
    assert sorted(double_col_map.preimage_col(0)) == [0, 1]
    assert sorted(double_all_map.preimage_col(0)) == [0, 1]


def test_preimage_cell(double_row_map, double_col_map, double_all_map):
    assert sorted(double_row_map.preimage_cell((0, 0))) == [(0, 0), (0, 1)]
    assert sorted(double_col_map.preimage_cell((0, 0))) == [(0, 0), (1, 0)]
    assert sorted(double_all_map.preimage_cell((0, 0))) == [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ]


def test_preimage_gp(double_all_map):
    assert sorted(double_all_map.preimage_gp(GriddedPerm((0,), ((0, 0),)))) == [
        GriddedPerm((0,), ((0, 0),)),
        GriddedPerm((0,), ((0, 1),)),
        GriddedPerm((0,), ((1, 0),)),
        GriddedPerm((0,), ((1, 1),)),
    ]
    assert sorted(double_all_map.preimage_gp(GriddedPerm((0, 1), ((0, 0),) * 2))) == [
        GriddedPerm((0, 1), ((0, 0), (0, 0))),
        GriddedPerm((0, 1), ((0, 0), (0, 1))),
        GriddedPerm((0, 1), ((0, 0), (1, 0))),
        GriddedPerm((0, 1), ((0, 0), (1, 1))),
        GriddedPerm((0, 1), ((0, 1), (0, 1))),
        GriddedPerm((0, 1), ((0, 1), (1, 1))),
        GriddedPerm((0, 1), ((1, 0), (1, 0))),
        GriddedPerm((0, 1), ((1, 0), (1, 1))),
        GriddedPerm((0, 1), ((1, 1), (1, 1))),
    ]


def test_preimage_tiling(double_row_map, double_col_map, double_all_map):
    t1 = Tiling(
        obstructions=[
            GriddedPerm((0, 2, 1), ((0, 0),) * 3),
        ],
        requirements=[[GriddedPerm((0,), ((0, 0),))]],
    )
    assert double_row_map.preimage_tiling(t1) == Tiling(
        [
            GriddedPerm((0, 2, 1), [(0, 0), (0, 0), (0, 0)]),
            GriddedPerm((0, 2, 1), [(0, 0), (0, 1), (0, 0)]),
            GriddedPerm((0, 2, 1), [(0, 0), (0, 1), (0, 1)]),
            GriddedPerm((0, 2, 1), [(0, 1), (0, 1), (0, 1)]),
        ],
        [[GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((0, 1),))]],
    )
    assert double_col_map.preimage_tiling(t1) == Tiling(
        [
            GriddedPerm((0, 2, 1), [(0, 0), (0, 0), (0, 0)]),
            GriddedPerm((0, 2, 1), [(0, 0), (0, 0), (1, 0)]),
            GriddedPerm((0, 2, 1), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm((0, 2, 1), [(1, 0), (1, 0), (1, 0)]),
        ],
        [[GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))]],
    )
    t2 = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0),) * 2),
        ],
        requirements=[[GriddedPerm((0,), ((0, 0),))]],
    )
    assert double_all_map.preimage_tiling(t2) == Tiling(
        [
            GriddedPerm((0, 1), [(0, 0), (0, 0)]),
            GriddedPerm((0, 1), [(0, 0), (0, 1)]),
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((0, 1), [(0, 0), (1, 1)]),
            GriddedPerm((0, 1), [(0, 1), (0, 1)]),
            GriddedPerm((0, 1), [(0, 1), (1, 1)]),
            GriddedPerm((0, 1), [(1, 0), (1, 0)]),
            GriddedPerm((0, 1), [(1, 0), (1, 1)]),
            GriddedPerm((0, 1), [(1, 1), (1, 1)]),
        ],
        [
            [
                GriddedPerm.point_perm((0, 0)),
                GriddedPerm.point_perm((1, 0)),
                GriddedPerm.point_perm((0, 1)),
                GriddedPerm.point_perm((1, 1)),
            ]
        ],
    )

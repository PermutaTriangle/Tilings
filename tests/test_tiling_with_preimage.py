import pytest

from tilings import GriddedPerm, Tiling
from tilings.map import RowColMap
from tilings.parameter_counter import ParameterCounter, PreimageCounter


@pytest.fixture
def normal_fusion_tiling():
    preimage_t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
        ),
    )
    preimage_map = RowColMap(col_map={0: 0, 1: 0, 2: 1}, row_map={0: 0})
    param = ParameterCounter([PreimageCounter(preimage_t, preimage_map)])

    return Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
        ),
        parameters=[param],
    )


def test_insert_point_obs(normal_fusion_tiling):
    # Insert in cell with one preimage
    preimage_t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
        ),
    )
    preimage_map = RowColMap(col_map={0: 0, 1: 0}, row_map={0: 0})
    param = ParameterCounter([PreimageCounter(preimage_t, preimage_map)])
    assert normal_fusion_tiling.empty_cell((1, 0)) == Tiling(
        [GriddedPerm.single_cell((0, 1), (0, 0))], parameters=[param]
    )

    # Insert in cell with two preimages
    preimage_t = Tiling.from_string("123")
    preimage_map = RowColMap.identity((1, 1))
    param = ParameterCounter([PreimageCounter(preimage_t, preimage_map)])
    assert normal_fusion_tiling.empty_cell((0, 0)) == Tiling(
        [GriddedPerm.single_cell((0, 1, 2), (0, 0))], parameters=[param]
    )


def test_insert_point_req(normal_fusion_tiling):
    # Insert in cell with one preimage
    preimage_t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
        ),
        requirements=[[GriddedPerm((0,), ((2, 0),))]],
    )
    preimage_map = RowColMap(col_map={0: 0, 1: 0, 2: 1}, row_map={0: 0})
    param = ParameterCounter([PreimageCounter(preimage_t, preimage_map)])
    t = (
        normal_fusion_tiling.remove_parameters()
        .insert_cell((1, 0))
        .add_parameter(param)
    )
    assert t == normal_fusion_tiling.insert_cell((1, 0))
    # Insert in cell with two preimages
    preimage_t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
        ),
        requirements=[[GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))]],
    )
    preimage_map = RowColMap(col_map={0: 0, 1: 0, 2: 1}, row_map={0: 0})
    param = ParameterCounter([PreimageCounter(preimage_t, preimage_map)])
    t = (
        normal_fusion_tiling.remove_parameters()
        .insert_cell((0, 0))
        .add_parameter(param)
    )
    assert t == normal_fusion_tiling.insert_cell((0, 0))


def test_insert_point_req_tiling_with_req(normal_fusion_tiling):
    # insert in cell with one preimage
    t_base = normal_fusion_tiling.insert_cell((0, 0))
    preimage_t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
        ),
        requirements=[
            [GriddedPerm((0,), ((2, 0),))],
            [GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))],
        ],
    )
    preimage_map = RowColMap(col_map={0: 0, 1: 0, 2: 1}, row_map={0: 0})
    param = ParameterCounter([PreimageCounter(preimage_t, preimage_map)])
    t_expected = t_base.remove_parameters().insert_cell((1, 0)).add_parameter(param)
    assert t_expected == t_base.insert_cell((1, 0))

    # insert in cell with two preimages
    t_base = normal_fusion_tiling.insert_cell((1, 0))
    assert t_expected == t_base.insert_cell((0, 0))


def test_tiling_is_empty_perm_tiling():
    tiling = Tiling(
        obstructions=(GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),),
        requirements=(),
        parameters=[
            ParameterCounter(
                [
                    PreimageCounter(
                        Tiling(
                            obstructions=(
                                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                                GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 1))),
                                GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 1))),
                            ),
                            requirements=(),
                            parameters=(),
                        ),
                        RowColMap({0: 0, 1: 0}, {0: 0}),
                    )
                ]
            )
        ],
    )
    empty_cell = tiling.empty_cell((0, 0))
    assert empty_cell.get_terms(0) == {(1,): 1}
    for i in range(1, 4):
        assert empty_cell.get_terms(i) == {}

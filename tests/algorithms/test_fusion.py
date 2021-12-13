import pytest

from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Fusion
from tilings.assumptions import TrackingAssumption

pytestmark = pytest.mark.xfail


class ComponentFusion:
    # delete me please
    pass


class TestFusion:
    @pytest.fixture
    def small_tiling(self):
        t = Tiling(
            obstructions=[
                GriddedPerm((1, 0), ((0, 1), (1, 1))),
                GriddedPerm((1, 0), ((0, 1), (0, 1))),
                GriddedPerm((1, 0), ((0, 1), (1, 0))),
                GriddedPerm((1, 0), ((0, 1), (0, 0))),
                GriddedPerm((1, 0), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((0, 0), (1, 0))),
                GriddedPerm((1, 0), ((1, 0), (1, 0))),
                GriddedPerm((1, 0), ((1, 1), (1, 0))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
            ]
        )
        return t

    @pytest.fixture
    def tiling_with_req(self):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((0, 0), (1, 0))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((2, 0),) * 3),
            ],
            requirements=[
                [
                    GriddedPerm((0, 1), ((0, 0), (2, 0))),
                    GriddedPerm((0, 1), ((1, 0), (2, 0))),
                ],
                [GriddedPerm((1, 0), ((2, 0), (2, 0)))],
            ],
        )
        return t

    @pytest.fixture
    def big_tiling(self):
        """The original tiling from Jay's idea"""
        t = Tiling(
            obstructions=(
                GriddedPerm((0,), ((0, 1),)),
                GriddedPerm((0,), ((0, 2),)),
                GriddedPerm((0,), ((0, 3),)),
                GriddedPerm((0,), ((1, 2),)),
                GriddedPerm((0,), ((1, 3),)),
                GriddedPerm((1, 0), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((0, 0), (1, 0))),
                GriddedPerm((1, 0), ((0, 0), (2, 0))),
                GriddedPerm((1, 0), ((1, 0), (1, 0))),
                GriddedPerm((1, 0), ((1, 0), (2, 0))),
                GriddedPerm((1, 0), ((1, 1), (1, 0))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
                GriddedPerm((1, 0), ((1, 1), (2, 0))),
                GriddedPerm((1, 0), ((1, 1), (2, 1))),
                GriddedPerm((1, 0), ((2, 0), (2, 0))),
                GriddedPerm((1, 0), ((2, 1), (2, 0))),
                GriddedPerm((1, 0), ((2, 1), (2, 1))),
                GriddedPerm((1, 0), ((2, 2), (2, 0))),
                GriddedPerm((1, 0), ((2, 2), (2, 1))),
                GriddedPerm((1, 0), ((2, 2), (2, 2))),
                GriddedPerm((2, 1, 0), ((2, 3), (2, 3), (2, 0))),
                GriddedPerm((2, 1, 0), ((2, 3), (2, 3), (2, 1))),
                GriddedPerm((2, 1, 0), ((2, 3), (2, 3), (2, 2))),
                GriddedPerm((2, 1, 0), ((2, 3), (2, 3), (2, 3))),
            ),
            requirements=(),
        )
        return t

    @pytest.fixture
    def row_fusion(self, small_tiling):
        return Fusion(small_tiling, row_idx=0)

    @pytest.fixture
    def col_fusion(self, small_tiling):
        return Fusion(small_tiling, col_idx=0)

    @pytest.fixture
    def fusion_with_req(self, tiling_with_req):
        return Fusion(tiling_with_req, col_idx=0)

    @pytest.fixture
    def gp1(self):
        return GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 1)))

    @pytest.fixture
    def gp2(self):
        return GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0)))

    @pytest.fixture
    def col_fusion_big(self, big_tiling):
        return Fusion(big_tiling, col_idx=0)

    def test_init(self, small_tiling):
        Fusion(small_tiling, row_idx=0)
        Fusion(small_tiling, col_idx=0)
        with pytest.raises(RuntimeError):
            Fusion(small_tiling, row_idx=0, col_idx=1)

    def test_fuse_gridded_perm(self, row_fusion, col_fusion, gp1):
        assert row_fusion.fuse_gridded_perm(gp1) == GriddedPerm(
            (0, 1, 2), ((0, 0), (1, 0), (1, 0))
        )
        assert col_fusion.fuse_gridded_perm(gp1) == GriddedPerm(
            (0, 1, 2), ((0, 0), (0, 0), (0, 1))
        )

    def test_unfuse_gridded_perm(self):
        rf0 = Fusion(Tiling(), row_idx=0)
        rf1 = Fusion(Tiling(), row_idx=1)
        cf0 = Fusion(Tiling(), col_idx=0)
        ob1 = GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 1), (0, 1), (0, 2)))
        assert list(rf1.unfuse_gridded_perm(ob1)) == [
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 2), (0, 2), (0, 3))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 1), (0, 2), (0, 3))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 1), (0, 1), (0, 3))),
        ]
        ob2 = GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 1), (0, 1), (0, 2)))
        assert list(rf1.unfuse_gridded_perm(ob2)) == [
            GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 2), (0, 2), (0, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 2), (0, 1), (0, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 1), (0, 1), (0, 3))),
        ]
        ob3 = GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 1), (0, 1), (0, 2), (0, 1)))
        assert list(rf1.unfuse_gridded_perm(ob3)) == [
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 2), (0, 2), (0, 3), (0, 2))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 2), (0, 1), (0, 3), (0, 2))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 1), (0, 1), (0, 3), (0, 2))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 1), (0, 1), (0, 3), (0, 1))),
        ]
        ob4 = GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 1), (1, 1), (1, 0)))
        assert list(rf0.unfuse_gridded_perm(ob4)) == [
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 2), (1, 2), (1, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 2), (1, 2), (1, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 2), (1, 2), (1, 0))),
        ]
        assert list(cf0.unfuse_gridded_perm(ob4)) == [
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 1), (2, 1), (2, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (1, 1), (2, 1), (2, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 1), (2, 1), (2, 0))),
        ]
        # Unfuse column
        ob5 = GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0)))
        assert list(cf0.unfuse_gridded_perm(ob5)) == [
            GriddedPerm((2, 0, 1), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((2, 0, 1), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0))),
        ]
        # Unfuse pattern with no point in the fuse region
        ob6 = GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0)))
        assert list(cf0.unfuse_gridded_perm(ob6)) == [
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
        ]
        ob6 = GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (1, 0)))
        assert list(cf0.unfuse_gridded_perm(ob6)) == [
            GriddedPerm((1, 0, 2), ((1, 0), (1, 0), (2, 0))),
            GriddedPerm((1, 0, 2), ((0, 0), (1, 0), (2, 0))),
            GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (2, 0))),
        ]

    def test_fuse_counter(self, row_fusion, col_fusion, gp1, gp2):
        assert row_fusion._fuse_counter([gp1, gp2]) == {
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))): 2
        }
        assert col_fusion._fuse_counter([gp1, gp2]) == {
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 1))): 1,
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))): 1,
        }

    def test_obstruction_fuse_counter(self, row_fusion, col_fusion, col_fusion_big):
        assert row_fusion.obstruction_fuse_counter == {
            GriddedPerm((1, 0), ((0, 0), (0, 0))): 3,
            GriddedPerm((1, 0), ((0, 0), (1, 0))): 3,
            GriddedPerm((1, 0), ((1, 0), (1, 0))): 3,
        }
        assert col_fusion.obstruction_fuse_counter == {
            GriddedPerm((1, 0), ((0, 0), (0, 0))): 3,
            GriddedPerm((1, 0), ((0, 1), (0, 0))): 3,
            GriddedPerm((1, 0), ((0, 1), (0, 1))): 3,
        }
        assert col_fusion_big.obstruction_fuse_counter == {
            GriddedPerm((0,), ((0, 1),)): 1,
            GriddedPerm((0,), ((0, 2),)): 2,
            GriddedPerm((0,), ((0, 3),)): 2,
            GriddedPerm((1, 0), ((0, 0), (0, 0))): 3,
            GriddedPerm((1, 0), ((0, 1), (0, 1))): 1,
            GriddedPerm((1, 0), ((0, 1), (0, 0))): 1,
            GriddedPerm((1, 0), ((0, 0), (1, 0))): 2,
            GriddedPerm((1, 0), ((0, 1), (1, 0))): 1,
            GriddedPerm((1, 0), ((0, 1), (1, 1))): 1,
            GriddedPerm((1, 0), ((1, 0), (1, 0))): 1,
            GriddedPerm((1, 0), ((1, 1), (1, 0))): 1,
            GriddedPerm((1, 0), ((1, 1), (1, 1))): 1,
            GriddedPerm((1, 0), ((1, 2), (1, 0))): 1,
            GriddedPerm((1, 0), ((1, 2), (1, 1))): 1,
            GriddedPerm((1, 0), ((1, 2), (1, 2))): 1,
            GriddedPerm((2, 1, 0), ((1, 3), (1, 3), (1, 0))): 1,
            GriddedPerm((2, 1, 0), ((1, 3), (1, 3), (1, 1))): 1,
            GriddedPerm((2, 1, 0), ((1, 3), (1, 3), (1, 2))): 1,
            GriddedPerm((2, 1, 0), ((1, 3), (1, 3), (1, 3))): 1,
        }

    def test_requirements_fuse_counters(self, row_fusion, fusion_with_req):
        assert row_fusion.requirements_fuse_counters == []
        print(fusion_with_req._tiling)
        assert fusion_with_req.requirements_fuse_counters == [
            {GriddedPerm((0, 1), ((0, 0), (1, 0))): 2},
            {GriddedPerm((1, 0), ((1, 0), (1, 0))): 1},
        ]

    def test_can_fuse_set_of_gridded_perms(
        self, row_fusion, col_fusion, col_fusion_big
    ):
        counter = row_fusion.obstruction_fuse_counter
        assert row_fusion._can_fuse_set_of_gridded_perms(counter)
        counter = col_fusion.obstruction_fuse_counter
        assert col_fusion._can_fuse_set_of_gridded_perms(counter)
        counter = col_fusion_big.obstruction_fuse_counter
        assert not col_fusion_big._can_fuse_set_of_gridded_perms(counter)

    def test_is_valid_count(self, row_fusion):
        assert row_fusion._is_valid_count(3, GriddedPerm((1, 0), ((0, 0), (0, 0))))
        assert row_fusion._is_valid_count(3, GriddedPerm((1, 0), ((0, 0), (1, 0))))
        assert row_fusion._is_valid_count(2, GriddedPerm((1, 0), ((1, 1), (1, 0))))
        assert not row_fusion._is_valid_count(1, GriddedPerm((1, 0), ((1, 0), (1, 0))))

    def test_point_in_fuse_region(self, row_fusion, col_fusion_big, gp1, gp2):
        assert row_fusion._point_in_fuse_region(gp1) == 2
        assert row_fusion._point_in_fuse_region(gp2) == 3
        assert col_fusion_big._point_in_fuse_region(gp1) == 1
        assert col_fusion_big._point_in_fuse_region(gp2) == 1

    def test_fusable(self, row_fusion, col_fusion, col_fusion_big, fusion_with_req):
        assert row_fusion.fusable()
        assert col_fusion.fusable()
        assert fusion_with_req.fusable()
        assert not col_fusion_big.fusable()
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
            ]
        )
        assert not Fusion(t, row_idx=0).fusable()

    def test_fused_tiling(
        self, row_fusion, col_fusion, col_fusion_big, fusion_with_req
    ):
        assert row_fusion.fused_tiling() == Tiling(
            obstructions=[
                GriddedPerm((1, 0), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((0, 0), (1, 0))),
                GriddedPerm((1, 0), ((1, 0), (1, 0))),
            ]
        )
        assert col_fusion.fused_tiling() == Tiling(
            obstructions=[
                GriddedPerm((1, 0), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((0, 1), (0, 0))),
                GriddedPerm((1, 0), ((0, 1), (0, 1))),
            ]
        )
        # We can get the fused tiling even for not fusable tilings
        assert col_fusion_big.fused_tiling() == Tiling(
            obstructions=[
                GriddedPerm((0,), ((0, 1),)),
                GriddedPerm((0,), ((0, 2),)),
                GriddedPerm((0,), ((0, 3),)),
                GriddedPerm((1, 0), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((0, 1), (0, 1))),
                GriddedPerm((1, 0), ((0, 1), (0, 0))),
                GriddedPerm((1, 0), ((0, 0), (1, 0))),
                GriddedPerm((1, 0), ((0, 1), (1, 0))),
                GriddedPerm((1, 0), ((0, 1), (1, 1))),
                GriddedPerm((1, 0), ((1, 0), (1, 0))),
                GriddedPerm((1, 0), ((1, 1), (1, 0))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
                GriddedPerm((1, 0), ((1, 2), (1, 0))),
                GriddedPerm((1, 0), ((1, 2), (1, 1))),
                GriddedPerm((1, 0), ((1, 2), (1, 2))),
                GriddedPerm((2, 1, 0), ((1, 3), (1, 3), (1, 0))),
                GriddedPerm((2, 1, 0), ((1, 3), (1, 3), (1, 1))),
                GriddedPerm((2, 1, 0), ((1, 3), (1, 3), (1, 2))),
                GriddedPerm((2, 1, 0), ((1, 3), (1, 3), (1, 3))),
            ]
        )
        assert fusion_with_req.fused_tiling() == Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((1, 0),) * 3),
            ],
            requirements=[
                [GriddedPerm((0, 1), ((0, 0), (1, 0)))],
                [GriddedPerm((1, 0), ((1, 0), (1, 0)))],
            ],
        )

    def test_positive_fusion(self):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1), [(0, 0), (0, 0)]),
                GriddedPerm((0, 1), [(0, 0), (1, 0)]),
                GriddedPerm((0, 1), [(1, 0), (1, 0)]),
            ],
            requirements=[[GriddedPerm((0,), [(0, 0)])]],
        )
        algo = Fusion(t, col_idx=0)
        assert algo.min_left_right_points() == (1, 0)


@pytest.mark.xfail
class TestComponentFusion(TestFusion):
    @pytest.fixture
    def col_tiling(self):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 2, 1), ((0, 0),) * 3),
                GriddedPerm((0, 2, 1), ((1, 0),) * 3),
                GriddedPerm((0, 1), ((0, 0), (1, 0))),
            ]
        )
        return t

    @pytest.fixture
    def col_fusion(self, col_tiling):
        return ComponentFusion(col_tiling, col_idx=0)

    @pytest.fixture
    def tiling_with_req(self, col_tiling):
        return col_tiling.insert_cell((0, 0))

    @pytest.fixture
    def row_tiling(self):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1, 2), ((0, 0),) * 3),
                GriddedPerm((0, 1, 2), ((0, 1),) * 3),
                GriddedPerm((0, 1, 2), ((0, 2),) * 3),
                GriddedPerm((0, 1), ((1, 2),) * 2),
                GriddedPerm((0, 1), ((0, 0), (0, 1))),
                GriddedPerm((0, 1), ((0, 0), (0, 2))),
                GriddedPerm((0, 1), ((0, 1), (0, 2))),
                GriddedPerm((2, 0, 1), ((0, 2), (0, 0), (1, 2))),
                GriddedPerm((2, 0, 1), ((0, 2), (0, 1), (1, 2))),
            ]
        )
        return t

    @pytest.fixture
    def row_fusion(self, row_tiling):
        return ComponentFusion(row_tiling, row_idx=0)

    @pytest.fixture
    def not_prechecked_fusion(self, row_tiling):
        t = row_tiling.add_single_cell_obstruction(Perm((0, 2, 1)), (0, 0))
        return ComponentFusion(t, row_idx=0)

    def test_init(self, col_tiling, tiling_with_req, row_tiling):
        ComponentFusion(col_tiling, col_idx=0)
        ComponentFusion(row_tiling, row_idx=0)
        with pytest.raises(RuntimeError):
            ComponentFusion(col_tiling, row_idx=0, col_idx=1)
        with pytest.raises(RuntimeError):
            ComponentFusion(tiling_with_req, col_idx=0)

    def test_pre_check(self, col_fusion, row_fusion, not_prechecked_fusion):
        assert col_fusion._pre_check()
        assert row_fusion._pre_check()
        assert not not_prechecked_fusion._pre_check()

    def test_first_cell(self, col_fusion, row_fusion, not_prechecked_fusion):
        assert col_fusion.first_cell == (0, 0)
        assert row_fusion.first_cell == (0, 0)
        with pytest.raises(RuntimeError):
            not_prechecked_fusion.first_cell

    def test_second_cell(self, col_fusion, row_fusion, not_prechecked_fusion):
        assert col_fusion.second_cell == (1, 0)
        assert row_fusion.second_cell == (0, 1)
        with pytest.raises(RuntimeError):
            not_prechecked_fusion.second_cell

    def test_pre_check_long_row(self):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((1, 0),) * 2),
                GriddedPerm((0, 1), ((0, 1),) * 2),
                GriddedPerm((0, 1), ((0, 0), (1, 0))),
                GriddedPerm((0, 1), ((0, 0), (0, 1))),
            ]
        )
        assert not ComponentFusion(t, row_idx=0)._pre_check()
        assert not ComponentFusion(t, col_idx=0)._pre_check()

    def test_pre_check_not_adjacent(self):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((1, 1),) * 2),
            ]
        )
        assert not ComponentFusion(t, row_idx=0)._pre_check()
        assert not ComponentFusion(t, col_idx=0)._pre_check()

    def test_pre_check_diff_basis(self):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1, 2), ((0, 0),) * 3),
                GriddedPerm((0, 1), ((0, 1),) * 2),
            ]
        )
        assert not ComponentFusion(t, row_idx=0)._pre_check()

    def test_has_crosssing_len2_ob(self, row_fusion, col_fusion):
        assert row_fusion.has_crossing_len2_ob()
        assert col_fusion.has_crossing_len2_ob()
        t1 = Tiling(
            obstructions=[
                GriddedPerm((0, 2, 1), ((0, 0),) * 3),
                GriddedPerm((0, 2, 1), ((1, 0),) * 3),
                GriddedPerm((1, 0), ((0, 0), (1, 0))),
            ]
        )
        assert ComponentFusion(t1, col_idx=0).has_crossing_len2_ob()
        t2 = Tiling(
            obstructions=[
                GriddedPerm((0, 1, 2), ((0, 0),) * 3),
                GriddedPerm((0, 1, 2), ((0, 1),) * 3),
                GriddedPerm((0, 1, 2), ((0, 2),) * 3),
                GriddedPerm((0, 1), ((1, 2),) * 2),
                GriddedPerm((1, 0), ((0, 1), (0, 0))),
                GriddedPerm((0, 1), ((0, 0), (0, 2))),
                GriddedPerm((0, 1), ((0, 1), (0, 2))),
                GriddedPerm((2, 0, 1), ((0, 2), (0, 0), (1, 2))),
                GriddedPerm((2, 0, 1), ((0, 2), (0, 1), (1, 2))),
            ]
        )
        # Tiling with no crossing length 2 obstruction.
        assert ComponentFusion(t2, row_idx=0).has_crossing_len2_ob()
        t3 = Tiling(
            obstructions=[
                GriddedPerm((0, 2, 1), ((0, 0),) * 3),
                GriddedPerm((0, 2, 1), ((1, 0),) * 3),
            ]
        )
        assert not ComponentFusion(t3, col_idx=0).has_crossing_len2_ob()
        t4 = Tiling(
            obstructions=[
                GriddedPerm((0, 1, 2), ((0, 0),) * 3),
                GriddedPerm((0, 1, 2), ((0, 1),) * 3),
                GriddedPerm((0, 1, 2), ((0, 2),) * 3),
                GriddedPerm((0, 1), ((1, 2),) * 2),
                GriddedPerm((0, 1), ((0, 0), (0, 2))),
                GriddedPerm((0, 1), ((0, 1), (0, 2))),
                GriddedPerm((2, 0, 1), ((0, 2), (0, 0), (1, 2))),
                GriddedPerm((2, 0, 1), ((0, 2), (0, 1), (1, 2))),
            ]
        )
        assert not ComponentFusion(t4, row_idx=0).has_crossing_len2_ob()

    def test_is_crossing_len2(self, col_fusion):
        c1 = col_fusion.first_cell
        c2 = col_fusion.second_cell
        gp1 = GriddedPerm((0, 1), (c1, c2))
        gp2 = GriddedPerm((1, 0), (c2, c1))
        gp3 = GriddedPerm((0, 1), (c1, c1))
        gp4 = GriddedPerm((1, 0), (c2, c2))
        gp5 = GriddedPerm((1, 0), (c1, (2, 0)))
        gp5 = GriddedPerm((0, 1, 2), (c1, c2, c2))
        assert col_fusion.is_crossing_len2(gp1)
        assert col_fusion.is_crossing_len2(gp2)
        assert not col_fusion.is_crossing_len2(gp3)
        assert not col_fusion.is_crossing_len2(gp4)
        assert not col_fusion.is_crossing_len2(gp5)

    def test_obstruction_fuse_counter(self, col_fusion, row_fusion):
        assert col_fusion.obstruction_fuse_counter == {
            GriddedPerm((0, 2, 1), ((0, 0),) * 3): 2
        }
        assert (
            GriddedPerm((0, 1), ((0, 0), (0, 0)))
            not in row_fusion.obstruction_fuse_counter
        )

    def test_obstruction_to_add(self, col_fusion, row_fusion):
        assert set(col_fusion.obstructions_to_add()) == set(
            [
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
            ]
        )
        assert set(row_fusion.obstructions_to_add()) == set(
            [
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 1))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 1))),
                GriddedPerm((0, 1, 2), ((0, 0),) * 3),
                GriddedPerm((0, 1, 2), ((0, 1),) * 3),
                GriddedPerm((0, 1, 2), ((0, 2),) * 3),
                GriddedPerm((0, 1), ((1, 2),) * 2),
                GriddedPerm((0, 1), ((0, 0), (0, 2))),
                GriddedPerm((0, 1), ((0, 1), (0, 2))),
                GriddedPerm((2, 0, 1), ((0, 2), (0, 0), (1, 2))),
                GriddedPerm((2, 0, 1), ((0, 2), (0, 1), (1, 2))),
                GriddedPerm((0,), ((1, 0),)),
                GriddedPerm((0,), ((1, 1),)),
            ]
        )

    def test_fusable(self, col_fusion, row_fusion, not_prechecked_fusion):
        assert col_fusion.fusable()
        assert row_fusion.fusable()
        assert not not_prechecked_fusion.fusable()
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
            ]
        )
        assert not ComponentFusion(t, col_idx=0).fusable()

    def test_fused_tiling(self, col_fusion, row_fusion):
        assert col_fusion.fused_tiling() == Tiling.from_string("021")
        assert row_fusion.fused_tiling() == Tiling(
            obstructions=[
                GriddedPerm((0, 1, 2), ((0, 0),) * 3),
                GriddedPerm((0, 1, 2), ((0, 1),) * 3),
                GriddedPerm((0, 1), ((1, 1),) * 2),
                GriddedPerm((0, 1), ((0, 0), (0, 1))),
                GriddedPerm((2, 0, 1), ((0, 1), (0, 0), (1, 1))),
            ]
        )

    def test_requirements_fuse_counters(self, row_fusion, col_fusion, tiling_with_req):
        assert row_fusion.requirements_fuse_counters == []
        assert col_fusion.requirements_fuse_counters == []
        with pytest.raises(RuntimeError):
            ComponentFusion(tiling_with_req).requirements_fuse_counters

    def test_can_fuse_set_of_gridded_perms(self, row_fusion):
        with pytest.raises(NotImplementedError):
            row_fusion._can_fuse_set_of_gridded_perms([])

    def test_is_valid_count(self, row_fusion):
        with pytest.raises(NotImplementedError):
            row_fusion._is_valid_count(2, GriddedPerm((0,), ((0, 0),)))

    def test_fusing_empty_region(self):
        tiling = Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((0, 0), (0, 1))),
                GriddedPerm((0, 1), ((0, 1), (0, 1))),
                GriddedPerm((1, 0), ((0, 3), (0, 0))),
                GriddedPerm((1, 0), ((0, 3), (0, 1))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 2))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 3))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 3), (0, 3))),
                GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (0, 2))),
                GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (0, 3))),
                GriddedPerm((0, 1, 2), ((0, 1), (0, 3), (0, 3))),
                GriddedPerm((0, 1, 2), ((0, 2), (0, 2), (0, 2))),
                GriddedPerm((0, 1, 2), ((0, 2), (0, 3), (0, 3))),
                GriddedPerm((2, 0, 1), ((0, 3), (0, 2), (0, 2))),
                GriddedPerm((0, 1, 2, 3), ((0, 3), (0, 3), (0, 3), (0, 3))),
                GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (0, 3), (0, 2))),
                GriddedPerm((0, 2, 3, 1), ((0, 3), (0, 3), (0, 3), (0, 3))),
                GriddedPerm((3, 0, 1, 2), ((0, 3), (0, 3), (0, 3), (0, 3))),
            ),
            requirements=((GriddedPerm((0, 1), ((0, 3), (0, 3))),),),
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
        )
        assert not Fusion(tiling, col_idx=0, tracked=True).fusable()


def test_upward_closure():
    t = Tiling(
        [
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
        ]
    )
    algo = Fusion(t, col_idx=1)
    assert GriddedPerm((1, 0), ((1, 0), (1, 0))) in algo.fused_tiling().obstructions

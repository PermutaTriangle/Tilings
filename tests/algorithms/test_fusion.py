import pytest

from comb_spec_searcher import Rule
from permuta import Perm
from tilings import Obstruction, Requirement, Tiling
from tilings.algorithms import Fusion

# ------------------------------------------------
#      Fixture
# ------------------------------------------------


@pytest.fixture
def small_tiling():
    t = Tiling(obstructions=[
        Obstruction(Perm((1, 0)), ((0, 1), (1, 1))),
        Obstruction(Perm((1, 0)), ((0, 1), (0, 1))),
        Obstruction(Perm((1, 0)), ((0, 1), (1, 0))),
        Obstruction(Perm((1, 0)), ((0, 1), (0, 0))),
        Obstruction(Perm((1, 0)), ((0, 0), (0, 0))),
        Obstruction(Perm((1, 0)), ((0, 0), (1, 0))),
        Obstruction(Perm((1, 0)), ((1, 0), (1, 0))),
        Obstruction(Perm((1, 0)), ((1, 1), (1, 0))),
        Obstruction(Perm((1, 0)), ((1, 1), (1, 1)))
    ])
    return t


@pytest.fixture
def tiling_with_req():
    t = Tiling(obstructions=[
        Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
        Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
        Obstruction(Perm((0, 1, 2)), ((2, 0),)*3),
    ], requirements=[
        [Requirement(Perm((0, 1)), ((0, 0), (2, 0))),
         Requirement(Perm((0, 1)), ((1, 0), (2, 0)))],
        [Requirement(Perm((1, 0)), ((2, 0), (2, 0)))],
    ]
    )
    return t


@pytest.fixture
def big_tiling():
    """ The original tiling from Jay's idea """
    t = Tiling(obstructions=(
        Obstruction(Perm((0,)), ((0, 1),)),
        Obstruction(Perm((0,)), ((0, 2),)),
        Obstruction(Perm((0,)), ((0, 3),)),
        Obstruction(Perm((0,)), ((1, 2),)),
        Obstruction(Perm((0,)), ((1, 3),)),
        Obstruction(Perm((1, 0)), ((0, 0), (0, 0))),
        Obstruction(Perm((1, 0)), ((0, 0), (1, 0))),
        Obstruction(Perm((1, 0)), ((0, 0), (2, 0))),
        Obstruction(Perm((1, 0)), ((1, 0), (1, 0))),
        Obstruction(Perm((1, 0)), ((1, 0), (2, 0))),
        Obstruction(Perm((1, 0)), ((1, 1), (1, 0))),
        Obstruction(Perm((1, 0)), ((1, 1), (1, 1))),
        Obstruction(Perm((1, 0)), ((1, 1), (2, 0))),
        Obstruction(Perm((1, 0)), ((1, 1), (2, 1))),
        Obstruction(Perm((1, 0)), ((2, 0), (2, 0))),
        Obstruction(Perm((1, 0)), ((2, 1), (2, 0))),
        Obstruction(Perm((1, 0)), ((2, 1), (2, 1))),
        Obstruction(Perm((1, 0)), ((2, 2), (2, 0))),
        Obstruction(Perm((1, 0)), ((2, 2), (2, 1))),
        Obstruction(Perm((1, 0)), ((2, 2), (2, 2))),
        Obstruction(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 0))),
        Obstruction(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 1))),
        Obstruction(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 2))),
        Obstruction(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 3)))
    ), requirements=())
    return t


class TestFusion():

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
    def gp1(self, ):
        return Obstruction(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 1)))

    @pytest.fixture
    def gp2(self, ):
        return Obstruction(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 0)))

    @pytest.fixture
    def col_fusion_big(self, big_tiling):
        return Fusion(big_tiling, col_idx=0)

    def test_init(self, small_tiling):
        Fusion(small_tiling, row_idx=0)
        Fusion(small_tiling, col_idx=0)
        with pytest.raises(RuntimeError):
            Fusion(small_tiling, row_idx=0, col_idx=1)

    def test_fuse_gridded_perm(self, row_fusion, col_fusion, gp1):
        assert (row_fusion._fuse_gridded_perm(gp1) ==
                Obstruction(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 0))))
        assert (col_fusion._fuse_gridded_perm(gp1) ==
                Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 1))))

    def test_unfuse_gridded_perm(self, ):
        rf0 = Fusion(Tiling(), row_idx=0)
        rf1 = Fusion(Tiling(), row_idx=1)
        cf0 = Fusion(Tiling(), col_idx=0)
        ob1 = Obstruction(Perm((0, 1, 2, 3)), ((0, 0), (0, 1), (0, 1), (0, 2)))
        assert list(rf1._unfuse_gridded_perm(ob1)) == [
            Obstruction(Perm((0, 1, 2, 3)), ((0, 0), (0, 2), (0, 2), (0, 3))),
            Obstruction(Perm((0, 1, 2, 3)), ((0, 0), (0, 1), (0, 2), (0, 3))),
            Obstruction(Perm((0, 1, 2, 3)), ((0, 0), (0, 1), (0, 1), (0, 3))),
        ]
        ob2 = Obstruction(Perm((0, 2, 1, 3)), ((0, 0), (0, 1), (0, 1), (0, 2)))
        assert list(rf1._unfuse_gridded_perm(ob2)) == [
            Obstruction(Perm((0, 2, 1, 3)), ((0, 0), (0, 2), (0, 2), (0, 3))),
            Obstruction(Perm((0, 2, 1, 3)), ((0, 0), (0, 2), (0, 1), (0, 3))),
            Obstruction(Perm((0, 2, 1, 3)), ((0, 0), (0, 1), (0, 1), (0, 3))),
        ]
        ob3 = Obstruction(Perm((0, 2, 1, 4, 3)),
                          ((0, 0), (0, 1), (0, 1), (0, 2), (0, 1)))
        assert list(rf1._unfuse_gridded_perm(ob3)) == [
            Obstruction(Perm((0, 2, 1, 4, 3)),
                        ((0, 0), (0, 2), (0, 2), (0, 3), (0, 2))),
            Obstruction(Perm((0, 2, 1, 4, 3)),
                        ((0, 0), (0, 2), (0, 1), (0, 3), (0, 2))),
            Obstruction(Perm((0, 2, 1, 4, 3)),
                        ((0, 0), (0, 1), (0, 1), (0, 3), (0, 2))),
            Obstruction(Perm((0, 2, 1, 4, 3)),
                        ((0, 0), (0, 1), (0, 1), (0, 3), (0, 1))),
        ]
        ob4 = Obstruction(Perm((0, 2, 3, 1)), ((0, 0), (0, 1), (1, 1), (1, 0)))
        assert list(rf0._unfuse_gridded_perm(ob4)) == [
            Obstruction(Perm((0, 2, 3, 1)), ((0, 1), (0, 2), (1, 2), (1, 1))),
            Obstruction(Perm((0, 2, 3, 1)), ((0, 0), (0, 2), (1, 2), (1, 1))),
            Obstruction(Perm((0, 2, 3, 1)), ((0, 0), (0, 2), (1, 2), (1, 0))),
        ]
        assert list(cf0._unfuse_gridded_perm(ob4)) == [
            Obstruction(Perm((0, 2, 3, 1)), ((1, 0), (1, 1), (2, 1), (2, 0))),
            Obstruction(Perm((0, 2, 3, 1)), ((0, 0), (1, 1), (2, 1), (2, 0))),
            Obstruction(Perm((0, 2, 3, 1)), ((0, 0), (0, 1), (2, 1), (2, 0))),
        ]
        # Unfuse column
        ob5 = Obstruction(Perm((2, 0, 1)), ((0, 0), (0, 0), (0, 0)))
        assert list(cf0._unfuse_gridded_perm(ob5)) == [
            Obstruction(Perm((2, 0, 1)), ((1, 0), (1, 0), (1, 0))),
            Obstruction(Perm((2, 0, 1)), ((0, 0), (1, 0), (1, 0))),
            Obstruction(Perm((2, 0, 1)), ((0, 0), (0, 0), (1, 0))),
            Obstruction(Perm((2, 0, 1)), ((0, 0), (0, 0), (0, 0))),
        ]
        # Unfuse pattern with no point in the fuse region
        ob6 = Obstruction(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 0)))
        assert list(cf0._unfuse_gridded_perm(ob6)) == [
            Obstruction(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0))),
        ]
        ob6 = Obstruction(Perm((1, 0, 2)), ((0, 0), (0, 0), (1, 0)))
        assert list(cf0._unfuse_gridded_perm(ob6)) == [
            Obstruction(Perm((1, 0, 2)), ((1, 0), (1, 0), (2, 0))),
            Obstruction(Perm((1, 0, 2)), ((0, 0), (1, 0), (2, 0))),
            Obstruction(Perm((1, 0, 2)), ((0, 0), (0, 0), (2, 0))),
        ]

    def test_fuse_counter(self, row_fusion, col_fusion, gp1, gp2):
        assert (row_fusion._fuse_counter([gp1, gp2]) ==
                {Obstruction(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 0))): 2})
        assert (col_fusion._fuse_counter([gp1, gp2]) == {
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 1))): 1,
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))): 1
        })

    def test_obstruction_fuse_counter(self, row_fusion, col_fusion,
                                      col_fusion_big):
        assert (row_fusion.obstruction_fuse_counter == {
            Obstruction(Perm((1, 0)), ((0, 0), (0, 0))): 3,
            Obstruction(Perm((1, 0)), ((0, 0), (1, 0))): 3,
            Obstruction(Perm((1, 0)), ((1, 0), (1, 0))): 3
        })
        assert (col_fusion.obstruction_fuse_counter == {
            Obstruction(Perm((1, 0)), ((0, 0), (0, 0))): 3,
            Obstruction(Perm((1, 0)), ((0, 1), (0, 0))): 3,
            Obstruction(Perm((1, 0)), ((0, 1), (0, 1))): 3
        })
        assert (col_fusion_big.obstruction_fuse_counter == {
            Obstruction(Perm((0,)), ((0, 1),)): 1,
            Obstruction(Perm((0,)), ((0, 2),)): 2,
            Obstruction(Perm((0,)), ((0, 3),)): 2,
            Obstruction(Perm((1, 0)), ((0, 0), (0, 0))): 3,
            Obstruction(Perm((1, 0)), ((0, 1), (0, 1))): 1,
            Obstruction(Perm((1, 0)), ((0, 1), (0, 0))): 1,
            Obstruction(Perm((1, 0)), ((0, 0), (1, 0))): 2,
            Obstruction(Perm((1, 0)), ((0, 1), (1, 0))): 1,
            Obstruction(Perm((1, 0)), ((0, 1), (1, 1))): 1,

            Obstruction(Perm((1, 0)), ((1, 0), (1, 0))): 1,
            Obstruction(Perm((1, 0)), ((1, 1), (1, 0))): 1,
            Obstruction(Perm((1, 0)), ((1, 1), (1, 1))): 1,
            Obstruction(Perm((1, 0)), ((1, 2), (1, 0))): 1,
            Obstruction(Perm((1, 0)), ((1, 2), (1, 1))): 1,
            Obstruction(Perm((1, 0)), ((1, 2), (1, 2))): 1,

            Obstruction(Perm((2, 1, 0)), ((1, 3), (1, 3), (1, 0))): 1,
            Obstruction(Perm((2, 1, 0)), ((1, 3), (1, 3), (1, 1))): 1,
            Obstruction(Perm((2, 1, 0)), ((1, 3), (1, 3), (1, 2))): 1,
            Obstruction(Perm((2, 1, 0)), ((1, 3), (1, 3), (1, 3))): 1
        })

    def test_requirements_fuse_counters(self, row_fusion, fusion_with_req):
        assert row_fusion.requirements_fuse_counters == []
        print(fusion_with_req._tiling)
        assert fusion_with_req.requirements_fuse_counters == [
            {Requirement(Perm((0, 1)), ((0, 0), (1, 0))): 2},
            {Requirement(Perm((1, 0)), ((1, 0), (1, 0))): 1},
        ]

    def test_can_fuse_set_of_gridded_perms(self, row_fusion, col_fusion,
                                           col_fusion_big):
        counter = row_fusion.obstruction_fuse_counter
        assert row_fusion._can_fuse_set_of_gridded_perms(counter)
        counter = col_fusion.obstruction_fuse_counter
        assert col_fusion._can_fuse_set_of_gridded_perms(counter)
        counter = col_fusion_big.obstruction_fuse_counter
        assert not col_fusion_big._can_fuse_set_of_gridded_perms(counter)

    def test_is_valid_count(self, row_fusion):
        assert row_fusion._is_valid_count(
            3, Obstruction(Perm((1, 0)), ((0, 0), (0, 0))))
        assert row_fusion._is_valid_count(
            3, Obstruction(Perm((1, 0)), ((0, 0), (1, 0))))
        assert row_fusion._is_valid_count(
            2, Obstruction(Perm((1, 0)), ((1, 1), (1, 0))))
        assert not row_fusion._is_valid_count(
            1, Obstruction(Perm((1, 0)), ((1, 0), (1, 0))))

    def test_point_in_fuse_region(self, row_fusion, col_fusion_big, gp1, gp2):
        assert row_fusion._point_in_fuse_region(gp1) == 2
        assert row_fusion._point_in_fuse_region(gp2) == 3
        assert col_fusion_big._point_in_fuse_region(gp1) == 1
        assert col_fusion_big._point_in_fuse_region(gp2) == 1

    def test_fusable(self, row_fusion, col_fusion, col_fusion_big,
                     fusion_with_req):
        assert row_fusion.fusable()
        assert col_fusion.fusable()
        assert fusion_with_req.fusable()
        assert not col_fusion_big.fusable()
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
            Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
        ])
        assert not Fusion(t, row_idx=0).fusable()

    def test_fused_tiling(self, row_fusion, col_fusion, col_fusion_big,
                          fusion_with_req):
        assert (row_fusion.fused_tiling() == Tiling(obstructions=[
            Obstruction(Perm((1, 0)), ((0, 0), (0, 0))),
            Obstruction(Perm((1, 0)), ((0, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 0), (1, 0)))
        ]))
        assert (col_fusion.fused_tiling() == Tiling(obstructions=[
            Obstruction(Perm((1, 0)), ((0, 0), (0, 0))),
            Obstruction(Perm((1, 0)), ((0, 1), (0, 0))),
            Obstruction(Perm((1, 0)), ((0, 1), (0, 1))),
        ]))
        # We can get the fused tiling even for not fusable tilings
        assert (col_fusion_big.fused_tiling() == Tiling(obstructions=[
            Obstruction(Perm((0,)), ((0, 1),)),
            Obstruction(Perm((0,)), ((0, 2),)),
            Obstruction(Perm((0,)), ((0, 3),)),
            Obstruction(Perm((1, 0)), ((0, 0), (0, 0))),
            Obstruction(Perm((1, 0)), ((0, 1), (0, 1))),
            Obstruction(Perm((1, 0)), ((0, 1), (0, 0))),
            Obstruction(Perm((1, 0)), ((0, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((0, 1), (1, 0))),
            Obstruction(Perm((1, 0)), ((0, 1), (1, 1))),
            Obstruction(Perm((1, 0)), ((1, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 1), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 1), (1, 1))),
            Obstruction(Perm((1, 0)), ((1, 2), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 2), (1, 1))),
            Obstruction(Perm((1, 0)), ((1, 2), (1, 2))),
            Obstruction(Perm((2, 1, 0)), ((1, 3), (1, 3), (1, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 3), (1, 3), (1, 1))),
            Obstruction(Perm((2, 1, 0)), ((1, 3), (1, 3), (1, 2))),
            Obstruction(Perm((2, 1, 0)), ((1, 3), (1, 3), (1, 3))),
        ]))
        assert (fusion_with_req.fused_tiling() == Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
            Obstruction(Perm((0, 1, 2)), ((1, 0),)*3)
        ], requirements=[
            [Requirement(Perm((0, 1)), ((0, 0), (1, 0)))],
            [Requirement(Perm((1, 0)), ((1, 0), (1, 0)))],
        ]))

    def test_formal_step(self, row_fusion, col_fusion):
        assert row_fusion.formal_step() == "Fuse rows 0 and 1."
        assert col_fusion.formal_step() == "Fuse columns 0 and 1."

    def test_rule(self, row_fusion):
        rule = row_fusion.rule()
        assert rule.formal_step == row_fusion.formal_step()
        assert rule.comb_classes == [row_fusion.fused_tiling()]
        assert rule.inferable == [True]
        assert rule.workable == [True]
        assert rule.possibly_empty == [False]
        assert rule.constructor == 'other'

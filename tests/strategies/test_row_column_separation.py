import pytest

from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.strategies import (
    ObstructionTransitivityStrategy,
    RowColumnSeparationStrategy,
)

pytest_plugins = ["tests.fixtures.simple_trans"]

# Row column separation test
@pytest.fixture
def not_separable_tilings():
    t1 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
        ]
    )
    t2 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((3, 0),) * 3),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (3, 0))),
        ]
    )
    t3 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((3, 0),) * 3),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (3, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (3, 0))),
        ]
    )
    return [t1, t2, t3]


@pytest.fixture
def seperable_tiling1():
    t1 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
        ]
    )
    return t1


@pytest.fixture
def seperable_tiling2():
    t2 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((3, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 1),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 1),) * 3),
            GriddedPerm(Perm((0,)), ((3, 1),)),
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (1, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (2, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (3, 1))),
            GriddedPerm(Perm((0, 1)), ((1, 1), (2, 1))),
            GriddedPerm(Perm((0, 1)), ((2, 1), (3, 1))),
        ]
    )
    return t2


@pytest.fixture
def seperable_tiling3():
    t3 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((3, 0),) * 3),
            GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (3, 0))),
        ]
    )
    return t3


def test_row_col_seperation(
    not_separable_tilings, seperable_tiling1, seperable_tiling2, seperable_tiling3
):
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
        ]
    )
    rcs = RowColumnSeparationStrategy()(t)
    assert rcs.comb_classes[0] == Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
        ]
    )

    for t in not_separable_tilings:
        assert RowColumnSeparationStrategy()(t) is None
    t1_sep = Tiling(
        obstructions=(
            GriddedPerm(Perm((0,)), ((0, 0),)),
            GriddedPerm(Perm((0,)), ((0, 1),)),
            GriddedPerm(Perm((0,)), ((1, 0),)),
            GriddedPerm(Perm((0,)), ((1, 2),)),
            GriddedPerm(Perm((0,)), ((2, 1),)),
            GriddedPerm(Perm((0,)), ((2, 2),)),
            GriddedPerm(Perm((0, 1, 2)), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm(Perm((0, 1, 2)), ((1, 1), (1, 1), (1, 1))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0))),
        ),
        requirements=(),
    )
    t2_sep = Tiling(
        obstructions=(
            GriddedPerm(Perm((0,)), ((0, 0),)),
            GriddedPerm(Perm((0,)), ((0, 1),)),
            GriddedPerm(Perm((0,)), ((0, 2),)),
            GriddedPerm(Perm((0,)), ((0, 3),)),
            GriddedPerm(Perm((0,)), ((1, 0),)),
            GriddedPerm(Perm((0,)), ((1, 2),)),
            GriddedPerm(Perm((0,)), ((1, 3),)),
            GriddedPerm(Perm((0,)), ((1, 4),)),
            GriddedPerm(Perm((0,)), ((2, 1),)),
            GriddedPerm(Perm((0,)), ((2, 2),)),
            GriddedPerm(Perm((0,)), ((2, 4),)),
            GriddedPerm(Perm((0,)), ((3, 1),)),
            GriddedPerm(Perm((0,)), ((3, 3),)),
            GriddedPerm(Perm((0,)), ((3, 4),)),
            GriddedPerm(Perm((0,)), ((4, 1),)),
            GriddedPerm(Perm((0,)), ((4, 2),)),
            GriddedPerm(Perm((0,)), ((4, 3),)),
            GriddedPerm(Perm((0,)), ((4, 4),)),
            GriddedPerm(Perm((0, 1)), ((2, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((3, 0), (4, 0))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 4), (0, 4), (0, 4))),
            GriddedPerm(Perm((0, 1, 2)), ((1, 1), (1, 1), (1, 1))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 0))),
            GriddedPerm(Perm((0, 1, 2)), ((3, 2), (3, 2), (3, 2))),
            GriddedPerm(Perm((0, 1, 2)), ((4, 0), (4, 0), (4, 0))),
        ),
        requirements=(),
    )
    t3_sep = Tiling(
        obstructions=(
            GriddedPerm(Perm((0,)), ((0, 0),)),
            GriddedPerm(Perm((0,)), ((1, 0),)),
            GriddedPerm(Perm((0,)), ((2, 1),)),
            GriddedPerm(Perm((0,)), ((3, 1),)),
            GriddedPerm(Perm((0, 1, 2)), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm(Perm((0, 1, 2)), ((1, 1), (1, 1), (1, 1))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 0))),
        ),
        requirements=(),
    )
    assert RowColumnSeparationStrategy()(seperable_tiling1).comb_classes[0] == t1_sep
    assert RowColumnSeparationStrategy()(seperable_tiling2).comb_classes[0] == t2_sep
    assert RowColumnSeparationStrategy()(seperable_tiling3).comb_classes[0] == t3_sep


def test_rule(separable_tiling1, not_separable_tilings):
    rcs = RowColSeparation(separable_tiling1)
    rule = rcs.rule()
    assert isinstance(rule, Rule)
    assert rule.comb_classes == [rcs.separated_tiling()]
    assert rule.ignore_parent
    assert rule.workable == [True]
    assert rule.constructor == "equiv"
    assert rule.possibly_empty == [False]
    assert RowColSeparation(not_separable_tilings[0]).rule() is None

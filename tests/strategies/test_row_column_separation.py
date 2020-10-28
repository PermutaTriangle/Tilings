import pytest

from comb_spec_searcher import DisjointUnion
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
from tilings import GriddedPerm, Tiling
from tilings.algorithms import RowColSeparation
from tilings.assumptions import TrackingAssumption
from tilings.strategies import RowColumnSeparationStrategy

pytest_plugins = ["tests.fixtures.simple_trans"]


# Row column separation test
@pytest.fixture
def not_separable_tilings():
    t1 = Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((0, 0),) * 3),
            GriddedPerm((0, 1, 2), ((1, 0),) * 3),
            GriddedPerm((0, 1, 2), ((2, 0),) * 3),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (2, 0))),
        ]
    )
    t2 = Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((0, 0),) * 3),
            GriddedPerm((0, 1, 2), ((1, 0),) * 3),
            GriddedPerm((0, 1, 2), ((2, 0),) * 3),
            GriddedPerm((0, 1, 2), ((3, 0),) * 3),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 1), ((0, 0), (2, 0))),
            GriddedPerm((0, 1), ((1, 0), (2, 0))),
            GriddedPerm((0, 1), ((2, 0), (3, 0))),
        ]
    )
    t3 = Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((0, 0),) * 3),
            GriddedPerm((0, 1, 2), ((1, 0),) * 3),
            GriddedPerm((0, 1, 2), ((2, 0),) * 3),
            GriddedPerm((0, 1, 2), ((3, 0),) * 3),
            GriddedPerm((0, 1), ((0, 0), (2, 0))),
            GriddedPerm((0, 1), ((0, 0), (3, 0))),
            GriddedPerm((1, 0), ((1, 0), (2, 0))),
            GriddedPerm((0, 1), ((1, 0), (3, 0))),
        ]
    )
    return [t1, t2, t3]


@pytest.fixture
def seperable_tiling1():
    t1 = Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((0, 0),) * 3),
            GriddedPerm((0, 1, 2), ((1, 0),) * 3),
            GriddedPerm((0, 1, 2), ((2, 0),) * 3),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (2, 0))),
            GriddedPerm((0, 1), ((0, 0), (2, 0))),
        ]
    )
    return t1


@pytest.fixture
def seperable_tiling2():
    t2 = Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((0, 0),) * 3),
            GriddedPerm((0, 1, 2), ((1, 0),) * 3),
            GriddedPerm((0, 1, 2), ((2, 0),) * 3),
            GriddedPerm((0, 1, 2), ((3, 0),) * 3),
            GriddedPerm((0, 1, 2), ((0, 1),) * 3),
            GriddedPerm((0, 1, 2), ((1, 1),) * 3),
            GriddedPerm((0, 1, 2), ((2, 1),) * 3),
            GriddedPerm((0,), ((3, 1),)),
            GriddedPerm((0, 1), ((0, 0), (0, 1))),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 1), ((0, 0), (2, 0))),
            GriddedPerm((0, 1), ((0, 0), (3, 0))),
            GriddedPerm((0, 1), ((1, 0), (2, 0))),
            GriddedPerm((0, 1), ((2, 0), (3, 0))),
            GriddedPerm((0, 1), ((0, 1), (1, 1))),
            GriddedPerm((0, 1), ((0, 1), (2, 1))),
            GriddedPerm((0, 1), ((0, 1), (3, 1))),
            GriddedPerm((0, 1), ((1, 1), (2, 1))),
            GriddedPerm((0, 1), ((2, 1), (3, 1))),
        ]
    )
    return t2


@pytest.fixture
def seperable_tiling3():
    t3 = Tiling(
        obstructions=[
            GriddedPerm((0, 1, 2), ((0, 0),) * 3),
            GriddedPerm((0, 1, 2), ((1, 0),) * 3),
            GriddedPerm((0, 1, 2), ((2, 0),) * 3),
            GriddedPerm((0, 1, 2), ((3, 0),) * 3),
            GriddedPerm((0, 1), ((0, 0), (2, 0))),
            GriddedPerm((0, 1), ((0, 0), (3, 0))),
            GriddedPerm((0, 1), ((1, 0), (2, 0))),
            GriddedPerm((0, 1), ((1, 0), (3, 0))),
        ]
    )
    return t3


def test_row_col_seperation(
    not_separable_tilings, seperable_tiling1, seperable_tiling2, seperable_tiling3
):
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0),) * 2),
            GriddedPerm((0, 1), ((1, 0),) * 2),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
        ]
    )
    rcs = RowColumnSeparationStrategy()(t)
    assert rcs.children[0] == Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 1),) * 2),
            GriddedPerm((0, 1), ((1, 0),) * 2),
        ]
    )

    for t in not_separable_tilings:
        with pytest.raises(StrategyDoesNotApply):
            RowColumnSeparationStrategy()(t).children
    t1_sep = Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0,), ((2, 2),)),
            GriddedPerm((0, 1, 2), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 1, 2), ((1, 1), (1, 1), (1, 1))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
        ),
        requirements=(),
    )
    t2_sep = Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((0, 2),)),
            GriddedPerm((0,), ((0, 3),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0,), ((1, 3),)),
            GriddedPerm((0,), ((1, 4),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0,), ((2, 2),)),
            GriddedPerm((0,), ((2, 4),)),
            GriddedPerm((0,), ((3, 1),)),
            GriddedPerm((0,), ((3, 3),)),
            GriddedPerm((0,), ((3, 4),)),
            GriddedPerm((0,), ((4, 1),)),
            GriddedPerm((0,), ((4, 2),)),
            GriddedPerm((0,), ((4, 3),)),
            GriddedPerm((0,), ((4, 4),)),
            GriddedPerm((0, 1), ((2, 0), (3, 0))),
            GriddedPerm((0, 1), ((3, 0), (4, 0))),
            GriddedPerm((0, 1, 2), ((0, 4), (0, 4), (0, 4))),
            GriddedPerm((0, 1, 2), ((1, 1), (1, 1), (1, 1))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2), ((3, 2), (3, 2), (3, 2))),
            GriddedPerm((0, 1, 2), ((4, 0), (4, 0), (4, 0))),
        ),
        requirements=(),
    )
    t3_sep = Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0,), ((3, 1),)),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 1, 2), ((1, 1), (1, 1), (1, 1))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (3, 0))),
        ),
        requirements=(),
    )
    assert RowColumnSeparationStrategy()(seperable_tiling1).children[0] == t1_sep
    assert RowColumnSeparationStrategy()(seperable_tiling2).children[0] == t2_sep
    assert RowColumnSeparationStrategy()(seperable_tiling3).children[0] == t3_sep


def test_rule(seperable_tiling1, not_separable_tilings):
    rcs = RowColSeparation(seperable_tiling1)
    rule = RowColumnSeparationStrategy()(seperable_tiling1)
    assert isinstance(rule, Rule)
    assert list(rule.children) == [rcs.separated_tiling()]
    assert rule.ignore_parent
    assert rule.workable
    assert isinstance(rule.constructor, DisjointUnion)
    assert not rule.possibly_empty
    assert (
        RowColumnSeparationStrategy().decomposition_function(not_separable_tilings[0])
        is None
    )
    with pytest.raises(StrategyDoesNotApply):
        RowColumnSeparationStrategy()(not_separable_tilings[0]).children


def test_formal_step(seperable_tiling1):
    assert (
        RowColumnSeparationStrategy()(seperable_tiling1).formal_step
        == "row and column separation"
    )


def test_backmap():
    tiling = Tiling(
        obstructions=(
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((0, 0), (1, 0))),
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 0, 1), ((0, 1), (0, 0), (0, 0))),
            GriddedPerm((2, 0, 1), ((0, 1), (0, 0), (1, 0))),
            GriddedPerm((2, 0, 1), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 2, 3, 0), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((2, 3, 0, 1), ((0, 1), (0, 1), (0, 0), (0, 1))),
            GriddedPerm((2, 3, 1, 0), ((0, 1), (0, 1), (0, 0), (0, 0))),
            GriddedPerm((2, 3, 1, 0), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((3, 0, 1, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((3, 1, 2, 0), ((0, 1), (0, 0), (0, 1), (0, 0))),
            GriddedPerm((3, 2, 0, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((3, 2, 1, 0), ((0, 1), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((4, 3, 2, 0, 1), ((0, 1), (0, 1), (0, 1), (0, 0), (0, 1))),
        ),
        requirements=((GriddedPerm((0,), ((1, 0),)),),),
    )
    strategy = RowColumnSeparationStrategy()
    rule = strategy(tiling)
    gps = (GriddedPerm((0,), ((1, 2),)),)
    assert next(rule.backward_map(gps)) == GriddedPerm((0,), ((0, 1),))


def test_maps():
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 0), (0, 1))),
            GriddedPerm((0, 1), ((0, 0), (0, 2))),
            GriddedPerm((0, 1), ((0, 0), (1, 1))),
            GriddedPerm((0, 1), ((0, 0), (2, 0))),
            GriddedPerm((0, 1), ((0, 0), (2, 2))),
            GriddedPerm((0, 1), ((0, 1), (0, 2))),
            GriddedPerm((0, 1), ((0, 1), (1, 1))),
            GriddedPerm((0, 1), ((0, 2), (0, 2))),
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
            GriddedPerm((0, 1), ((1, 1), (2, 1))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((1, 0), ((0, 0), (2, 0))),
            GriddedPerm((1, 0), ((0, 1), (0, 0))),
            GriddedPerm((1, 0), ((0, 1), (2, 1))),
            GriddedPerm((1, 0), ((0, 2), (0, 0))),
            GriddedPerm((1, 0), ((0, 2), (0, 1))),
            GriddedPerm((1, 0), ((1, 1), (2, 1))),
            GriddedPerm((1, 0), ((2, 1), (2, 0))),
            GriddedPerm((1, 0), ((2, 1), (2, 1))),
            GriddedPerm((1, 0), ((2, 2), (2, 1))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (2, 1))),
            GriddedPerm((0, 1, 2), ((0, 1), (2, 1), (2, 2))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1), ((0, 1), (2, 2), (2, 2))),
            GriddedPerm((0, 2, 1), ((2, 1), (2, 2), (2, 2))),
            GriddedPerm((0, 2, 1), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((1, 0, 2), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (2, 2), (2, 2))),
            GriddedPerm((1, 2, 0), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((2, 0, 1), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((2, 0, 1), ((2, 2), (2, 0), (2, 2))),
            GriddedPerm((2, 0, 1), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((2, 1, 0), ((0, 2), (2, 2), (2, 0))),
            GriddedPerm((2, 1, 0), ((0, 2), (2, 2), (2, 2))),
            GriddedPerm((2, 1, 0), ((2, 2), (2, 2), (2, 0))),
            GriddedPerm((2, 1, 0), ((2, 2), (2, 2), (2, 2))),
        ),
        requirements=((GriddedPerm((0,), ((2, 1),)),),),
    )
    print(t)
    print(t.row_and_column_separation())
    strategy = RowColumnSeparationStrategy()
    rule = strategy(t)
    cell_pre_sep = [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)]
    cell_post_sep = [(2, 0), (0, 2), (1, 4), (3, 1), (3, 3), (3, 4)]
    # Testing forward map
    for cell, image in zip(cell_pre_sep, cell_post_sep):
        gp = GriddedPerm((0,), (cell,))
        print(f"{cell} -> {image}")
        assert rule.forward_map(gp) == (GriddedPerm((0,), (image,)),)
    # Testing backmap
    for cell, image in zip(cell_post_sep, cell_pre_sep):
        gps = [GriddedPerm((0,), (cell,))]
        print(f"{cell} -> {image}")
        assert next(rule.backward_map(gps)) == GriddedPerm((0,), (image,))


def test_mapping_assumptions():
    tiling = Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 1))),
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((1, 1), (1, 0))),
            GriddedPerm((1, 0), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
        ),
        requirements=((GriddedPerm((0,), ((1, 1),)),),),
        assumptions=(
            TrackingAssumption(
                (GriddedPerm((0,), ((1, 0),)), GriddedPerm((0,), ((1, 1),)))
            ),
        ),
    )
    strategy = RowColumnSeparationStrategy()
    rule = strategy(tiling)
    assert strategy.extra_parameters(tiling, rule.children) == ({"k_0": "k_0"},)

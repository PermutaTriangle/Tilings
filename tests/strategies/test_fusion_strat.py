import pytest
from sympy import Eq, Function, Lambda, cancel, expand, var

from comb_spec_searcher.strategies import Rule
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Fusion
from tilings.assumptions import TrackingAssumption
from tilings.strategies import ComponentFusionFactory, FusionFactory
from tilings.strategies.fusion import (
    ComponentFusionStrategy,
    FusionConstructor,
    FusionStrategy,
)


@pytest.fixture
def tiling1():
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
def tiling2():
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 2, 1, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 2, 1, 3), ((1, 0), (1, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 2, 1, 3), ((1, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 2, 1, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
        ]
    )
    return t


def test_component_fusion(tiling1, tiling2):
    assert len(list(ComponentFusionFactory()(tiling1))) == 0
    assert len(list(ComponentFusionFactory()(tiling2))) == 1


@pytest.fixture
def small_tiling():
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
def big_tiling():
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


def test_fusion(small_tiling, big_tiling):
    assert len(list(FusionFactory()(big_tiling))) == 0
    small_tiling_rules = list(FusionFactory()(small_tiling))
    assert len(small_tiling_rules) == 2
    assert all(isinstance(rule, Rule) for rule in small_tiling_rules)
    assert all(
        isinstance(rule.constructor, FusionConstructor) for rule in small_tiling_rules
    )
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
        ]
    )
    t_rules = list(FusionFactory()(t))
    assert len(t_rules) == 1


@pytest.fixture
def row_fusion(small_tiling):
    return FusionStrategy(row_idx=0, tracked=True)(small_tiling)


@pytest.fixture
def col_fusion(small_tiling):
    return FusionStrategy(col_idx=0, tracked=True)(small_tiling)


def test_formal_step_fusion(row_fusion, col_fusion):
    assert row_fusion.formal_step == "fuse rows 0 and 1"
    assert col_fusion.formal_step == "fuse columns 0 and 1"


def test_rule(row_fusion):
    assert row_fusion.formal_step == "fuse rows 0 and 1"
    assert list(row_fusion.children) == [
        Fusion(row_fusion.comb_class, row_idx=0, tracked=True).fused_tiling()
    ]
    assert row_fusion.inferrable
    assert row_fusion.workable
    assert not row_fusion.possibly_empty
    assert isinstance(row_fusion.constructor, FusionConstructor)


@pytest.fixture
def row_tiling():
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
def col_tiling():
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 2, 1), ((0, 0),) * 3),
            GriddedPerm((0, 2, 1), ((1, 0),) * 3),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
        ]
    )
    return t


@pytest.fixture
def component_row_fusion(row_tiling):
    return ComponentFusionStrategy(row_idx=0, tracked=True)(row_tiling)


@pytest.fixture
def component_col_fusion(col_tiling):
    return ComponentFusionStrategy(col_idx=0, tracked=True)(col_tiling)


def test_formal_step_component(component_col_fusion, component_row_fusion):
    assert component_col_fusion.formal_step == "component fuse columns 0 and 1"
    assert component_row_fusion.formal_step == "component fuse rows 0 and 1"
    assert len(component_col_fusion.children) == 1
    assert len(component_row_fusion.children) == 1
    assert component_row_fusion.inferrable
    assert component_row_fusion.workable
    assert not component_row_fusion.possibly_empty
    assert isinstance(component_row_fusion.constructor, FusionConstructor)
    assert component_col_fusion.inferrable
    assert component_col_fusion.workable
    assert not component_col_fusion.possibly_empty
    assert isinstance(component_col_fusion.constructor, FusionConstructor)


def test_fuse_parameter():
    tiling = Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((0, 2),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0,), ((2, 0),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0,), ((3, 0),)),
            GriddedPerm((0,), ((3, 2),)),
            GriddedPerm((1, 0), ((3, 1), (3, 1))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (1, 2))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (2, 2))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 1), (3, 1))),
            GriddedPerm((0, 2, 1), ((1, 2), (1, 2), (1, 2))),
            GriddedPerm((0, 2, 1), ((1, 2), (1, 2), (2, 2))),
            GriddedPerm((0, 2, 1), ((1, 2), (2, 2), (2, 2))),
            GriddedPerm((0, 2, 1), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((1, 0, 2), ((1, 2), (1, 2), (1, 2))),
            GriddedPerm((1, 0, 2), ((1, 2), (1, 2), (2, 2))),
            GriddedPerm((1, 0, 2), ((1, 2), (2, 2), (2, 2))),
            GriddedPerm((1, 0, 2), ((2, 2), (2, 2), (2, 2))),
        ),
        requirements=((GriddedPerm((0,), ((2, 2),)), GriddedPerm((0,), ((3, 2),))),),
        assumptions=(),
    )
    strategy = FusionStrategy(col_idx=1, tracked=True)
    assert strategy._fuse_parameter(tiling) == "k_0"
    rule = strategy(tiling)
    assert isinstance(rule.constructor, FusionConstructor)


def test_positive_fusion():
    tiling = Tiling(
        [
            GriddedPerm((0, 1, 2), [(0, 0), (0, 0), (0, 0)]),
            GriddedPerm((0, 1, 2), [(0, 0), (0, 0), (1, 0)]),
            GriddedPerm((0, 1, 2), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm((0, 1, 2), [(1, 0), (1, 0), (1, 0)]),
        ]
    )

    positive_left = tiling.insert_cell((0, 0))
    positive_right = tiling.insert_cell((1, 0))
    positive_both = tiling.insert_cell((0, 0)).insert_cell((1, 0))

    strategy = FusionStrategy(col_idx=0, tracked=True)

    rule = strategy(tiling)
    assert rule.children == (
        Tiling(
            obstructions=(GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),),
            requirements=(),
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
        ),
    )

    rule = strategy(positive_left)
    assert rule.children == (
        Tiling(
            obstructions=(GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),),
            requirements=((GriddedPerm((0,), ((0, 0),)),),),
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
        ),
    )

    rule = strategy(positive_right)
    assert rule.children == (
        Tiling(
            obstructions=(GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),),
            requirements=((GriddedPerm((0,), ((0, 0),)),),),
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
        ),
    )

    rule = strategy(positive_both)
    assert rule.children == (
        Tiling(
            obstructions=(GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),),
            requirements=(
                (
                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((0, 0), (0, 0))),
                ),
            ),
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
        ),
    )


def easy_fusable(
    pos_left=False,
    pos_right=False,
    track_left=False,
    track_right=False,
    same_tracking=False,
    pos_either=False,
    tracked_beyond=(),
):
    """Two decreasing cells, (0, 0) and (1, 0), every point of the left one
    above those of the right one, so that their columns fuse. With pos_either, a
    point is required in one of them; tracked_beyond adds an increasing cell (2, 0)
    beside them and an assumption tracking each list of cells it gives."""
    if same_tracking:
        assert track_left and track_right
    obs = [
        GriddedPerm.single_cell((0, 1), (0, 0)),
        GriddedPerm((0, 1), ((0, 0), (1, 0))),
        GriddedPerm.single_cell((0, 1), (1, 0)),
    ]
    if tracked_beyond:
        obs.append(GriddedPerm.single_cell((1, 0), (2, 0)))

    reqs = []
    if pos_left:
        reqs.append([GriddedPerm.single_cell((0,), (0, 0))])
    if pos_right:
        reqs.append([GriddedPerm.single_cell((0,), (1, 0))])
    if pos_either:
        reqs.append(
            [
                GriddedPerm.single_cell((0,), (0, 0)),
                GriddedPerm.single_cell((0,), (1, 0)),
            ]
        )

    ass = [
        TrackingAssumption([GriddedPerm.single_cell((0,), cell) for cell in cells])
        for cells in tracked_beyond
    ]
    if same_tracking:
        ass.append(
            TrackingAssumption(
                [
                    GriddedPerm.single_cell((0,), (0, 0)),
                    GriddedPerm.single_cell((0,), (1, 0)),
                ]
            )
        )
    else:
        if track_left:
            ass.append(TrackingAssumption([GriddedPerm.single_cell((0,), (0, 0))]))
        if track_right:
            ass.append(TrackingAssumption([GriddedPerm.single_cell((0,), (1, 0))]))

    tiling = Tiling(obstructions=obs, requirements=reqs, assumptions=ass)
    return tiling


def eq_equality(e1, e2):
    return e1.lhs == e2.lhs and (e1.rhs - e2.rhs).simplify() == 0


def test_fusion_gfs():
    """The equations of fusions whose two sides are given different values. Those
    whose sides are given the same value have none
    (test_fusion_with_both_sides_the_same_value)."""
    x = var("x")
    k_0 = var("k_0")
    k_1 = var("k_1")

    t2 = easy_fusable(track_left=True)
    rules = list(FusionFactory()(t2))
    assert len(rules) == 1
    F0 = Function("F0")(x)
    F1 = Function("F1")(x, k_0)
    actual_eq = rules[0].constructor.get_equation(F0, (F1,))
    expected_eq = Eq(F0, (k_0 * F1 - F1.subs({k_0: 1})) / (k_0 - 1))
    assert eq_equality(actual_eq, expected_eq)

    t4 = easy_fusable(track_left=True, track_right=True, same_tracking=False)
    rules = list(FusionFactory()(t4))
    assert len(rules) == 1
    F0 = Function("F0")(x, k_0, k_1)
    F1 = Function("F1")(x, k_0)
    actual_eq = rules[0].constructor.get_equation(F0, (F1,))
    expected_eq = Eq(F0, (k_0 * F1 - k_1 * F1.subs({k_0: k_1})) / (k_0 - k_1))
    assert eq_equality(actual_eq, expected_eq)

    t6 = easy_fusable(pos_left=True, track_left=True)
    rules = list(FusionFactory()(t6))
    assert len(rules) == 1
    F0 = Function("F0")(x, k_0)
    F1 = Function("F1")(x, k_0)
    actual_eq = rules[0].constructor.get_equation(F0, (F1,))
    expected_eq = Eq(F0, (k_0 * F1 - F1.subs({k_0: 1})) / (k_0 - 1) - F1.subs({k_0: 1}))
    assert eq_equality(actual_eq, expected_eq)

    t7 = easy_fusable(pos_left=True, track_right=True)
    rules = list(FusionFactory()(t7))
    assert len(rules) == 1
    F0 = Function("F0")(x, k_0)
    F1 = Function("F1")(x, k_0)
    actual_eq = rules[0].constructor.get_equation(F0, (F1,))
    expected_eq = Eq(F0, (k_0 * F1 - F1.subs({k_0: 1})) / (k_0 - 1) - F1)
    assert eq_equality(actual_eq, expected_eq)

    t9 = easy_fusable(
        pos_left=True, track_left=True, track_right=True, same_tracking=False
    )
    rules = list(FusionFactory()(t9))
    assert len(rules) == 1
    F0 = Function("F0")(x, k_0, k_1)
    F1 = Function("F1")(x, k_0)
    actual_eq = rules[0].constructor.get_equation(F0, (F1,))
    expected_eq = Eq(
        F0, (k_0 * F1 - k_1 * F1.subs({k_0: k_1})) / (k_0 - k_1) - F1.subs({k_0: k_1})
    )
    assert eq_equality(actual_eq, expected_eq)

    t10 = easy_fusable(
        pos_right=True, track_left=True, track_right=True, same_tracking=False
    )
    rules = list(FusionFactory()(t10))
    assert len(rules) == 1
    F0 = Function("F0")(x, k_0, k_1)
    F1 = Function("F1")(x, k_0)
    actual_eq = rules[0].constructor.get_equation(F0, (F1,))
    expected_eq = Eq(F0, (k_0 * F1 - k_1 * F1.subs({k_0: k_1})) / (k_0 - k_1) - F1)
    assert eq_equality(actual_eq, expected_eq)

    t12 = easy_fusable(pos_left=True, pos_right=True, track_left=True)
    rules = list(FusionFactory()(t12))
    assert len(rules) == 1
    F0 = Function("F0")(x, k_0)
    F1 = Function("F1")(x, k_0)
    actual_eq = rules[0].constructor.get_equation(F0, (F1,))
    expected_eq = Eq(
        F0, (k_0 * F1 - F1.subs({k_0: 1})) / (k_0 - 1) - F1 - F1.subs({k_0: 1})
    )
    assert eq_equality(actual_eq, expected_eq)

    t14 = easy_fusable(
        pos_left=True,
        pos_right=True,
        track_left=True,
        track_right=True,
        same_tracking=False,
    )
    rules = list(FusionFactory()(t14))
    assert len(rules) == 1
    F0 = Function("F0")(x, k_0, k_1)
    F1 = Function("F1")(x, k_0)
    actual_eq = rules[0].constructor.get_equation(F0, (F1,))
    expected_eq = Eq(
        F0,
        (k_0 * F1 - k_1 * F1.subs({k_0: k_1})) / (k_0 - k_1) - F1 - F1.subs({k_0: k_1}),
    )
    assert eq_equality(actual_eq, expected_eq)


def test_indexed_forward_map():
    assert FusionStrategy(col_idx=0, tracked=True)(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((0, 0), (1, 0))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
        )
    ).indexed_forward_map(
        GriddedPerm(
            (6, 5, 4, 3, 1, 0, 2),
            ((0, 0), (0, 0), (0, 0), (1, 0), (1, 0), (1, 0), (2, 0)),
        )
    ) == (
        (
            GriddedPerm(
                (6, 5, 4, 3, 1, 0, 2),
                ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (1, 0)),
            ),
        ),
        3,
    )


def test_indexed_backward_map():
    r = FusionStrategy(col_idx=0, tracked=True)(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((0, 0), (1, 0))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
        )
    )
    order = [
        GriddedPerm(
            (6, 5, 4, 3, 1, 0, 2),
            ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (2, 0)),
        ),
        GriddedPerm(
            (6, 5, 4, 3, 1, 0, 2),
            ((0, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (2, 0)),
        ),
        GriddedPerm(
            (6, 5, 4, 3, 1, 0, 2),
            ((0, 0), (0, 0), (1, 0), (1, 0), (1, 0), (1, 0), (2, 0)),
        ),
        GriddedPerm(
            (6, 5, 4, 3, 1, 0, 2),
            ((0, 0), (0, 0), (0, 0), (1, 0), (1, 0), (1, 0), (2, 0)),
        ),
        GriddedPerm(
            (6, 5, 4, 3, 1, 0, 2),
            ((0, 0), (0, 0), (0, 0), (0, 0), (1, 0), (1, 0), (2, 0)),
        ),
        GriddedPerm(
            (6, 5, 4, 3, 1, 0, 2),
            ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (1, 0), (2, 0)),
        ),
        GriddedPerm(
            (6, 5, 4, 3, 1, 0, 2),
            ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (2, 0)),
        ),
    ]
    gp = GriddedPerm(
        (6, 5, 4, 3, 1, 0, 2), ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (1, 0))
    )
    assert all(
        r.indexed_backward_map((gp,), i) == target for i, target in enumerate(order)
    )
    assert all(
        r.indexed_backward_map((gp,), i, True) == target
        for i, target in enumerate(reversed(order))
    )


def column_fusion(tiling):
    """The rule fusing the tiling's columns 0 and 1."""
    rules = [
        rule
        for rule in FusionFactory()(tiling)
        if rule.formal_step == "fuse columns 0 and 1"
    ]
    assert len(rules) == 1
    return rules[0]


def objects_series(tiling, parameters, x, largest):
    """The tiling's objects of size at most largest, as a polynomial in x and the
    parameters."""
    total = 0
    for size in range(largest + 1):
        for gridded_perm in tiling.objects_of_size(size):
            term = x**size
            for parameter, value in zip(
                parameters, tiling.get_parameters(gridded_perm)
            ):
                term *= parameter**value
            total += term
    return expand(total)


def equation_gives_the_parent(rule, largest=4):
    """Whether the rule's equation, expanded with the child's objects, gives the
    parent's objects of each size up to largest, monomial by monomial in the
    parent's parameters."""
    x = var("x")
    parent, child = rule.comb_class, rule.children[0]
    parent_parameters = [var(name) for name in parent.extra_parameters]
    child_parameters = [var(name) for name in child.extra_parameters]
    child_function = Function("F1")
    equation = rule.constructor.get_equation(
        Function("F0")(x, *parent_parameters),
        (child_function(x, *child_parameters),),
    )
    child_series = objects_series(child, child_parameters, x, largest)
    expanded = expand(
        equation.rhs.replace(
            child_function, Lambda((x, *child_parameters), child_series)
        ).doit()
    )
    parent_series = objects_series(parent, parent_parameters, x, largest)
    return all(
        expand(cancel(expanded.coeff(x, size) - parent_series.coeff(x, size))) == 0
        for size in range(largest + 1)
    )


@pytest.mark.parametrize("side", [(0, 0), (1, 0)], ids=["left", "right"])
def test_fusion_one_sided_beyond_the_region(side):
    """One parameter of the parent tracks a side of the region, the left cell or
    the right one, and the cell (2, 0) beside the region together. It is
    one-sided, so the equation stays the divided difference, though both sides of
    the region are given the value 1."""
    tiling = easy_fusable(tracked_beyond=[[side, (2, 0)]])
    assert equation_gives_the_parent(column_fusion(tiling))


def test_fusion_both_sides_tracked_beside_a_tracked_cell():
    """The parent tracks the two sides of the region apart, k_0 and k_1, and a cell
    (2, 0) beside it, k_2, which the child's k_1 is given while its k_0 is given the
    sides' values: substituting one name at a time would give k_0's place the value
    of k_1 and then that of k_2, so the child's parameters must be substituted
    simultaneously."""
    tiling = easy_fusable(track_left=True, track_right=True, tracked_beyond=[[(2, 0)]])
    assert equation_gives_the_parent(column_fusion(tiling))


TRACKINGS = {
    "untracked": {},
    "left tracked": {"track_left": True},
    "right tracked": {"track_right": True},
    "both tracked apart": {"track_left": True, "track_right": True},
    "both tracked together": {
        "track_left": True,
        "track_right": True,
        "same_tracking": True,
    },
}
POSITIVES = {
    "none positive": {},
    "left positive": {"pos_left": True},
    "right positive": {"pos_right": True},
    "both positive": {"pos_left": True, "pos_right": True},
    "either positive": {"pos_either": True},
}


SAME_VALUE = ("untracked", "both tracked together")  # both sides given the same value


@pytest.mark.parametrize(
    "tracking", [name for name in TRACKINGS if name not in SAME_VALUE]
)
@pytest.mark.parametrize("positive", POSITIVES)
def test_fusion_equation_counts(tracking, positive):
    """The equation of each of easy_fusable's fusions with a one-sided parameter,
    against the objects."""
    tiling = easy_fusable(**TRACKINGS[tracking], **POSITIVES[positive])
    assert equation_gives_the_parent(column_fusion(tiling))


@pytest.mark.parametrize("tracking", SAME_VALUE)
@pytest.mark.parametrize("positive", POSITIVES)
def test_fusion_with_both_sides_the_same_value(tracking, positive):
    """A fusion whose two sides are given the same value, its parent untracked or
    tracking the whole region, has no equation, and the error says so."""
    tiling = easy_fusable(**TRACKINGS[tracking], **POSITIVES[positive])
    with pytest.raises(NotImplementedError, match="given the same value"):
        equation_gives_the_parent(column_fusion(tiling))


@pytest.mark.parametrize(
    "fusion",
    ["row_fusion", "col_fusion", "component_row_fusion", "component_col_fusion"],
)
def test_fusion_of_fixtures_with_both_sides_the_same_value(request, fusion):
    """The fusions of small_tiling, whose fused rows and columns have two cells
    each, and the component fusions, their parents untracked, have no equation."""
    with pytest.raises(NotImplementedError, match="given the same value"):
        equation_gives_the_parent(request.getfixturevalue(fusion))

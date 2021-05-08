import pytest
from sympy import Eq, Function, var

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
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0,), ((2, 0),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0,), ((3, 0),)),
            GriddedPerm((0,), ((3, 1),)),
            GriddedPerm((0,), ((4, 0),)),
            GriddedPerm((0,), ((4, 2),)),
            GriddedPerm((0, 1), ((1, 0), (2, 2))),
            GriddedPerm((0, 1), ((1, 0), (3, 2))),
            GriddedPerm((1, 0), ((4, 1), (4, 1))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (2, 2))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (3, 2))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 1), (4, 1))),
            GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 1), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((0, 2, 1), ((2, 2), (2, 2), (3, 2))),
            GriddedPerm((0, 2, 1), ((2, 2), (3, 2), (3, 2))),
            GriddedPerm((0, 2, 1), ((3, 2), (3, 2), (3, 2))),
            GriddedPerm((1, 0, 2), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((1, 0, 2), ((2, 2), (2, 2), (3, 2))),
            GriddedPerm((1, 0, 2), ((2, 2), (3, 2), (3, 2))),
            GriddedPerm((1, 0, 2), ((3, 2), (3, 2), (3, 2))),
        ),
        requirements=((GriddedPerm((0,), ((2, 2),)), GriddedPerm((0,), ((3, 2),))),),
        assumptions=(),
    )
    strategy = FusionStrategy(col_idx=2, tracked=True)
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
):
    if same_tracking:
        assert track_left and track_right
    obs = [
        GriddedPerm.single_cell((0, 1), (0, 0)),
        GriddedPerm((0, 1), ((0, 0), (1, 0))),
        GriddedPerm.single_cell((0, 1), (1, 0)),
    ]

    reqs = []
    if pos_left:
        reqs.append([GriddedPerm.single_cell((0,), (0, 0))])
    if pos_right:
        reqs.append([GriddedPerm.single_cell((0,), (1, 0))])

    ass = []
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


def test_fusion_gfs():

    x = var("x")
    k_0 = var("k_0")
    k_1 = var("k_1")

    def eq_equality(e1, e2):
        return (e1.rhs - e2.rhs).simplify() == 0

    t1 = easy_fusable()
    rules = list(FusionFactory()(t1))
    assert len(rules) == 1
    # EQ NOT IMPLEMENTED

    t2 = easy_fusable(track_left=True)
    rules = list(FusionFactory()(t2))
    assert len(rules) == 1
    F0 = Function("F0")(x)
    F1 = Function("F1")(x, k_0)
    actual_eq = rules[0].constructor.get_equation(F0, (F1,))
    expected_eq = Eq(F0, (k_0 * F1 - F1.subs({k_0: 1})) / (k_0 - 1))
    assert eq_equality(actual_eq, expected_eq)

    t3 = easy_fusable(track_left=True, track_right=True, same_tracking=True)
    rules = list(FusionFactory()(t3))
    assert len(rules) == 1
    # EQ NOT IMPLEMENTED

    t4 = easy_fusable(track_left=True, track_right=True, same_tracking=False)
    rules = list(FusionFactory()(t4))
    assert len(rules) == 1
    F0 = Function("F0")(x, k_0, k_1)
    F1 = Function("F1")(x, k_0)
    actual_eq = rules[0].constructor.get_equation(F0, (F1,))
    expected_eq = Eq(F0, (k_0 * F1 - k_1 * F1.subs({k_0: k_1})) / (k_0 - k_1))
    assert eq_equality(actual_eq, expected_eq)

    t5 = easy_fusable(pos_left=True)
    rules = list(FusionFactory()(t5))
    assert len(rules) == 1
    # EQ NOT IMPLEMENTED

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

    t8 = easy_fusable(
        pos_left=True, track_left=True, track_right=True, same_tracking=True
    )
    rules = list(FusionFactory()(t8))
    assert len(rules) == 1
    # EQ NOT IMPLEMENTED

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

    t11 = easy_fusable(pos_left=True, pos_right=True)
    rules = list(FusionFactory()(t11))
    assert len(rules) == 1
    # EQ NOT IMPLEMENTED

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

    t13 = easy_fusable(
        pos_left=True,
        pos_right=True,
        track_left=True,
        track_right=True,
        same_tracking=True,
    )
    rules = list(FusionFactory()(t13))
    assert len(rules) == 1
    # EQ NOT IMPLEMENTED

    t14 = easy_fusable(
        pos_left=True,
        pos_right=True,
        track_left=True,
        track_right=True,
        same_tracking=False,
    )
    rules = list(FusionFactory()(t14))
    assert len(rules) == 1
    # EQ NOT IMPLEMENTED
    F0 = Function("F0")(x, k_0, k_1)
    F1 = Function("F1")(x, k_0)
    actual_eq = rules[0].constructor.get_equation(F0, (F1,))
    expected_eq = Eq(
        F0,
        (k_0 * F1 - k_1 * F1.subs({k_0: k_1})) / (k_0 - k_1) - F1 - F1.subs({k_0: k_1}),
    )
    assert eq_equality(actual_eq, expected_eq)

    # TODO: Add tests for the versions where there is a list requirement with a point
    # in each cell. Equations for this are not currently implemented.


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

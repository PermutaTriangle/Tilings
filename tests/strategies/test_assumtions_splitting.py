from sympy import Eq, Function, var

from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.strategies import SplittingStrategy

t = Tiling(
    obstructions=[
        GriddedPerm.single_cell(Perm((0, 1, 2)), (0, 0)),
        GriddedPerm.single_cell(Perm((0, 1)), (1, 0)),
        GriddedPerm.single_cell(Perm((0, 1, 2)), (2, 1)),
        GriddedPerm.single_cell(Perm((0, 1, 2)), (3, 1)),
    ],
    assumptions=[
        TrackingAssumption(
            [
                GriddedPerm.point_perm((0, 0)),
                GriddedPerm.point_perm((1, 0)),
                GriddedPerm.point_perm((2, 1)),
                GriddedPerm.point_perm((3, 1)),
            ]
        )
    ],
)


def test_no_interleaving():
    strat = SplittingStrategy(interleaving="none")
    rule = strat(t)
    assert len(rule.children) == 1
    child = rule.children[0]
    assert len(child.assumptions) == 2
    assert (
        TrackingAssumption(
            [GriddedPerm.point_perm((0, 0)), GriddedPerm.point_perm((1, 0))]
        )
        in child.assumptions
    )
    assert (
        TrackingAssumption(
            [GriddedPerm.point_perm((2, 1)), GriddedPerm.point_perm((3, 1))]
        )
        in child.assumptions
    )


def test_montone_interleaving():
    strat = SplittingStrategy(interleaving="monotone")
    rule = strat(t)
    assert len(rule.children) == 1
    child = rule.children[0]
    assert len(child.assumptions) == 3
    assert TrackingAssumption([GriddedPerm.point_perm((0, 0))]) in child.assumptions
    assert TrackingAssumption([GriddedPerm.point_perm((1, 0))]) in child.assumptions
    assert (
        TrackingAssumption(
            [GriddedPerm.point_perm((2, 1)), GriddedPerm.point_perm((3, 1))]
        )
        in child.assumptions
    )


def test_any_interleaving():
    strat = SplittingStrategy(interleaving="all")
    rule = strat(t)
    assert len(rule.children) == 1
    child = rule.children[0]
    assert len(child.assumptions) == 4
    assert TrackingAssumption([GriddedPerm.point_perm((0, 0))]) in child.assumptions
    assert TrackingAssumption([GriddedPerm.point_perm((1, 0))]) in child.assumptions
    assert TrackingAssumption([GriddedPerm.point_perm((2, 1))]) in child.assumptions
    assert TrackingAssumption([GriddedPerm.point_perm((3, 1))]) in child.assumptions


def test_splitting_gf():
    parent = Tiling(
        obstructions=(
            GriddedPerm.single_cell(Perm((0, 1)), (0, 1)),
            GriddedPerm.single_cell(Perm((0, 1)), (1, 0)),
        ),
        assumptions=(
            TrackingAssumption(
                [GriddedPerm.point_perm((0, 1)), GriddedPerm.point_perm((1, 0)),]
            ),
            TrackingAssumption([GriddedPerm.point_perm((1, 0)),]),
        ),
    )
    child = Tiling(
        obstructions=(
            GriddedPerm.single_cell(Perm((0, 1)), (0, 1)),
            GriddedPerm.single_cell(Perm((0, 1)), (1, 0)),
        ),
        assumptions=(
            TrackingAssumption([GriddedPerm.point_perm((0, 1))]),
            TrackingAssumption([GriddedPerm.point_perm((1, 0)),]),
        ),
    )
    strat = SplittingStrategy()
    rule = strat(parent)
    x, k0, k1 = var("x k_0 k_1")
    parent_func = Function("F_0")(x, k0, k1)
    child_func = Function("F_1")(x, k0, k1)
    expected_eq = Eq(parent_func, child_func.subs({k1: k0 * k1}))

    assert len(rule.children) == 1
    assert rule.children[0] == child
    assert rule.constructor.get_equation(parent_func, (child_func,)) == expected_eq

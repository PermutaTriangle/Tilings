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

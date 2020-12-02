from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.strategies.rearrange_assumption import RearrangeAssumptionStrategy


def test_rearrange():
    ass1 = TrackingAssumption([GriddedPerm((0,), ((0, 0),))])
    ass2 = TrackingAssumption(
        [GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))]
    )
    strat = RearrangeAssumptionStrategy(ass2, ass1)
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0),) * 2),
            GriddedPerm((0, 1), ((1, 0),) * 2),
        ],
        assumptions=[ass1, ass2],
    )
    rule = strat(t)
    print(rule)
    for i in range(5):
        rule.sanity_check(i)

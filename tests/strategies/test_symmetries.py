from tilings import GriddedPerm, Tiling
from tilings.strategies.symmetry import SymmetriesFactory


def test_symmetries():
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((1, 1), (1, 1))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 2), (0, 0))),
            GriddedPerm((1, 3, 0, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((1, 3, 0, 2), ((0, 2), (0, 2), (0, 0), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 2),) * 3),
        ),
        requirements=((GriddedPerm((0,), ((1, 1),)),),),
        assumptions=(),
    )
    for strat in SymmetriesFactory()(t):
        rule = strat(t)
        rule.sanity_check(1)
        rule.sanity_check(4)

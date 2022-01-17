from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.strategies.sliding import SlidingFactory

tiling = Tiling(
    obstructions=(
        GriddedPerm((0, 1), ((2, 0), (2, 0))),
        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (3, 0))),
        GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (3, 0))),
        GriddedPerm((0, 1, 2), ((1, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 2), ((2, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (3, 0))),
        GriddedPerm((3, 0, 1, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
        GriddedPerm((3, 0, 1, 2), ((0, 0), (0, 0), (0, 0), (1, 0))),
        GriddedPerm((3, 0, 1, 2), ((0, 0), (0, 0), (0, 0), (2, 0))),
        GriddedPerm((3, 0, 1, 2), ((0, 0), (0, 0), (0, 0), (3, 0))),
        GriddedPerm((3, 0, 1, 2), ((0, 0), (0, 0), (1, 0), (1, 0))),
        GriddedPerm((3, 0, 1, 2), ((0, 0), (0, 0), (1, 0), (2, 0))),
        GriddedPerm((3, 0, 1, 2), ((0, 0), (0, 0), (1, 0), (3, 0))),
        GriddedPerm((3, 0, 1, 2), ((0, 0), (0, 0), (2, 0), (3, 0))),
        GriddedPerm((3, 0, 1, 2), ((0, 0), (0, 0), (3, 0), (3, 0))),
    ),
    requirements=(),
    assumptions=(
        TrackingAssumption(
            (GriddedPerm((0,), ((2, 0),)), GriddedPerm((0,), ((3, 0),)))
        ),
        TrackingAssumption((GriddedPerm((0,), ((3, 0),)),)),
    ),
)


def sanity_checker(rules):
    found_some = False
    for rule in rules:
        found_some = True
        for length in range(5):
            rule.sanity_check(length)
    return found_some


def test_sliding_factory():
    assert sanity_checker(SlidingFactory(True)(tiling))
    assert sanity_checker(SlidingFactory(True)(tiling.reverse()))
    assert sanity_checker(SlidingFactory(True)(tiling.rotate90()))
    assert sanity_checker(SlidingFactory(True)(tiling.rotate90().reverse()))

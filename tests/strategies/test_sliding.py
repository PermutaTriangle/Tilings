from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.strategies.monotone_sliding import MonotoneSlidingFactory
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

noslidetiling1 = Tiling(
    obstructions=(
        GriddedPerm((0, 1), ((0, 0), (0, 0))),
        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
        GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((0, 1, 3, 2), ((2, 0), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((0, 1, 2, 3, 4), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 2, 4, 3), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 3, 2, 4), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 3, 4, 2), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 4, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 4, 3, 2), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 2, 3, 4, 1), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 2, 4, 3, 1), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (3, 0))),
        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (3, 0))),
        GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (3, 0))),
        GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (3, 0))),
        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (3, 0))),
        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (3, 0))),
        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (3, 0), (3, 0))),
    ),
    requirements=(),
    assumptions=[TrackingAssumption((GriddedPerm((0,), ((0, 0),)),))],
)

noslidetiling2 = Tiling(
    obstructions=(
        GriddedPerm((0, 1), ((1, 0), (1, 0))),
        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
        GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((0, 1, 3, 2), ((2, 0), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((0, 1, 2, 3, 4), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 2, 4, 3), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 3, 2, 4), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 3, 4, 2), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 4, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 4, 3, 2), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 2, 3, 4, 1), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 2, 4, 3, 1), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (3, 0))),
        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (3, 0))),
        GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (3, 0))),
        GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (3, 0))),
        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (3, 0))),
        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (3, 0))),
        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (3, 0), (3, 0))),
    ),
    requirements=(),
    assumptions=[TrackingAssumption((GriddedPerm((0,), ((1, 0),)),))],
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


def test_monotone_sliding_factory():
    assert list(MonotoneSlidingFactory()(noslidetiling1)) == []
    assert list(MonotoneSlidingFactory()(noslidetiling2)) == []
    assert sanity_checker(MonotoneSlidingFactory()(tiling))
    assert sanity_checker(MonotoneSlidingFactory()(tiling.rotate90()))
    assert sanity_checker(MonotoneSlidingFactory()(tiling.rotate180()))
    assert sanity_checker(MonotoneSlidingFactory()(tiling.rotate270()))

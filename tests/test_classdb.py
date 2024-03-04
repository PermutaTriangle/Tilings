from tilings.assumptions import SkewComponentAssumption, TrackingAssumption
from tilings.griddedperm import GriddedPerm
from tilings.tilescope import TrackedClassDB
from tilings.tiling import Tiling


def test_tracked_classdb():
    tiling = Tiling(
        obstructions=(
            GriddedPerm((1, 0, 2), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 0), (1, 0), (1, 0))),
        ),
        requirements=(),
        assumptions=(
            SkewComponentAssumption((GriddedPerm((0,), ((1, 0),)),)),
            TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),
        ),
    )
    tracked_classdb = TrackedClassDB()
    tracked_classdb.add(tiling)
    new_tiling = tracked_classdb.get_class(0)
    assert tiling == new_tiling

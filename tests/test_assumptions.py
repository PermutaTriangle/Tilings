import json
import pytest

from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption


@pytest.fixture
def tplaced():
    t = Tiling.from_string("123")
    return t.place_point_in_cell((0, 0), 1)


@pytest.fixture
def tplaced_tracked(tplaced):
    return Tiling(
        tplaced.obstructions,
        tplaced.requirements,
        [
            TrackingAssumption([GriddedPerm.single_cell(Perm((0,)), (0, 0))]),
            TrackingAssumption([GriddedPerm.single_cell(Perm((0,)), (0, 0))]),
            TrackingAssumption([GriddedPerm.single_cell(Perm((0,)), (2, 0))]),
        ],
    )


def test_bytes(tplaced, tplaced_tracked):

    assert len(tplaced.assumptions) == 0
    remade = Tiling.from_bytes(tplaced.to_bytes())
    assert remade == tplaced

    assert len(tplaced_tracked.assumptions) == 2
    remade = Tiling.from_bytes(tplaced_tracked.to_bytes())
    assert remade == tplaced_tracked

    assert tplaced != tplaced_tracked
    assert (
        Tiling.from_json(json.dumps(tplaced_tracked.to_jsonable())) == tplaced_tracked
    )

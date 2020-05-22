import json

import pytest

from comb_spec_searcher import CombinatorialSpecification
from comb_spec_searcher.exception import ExceededMaxtimeError
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Factor
from tilings.assumptions import TrackingAssumption
from tilings.strategy_pack import TileScopePack
from tilings.tilescope import TileScope


@pytest.fixture
def tplaced():
    t = Tiling.from_string("132")
    return t.place_point_in_cell((0, 0), 1)


@pytest.fixture
def tplaced_factored1(tplaced):
    return tplaced.sub_tiling([(0, 0), (2, 0)])


@pytest.fixture
def tplaced_factored2(tplaced):
    return tplaced.sub_tiling([(1, 1)])


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


@pytest.fixture
def tplaced_tracked_factored1(tplaced_tracked):
    return tplaced_tracked.sub_tiling([(0, 0), (2, 0)])


@pytest.fixture
def tplaced_tracked_factored2(tplaced_tracked):
    return tplaced_tracked.sub_tiling([(1, 1)])


@pytest.fixture
def all_tilings(
    tplaced,
    tplaced_factored1,
    tplaced_factored2,
    tplaced_tracked,
    tplaced_tracked_factored1,
    tplaced_tracked_factored2,
):
    return [
        tplaced,
        tplaced_factored1,
        tplaced_factored2,
        tplaced_tracked,
        tplaced_tracked_factored1,
        tplaced_tracked_factored2,
    ]


def test_bytes(tplaced, tplaced_tracked, all_tilings):

    assert len(tplaced.assumptions) == 0
    remade = Tiling.from_bytes(tplaced.to_bytes())
    assert tplaced != tplaced_tracked

    assert len(tplaced_tracked.assumptions) == 2

    for tiling in all_tilings:
        remade = Tiling.from_bytes(tiling.to_bytes())
        assert remade == tiling


def test_json(all_tilings):
    for tiling in all_tilings:
        assert Tiling.from_json(json.dumps(tiling.to_jsonable())) == tiling


def test_factors(
    tplaced_tracked, tplaced_tracked_factored1, tplaced_tracked_factored2,
):
    assert len(tplaced_tracked_factored1.assumptions) == 2

    assert all(
        isinstance(ass, TrackingAssumption)
        for ass in tplaced_tracked_factored1.assumptions
    )
    assert tplaced_tracked_factored1.assumptions[0].gps == (
        GriddedPerm.single_cell(Perm((0,)), (0, 0)),
    )
    assert tplaced_tracked_factored1.assumptions[1].gps == (
        GriddedPerm.single_cell(Perm((0,)), (1, 0)),
    )

    assert set(Factor(tplaced_tracked).factors()) == set(
        [tplaced_tracked_factored1, tplaced_tracked_factored2]
    )


@pytest.mark.timeout(60)
def test_123_fusion():
    point_placements = TileScopePack.point_placements().make_fusion(tracked=True)
    css = TileScope("123", point_placements)
    with pytest.raises(ExceededMaxtimeError):
        spec = css.auto_search(max_time=30)
        assert isinstance(spec, CombinatorialSpecification)

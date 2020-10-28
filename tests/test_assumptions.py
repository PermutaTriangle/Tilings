import json
import os

import pytest

from comb_spec_searcher import CombinatorialSpecification
from permuta import Av, Perm
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
            TrackingAssumption([GriddedPerm.single_cell((0,), (0, 0))]),
            TrackingAssumption([GriddedPerm.single_cell((0,), (0, 0))]),
            TrackingAssumption([GriddedPerm.single_cell((0,), (2, 0))]),
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


def test_factors(tplaced_tracked, tplaced_tracked_factored1, tplaced_tracked_factored2):
    assert len(tplaced_tracked_factored1.assumptions) == 2

    assert all(
        isinstance(ass, TrackingAssumption)
        for ass in tplaced_tracked_factored1.assumptions
    )
    assert tplaced_tracked_factored1.assumptions[0].gps == (
        GriddedPerm.single_cell((0,), (0, 0)),
    )
    assert tplaced_tracked_factored1.assumptions[1].gps == (
        GriddedPerm.single_cell((0,), (1, 0)),
    )

    assert set(Factor(tplaced_tracked).factors()) == set(
        [tplaced_tracked_factored1, tplaced_tracked_factored2]
    )


@pytest.mark.timeout(90)
def test_123_fusion():
    pack = TileScopePack.row_and_col_placements(row_only=True).make_fusion(tracked=True)
    css = TileScope("123", pack)
    spec = css.auto_search(status_update=30)
    spec.expand_verified()
    assert isinstance(spec, CombinatorialSpecification)
    assert [spec.count_objects_of_size(i) for i in range(20)] == [
        1,
        1,
        2,
        5,
        14,
        42,
        132,
        429,
        1430,
        4862,
        16796,
        58786,
        208012,
        742900,
        2674440,
        9694845,
        35357670,
        129644790,
        477638700,
        1767263190,
    ]
    av = Av([Perm((0, 1, 2))])
    for i in range(10):
        assert set(av.of_length(i)) == set(
            gp.patt for gp in spec.generate_objects_of_size(i)
        )
        assert spec.random_sample_object_of_size(i).patt in av


@pytest.mark.timeout(60)
def test_123_positive_fusions():
    pack = TileScopePack.insertion_row_and_col_placements(row_only=True).make_fusion(
        tracked=True, apply_first=True
    )
    css = TileScope("123", pack)
    spec = css.auto_search(status_update=30)
    spec.expand_verified()
    print(spec)
    assert isinstance(spec, CombinatorialSpecification)
    assert [spec.count_objects_of_size(i) for i in range(20)] == [
        1,
        1,
        2,
        5,
        14,
        42,
        132,
        429,
        1430,
        4862,
        16796,
        58786,
        208012,
        742900,
        2674440,
        9694845,
        35357670,
        129644790,
        477638700,
        1767263190,
    ]
    av = Av([Perm((0, 1, 2))])
    for i in range(10):
        assert set(av.of_length(i)) == set(
            gp.patt for gp in spec.generate_objects_of_size(i)
        )
        assert spec.random_sample_object_of_size(i).patt in av


@pytest.mark.timeout(60)
def test_123_interleaving():
    pack = TileScopePack.point_placements().make_interleaving()
    css = TileScope("123", pack)
    spec = css.auto_search(status_update=30)
    spec.expand_verified()
    assert isinstance(spec, CombinatorialSpecification)
    assert [spec.count_objects_of_size(i) for i in range(20)] == [
        1,
        1,
        2,
        5,
        14,
        42,
        132,
        429,
        1430,
        4862,
        16796,
        58786,
        208012,
        742900,
        2674440,
        9694845,
        35357670,
        129644790,
        477638700,
        1767263190,
    ]


@pytest.mark.timeout(120)
def test_1234_fusion():
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    with open(os.path.join(__location__, "spec-1234.json")) as f:
        d = json.loads(f.read())
    spec = CombinatorialSpecification.from_dict(d)
    assert isinstance(spec, CombinatorialSpecification)
    assert not any("NOTIMPLEMENTED" in str(eq.rhs) for eq in spec.get_equations())
    assert [spec.count_objects_of_size(i) for i in range(15)] == [
        1,
        1,
        2,
        6,
        23,
        103,
        513,
        2761,
        15767,
        94359,
        586590,
        3763290,
        24792705,
        167078577,
        1148208090,
    ]
    av = Av([Perm((0, 1, 2, 3))])
    for i in range(10):
        assert set(av.of_length(i)) == set(
            gp.patt for gp in spec.generate_objects_of_size(i)
        )
        assert spec.random_sample_object_of_size(i).patt in av

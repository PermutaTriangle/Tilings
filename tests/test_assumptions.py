import json
import os
import pickle

import pytest

from comb_spec_searcher import CombinatorialSpecification
from permuta import Av, Perm
from tilings import GriddedPerm, Tiling
from tilings.map import RowColMap
from tilings.parameter_counter import ParameterCounter, PreimageCounter
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
    preimg0 = PreimageCounter(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (3, 0))),
                GriddedPerm((0, 1), ((1, 0), (3, 0))),
                GriddedPerm((0, 1), ((2, 1), (2, 1))),
                GriddedPerm((1, 0), ((2, 1), (2, 1))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 1), ((3, 0), (3, 0), (3, 0))),
            ),
            requirements=((GriddedPerm((0,), ((2, 1),)),),),
            parameters=(),
        ),
        RowColMap({0: 0, 1: 1}, {0: 0, 1: 0, 2: 1, 3: 2}),
    )
    preimg2 = PreimageCounter(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (2, 0))),
                GriddedPerm((0, 1), ((0, 0), (3, 0))),
                GriddedPerm((0, 1), ((1, 1), (1, 1))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((2, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((3, 0), (3, 0), (3, 0))),
            ),
            requirements=((GriddedPerm((0,), ((1, 1),)),),),
            parameters=(),
        ),
        RowColMap({0: 0, 1: 1}, {0: 0, 1: 1, 2: 2, 3: 2}),
    )

    return tplaced.add_parameters(
        [
            ParameterCounter([preimg0]),
            ParameterCounter([preimg2]),
        ]
    )


@pytest.fixture
def tplaced_tracked_factors(tplaced_tracked):
    return tplaced_tracked.find_factors()


@pytest.fixture
def all_tilings(
    tplaced,
    tplaced_factored1,
    tplaced_factored2,
    tplaced_tracked,
    tplaced_tracked_factors,
):
    tilings = [
        tplaced,
        tplaced_factored1,
        tplaced_factored2,
        tplaced_tracked,
    ]
    tilings.extend(tplaced_tracked_factors)
    return tilings


@pytest.mark.xfail
def test_bytes(tplaced, tplaced_tracked, all_tilings):

    assert len(tplaced.assumptions) == 0
    remade = Tiling.from_bytes(tplaced.to_bytes())
    assert tplaced != tplaced_tracked

    assert len(tplaced_tracked.assumptions) == 2

    for tiling in all_tilings:
        remade = Tiling.from_bytes(tiling.to_bytes())
        assert remade == tiling


@pytest.mark.xfail
def test_json(all_tilings):
    for tiling in all_tilings:
        assert Tiling.from_json(json.dumps(tiling.to_jsonable())) == tiling


def test_factors(tplaced_tracked, tplaced_tracked_factors):
    assert sorted(len(f.parameters) for f in tplaced_tracked_factors) == [0, 2]

    main_factor = next(f for f in tplaced_tracked_factors if f.dimensions == (2, 1))

    assert all(isinstance(ass, ParameterCounter) for ass in main_factor.parameters)
    assert main_factor.parameters[0] == ParameterCounter(
        (
            PreimageCounter(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((0, 0), (1, 0))),
                        GriddedPerm((0, 1), ((0, 0), (2, 0))),
                        GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 2, 1), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    parameters=(),
                ),
                RowColMap({0: 0}, {0: 0, 1: 1, 2: 1}),
            ),
        )
    )
    assert main_factor.parameters[1] == ParameterCounter(
        (
            PreimageCounter(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((0, 0), (2, 0))),
                        GriddedPerm((0, 1), ((1, 0), (2, 0))),
                        GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    parameters=(),
                ),
                RowColMap({0: 0}, {0: 0, 1: 0, 2: 1}),
            ),
        )
    )


@pytest.mark.timeout(90)
def test_123_fusion():
    pack = TileScopePack.row_and_col_placements(row_only=True).make_fusion(tracked=True)
    css = TileScope("123", pack)
    spec = css.auto_search(status_update=30)
    spec = spec.expand_verified()
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


@pytest.mark.timeout(90)
def test_123_ppfusion():
    pack = TileScopePack.point_placements().make_fusion(tracked=True)
    strat = pack.expansion_strats[0][1]
    assert strat.__class__.__name__ == "PatternPlacementFactory"
    strat.dirs = (0, 3)
    pack.initial_strats
    pack.ver_strats = pack.ver_strats[:1]
    css = TileScope("123", pack)
    spec = css.auto_search(status_update=30)
    assert isinstance(spec, CombinatorialSpecification)
    spec = spec.expand_verified()
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
    assert any(
        "fuse" in rule.formal_step and rule.comb_class.dimensions == (2, 2)
        for rule in spec
    )


@pytest.mark.xfail
@pytest.mark.timeout(90)
def test_123_fusion_generate_and_sample():
    av = Av([Perm((0, 1, 2))])
    pack = TileScopePack.row_and_col_placements(row_only=True).make_fusion(tracked=True)
    css = TileScope("123", pack)
    spec = css.auto_search(status_update=30)
    spec = spec.expand_verified()
    assert isinstance(spec, CombinatorialSpecification)
    for i in range(10):
        assert set(av.of_length(i)) == set(
            gp.patt for gp in spec.generate_objects_of_size(i)
        )
        assert spec.random_sample_object_of_size(i).patt in av


@pytest.mark.skip(reason="positive fusion not implemented")
@pytest.mark.timeout(60)
def test_123_positive_fusions():
    pack = TileScopePack.insertion_row_and_col_placements(row_only=True).make_fusion(
        tracked=True, apply_first=True
    )
    css = TileScope("123", pack)
    spec = css.auto_search(status_update=30)
    spec = spec.expand_verified()
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


@pytest.mark.skip(reason="interleaving factor not implemented")
@pytest.mark.timeout(60)
def test_123_interleaving():
    pack = TileScopePack.point_placements().make_interleaving()
    css = TileScope("123", pack)
    spec = css.auto_search(status_update=30)
    spec = spec.expand_verified()
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


@pytest.mark.xfail
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


@pytest.mark.xfail
def test_1234_pickle():
    """
    Test that the specification can be pickled.
    """
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    with open(os.path.join(__location__, "spec-1234.json")) as f:
        d = json.loads(f.read())
    spec = CombinatorialSpecification.from_dict(d)
    spec.count_objects_of_size(10)
    s = pickle.dumps(spec)
    new_spec = pickle.loads(s)
    assert new_spec == spec

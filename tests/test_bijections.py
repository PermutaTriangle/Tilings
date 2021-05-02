import json
import pathlib

import requests

from comb_spec_searcher import (
    AtomStrategy,
    CombinatorialSpecificationSearcher,
    StrategyPack,
    find_bijection_between,
)
from comb_spec_searcher.isomorphism import Bijection
from comb_spec_searcher.specification import CombinatorialSpecification
from tilings import GriddedPerm, Tiling
from tilings import strategies as strat
from tilings.strategies import BasicVerificationStrategy
from tilings.strategies.sliding import SlidingFactory
from tilings.tilescope import TileScope, TileScopePack


def _b2rc(basis: str) -> CombinatorialSpecificationSearcher:
    pack = TileScopePack.row_and_col_placements(row_only=True)
    pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
    searcher = TileScope(basis, pack)
    assert isinstance(searcher, CombinatorialSpecificationSearcher)
    return searcher


def _bijection_asserter(bi, max_size=7):
    assert bi is not None
    for i in range(max_size + 1):
        assert {bi.map(gp) for gp in bi.domain.generate_objects_of_size(i)} == set(
            bi.codomain.generate_objects_of_size(i)
        )
        assert {
            bi.inverse_map(gp) for gp in bi.codomain.generate_objects_of_size(i)
        } == set(bi.domain.generate_objects_of_size(i))
        for gp in bi.domain.generate_objects_of_size(i):
            assert bi.inverse_map(bi.map(gp)) == gp


def _tester(basis1: str, basis2: str, max_size=7):
    _bijection_asserter(
        find_bijection_between(_b2rc(basis1), _b2rc(basis2)),
        max_size,
    )


def _import_css_example():
    r = requests.get(
        "https://raw.githubusercontent.com/PermutaTriangle"
        "/comb_spec_searcher/develop/example.py"
    )
    r.raise_for_status()
    exec(r.text[: r.text.find("pack = StrategyPack(")], globals())


def test_bijection_1():
    _tester(
        "0132_0213_0231_0312_1302_1320_2031_2301_3021_3120",
        "0132_0213_0231_0321_1302_1320_2031_2301_3021_3120",
    )


def test_bijection_2():
    _tester(
        "0132_0213_0231_0312_0321_1032_1320_2301_3021_3120",
        "0132_0213_0231_0312_1032_1302_1320_2301_3021_3120",
    )


def test_bijection_3():
    _tester("132", "231", max_size=6)


def test_bijection_4():
    basis1 = "0132_0213_0231_0312_1032_1302_1320_2031_2301_3021_3120"
    basis2 = "0132_0213_0231_0312_0321_1302_1320_2031_2301_3021_3120"
    _tester(basis1, basis2)


def test_bijection_5():
    basis1 = "0132_0213_0231_0312_1032_1302_1320_2031_2301_3021_3120"
    basis2 = "0132_0213_0231_0312_0321_1230_1320_2031_2301_3021_3120"
    assert find_bijection_between(_b2rc(basis1), _b2rc(basis2)) is None


def test_bijection_6():
    _tester("231_312", "231_321")
    _tester("231_321", "132_312")


def test_bijection_7():
    _tester(
        "0132_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
        "0213_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    )
    _tester(
        "0132_0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        "0132_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    )
    _tester(
        "0132_0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        "0132_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    )
    _tester(
        "0132_0213_0231_0312_0321_1302_1320_2031_2301_3021_3120",
        "0132_0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
    )
    _tester(
        "0132_0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
        "0213_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    )
    _tester(
        "0132_0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
        "0213_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    )


def test_bijection_8_cross_domain():
    _import_css_example()
    # 231_321 after row placement and factoring
    t = Tiling(
        obstructions=(
            GriddedPerm((1, 0), ((0, 0), (1, 0))),
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),
        ),
        requirements=(),
        assumptions=(),
    )
    pack = TileScopePack.row_and_col_placements(row_only=True)
    pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
    pack.inferral_strats = ()
    searcher1 = TileScope(t, pack)

    pack = StrategyPack(
        initial_strats=[RemoveFrontOfPrefix()],
        inferral_strats=[],
        expansion_strats=[[ExpansionStrategy()]],
        ver_strats=[AtomStrategy()],
        name=("Finding specification for words avoiding consecutive patterns."),
    )
    start_class = AvoidingWithPrefix("", [], ["a", "b"])
    searcher2 = CombinatorialSpecificationSearcher(start_class, pack)
    _bijection_asserter(find_bijection_between(searcher2, searcher1))


def test_bijection_9_cross_domain():
    _import_css_example()
    # 231_312_321 after a single row placement + factoring
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((0, 0), (1, 0))),
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),
        ),
        requirements=(),
        assumptions=(),
    )
    pack = TileScopePack(
        initial_strats=[
            strat.FactorFactory(unions=True, workable=False, ignore_parent=False),
        ],
        ver_strats=[
            strat.BasicVerificationStrategy(),
            # strat.OneByOneVerificationStrategy(), # gives left spec
        ],
        inferral_strats=[],
        expansion_strats=[
            [
                strat.RowAndColumnPlacementFactory(
                    place_row=True, place_col=False, partial=False
                ),
            ],
        ],
        name=".............",
    )
    searcher1 = TileScope(t, pack)
    pack = StrategyPack(
        initial_strats=[RemoveFrontOfPrefix()],
        inferral_strats=[],
        expansion_strats=[[ExpansionStrategy()]],
        ver_strats=[AtomStrategy()],
        name=("Finding specification for words avoiding consecutive patterns."),
    )
    start_class = AvoidingWithPrefix("", ["bb"], ["a", "b"])
    searcher2 = CombinatorialSpecificationSearcher(start_class, pack)
    _bijection_asserter(find_bijection_between(searcher2, searcher1))


def test_bijection_10():
    pack1 = TileScopePack.requirement_placements()
    pack1 = pack1.add_verification(BasicVerificationStrategy(), replace=True)
    searcher1 = TileScope("132_4312", pack1)
    pack2 = TileScopePack.requirement_placements()
    pack2 = pack2.add_verification(BasicVerificationStrategy(), replace=True)
    searcher2 = TileScope("132_4231", pack2)
    _bijection_asserter(find_bijection_between(searcher1, searcher2))


def test_bijection_11():
    pairs = [
        (
            "0132_0213_0231_0312_0321_1302_1320_2031_2301_3120",
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
        ),
        (
            "0132_0213_0231_0312_0321_1302_1320_2031_2301_3120",
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
        ),
        (
            "0132_0213_0231_0312_0321_1302_1320_2301_3021_3120",
            "0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1032_1302_1320_2031_2301_3120",
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
        ),
        (
            "0132_0213_0231_0312_1032_1302_1320_2031_2301_3120",
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1032_1302_1320_2031_2301_3120",
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1032_1302_1320_2031_2301_3120",
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
        ),
        (
            "0132_0213_0231_0312_1032_1302_1320_2031_2301_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1302_1320_2031_2301_3021_3120",
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
        ),
        (
            "0132_0213_0231_0312_1302_1320_2031_2301_3021_3120",
            "0132_0213_0231_0321_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1302_1320_2031_2301_3021_3120",
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1302_1320_2031_2301_3021_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1302_1320_2031_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
            "0132_0231_0312_0321_1032_1302_1320_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
        ),
        (
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1302_1320_2031_2301_3021_3120",
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1302_1320_2031_2301_3021_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1302_1320_2031_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0132_0231_0312_0321_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0132_0231_0312_0321_1302_1320_2031_2301_3021_3120",
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_0321_1302_1320_2031_2301_3021_3120",
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_0321_1302_1320_2031_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
            "0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
    ]
    for basis1, basis2 in pairs:
        _tester(basis1, basis2, max_size=5)


def test_bijection_12():
    bases = [
        "321_2341",  # 0
        "321_3412",  # 1, pnt rowcol needed
        "321_3142",  # 2, pnt rowcol needed
        "132_1234",  # 3
        "132_4213",  # 4
        "132_4123",  # 5
        "132_3124",  # 6
        "132_2134",  # 7
        "132_3412",  # 8, pnt rowcol needed
    ]

    def _pntrcpls(b1, b2):
        pack = TileScopePack.point_and_row_and_col_placements(row_only=True)
        pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
        searcher1 = TileScope(b1, pack)
        searcher2 = TileScope(b2, pack)
        _bijection_asserter(find_bijection_between(searcher1, searcher2))

    _tester(bases[0], bases[4])
    _tester(bases[3], bases[4])
    _tester(bases[3], bases[5])
    _tester(bases[3], bases[6])
    _tester(bases[3], bases[7])
    _pntrcpls(bases[1], bases[5])
    _pntrcpls(bases[1], bases[2])
    _pntrcpls(bases[1], bases[8])


def test_bijection_13():
    pack = TileScopePack.point_and_row_and_col_placements(row_only=True)
    pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
    searcher1 = TileScope("0132_0213_0231_0321_1032_1320_2031_2301_3021_3120", pack)
    searcher2 = TileScope("0132_0213_0231_0312_0321_1302_1320_2031_2301_3120", pack)
    _bijection_asserter(find_bijection_between(searcher1, searcher2))


def test_bijection_14_json():
    # JSON with no assumption/fusion
    bi = find_bijection_between(
        _b2rc("0213_0231_0312_0321_1302_2301_3120"),
        _b2rc("0213_0231_0312_0321_1320_2301_3120"),
    )
    assert bi is not None
    _bijection_asserter(Bijection.from_dict(json.loads(json.dumps(bi.to_jsonable()))))
    # JSON with fusion+assumption
    pack = TileScopePack(
        initial_strats=[strat.FactorFactory()],
        ver_strats=[
            strat.BasicVerificationStrategy(),
        ],
        inferral_strats=[
            strat.ObstructionTransitivityFactory(),
        ],
        expansion_strats=[[strat.RowAndColumnPlacementFactory()]],
        name="custom",
    ).make_fusion()
    pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
    bi = find_bijection_between(TileScope("132", pack), TileScope("123", pack))
    assert bi is not None
    _bijection_asserter(Bijection.from_dict(json.loads(json.dumps(bi.to_jsonable()))))


def test_bijection_15_fusion():
    pack = TileScopePack.row_and_col_placements(row_only=True).make_fusion(tracked=True)
    pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
    pack2 = TileScopePack.row_and_col_placements(row_only=True).make_fusion(
        tracked=True
    )
    pack2 = pack2.add_initial(SlidingFactory(True))
    pack2 = pack2.add_verification(BasicVerificationStrategy(), replace=True)
    t1 = TileScope("1234", pack)
    t2 = TileScope("1243", pack)
    t3 = TileScope("1432", pack2)
    _bijection_asserter(find_bijection_between(t1, t2), max_size=6)
    _bijection_asserter(find_bijection_between(t1, t3), max_size=6)
    _bijection_asserter(find_bijection_between(t2, t3), max_size=6)

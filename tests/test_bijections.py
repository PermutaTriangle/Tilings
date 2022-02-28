import json
from collections import deque
from typing import Optional

import pytest
import requests
from sympy import Point

from comb_spec_searcher import (
    AtomStrategy,
    CombinatorialSpecificationSearcher,
    StrategyPack,
)
from comb_spec_searcher.bijection import ParallelSpecFinder
from comb_spec_searcher.isomorphism import Bijection
from permuta import Perm
from tilings import GriddedPerm, Tiling, TrackingAssumption
from tilings import strategies as strat
from tilings.bijections import (
    FusionBijection,
    FusionParallelSpecFinder,
    _AssumptionPathTracker,
)
from tilings.strategies import BasicVerificationStrategy, PositiveCorroborationFactory
from tilings.strategies.assumption_insertion import AddAssumptionsStrategy
from tilings.strategies.factor import FactorStrategy
from tilings.strategies.fusion import FusionStrategy
from tilings.strategies.requirement_placement import RequirementPlacementStrategy
from tilings.strategies.sliding import SlidingFactory, SlidingStrategy
from tilings.tilescope import TileScope, TileScopePack


def find_bijection_between(
    searcher1: CombinatorialSpecificationSearcher,
    searcher2: CombinatorialSpecificationSearcher,
) -> Optional[Bijection]:
    specs = ParallelSpecFinder(searcher1, searcher2).find()
    if specs is not None:
        s1, s2 = specs
        return Bijection.construct(s1, s2)


def find_bijection_between_fusion(
    searcher1: TileScope, searcher2: TileScope
) -> Optional[Bijection]:
    specs = FusionParallelSpecFinder(searcher1, searcher2).find()
    if specs is not None:
        s1, s2 = specs
        return FusionBijection.construct(s1, s2)


def _b2rc(basis: str) -> CombinatorialSpecificationSearcher:
    pack = TileScopePack.row_and_col_placements(row_only=True)
    pack = pack.remove_strategy(PositiveCorroborationFactory())
    pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
    searcher = TileScope(basis, pack)
    assert isinstance(searcher, CombinatorialSpecificationSearcher)
    return searcher


def _bijection_asserter(bi, max_size=7, key_vals: Optional[dict] = None):
    assert bi is not None
    assert key_vals is None or all(bi.map(k) == v for k, v in key_vals.items())
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


@pytest.mark.slow
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
    # flake8: noqa
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
    # flake8: noqa
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


@pytest.mark.slow
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
    pack = pack.remove_strategy(PositiveCorroborationFactory())
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


@pytest.mark.slow
def test_bijection_15_fusion():
    pack = TileScopePack.row_and_col_placements(row_only=True).make_fusion(tracked=True)
    pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
    pack2 = TileScopePack.row_and_col_placements(row_only=True).make_fusion(
        tracked=True
    )
    pack2 = pack2.add_initial(SlidingFactory(True))
    pack2 = pack2.add_verification(BasicVerificationStrategy(), replace=True)
    long_1234 = Perm(
        (
            47,
            42,
            48,
            39,
            46,
            37,
            49,
            26,
            41,
            45,
            44,
            43,
            38,
            36,
            31,
            40,
            35,
            34,
            33,
            30,
            29,
            27,
            17,
            15,
            32,
            25,
            28,
            23,
            24,
            21,
            20,
            5,
            22,
            13,
            19,
            18,
            9,
            16,
            14,
            12,
            0,
            11,
            8,
            10,
            1,
            7,
            6,
            4,
            3,
            2,
        )
    )
    long_1243 = Perm(
        (
            47,
            41,
            40,
            48,
            42,
            39,
            38,
            43,
            27,
            44,
            35,
            34,
            36,
            37,
            45,
            46,
            31,
            32,
            30,
            19,
            28,
            26,
            24,
            14,
            12,
            22,
            23,
            21,
            25,
            15,
            9,
            16,
            17,
            8,
            7,
            18,
            0,
            11,
            10,
            5,
            4,
            3,
            2,
            6,
            13,
            1,
            20,
            29,
            33,
            49,
        )
    )
    expected_1234_to_1243 = Perm(
        (
            47,
            46,
            45,
            43,
            42,
            48,
            39,
            41,
            38,
            44,
            37,
            35,
            33,
            40,
            31,
            30,
            36,
            27,
            49,
            29,
            28,
            25,
            26,
            21,
            24,
            17,
            32,
            34,
            22,
            20,
            19,
            16,
            15,
            14,
            9,
            18,
            13,
            11,
            6,
            5,
            4,
            8,
            10,
            0,
            12,
            3,
            7,
            1,
            2,
            23,
        )
    )
    expected_1234_to_1432 = Perm(
        (
            47,
            46,
            45,
            43,
            42,
            49,
            39,
            44,
            38,
            40,
            37,
            35,
            33,
            34,
            31,
            30,
            48,
            27,
            32,
            36,
            28,
            25,
            29,
            21,
            23,
            17,
            22,
            18,
            19,
            20,
            26,
            16,
            15,
            14,
            9,
            12,
            41,
            10,
            6,
            5,
            4,
            7,
            11,
            0,
            2,
            13,
            1,
            24,
            3,
            8,
        )
    )
    expected_1243_to_1432 = Perm(
        (
            47,
            41,
            40,
            43,
            44,
            39,
            38,
            45,
            27,
            29,
            32,
            28,
            33,
            30,
            31,
            36,
            37,
            42,
            46,
            19,
            20,
            23,
            21,
            14,
            12,
            13,
            16,
            17,
            18,
            25,
            9,
            15,
            22,
            8,
            7,
            34,
            0,
            6,
            10,
            11,
            24,
            1,
            35,
            49,
            2,
            3,
            4,
            5,
            26,
            48,
        )
    )
    _bijection_asserter(
        find_bijection_between_fusion(TileScope("1234", pack), TileScope("1243", pack)),
        max_size=6,
        key_vals={
            GriddedPerm.single_cell(long_1234, (0, 0)): GriddedPerm.single_cell(
                expected_1234_to_1243, (0, 0)
            )
        },
    )
    _bijection_asserter(
        find_bijection_between_fusion(
            TileScope("1234", pack), TileScope("1432", pack2)
        ),
        max_size=6,
        key_vals={
            GriddedPerm.single_cell(long_1234, (0, 0)): GriddedPerm.single_cell(
                expected_1234_to_1432, (0, 0)
            )
        },
    )
    _bijection_asserter(
        find_bijection_between_fusion(
            TileScope("1243", pack), TileScope("1432", pack2)
        ),
        max_size=6,
        key_vals={
            GriddedPerm.single_cell(long_1243, (0, 0)): GriddedPerm.single_cell(
                expected_1243_to_1432, (0, 0)
            )
        },
    )


def test_bijection_16_fusion_json():
    pack = TileScopePack(
        initial_strats=[strat.FactorFactory()],
        ver_strats=[
            strat.BasicVerificationStrategy(),
        ],
        inferral_strats=[
            strat.ObstructionTransitivityFactory(),
        ],
        expansion_strats=[
            [
                strat.RowAndColumnPlacementFactory(place_row=True, place_col=False),
            ]
        ],
        name="mypack",
    ).make_fusion()
    t1 = TileScope("123", pack)
    t2 = TileScope("132", pack)
    bi = find_bijection_between_fusion(t1, t2)
    idx_data = bi._index_data
    order = bi._get_order
    assert len(idx_data) > 0
    assert len(order) > 0
    bi_from_dict = Bijection.from_dict(bi.to_jsonable())
    assert idx_data == bi_from_dict._index_data
    assert order == bi_from_dict._get_order
    _bijection_asserter(bi_from_dict)


def test_atom_assumption_path_mismatch():
    path1 = [
        (
            RequirementPlacementStrategy(
                gps=(GriddedPerm((0,), ((0, 0),)),),
                indices=(0,),
                direction=3,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
                    ),
                    requirements=(),
                    assumptions=(),
                )
            ),
            1,
        ),
        (
            FactorStrategy(
                partition=(((0, 1), (2, 1)), ((1, 0),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((0, 2, 1), ((2, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (2, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (2, 1), (2, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 0),)),),),
                    assumptions=(),
                )
            ),
            0,
        ),
        (
            RequirementPlacementStrategy(
                gps=(GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))),
                indices=(0, 0),
                direction=3,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (1, 0))),
                    ),
                    requirements=(),
                    assumptions=(),
                )
            ),
            1,
        ),
        (
            AddAssumptionsStrategy(
                assumptions=(TrackingAssumption((GriddedPerm((0,), ((3, 1),)),)),),
                workable=False,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((0, 2, 1), ((2, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 2, 1), ((2, 1), (2, 1), (3, 1))),
                        GriddedPerm((0, 2, 1), ((2, 1), (3, 1), (3, 1))),
                        GriddedPerm((0, 2, 1), ((3, 1), (3, 1), (3, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (2, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (3, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (2, 1), (3, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (3, 1), (3, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 0),)),),),
                    assumptions=(),
                )
            ),
            0,
        ),
        (
            FactorStrategy(
                partition=(((0, 1), (2, 1), (3, 1)), ((1, 0),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((0, 2, 1), ((2, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 2, 1), ((2, 1), (2, 1), (3, 1))),
                        GriddedPerm((0, 2, 1), ((2, 1), (3, 1), (3, 1))),
                        GriddedPerm((0, 2, 1), ((3, 1), (3, 1), (3, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (2, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (3, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (2, 1), (3, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (3, 1), (3, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 0),)),),),
                    assumptions=(TrackingAssumption((GriddedPerm((0,), ((3, 1),)),)),),
                )
            ),
            0,
        ),
        (
            AddAssumptionsStrategy(
                assumptions=(TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),),
                workable=False,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 2, 1), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (2, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    assumptions=(TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),),
                )
            ),
            0,
        ),
        (
            RequirementPlacementStrategy(
                gps=(
                    GriddedPerm((0,), ((0, 0),)),
                    GriddedPerm((0,), ((2, 0),)),
                    GriddedPerm((0,), ((1, 0),)),
                ),
                indices=(0, 0, 0),
                direction=3,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 2, 1), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (2, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    assumptions=(
                        TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),
                        TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),
                    ),
                )
            ),
            3,
        ),
        (
            FactorStrategy(
                partition=(((0, 1), (1, 1), (2, 1), (4, 1)), ((3, 0),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((3, 0), (3, 0))),
                        GriddedPerm((1, 0), ((3, 0), (3, 0))),
                        GriddedPerm((1, 0), ((4, 1), (4, 1))),
                        GriddedPerm((0, 2, 1), ((1, 1), (1, 1), (1, 1))),
                        GriddedPerm((0, 2, 1), ((1, 1), (1, 1), (2, 1))),
                        GriddedPerm((0, 2, 1), ((1, 1), (1, 1), (4, 1))),
                        GriddedPerm((0, 2, 1), ((1, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 2, 1), ((1, 1), (2, 1), (4, 1))),
                        GriddedPerm((0, 2, 1), ((2, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 2, 1), ((2, 1), (2, 1), (4, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (1, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (2, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (4, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (1, 1), (1, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (1, 1), (2, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (1, 1), (4, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (2, 1), (4, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((3, 0),)),),),
                    assumptions=(
                        TrackingAssumption((GriddedPerm((0,), ((1, 1),)),)),
                        TrackingAssumption(
                            (
                                GriddedPerm((0,), ((2, 1),)),
                                GriddedPerm((0,), ((3, 0),)),
                                GriddedPerm((0,), ((4, 1),)),
                            )
                        ),
                    ),
                )
            ),
            1,
        ),
    ]
    path2 = [
        (
            RequirementPlacementStrategy(
                gps=(GriddedPerm((0,), ((0, 0),)),),
                indices=(0,),
                direction=3,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                    ),
                    requirements=(),
                    assumptions=(),
                )
            ),
            1,
        ),
        (
            FactorStrategy(
                partition=(((0, 1), (2, 1)), ((1, 0),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (2, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 0),)),),),
                    assumptions=(),
                )
            ),
            0,
        ),
        (
            RequirementPlacementStrategy(
                gps=(GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))),
                indices=(0, 0),
                direction=3,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (1, 0))),
                    ),
                    requirements=(),
                    assumptions=(),
                )
            ),
            1,
        ),
        (
            AddAssumptionsStrategy(
                assumptions=(TrackingAssumption((GriddedPerm((0,), ((3, 1),)),)),),
                workable=False,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (2, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (3, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((3, 1), (3, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (3, 1), (3, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 0),)),),),
                    assumptions=(),
                )
            ),
            0,
        ),
        (
            FactorStrategy(
                partition=(((0, 1), (2, 1), (3, 1)), ((1, 0),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (2, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (3, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((3, 1), (3, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (3, 1), (3, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 0),)),),),
                    assumptions=(TrackingAssumption((GriddedPerm((0,), ((3, 1),)),)),),
                )
            ),
            0,
        ),
        (
            AddAssumptionsStrategy(
                assumptions=(TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),),
                workable=False,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    assumptions=(TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),),
                )
            ),
            0,
        ),
        (
            RequirementPlacementStrategy(
                gps=(
                    GriddedPerm((0,), ((0, 0),)),
                    GriddedPerm((0,), ((2, 0),)),
                    GriddedPerm((0,), ((1, 0),)),
                ),
                indices=(0, 0, 0),
                direction=3,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    assumptions=(
                        TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),
                        TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),
                    ),
                )
            ),
            2,
        ),
        (
            FactorStrategy(
                partition=(((0, 1), (1, 1), (3, 1), (4, 1)), ((2, 0),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((2, 0), (2, 0))),
                        GriddedPerm((1, 0), ((1, 1), (1, 1))),
                        GriddedPerm((1, 0), ((2, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((1, 1), (3, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((1, 1), (3, 1), (4, 1))),
                        GriddedPerm((2, 1, 0), ((1, 1), (4, 1), (4, 1))),
                        GriddedPerm((2, 1, 0), ((3, 1), (3, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((3, 1), (3, 1), (4, 1))),
                        GriddedPerm((2, 1, 0), ((3, 1), (4, 1), (4, 1))),
                        GriddedPerm((2, 1, 0), ((4, 1), (4, 1), (4, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (1, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (4, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (1, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (1, 1), (4, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (3, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (3, 1), (4, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (4, 1), (4, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((2, 0),)),),),
                    assumptions=(
                        TrackingAssumption(
                            (
                                GriddedPerm((0,), ((1, 1),)),
                                GriddedPerm((0,), ((2, 0),)),
                                GriddedPerm((0,), ((3, 1),)),
                            )
                        ),
                        TrackingAssumption((GriddedPerm((0,), ((4, 1),)),)),
                    ),
                )
            ),
            1,
        ),
    ]
    assert not _AssumptionPathTracker(
        deque(path1), deque(path2)
    ).assumptions_match_down_to_atom()


def test_atom_assumption_path_match():
    path1 = [
        (
            RequirementPlacementStrategy(
                gps=(GriddedPerm((0,), ((0, 0),)),),
                indices=(0,),
                direction=1,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 0))),
                    ),
                    requirements=(),
                    assumptions=(),
                )
            ),
            1,
        ),
        (
            FactorStrategy(
                partition=(((0, 0), (2, 0)), ((1, 1),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((1, 1), (1, 1))),
                        GriddedPerm((1, 0), ((1, 1), (1, 1))),
                        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 1),)),),),
                    assumptions=(),
                )
            ),
            0,
        ),
        (
            RequirementPlacementStrategy(
                gps=(GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))),
                indices=(0, 0),
                direction=1,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (1, 0), (1, 0))),
                    ),
                    requirements=(),
                    assumptions=(),
                )
            ),
            2,
        ),
        (
            AddAssumptionsStrategy(
                assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
                workable=False,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((2, 1), (2, 1))),
                        GriddedPerm((1, 0), ((2, 1), (2, 1))),
                        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
                    ),
                    requirements=((GriddedPerm((0,), ((2, 1),)),),),
                    assumptions=(),
                )
            ),
            0,
        ),
        (
            FactorStrategy(
                partition=(((0, 0), (1, 0), (3, 0)), ((2, 1),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((2, 1), (2, 1))),
                        GriddedPerm((1, 0), ((2, 1), (2, 1))),
                        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
                    ),
                    requirements=((GriddedPerm((0,), ((2, 1),)),),),
                    assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
                )
            ),
            0,
        ),
        (
            FusionStrategy(row_idx=None, col_idx=0, tracked=True)(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
                )
            ),
            0,
        ),
        (
            RequirementPlacementStrategy(
                gps=(GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))),
                indices=(0, 0),
                direction=1,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (1, 0), (1, 0))),
                    ),
                    requirements=(),
                    assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
                )
            ),
            1,
        ),
        (
            FactorStrategy(
                partition=(((0, 0), (2, 0), (3, 0)), ((1, 1),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((0, 0), (0, 0))),
                        GriddedPerm((0, 1), ((1, 1), (1, 1))),
                        GriddedPerm((1, 0), ((1, 1), (1, 1))),
                        GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 1),)),),),
                    assumptions=(
                        TrackingAssumption(
                            (
                                GriddedPerm((0,), ((0, 0),)),
                                GriddedPerm((0,), ((1, 1),)),
                                GriddedPerm((0,), ((2, 0),)),
                            )
                        ),
                    ),
                )
            ),
            0,
        ),
        (
            RequirementPlacementStrategy(
                gps=(
                    GriddedPerm((0,), ((0, 0),)),
                    GriddedPerm((0,), ((2, 0),)),
                    GriddedPerm((0,), ((1, 0),)),
                ),
                indices=(0, 0, 0),
                direction=1,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((0, 0), (0, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    assumptions=(
                        TrackingAssumption(
                            (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),)))
                        ),
                    ),
                )
            ),
            3,
        ),
        (
            FactorStrategy(
                partition=(((0, 0), (1, 0), (2, 0), (4, 0)), ((3, 1),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((0, 0), (0, 0))),
                        GriddedPerm((0, 1), ((3, 1), (3, 1))),
                        GriddedPerm((1, 0), ((3, 1), (3, 1))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (4, 0), (4, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (4, 0), (4, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (4, 0), (4, 0), (4, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (4, 0), (4, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (4, 0), (4, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (4, 0), (4, 0), (4, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (4, 0), (4, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (4, 0), (4, 0), (4, 0))),
                        GriddedPerm((0, 1, 2, 3), ((4, 0), (4, 0), (4, 0), (4, 0))),
                    ),
                    requirements=((GriddedPerm((0,), ((3, 1),)),),),
                    assumptions=(
                        TrackingAssumption(
                            (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),)))
                        ),
                    ),
                )
            ),
            0,
        ),
        (
            AddAssumptionsStrategy(
                assumptions=(TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),),
                workable=False,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((0, 0), (0, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
                    ),
                    requirements=(),
                    assumptions=(
                        TrackingAssumption(
                            (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),)))
                        ),
                    ),
                )
            ),
            0,
        ),
        (
            FusionStrategy(row_idx=None, col_idx=1, tracked=True)(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((0, 0), (0, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
                    ),
                    requirements=(),
                    assumptions=(
                        TrackingAssumption(
                            (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),)))
                        ),
                        TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),
                    ),
                )
            ),
            0,
        ),
        (
            RequirementPlacementStrategy(
                gps=(
                    GriddedPerm((0,), ((0, 0),)),
                    GriddedPerm((0,), ((2, 0),)),
                    GriddedPerm((0,), ((1, 0),)),
                ),
                indices=(0, 0, 0),
                direction=1,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((0, 0), (0, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    assumptions=(
                        TrackingAssumption(
                            (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),)))
                        ),
                        TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),
                    ),
                )
            ),
            1,
        ),
        (
            FactorStrategy(
                partition=(((0, 1),), ((1, 0), (2, 0), (3, 0))),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((0, 1), (0, 1))),
                        GriddedPerm((0, 1), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((0, 1), (0, 1))),
                        GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((1, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((2, 0), (3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 1, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
                    ),
                    requirements=((GriddedPerm((0,), ((0, 1),)),),),
                    assumptions=(
                        TrackingAssumption(
                            (
                                GriddedPerm((0,), ((0, 1),)),
                                GriddedPerm((0,), ((1, 0),)),
                                GriddedPerm((0,), ((2, 0),)),
                            )
                        ),
                        TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),
                    ),
                )
            ),
            0,
        ),
    ]
    path2 = [
        (
            RequirementPlacementStrategy(
                gps=(GriddedPerm((0,), ((0, 0),)),),
                indices=(0,),
                direction=3,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                    ),
                    requirements=(),
                    assumptions=(),
                )
            ),
            1,
        ),
        (
            FactorStrategy(
                partition=(((0, 1), (2, 1)), ((1, 0),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (2, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 0),)),),),
                    assumptions=(),
                )
            ),
            0,
        ),
        (
            RequirementPlacementStrategy(
                gps=(GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))),
                indices=(0, 0),
                direction=3,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (1, 0))),
                    ),
                    requirements=(),
                    assumptions=(),
                )
            ),
            1,
        ),
        (
            AddAssumptionsStrategy(
                assumptions=(TrackingAssumption((GriddedPerm((0,), ((3, 1),)),)),),
                workable=False,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (2, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (3, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((3, 1), (3, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (3, 1), (3, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 0),)),),),
                    assumptions=(),
                )
            ),
            0,
        ),
        (
            FactorStrategy(
                partition=(((0, 1), (2, 1), (3, 1)), ((1, 0),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (2, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (3, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((3, 1), (3, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (3, 1), (3, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 0),)),),),
                    assumptions=(TrackingAssumption((GriddedPerm((0,), ((3, 1),)),)),),
                )
            ),
            0,
        ),
        (
            FusionStrategy(row_idx=None, col_idx=1, tracked=True)(
                Tiling(
                    obstructions=(
                        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    assumptions=(TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),),
                )
            ),
            0,
        ),
        (
            RequirementPlacementStrategy(
                gps=(GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))),
                indices=(0, 0),
                direction=3,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (1, 0))),
                    ),
                    requirements=(),
                    assumptions=(TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),),
                )
            ),
            2,
        ),
        (
            FactorStrategy(
                partition=(((0, 1), (1, 1), (3, 1)), ((2, 0),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((2, 0), (2, 0))),
                        GriddedPerm((1, 0), ((1, 1), (1, 1))),
                        GriddedPerm((1, 0), ((2, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((1, 1), (3, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((3, 1), (3, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (1, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (1, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (3, 1), (3, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((2, 0),)),),),
                    assumptions=(
                        TrackingAssumption(
                            (
                                GriddedPerm((0,), ((1, 1),)),
                                GriddedPerm((0,), ((2, 0),)),
                                GriddedPerm((0,), ((3, 1),)),
                            )
                        ),
                    ),
                )
            ),
            0,
        ),
        (
            RequirementPlacementStrategy(
                gps=(
                    GriddedPerm((0,), ((0, 0),)),
                    GriddedPerm((0,), ((2, 0),)),
                    GriddedPerm((0,), ((1, 0),)),
                ),
                indices=(0, 0, 0),
                direction=3,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    assumptions=(
                        TrackingAssumption(
                            (GriddedPerm((0,), ((1, 0),)), GriddedPerm((0,), ((2, 0),)))
                        ),
                    ),
                )
            ),
            1,
        ),
        (
            FactorStrategy(
                partition=(((0, 1), (2, 1), (3, 1), (4, 1)), ((1, 0),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((3, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (2, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (4, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (3, 1), (4, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (4, 1), (4, 1))),
                        GriddedPerm((2, 1, 0), ((3, 1), (4, 1), (4, 1))),
                        GriddedPerm((2, 1, 0), ((4, 1), (4, 1), (4, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (4, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (4, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (3, 1), (4, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (4, 1), (4, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 0),)),),),
                    assumptions=(
                        TrackingAssumption(
                            (GriddedPerm((0,), ((3, 1),)), GriddedPerm((0,), ((4, 1),)))
                        ),
                    ),
                )
            ),
            0,
        ),
        (
            SlidingStrategy(av_12=1, av_123=2, symmetry_type=2)(
                Tiling(
                    obstructions=(
                        GriddedPerm((1, 0), ((2, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (3, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (3, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (3, 0), (3, 0))),
                        GriddedPerm((2, 1, 0), ((2, 0), (3, 0), (3, 0))),
                        GriddedPerm((2, 1, 0), ((3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (3, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (3, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (2, 0), (3, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (3, 0), (3, 0))),
                    ),
                    requirements=(),
                    assumptions=(
                        TrackingAssumption(
                            (GriddedPerm((0,), ((2, 0),)), GriddedPerm((0,), ((3, 0),)))
                        ),
                    ),
                )
            ),
            0,
        ),
        (
            AddAssumptionsStrategy(
                assumptions=(TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),),
                workable=False,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (3, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (3, 0), (3, 0))),
                        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (3, 0))),
                        GriddedPerm((2, 1, 0), ((2, 0), (3, 0), (3, 0))),
                        GriddedPerm((2, 1, 0), ((3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (3, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (3, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (2, 0), (3, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (3, 0), (3, 0))),
                    ),
                    requirements=(),
                    assumptions=(
                        TrackingAssumption(
                            (GriddedPerm((0,), ((1, 0),)), GriddedPerm((0,), ((3, 0),)))
                        ),
                    ),
                )
            ),
            0,
        ),
        (
            FusionStrategy(row_idx=None, col_idx=2, tracked=True)(
                Tiling(
                    obstructions=(
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (3, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (3, 0), (3, 0))),
                        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (3, 0))),
                        GriddedPerm((2, 1, 0), ((2, 0), (3, 0), (3, 0))),
                        GriddedPerm((2, 1, 0), ((3, 0), (3, 0), (3, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (3, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (3, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (2, 0), (3, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (3, 0), (3, 0))),
                    ),
                    requirements=(),
                    assumptions=(
                        TrackingAssumption(
                            (GriddedPerm((0,), ((1, 0),)), GriddedPerm((0,), ((3, 0),)))
                        ),
                        TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),
                    ),
                )
            ),
            0,
        ),
        (
            RequirementPlacementStrategy(
                gps=(
                    GriddedPerm((0,), ((0, 0),)),
                    GriddedPerm((0,), ((2, 0),)),
                    GriddedPerm((0,), ((1, 0),)),
                ),
                indices=(0, 0, 0),
                direction=3,
                own_col=True,
                own_row=True,
                ignore_parent=False,
                include_empty=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    assumptions=(
                        TrackingAssumption(
                            (GriddedPerm((0,), ((1, 0),)), GriddedPerm((0,), ((2, 0),)))
                        ),
                        TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),
                    ),
                )
            ),
            2,
        ),
        (
            FactorStrategy(
                partition=(((0, 1), (2, 1), (3, 1)), ((1, 0),)),
                ignore_parent=True,
                workable=True,
            )(
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((1, 0), (1, 0))),
                        GriddedPerm((1, 0), ((2, 1), (2, 1))),
                        GriddedPerm((2, 1, 0), ((2, 1), (3, 1), (3, 1))),
                        GriddedPerm((2, 1, 0), ((3, 1), (3, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (2, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (3, 1))),
                        GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (3, 1), (3, 1))),
                    ),
                    requirements=((GriddedPerm((0,), ((1, 0),)),),),
                    assumptions=(
                        TrackingAssumption(
                            (
                                GriddedPerm((0,), ((1, 0),)),
                                GriddedPerm((0,), ((2, 1),)),
                                GriddedPerm((0,), ((3, 1),)),
                            )
                        ),
                        TrackingAssumption((GriddedPerm((0,), ((3, 1),)),)),
                    ),
                )
            ),
            1,
        ),
    ]
    assert _AssumptionPathTracker(
        deque(path1), deque(path2)
    ).assumptions_match_down_to_atom()

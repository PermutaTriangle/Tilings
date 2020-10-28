import pytest
import sympy

from comb_spec_searcher import CombinatorialSpecification
from comb_spec_searcher.rule_db import LimitedStrategyRuleDB
from comb_spec_searcher.strategies import EmptyStrategy
from comb_spec_searcher.strategies.rule import VerificationRule
from comb_spec_searcher.utils import taylor_expand
from permuta import Av, Perm
from tilings import GriddedPerm, Tiling
from tilings import strategies as strat
from tilings.strategies.fusion import ComponentFusionStrategy, FusionStrategy
from tilings.strategy_pack import TileScopePack
from tilings.tilescope import TileScope

point_placements = TileScopePack.point_placements()
all_the_strategies_verify_database = TileScopePack.all_the_strategies().make_database()
all_the_strategies_fusion = TileScopePack.all_the_strategies().make_fusion(
    tracked=False
)
point_placements_fusion = point_placements.make_fusion(tracked=False)
point_placements_component_fusion = point_placements.make_fusion(
    component=True, tracked=False
)
row_placements_fusion = TileScopePack.row_and_col_placements(row_only=True).make_fusion(
    tracked=True
)
row_and_col_placements_component_fusion_fusion = (
    TileScopePack.row_and_col_placements()
    .make_fusion(component=True, tracked=False)
    .make_fusion(tracked=False)
)
reginsenc = TileScopePack.regular_insertion_encoding(3)


@pytest.mark.timeout(20)
def test_132():
    searcher = TileScope("132", point_placements)
    spec = searcher.auto_search(smallest=True)
    assert isinstance(spec, CombinatorialSpecification)


@pytest.mark.timeout(20)
def test_132_genf():
    searcher = TileScope([Perm((0, 2, 1))], point_placements)
    spec = searcher.auto_search(smallest=True)
    spec.expand_verified()
    av = Av([Perm((0, 2, 1))])
    for i in range(10):
        assert set(av.of_length(i)) == set(
            gp.patt for gp in spec.generate_objects_of_size(i)
        )
        assert spec.random_sample_object_of_size(i).patt in av
    gf = spec.get_genf()
    gf = sympy.series(spec.get_genf(), n=15)
    x = sympy.Symbol("x")
    assert [gf.coeff(x, n) for n in range(13)] == [
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
    ]


@pytest.mark.timeout(20)
def test_132_elementary():
    searcher = TileScope(Tiling.from_string("132"), point_placements.make_elementary())
    spec = searcher.auto_search()
    assert spec.number_of_rules() == 4
    spec.expand_verified()
    assert spec.number_of_rules() == 5
    assert isinstance(spec, CombinatorialSpecification)


@pytest.mark.timeout(20)
def test_132_321_genf():
    searcher = TileScope("132_321", point_placements)
    spec = searcher.auto_search(smallest=True)
    assert isinstance(spec, CombinatorialSpecification)
    gf = spec.get_genf()
    assert taylor_expand(gf, 15) == [
        1,
        1,
        2,
        4,
        7,
        11,
        16,
        22,
        29,
        37,
        46,
        56,
        67,
        79,
        92,
        106,
    ]


@pytest.mark.timeout(20)
def test_123():
    searcher = TileScope((Perm((0, 1, 2)),), point_placements_fusion)
    spec = searcher.auto_search(smallest=True)
    assert isinstance(spec, CombinatorialSpecification)


@pytest.mark.timeout(120)
def test_123_with_db():
    searcher = TileScope("123", all_the_strategies_verify_database)
    spec = searcher.auto_search(smallest=True)
    assert isinstance(spec, CombinatorialSpecification)


@pytest.mark.timeout(20)
def test_1342_1423():
    searcher = TileScope("1342_1423", point_placements_component_fusion)
    spec = searcher.auto_search(smallest=True)
    assert spec.number_of_rules() == 9
    assert isinstance(spec, CombinatorialSpecification)


@pytest.mark.timeout(60)
def test_reverse_equiv():
    """A specification that should use reverse equivalence."""
    pack = TileScopePack(
        initial_strats=[
            strat.FactorFactory(),
            strat.RequirementCorroborationFactory(),
            strat.RequirementPlacementFactory(partial=False),
        ],
        inferral_strats=[strat.RowColumnSeparationStrategy()],
        expansion_strats=[[strat.CellInsertionFactory()]],
        ver_strats=[strat.BasicVerificationStrategy()],
        iterative=False,
        name="test pack",
    )
    basis = (Perm((0, 1, 3, 2)), Perm((0, 2, 3, 1)), Perm((1, 0, 3, 2)))
    # From https://oeis.org/A033321
    expected_enum = [1, 1, 2, 6, 21, 79, 311, 1265, 5275, 22431, 96900, 424068, 1876143]
    x, f = sympy.symbols("x f")
    expected_min_poly = sympy.sympify("-4*f^2*x^2 + 8*f^2*x - 4*f*x - 4*f + 4")
    searcher = TileScope(basis, pack)
    spec = searcher.auto_search(smallest=True)
    assert [spec.count_objects_of_size(i) for i in range(13)] == expected_enum
    genf = spec.get_genf()
    assert sympy.simplify(expected_min_poly.subs(f, genf)) == 0
    assert taylor_expand(genf, 12) == expected_enum
    # In order to avoid ReccursionError we go incrementally
    for i in range(0, 100):
        spec.count_objects_of_size(i)
    assert spec.count_objects_of_size(50) == 86055297645519796258217673160170
    assert (
        spec.count_objects_of_size(100)
        == 2733073112795720153237297124938915907723365837935699807314396095313
    )
    len4_perms = tuple(spec.generate_objects_of_size(4))
    assert len(len4_perms) == 21
    assert all(p not in len4_perms for p in basis)
    len8_perms = tuple(spec.generate_objects_of_size(8))
    assert len(len8_perms) == 5275
    assert len(set(len8_perms)) == 5275
    for _ in range(10):
        gp = spec.random_sample_object_of_size(10)
        print(gp)
        assert gp.patt.avoids(*basis)

    av = Av(basis)
    for i in range(10):
        assert set(av.of_length(i)) == set(
            gp.patt for gp in spec.generate_objects_of_size(i)
        )
        assert spec.random_sample_object_of_size(i).patt in av


@pytest.mark.timeout(20)
def test_1324():
    searcher = TileScope("1324", row_and_col_placements_component_fusion_fusion)
    spec = searcher.auto_search(smallest=True)
    assert spec.number_of_rules() == 9
    num_fusion = 0
    num_comp_fusion = 0
    for rule in spec.rules_dict.values():
        if isinstance(rule.strategy, FusionStrategy) and not isinstance(
            rule.strategy, ComponentFusionStrategy
        ):
            num_fusion += 1
        if isinstance(rule.strategy, ComponentFusionStrategy):
            num_comp_fusion += 1
    assert num_fusion == 1
    assert num_comp_fusion == 1
    assert isinstance(spec, CombinatorialSpecification)


@pytest.mark.timeout(20)
def test_321_1324():
    searcher = TileScope("321_1324", reginsenc)
    spec = searcher.auto_search()
    assert isinstance(spec, CombinatorialSpecification)
    for i in range(20):
        gp = spec.random_sample_object_of_size(i)
        assert all(cell == (0, 0) for cell in gp.pos)
        assert gp.patt.avoids(Perm((2, 1, 0)), Perm((0, 2, 1, 3)))
    av = Av([Perm((2, 1, 0)), Perm((0, 2, 1, 3))])
    for i in range(10):
        assert set(av.of_length(i)) == set(
            gp.patt for gp in spec.generate_objects_of_size(i)
        )
    assert [spec.count_objects_of_size(i) for i in range(50)] == [
        1,
        1,
        2,
        5,
        13,
        32,
        72,
        148,
        281,
        499,
        838,
        1343,
        2069,
        3082,
        4460,
        6294,
        8689,
        11765,
        15658,
        20521,
        26525,
        33860,
        42736,
        53384,
        66057,
        81031,
        98606,
        119107,
        142885,
        170318,
        201812,
        237802,
        278753,
        325161,
        377554,
        436493,
        502573,
        576424,
        658712,
        750140,
        851449,
        963419,
        1086870,
        1222663,
        1371701,
        1534930,
        1713340,
        1907966,
        2119889,
        2350237,
    ]


@pytest.mark.timeout(5)
def test_from_tiling():
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 0), (1, 1))),
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
        ]
    )
    searcher = TileScope(t, TileScopePack.point_placements())
    spec = searcher.auto_search()
    print(spec)
    assert sympy.simplify(spec.get_genf() - sympy.sympify("(1+x)/(1-x)")) == 0


@pytest.mark.timeout(5)
def test_expansion():
    """
    For this pack only some basic verification are needed.
    """
    pack = TileScopePack.only_root_placements(3, 1)
    css = TileScope("132", pack)
    spec = css.auto_search(smallest=True)
    spec.expand_verified()
    for comb_class, rule in spec.rules_dict.items():
        if isinstance(rule, VerificationRule):
            assert isinstance(
                rule.strategy,
                (
                    strat.OneByOneVerificationStrategy,
                    strat.MonotoneTreeVerificationStrategy,
                    strat.BasicVerificationStrategy,
                    EmptyStrategy,
                ),
            )


@pytest.mark.timeout(10)
def test_single_fusion_db():
    ruledb = LimitedStrategyRuleDB(
        strategies_to_limit=set([FusionStrategy]), limit=1, mark_verified=False
    )
    searcher = TileScope("0123_0132", row_placements_fusion, ruledb=ruledb)
    spec = searcher.auto_search()
    assert isinstance(spec, CombinatorialSpecification)
    expected_enum = [1, 1, 2, 6, 22, 90, 394, 1806, 8558, 41586, 206098]
    assert [spec.count_objects_of_size(n) for n in range(11)] == expected_enum


@pytest.mark.timeout(30)
def test_domino():
    domino = Tiling(
        obstructions=[
            GriddedPerm((0, 2, 1), [(0, 0), (0, 0), (0, 0)]),
            GriddedPerm((1, 0, 2), [(0, 1), (0, 1), (0, 1)]),
            GriddedPerm((0, 2, 1, 3), [(0, 0), (0, 1), (0, 0), (0, 1)]),
        ]
    )
    tilescope = TileScope(
        domino,
        TileScopePack.row_and_col_placements().make_fusion(
            tracked=True, component=True
        ),
    )
    spec = tilescope.auto_search()
    assert isinstance(spec, CombinatorialSpecification)
    assert [spec.count_objects_of_size(i) for i in range(15)] == [
        1,
        2,
        6,
        22,
        91,
        408,
        1938,
        9614,
        49335,
        260130,
        1402440,
        7702632,
        42975796,
        243035536,
        1390594458,
    ]

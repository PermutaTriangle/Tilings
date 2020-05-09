import pytest
import sympy

from comb_spec_searcher import CombinatorialSpecification
from tilings.strategies.fusion import ComponentFusionStrategy, FusionStrategy
from tilings.strategy_pack import TileScopePack
from tilings.tilescope import TileScope

point_placements = TileScopePack.point_placements()
all_the_strategies_verify_database = TileScopePack.all_the_strategies().make_database()
all_the_strategies_fusion = TileScopePack.all_the_strategies().make_fusion()
point_placements_fusion = point_placements.make_fusion()
point_placements_component_fusion = point_placements.make_fusion(component=True)
row_and_col_placements_component_fusion_fusion = (
    TileScopePack.row_and_col_placements().make_fusion(component=True).make_fusion()
)


@pytest.mark.timeout(20)
def test_132():
    searcher = TileScope("132", point_placements)
    spec = searcher.auto_search(smallest=True)
    assert isinstance(spec, CombinatorialSpecification)


@pytest.mark.xfail(reason="factoring for generating functions not implemented")
def test_132_genf():
    searcher = TileScope("132", point_placements)
    spec = searcher.auto_search(smallest=True)
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
    searcher = TileScope("132", point_placements.make_elementary())
    spec = searcher.auto_search()
    assert spec.number_of_rules() == 4
    assert isinstance(spec, CombinatorialSpecification)


@pytest.mark.timeout(20)
def test_123():
    searcher = TileScope("123", point_placements_fusion)
    spec = searcher.auto_search(smallest=True)
    assert isinstance(spec, CombinatorialSpecification)


@pytest.mark.timeout(60)
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

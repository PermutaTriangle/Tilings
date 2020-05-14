import pytest
import sympy

from comb_spec_searcher import CombinatorialSpecification
from comb_spec_searcher.utils import taylor_expand
from permuta import Perm
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
reginsenc = TileScopePack.regular_insertion_encoding(3)


@pytest.mark.timeout(20)
def test_132():
    searcher = TileScope("132", point_placements)
    spec = searcher.auto_search(smallest=True)
    assert isinstance(spec, CombinatorialSpecification)


@pytest.mark.timeout(20)
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
    assert spec.number_of_rules() == 5
    assert isinstance(spec, CombinatorialSpecification)


@pytest.mark.timeout(20)
def test_132_321_genf():
    searcher = TileScope("132_321", point_placements)
    spec = searcher.auto_search(smallest=True)
    assert isinstance(spec, CombinatorialSpecification)
    assert spec.number_of_rules() == 9
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


@pytest.mark.timeout(20)
def test_321_1324():
    searcher = TileScope("321_1324", reginsenc)
    spec = searcher.auto_search()
    assert isinstance(spec, CombinatorialSpecification)
    for i in range(20):
        gp = spec.random_sample_object_of_size(i)
        assert all(cell == (0, 0) for cell in gp.pos)
        assert gp.patt.avoids(Perm((2, 1, 0)), Perm((0, 2, 1, 3)))
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

import json

import pytest
import sympy

from comb_spec_searcher import ProofTree
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
    t = searcher.auto_search(smallest=True)
    assert isinstance(t, ProofTree)


@pytest.mark.xfail(reason="Generating function finding not implemented")
def test_132_genf():
    searcher = TileScope("132", point_placements)
    t = searcher.auto_search(smallest=True)
    gf = sympy.series(t.get_genf(), n=15)
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
    t = searcher.auto_search()
    assert t.number_of_nodes() == 5
    assert isinstance(t, ProofTree)


@pytest.mark.timeout(20)
def test_123():
    print(all_the_strategies_verify_database)
    searcher = TileScope("123", point_placements_fusion)
    t = searcher.auto_search(smallest=True)
    assert isinstance(t, ProofTree)


@pytest.mark.timeout(60)
def test_123_with_db():
    searcher = TileScope("123", all_the_strategies_verify_database)
    t = searcher.auto_search(smallest=True)
    assert isinstance(t, ProofTree)


@pytest.mark.timeout(20)
def test_1342_1423():
    searcher = TileScope("1342_1423", point_placements_component_fusion)
    t = searcher.auto_search(smallest=True)
    t.number_of_nodes() == 14
    assert isinstance(t, ProofTree)


@pytest.mark.timeout(20)
def test_1324():
    searcher = TileScope("1324", row_and_col_placements_component_fusion_fusion)
    t = searcher.auto_search(smallest=True)
    t.number_of_nodes() == 14
    num_fusion = 0
    num_comp_fusion = 0
    for node in t.nodes():
        if "Fuse" in node.formal_step:
            num_fusion += 1
        if "Component" in node.formal_step:
            num_comp_fusion += 1
    assert num_fusion == 1
    assert num_comp_fusion == 1
    assert isinstance(t, ProofTree)


def test_json():
    searcher = TileScope("1324", all_the_strategies_fusion)
    searcher.auto_search(max_time=2)
    dict_ = searcher.to_dict()
    json_str = json.dumps(dict_)
    new_dict = json.loads(json_str)
    new_searcher = TileScope.from_dict(new_dict)
    assert new_searcher.__dict__.keys() == searcher.__dict__.keys()
    assert new_searcher._time_taken == searcher._time_taken
    assert new_searcher.strategy_times == searcher.strategy_times
    assert new_searcher.strategy_expansions == searcher.strategy_expansions
    assert new_searcher.kwargs == searcher.kwargs
    assert new_searcher.strategy_pack == searcher.strategy_pack
    assert new_searcher.start_class == searcher.start_class
    new_searcher.auto_search(max_time=2)
    assert new_searcher._time_taken > 2

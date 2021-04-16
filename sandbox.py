# 1234
# 1243
# 1432 sliding


import json
from typing import List

from comb_spec_searcher.specification import CombinatorialSpecification
from comb_spec_searcher.strategies.constructor import (
    CartesianProduct,
    Complement,
    DisjointUnion,
    Quotient,
)
from comb_spec_searcher.strategies.rule import Rule
from permuta import Perm
from tilings import GriddedPerm, Tiling, TrackingAssumption, tilescope
from tilings.strategies.factor import FactorStrategy
from tilings.strategies.fusion import FusionStrategy
from tilings.strategies.fusion.fusion import FusionStrategy
from tilings.strategies.requirement_placement import RequirementPlacementStrategy
from tilings.strategies.sliding import SlidingFactory
from tilings.tilescope import TileScope, TileScopePack


def slider(plot=False):
    pack = TileScopePack.row_and_col_placements(row_only=True).make_fusion(tracked=True)
    pack = pack.add_initial(SlidingFactory(True))
    spec = TileScope("1432", pack).auto_search()
    if plot:
        spec.show()
    return spec


def traverse_spec(spec: CombinatorialSpecification, path: List[int]):
    if not path:
        raise ValueError("List must contain at least one element")
    path = path[::-1]
    par, rule = spec.root, spec.root_rule
    while len(path) > 1:
        par = rule.children[path.pop()]
        rule = spec.rules_dict[par]
    return par, rule, rule.children[path.pop()]


def get_specs(plot=False):
    with open("1234_spec.json") as f:
        _s1234 = CombinatorialSpecification.from_dict(json.loads(f.read()))
    with open("1243_spec.json") as f:
        _s1243 = CombinatorialSpecification.from_dict(json.loads(f.read()))
    if plot:
        _s1234.show()
        _s1243.show()
    return _s1234, _s1243


s1234, s1243 = get_specs()

"""
from comb_spec_searcher.isomorphism import Bijection

bi = Bijection.construct(s1234, s1243)

for i in range(8):
    domain = set(s1234.generate_objects_of_size(i))
    codomain = set(s1243.generate_objects_of_size(i))
    print({bi.inverse_map(gp) for gp in codomain} == domain)
"""

"""s1234.show()
s1243.show()"""

"""
p, r, c = traverse_spec(s1243, list(map(int, "100100")))

assert isinstance(r, Rule)
# print(list(r.backward_map((GriddedPerm.single_cell((0,), (1, 0)),))))
# print(r.indexed_backward_map((GriddedPerm.single_cell((0,), (1, 0)),), 1, True))

#print(bi.map(GriddedPerm.single_cell((0, 2, 1), (0, 0))))"""

from comb_spec_searcher import find_bijection_between
from tilings.strategies import BasicVerificationStrategy

pack = TileScopePack.row_and_col_placements(row_only=True).make_fusion(tracked=True)
pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
# pack = pack.add_initial(SlidingFactory(True))

bi = find_bijection_between(TileScope("1234", pack), TileScope("1243", pack))
print(bi)

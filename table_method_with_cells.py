from collections import defaultdict
from itertools import chain
from typing import Dict, FrozenSet, List, Tuple

from comb_spec_searcher.strategies import Rule, VerificationRule
from tilings import Tiling
from tilings.tilescope import TileScope, TileScopePack

Cell = Tuple[int, int]
CellMap = Dict[Cell, List[Cell]]
Tracking = FrozenSet[FrozenSet[Cell]]

css = TileScope(
    "123",
    TileScopePack.point_placements().make_fusion(tracked=False),
)
css.auto_search()

rules = list(css.ruledb.all_rules())

print(len(rules))


class RuleWithCellMap:
    def __init__(self, rule: Rule):
        self.rule = rule
        self.cell_maps: Tuple[CellMap, ...] = rule.strategy.cell_maps(
            rule.comb_class, rule.children
        )
        self.value_partitions = tuple(
            frozenset(frozenset(v) for v in cell_map.values())
            for cell_map in self.cell_maps
        )
        self.reverse_cell_maps = tuple(
            {b: [a] for a, bs in cell_map.items() for b in bs}
            for cell_map in self.cell_maps
        )

    def map_tracking(self, tracking: Tracking) -> Tuple[Tracking, ...]:
        res = []
        for cell_map in self.cell_maps:
            new_tracking = []
            for part in tracking:
                new_part = frozenset(
                    chain.from_iterable(cell_map[cell] for cell in part)
                )
                new_tracking.append(new_part)
            new_tracking = frozenset(new_tracking)
            res.append(new_tracking)
        return tuple(res)

    def reverse_mappable(self, idx: int, tracking: Tracking) -> bool:
        value_partition = self.value_partitions[idx]
        cell_map = self.cell_maps[idx]

        def subset_mappable(subset: FrozenSet[Cell]):
            mapped = set(chain.from_iterable(cell_map[cell] for cell in subset))
            # exact cover

        return all(
            any(part.issubset(other) for other in tracking) for part in value_partition
        )

    def reverse_map_tracking(self, tracking: Tracking) -> Tuple[Tracking, ...]:
        assert len(self.cell_maps) == 1
        if self.reverse_mappable(0, tracking):
            return self._reverse_map_tracking(tracking)
        raise ValueError("NOT MAPPABLE")

    def _reverse_map_tracking(self, tracking: Tracking) -> Tuple[Tracking, ...]:
        res = []
        for cell_map in self.reverse_cell_maps:
            new_tracking = []
            for part in tracking:
                new_part = frozenset(
                    chain.from_iterable(cell_map[cell] for cell in part)
                )
                new_tracking.append(new_part)
            new_tracking = frozenset(new_tracking)
            res.append(new_tracking)
        return tuple(res)

    def __str__(self) -> str:
        return (
            str(self.rule)
            + "\n"
            + str(self.cell_maps)
            + "\n"
            + str(self.reverse_cell_maps)
        )


class TilingWithTrackings:
    def __init__(self, tiling: Tiling):
        self.tiling = tiling
        self.trackings = set(
            [frozenset(frozenset([cell]) for cell in rule.comb_class.active_cells)]
        )

    def __str__(self) -> str:
        return str(self.tiling) + "\n" + str(self.trackings)


tiling_to_rule_with_cell_maps = defaultdict(list)
tilings_with_trackings = {}
for rule in rules:
    if isinstance(rule, VerificationRule):
        continue
    rule_with_cell_map = RuleWithCellMap(rule)
    tilings = (rule.comb_class,) + rule.children
    for tiling in tilings:
        tilings_with_trackings[tiling] = TilingWithTrackings(tiling)
        tiling_to_rule_with_cell_maps[tiling].append(rule_with_cell_map)

for t in tilings_with_trackings.values():
    if t.tiling.dimensions == (1, 2) and t.tiling.positive_cells:
        print(t)
        break

for rule in tiling_to_rule_with_cell_maps[t.tiling]:
    if rule.rule.comb_class == t.tiling and len(rule.rule.children) == 1:
        print(rule)
        tracking = list(t.trackings)[0]
        new_tracking = rule.map_tracking(tracking)
        print(new_tracking)
        print(rule.reverse_map_tracking(new_tracking[0]))

        tracking = list(tilings_with_trackings[rule.rule.children[0]].trackings)[0]

        print(rule.reverse_map_tracking(tracking))

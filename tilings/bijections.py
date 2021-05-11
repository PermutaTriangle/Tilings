from typing import Deque, Dict, Set, Tuple

from comb_spec_searcher.bijection import EqPathParallelSpecFinder, SpecMap
from comb_spec_searcher.comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.specification_extrator import RulePathToAtomExtractor
from comb_spec_searcher.strategies.rule import AbstractRule, Rule
from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.strategies import BasicVerificationStrategy
from tilings.tilescope import TileScope

AssumptionLabels = Dict[int, Set[TrackingAssumption]]


class _AssumptionPathTracker:
    def __init__(
        self,
        path1: Deque[Tuple[AbstractRule, int]],
        path2: Deque[Tuple[AbstractRule, int]],
    ) -> None:
        assert sum(1 for r, _ in path1 if not r.is_equivalence()) == sum(
            1 for r, _ in path2 if not r.is_equivalence()
        )
        self.nxt_label = 0
        self.path1 = path1
        self.path2 = path2
        self.r1, self.idx1 = _AssumptionPathTracker._get_next(path1)
        self.r2, self.idx2 = _AssumptionPathTracker._get_next(path2)
        self.assumptions1, self.assumptions2 = self._init_assumptions()

    def _init_assumptions(self) -> Tuple[AssumptionLabels, AssumptionLabels]:
        a1: AssumptionLabels = {}
        a2: AssumptionLabels = {}
        if self.r1.comb_class.assumptions:
            a1[self.nxt_label] = set(self.r1.comb_class.assumptions)
        if self.r2.comb_class.assumptions:
            a2[self.nxt_label] = set(self.r2.comb_class.assumptions)
        self.nxt_label = max(len(a1), len(a2))
        return a1, a2

    @staticmethod
    def _get_next(
        path: Deque[Tuple[AbstractRule, int]]
    ) -> Tuple[Rule[Tiling, GriddedPerm], int]:
        r, idx = path.popleft()
        assert isinstance(r, Rule)
        assert not path or r.children[idx] == path[0][0].comb_class
        return r, idx

    @staticmethod
    def _forward_all_labels(
        assumptions: AssumptionLabels,
        rule: Rule[Tiling, GriddedPerm],
        idx: int,
    ) -> AssumptionLabels:
        d: AssumptionLabels = {}
        parmap = rule.strategy.extra_parameters(rule.comb_class, rule.children)[idx]
        for i, s in assumptions.items():
            new_set = set()
            for assumption in s:
                parent_var = rule.comb_class.get_assumption_parameter(assumption)
                if parent_var in parmap:
                    child_var = parmap[parent_var]
                    child_assumption = rule.children[idx].get_assumption(child_var)
                    new_set.add(child_assumption)
            if new_set:
                d[i] = new_set
        return d

    def _step_through_equivalences(self):
        while self.r1.is_equivalence():
            self.assumptions1 = _AssumptionPathTracker._forward_all_labels(
                self.assumptions1, self.r1, self.idx1
            )
            self.r1, self.idx1 = _AssumptionPathTracker._get_next(self.path1)
        while self.r2.is_equivalence():
            self.assumptions2 = _AssumptionPathTracker._forward_all_labels(
                self.assumptions2, self.r2, self.idx2
            )
            self.r2, self.idx2 = _AssumptionPathTracker._get_next(self.path2)

    def _step_forward(self) -> None:
        self._step_through_equivalences()
        self.assumptions1 = _AssumptionPathTracker._forward_all_labels(
            self.assumptions1, self.r1, self.idx1
        )
        self.assumptions2 = _AssumptionPathTracker._forward_all_labels(
            self.assumptions2, self.r2, self.idx2
        )

    @staticmethod
    def _find_new_assumptions(
        rule: Rule[Tiling, GriddedPerm],
        assumptions: AssumptionLabels,
    ) -> Set[TrackingAssumption]:
        return set(
            assumption
            for assumption in rule.comb_class.assumptions
            if all(assumption not in v for v in assumptions.values())
        )

    def _check_for_new_assumptions(self) -> None:
        a1 = _AssumptionPathTracker._find_new_assumptions(self.r1, self.assumptions1)
        a2 = _AssumptionPathTracker._find_new_assumptions(self.r2, self.assumptions2)
        if a1:
            self.assumptions1[self.nxt_label] = a1
        if a2:
            self.assumptions2[self.nxt_label] = a2
        if a1 or a2:
            self.nxt_label += 1

    def assumptions_match_down_to_atom(self) -> bool:
        while True:
            self._step_forward()
            if not self.path1 and not self.path2:
                break
            self.r1, self.idx1 = _AssumptionPathTracker._get_next(self.path1)
            self.r2, self.idx2 = _AssumptionPathTracker._get_next(self.path2)
            self._check_for_new_assumptions()

        return sorted(self.assumptions1.keys()) == sorted(self.assumptions2.keys())


class FusionParallelSpecFinder(
    EqPathParallelSpecFinder[Tiling, GriddedPerm, Tiling, GriddedPerm]
):
    def __init__(
        self,
        searcher1: TileScope,
        searcher2: TileScope,
    ):
        super().__init__(searcher1, searcher2)

    def _pre_expand(
        self,
        searcher1: CombinatorialSpecificationSearcher[Tiling],
        searcher2: CombinatorialSpecificationSearcher[Tiling],
    ) -> None:
        # pylint: disable=no-self-use
        searcher1.strategy_pack = searcher1.strategy_pack.add_verification(
            BasicVerificationStrategy(), replace=True
        )
        searcher2.strategy_pack = searcher2.strategy_pack.add_verification(
            BasicVerificationStrategy(), replace=True
        )

    def _atom_path_match(self, id1: int, id2: int, sp1: SpecMap, sp2: SpecMap) -> bool:
        path1, path2 = self._get_paths(id1, id2, sp1, sp2)
        return _AssumptionPathTracker(path1, path2).assumptions_match_down_to_atom()

    def _get_paths(
        self, id1: int, id2: int, sp1: SpecMap, sp2: SpecMap
    ) -> Tuple[Deque[Tuple[AbstractRule, int]], Deque[Tuple[AbstractRule, int]]]:
        path1 = RulePathToAtomExtractor(
            self._pi1.root_eq_label,
            FusionParallelSpecFinder._create_tree(sp1, self._pi1.root_eq_label),
            self._pi1.searcher.ruledb,
            self._pi1.searcher.classdb,
            ((label, idx) for label, _, idx, _ in self._path),
            id1,
        ).rule_path()
        path2 = RulePathToAtomExtractor(
            self._pi2.root_eq_label,
            FusionParallelSpecFinder._create_tree(sp2, self._pi2.root_eq_label),
            self._pi2.searcher.ruledb,
            self._pi2.searcher.classdb,
            ((label, idx) for _, label, _, idx in self._path),
            id2,
        ).rule_path()
        return path1, path2

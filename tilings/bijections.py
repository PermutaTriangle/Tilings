from collections import defaultdict, deque
from functools import partial
from typing import Callable, DefaultDict, Deque, Dict, Optional, Set, Tuple

from comb_spec_searcher.bijection import EqPathParallelSpecFinder, SpecMap
from comb_spec_searcher.comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.isomorphism import Bijection, Isomorphism
from comb_spec_searcher.specification import CombinatorialSpecification
from comb_spec_searcher.specification_extrator import RulePathToAtomExtractor
from comb_spec_searcher.strategies.rule import AbstractRule, ReverseRule, Rule
from comb_spec_searcher.typing import Terms
from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.strategies import BasicVerificationStrategy
from tilings.strategies.fusion.fusion import FusionRule
from tilings.tilescope import TileScope

AssumptionLabels = Dict[int, Set[TrackingAssumption]]


class _TermCacher:
    """A cache wrapper for getting terms."""

    MAX_TERMS_LEN = 5

    def __init__(self) -> None:
        self._cache: DefaultDict[Tiling, Dict[int, Terms]] = defaultdict(dict)

    def get_term_function_from_tiling(self, tiling: Tiling) -> Callable[[int], Terms]:
        """Return a cached version of `get_terms` given a tiling."""
        return partial(self._tiling_f, tiling)

    def get_term_function_from_rule(self, rule: FusionRule) -> Callable[[int], Terms]:
        """Return a cached version of `get_terms` given a fusion rule."""
        return partial(self._rule_f, rule)

    def _tiling_f(self, tiling: Tiling, n: int) -> Terms:
        return self._f(tiling, tiling.get_terms, n)

    def _rule_f(self, rule: FusionRule, n: int) -> Terms:
        return self._f(rule.comb_class, rule.get_terms, n)

    def _f(self, cache_key: Tiling, func: Callable[[int], Terms], n: int) -> Terms:
        cached = self._cache[cache_key]
        retval = cached.get(n, None)
        if retval is None:
            retval = func(n)
            cached[n] = retval
        return retval


class _AssumptionPathTracker:
    """Tracks assumptions down to atoms with labels."""

    def __init__(
        self,
        path1: Deque[Tuple[AbstractRule[Tiling, GriddedPerm], int]],
        path2: Deque[Tuple[AbstractRule[Tiling, GriddedPerm], int]],
    ) -> None:
        if 0 in (len(path1), len(path2)):
            raise ValueError("Paths should contain at least one rule.")

        # Number of non-equivalence rules should be the same
        assert sum(1 for r, _ in path1 if not r.is_equivalence()) == sum(
            1 for r, _ in path2 if not r.is_equivalence()
        )

        self.nxt_label = 0
        self.path1 = path1
        self.path2 = path2

        # rules and indices set to that of root and first child in each path
        self.r1, self.idx1 = _AssumptionPathTracker._get_next(path1)
        self.r2, self.idx2 = _AssumptionPathTracker._get_next(path2)

        # If root contains any assumptions, they are gathered here
        # These are a map of labels (ids) to assumptions
        self.assumptions1, self.assumptions2 = self._init_assumptions()

    def _init_assumptions(self) -> Tuple[AssumptionLabels, AssumptionLabels]:
        if (
            self.r1.comb_class.predicate_assumptions
            or self.r2.comb_class.predicate_assumptions
        ):
            raise NotImplementedError("not implemented bijections for predicates")
        a1: AssumptionLabels = {}
        a2: AssumptionLabels = {}
        # If any label at root, we store them at the first label
        if self.r1.comb_class.assumptions:
            a1[self.nxt_label] = set(self.r1.comb_class.tracking_assumptions)
        if self.r2.comb_class.assumptions:
            a2[self.nxt_label] = set(self.r2.comb_class.tracking_assumptions)
        # Increment next label if root had any assumptions
        self.nxt_label = max(len(a1), len(a2))
        return a1, a2

    @staticmethod
    def _get_next(
        path: Deque[Tuple[AbstractRule, int]]
    ) -> Tuple[Rule[Tiling, GriddedPerm], int]:
        """Get next rule and the index of its child we traverse through."""
        r, idx = path.popleft()
        assert isinstance(r, Rule)
        assert not path or r.children[idx] == path[0][0].comb_class
        return r, idx

    @staticmethod
    def _get_par_map(rule: Rule[Tiling, GriddedPerm], idx: int) -> Dict[str, str]:
        """Given a rule and an index of its child, give the extra parameters map from
        the parent to that child.
        """
        if not isinstance(rule, ReverseRule):
            return rule.strategy.extra_parameters(rule.comb_class, rule.children)[idx]
        # If the rule is a reverse rule, we assume that it has only one children
        # as that is the only used reverse rule that have been implemented so far.
        assert len(rule.children) == 1
        pmap = rule.strategy.extra_parameters(rule.children[0], (rule.comb_class,))[idx]
        assert len(pmap) == len(set(pmap.values()))  # invertible
        return {v: k for k, v in pmap.items()}

    @staticmethod
    def _forward_all_labels(
        assumptions: AssumptionLabels,
        rule: Rule[Tiling, GriddedPerm],
        idx: int,
    ) -> AssumptionLabels:
        """Recreate the dictionary of labels to assumptions by mapping each assumption
        to the corresponding assumption in the idx-th child of rule, if there is any.
        If the label's value becomes empty, we remove it.
        """
        d: AssumptionLabels = {}
        parmap = _AssumptionPathTracker._get_par_map(rule, idx)
        for i, s in assumptions.items():
            new_set = set()
            for assumption in s:
                parent_var = rule.comb_class.get_assumption_parameter(assumption)
                # If parent's assumption is in child
                if parent_var in parmap:
                    child_var = parmap[parent_var]
                    child_assumption = rule.children[idx].get_assumption(child_var)
                    new_set.add(child_assumption)
            if new_set:
                d[i] = new_set
        return d

    def _step_through_equivalences(self):
        """
        Map assumptions though equivalences assuming they won't introduce new ones.
        """
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
        """
        A step forward will perform the map for one non-equivalence rule for each path.
        """
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
        """The assumption in the current class that don't correspond to any label."""
        if rule.comb_class.predicate_assumptions:
            raise NotImplementedError("Not implemented bijections for predicates")
        return set(
            assumption
            for assumption in rule.comb_class.tracking_assumptions
            if all(assumption not in v for v in assumptions.values())
        )

    def _check_for_new_assumptions(self) -> None:
        a1 = _AssumptionPathTracker._find_new_assumptions(self.r1, self.assumptions1)
        a2 = _AssumptionPathTracker._find_new_assumptions(self.r2, self.assumptions2)

        # Add any new atoms to the label tra
        if a1:
            self.assumptions1[self.nxt_label] = a1
        if a2:
            self.assumptions2[self.nxt_label] = a2

        # Increment the label system if new ones
        if a1 or a2:
            self.nxt_label += 1

    def assumptions_match_down_to_atom(self) -> bool:
        while True:
            # Map assumptions to next node
            self._step_forward()

            # If there aren't any more rules, we are done as we should be at an atom now
            if not self.path1 and not self.path2:
                break

            # Assign next rules
            self.r1, self.idx1 = _AssumptionPathTracker._get_next(self.path1)
            self.r2, self.idx2 = _AssumptionPathTracker._get_next(self.path2)

            # Search for new assumptions that will recieve a new label
            self._check_for_new_assumptions()

        # When at the atoms, the labels should match
        return sorted(self.assumptions1.keys()) == sorted(self.assumptions2.keys())


class FusionParallelSpecFinder(
    EqPathParallelSpecFinder[Tiling, GriddedPerm, Tiling, GriddedPerm]
):
    """A specialized parallel specification finder for fusion."""

    def __init__(self, searcher1: TileScope, searcher2: TileScope):
        super().__init__(searcher1, searcher2)
        self._term_cacher = _TermCacher()

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
        path1, path2 = self._get_paths(sp1, sp2)
        return _AssumptionPathTracker(path1, path2).assumptions_match_down_to_atom()

    def _rule_match(
        self,
        rule1: AbstractRule[Tiling, GriddedPerm],
        rule2: AbstractRule[Tiling, GriddedPerm],
    ) -> bool:
        # pylint: disable=no-self-use
        if not isinstance(rule1, Rule):
            return not isinstance(rule2, Rule)
        if not isinstance(rule2, Rule):
            return False
        # If comparing two fusion rules, terms are required
        if isinstance(rule1, FusionRule) and isinstance(rule2, FusionRule):
            terms = (
                self._term_cacher.get_term_function_from_tiling(rule1.comb_class),
                self._term_cacher.get_term_function_from_tiling(rule2.comb_class),
                _TermCacher.MAX_TERMS_LEN,
            )
            return rule1.constructor.equiv(rule2.constructor, terms)[0]
        return rule1.constructor.equiv(rule2.constructor)[0]

    def _get_paths(
        self, sp1: SpecMap, sp2: SpecMap
    ) -> Tuple[Deque[Tuple[AbstractRule, int]], Deque[Tuple[AbstractRule, int]]]:
        path1 = RulePathToAtomExtractor(
            self._pi1.searcher.start_label,
            self._pi1.root_eq_label,
            FusionParallelSpecFinder._create_tree(sp1, self._pi1.root_eq_label),
            self._pi1.ruledb,
            self._pi1.searcher.classdb,
            [(label, idx) for label, _, idx, _ in reversed(self._path)],
        ).rule_path()
        path2 = RulePathToAtomExtractor(
            self._pi2.searcher.start_label,
            self._pi2.root_eq_label,
            FusionParallelSpecFinder._create_tree(sp2, self._pi2.root_eq_label),
            self._pi2.ruledb,
            self._pi2.searcher.classdb,
            [(label, idx) for _, label, _, idx in reversed(self._path)],
        ).rule_path()
        return path1, path2


class FusionIsomorphism(Isomorphism[Tiling, GriddedPerm, Tiling, GriddedPerm]):
    """Does additional checks for atoms and fusion constructors."""

    def __init__(
        self,
        spec1: CombinatorialSpecification[Tiling, GriddedPerm],
        spec2: CombinatorialSpecification[Tiling, GriddedPerm],
        term_cacher: Optional[_TermCacher] = None,
    ) -> None:
        self._term_cacher = term_cacher if term_cacher else _TermCacher()
        super().__init__(spec1, spec2)

    def _atom_match(
        self,
        atom1: Tiling,
        atom2: Tiling,
        rule1: AbstractRule[Tiling, GriddedPerm],
        rule2: AbstractRule[Tiling, GriddedPerm],
    ) -> bool:
        """Returns true if atoms match, false otherwise."""
        # pylint: disable=no-self-use
        if not super()._atom_match(atom1, atom2, rule1, rule2):
            return False
        return self._assumption_match_down_to_atom()

    def _assumption_match_down_to_atom(self) -> bool:
        path1: Deque[Tuple[AbstractRule[Tiling, GriddedPerm], int]] = deque([])
        path2: Deque[Tuple[AbstractRule[Tiling, GriddedPerm], int]] = deque([])
        curr1, curr2 = self.root1, self.root2
        # Collect the rules and child indices down to our current atom
        for step1, step2 in self._path_tracker:
            # spec 1
            for idx in step1:
                rule = self._rules1[curr1]
                i = tuple(j for j, c in enumerate(rule.children) if not c.is_empty())[
                    idx
                ]
                path1.append((rule, i))
                curr1 = rule.children[i]
            # spec 2
            for idx in step2:
                rule = self._rules2[curr2]
                i = tuple(j for j, c in enumerate(rule.children) if not c.is_empty())[
                    idx
                ]
                path2.append((rule, i))
                curr2 = rule.children[i]
        return _AssumptionPathTracker(path1, path2).assumptions_match_down_to_atom()

    def _constructor_match(
        self,
        rule1: Rule[Tiling, GriddedPerm],
        rule2: Rule[Tiling, GriddedPerm],
        curr1: Tiling,
        curr2: Tiling,
    ) -> bool:
        if not (isinstance(rule1, FusionRule) and isinstance(rule2, FusionRule)):
            return super()._constructor_match(rule1, rule2, curr1, curr2)
        terms = (
            self._term_cacher.get_term_function_from_rule(rule1),
            self._term_cacher.get_term_function_from_rule(rule2),
            _TermCacher.MAX_TERMS_LEN,
        )
        are_eq, data = rule1.constructor.equiv(rule2.constructor, terms)
        if not are_eq:
            return False
        assert isinstance(data, list) and 0 < len(data) < 3
        # If data contains two values, we can't determine the direction of the match
        if (len(data) == 1 and data[0]) or (
            len(data) == 2 and self._fusion_reverse_match(rule1, rule2)
        ):
            self._index_data[(curr1, curr2)] = True  # Reverse match cached
        return True

    def _fusion_reverse_match(self, rule1: FusionRule, rule2: FusionRule) -> bool:
        # Find fused parameter in parents by going downwards
        parent_param1 = FusionIsomorphism._assumption_bfs_to_parent(rule1, self._rules1)
        parent_param2 = FusionIsomorphism._assumption_bfs_to_parent(rule2, self._rules2)
        # If we fail to find parent in either, we use normal matching
        if parent_param1 is None or parent_param2 is None:
            return False
        # Reverse match if there is a mismatch in where the parameters land
        return (
            parent_param1 in rule1.constructor.left_sided_parameters
            and parent_param2 in rule2.constructor.right_sided_parameters
        ) or (
            parent_param1 in rule1.constructor.right_sided_parameters
            and parent_param2 in rule2.constructor.left_sided_parameters
        )

    @staticmethod
    def _get_par_maps(_rule: Rule[Tiling, GriddedPerm]) -> Tuple[Dict[str, str], ...]:
        if not isinstance(_rule, ReverseRule):
            return _rule.strategy.extra_parameters(_rule.comb_class, _rule.children)
        assert len(_rule.children) == 1  # We currently only have 1-1 rev rules
        return _rule.strategy.extra_parameters(_rule.children[0], (_rule.comb_class,))

    @staticmethod
    def _assumption_bfs_to_parent(
        fusion_rule: FusionRule,
        rules: Dict[Tiling, AbstractRule[Tiling, GriddedPerm]],
    ) -> Optional[str]:
        """A memory enhanced bfs to find parent that tracks parameter."""
        mem: Set[Tiling] = {fusion_rule.children[0]}
        queue: Deque[Tuple[Tiling, str]] = deque(
            [(fusion_rule.children[0], fusion_rule.constructor.fuse_parameter)]
        )
        while queue:
            curr, par = queue.popleft()
            if curr == fusion_rule.comb_class:
                return par
            rule = rules[curr]
            assert isinstance(rule, Rule)
            for i, pmap in enumerate(FusionIsomorphism._get_par_maps(rule)):
                child = rule.children[i]
                if not child.is_atom() and par in pmap and child not in mem:
                    queue.append((child, pmap[par]))
                    mem.add(child)


class FusionBijection(Bijection[Tiling, GriddedPerm, Tiling, GriddedPerm]):
    """Replaces base Isomorphism with FusionIsomorphism."""

    @classmethod
    def construct(
        cls,
        spec: CombinatorialSpecification[Tiling, GriddedPerm],
        other: CombinatorialSpecification[Tiling, GriddedPerm],
    ) -> Optional["FusionBijection"]:
        iso = FusionIsomorphism(spec, other)
        if not iso.are_isomorphic():
            return None
        return cls(spec, other, iso.get_order(), iso.get_order_data())

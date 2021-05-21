from collections import Counter, deque
from typing import Any
from typing import Counter as CounterType
from typing import Deque, Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union

import requests
import tabulate
from logzero import logger

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
    StrategyPack,
)
from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.class_queue import DefaultQueue
from comb_spec_searcher.rule_db.abstract import RuleDBAbstract

# from comb_spec_searcher.strategies import AbstractStrategy
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.typing import CombinatorialClassType, CSSstrategy, WorkPacket
from comb_spec_searcher.utils import cssmethodtimer
from permuta import Basis, Perm
from tilings import GriddedPerm, Tiling
from tilings.strategies import AddAssumptionFactory, RearrangeAssumptionFactory
from tilings.strategies.assumption_insertion import AddAssumptionsStrategy
from tilings.strategy_pack import TileScopePack

__all__ = ("TileScope", "TileScopePack", "LimitedAssumptionTileScope", "GuidedSearcher")


class TileScope(CombinatorialSpecificationSearcher):
    """
    An instance of TileScope is used to build up knowledge about tilings with
    respect to the given basis.
    """

    def __init__(
        self,
        start_class: Union[str, Iterable[Perm], Tiling],
        strategy_pack: TileScopePack,
        ruledb: Optional[RuleDBAbstract] = None,
        expand_verified: bool = False,
        debug: bool = False,
    ) -> None:

        """Initialise TileScope."""
        if isinstance(start_class, str):
            basis = Basis.from_string(start_class)
        elif isinstance(start_class, Tiling):
            if start_class.dimensions == (1, 1):
                basis = Basis(*[o.patt for o in start_class.obstructions])
            start_tiling = start_class
        else:
            try:
                basis = Basis(*start_class)
            except TypeError as e:
                raise ValueError(
                    "start class must be a string, an iterable of Perm or a tiling"
                ) from e

        if not isinstance(start_class, Tiling):
            start_tiling = Tiling(
                obstructions=[GriddedPerm.single_cell(patt, (0, 0)) for patt in basis]
            )

        if start_tiling.dimensions == (1, 1):
            logger.debug("Fixing basis in basis aware verification strategies.")
            strategy_pack = strategy_pack.add_basis(basis)
        strategy_pack = strategy_pack.setup_subclass_verification(start_tiling)

        super().__init__(
            start_class=start_tiling,
            strategy_pack=strategy_pack,
            ruledb=ruledb,
            expand_verified=expand_verified,
            debug=debug,
        )


class LimitedAssumptionTileScope(TileScope):
    """
    A subclass of Tilescope that allows a limit to be set on the maximum number of
    assumptions that appear on any tiling in the universe.
    """

    def __init__(
        self,
        start_class: Union[str, Iterable[Perm], Tiling],
        strategy_pack: TileScopePack,
        max_assumptions: int,
        **kwargs
    ) -> None:
        super().__init__(start_class, strategy_pack, **kwargs)
        self.max_assumptions = max_assumptions

    def _expand(
        self,
        comb_class: CombinatorialClassType,
        label: int,
        strategies: Tuple[CSSstrategy, ...],
        inferral: bool,
    ) -> None:
        """
        Will expand the combinatorial class with given label using the given
        strategies, but only add rules whose children all satisfy the max_assumptions
        requirement.
        """
        if inferral:
            self._inferral_expand(comb_class, label, strategies)
        else:
            for strategy_generator in strategies:
                for start_label, end_labels, rule in self._expand_class_with_strategy(
                    comb_class, strategy_generator, label
                ):
                    if all(
                        len(child.assumptions) <= self.max_assumptions
                        for child in rule.children
                    ):
                        self.add_rule(start_label, end_labels, rule)


class GuidedSearcher(TileScope):
    def __init__(
        self,
        tilings: Iterable[Tiling],
        basis: Tiling,
        pack: TileScopePack,
        *args,
        **kwargs
    ):
        self.tilings = frozenset(t.remove_assumptions() for t in tilings)
        super().__init__(basis, pack, *args, **kwargs)
        for t in self.tilings:
            class_label = self.classdb.get_label(t)
            is_empty = self.classdb.is_empty(t, class_label)
            if not is_empty:
                self.classqueue.add(class_label)

    def _expand(
        self,
        comb_class: Tiling,
        label: int,
        strategies: Tuple[CSSstrategy, ...],
        inferral: bool,
    ) -> None:
        if comb_class.remove_assumptions() not in self.tilings:
            return
        return super()._expand(comb_class, label, strategies, inferral)

    @classmethod
    def from_spec(
        cls, specification: CombinatorialSpecification, pack: TileScopePack
    ) -> "GuidedSearcher":
        tilings = specification.comb_classes()
        root = specification.root
        return cls(tilings, root, pack)

    @classmethod
    def from_uri(cls, URI: str) -> "GuidedSearcher":
        response = requests.get(URI)
        spec = CombinatorialSpecification.from_dict(response.json()["specification"])
        pack = TileScopePack.from_dict(response.json()["pack"]).make_tracked()
        return cls.from_spec(spec, pack)


class OldTrackedSearcher(LimitedAssumptionTileScope):
    """
    A TileScope that keeps track of the strategies that apply to Tilings without
    assumptions and applies these to any tiling with assumptions.
    """

    def __init__(self, *args, **kwargs):
        self.assumptionless_strategies: Dict[int, List[AbstractStrategy]] = dict()
        self.expanded = set()
        super().__init__(*args, **kwargs)

    # @cssmethodtimer("add rule") # called recursively so shouldn't time it.
    def add_rule(
        self, start_label: int, end_labels: Tuple[int, ...], rule: AbstractRule
    ) -> None:
        if not rule.comb_class.assumptions:
            if start_label not in self.assumptionless_strategies:
                self.assumptionless_strategies[start_label] = [
                    rule.strategy,
                ]
            else:
                self.assumptionless_strategies[start_label].append(rule.strategy)
        for comb_class, child_label in zip(rule.children, end_labels):
            if self.symmetries and child_label not in self.symmetry_expanded:
                self._symmetry_expand(
                    comb_class, child_label
                )  # TODO: mark symmetries as empty where appropriate
            if comb_class.assumptions:
                if self.expand_sooner(comb_class, child_label):
                    # print("SKIPPING")
                    # print(comb_class)
                    # input()
                    continue
                # print("ADDING")
                # print(comb_class)
                # input()
            if rule.workable:
                # assert child_label >= self.classdb.get_label(
                #     comb_class.remove_assumptions()
                # )
                self.classqueue.add(child_label)
            if not rule.inferrable:
                self.classqueue.set_not_inferrable(child_label)
            if not rule.possibly_empty:
                self.classdb.set_empty(child_label, empty=False)
            self.try_verify(comb_class, child_label)
        if rule.ignore_parent:
            self.classqueue.set_stop_yielding(start_label)
        self.ruledb.add(start_label, end_labels, rule)

    def expand_sooner(self, comb_class: Tiling, label: int) -> bool:
        """
        Return True if all strategies have been tried, i.e., the underlying tiling
        has been fully expanded.
        """
        if label in self.expanded:
            return True
        self.expanded.add(label)
        underlying_label = self.classdb.get_label(comb_class.remove_assumptions())
        if underlying_label in self.assumptionless_strategies:
            for strategy in [
                AddAssumptionFactory(),
                RearrangeAssumptionFactory(),
            ] + self.assumptionless_strategies[underlying_label]:
                if isinstance(strategy, AddAssumptionsStrategy):
                    continue
                for start_label, end_labels, rule in self._expand_class_with_strategy(
                    comb_class, strategy, label
                ):
                    if all(
                        len(child.assumptions) <= self.max_assumptions
                        for child in rule.children
                    ):
                        self.add_rule(start_label, end_labels, rule)
            return underlying_label in self.classqueue.ignore
        return False


class TrackedSearcher(LimitedAssumptionTileScope):
    """
    A TileScope that keeps track of the level that underlying tilings are first found to
    prioritise expanding classes with assumtions that have been seen before.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classqueue = TrackedQueue(self.strategy_pack, self.classdb)
        self.classqueue.add(self.start_label, self.start_class)

    @cssmethodtimer("add rule")
    def add_rule(
        self, start_label: int, end_labels: Tuple[int, ...], rule: AbstractRule
    ) -> None:
        """
        Add the rule to the searcher

        - try to verify children combinatorial classes
        - set workability of combinatorial classes
        - symmetry expand combinatorial classes
        - add class to classqueue
        """
        for comb_class, child_label in zip(rule.children, end_labels):
            if self.symmetries and child_label not in self.symmetry_expanded:
                self._symmetry_expand(
                    comb_class, child_label
                )  # TODO: mark symmetries as empty where appropriate
            if not rule.inferrable:
                self.classqueue.set_not_inferrable(child_label)
            if not rule.possibly_empty:
                self.classdb.set_empty(child_label, empty=False)
            self.try_verify(comb_class, child_label)
            if rule.workable:
                self.classqueue.add(
                    child_label, comb_class
                )  # only line changed from original method
        if rule.ignore_parent:
            self.classqueue.set_stop_yielding(start_label)
        self.ruledb.add(start_label, end_labels, rule)


class TrackedQueue(DefaultQueue):
    """
    A queue that puts tracked tilings on the queue at the level the
    underlying tiling was first seen.
    """

    def __init__(self, pack: StrategyPack, classdb: ClassDB):
        super().__init__(pack)
        self.get_label = classdb.get_label
        self.working: Deque[int] = deque()
        self.next_level: CounterType[int] = Counter()
        self.curr_levels: List[Tuple[Deque[int], ...]] = []
        self._inferral_expanded: Set[int] = set()
        self._initial_expanded: Set[int] = set()
        self.ignore: Set[int] = set()
        self.queue_sizes: List[int] = []
        self.staging: Deque[WorkPacket] = deque([])
        self.levels: Dict[int, int] = dict()
        self.added_already: List[Set[int]] = []

    def _new_curr_level(self) -> Tuple[Deque[int], ...]:
        # One extra deque to be able to set ignore
        return tuple(deque() for _ in range(len(self.expansion_strats) + 1))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrackedQueue):
            return NotImplemented
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    def get_underlying_label(self, label: int, tiling: Tiling):
        if not tiling.assumptions:
            return label
        return self.get_label(tiling.remove_assumptions())

    def add(self, label: int, tiling: Tiling) -> None:
        self.levels[label] = self.levels.get(
            self.get_underlying_label(label, tiling), len(self.curr_levels)
        )
        if self.can_do_inferral(label) or self.can_do_initial(label):
            self.working.append(label)
        elif label not in self.ignore:
            self.next_level.update((label,))

    def _populate_staging(self) -> None:
        """
        Populate the staging queue that is used by next to return WorkPacket.
        """
        while not self.staging and self.working:
            self.staging.extend(self._iter_helper_working())
        while not self.staging:
            if not any(any(curr_level) for curr_level in self.curr_levels):
                self._change_level()
            self.staging.extend(self._iter_helper_curr())

    def _change_level(self) -> None:
        print("changing level")
        assert not self.staging, "Can't change level is staging is not empty"
        assert not self.working, "Can't change level is working is not empty"
        assert not any(
            any(curr_level) for curr_level in self.curr_levels
        ), "Can't change level is curr_level is not empty"
        new_level = self._new_curr_level()
        new_level[0].extend(
            label for label, _ in sorted(self.next_level.items(), key=lambda x: -x[1])
        )
        added_already = set(self.next_level.keys())
        if not any(new_level):
            raise StopIteration
        self.queue_sizes.append(len(new_level[0]))
        self.curr_levels.append(new_level)
        self.added_already.append(added_already)
        self.next_level = Counter()

    def _iter_helper_curr(self) -> Iterator[WorkPacket]:
        assert any(
            any(curr_level) for curr_level in self.curr_levels
        ), "The current queue is empty"

        for curr_level in self.curr_levels:
            if any(curr_level):
                # pylint: disable=stop-iteration-return
                idx, label = next(
                    (
                        (idx, queue.popleft())
                        for idx, queue in enumerate(curr_level)
                        if queue
                    )
                )
                if idx == len(self.expansion_strats):
                    self.set_stop_yielding(label)
                    return
                for strat in self.expansion_strats[idx]:
                    yield WorkPacket(label, (strat,), False)
                curr_level[idx + 1].append(label)

    def _iter_helper_working(self) -> Iterator[WorkPacket]:
        label = self.working.popleft()
        if self.can_do_inferral(label):
            yield WorkPacket(label, self.inferral_strategies, True)
            self.set_not_inferrable(label)
        if self.can_do_initial(label):
            for strat in self.initial_strategies:
                yield WorkPacket(label, (strat,), False)
            self.set_not_initial(label)
        level = self.levels[label]
        if level == len(self.curr_levels):
            self.next_level.update((label,))
        else:
            # TODO: don't add to the queue twice
            if label not in self.added_already[level]:
                self.curr_levels[level][0].append(label)
                self.added_already[level].add(label)

    def status(self) -> str:
        status = f"Queue status (currently on level {self.levels_completed}):\n"
        table: List[Tuple[str, str]] = []
        table.append(("working", f"{len(self.working):,d}"))
        for level, curr_level in enumerate(self.curr_levels):
            for idx, queue in enumerate(curr_level[:-1]):
                table.append(
                    (f"level {level} current (set {idx+1})", f"{len(queue):,d}")
                )
        table.append(("next", f"{len(self.next_level):,d}"))
        status += "    "
        headers = ("Queue", "Size")
        colalign = ("left", "right")
        status += (
            tabulate.tabulate(table, headers=headers, colalign=colalign).replace(
                "\n", "\n    "
            )
            + "\n"
        )
        status += "\tThe size of the current queues at each level: {}".format(
            ", ".join(str(i) for i in self.queue_sizes)
        )
        return status

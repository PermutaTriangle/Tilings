from collections import deque
from typing import (
    Any,
    Deque,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

import requests
import tabulate
from logzero import logger

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
    StrategyPack,
)
from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.class_queue import CSSQueue
from comb_spec_searcher.exception import NoMoreClassesToExpandError
from comb_spec_searcher.rule_db.abstract import RuleDBAbstract

# from comb_spec_searcher.strategies import AbstractStrategy
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.typing import CombinatorialClassType, CSSstrategy, WorkPacket
from comb_spec_searcher.utils import cssmethodtimer
from permuta import Basis, Perm
from tilings import GriddedPerm, Tiling

# from tilings.strategies import AddAssumptionFactory, RearrangeAssumptionFactory
# from tilings.strategies.assumption_insertion import AddAssumptionsStrategy
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
        self.classqueue = TrackedQueue(self.classdb, self.strategy_pack)
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


class TrackedQueue(CSSQueue):
    def __init__(self, classdb: ClassDB, pack: StrategyPack):
        self.inferral_strategies = tuple(pack.inferral_strats)
        self.initial_strategies = tuple(pack.initial_strats)
        self.expansion_strats = tuple(tuple(x) for x in pack.expansion_strats)

        self.class_db = classdb
        self.working: Deque[int] = deque()
        self.next: Set[int] = set()
        self.queues: List[Deque[int]] = list()
        self.levels: Dict[int, int] = dict()
        self._inferral_expanded: Set[int] = set()
        self._initial_expanded: Set[int] = set()
        self._expansion_expanded: Tuple[Set[int], ...] = tuple(
            set() for _ in self.expansion_strats
        )
        self.ignore: Set[int] = set()
        self.queue_sizes: List[int] = []
        self.staging: Deque[WorkPacket] = deque([])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CSSQueue):
            return NotImplemented
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    def get_underlying_label(self, label: int, tiling: Tiling):
        if not tiling.assumptions:
            return label
        return self.class_db.get_label(tiling.remove_assumptions())

    def add(self, label: int, tiling: Tiling) -> None:
        if label not in self.ignore:
            underlying_label = self.get_underlying_label(label, tiling)
            level = self.levels.get(underlying_label, len(self.queues))
            if level == len(self.queues):
                self.next.add(label)
                self.levels[underlying_label] = len(self.queues)
            else:
                self.queues[level].append(label)
            if self.can_do_inferral(label) or self.can_do_initial(label):
                self.working.append(label)

    def set_verified(self, label) -> None:
        self.set_stop_yielding(label)

    def set_not_inferrable(self, label: int) -> None:
        """Mark the label such that it's not expanded with inferral anymore"""
        if label not in self.ignore:
            self._inferral_expanded.add(label)

    def set_not_initial(self, label: int) -> None:
        """Mark the label such that it's not expanded with initial anymore"""
        if label not in self.ignore:
            self._initial_expanded.add(label)

    def set_stop_yielding(self, label: int) -> None:
        self.ignore.add(label)
        # can remove it elsewhere to keep sets "small"
        self._inferral_expanded.discard(label)
        self._initial_expanded.discard(label)
        for S in self._expansion_expanded:
            S.discard(label)

    def can_do_inferral(self, label: int) -> bool:
        """Return true if inferral strategies can be applied."""
        return bool(self.inferral_strategies) and label not in self._inferral_expanded

    def can_do_initial(self, label: int) -> bool:
        """Return true if initial strategies can be applied."""
        return bool(self.initial_strategies) and label not in self._initial_expanded

    def can_do_expansion(self, label: int, idx: int) -> bool:
        """Return true if expansion strategies can be applied."""
        return label not in self.ignore and label not in self._expansion_expanded[idx]

    def _populate_staging(self) -> None:
        """
        Populate the staging queue that is used by next to return WorkPacket.
        """
        while not self.staging and self.working:
            self.staging.extend(self._iter_helper_working())
        while not self.staging:
            if not any(self.queues):
                self._change_level()
            self.staging.extend(self._iter_helper_curr())

    def _change_level(self) -> None:
        print("changing level")
        assert not self.staging, "Can't change level is staging is not empty"
        assert not self.working, "Can't change level is working is not empty"
        assert not any(self.queues), "Can't change level if a queue is not empty"
        if not self.next:
            raise StopIteration
        self.queues.append(deque(self.next))
        self.queue_sizes.append(len(self.next))
        self.next = set()

    def _iter_helper_curr(self) -> Iterator[WorkPacket]:
        assert any(self.queues)
        # pylint: disable=stop-iteration-return
        for queue in self.queues:
            while len(queue):
                label = queue.popleft()
                for idx, strats in enumerate(self.expansion_strats):
                    if self.can_do_expansion(label, idx):
                        for strat in strats:
                            yield WorkPacket(label, (strat,), False)
                        self._expansion_expanded[idx].add(label)
                        break
                else:
                    self.set_stop_yielding(label)

    def _iter_helper_working(self) -> Iterator[WorkPacket]:
        label = self.working.popleft()
        if self.can_do_inferral(label):
            yield WorkPacket(label, self.inferral_strategies, True)
            self.set_not_inferrable(label)
        if self.can_do_initial(label):
            for strat in self.initial_strategies:
                yield WorkPacket(label, (strat,), False)
            self.set_not_initial(label)

    def __next__(self) -> WorkPacket:
        while True:
            while self.staging:
                wp = self.staging.popleft()
                if wp.label not in self.ignore:
                    return wp
            self._populate_staging()

    @property
    def levels_completed(self) -> int:
        return len(self.queues)

    def do_level(self) -> Iterator[WorkPacket]:
        """
        An iterator of all combinatorial classes in the current queue.

        Will swap next queue to current after iteration.
        """
        curr_level = self.levels_completed
        while curr_level == self.levels_completed:
            try:
                yield next(self)
            except StopIteration as e:
                if curr_level == self.levels_completed:
                    raise NoMoreClassesToExpandError from e
                return

    def status(self) -> str:
        status = f"Queue status (currently on level {self.levels_completed}):\n"
        table: List[Tuple[str, str]] = []
        table.append(("working", f"{len(self.working):,d}"))
        table.append(("next", f"{len(self.next):,d}"))
        status += "    "
        headers = ("Queue", "Size")
        colalign = ("left", "right")
        status += (
            tabulate.tabulate(table, headers=headers, colalign=colalign).replace(
                "\n", "\n    "
            )
            + "\n"
        )
        status += "\tThe size of the current queues at each level: {}\n".format(
            ", ".join(str(len(q)) for q in self.queues)
        )
        status += "\tThe size of the next queue at each change level: {}".format(
            ", ".join(str(i) for i in self.queue_sizes)
        )
        return status

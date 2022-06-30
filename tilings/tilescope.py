from collections import Counter
from typing import Counter as CounterType
from typing import (
    Deque,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
)

import requests
import tabulate
from logzero import logger

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
)
from comb_spec_searcher.class_queue import CSSQueue, DefaultQueue, WorkPacket
from comb_spec_searcher.rule_db.abstract import RuleDBAbstract
from comb_spec_searcher.typing import CombinatorialClassType, CSSstrategy
from permuta import Basis, Perm
from tilings import GriddedPerm, Tiling
from tilings.assumptions import OppositeParityAssumption
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
        ignore_full_tiling_assumptions: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(start_class, strategy_pack, **kwargs)
        self.max_assumptions = max_assumptions
        self.ignore_full_tiling_assumptions = ignore_full_tiling_assumptions

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

        def num_child_assumptions(child: Tiling) -> int:
            return sum(
                1
                for ass in child.assumptions
                if (
                    (not self.ignore_full_tiling_assumptions)
                    or len(ass.gps) != len(child.active_cells)
                )
                and not isinstance(ass, OppositeParityAssumption)
            )

        if inferral:
            self._inferral_expand(comb_class, label, strategies)
        else:
            for strategy_generator in strategies:
                for start_label, end_labels, rule in self._expand_class_with_strategy(
                    comb_class, strategy_generator, label
                ):
                    if all(
                        num_child_assumptions(child) <= self.max_assumptions
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
        **kwargs,
    ):
        self.tilings = frozenset(t.remove_assumptions() for t in tilings)
        super().__init__(basis, pack, *args, **kwargs)
        for t in self.tilings:
            class_label = self.classdb.get_label(t)
            is_empty = self.classdb.is_empty(t, class_label)
            if not is_empty:
                self.classqueue.add(class_label)
            self._symmetry_expand(t, class_label)

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

    def _symmetry_expand(self, comb_class: CombinatorialClassType, label: int) -> None:
        sym_labels = set([label])
        for strategy_generator in self.symmetries:
            for start_label, end_labels, rule in self._expand_class_with_strategy(
                comb_class, strategy_generator, label=label
            ):
                sym_label = end_labels[0]
                self.ruledb.add(start_label, (sym_label,), rule)
                self.classqueue.add(sym_label)
                sym_labels.add(sym_label)
        self.symmetry_expanded.update(sym_labels)

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


class TrackedSearcher(LimitedAssumptionTileScope):
    """
    A TileScope that will prioritise expanding tilings whose underlying tilings
    were found at earlier levels. It does this by keeping a queue for each level,
    and adding tilings to the queue that the underlying was first found at.

    The first time a queue changes level, the next level of queue i will be added
    to the curr level of queue i + 1. If `delay_next` is False then it continues
    in this way for future change levels but if it is False (the default) the next
    level of queue i will be added to the curr level of queue i after the first
    change levels.
    """

    def __init__(
        self,
        start_class: Union[str, Iterable[Perm], Tiling],
        strategy_pack: TileScopePack,
        max_assumptions: int,
        delay_next: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(
            start_class, strategy_pack, max_assumptions=max_assumptions, **kwargs
        )
        # reset to the trackedqueue!
        self.classqueue = cast(
            DefaultQueue,
            TrackedQueue(cast(TileScopePack, self.strategy_pack), self, delay_next),
        )  # TODO: make CSS accept a CSSQueue as a kwarg
        self.classqueue.add(self.start_label)


class TrackedDefaultQueue(DefaultQueue):
    def __init__(self, pack: TileScopePack, delay_next: bool):
        super().__init__(pack)
        self.next_curr_level: Optional[Tuple[Deque[int], ...]] = None
        self.delay_next = delay_next

    def is_empty(self) -> bool:
        return bool(
            not self.working and not self.next_level and not any(self.curr_level)
        )

    def set_next_curr_level(self, other: "TrackedDefaultQueue"):
        self.next_curr_level = other.curr_level

    def set_tracked_queue(self, tracked_queue: "TrackedQueue") -> None:
        self._inferral_expanded = tracked_queue.inferral_expanded
        self._initial_expanded = tracked_queue.initial_expanded
        self.ignore = tracked_queue.ignore

    def _change_level(self) -> None:
        assert not self.staging, "Can't change level is staging is not empty"
        assert not self.working, "Can't change level is working is not empty"
        assert not any(self.curr_level), "Can't change level is curr_level is not empty"
        assert self.next_curr_level is not None, "not set the next curr queue"
        if any(self.next_curr_level):
            # this ensures we only change level when the next curr queue is empty
            # and therefore makes sure we never expand a label with the same strategy
            # twice
            raise StopIteration
        self.next_curr_level[0].extend(
            label
            for label, _ in sorted(self.next_level.items(), key=lambda x: -x[1])
            if label not in self.ignore
        )
        self.next_level: CounterType[int] = Counter()
        if not self.delay_next:
            self.next_curr_level = self.curr_level
        if not any(self.curr_level):
            raise StopIteration


class TrackedQueue(CSSQueue):
    def __init__(
        self, pack: TileScopePack, tilescope: TrackedSearcher, delay_next: bool
    ):
        self.tilescope = tilescope
        self.pack = pack
        self.delay_next = delay_next
        self.label_to_underlying: Dict[int, int] = {}
        self._level_first_found: Dict[int, int] = {}
        self._underlyng_labels_per_level: CounterType[int] = Counter()
        self._all_labels_per_level: CounterType[int] = Counter()
        self.inferral_expanded: Set[int] = set()
        self.initial_expanded: Set[int] = set()
        self.ignore: Set[int] = set()
        first_queue = TrackedDefaultQueue(pack, self.delay_next)
        first_queue.set_tracked_queue(self)
        self.queues = [first_queue]
        self.add_new_queue()

        super().__init__(pack)

    @property
    def levels_completed(self):
        """Return the number of levels completed for underlying tilings"""
        return len(self.queues) - 2

    def add_new_queue(self) -> None:
        last_queue = self.queues[-1]
        new_queue = TrackedDefaultQueue(self.pack, self.delay_next)
        new_queue.set_tracked_queue(self)
        last_queue.set_next_curr_level(new_queue)
        self.queues.append(new_queue)

    def get_underlying_label(self, label: int) -> int:
        underlying_label = self.label_to_underlying.get(label)
        if underlying_label is None:
            tiling = self.tilescope.classdb.get_class(label)
            underlying_tiling = tiling.remove_assumptions()
            underlying_label = self.tilescope.classdb.get_label(underlying_tiling)
            self.label_to_underlying[label] = underlying_label
            # count the number of labels that will be added to this level
            self._all_labels_per_level[self.level_first_found(underlying_label)] += 1
        return underlying_label

    def level_first_found(self, label: int) -> int:
        """Return the level that the underlying label was first found at."""
        underlying_label = self.get_underlying_label(label)
        level = self._level_first_found.get(underlying_label)
        if level is None:
            level = len(self.queues) - 2
            self._level_first_found[underlying_label] = level
            # count the number of underlying labels added to this level
            self._underlyng_labels_per_level[level] += 1
        return level

    def add(self, label: int) -> None:
        if label in self.ignore:
            return
        self.queues[self.level_first_found(label)].add(label)

    def set_not_inferrable(self, label: int) -> None:
        self.queues[self.level_first_found(label)].set_not_inferrable(label)

    def set_verified(self, label: int) -> None:
        self.queues[self.level_first_found(label)].set_verified(label)

    def set_stop_yielding(self, label: int) -> None:
        self.queues[self.level_first_found(label)].set_stop_yielding(label)

    def do_level(self) -> Iterator[WorkPacket]:
        raise NotImplementedError

    def status(self) -> str:
        status = f"Queue status (currently on level {self.levels_completed}):\n"
        table: List[Tuple[str, ...]] = []
        working = ("working",) + tuple(
            f"{len(queue.working):,d}" for queue in self.queues[:-1]
        )
        table.append(working)
        for idx in range(len(self.pack.expansion_strats)):
            current = (f"current (set {idx+1})",) + tuple(
                f"{len(queue.curr_level[idx]):,d}" for queue in self.queues[:-1]
            )
            table.append(current)
        nxt = ("next",) + tuple(
            f"{len(queue.next_level):,d}" for queue in self.queues[:-1]
        )
        table.append(nxt)
        status += "    "
        headers = ("Size",) + tuple(
            f"Queue {idx}" for idx in range(len(self.queues) - 1)
        )
        underlying = ("underlying",) + tuple(
            self._underlyng_labels_per_level[level] for level in range(len(self.queues))
        )
        table.append(underlying)
        all_labels = ("all labels",) + tuple(
            self._all_labels_per_level[level] for level in range(len(self.queues))
        )
        table.append(all_labels)
        table = [headers] + table
        table = list(zip(*table))
        headers = table[0]
        table = table[1:]
        colalign = ("left",) + tuple("right" for _ in headers[1:])
        status += (
            tabulate.tabulate(table, headers=headers, colalign=colalign).replace(
                "\n", "\n    "
            )
            + "\n"
        )
        return status

    def __next__(self) -> WorkPacket:
        for idx, queue in enumerate(self.queues):
            if idx == len(self.queues) - 1:
                if all(queue.is_empty() for queue in self.queues):
                    raise StopIteration
                self.add_new_queue()
            try:
                return next(queue)
            except StopIteration:
                continue

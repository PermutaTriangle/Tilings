import itertools
import math
from array import array
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
    Type,
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
from comb_spec_searcher.class_db import ClassDB, ClassKey, Info, Key
from comb_spec_searcher.class_queue import CSSQueue, DefaultQueue, WorkPacket
from comb_spec_searcher.rule_db.abstract import RuleDBAbstract
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.strategies.strategy import DisjointUnionStrategy
from comb_spec_searcher.typing import CombinatorialClassType, CSSstrategy
from permuta import Basis, Perm
from tilings import GriddedPerm, Tiling
from tilings.assumptions import (
    Assumption,
    EqualParityAssumption,
    EvenCountAssumption,
    OddCountAssumption,
)
from tilings.strategies.predicate_refinement import RefinePredicatesStrategy
from tilings.strategies.verification import BasicVerificationStrategy
from tilings.strategy_pack import TileScopePack
from tilings.tiling import set_debug

__all__ = ("TileScope", "TileScopePack", "LimitedAssumptionTileScope", "GuidedSearcher")

Cell = Tuple[int, int]
TrackedClassAssumption = Tuple[int, Tuple[Cell, ...]]
TrackedClassDBKey = Tuple[int, Tuple[TrackedClassAssumption, ...]]


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
        classdb: Optional[ClassDB] = None,
        classqueue: Optional[CSSQueue] = None,
        expand_verified: bool = False,
        debug: bool = False,
    ) -> None:
        """Initialise TileScope."""
        if debug:
            set_debug()
        start_tiling, basis = self.get_start_tiling(start_class)

        if start_tiling.dimensions == (1, 1):
            logger.debug("Fixing basis in basis aware verification strategies.")
            assert isinstance(basis, Basis)
            strategy_pack = strategy_pack.add_basis(basis)
        strategy_pack = strategy_pack.setup_subclass_verification(start_tiling)

        super().__init__(
            start_class=start_tiling,
            strategy_pack=strategy_pack,
            classdb=classdb,
            ruledb=ruledb,
            classqueue=classqueue,
            expand_verified=expand_verified,
            debug=debug,
        )

    @staticmethod
    def get_start_tiling(
        start_class: Union[str, Iterable[Perm], Tiling]
    ) -> Tuple[Tiling, Optional[Basis]]:
        """Return the start tiling implied by the input."""
        basis: Optional[Basis] = None
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
            assert basis is not None
            start_tiling = Tiling(
                obstructions=[GriddedPerm.single_cell(patt, (0, 0)) for patt in basis]
            )
        return start_tiling, basis


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
        self.max_assumptions = max_assumptions
        super().__init__(
            start_class,
            strategy_pack,
            classdb=TrackedClassDB(),
            **kwargs,
        )
        self.ignore_full_tiling_assumptions = ignore_full_tiling_assumptions

    def _rules_from_strategy(  # type: ignore
        self, comb_class: CombinatorialClassType, strategy: CSSstrategy
    ) -> Iterator[AbstractRule]:
        """
        Yield all the rules given by a strategy/strategy factory whose children all
        satisfy the max_assumptions constraint.
        """
        # pylint: disable=arguments-differ
        def num_child_assumptions(child: Tiling) -> int:
            return sum(
                1
                for ass in child.tracking_assumptions
                if (not self.ignore_full_tiling_assumptions)
                or len(ass.gps) != len(child.active_cells)
            )

        for rule in super()._rules_from_strategy(comb_class, strategy):
            if all(
                num_child_assumptions(child) <= self.max_assumptions
                for child in rule.children
            ):
                yield rule


class GuidedSearcher(TileScope):
    def __init__(
        self,
        tilings: Iterable[Tiling],
        basis: Tiling,
        pack: TileScopePack,
        **kwargs,
    ):
        self.tilings = frozenset(t.remove_assumptions() for t in tilings)
        super().__init__(
            basis,
            pack,
            classdb=TrackedClassDB(),
            **kwargs,
        )
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
        response = requests.get(URI, timeout=10)
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
            start_class,
            strategy_pack,
            max_assumptions=max_assumptions,
            classqueue=TrackedQueue(
                cast(TileScopePack, strategy_pack), self, delay_next
            ),
            **kwargs,
        )


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
            str(self._underlyng_labels_per_level[level])
            for level in range(len(self.queues))
        )
        table.append(underlying)
        all_labels = ("all labels",) + tuple(
            str(self._all_labels_per_level[level]) for level in range(len(self.queues))
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
        raise StopIteration("No elements in queue")


class TrackedClassDB(ClassDB[Tiling]):
    def __init__(self) -> None:
        super().__init__(Tiling)
        self.classdb = ClassDB(Tiling)
        self.label_to_tilings: List[bytes] = []
        self.tilings_to_label: Dict[bytes, int] = {}
        self.assumption_type_to_int: Dict[Type[Assumption], int] = {}
        self.int_to_assumption_type: List[Type[Assumption]] = []

    def __iter__(self) -> Iterator[int]:
        for key in self.label_to_info:
            yield key

    def __contains__(self, key: Key) -> bool:
        if isinstance(key, Tiling):
            actual_key = self.tiling_to_key(key)
            compressed_key = self._compress_key(actual_key)
            return self.tilings_to_label.get(compressed_key) is not None
        if isinstance(key, int):
            return 0 <= key < len(self.label_to_tilings)
        raise ValueError("Invalid key")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrackedClassDB):
            return NotImplemented
        return bool(
            self.classdb == other.classdb
            and self.label_to_tilings == other.label_to_tilings
            and self.tilings_to_label == other.tilings_to_label
        )

    def tiling_to_key(self, tiling: Tiling) -> TrackedClassDBKey:
        """
        Converts a tiling to its corresponding key.
        """
        underlying_label = self.classdb.get_label(tiling.remove_assumptions())
        assumption_keys = tuple(
            self.assumption_to_key(ass) for ass in tiling.assumptions
        )
        return (underlying_label, assumption_keys)

    def assumption_to_key(self, ass: Assumption) -> TrackedClassAssumption:
        """
        Determines the type of the assumption and retrieves the int representing
        that type from the appropriate class variables, and then apprends the cells.
        """
        try:
            ass_type_int = self.assumption_type_to_int[type(ass)]
        except KeyError:
            ass_type_int = len(self.int_to_assumption_type)
            assert ass_type_int < 256
            self.int_to_assumption_type.append(type(ass))
            self.assumption_type_to_int[type(ass)] = ass_type_int
        return (ass_type_int, ass.get_cells())

    def key_to_tiling(self, key: TrackedClassDBKey) -> Tiling:
        """
        Converts a key back to a Tiling.
        """
        return self.classdb.get_class(key[0]).add_assumptions(
            (
                self.int_to_assumption_type[ass_key[0]].from_cells(ass_key[1])
                for ass_key in key[1]
            ),
            clean=False,
        )

    @staticmethod
    def _compress_key(key: TrackedClassDBKey) -> bytes:
        # Assumes there are fewer than 256 assumptions
        # Assumes every assumption covers fewer than 256 cells
        # Assumes the positions in an assumption have value < 256

        def int_to_bytes(n: int) -> List[int]:
            """
            Converts an int to a list of ints all in [0 .. 255] ready for
            byte compression. First entry is the number of bytes needed (assumes < 256),
            remaining entries the bytes composing the int from lowest byte up to largest
            byte.
            """
            bytes_needed = max(math.ceil(n.bit_length() / 8), 1)
            result: List[int] = [bytes_needed]
            while n >= 2**8:
                result.append(n & 0xFF)
                n = n >> 8
            result.append(n)
            return result

        def _compress_assumption(ass_key: TrackedClassAssumption) -> List[int]:
            type_int, cells = ass_key
            assert type_int < 256
            assert len(cells) < 256
            assert all(cell[0] < 256 and cell[1] < 256 for cell in cells)

            result = [type_int]
            result.append(len(cells))
            result.extend(itertools.chain(*cells))
            return result

        result: List[int] = int_to_bytes(key[0])
        result.extend(
            itertools.chain.from_iterable(
                _compress_assumption(ass_key) for ass_key in key[1]
            )
        )
        compressed_key = array("B", result).tobytes()
        return compressed_key

    @staticmethod
    def _decompress_key(compressed_key: bytes) -> TrackedClassDBKey:
        def int_from_bytes(n: array) -> int:
            """
            Converts a list of ints to a single int assuming the first entry is the
            lowest byte and so on.
            """
            result = n[0]
            for idx in range(1, len(n)):
                result |= n[idx] << (8 * idx)
            return cast(int, result)

        def _decompress_tuple_of_cells(
            compressed_cells: array,
        ) -> Tuple[Cell, ...]:
            """
            compressed_cells is a list of 2*i bytes, each of which is a coordinates
            """
            vals = iter(compressed_cells)
            return tuple(
                (next(vals), next(vals)) for _ in range(len(compressed_cells) // 2)
            )

        vals = array("B", compressed_key)
        offset = 0

        num_bytes_int = vals[offset]
        offset += 1
        label = int_from_bytes(vals[offset : offset + num_bytes_int])
        offset += num_bytes_int

        tuples_of_cells = []
        while offset < len(vals):
            type_int, num_cells = vals[offset : offset + 2]
            offset += 2
            tuples_of_cells.append(
                (
                    type_int,
                    _decompress_tuple_of_cells(vals[offset : offset + 2 * num_cells]),
                )
            )
            offset += 2 * num_cells

        return (label, tuple(tuples_of_cells))

    def add(self, comb_class: ClassKey, compressed: bool = False) -> None:
        """
        Adds a Tiling to the classdb
        """
        if compressed:
            raise NotImplementedError
        if isinstance(comb_class, Tiling):
            key = self.tiling_to_key(comb_class)
            compressed_key = self._compress_key(key)
            if compressed_key not in self.tilings_to_label:
                self.label_to_tilings.append(compressed_key)
                self.tilings_to_label[compressed_key] = len(self.tilings_to_label)

    def _get_info(self, key: Key) -> Info:
        """
        Return the "Info" object corresponding to the key, which is
        either a Tiling or an integer
        """
        # pylint: disable=protected-access
        if isinstance(key, Tiling):
            actual_key = self.tiling_to_key(key)
            compressed_key = self._compress_key(actual_key)
            if compressed_key not in self.tilings_to_label:
                self.add(key)
            info: Optional[Info] = self.classdb._get_info(actual_key[0])
            if info is None:
                raise ValueError("Invalid key")
            info = Info(
                key,
                self.tilings_to_label[compressed_key],
                info.empty,
            )
        elif isinstance(key, int):
            if not 0 <= key < len(self.label_to_tilings):
                raise KeyError("Key not in ClassDB")
            tiling_key = self._decompress_key(self.label_to_tilings[key])
            info = self.classdb.label_to_info.get(tiling_key[0])
            if info is None:
                raise ValueError("Invalid key")
            info = Info(
                self.key_to_tiling(tiling_key),
                key,
                info.empty,
            )
        else:
            raise TypeError()
        return info

    def get_class(self, key: Key) -> Tiling:
        """
        Return combinatorial class of key.
        """
        info = self._get_info(key)
        return cast(Tiling, info.comb_class)

    def is_empty(self, comb_class: Tiling, label: Optional[int] = None) -> bool:
        """
        Return True if combinatorial class is set to be empty, False if not.
        """
        return bool(self.classdb.is_empty(comb_class.remove_assumptions()))

    def set_empty(self, key: Key, empty: bool = True) -> None:
        """
        Set a class to be empty.
        """
        if isinstance(key, int):
            if 0 <= key < len(self.label_to_tilings):
                underlying_label, _ = self._decompress_key(self.label_to_tilings[key])
        if isinstance(key, Tiling):
            underlying_label = self.classdb.get_label(key.remove_assumptions())
        self.classdb.set_empty(underlying_label, empty)

    def status(self) -> str:
        """
        Return a string with the current status of the run.
        """
        status = self.classdb.status()
        status = status.replace("combinatorial classes", "underlying tilings")
        tilings = "\n\tTotal number of tilings found is"
        tilings += f" {len(self.label_to_tilings):,d}"
        status = status.replace("ClassDB status:", "TrackedClassDB status:" + tilings)
        return status + "\n"


class OddOrEvenStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    def __init__(self):
        super().__init__(True, True, True, True)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, Tiling]:
        return (
            comb_class.add_assumption(
                EvenCountAssumption.from_cells(comb_class.active_cells)
            ),
            comb_class.add_assumption(
                OddCountAssumption.from_cells(comb_class.active_cells)
            ),
        )

    def formal_step(self) -> str:
        return "has an odd or even number of points"

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        if children is None:
            children = self.decomposition_function(comb_class)
        try:
            gp = next((gp for gp in objs if gp is not None))
            yield gp
        except StopIteration:
            return StopIteration

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        if len(obj) % 2:
            return (obj, None)
        return (None, obj)

    def extra_parameters(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Dict[str, str], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        return tuple(
            {
                comb_class.get_assumption_parameter(
                    ass
                ): child.get_assumption_parameter(ass)
                for ass in comb_class.tracking_assumptions
            }
            if not child.is_empty()
            else {}
            for child in children
        )

    @classmethod
    def from_dict(cls, d: dict) -> "OddOrEvenStrategy":
        return cls()


class ParityScope(TrackedSearcher):
    def __init__(
        self,
        start_class: Union[str, Iterable[Perm], Tiling],
        strategy_pack: TileScopePack,
        max_assumptions: int,
        delay_next: bool = False,
        **kwargs,
    ) -> None:
        strategy_pack = strategy_pack.add_initial(
            RefinePredicatesStrategy(), apply_first=True
        )
        strategy_pack.ver_strats = (BasicVerificationStrategy(),)
        strategy_pack.name = "parity_" + strategy_pack.name
        super().__init__(
            start_class,
            strategy_pack,
            max_assumptions,
            delay_next,
            **kwargs,
        )
        rule = OddOrEvenStrategy()(self.start_class)
        end_labels = tuple(self.classdb.get_label(child) for child in rule.children)
        self.add_rule(self.start_label, end_labels, rule)

    @staticmethod
    def get_start_tiling(
        start_class: Union[str, Iterable[Perm], Tiling]
    ) -> Tuple[Tiling, Optional[Basis]]:
        start_tiling, basis = TileScope.get_start_tiling(start_class)
        return (
            start_tiling.add_assumption(
                EqualParityAssumption.from_cells(start_tiling.active_cells)
            ),
            basis,
        )

from itertools import chain
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple, cast

from sympy import Eq, Function

from comb_spec_searcher import (
    CartesianProduct,
    CartesianProductStrategy,
    CombinatorialObject,
    Strategy,
    StrategyFactory,
)
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies.constructor import SubGens, SubRecs, SubSamplers
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import (
    Factor,
    FactorWithInterleaving,
    FactorWithMonotoneInterleaving,
)
from tilings.assumptions import TrackingAssumption
from tilings.exception import InvalidOperationError
from tilings.misc import partitions_iterator

Cell = Tuple[int, int]

__all__ = (
    "FactorFactory",
    "FactorStrategy",
    "FactorWithInterleavingStrategy",
    "FactorWithMonotoneInterleavingStrategy",
)


class FactorStrategy(CartesianProductStrategy[Tiling, GriddedPerm]):
    def __init__(
        self,
        partition: Iterable[Iterable[Cell]],
        ignore_parent: bool = True,
        workable: bool = True,
    ):
        self.partition = tuple(sorted(tuple(sorted(p)) for p in partition))
        super().__init__(ignore_parent=ignore_parent, workable=workable)

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, ...]:
        return tuple(tiling.sub_tiling(cells) for cells in self.partition)

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Dict[str, str], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        extra_parameters: Tuple[Dict[str, str], ...] = tuple({} for _ in children)
        for parent_var, assumption in zip(
            comb_class.extra_parameters, comb_class.assumptions
        ):
            for i, cells in enumerate(self.partition):
                if assumption.gps[0].pos[0] in cells:
                    new_assumption = TrackingAssumption(
                        children[i].forward_map(gp) for gp in assumption.gps
                    )
                    child_var = children[i].get_parameter(new_assumption)
                    extra_parameters[i][parent_var] = child_var
                    break
            else:
                raise ValueError("Assumption was not mapped to any child")
        return extra_parameters

    def formal_step(self) -> str:
        """
        Return a string that describe the operation performed on the tiling.
        """
        return "factor with partition {}".format(
            " / ".join(
                "{{{}}}".format(", ".join(str(c) for c in part))
                for part in self.partition
            )
        )

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> GriddedPerm:
        if children is None:
            children = self.decomposition_function(tiling)
        gps_to_combine = tuple(
            tiling.backward_map(cast(GriddedPerm, gp))
            for gp, tiling in zip(gps, children)
        )
        temp = [
            ((cell[0], idx), (cell[1], val))
            for gp in gps_to_combine
            for (idx, val), cell in zip(enumerate(gp.patt), gp.pos)
        ]
        temp.sort()
        new_pos = [(idx[0], val[0]) for idx, val in temp]
        new_patt = Perm.to_standard(val for _, val in temp)
        return GriddedPerm(new_patt, new_pos)

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm, ...]:
        if children is None:
            children = self.decomposition_function(tiling)
        return tuple(
            tiling.forward_map(gp.get_gridded_perm_in_cells(part))
            for tiling, part in zip(children, self.partition)
        )

    def __str__(self) -> str:
        return "factor"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "(partition={}, workable={})".format(
            self.partition, self.workable
        )

    # JSON methods

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the strategy."""
        d: dict = super().to_jsonable()
        d.pop("inferrable")
        d.pop("possibly_empty")
        d["partition"] = self.partition
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "FactorStrategy":
        partition = cast(
            Tuple[Tuple[Cell]],
            tuple(tuple(tuple(c) for c in p) for p in d.pop("partition")),
        )
        return cls(partition=partition, **d)


class Interleaving(CartesianProduct):
    def __init__(self, children: Tuple[Tiling, ...]):
        super().__init__(children)

    @staticmethod
    def is_equivalence() -> bool:
        return False

    @staticmethod
    def get_equation(lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        raise NotImplementedError

    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
        raise NotImplementedError

    def get_sub_objects(
        self, subgens: SubGens, n: int, **parameters: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        raise NotImplementedError

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int
    ):
        raise NotImplementedError

    @staticmethod
    def get_eq_symbol() -> str:
        return "="

    @staticmethod
    def get_op_symbol() -> str:
        return "*"


class FactorWithInterleavingStrategy(FactorStrategy):
    def __init__(
        self,
        partition: Iterable[Iterable[Cell]],
        ignore_parent: bool = True,
        workable: bool = True,
        tracked: bool = True,
    ):
        self.tracked = tracked
        super().__init__(partition, ignore_parent, workable)

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, ...]:
        if not self.tracked:
            return super().decomposition_function(tiling)
        cols, rows = self._interleaving_rows_and_cols()
        return tuple(
            tiling.sub_tiling(
                cells, add_assumptions=self._assumptions_to_add(cells, cols, rows)
            )
            for cells in self.partition
        )

    @staticmethod
    def _assumptions_to_add(
        cells: Tuple[Cell, ...], cols: Set[int], rows: Set[int]
    ) -> Tuple[TrackingAssumption, ...]:
        """
        Return the assumption that should be tracked if we are interleaving
        the given rows and cols.
        """
        col_assumptions = [
            TrackingAssumption(
                [
                    GriddedPerm.single_cell(Perm((0,)), cell)
                    for cell in cells
                    if x == cell[0]
                ]
            )
            for x in cols
        ]
        row_assumptions = [
            TrackingAssumption(
                [
                    GriddedPerm.single_cell(Perm((0,)), cell)
                    for cell in cells
                    if y == cell[1]
                ]
            )
            for y in rows
        ]
        return tuple(ass for ass in chain(col_assumptions, row_assumptions) if ass.gps)

    def _interleaving_rows_and_cols(self) -> Tuple[Set[int], Set[int]]:
        """
        Return the set of cols and the set of rows that are being interleaved.
        """
        cols: Set[int] = set()
        rows: Set[int] = set()
        x_seen: Set[int] = set()
        y_seen: Set[int] = set()
        for part in self.partition:
            cols.update(x for x, _ in part if x in x_seen)
            rows.update(y for _, y in part if y in y_seen)
            x_seen.update(x for x, _ in part)
            y_seen.update(y for _, y in part)
        return cols, rows

    def formal_step(self) -> str:
        return "interleaving " + super().formal_step()

    def constructor(
        self, tiling: Tiling, children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Interleaving:
        if children is None:
            children = self.decomposition_function(tiling)
        return Interleaving(children)

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> GriddedPerm:
        raise NotImplementedError

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm, ...]:
        raise NotImplementedError

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the strategy."""
        d: dict = super().to_jsonable()
        d["tracked"] = self.tracked
        return d

    def __str__(self) -> str:
        return ("tracked " if self.tracked else "") + "interleaving factors"

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + f"(partition={self.partition}, workable={self.workable}, tracked={self.tracked})"
        )


class MonotoneInterleaving(Interleaving):
    pass


class FactorWithMonotoneInterleavingStrategy(FactorWithInterleavingStrategy):
    def constructor(
        self, tiling: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> MonotoneInterleaving:
        if children is None:
            children = self.decomposition_function(tiling)
        return MonotoneInterleaving(children)


class FactorFactory(StrategyFactory[Tiling]):

    FACTOR_ALGO_AND_CLASS = {
        None: (Factor, FactorStrategy),
        "monotone": (
            FactorWithMonotoneInterleaving,
            FactorWithMonotoneInterleavingStrategy,
        ),
        "all": (FactorWithInterleaving, FactorWithInterleavingStrategy),
    }

    def __init__(
        self,
        interleaving: Optional[str] = None,
        unions: bool = False,
        ignore_parent: bool = True,
        workable: bool = True,
        tracked: bool = True,
    ) -> None:
        try:
            self.factor_algo, self.factor_class = self.FACTOR_ALGO_AND_CLASS[
                interleaving
            ]
        except KeyError:
            raise InvalidOperationError(
                "Invalid interleaving option. Must be in {}, used {}".format(
                    FactorFactory.FACTOR_ALGO_AND_CLASS.keys(), interleaving
                )
            )
        self.unions = unions
        self.ignore_parent = ignore_parent
        self.workable = workable
        self.tracked = tracked and self.factor_class in (
            FactorWithInterleavingStrategy,
            FactorWithMonotoneInterleaving,
        )

    @staticmethod
    def interleaving_components(components: Iterable[Iterable[Cell]]) -> bool:
        x_seen: Set[int] = set()
        y_seen: Set[int] = set()
        for component in components:
            if any(x in x_seen or y in y_seen for x, y in component):
                return True
            x_seen.update(x for x, _ in component)
            y_seen.update(y for _, y in component)
        return False

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[Strategy]:
        factor_algo = self.factor_algo(comb_class)
        if factor_algo.factorable():
            min_comp = factor_algo.get_components()
            if self.unions:
                for partition in partitions_iterator(min_comp):
                    components = tuple(
                        tuple(chain.from_iterable(part)) for part in partition
                    )
                    if self.interleaving_components(components):
                        yield FactorWithInterleavingStrategy(
                            components,
                            ignore_parent=self.ignore_parent,
                            workable=False,
                            tracked=True,
                        )
                    else:
                        yield FactorStrategy(
                            components, ignore_parent=self.ignore_parent, workable=False
                        )
            if self.interleaving_components(min_comp):
                yield FactorWithInterleavingStrategy(
                    min_comp,
                    ignore_parent=self.ignore_parent,
                    workable=self.workable,
                    tracked=self.tracked,
                )
            else:
                yield FactorStrategy(
                    min_comp, ignore_parent=self.ignore_parent, workable=self.workable
                )

    def __str__(self) -> str:
        if self.factor_class is FactorStrategy:
            s = "factor"
        elif self.factor_class is FactorWithInterleavingStrategy:
            s = "factor with monotone interleaving"
        elif self.factor_class is FactorWithMonotoneInterleavingStrategy:
            s = "factor with interleaving"
        else:
            raise Exception("Invalid interleaving type")
        if self.unions:
            s = "unions of " + s
        if self.tracked:
            s = "tracked " + s
        return s

    def __repr__(self) -> str:
        if self.factor_class is FactorStrategy:
            interleaving = None
        elif self.factor_class is FactorWithInterleavingStrategy:
            interleaving = "all"
        elif self.factor_class is FactorWithMonotoneInterleavingStrategy:
            interleaving = "monotone"
        return (
            f"AllFactorStrategy(interleaving={interleaving}, unions={self.unions},"
            f" ignore_parent={self.ignore_parent}, workable={self.workable})"
        )

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        if self.factor_class is FactorStrategy:
            interleaving = None
        elif self.factor_class is FactorWithInterleavingStrategy:
            interleaving = "all"
        elif self.factor_class is FactorWithMonotoneInterleavingStrategy:
            interleaving = "monotone"
        d["interleaving"] = interleaving
        d["unions"] = self.unions
        d["ignore_parent"] = self.ignore_parent
        d["workable"] = self.workable
        d["tracked"] = self.tracked
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "FactorFactory":
        return cls(**d)

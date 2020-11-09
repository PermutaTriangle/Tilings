from collections import Counter
from functools import reduce
from itertools import chain
from operator import mul
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple, cast

from sympy import Eq, Function

from comb_spec_searcher import (
    CartesianProduct,
    CartesianProductStrategy,
    Strategy,
    StrategyFactory,
)
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.typing import (
    Parameters,
    SubObjects,
    SubRecs,
    SubSamplers,
    SubTerms,
    Terms,
)
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import (
    Factor,
    FactorWithInterleaving,
    FactorWithMonotoneInterleaving,
)
from tilings.assumptions import TrackingAssumption
from tilings.exception import InvalidOperationError
from tilings.misc import multinomial, partitions_iterator

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
        inferrable = any(interleaving_rows_and_cols(self.partition))
        super().__init__(
            ignore_parent=ignore_parent, workable=workable, inferrable=inferrable
        )

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, ...]:
        return tuple(tiling.sub_tiling(cells) for cells in self.partition)

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        extra_parameters: Tuple[Dict[str, str], ...] = tuple({} for _ in children)
        for parent_var, assumption in zip(
            comb_class.extra_parameters, comb_class.assumptions
        ):
            for idx, child in enumerate(children):
                # TODO: consider skew/sum
                new_assumption = child.forward_map_assumption(assumption)
                if new_assumption.gps:
                    child_var = child.get_assumption_parameter(new_assumption)
                    extra_parameters[idx][parent_var] = child_var
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
    ) -> Iterator[GriddedPerm]:
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
        yield GriddedPerm(new_patt, new_pos)

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


# The following functions are used to determine assumptions needed to count the
# interleavings of a factor. They are also used by AddInterleavingAssumptionStrategy.


def interleaving_rows_and_cols(
    partition: Tuple[Tuple[Cell, ...], ...]
) -> Tuple[Set[int], Set[int]]:
    """
    Return the set of cols and the set of rows that are being interleaved when
    factoring with partition.
    """
    cols: Set[int] = set()
    rows: Set[int] = set()
    x_seen: Set[int] = set()
    y_seen: Set[int] = set()
    for part in partition:
        cols.update(x for x, _ in part if x in x_seen)
        rows.update(y for _, y in part if y in y_seen)
        x_seen.update(x for x, _ in part)
        y_seen.update(y for _, y in part)
    return cols, rows


def assumptions_to_add(
    cells: Tuple[Cell, ...], cols: Set[int], rows: Set[int]
) -> Tuple[TrackingAssumption, ...]:
    """
    Return the assumptions that should be tracked in the set of cells if we are
    interleaving the given rows and cols.
    """
    col_assumptions = [
        TrackingAssumption(
            [GriddedPerm.point_perm(cell) for cell in cells if x == cell[0]]
        )
        for x in cols
    ]
    row_assumptions = [
        TrackingAssumption(
            [GriddedPerm.point_perm(cell) for cell in cells if y == cell[1]]
        )
        for y in rows
    ]
    return tuple(ass for ass in chain(col_assumptions, row_assumptions) if ass.gps)


def contains_interleaving_assumptions(
    comb_class: Tiling, partition: Tuple[Tuple[Cell, ...], ...]
) -> bool:
    """
    Return True if the parent tiling contains all of the necessary tracking
    assumptions needed to count the interleavings, and therefore the
    children too.
    """
    cols, rows = interleaving_rows_and_cols(partition)
    return all(
        ass in comb_class.assumptions
        for ass in chain.from_iterable(
            assumptions_to_add(cells, cols, rows) for cells in partition
        )
    )


class Interleaving(CartesianProduct[Tiling, GriddedPerm]):
    def __init__(
        self,
        parent: Tiling,
        children: Iterable[Tiling],
        extra_parameters: Tuple[Dict[str, str], ...],
        interleaving_parameters: Iterable[Tuple[str, ...]],
    ):
        super().__init__(parent, children, extra_parameters)
        self.interleaving_parameters = tuple(interleaving_parameters)
        self.interleaving_indices = tuple(
            tuple(parent.extra_parameters.index(k) for k in parameters)
            for parameters in interleaving_parameters
        )

    @staticmethod
    def is_equivalence() -> bool:
        return False

    @staticmethod
    def get_equation(lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        raise NotImplementedError

    def get_terms(self, subterms: SubTerms, n: int) -> Terms:
        non_interleaved_terms = super().get_terms(subterms, n)
        interleaved_terms: Terms = Counter()
        for parameters, value in non_interleaved_terms.items():
            # multinomial counts the number of ways to interleave the values k1, ...,kn.
            multiplier = reduce(
                mul,
                [
                    multinomial([parameters[k] for k in int_parameters])
                    for int_parameters in self.interleaving_indices
                ],
                1,
            )
            interleaved_terms[parameters] += multiplier * value
        return interleaved_terms

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[Tuple[Parameters, Tuple[List[Optional[GriddedPerm]], ...]]]:
        raise NotImplementedError

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ):
        raise NotImplementedError


class FactorWithInterleavingStrategy(FactorStrategy):
    def formal_step(self) -> str:
        return "interleaving " + super().formal_step()

    def constructor(
        self, tiling: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Interleaving:
        if children is None:
            children = self.decomposition_function(tiling)
        try:
            interleaving_parameters = self.interleaving_parameters(tiling)
        except ValueError as e:
            # must be untracked
            raise NotImplementedError("The interleaving factor was not tracked.") from e
        return Interleaving(
            tiling,
            children,
            self.extra_parameters(tiling, children),
            interleaving_parameters,
        )

    def interleaving_parameters(self, comb_class: Tiling) -> List[Tuple[str, ...]]:
        """
        Return the parameters on the parent tiling that needed to be interleaved.
        """
        res: List[Tuple[str, ...]] = []
        cols, rows = interleaving_rows_and_cols(self.partition)
        for x in cols:
            assumptions = [
                TrackingAssumption(
                    GriddedPerm.point_perm(cell) for cell in cells if x == cell[0]
                )
                for cells in self.partition
            ]
            res.append(
                tuple(
                    comb_class.get_assumption_parameter(ass)
                    for ass in assumptions
                    if ass.gps
                )
            )
        for y in rows:
            assumptions = [
                TrackingAssumption(
                    GriddedPerm.point_perm(cell) for cell in cells if y == cell[1]
                )
                for cells in self.partition
            ]
            res.append(
                tuple(
                    comb_class.get_assumption_parameter(ass)
                    for ass in assumptions
                    if ass.gps
                )
            )
        return res

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm, ...]:
        raise NotImplementedError

    @staticmethod
    def get_eq_symbol() -> str:
        return "="

    @staticmethod
    def get_op_symbol() -> str:
        return "*"

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + f"(partition={self.partition}, workable={self.workable})"
        )


class MonotoneInterleaving(Interleaving):
    pass


class FactorWithMonotoneInterleavingStrategy(FactorWithInterleavingStrategy):
    def constructor(
        self, tiling: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> MonotoneInterleaving:
        if children is None:
            children = self.decomposition_function(tiling)
        try:
            interleaving_parameters = self.interleaving_parameters(tiling)
        except ValueError as e:
            # must be untracked
            raise NotImplementedError(
                "The monotone interleaving was not tracked."
            ) from e
        return MonotoneInterleaving(
            tiling,
            children,
            self.extra_parameters(tiling, children),
            interleaving_parameters,
        )


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
        tracked: bool = False,
    ) -> None:
        try:
            self.factor_algo, self.factor_class = self.FACTOR_ALGO_AND_CLASS[
                interleaving
            ]
        except KeyError as e:
            raise InvalidOperationError(
                "Invalid interleaving option. Must be in "
                f"{FactorFactory.FACTOR_ALGO_AND_CLASS.keys()}, "
                f"used {interleaving}"
            ) from e
        self.unions = unions
        self.ignore_parent = ignore_parent
        self.workable = workable
        self.tracked = tracked and self.factor_class in (
            FactorWithInterleavingStrategy,
            FactorWithMonotoneInterleaving,
        )

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[Strategy]:
        factor_algo = self.factor_algo(comb_class)
        if factor_algo.factorable():
            min_comp = tuple(tuple(part) for part in factor_algo.get_components())
            if self.unions:
                for partition in partitions_iterator(min_comp):
                    components = tuple(
                        tuple(chain.from_iterable(part)) for part in partition
                    )
                    if not self.tracked or contains_interleaving_assumptions(
                        comb_class, components
                    ):
                        yield self._build_strategy(components, workable=False)
            if not self.tracked or contains_interleaving_assumptions(
                comb_class, min_comp
            ):
                yield self._build_strategy(min_comp, workable=self.workable)

    def _build_strategy(
        self, components: Tuple[Tuple[Cell, ...], ...], workable: bool
    ) -> FactorStrategy:
        """
        Build the factor strategy for the given components.

        It ensure that a plain factor rule is returned.
        """
        interleaving = any(interleaving_rows_and_cols(components))
        factor_strat = self.factor_class if interleaving else FactorStrategy
        return factor_strat(
            components, ignore_parent=self.ignore_parent, workable=workable
        )

    def __str__(self) -> str:
        if self.factor_class is FactorStrategy:
            s = "factor"
        elif self.factor_class is FactorWithInterleavingStrategy:
            s = "factor with interleaving"
        elif self.factor_class is FactorWithMonotoneInterleavingStrategy:
            s = "factor with monotone interleaving"
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

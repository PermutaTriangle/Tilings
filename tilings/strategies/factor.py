from collections import Counter
from functools import reduce
from itertools import chain, combinations
from operator import mul
from typing import (
    Callable,
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

from sympy import Eq, Function

from comb_spec_searcher import (
    CartesianProduct,
    CartesianProductStrategy,
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
from tilings.strategies.assumption_insertion import (
    AddAssumptionsConstructor,
    AddAssumptionsStrategy,
)

Cell = Tuple[int, int]

__all__ = (
    "FactorFactory",
    "FactorStrategy",
    "FactorWithInterleavingStrategy",
    "FactorWithMonotoneInterleavingStrategy",
)

TempGP = Tuple[
    Tuple[
        Tuple[Union[float, int], ...], Tuple[Union[float, int], ...], Tuple[Cell, ...]
    ],
    ...,
]


class FactorStrategy(CartesianProductStrategy[Tiling, GriddedPerm]):
    def __init__(
        self,
        partition: Iterable[Iterable[Cell]],
        ignore_parent: bool = True,
        workable: bool = True,
    ):
        self.partition = tuple(sorted(tuple(sorted(p)) for p in partition))
        inferrable = any(
            FactorWithInterleavingStrategy.interleaving_rows_and_cols(self.partition)
        )
        super().__init__(
            ignore_parent=ignore_parent, workable=workable, inferrable=inferrable
        )

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        return tuple(comb_class.sub_tiling(cells) for cells in self.partition)

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
                new_assumption = child.forward_map.map_assumption(assumption).avoiding(
                    child.obstructions
                )
                if new_assumption.gps:
                    child_var = child.get_assumption_parameter(new_assumption)
                    extra_parameters[idx][parent_var] = child_var
        return extra_parameters

    def formal_step(self) -> str:
        """
        Return a string that describe the operation performed on the tiling.
        """
        partition_str = " / ".join(
            f"{{{', '.join(map(str, part))}}}" for part in self.partition
        )
        return f"factor with partition {partition_str}"

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        if children is None:
            children = self.decomposition_function(comb_class)
        gps_to_combine = tuple(
            tiling.backward_map.map_gp(cast(GriddedPerm, gp))
            for gp, tiling in zip(objs, children)
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
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm, ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        return tuple(
            tiling.forward_map.map_gp(obj.get_gridded_perm_in_cells(part))
            for tiling, part in zip(children, self.partition)
        )

    def __str__(self) -> str:
        return "factor"

    def __repr__(self) -> str:
        args = ", ".join(
            [
                f"partition={self.partition}",
                f"ignore_parent={self.ignore_parent}",
                f"workable={self.workable}",
            ]
        )
        return f"{self.__class__.__name__}({args})"

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


class Interleaving(CartesianProduct[Tiling, GriddedPerm]):
    def __init__(
        self,
        parent: Tiling,
        children: Iterable[Tiling],
        extra_parameters: Tuple[Dict[str, str], ...],
        interleaving_parameters: Iterable[Tuple[str, ...]],
        insertion_constructor: Optional[AddAssumptionsConstructor],
    ):
        super().__init__(parent, children, extra_parameters)
        self.interleaving_parameters = tuple(interleaving_parameters)
        self.interleaving_indices = tuple(
            tuple(parent.extra_parameters.index(k) for k in parameters)
            for parameters in interleaving_parameters
        )
        self.insertion_constructor = insertion_constructor

    @staticmethod
    def is_equivalence() -> bool:
        return False

    @staticmethod
    def get_equation(lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        raise NotImplementedError

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        non_interleaved_terms = super().get_terms(parent_terms, subterms, n)
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
        if self.insertion_constructor:
            new_terms: Terms = Counter()
            for param, value in interleaved_terms.items():
                new_terms[self.insertion_constructor.child_param_map(param)] += value
            return new_terms
        return interleaved_terms

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[Tuple[Parameters, Tuple[List[Optional[GriddedPerm]], ...]]]:
        for param, objs in super().get_sub_objects(subobjs, n):
            if self.insertion_constructor:
                param = self.insertion_constructor.child_param_map(param)
            yield param, objs

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
    def __init__(
        self,
        partition: Iterable[Iterable[Cell]],
        ignore_parent: bool = True,
        workable: bool = True,
        tracked: bool = True,
    ):
        super().__init__(partition, ignore_parent, workable)
        self.tracked = tracked
        self.cols, self.rows = self.interleaving_rows_and_cols(self.partition)

    def formal_step(self) -> str:
        return "interleaving " + super().formal_step()

    def assumptions_to_add(self, comb_class: Tiling) -> Tuple[TrackingAssumption, ...]:
        """Return the set of assumptions that need to be added to"""
        cols, rows = self.interleaving_rows_and_cols(self.partition)
        return tuple(
            ass
            for ass in chain.from_iterable(
                self._assumptions_to_add(cells, cols, rows) for cells in self.partition
            )
            if ass not in comb_class.assumptions
        )

    @staticmethod
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

    @staticmethod
    def _assumptions_to_add(
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

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        if self.tracked:
            comb_class = comb_class.add_assumptions(self.assumptions_to_add(comb_class))
        return super().decomposition_function(comb_class)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Interleaving:
        if children is None:
            children = self.decomposition_function(comb_class)
        assumptions = self.assumptions_to_add(comb_class)
        insertion_constructor = None
        if assumptions:
            insertion_constructor = AddAssumptionsStrategy(assumptions).constructor(
                comb_class
            )
            comb_class = comb_class.add_assumptions(assumptions)
        interleaving_parameters = self.interleaving_parameters(comb_class)
        if interleaving_parameters and not self.tracked:
            raise NotImplementedError("The interleaving factor was not tracked.")
        return Interleaving(
            comb_class,
            children,
            self.extra_parameters(comb_class, children),
            interleaving_parameters,
            insertion_constructor,
        )

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ):
        raise NotImplementedError

    def interleaving_parameters(self, comb_class: Tiling) -> List[Tuple[str, ...]]:
        """
        Return the parameters on the parent tiling that needed to be interleaved.
        """
        res: List[Tuple[str, ...]] = []
        cols, rows = self.interleaving_rows_and_cols(self.partition)
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
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        if children is None:
            children = self.decomposition_function(comb_class)
        gps_to_combine = tuple(
            tiling.backward_map.map_gp(cast(GriddedPerm, gp))
            for gp, tiling in zip(objs, children)
        )
        all_gps_to_combine: List[TempGP] = [
            tuple(
                (tuple(range(len(gp))), tuple(gp.patt), gp.pos) for gp in gps_to_combine
            )
        ]
        for row in self.rows:
            all_gps_to_combine = self._interleave_row(all_gps_to_combine, row)
        for col in self.cols:
            all_gps_to_combine = self._interleave_col(all_gps_to_combine, col)

        for interleaved_gps_to_combine in all_gps_to_combine:
            temp = [
                ((cell[0], idx), (cell[1], val))
                for gp in interleaved_gps_to_combine
                for idx, val, cell in zip(*gp)
            ]
            temp.sort()
            new_pos = [(idx[0], val[0]) for idx, val in temp]
            new_patt = Perm.to_standard(val for _, val in temp)
            assert not GriddedPerm(new_patt, new_pos).contradictory()
            yield GriddedPerm(new_patt, new_pos)

    def _interleave_row(
        self,
        all_gps_to_combine: List[TempGP],
        row: int,
    ) -> List[TempGP]:
        # pylint: disable=too-many-locals
        res: List[TempGP] = []
        for gps_to_combine in all_gps_to_combine:
            row_points = tuple(
                tuple(
                    (idx, values[idx])
                    for idx, cell in enumerate(position)
                    if cell[1] == row
                )
                for _, values, position in gps_to_combine
            )
            total = sum(len(points) for points in row_points)
            if total == 0:
                res.append(gps_to_combine)
                continue
            min_val = min(val for _, val in chain(*row_points))
            max_val = max(val for _, val in chain(*row_points)) + 1
            temp_values = tuple(
                min_val + i * (max_val - min_val) / total for i in range(total)
            )
            for partition in self._partitions(
                set(temp_values), tuple(len(indices) for indices in row_points)
            ):
                new_gps_to_combine = []
                for part, (indices, values, position), points in zip(
                    partition, gps_to_combine, row_points
                ):
                    new_values = list(values)
                    actual_indices = [
                        idx for _, idx in sorted((val, idx) for idx, val in points)
                    ]
                    for idx, val in zip(actual_indices, sorted(part)):
                        new_values[idx] = val
                    new_gps_to_combine.append((indices, tuple(new_values), position))
                res.append(tuple(new_gps_to_combine))
        return res

    def _interleave_col(
        self,
        all_gps_to_combine: List[TempGP],
        col: int,
    ):
        # pylint: disable=too-many-locals
        res: List[TempGP] = []
        for gps_to_combine in all_gps_to_combine:
            col_points = tuple(
                tuple(
                    (idx, indices[idx])
                    for idx, cell in enumerate(position)
                    if cell[0] == col
                )
                for indices, _, position in gps_to_combine
            )
            total = sum(len(points) for points in col_points)
            if total == 0:
                res.append(gps_to_combine)
                continue
            mindex = min(val for _, val in chain(*col_points))
            maxdex = max(val for _, val in chain(*col_points)) + 1
            temp_indices = tuple(
                mindex + i * (maxdex - mindex) / total for i in range(total)
            )
            for partition in self._partitions(
                set(temp_indices), tuple(len(indices) for indices in col_points)
            ):
                new_gps_to_combine = []
                for part, (indices, values, position), points in zip(
                    partition, gps_to_combine, col_points
                ):
                    new_indices = list(indices)
                    for idx, new_idx in zip([idx for idx, _ in points], sorted(part)):
                        new_indices[idx] = new_idx
                    new_gps_to_combine.append((tuple(new_indices), values, position))
                res.append(tuple(new_gps_to_combine))
        return res

    @staticmethod
    def _partitions(
        values: Set[float], size_of_parts: Tuple[int, ...]
    ) -> Iterator[Tuple[Tuple[float, ...], ...]]:
        if not size_of_parts:
            if not values:
                yield tuple()
            return
        size = size_of_parts[0]
        for part in combinations(values, size):
            for rest in FactorWithInterleavingStrategy._partitions(
                values - set(part), size_of_parts[1:]
            ):
                yield (part,) + rest

    @staticmethod
    def get_eq_symbol() -> str:
        return "="

    @staticmethod
    def get_op_symbol() -> str:
        return "*"


class FactorWithMonotoneInterleavingStrategy(FactorWithInterleavingStrategy):
    pass


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

    def __call__(self, comb_class: Tiling) -> Iterator[FactorStrategy]:
        factor_algo = self.factor_algo(comb_class)
        if factor_algo.factorable():
            min_comp = tuple(tuple(part) for part in factor_algo.get_components())
            if self.unions:
                for partition in partitions_iterator(min_comp):
                    components = tuple(
                        tuple(chain.from_iterable(part)) for part in partition
                    )
                    yield self._build_strategy(components, workable=False)
            yield self._build_strategy(min_comp, workable=self.workable)

    def _build_strategy(
        self, components: Tuple[Tuple[Cell, ...], ...], workable: bool
    ) -> FactorStrategy:
        """
        Build the factor strategy for the given components.

        It ensure that a plain factor rule is returned.
        """
        interleaving = any(
            FactorWithInterleavingStrategy.interleaving_rows_and_cols(components)
        )
        if interleaving:
            return cast(
                FactorStrategy,
                self.factor_class(
                    components,
                    ignore_parent=self.ignore_parent,
                    workable=workable,
                    tracked=self.tracked,
                ),
            )
        return FactorStrategy(
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
        args = ", ".join(
            [
                f"interleaving={interleaving!r}",
                f"unions={self.unions}",
                f"ignore_parent={self.ignore_parent}",
                f"workable={self.workable}",
                f"tracked={self.tracked}",
            ]
        )
        return f"{self.__class__.__name__}({args})"

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

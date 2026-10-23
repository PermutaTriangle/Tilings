"""The reduction strategy, which makes a set of cells monotone.

A set of active cells of a tiling is reducible, in a direction (increasing or
decreasing), if every obstruction with points both in the set and outside it has
exactly one point in the set, in the cell c say, and

- it does not have points both in another cell of the row of c and in another
  cell of the column of c;
- if it has a point in another cell of the column (row) of c, then the cells of
  the set in that column (row) are already in the order of the direction: c is
  the only one, or the tiling's obstructions put the points of the lower (left)
  of any two of them all to the left of (below) those of the other, the other
  way round when decreasing;

and every requirement list lies in the set, or each of its gridded permutations
has no point in the set or one point in it that the obstructions may have.

A gridded permutation is the same as, for each column, the word of the cells of
its points from left to right, for each row, the word of the cells of its points
from bottom to top, and the permutation in each cell, chosen independently. The
share of a set of cells in these is the order of its points among themselves in
each column and in each row, and the permutation in each of its cells; the rest
is the places of the set's points among the other points of each column and
row, and the permutations in the other cells. An obstruction with one point in a
reducible set sees that point only through its cell and its place among the
other points of its column or of its row, and which of the set's places there
are the cell's is fixed by the rest: the cell is the only one of the set there,
or the set's own obstructions fix the order of its cells there. Sorting the
share into the canonical one, in which every cell of the set is increasing (or
decreasing), and so are the points of the cells of the set in each row and in
each column, keeps both. So the gridded permutations of the tiling are the pairs
of a gridded permutation of the reduced tiling, whose share is canonical, and
one of the tiling of the set's own obstructions and requirements, with as many
points in the cells of the set.

The reduced tiling keeps what the rest of the tiling sees of the set and no
more. A cell of the set whose row and column have no cell outside the set, and
in which no obstruction or requirement with points outside the set has a point,
is seen only through its number of points, which the own tiling counts: the
reduced tiling leaves it out. Cells of the set in one row are seen as one if
their columns, and the columns between them, have no cell outside the set, no
other cell of the set that the rest sees lies between them, and the
obstructions and requirements with points outside the set treat a point in any
of them alike; likewise in a column. The reduced tiling keeps the first of such
a group, with all the group's points. Each group is tracked once, in both
children, and the count is the Hadamard product of the children in the numbers
of points of the groups, at 1, and the product in the number of points of the
cells left out:

    parent(n) = sum over w and m of reduced(n - m; w) * own(|w| + m; w),

w the number of points in each group and m in the cells left out. A single cell
is the cell reduction (`tilings.strategies.cell_reduction`). The condition, the
plan, the children and the words of the maps are in `tilings.algorithms.reduction`.
"""

import random
from collections import Counter, defaultdict
from itertools import combinations
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    cast,
)

import sympy

from comb_spec_searcher import Constructor, Strategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.typing import (
    Objects,
    Parameters,
    RelianceProfile,
    SubObjects,
    SubRecs,
    SubSamplers,
    SubTerms,
    Terms,
)
from tilings import GriddedPerm, Tiling
from tilings.algorithms.reduction import (
    Cell,
    ReductionPlan,
    combine_gridded_perms,
    is_reducible,
    is_rigid,
    own_is_tracked,
    reduce_gridded_perm,
    reduction_children,
    reduction_plan,
)
from tilings.assumptions import TrackingAssumption

__all__ = ("ReductionConstructor", "ReductionStrategy", "ReductionFactory")

REGIONS = ("cell", "row", "column", "line", "cut", "any")


class SampleChoice(NamedTuple):
    """The sizes and the parameters of the reduced tiling and of the own tiling for
    one choice of the numbers of points in the groups and the cells left out."""

    reduced_size: int
    reduced_parameters: Dict[str, int]
    own_size: int
    own_parameters: Dict[str, int]


def _bounded_compositions(bound: int, parts: int) -> Iterator[Tuple[int, ...]]:
    """The tuples of parts numbers, each at least 0, of sum at most bound."""
    if parts == 0:
        yield ()
        return
    for first in range(bound + 1):
        for rest in _bounded_compositions(bound - first, parts - 1):
            yield (first,) + rest


class ReductionConstructor(Constructor[Tiling, GriddedPerm]):
    """The constructor of a reduction: the Hadamard product of the reduced tiling
    and the tiling of the cells' own obstructions in the variables that count the
    points in the groups of cells the rest of the tiling sees as one, at 1, and the
    product in the size of the cells the reduced tiling leaves out.

        parent(n; p) = sum over w and m of reduced(n - m; p, w) * own(|w| + m; w)

    parent_to_reduced is the strategy's map of the parent's parameters to the
    reduced tiling's (its extra parameters for the reduced tiling).
    """

    def __init__(
        self,
        parent: Tiling,
        children: Tuple[Tiling, ...],
        cells: Iterable[Cell],
        plan: ReductionPlan,
        parent_to_reduced: Optional[Dict[str, str]] = None,
    ):
        reduced_tiling, own_tiling = children
        self.cells = tuple(sorted(set(cells)))
        self.groups, left_out = plan
        self.leaves_out = bool(left_out)
        if parent_to_reduced is None:
            parent_to_reduced = {
                parent_parameter: self._parameter_of(reduced_tiling, assumption)
                for parent_parameter, assumption in zip(
                    parent.extra_parameters, parent.assumptions
                )
            }
        self.parent_to_reduced = parent_to_reduced
        self.reduced_group_parameters = tuple(
            self._parameter_of(
                reduced_tiling, TrackingAssumption.from_cells([group[0]])
            )
            for group in self.groups
        )
        self.reduced_group_indices = self._indices(
            reduced_tiling, self.reduced_group_parameters
        )
        self.parent_indices = self._indices(
            reduced_tiling,
            [self.parent_to_reduced[name] for name in parent.extra_parameters],
        )
        self.own_group_parameters: Optional[Tuple[str, ...]] = None
        self.own_group_indices: Tuple[int, ...] = ()
        if own_is_tracked(self.groups, left_out):
            self.own_group_parameters = tuple(
                self._parameter_of(own_tiling, TrackingAssumption.from_cells(group))
                for group in self.groups
            )
            self.own_group_indices = self._indices(
                own_tiling, self.own_group_parameters
            )

    @staticmethod
    def _parameter_of(child: Tiling, assumption: TrackingAssumption) -> str:
        """The child's parameter for an assumption in the parent's cells."""
        return child.get_assumption_parameter(
            child.forward_map.map_assumption(assumption)
        )

    @staticmethod
    def _indices(child: Tiling, parameters: Iterable[str]) -> Tuple[int, ...]:
        """The places of the parameters in the child's extra parameters."""
        return tuple(child.extra_parameters.index(name) for name in parameters)

    def _left_out_sizes(self, n: int) -> range:
        """The numbers of points the cells left out may have."""
        return range(n + 1) if self.leaves_out else range(1)

    def _group_sizes(self, own_parameters: Parameters, size: int) -> Tuple[int, ...]:
        """The number of points in each group, from a parameter of the own tiling."""
        if self.own_group_parameters is None:
            return (size,)
        return tuple(own_parameters[index] for index in self.own_group_indices)

    def _own_parameters(self, group_sizes: Tuple[int, ...]) -> Dict[str, int]:
        if self.own_group_parameters is None:
            return {}
        return dict(zip(self.own_group_parameters, group_sizes))

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        raise NotImplementedError(
            "A Hadamard product has no equation in the generating functions"
        )

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def _split(self, reduced_parameters: Parameters) -> Tuple[Parameters, Parameters]:
        """The number of points in each group, and the parent's parameters, from a
        parameter of the reduced tiling."""
        return (
            tuple(reduced_parameters[index] for index in self.reduced_group_indices),
            tuple(reduced_parameters[index] for index in self.parent_indices),
        )

    def _pairs(
        self,
        n: int,
        reduced_by_parameters: Callable[[int], Dict[Parameters, Any]],
        own_by_group_sizes: Callable[[int], Dict[Tuple[int, ...], Any]],
    ) -> Iterator[Tuple[Parameters, Any, Any]]:
        """For each number of points in the cells left out, and each parameter of
        the reduced tiling at the size that leaves, the parent's parameters, the
        reduced tiling's value and the own tiling's value with as many points in
        each group (counts, or lists of objects)."""
        own_by_size: Dict[int, Dict[Tuple[int, ...], Any]] = {}
        for left_out_size in self._left_out_sizes(n):
            reduced_values = reduced_by_parameters(n - left_out_size)
            for reduced_parameters, reduced_value in reduced_values.items():
                group_sizes, parent_parameters = self._split(reduced_parameters)
                own_size = sum(group_sizes) + left_out_size
                if own_size not in own_by_size:
                    own_by_size[own_size] = own_by_group_sizes(own_size)
                own_value = own_by_size[own_size].get(group_sizes)
                if reduced_value and own_value:
                    yield parent_parameters, reduced_value, own_value

    def _own_counts(self, own_terms: Callable[[int], Terms], size: int) -> Counter:
        """The number of objects of the own tiling of the size with each number of
        points in the groups."""
        own_counts: Counter = Counter()
        for own_parameters, own_count in own_terms(size).items():
            own_counts[self._group_sizes(own_parameters, size)] += own_count
        return own_counts

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        reduced_terms, own_terms = subterms
        terms: Terms = Counter()
        for parent_parameters, reduced_count, own_count in self._pairs(
            n, reduced_terms, lambda size: self._own_counts(own_terms, size)
        ):
            terms[parent_parameters] += reduced_count * own_count
        return terms

    def _own_objects(
        self, own_objects: Callable[[int], Objects], size: int
    ) -> DefaultDict[Parameters, List[Optional[GriddedPerm]]]:
        """The objects of the own tiling of the size, by the number of points in
        each group."""
        own_lists: DefaultDict[Parameters, List[Optional[GriddedPerm]]] = defaultdict(
            list
        )
        for own_parameters, own_list in own_objects(size).items():
            own_lists[self._group_sizes(own_parameters, size)].extend(own_list)
        return own_lists

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[Tuple[Parameters, Tuple[List[Optional[GriddedPerm]], ...]]]:
        reduced_objects, own_objects = subobjs
        for parent_parameters, reduced_list, own_list in self._pairs(
            n, reduced_objects, lambda size: self._own_objects(own_objects, size)
        ):
            yield parent_parameters, (reduced_list, own_list)

    def _sample_choices(
        self, n: int, parent_parameters: Dict[str, int]
    ) -> Iterator[SampleChoice]:
        """For each number of points in the cells left out and in the groups that
        the parent's parameters allow, the sizes and the parameters of the two
        children."""
        fixed_parameters = {
            self.parent_to_reduced[name]: value
            for name, value in parent_parameters.items()
        }
        fixed_sizes = [
            fixed_parameters.get(name) for name in self.reduced_group_parameters
        ]
        free = [index for index, size in enumerate(fixed_sizes) if size is None]
        fixed_total = sum(size for size in fixed_sizes if size is not None)
        for left_out_size in self._left_out_sizes(n):
            reduced_size = n - left_out_size
            if fixed_total > reduced_size:
                continue
            for free_sizes in _bounded_compositions(
                reduced_size - fixed_total, len(free)
            ):
                group_sizes = list(fixed_sizes)
                for index, size in zip(free, free_sizes):
                    group_sizes[index] = size
                reduced_parameters = dict(fixed_parameters)
                reduced_parameters.update(
                    zip(self.reduced_group_parameters, cast(List[int], group_sizes))
                )
                yield SampleChoice(
                    reduced_size,
                    reduced_parameters,
                    sum(cast(List[int], group_sizes)) + left_out_size,
                    self._own_parameters(tuple(cast(List[int], group_sizes))),
                )

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        random_choice = random.randint(1, parent_count)
        total = 0
        for choice in self._sample_choices(n, parameters):
            total += self._choice_count(subrecs, choice)
            if random_choice <= total:
                return (
                    subsamplers[0](n=choice.reduced_size, **choice.reduced_parameters),
                    subsamplers[1](n=choice.own_size, **choice.own_parameters),
                )
        raise RuntimeError("Function did not return")

    @staticmethod
    def _choice_count(subrecs: SubRecs, choice: SampleChoice) -> int:
        """The number of pairs of objects of the two children for the choice."""
        reduced_count = subrecs[0](n=choice.reduced_size, **choice.reduced_parameters)
        if not reduced_count:
            return 0
        return reduced_count * subrecs[1](n=choice.own_size, **choice.own_parameters)

    def equiv(
        self, other: "Constructor", data: Optional[object] = None
    ) -> Tuple[bool, Optional[object]]:
        """Two reductions' constructors are taken as equivalent only when they pair
        their children the same way: as many groups, cells left out or not, the
        own tiling tracked or not, and the groups' and the parent's parameters at
        the same places of the children's parameters. This errs on the side of
        not equivalent."""
        return (
            isinstance(other, ReductionConstructor)
            and len(self.groups) == len(other.groups)
            and self.leaves_out == other.leaves_out
            and (self.own_group_parameters is None)
            == (other.own_group_parameters is None)
            and self.reduced_group_indices == other.reduced_group_indices
            and self.parent_indices == other.parent_indices
            and self.own_group_indices == other.own_group_indices,
            None,
        )

    @staticmethod
    def get_eq_symbol() -> str:
        return ReductionStrategy.get_eq_symbol()

    @staticmethod
    def get_op_symbol() -> str:
        return ReductionStrategy.get_op_symbol()

    def __str__(self) -> str:
        return "Hadamard product in the reduced cells"


class ReductionStrategy(Strategy[Tiling, GriddedPerm]):
    """A strategy that makes a set of cells increasing (or decreasing), the points
    of its cells in each row and each column in that order, and counts the cells'
    own tiling beside it. The reduced tiling keeps only the cells of the set that
    the rest of the tiling sees, one for each group it sees as one."""

    def __init__(
        self,
        cells: Iterable[Cell],
        increasing: bool,
        tracked: bool = True,
    ):
        self.cells: Tuple[Cell, ...] = tuple(
            sorted(set(cast(Cell, tuple(cell)) for cell in cells))
        )
        self.increasing = increasing
        self.tracked = tracked
        super().__init__()

    def can_be_equivalent(self) -> bool:
        return False

    def is_two_way(self, comb_class: Tiling) -> bool:
        return False

    def is_reversible(self, comb_class: Tiling) -> bool:
        return False

    def shifts(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[int, ...]:
        return (0, 0)

    def plan(self, comb_class: Tiling) -> ReductionPlan:
        """The groups of the set the reduced tiling keeps a cell for, and the cells
        it leaves out."""
        return reduction_plan(comb_class, self.cells)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, Tiling]:
        if not is_reducible(comb_class, self.cells, self.increasing):
            direction = "increasing" if self.increasing else "decreasing"
            raise StrategyDoesNotApply(
                f"The cells {self.cells} are not reducible to {direction}"
            )
        return reduction_children(comb_class, self.cells, self.increasing, self.tracked)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> ReductionConstructor:
        if not self.tracked:
            raise NotImplementedError("The reduction strategy was not tracked")
        if children is None:
            children = self.decomposition_function(comb_class)
        return ReductionConstructor(
            comb_class,
            children,
            self.cells,
            self.plan(comb_class),
            self.extra_parameters(comb_class, children)[0],
        )

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        raise NotImplementedError

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        reduced_tiling = children[0]
        return (
            {
                parent_parameter: reduced_tiling.get_assumption_parameter(
                    reduced_tiling.forward_map.map_assumption(assumption)
                )
                for parent_parameter, assumption in zip(
                    comb_class.extra_parameters, comb_class.assumptions
                )
            },
            {},
        )

    def formal_step(self) -> str:
        cells = ", ".join(str(cell) for cell in self.cells)
        direction = "increasing" if self.increasing else "decreasing"
        noun = "cell" if len(self.cells) == 1 else "cells"
        return f"reducing {noun} {cells} to {direction}"

    def reduce_gridded_perm(
        self, comb_class: Tiling, gridded_perm: GriddedPerm
    ) -> GriddedPerm:
        """The gridded permutation of the reduced tiling for one of the tiling, in
        the tiling's cells (see tilings.algorithms.reduction)."""
        return reduce_gridded_perm(
            comb_class, self.cells, gridded_perm, self.increasing
        )

    def combine_gridded_perms(
        self,
        comb_class: Tiling,
        reduced_gridded_perm: GriddedPerm,
        own_gridded_perm: GriddedPerm,
    ) -> GriddedPerm:
        """The gridded permutation of the tiling for one of the reduced tiling and
        one of the own tiling, both in the tiling's cells (see
        tilings.algorithms.reduction)."""
        return combine_gridded_perms(
            comb_class, self.cells, reduced_gridded_perm, own_gridded_perm
        )

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        if children is None:
            children = self.decomposition_function(comb_class)
        reduced_gridded_perm, own_gridded_perm = objs
        assert reduced_gridded_perm is not None and own_gridded_perm is not None
        yield self.combine_gridded_perms(
            comb_class,
            children[0].backward_map.map_gp(reduced_gridded_perm),
            children[1].backward_map.map_gp(own_gridded_perm),
        )

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        return (
            children[0].forward_map.map_gp(self.reduce_gridded_perm(comb_class, obj)),
            children[1].forward_map.map_gp(obj.get_gridded_perm_in_cells(self.cells)),
        )

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d.pop("ignore_parent")
        d.pop("inferrable")
        d.pop("possibly_empty")
        d.pop("workable")
        d["cells"] = self.cells
        d["increasing"] = self.increasing
        d["tracked"] = self.tracked
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ReductionStrategy":
        cells = [cast(Cell, tuple(cell)) for cell in d.pop("cells")]
        increasing = d.pop("increasing")
        tracked = d.pop("tracked")
        assert not d
        return cls(cells, increasing, tracked)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(cells={self.cells!r}, "
            f"increasing={self.increasing!r}, tracked={self.tracked!r})"
        )

    @staticmethod
    def get_eq_symbol() -> str:
        return "↣"

    @staticmethod
    def get_op_symbol() -> str:
        return "⊙"


class ReductionFactory(StrategyFactory[Tiling]):
    """The reductions of the sets of cells of a region, in each direction the set
    is reducible in.

    The region says which sets are tried:

    - "cell": every single cell (the cell reduction);
    - "row": the active cells of every row;
    - "column": the active cells of every column;
    - "line": every set of cells in one row or in one column, so single cells and
      whole rows and columns among them;
    - "cut": the active cells on one side of a line between two adjacent columns
      or two adjacent rows: left of it, right of it, below it or above it, as the
      cells left of a placed point, which a threshold reduction reduces; at most
      twice the number of columns and rows;
    - "any": every set of cells.

    With max_cells, the sets of "cut" and "any" have at most that many cells. The
    region "any" tries every set of active cells, whose number grows exponentially
    with the number of active cells; give it a max_cells, or use "cut" or "line".

    A set is reduced if it is reducible, it is not all of the active cells, it is
    not rigid (every cell monotone, and the points of any two of its cells in a
    row or a column in a fixed order: reducing it would change nothing, or reverse
    it), it is not a single finite cell, and the rest of the tiling sees one of its
    cells (if it sees none, the set is a factor).

    With tracked=False the strategies track nothing and have no constructor: for
    an untracked search, whose specification a tracked search then counts.
    """

    def __init__(
        self,
        tracked: bool = True,
        region: str = "cell",
        max_cells: Optional[int] = None,
    ):
        if region not in REGIONS:
            raise ValueError(f"The region must be one of {REGIONS}, not {region!r}")
        self.tracked = tracked
        self.region = region
        self.max_cells = max_cells
        super().__init__()

    def candidate_sets(self, tiling: Tiling) -> Iterator[Tuple[Cell, ...]]:
        """The sets of active cells of the region, each once."""
        active_cells = sorted(tiling.active_cells)
        seen = set()
        for cells in self._region_sets(tiling, active_cells):
            if cells and cells not in seen:
                seen.add(cells)
                yield cells

    def _region_sets(
        self, tiling: Tiling, active_cells: List[Cell]
    ) -> Iterator[Tuple[Cell, ...]]:
        if self.region == "cell":
            return ((cell,) for cell in active_cells)
        if self.region in ("row", "column"):
            return (tuple(line) for line in self._lines(tiling, active_cells))
        if self.region == "line":
            return (
                subset
                for line in self._lines(tiling, active_cells)
                for size in range(1, len(line) + 1)
                for subset in combinations(line, size)
            )
        if self.region == "cut":
            return (
                side
                for side in self.cuts(tiling, active_cells)
                if self.max_cells is None or len(side) <= self.max_cells
            )
        largest = len(active_cells)
        if self.max_cells is not None:
            largest = min(largest, self.max_cells)
        return (
            subset
            for size in range(1, largest + 1)
            for subset in combinations(active_cells, size)
        )

    def _lines(self, tiling: Tiling, active_cells: List[Cell]) -> List[List[Cell]]:
        """The active cells of each row (for "row" and "line") and of each column
        (for "column" and "line")."""
        width, height = tiling.dimensions
        lines: List[List[Cell]] = []
        if self.region in ("row", "line"):
            lines.extend(
                [cell for cell in active_cells if cell[1] == row]
                for row in range(height)
            )
        if self.region in ("column", "line"):
            lines.extend(
                [cell for cell in active_cells if cell[0] == column]
                for column in range(width)
            )
        return lines

    @staticmethod
    def cuts(tiling: Tiling, active_cells: List[Cell]) -> Iterator[Tuple[Cell, ...]]:
        """For each line between two adjacent columns, the active cells left of it
        and those right of it; likewise below and above each line between two
        adjacent rows."""
        width, height = tiling.dimensions
        for column in range(1, width):
            yield tuple(cell for cell in active_cells if cell[0] < column)
            yield tuple(cell for cell in active_cells if cell[0] >= column)
        for row in range(1, height):
            yield tuple(cell for cell in active_cells if cell[1] < row)
            yield tuple(cell for cell in active_cells if cell[1] >= row)

    @staticmethod
    def is_finite_cell(tiling: Tiling, cell: Cell) -> bool:
        cell_basis = tiling.cell_basis()[cell][0]
        return any(pattern.is_increasing() for pattern in cell_basis) and any(
            pattern.is_decreasing() for pattern in cell_basis
        )

    def __call__(self, comb_class: Tiling) -> Iterator[ReductionStrategy]:
        active_cells = comb_class.active_cells
        for cells in self.candidate_sets(comb_class):
            if len(cells) == len(active_cells):
                continue
            if len(cells) == 1 and self.is_finite_cell(comb_class, cells[0]):
                continue
            directions = [
                increasing
                for increasing in (True, False)
                if is_reducible(comb_class, cells, increasing)
            ]
            if not directions or is_rigid(comb_class, cells):
                continue
            if not reduction_plan(comb_class, cells).groups:
                continue
            for increasing in directions:
                yield self.strategy(cells, increasing)

    def strategy(self, cells: Tuple[Cell, ...], increasing: bool) -> ReductionStrategy:
        return ReductionStrategy(cells, increasing, self.tracked)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(tracked={self.tracked!r}, "
            f"region={self.region!r}, max_cells={self.max_cells!r})"
        )

    def __str__(self) -> str:
        tracked = "tracked " if self.tracked else ""
        if self.region == "cut":
            bound = (
                "" if self.max_cells is None else f" of at most {self.max_cells} cells"
            )
            return (
                f"{tracked}reduction factory of the cells on one side of a line{bound}"
            )
        if self.region != "any":
            return f"{tracked}{self.region} reduction factory"
        if self.max_cells is None:
            return f"{tracked}reduction factory of any set of cells"
        return f"{tracked}reduction factory of sets of at most {self.max_cells} cells"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["tracked"] = self.tracked
        d["region"] = self.region
        d["max_cells"] = self.max_cells
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ReductionFactory":
        tracked = d.pop("tracked", True)
        region = d.pop("region", "cell")
        max_cells = d.pop("max_cells", None)
        assert not d
        return cls(tracked, region, max_cells)

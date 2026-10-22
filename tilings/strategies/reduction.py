"""The reduction strategy, which makes a set of cells monotone.

A set of active cells of a tiling is reducible if every obstruction with points
both in the set and outside it has exactly one point in the set, in the cell c
say, and

- it does not have points both in another cell of the row of c and in another
  cell of the column of c;
- if it has a point in another cell of the column of c, then c is the only cell
  of the set in its column, and if it has a point in another cell of the row of
  c, then c is the only cell of the set in its row;

and every requirement list lies in the set, or each of its gridded permutations
has no point in the set or one point in it that the obstructions may have.

A gridded permutation is the same as, for each column, the word of the cells of
its points from left to right, for each row, the word of the cells of its points
from bottom to top, and the permutation in each cell, chosen independently. The
share of a set of cells in these is the order of its points among themselves in
each column and in each row, and the permutation in each of its cells. An
obstruction with one point in a reducible set sees that point only through its
cell and its place among the other points of its column or of its row, and
sorting the share of the set into a canonical one keeps both. So sorting is a
bijection from the gridded permutations of the tiling to the pairs of a gridded
permutation of the reduced tiling, in which the share of the set is canonical,
and one of the tiling of the set's own obstructions and requirements, with the
same number of points in each cell of the set. In the canonical share every cell
of the set is increasing (or decreasing), and so are the points of the cells of
the set in each row and in each column.

The count is the Hadamard product of the two children in the variables that
count the points in the cells of the set, at 1:

    parent(n) = sum over v of reduced(n; v) * own(v),

the sum over the number of points v in each cell of the set. A single cell is the
cell reduction (`tilings.strategies.cell_reduction`).
"""

import random
from collections import Counter, defaultdict
from itertools import combinations, product
from typing import (
    Callable,
    DefaultDict,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
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
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.assumptions import ComponentAssumption, TrackingAssumption

__all__ = ("ReductionConstructor", "ReductionStrategy", "ReductionFactory")

Cell = Tuple[int, int]
REGIONS = ("cell", "row", "column", "line", "any")


def _crossing_is_allowed(gp: GriddedPerm, cells: FrozenSet[Cell]) -> bool:
    """Return True if the gridded permutation, which has points in the cells and
    outside them, has exactly one point in them, and touches either no other cell
    of that point's row or no other cell of its column, and touches the other
    cells of the column (row) only if that point's cell is the only one of the
    cells in its column (row)."""
    cells_inside = [cell for cell in gp.pos if cell in cells]
    if len(cells_inside) != 1:
        return False
    column, row = cells_inside[0]
    cells_outside = [cell for cell in gp.pos if cell not in cells]
    touches_column = any(cell[0] == column for cell in cells_outside)
    touches_row = any(cell[1] == row for cell in cells_outside)
    if touches_column and touches_row:
        return False
    if touches_column and any(cell[0] == column and cell[1] != row for cell in cells):
        return False
    if touches_row and any(cell[1] == row and cell[0] != column for cell in cells):
        return False
    return True


def is_reducible(tiling: Tiling, cells: Iterable[Cell]) -> bool:
    """Return True if the set of cells is reducible on the tiling."""
    cell_set = frozenset(cells)
    if not cell_set or not cell_set <= tiling.active_cells:
        return False
    if any(
        isinstance(assumption, ComponentAssumption)
        and any(gp.pos[0] in cell_set for gp in assumption.gps)
        for assumption in tiling.assumptions
    ):
        return False
    # the tiling of the set's own obstructions must have every cell of the set, so
    # each cell needs an obstruction of its own (an unrestricted cell has none)
    cells_with_own_obstructions = {
        cell
        for obstruction in tiling.obstructions
        if all(cell in cell_set for cell in obstruction.pos)
        for cell in obstruction.pos
    }
    if not cell_set <= cells_with_own_obstructions:
        return False
    for obstruction in tiling.obstructions:
        points_inside = sum(1 for cell in obstruction.pos if cell in cell_set)
        if 0 < points_inside < len(obstruction) and not _crossing_is_allowed(
            obstruction, cell_set
        ):
            return False
    for requirement in tiling.requirements:
        if all(cell in cell_set for gp in requirement for cell in gp.pos):
            continue
        for gp in requirement:
            if any(cell in cell_set for cell in gp.pos) and not _crossing_is_allowed(
                gp, cell_set
            ):
                return False
    return True


def is_rigid(tiling: Tiling, cells: Iterable[Cell]) -> bool:
    """Return True if the share of the cells is the same in every gridded
    permutation with the same number of points in each cell: every cell is
    monotone, and the points of any two of the cells in a row or a column are in
    a fixed order. Reducing such cells changes nothing, or reverses them."""
    cell_list = sorted(set(cells))
    obstructions = tiling.obstructions

    def is_forbidden(gp: GriddedPerm) -> bool:
        return gp.contains(*obstructions)

    for first_cell, second_cell in product(cell_list, repeat=2):
        if first_cell > second_cell:
            continue
        if first_cell == second_cell or first_cell[1] == second_cell[1]:
            # a cell, or two cells of a row, read from left to right
            if not (
                is_forbidden(GriddedPerm(Perm((0, 1)), (first_cell, second_cell)))
                or is_forbidden(GriddedPerm(Perm((1, 0)), (first_cell, second_cell)))
            ):
                return False
        elif first_cell[0] == second_cell[0]:
            # two cells of a column, the lower one first
            if not (
                is_forbidden(GriddedPerm(Perm((0, 1)), (first_cell, second_cell)))
                or is_forbidden(GriddedPerm(Perm((1, 0)), (second_cell, first_cell)))
            ):
                return False
    return True


def monotone_obstructions(cells: Iterable[Cell], increasing: bool) -> List[GriddedPerm]:
    """Return the gridded 21s (increasing) or 12s (decreasing) with both points in
    cells of the set that share a row or a column, which make the share of the set
    canonical."""
    cell_list = sorted(set(cells))
    patt = Perm((1, 0)) if increasing else Perm((0, 1))
    obstructions = []
    for left_cell, right_cell in product(cell_list, repeat=2):
        if left_cell[0] != right_cell[0] and left_cell[1] != right_cell[1]:
            continue
        if left_cell[0] > right_cell[0]:
            continue
        if increasing and left_cell[1] < right_cell[1]:
            continue
        if not increasing and left_cell[1] > right_cell[1]:
            continue
        obstructions.append(GriddedPerm(patt, (left_cell, right_cell)))
    return obstructions


def compression(cells: Iterable[Cell]) -> Tuple[Dict[Cell, Cell], Dict[Cell, Cell]]:
    """Return the maps from the cells of the set to the cells of its own tiling,
    which keeps the columns and rows of the set only, and back."""
    cell_list = sorted(set(cells))
    column_index = {
        column: index
        for index, column in enumerate(sorted({cell[0] for cell in cell_list}))
    }
    row_index = {
        row: index for index, row in enumerate(sorted({cell[1] for cell in cell_list}))
    }
    forward = {cell: (column_index[cell[0]], row_index[cell[1]]) for cell in cell_list}
    backward = {own_cell: cell for cell, own_cell in forward.items()}
    return forward, backward


def reduction_children(
    tiling: Tiling, cells: Iterable[Cell], increasing: bool, tracked: bool = True
) -> Tuple[Tiling, Tiling]:
    """Return the reduced tiling, with the cells tracked if tracked, and the
    tiling of the cells' own obstructions and requirements, with every cell
    tracked if there are two or more."""
    cell_set = frozenset(cells)

    def lies_in_cells(gps: Iterable[GriddedPerm]) -> bool:
        return all(cell in cell_set for gp in gps for cell in gp.pos)

    cell_assumptions = [
        TrackingAssumption.from_cells([cell]) for cell in sorted(cell_set)
    ]
    reduced_tiling = Tiling(
        [ob for ob in tiling.obstructions if not lies_in_cells([ob])]
        + monotone_obstructions(cell_set, increasing),
        [req for req in tiling.requirements if not lies_in_cells(req)],
        list(tiling.assumptions) + (cell_assumptions if tracked else []),
    )
    width, height = tiling.dimensions
    other_cells_emptied = [
        GriddedPerm.point_perm((column, row))
        for column in range(width)
        for row in range(height)
        if (column, row) not in cell_set
    ]
    own_tiling = Tiling(
        [ob for ob in tiling.obstructions if lies_in_cells([ob])] + other_cells_emptied,
        [req for req in tiling.requirements if lies_in_cells(req)],
        cell_assumptions if len(cell_set) > 1 else [],
    )
    return reduced_tiling, own_tiling


def _canonical_words(
    points_in_cell: Counter, increasing: bool
) -> Tuple[Dict[int, List[Cell]], Dict[int, List[Cell]]]:
    """The canonical words of the cells: for each column the cells of its points
    from left to right, and for each row from bottom to top."""
    column_words: Dict[int, List[Cell]] = {}
    for column in {cell[0] for cell in points_in_cell}:
        cells_in_column = sorted(
            (cell for cell in points_in_cell if cell[0] == column),
            key=lambda cell: cell[1],
            reverse=not increasing,
        )
        column_words[column] = [
            cell for cell in cells_in_column for _ in range(points_in_cell[cell])
        ]
    row_words: Dict[int, List[Cell]] = {}
    for row in {cell[1] for cell in points_in_cell}:
        cells_in_row = sorted(
            (cell for cell in points_in_cell if cell[1] == row),
            key=lambda cell: cell[0],
            reverse=not increasing,
        )
        row_words[row] = [
            cell for cell in cells_in_row for _ in range(points_in_cell[cell])
        ]
    return column_words, row_words


def _pattern_words(
    pattern: GriddedPerm,
) -> Tuple[Dict[int, List[Cell]], Dict[int, List[Cell]]]:
    """The words of the pattern: for each column the cells of its points from
    left to right, and for each row from bottom to top."""
    column_words: DefaultDict[int, List[Cell]] = defaultdict(list)
    for cell in pattern.pos:
        column_words[cell[0]].append(cell)
    row_words: DefaultDict[int, List[Cell]] = defaultdict(list)
    for index in sorted(range(len(pattern)), key=lambda index: pattern.patt[index]):
        row_words[pattern.pos[index][1]].append(pattern.pos[index])
    return column_words, row_words


def _cell_ranks(
    points_in_cell: Counter, increasing: bool, pattern: Optional[GriddedPerm]
) -> Dict[Cell, List[int]]:
    """For each cell, the ranks of the values of its points, from left to right."""
    if pattern is None:
        return {
            cell: list(range(size)) if increasing else list(range(size - 1, -1, -1))
            for cell, size in points_in_cell.items()
        }
    ranks = {}
    for cell in points_in_cell:
        pattern_values = [
            value for value, other in zip(pattern.patt, pattern.pos) if other == cell
        ]
        sorted_values = sorted(pattern_values)
        ranks[cell] = [sorted_values.index(value) for value in pattern_values]
    return ranks


def _deal_slots(
    gp: GriddedPerm,
    indices_in_cells: List[int],
    column_words: Dict[int, List[Cell]],
    row_words: Dict[int, List[Cell]],
) -> Tuple[DefaultDict[Cell, List[int]], DefaultDict[Cell, List[int]]]:
    """The positions and values that the points of each cell get: the positions
    of the cells' points in each column dealt out in the order of its word, and
    the values of their points in each row."""
    positions: DefaultDict[Cell, List[int]] = defaultdict(list)
    for column, word in column_words.items():
        slots = [index for index in indices_in_cells if gp.pos[index][0] == column]
        for slot, cell in zip(slots, word):
            positions[cell].append(slot)
    values: DefaultDict[Cell, List[int]] = defaultdict(list)
    for row, word in row_words.items():
        slots = sorted(
            gp.patt[index] for index in indices_in_cells if gp.pos[index][1] == row
        )
        for slot, cell in zip(slots, word):
            values[cell].append(slot)
    return positions, values


def _assemble(
    gp: GriddedPerm,
    positions: DefaultDict[Cell, List[int]],
    values: DefaultDict[Cell, List[int]],
    ranks: Dict[Cell, List[int]],
) -> GriddedPerm:
    """The gridded permutation with each cell's points at its positions, with its
    values in the order of its ranks."""
    new_values, new_cells = list(gp.patt), list(gp.pos)
    for cell, cell_ranks in ranks.items():
        cell_values = sorted(values[cell])
        for position, rank in zip(sorted(positions[cell]), cell_ranks):
            new_values[position] = cell_values[rank]
            new_cells[position] = cell
    return GriddedPerm(Perm(new_values), tuple(new_cells))


def resort(
    gp: GriddedPerm,
    cells: Iterable[Cell],
    increasing: bool,
    pattern: Optional[GriddedPerm] = None,
) -> GriddedPerm:
    """Return the gridded permutation with the share of the cells made canonical,
    or, if pattern is given, made that of pattern, a gridded permutation in the
    cells with as many points in each of them. Every column keeps the positions
    of the points of the cells in it, and every row their values."""
    cell_set = frozenset(cells)
    indices_in_cells = [index for index, cell in enumerate(gp.pos) if cell in cell_set]
    points_in_cell = Counter(gp.pos[index] for index in indices_in_cells)
    if pattern is None:
        column_words, row_words = _canonical_words(points_in_cell, increasing)
    else:
        if Counter(pattern.pos) != points_in_cell:
            raise ValueError("the pattern has a different number of points in a cell")
        column_words, row_words = _pattern_words(pattern)
    positions, values = _deal_slots(gp, indices_in_cells, column_words, row_words)
    return _assemble(
        gp, positions, values, _cell_ranks(points_in_cell, increasing, pattern)
    )


class ReductionConstructor(Constructor[Tiling, GriddedPerm]):
    """The constructor of a reduction: the Hadamard product of the reduced tiling
    and the tiling of the cells' own obstructions in the variables that count the
    points in the cells, at 1.

        parent(n; p) = sum over v of reduced(n; p, v) * own(|v|; v)
    """

    def __init__(
        self,
        parent: Tiling,
        children: Tuple[Tiling, ...],
        cells: Iterable[Cell],
    ):
        reduced_tiling, own_tiling = children
        self.cells = tuple(sorted(set(cells)))
        reduced_parameters = reduced_tiling.extra_parameters

        def reduced_parameter(assumption: TrackingAssumption) -> str:
            return reduced_tiling.get_assumption_parameter(
                reduced_tiling.forward_map.map_assumption(assumption)
            )

        self.reduced_cell_parameters = tuple(
            reduced_parameter(TrackingAssumption.from_cells([cell]))
            for cell in self.cells
        )
        self.reduced_cell_indices = tuple(
            reduced_parameters.index(name) for name in self.reduced_cell_parameters
        )
        self.parent_to_reduced = {
            parent_parameter: reduced_parameter(assumption)
            for parent_parameter, assumption in zip(
                parent.extra_parameters, parent.assumptions
            )
        }
        self.parent_indices = tuple(
            reduced_parameters.index(self.parent_to_reduced[parent_parameter])
            for parent_parameter in parent.extra_parameters
        )
        if len(self.cells) == 1:
            self.own_cell_parameters: Optional[Tuple[str, ...]] = None
            self.own_cell_indices: Tuple[int, ...] = ()
        else:
            forward, _ = compression(self.cells)
            self.own_cell_parameters = tuple(
                own_tiling.get_assumption_parameter(
                    TrackingAssumption.from_cells([forward[cell]])
                )
                for cell in self.cells
            )
            self.own_cell_indices = tuple(
                own_tiling.extra_parameters.index(name)
                for name in self.own_cell_parameters
            )

    def _cell_sizes(self, own_parameters: Parameters, size: int) -> Tuple[int, ...]:
        """The number of points in each cell, from a parameter of the own tiling."""
        if self.own_cell_parameters is None:
            return (size,)
        return tuple(own_parameters[index] for index in self.own_cell_indices)

    def _own_parameters(self, cell_sizes: Tuple[int, ...]) -> Dict[str, int]:
        if self.own_cell_parameters is None:
            return {}
        return dict(zip(self.own_cell_parameters, cell_sizes))

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        raise NotImplementedError(
            "A Hadamard product has no equation in the generating functions"
        )

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def _split(self, reduced_parameters: Parameters) -> Tuple[Parameters, Parameters]:
        """The number of points in each cell, and the parent's parameters, from a
        parameter of the reduced tiling."""
        return (
            tuple(reduced_parameters[index] for index in self.reduced_cell_indices),
            tuple(reduced_parameters[index] for index in self.parent_indices),
        )

    def _own_counts(self, own_terms: Callable[[int], Terms], size: int) -> Counter:
        """The number of objects of the own tiling with each number of points in
        the cells, for objects of the size."""
        own_counts: Counter = Counter()
        for own_parameters, own_count in own_terms(size).items():
            own_counts[self._cell_sizes(own_parameters, size)] += own_count
        return own_counts

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        reduced_terms, own_terms = subterms
        own_counts_by_size: Dict[int, Counter] = {}
        terms: Terms = Counter()
        for reduced_parameters, reduced_count in reduced_terms(n).items():
            cell_sizes, parent_parameters = self._split(reduced_parameters)
            size = sum(cell_sizes)
            if size not in own_counts_by_size:
                own_counts_by_size[size] = self._own_counts(own_terms, size)
            own_count = own_counts_by_size[size][cell_sizes]
            if own_count:
                terms[parent_parameters] += reduced_count * own_count
        return terms

    def _own_objects(
        self, own_objects: Callable[[int], Objects], size: int
    ) -> DefaultDict[Parameters, List[Optional[GriddedPerm]]]:
        """The objects of the own tiling of the size, by the number of points in
        each cell."""
        own_lists: DefaultDict[Parameters, List[Optional[GriddedPerm]]] = defaultdict(
            list
        )
        for own_parameters, own_list in own_objects(size).items():
            own_lists[self._cell_sizes(own_parameters, size)].extend(own_list)
        return own_lists

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[Tuple[Parameters, Tuple[List[Optional[GriddedPerm]], ...]]]:
        reduced_objects, own_objects = subobjs
        own_by_size: Dict[int, DefaultDict[Parameters, List[Optional[GriddedPerm]]]]
        own_by_size = {}
        for reduced_parameters, reduced_list in reduced_objects(n).items():
            cell_sizes, parent_parameters = self._split(reduced_parameters)
            size = sum(cell_sizes)
            if size not in own_by_size:
                own_by_size[size] = self._own_objects(own_objects, size)
            own_list = own_by_size[size].get(cell_sizes, [])
            if reduced_list and own_list:
                yield parent_parameters, (reduced_list, own_list)

    def _sample_choices(
        self, n: int, parent_parameters: Dict[str, int]
    ) -> Iterator[Tuple[Dict[str, int], int, Dict[str, int]]]:
        """For each number of points in the cells that the parent's parameters
        allow, the parameters of the reduced tiling, the size and the parameters
        of the own tiling."""
        fixed_parameters = {
            self.parent_to_reduced[name]: value
            for name, value in parent_parameters.items()
        }
        for cell_sizes in product(range(n + 1), repeat=len(self.cells)):
            if sum(cell_sizes) > n:
                continue
            reduced_parameters = dict(fixed_parameters)
            if all(
                reduced_parameters.setdefault(name, cell_size) == cell_size
                for name, cell_size in zip(self.reduced_cell_parameters, cell_sizes)
            ):
                yield reduced_parameters, sum(cell_sizes), self._own_parameters(
                    cell_sizes
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
            total += self._choice_count(subrecs, n, choice)
            if random_choice <= total:
                reduced_parameters, size, own_parameters = choice
                return (
                    subsamplers[0](n=n, **reduced_parameters),
                    subsamplers[1](n=size, **own_parameters),
                )
        raise RuntimeError("Function did not return")

    @staticmethod
    def _choice_count(
        subrecs: SubRecs, n: int, choice: Tuple[Dict[str, int], int, Dict[str, int]]
    ) -> int:
        """The number of pairs of objects for the choice of the reduced tiling's
        parameters, the size and the own tiling's parameters."""
        reduced_parameters, size, own_parameters = choice
        reduced_count = subrecs[0](n=n, **reduced_parameters)
        if not reduced_count:
            return 0
        return reduced_count * subrecs[1](n=size, **own_parameters)

    def equiv(
        self, other: "Constructor", data: Optional[object] = None
    ) -> Tuple[bool, Optional[object]]:
        return (
            isinstance(other, ReductionConstructor)
            and len(self.cells) == len(other.cells)
            and len(self.parent_indices) == len(other.parent_indices),
            None,
        )

    @staticmethod
    def get_eq_symbol() -> str:
        return "↣"

    @staticmethod
    def get_op_symbol() -> str:
        return "⊙"

    def __str__(self) -> str:
        return "Hadamard product in the reduced cells"


class ReductionStrategy(Strategy[Tiling, GriddedPerm]):
    """A strategy that makes a set of cells increasing (or decreasing), the points
    of its cells in each row and each column in that order, and counts the cells'
    own tiling beside it."""

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

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, Tiling]:
        if not is_reducible(comb_class, self.cells):
            raise StrategyDoesNotApply(f"The cells {self.cells} are not reducible")
        return reduction_children(comb_class, self.cells, self.increasing, self.tracked)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> ReductionConstructor:
        if not self.tracked:
            raise NotImplementedError("The reduction strategy was not tracked")
        if children is None:
            children = self.decomposition_function(comb_class)
        return ReductionConstructor(comb_class, children, self.cells)

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

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        if children is None:
            children = self.decomposition_function(comb_class)
        reduced_gp, own_gp = objs
        assert reduced_gp is not None and own_gp is not None
        _, backward = compression(self.cells)
        pattern = GriddedPerm(own_gp.patt, tuple(backward[cell] for cell in own_gp.pos))
        yield resort(
            children[0].backward_map.map_gp(reduced_gp),
            self.cells,
            self.increasing,
            pattern,
        )

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        forward, _ = compression(self.cells)
        own_gp = obj.get_gridded_perm_in_cells(self.cells)
        return (
            children[0].forward_map.map_gp(resort(obj, self.cells, self.increasing)),
            GriddedPerm(own_gp.patt, tuple(forward[cell] for cell in own_gp.pos)),
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
    """The reductions of the sets of cells of a region, in both directions.

    The region says which sets are tried:

    - "cell": every single cell (the cell reduction);
    - "row": the active cells of every row;
    - "column": the active cells of every column;
    - "line": every set of cells in one row or in one column, so single cells and
      whole rows and columns among them;
    - "any": every set of cells, of at most max_cells cells if that is given.

    A set is reduced if it is reducible, it is not all of the active cells, it is
    not rigid (every cell monotone, and the points of any two of its cells in a
    row or a column in a fixed order: reducing it would change nothing, or reverse
    it) and it is not a single finite cell. So the reduced tiling is never larger
    than the tiling, and smaller at some size.
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
        lines: List[List[Cell]] = []
        if self.region in ("row", "line"):
            lines.extend(
                [cell for cell in active_cells if cell[1] == row]
                for row in range(tiling.dimensions[1])
            )
        if self.region in ("column", "line"):
            lines.extend(
                [cell for cell in active_cells if cell[0] == column]
                for column in range(tiling.dimensions[0])
            )
        seen = set()
        if self.region == "cell":
            candidates: Iterable[Tuple[Cell, ...]] = ((cell,) for cell in active_cells)
        elif self.region in ("row", "column"):
            candidates = (tuple(line) for line in lines)
        elif self.region == "line":
            candidates = (
                subset
                for line in lines
                for size in range(1, len(line) + 1)
                for subset in combinations(line, size)
            )
        else:
            largest = len(active_cells)
            if self.max_cells is not None:
                largest = min(largest, self.max_cells)
            candidates = (
                subset
                for size in range(1, largest + 1)
                for subset in combinations(active_cells, size)
            )
        for cells in candidates:
            if cells and cells not in seen:
                seen.add(cells)
                yield cells

    @staticmethod
    def is_finite_cell(tiling: Tiling, cell: Cell) -> bool:
        cell_basis = tiling.cell_basis()[cell][0]
        return any(patt.is_increasing() for patt in cell_basis) and any(
            patt.is_decreasing() for patt in cell_basis
        )

    def __call__(self, comb_class: Tiling) -> Iterator[ReductionStrategy]:
        active_cells = comb_class.active_cells
        for cells in self.candidate_sets(comb_class):
            if len(cells) == len(active_cells):
                continue
            if len(cells) == 1 and self.is_finite_cell(comb_class, cells[0]):
                continue
            if not is_reducible(comb_class, cells) or is_rigid(comb_class, cells):
                continue
            yield from self.strategies(cells)

    def strategies(self, cells: Tuple[Cell, ...]) -> Iterator[ReductionStrategy]:
        yield ReductionStrategy(cells, True, self.tracked)
        yield ReductionStrategy(cells, False, self.tracked)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(tracked={self.tracked!r}, "
            f"region={self.region!r}, max_cells={self.max_cells!r})"
        )

    def __str__(self) -> str:
        tracked = "tracked " if self.tracked else ""
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
        return cls(d.get("tracked", True), d.get("region", "cell"), d.get("max_cells"))

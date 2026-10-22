# pylint: disable=too-many-lines
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
is the cell reduction (`tilings.strategies.cell_reduction`).
"""

import random
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, product
from operator import itemgetter
from typing import (
    Callable,
    DefaultDict,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Set,
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
Groups = Tuple[Tuple[Cell, ...], ...]
Plan = Tuple[Groups, Tuple[Cell, ...]]
Words = Dict[int, List[Cell]]
REGIONS = ("cell", "row", "column", "line", "cut", "any")


def _lies_in(gps: Iterable[GriddedPerm], cells: FrozenSet[Cell]) -> bool:
    """Return True if every point of the gridded permutations is in the cells."""
    return all(cell in cells for gp in gps for cell in gp.pos)


def _crosses(gp: GriddedPerm, cells: FrozenSet[Cell]) -> bool:
    """Return True if the gridded permutation has points in the cells and outside
    them."""
    points_inside = sum(1 for cell in gp.pos if cell in cells)
    return 0 < points_inside < len(gp)


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


def _in_order(tiling: Tiling, line_cells: Iterable[Cell], increasing: bool) -> bool:
    """Return True if the tiling's obstructions put the points of the cells, which
    share a row or a column, in the order of the direction: each monotone
    obstruction between two of them is implied."""
    return all(
        obstruction.contains(*tiling.obstructions)
        for obstruction in monotone_obstructions(line_cells, increasing)
        if obstruction.pos[0] != obstruction.pos[1]
    )


def _ordered_lines(
    tiling: Tiling, cells: FrozenSet[Cell], increasing: bool
) -> Tuple[Set[int], Set[int]]:
    """The columns, and the rows, whose cells of the set are in the order of the
    direction, those with one cell of the set among them."""
    ordered_columns = {
        column
        for column in {cell[0] for cell in cells}
        if _in_order(tiling, [cell for cell in cells if cell[0] == column], increasing)
    }
    ordered_rows = {
        row
        for row in {cell[1] for cell in cells}
        if _in_order(tiling, [cell for cell in cells if cell[1] == row], increasing)
    }
    return ordered_columns, ordered_rows


def _crossing_is_allowed(
    gp: GriddedPerm,
    cells: FrozenSet[Cell],
    ordered_columns: Set[int],
    ordered_rows: Set[int],
) -> bool:
    """Return True if the gridded permutation, which has points in the cells and
    outside them, has exactly one point in them, and touches either no other cell
    of that point's row or no other cell of its column, and touches the other cells
    of the column (row) only if the cells' points there are in the order of the
    direction."""
    cells_inside = [cell for cell in gp.pos if cell in cells]
    if len(cells_inside) != 1:
        return False
    column, row = cells_inside[0]
    cells_outside = [cell for cell in gp.pos if cell not in cells]
    touches_column = any(cell[0] == column for cell in cells_outside)
    touches_row = any(cell[1] == row for cell in cells_outside)
    if touches_column and touches_row:
        return False
    if touches_column and column not in ordered_columns:
        return False
    if touches_row and row not in ordered_rows:
        return False
    return True


def _qualifies(tiling: Tiling, cell_set: FrozenSet[Cell]) -> bool:
    """Return True if the set is of active cells, with no component assumption
    on them, and each of its cells has an obstruction of its own: the tiling of the
    set's own obstructions must have every cell of the set (an unrestricted cell
    has none)."""
    if not cell_set or not cell_set <= tiling.active_cells:
        return False
    if any(
        isinstance(assumption, ComponentAssumption)
        and any(gp.pos[0] in cell_set for gp in assumption.gps)
        for assumption in tiling.assumptions
    ):
        return False
    cells_with_own_obstructions = {
        cell
        for obstruction in tiling.obstructions
        if all(cell in cell_set for cell in obstruction.pos)
        for cell in obstruction.pos
    }
    return cell_set <= cells_with_own_obstructions


def _seen_gps(tiling: Tiling, cell_set: FrozenSet[Cell]) -> Iterator[GriddedPerm]:
    """The obstructions with points in the set and outside it, and the gridded
    permutations with points in the set of the requirement lists that do not lie
    in it."""
    for obstruction in tiling.obstructions:
        if _crosses(obstruction, cell_set):
            yield obstruction
    for requirement in tiling.requirements:
        if not _lies_in(requirement, cell_set):
            for gp in requirement:
                if any(cell in cell_set for cell in gp.pos):
                    yield gp


def is_reducible(
    tiling: Tiling, cells: Iterable[Cell], increasing: Optional[bool] = None
) -> bool:
    """Return True if the set of cells is reducible on the tiling in the direction,
    or in one of the two directions if none is given."""
    if increasing is None:
        return is_reducible(tiling, cells, True) or is_reducible(tiling, cells, False)
    cell_set = frozenset(cells)
    if not _qualifies(tiling, cell_set):
        return False
    ordered_columns, ordered_rows = _ordered_lines(tiling, cell_set, increasing)
    return all(
        _crossing_is_allowed(gp, cell_set, ordered_columns, ordered_rows)
        for gp in _seen_gps(tiling, cell_set)
    )


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


class _View(NamedTuple):
    """What the rest of the tiling has to do with a set of cells: the columns and
    the rows with cells outside the set, the obstructions and the requirement lists
    with points outside it, and the tracked cells."""

    outside_columns: FrozenSet[int]
    outside_rows: FrozenSet[int]
    crossing_obstructions: Tuple[GriddedPerm, ...]
    crossing_requirements: Tuple[Tuple[GriddedPerm, ...], ...]
    tracked: FrozenSet[Cell]


def _view(tiling: Tiling, cell_set: FrozenSet[Cell]) -> _View:
    outside = tiling.active_cells - cell_set
    return _View(
        frozenset(cell[0] for cell in outside),
        frozenset(cell[1] for cell in outside),
        tuple(ob for ob in tiling.obstructions if _crosses(ob, cell_set)),
        tuple(req for req in tiling.requirements if not _lies_in(req, cell_set)),
        frozenset(
            gp.pos[0] for assumption in tiling.assumptions for gp in assumption.gps
        ),
    )


def _moved(gp: GriddedPerm, source: Cell, target: Cell) -> GriddedPerm:
    """The gridded permutation with its point in the source cell in the target
    cell instead."""
    return GriddedPerm(
        gp.patt, tuple(target if cell == source else cell for cell in gp.pos)
    )


def _seen_alike(tiling: Tiling, source: Cell, target: Cell, view: _View) -> bool:
    """Return True if every obstruction with points outside the set that has its
    point of the set in the source cell is still an obstruction with that point in
    the target cell, and every such gridded permutation of a requirement list is
    still in the list."""
    for obstruction in view.crossing_obstructions:
        if source in obstruction.pos and not _moved(
            obstruction, source, target
        ).contains(*tiling.obstructions):
            return False
    for requirement in view.crossing_requirements:
        for gp in requirement:
            if source in gp.pos and _moved(gp, source, target) not in requirement:
                return False
    return True


def _left_out(
    cells: Tuple[Cell, ...], cell_set: FrozenSet[Cell], view: _View
) -> Tuple[Cell, ...]:
    """The cells of the set the rest does not see: no cell outside the set in
    their row or column, no point of an obstruction or requirement with points
    outside the set, and not tracked."""
    touched = {
        cell for gp in view.crossing_obstructions for cell in gp.pos if cell in cell_set
    }
    touched.update(
        cell
        for requirement in view.crossing_requirements
        for gp in requirement
        for cell in gp.pos
        if cell in cell_set
    )
    return tuple(
        cell
        for cell in cells
        if cell[0] not in view.outside_columns
        and cell[1] not in view.outside_rows
        and cell not in touched
        and cell not in view.tracked
    )


def _runs(
    tiling: Tiling, seen: List[Cell], along_row: bool, view: _View
) -> List[Tuple[Cell, ...]]:
    """The groups of two or more cells that the rest sees as one, in the rows (or
    the columns) with cells outside the set: consecutive cells of such a line whose
    columns (rows), and those between them, have no cell outside the set, and that
    the obstructions and requirements with points outside the set treat alike."""
    line_index, place_index = (1, 0) if along_row else (0, 1)
    outside_lines = view.outside_rows if along_row else view.outside_columns
    outside_places = view.outside_columns if along_row else view.outside_rows
    lines: DefaultDict[int, List[Cell]] = defaultdict(list)
    for cell in seen:
        if cell[line_index] in outside_lines:
            lines[cell[line_index]].append(cell)
    runs: List[Tuple[Cell, ...]] = []
    for line in sorted(lines):
        run: List[Cell] = []
        for cell in sorted(lines[line], key=itemgetter(place_index)):
            joins = cell not in view.tracked and cell[place_index] not in outside_places
            if (
                joins
                and run
                and not any(
                    run[-1][place_index] < place < cell[place_index]
                    for place in outside_places
                )
                and _seen_alike(tiling, run[-1], cell, view)
                and _seen_alike(tiling, cell, run[-1], view)
            ):
                run.append(cell)
                continue
            if len(run) > 1:
                runs.append(tuple(run))
            run = [cell] if joins else []
        if len(run) > 1:
            runs.append(tuple(run))
    return runs


@lru_cache(maxsize=1024)
def _layout(
    tiling: Tiling, cells: Tuple[Cell, ...]
) -> Tuple[Plan, FrozenSet[int], FrozenSet[int]]:
    """The plan of the reduction (see reduction_plan), and the columns and the
    rows with cells outside the set."""
    cell_set = frozenset(cells)
    view = _view(tiling, cell_set)
    left_out = _left_out(cells, cell_set, view)
    seen = [cell for cell in cells if cell not in left_out]
    # a cell of a group along a row has a column with no cell outside the set, so
    # it is in no column with one, and the two kinds of group do not meet
    runs = _runs(tiling, seen, True, view) + _runs(tiling, seen, False, view)
    grouped = {cell for run in runs for cell in run}
    groups = runs + [(cell,) for cell in seen if cell not in grouped]
    return (tuple(sorted(groups)), left_out), view.outside_columns, view.outside_rows


def reduction_plan(tiling: Tiling, cells: Iterable[Cell]) -> Plan:
    """Return the groups of the set's cells that the rest of the tiling sees as
    one, each first the cell the reduced tiling keeps for it, and the cells the
    rest does not see, which the reduced tiling leaves out."""
    return _layout(tiling, tuple(sorted(set(cells))))[0]


def _own_is_tracked(groups: Groups, left_out: Tuple[Cell, ...]) -> bool:
    """The own tiling tracks the groups unless its size alone is their number of
    points: one group, and no cell left out."""
    return len(groups) != 1 or bool(left_out)


def _reduced_tiling(
    tiling: Tiling,
    cell_set: FrozenSet[Cell],
    plan: Plan,
    increasing: bool,
    tracked: bool,
) -> Tiling:
    groups, left_out = plan
    kept = [group[0] for group in groups]
    emptied = [cell for group in groups for cell in group[1:]] + list(left_out)
    return Tiling(
        [ob for ob in tiling.obstructions if not _lies_in([ob], cell_set)]
        + monotone_obstructions(kept, increasing)
        + [GriddedPerm.point_perm(cell) for cell in emptied],
        [req for req in tiling.requirements if not _lies_in(req, cell_set)],
        list(tiling.assumptions)
        + ([TrackingAssumption.from_cells([cell]) for cell in kept] if tracked else []),
    )


def _own_tiling(tiling: Tiling, cell_set: FrozenSet[Cell], plan: Plan) -> Tiling:
    groups, left_out = plan
    width, height = tiling.dimensions
    other_cells_emptied = [
        GriddedPerm.point_perm((column, row))
        for column in range(width)
        for row in range(height)
        if (column, row) not in cell_set
    ]
    return Tiling(
        [ob for ob in tiling.obstructions if _lies_in([ob], cell_set)]
        + other_cells_emptied,
        [req for req in tiling.requirements if _lies_in(req, cell_set)],
        (
            [TrackingAssumption.from_cells(list(group)) for group in groups]
            if _own_is_tracked(groups, left_out)
            else []
        ),
    )


def reduction_children(
    tiling: Tiling,
    cells: Iterable[Cell],
    increasing: bool,
    tracked: bool = True,
) -> Tuple[Tiling, Tiling]:
    """Return the reduced tiling, with a cell for each group of the set that the
    rest sees as one and none for the cells it does not see, those cells increasing
    (or decreasing) and in that order in their rows and columns, each tracked if
    tracked; and the tiling of the set's own obstructions and requirements, each
    group tracked if there are two or more, or cells left out."""
    cell_set = frozenset(cells)
    plan = reduction_plan(tiling, cell_set)
    return (
        _reduced_tiling(tiling, cell_set, plan, increasing, tracked),
        _own_tiling(tiling, cell_set, plan),
    )


def _words(gp: GriddedPerm) -> Tuple[Words, Words, Dict[Cell, List[int]]]:
    """The words of the gridded permutation: for each column the cells of its
    points from left to right, for each row from bottom to top, and for each cell
    the ranks of the values of its points from left to right."""
    column_words: DefaultDict[int, List[Cell]] = defaultdict(list)
    for cell in gp.pos:
        column_words[cell[0]].append(cell)
    row_words: DefaultDict[int, List[Cell]] = defaultdict(list)
    for index in sorted(range(len(gp)), key=lambda index: gp.patt[index]):
        row_words[gp.pos[index][1]].append(gp.pos[index])
    values_in_cell: DefaultDict[Cell, List[int]] = defaultdict(list)
    for value, cell in zip(gp.patt, gp.pos):
        values_in_cell[cell].append(value)
    ranks = {
        cell: [sorted(values).index(value) for value in values]
        for cell, values in values_in_cell.items()
    }
    return column_words, row_words, ranks


def _slots(words: Words) -> Tuple[DefaultDict[Cell, List[int]], int]:
    """For each cell, the places of its letters in the words read one line after
    the other, and the number of letters."""
    slots: DefaultDict[Cell, List[int]] = defaultdict(list)
    index = 0
    for line in sorted(words):
        for cell in words[line]:
            slots[cell].append(index)
            index += 1
    return slots, index


def _from_words(
    column_words: Words, row_words: Words, ranks: Dict[Cell, List[int]]
) -> GriddedPerm:
    """The gridded permutation with the words."""
    positions, size = _slots(column_words)
    values, number_of_values = _slots(row_words)
    if number_of_values != size:
        raise ValueError("the column words and the row words have different lengths")
    patt = [0] * size
    pos: List[Cell] = [(0, 0)] * size
    for cell, cell_positions in positions.items():
        if not len(values[cell]) == len(cell_positions) == len(ranks[cell]):
            raise ValueError(f"the words have different numbers of points in {cell}")
        for position, rank in zip(cell_positions, ranks[cell]):
            patt[position] = values[cell][rank]
            pos[position] = cell
    return GriddedPerm(Perm(patt), tuple(pos))


def _monotone_ranks(size: int, increasing: bool) -> List[int]:
    return list(range(size)) if increasing else list(range(size - 1, -1, -1))


def _canonical_words(
    kept: List[Cell], points_in_cell: Counter, along_row: bool, increasing: bool
) -> Words:
    """The canonical word of each row (from bottom to top) or each column (from
    left to right) of the kept cells, each with its number of points: the cells in
    the order of their columns (rows), the other way round when decreasing."""
    line_index, place_index = (1, 0) if along_row else (0, 1)
    lines: DefaultDict[int, List[Cell]] = defaultdict(list)
    for cell in kept:
        lines[cell[line_index]].append(cell)
    return {
        line: [
            cell
            for cell in sorted(
                cells, key=itemgetter(place_index), reverse=not increasing
            )
            for _ in range(points_in_cell[cell])
        ]
        for line, cells in lines.items()
    }


def _fill(
    word: List[Cell], cells: FrozenSet[Cell], filler: List[Cell], line: int
) -> List[Cell]:
    """The word with its letters of the cells, in order, replaced by the filler's."""
    if sum(1 for cell in word if cell in cells) != len(filler):
        raise ValueError(f"the line {line} has a different number of the set's points")
    letters = iter(filler)
    return [next(letters) if cell in cells else cell for cell in word]


def _combined_words(
    base: Words, filler: Words, cells: FrozenSet[Cell], outside_lines: FrozenSet[int]
) -> Words:
    """For each line with cells outside the set, the base's word with its letters
    of the set replaced, in order, by the filler's; for every other line, the
    filler's word."""
    return {
        line: (
            _fill(base.get(line, []), cells, filler.get(line, []), line)
            if line in outside_lines
            else list(filler.get(line, []))
        )
        for line in set(base) | set(filler)
    }


class ReductionConstructor(Constructor[Tiling, GriddedPerm]):
    """The constructor of a reduction: the Hadamard product of the reduced tiling
    and the tiling of the cells' own obstructions in the variables that count the
    points in the groups of cells the rest of the tiling sees as one, at 1, and the
    product in the size of the cells the reduced tiling leaves out.

        parent(n; p) = sum over w and m of reduced(n - m; p, w) * own(|w| + m; w)
    """

    def __init__(
        self,
        parent: Tiling,
        children: Tuple[Tiling, ...],
        cells: Iterable[Cell],
        plan: Plan,
    ):
        reduced_tiling, own_tiling = children
        self.cells = tuple(sorted(set(cells)))
        self.groups, left_out = plan
        self.leaves_out = bool(left_out)
        reduced_parameters = reduced_tiling.extra_parameters

        def reduced_parameter(assumption: TrackingAssumption) -> str:
            return reduced_tiling.get_assumption_parameter(
                reduced_tiling.forward_map.map_assumption(assumption)
            )

        self.reduced_group_parameters = tuple(
            reduced_parameter(TrackingAssumption.from_cells([group[0]]))
            for group in self.groups
        )
        self.reduced_group_indices = tuple(
            reduced_parameters.index(name) for name in self.reduced_group_parameters
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
        if not _own_is_tracked(self.groups, left_out):
            self.own_group_parameters: Optional[Tuple[str, ...]] = None
            self.own_group_indices: Tuple[int, ...] = ()
        else:
            forward, _ = compression(self.cells)
            self.own_group_parameters = tuple(
                own_tiling.get_assumption_parameter(
                    TrackingAssumption.from_cells([forward[cell] for cell in group])
                )
                for group in self.groups
            )
            self.own_group_indices = tuple(
                own_tiling.extra_parameters.index(name)
                for name in self.own_group_parameters
            )

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

    def _own_counts(self, own_terms: Callable[[int], Terms], size: int) -> Counter:
        """The number of objects of the own tiling with each number of points in
        the groups, for objects of the size."""
        own_counts: Counter = Counter()
        for own_parameters, own_count in own_terms(size).items():
            own_counts[self._group_sizes(own_parameters, size)] += own_count
        return own_counts

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        reduced_terms, own_terms = subterms
        own_counts_by_size: Dict[int, Counter] = {}
        terms: Terms = Counter()
        for left_out_size in self._left_out_sizes(n):
            for reduced_parameters, reduced_count in reduced_terms(
                n - left_out_size
            ).items():
                group_sizes, parent_parameters = self._split(reduced_parameters)
                own_size = sum(group_sizes) + left_out_size
                if own_size not in own_counts_by_size:
                    own_counts_by_size[own_size] = self._own_counts(own_terms, own_size)
                own_count = own_counts_by_size[own_size][group_sizes]
                if own_count:
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
        own_by_size: Dict[int, DefaultDict[Parameters, List[Optional[GriddedPerm]]]]
        own_by_size = {}
        for left_out_size in self._left_out_sizes(n):
            for reduced_parameters, reduced_list in reduced_objects(
                n - left_out_size
            ).items():
                group_sizes, parent_parameters = self._split(reduced_parameters)
                own_size = sum(group_sizes) + left_out_size
                if own_size not in own_by_size:
                    own_by_size[own_size] = self._own_objects(own_objects, own_size)
                own_list = own_by_size[own_size].get(group_sizes, [])
                if reduced_list and own_list:
                    yield parent_parameters, (reduced_list, own_list)

    def _sample_choices(
        self, n: int, parent_parameters: Dict[str, int]
    ) -> Iterator[Tuple[int, Dict[str, int], int, Dict[str, int]]]:
        """For each number of points in the cells left out and in the groups that
        the parent's parameters allow, the size and the parameters of the reduced
        tiling, and the size and the parameters of the own tiling."""
        fixed_parameters = {
            self.parent_to_reduced[name]: value
            for name, value in parent_parameters.items()
        }
        for left_out_size in self._left_out_sizes(n):
            reduced_size = n - left_out_size
            for group_sizes in product(
                range(reduced_size + 1), repeat=len(self.groups)
            ):
                if sum(group_sizes) > reduced_size:
                    continue
                reduced_parameters = dict(fixed_parameters)
                if all(
                    reduced_parameters.setdefault(name, group_size) == group_size
                    for name, group_size in zip(
                        self.reduced_group_parameters, group_sizes
                    )
                ):
                    yield (
                        reduced_size,
                        reduced_parameters,
                        sum(group_sizes) + left_out_size,
                        self._own_parameters(group_sizes),
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
                reduced_size, reduced_parameters, own_size, own_parameters = choice
                return (
                    subsamplers[0](n=reduced_size, **reduced_parameters),
                    subsamplers[1](n=own_size, **own_parameters),
                )
        raise RuntimeError("Function did not return")

    @staticmethod
    def _choice_count(
        subrecs: SubRecs, choice: Tuple[int, Dict[str, int], int, Dict[str, int]]
    ) -> int:
        """The number of pairs of objects for the choice of the sizes and the
        parameters of the reduced tiling and of the own tiling."""
        reduced_size, reduced_parameters, own_size, own_parameters = choice
        reduced_count = subrecs[0](n=reduced_size, **reduced_parameters)
        if not reduced_count:
            return 0
        return reduced_count * subrecs[1](n=own_size, **own_parameters)

    def equiv(
        self, other: "Constructor", data: Optional[object] = None
    ) -> Tuple[bool, Optional[object]]:
        return (
            isinstance(other, ReductionConstructor)
            and len(self.groups) == len(other.groups)
            and self.leaves_out == other.leaves_out
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

    def plan(self, comb_class: Tiling) -> Plan:
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
            comb_class, children, self.cells, self.plan(comb_class)
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

    def reduced_gp(self, comb_class: Tiling, gp: GriddedPerm) -> GriddedPerm:
        """The gridded permutation of the reduced tiling for one of the tiling, in
        the tiling's cells: the share of the set canonical, each group's points in
        its first cell, and the points of the cells left out removed."""
        (groups, _), outside_columns, outside_rows = _layout(comb_class, self.cells)
        cell_set = frozenset(self.cells)
        keeper = {cell: group[0] for group in groups for cell in group}
        kept = [group[0] for group in groups]
        points_in_cell = Counter(keeper[cell] for cell in gp.pos if cell in keeper)
        column_words, row_words, ranks = _words(gp)
        new_ranks = {
            cell: values for cell, values in ranks.items() if cell not in cell_set
        }
        for cell in kept:
            new_ranks[cell] = _monotone_ranks(points_in_cell[cell], self.increasing)
        return _from_words(
            _combined_words(
                column_words,
                _canonical_words(kept, points_in_cell, False, self.increasing),
                cell_set,
                outside_columns,
            ),
            _combined_words(
                row_words,
                _canonical_words(kept, points_in_cell, True, self.increasing),
                cell_set,
                outside_rows,
            ),
            new_ranks,
        )

    def parent_gp(
        self, comb_class: Tiling, reduced_gp: GriddedPerm, own_gp: GriddedPerm
    ) -> GriddedPerm:
        """The gridded permutation of the tiling for one of the reduced tiling and
        one of the own tiling, both in the tiling's cells: the rest from the first,
        the share of the set from the second."""
        _, outside_columns, outside_rows = _layout(comb_class, self.cells)
        cell_set = frozenset(self.cells)
        reduced_columns, reduced_rows, reduced_ranks = _words(reduced_gp)
        own_columns, own_rows, own_ranks = _words(own_gp)
        ranks = {
            cell: values
            for cell, values in reduced_ranks.items()
            if cell not in cell_set
        }
        ranks.update(own_ranks)
        return _from_words(
            _combined_words(reduced_columns, own_columns, cell_set, outside_columns),
            _combined_words(reduced_rows, own_rows, cell_set, outside_rows),
            ranks,
        )

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
        yield self.parent_gp(
            comb_class,
            children[0].backward_map.map_gp(reduced_gp),
            GriddedPerm(own_gp.patt, tuple(backward[cell] for cell in own_gp.pos)),
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
            children[0].forward_map.map_gp(self.reduced_gp(comb_class, obj)),
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

    With max_cells, the sets of "cut" and "any" have at most that many cells.

    A set is reduced if it is reducible, it is not all of the active cells, it is
    not rigid (every cell monotone, and the points of any two of its cells in a
    row or a column in a fixed order: reducing it would change nothing, or reverse
    it), it is not a single finite cell, and the rest of the tiling sees
    one of its cells (if it sees none, the set is a factor). So the reduced tiling
    is never larger than the tiling, and smaller at some size.
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
        elif self.region == "cut":
            candidates = (
                side
                for side in self.cuts(tiling, active_cells)
                if self.max_cells is None or len(side) <= self.max_cells
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
            directions = [
                increasing
                for increasing in (True, False)
                if is_reducible(comb_class, cells, increasing)
            ]
            if not directions or is_rigid(comb_class, cells):
                continue
            if not reduction_plan(comb_class, cells)[0]:
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
        return cls(d.get("tracked", True), d.get("region", "cell"), d.get("max_cells"))

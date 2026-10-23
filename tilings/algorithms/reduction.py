"""The reduction of a set of cells of a tiling: the condition under which a set is
reducible, the plan of what the reduced tiling keeps of it, the two children, and
the words that the maps between the tiling and the children are built from.

`tilings.strategies.reduction` has the strategy, its constructor and its factory,
and the argument why the reduction holds.
"""

from collections import Counter, defaultdict
from functools import lru_cache
from itertools import product
from operator import itemgetter
from typing import (
    TYPE_CHECKING,
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
)

from permuta import Perm
from tilings.assumptions import ComponentAssumption, TrackingAssumption
from tilings.griddedperm import GriddedPerm

if TYPE_CHECKING:
    from tilings import Tiling

__all__ = (
    "combine_gridded_perms",
    "is_reducible",
    "is_rigid",
    "monotone_obstructions",
    "own_is_tracked",
    "reduce_gridded_perm",
    "ReductionPlan",
    "reduction_children",
    "reduction_plan",
)

Cell = Tuple[int, int]
Groups = Tuple[Tuple[Cell, ...], ...]
Words = Dict[int, List[Cell]]


class ReductionPlan(NamedTuple):
    """The groups of the set's cells that the rest of the tiling sees as one, each
    first the cell the reduced tiling keeps for it, and the cells the rest does not
    see, which the reduced tiling leaves out."""

    groups: Groups
    left_out: Tuple[Cell, ...]


class _Layout(NamedTuple):
    """The plan, and the columns and the rows with cells outside the set."""

    plan: ReductionPlan
    outside_columns: FrozenSet[int]
    outside_rows: FrozenSet[int]


def _lies_in(gridded_perms: Iterable[GriddedPerm], cells: FrozenSet[Cell]) -> bool:
    """Return True if every point of the gridded permutations is in the cells."""
    return all(
        cell in cells for gridded_perm in gridded_perms for cell in gridded_perm.pos
    )


def _crosses(gridded_perm: GriddedPerm, cells: FrozenSet[Cell]) -> bool:
    """Return True if the gridded permutation has points in the cells and outside
    them."""
    points_inside = sum(1 for cell in gridded_perm.pos if cell in cells)
    return 0 < points_inside < len(gridded_perm)


def monotone_obstructions(cells: Iterable[Cell], increasing: bool) -> List[GriddedPerm]:
    """Return the gridded 21s (increasing) or 12s (decreasing) with both points in
    cells of the set that share a row or a column, which make the share of the set
    canonical."""
    cell_list = sorted(set(cells))
    pattern = Perm((1, 0)) if increasing else Perm((0, 1))
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
        obstructions.append(GriddedPerm(pattern, (left_cell, right_cell)))
    return obstructions


def _in_order(tiling: "Tiling", line_cells: Iterable[Cell], increasing: bool) -> bool:
    """Return True if the tiling's obstructions put the points of the cells, which
    share a row or a column, in the order of the direction: each monotone
    obstruction between two of them is implied."""
    return all(
        obstruction.contains(*tiling.obstructions)
        for obstruction in monotone_obstructions(line_cells, increasing)
        if obstruction.pos[0] != obstruction.pos[1]
    )


def _ordered_lines(
    tiling: "Tiling", cells: FrozenSet[Cell], increasing: bool
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
    gridded_perm: GriddedPerm,
    cells: FrozenSet[Cell],
    ordered_columns: Set[int],
    ordered_rows: Set[int],
) -> bool:
    """Return True if the gridded permutation, which has points in the cells and
    outside them, has exactly one point in them, and touches either no other cell
    of that point's row or no other cell of its column, and touches the other cells
    of the column (row) only if the cells' points there are in the order of the
    direction."""
    cells_inside = [cell for cell in gridded_perm.pos if cell in cells]
    if len(cells_inside) != 1:
        return False
    column, row = cells_inside[0]
    cells_outside = [cell for cell in gridded_perm.pos if cell not in cells]
    touches_column = any(cell[0] == column for cell in cells_outside)
    touches_row = any(cell[1] == row for cell in cells_outside)
    if touches_column and touches_row:
        return False
    if touches_column and column not in ordered_columns:
        return False
    if touches_row and row not in ordered_rows:
        return False
    return True


def _qualifies(tiling: "Tiling", cell_set: FrozenSet[Cell]) -> bool:
    """Return True if the set is of active cells, the assumptions track points in
    its cells only one by one (no component assumption on them, and no tracked
    gridded permutation of two or more points with a point in them: the sorting
    keeps the number of points in each cell, but not the occurrences of a pattern),
    and each of its cells has an obstruction of its own: the tiling of the set's
    own obstructions must have every cell of the set (an unrestricted cell has
    none)."""
    if not cell_set or not cell_set <= tiling.active_cells:
        return False
    if any(
        (isinstance(assumption, ComponentAssumption) or len(gridded_perm) > 1)
        and any(cell in cell_set for cell in gridded_perm.pos)
        for assumption in tiling.assumptions
        for gridded_perm in assumption.gps
    ):
        return False
    cells_with_own_obstructions = {
        cell
        for obstruction in tiling.obstructions
        if all(cell in cell_set for cell in obstruction.pos)
        for cell in obstruction.pos
    }
    return cell_set <= cells_with_own_obstructions


def _seen_gridded_perms(
    tiling: "Tiling", cell_set: FrozenSet[Cell]
) -> Iterator[GriddedPerm]:
    """The obstructions with points in the set and outside it, and the gridded
    permutations with points in the set of the requirement lists that do not lie
    in it."""
    for obstruction in tiling.obstructions:
        if _crosses(obstruction, cell_set):
            yield obstruction
    for requirement in tiling.requirements:
        if not _lies_in(requirement, cell_set):
            for gridded_perm in requirement:
                if any(cell in cell_set for cell in gridded_perm.pos):
                    yield gridded_perm


def is_reducible(
    tiling: "Tiling", cells: Iterable[Cell], increasing: Optional[bool] = None
) -> bool:
    """Return True if the set of cells is reducible on the tiling in the direction,
    or in one of the two directions if none is given."""
    cell_set = frozenset(cells)
    if increasing is None:
        return is_reducible(tiling, cell_set, True) or is_reducible(
            tiling, cell_set, False
        )
    if not _qualifies(tiling, cell_set):
        return False
    ordered_columns, ordered_rows = _ordered_lines(tiling, cell_set, increasing)
    return all(
        _crossing_is_allowed(gridded_perm, cell_set, ordered_columns, ordered_rows)
        for gridded_perm in _seen_gridded_perms(tiling, cell_set)
    )


def is_rigid(tiling: "Tiling", cells: Iterable[Cell]) -> bool:
    """Return True if the share of the cells is the same in every gridded
    permutation with the same number of points in each cell: every cell is
    monotone, and the points of any two of the cells in a row or a column are in
    a fixed order. Reducing such cells changes nothing, or reverses them."""
    cell_list = sorted(set(cells))
    obstructions = tiling.obstructions

    def is_forbidden(gridded_perm: GriddedPerm) -> bool:
        return gridded_perm.contains(*obstructions)

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


class _View(NamedTuple):
    """What the rest of the tiling has to do with a set of cells: the columns and
    the rows with cells outside the set, the obstructions and the requirement lists
    with points outside it, and the tracked cells."""

    outside_columns: FrozenSet[int]
    outside_rows: FrozenSet[int]
    crossing_obstructions: Tuple[GriddedPerm, ...]
    crossing_requirements: Tuple[Tuple[GriddedPerm, ...], ...]
    tracked: FrozenSet[Cell]


def _view(tiling: "Tiling", cell_set: FrozenSet[Cell]) -> _View:
    outside = tiling.active_cells - cell_set
    return _View(
        frozenset(cell[0] for cell in outside),
        frozenset(cell[1] for cell in outside),
        tuple(
            obstruction
            for obstruction in tiling.obstructions
            if _crosses(obstruction, cell_set)
        ),
        tuple(
            requirement
            for requirement in tiling.requirements
            if not _lies_in(requirement, cell_set)
        ),
        frozenset(
            cell
            for assumption in tiling.assumptions
            for gridded_perm in assumption.gps
            for cell in gridded_perm.pos
        ),
    )


def _moved(gridded_perm: GriddedPerm, source: Cell, target: Cell) -> GriddedPerm:
    """The gridded permutation with its point in the source cell in the target
    cell instead."""
    return GriddedPerm(
        gridded_perm.patt,
        tuple(target if cell == source else cell for cell in gridded_perm.pos),
    )


def _seen_alike(tiling: "Tiling", source: Cell, target: Cell, view: _View) -> bool:
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
        for gridded_perm in requirement:
            if (
                source in gridded_perm.pos
                and _moved(gridded_perm, source, target) not in requirement
            ):
                return False
    return True


def _left_out(
    cells: Tuple[Cell, ...], cell_set: FrozenSet[Cell], view: _View
) -> Tuple[Cell, ...]:
    """The cells of the set the rest does not see: no cell outside the set in
    their row or column, no point of an obstruction or requirement with points
    outside the set, and not tracked."""
    touched = {
        cell
        for gridded_perm in view.crossing_obstructions
        for cell in gridded_perm.pos
        if cell in cell_set
    }
    touched.update(
        cell
        for requirement in view.crossing_requirements
        for gridded_perm in requirement
        for cell in gridded_perm.pos
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
    tiling: "Tiling", seen: List[Cell], view: _View, along_row: bool
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


# The maps call _layout once for every gridded permutation they map, each time for the
# same tiling and set: the cache computes the plan and the lines with cells outside
# the set once for each.
@lru_cache(maxsize=1024)
def _layout(tiling: "Tiling", cells: Tuple[Cell, ...]) -> _Layout:
    """The plan of the reduction (see reduction_plan), and the columns and the
    rows with cells outside the set."""
    cell_set = frozenset(cells)
    view = _view(tiling, cell_set)
    left_out = _left_out(cells, cell_set, view)
    seen = [cell for cell in cells if cell not in left_out]
    # a cell of a group along a row has a column with no cell outside the set, so
    # it is in no column with one, and the two kinds of group do not meet
    runs = _runs(tiling, seen, view, along_row=True) + _runs(
        tiling, seen, view, along_row=False
    )
    grouped = {cell for run in runs for cell in run}
    groups = runs + [(cell,) for cell in seen if cell not in grouped]
    return _Layout(
        ReductionPlan(tuple(sorted(groups)), left_out),
        view.outside_columns,
        view.outside_rows,
    )


def reduction_plan(tiling: "Tiling", cells: Iterable[Cell]) -> ReductionPlan:
    """Return the groups of the set's cells that the rest of the tiling sees as
    one, each first the cell the reduced tiling keeps for it, and the cells the
    rest does not see, which the reduced tiling leaves out."""
    return _layout(tiling, tuple(sorted(set(cells)))).plan


def own_is_tracked(groups: Groups, left_out: Tuple[Cell, ...]) -> bool:
    """The own tiling tracks the groups unless its size alone is their number of
    points: one group, and no cell left out."""
    return len(groups) != 1 or bool(left_out)


def _reduced_tiling(
    tiling: "Tiling",
    cell_set: FrozenSet[Cell],
    plan: ReductionPlan,
    increasing: bool,
    tracked: bool,
) -> "Tiling":
    groups, left_out = plan
    kept = [group[0] for group in groups]
    emptied = [cell for group in groups for cell in group[1:]] + list(left_out)
    return tiling.__class__(
        [
            obstruction
            for obstruction in tiling.obstructions
            if not _lies_in([obstruction], cell_set)
        ]
        + monotone_obstructions(kept, increasing)
        + [GriddedPerm.point_perm(cell) for cell in emptied],
        [
            requirement
            for requirement in tiling.requirements
            if not _lies_in(requirement, cell_set)
        ],
        list(tiling.assumptions)
        + ([TrackingAssumption.from_cells([cell]) for cell in kept] if tracked else []),
    )


def _own_tiling(
    tiling: "Tiling", cell_set: FrozenSet[Cell], plan: ReductionPlan
) -> "Tiling":
    groups, left_out = plan
    width, height = tiling.dimensions
    other_cells_emptied = [
        GriddedPerm.point_perm((column, row))
        for column in range(width)
        for row in range(height)
        if (column, row) not in cell_set
    ]
    return tiling.__class__(
        [
            obstruction
            for obstruction in tiling.obstructions
            if _lies_in([obstruction], cell_set)
        ]
        + other_cells_emptied,
        [
            requirement
            for requirement in tiling.requirements
            if _lies_in(requirement, cell_set)
        ],
        (
            [TrackingAssumption.from_cells(list(group)) for group in groups]
            if own_is_tracked(groups, left_out)
            else []
        ),
    )


def reduction_children(
    tiling: "Tiling",
    cells: Iterable[Cell],
    increasing: bool,
    tracked: bool = True,
) -> Tuple["Tiling", "Tiling"]:
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


def _words(gridded_perm: GriddedPerm) -> Tuple[Words, Words, Dict[Cell, List[int]]]:
    """The words of the gridded permutation: for each column the cells of its
    points from left to right, for each row from bottom to top, and for each cell
    the ranks of the values of its points from left to right."""
    column_words: DefaultDict[int, List[Cell]] = defaultdict(list)
    for cell in gridded_perm.pos:
        column_words[cell[0]].append(cell)
    row_words: DefaultDict[int, List[Cell]] = defaultdict(list)
    for index in sorted(
        range(len(gridded_perm)), key=lambda index: gridded_perm.patt[index]
    ):
        row_words[gridded_perm.pos[index][1]].append(gridded_perm.pos[index])
    values_in_cell: DefaultDict[Cell, List[int]] = defaultdict(list)
    for value, cell in zip(gridded_perm.patt, gridded_perm.pos):
        values_in_cell[cell].append(value)
    ranks = {
        cell: list(Perm.to_standard(values)) for cell, values in values_in_cell.items()
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
    pattern = [0] * size
    cells_of_points: List[Cell] = [(0, 0)] * size
    for cell, cell_positions in positions.items():
        if not len(values[cell]) == len(cell_positions) == len(ranks[cell]):
            raise ValueError(f"the words have different numbers of points in {cell}")
        for position, rank in zip(cell_positions, ranks[cell]):
            pattern[position] = values[cell][rank]
            cells_of_points[position] = cell
    return GriddedPerm(Perm(pattern), tuple(cells_of_points))


def _monotone_ranks(size: int, increasing: bool) -> List[int]:
    return list(range(size)) if increasing else list(range(size - 1, -1, -1))


def _canonical_words(
    kept: List[Cell], points_in_cell: Counter, *, along_row: bool, increasing: bool
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


def reduce_gridded_perm(
    tiling: "Tiling",
    cells: Iterable[Cell],
    gridded_perm: GriddedPerm,
    increasing: bool,
) -> GriddedPerm:
    """Return the gridded permutation of the reduced tiling for one of the tiling, in
    the tiling's cells: the share of the set canonical, each group's points in its
    first cell, and the points of the cells left out removed."""
    cell_tuple = tuple(sorted(set(cells)))
    layout = _layout(tiling, cell_tuple)
    cell_set = frozenset(cell_tuple)
    keeper = {cell: group[0] for group in layout.plan.groups for cell in group}
    kept = [group[0] for group in layout.plan.groups]
    points_in_cell = Counter(
        keeper[cell] for cell in gridded_perm.pos if cell in keeper
    )
    column_words, row_words, ranks = _words(gridded_perm)
    new_ranks = {cell: values for cell, values in ranks.items() if cell not in cell_set}
    for cell in kept:
        new_ranks[cell] = _monotone_ranks(points_in_cell[cell], increasing)
    return _from_words(
        _combined_words(
            column_words,
            _canonical_words(
                kept, points_in_cell, along_row=False, increasing=increasing
            ),
            cell_set,
            layout.outside_columns,
        ),
        _combined_words(
            row_words,
            _canonical_words(
                kept, points_in_cell, along_row=True, increasing=increasing
            ),
            cell_set,
            layout.outside_rows,
        ),
        new_ranks,
    )


def combine_gridded_perms(
    tiling: "Tiling",
    cells: Iterable[Cell],
    reduced_gridded_perm: GriddedPerm,
    own_gridded_perm: GriddedPerm,
) -> GriddedPerm:
    """Return the gridded permutation of the tiling for one of the reduced tiling and
    one of the own tiling, both in the tiling's cells: the rest from the first, the
    share of the set from the second."""
    cell_tuple = tuple(sorted(set(cells)))
    layout = _layout(tiling, cell_tuple)
    cell_set = frozenset(cell_tuple)
    reduced_columns, reduced_rows, reduced_ranks = _words(reduced_gridded_perm)
    own_columns, own_rows, own_ranks = _words(own_gridded_perm)
    ranks = {
        cell: values for cell, values in reduced_ranks.items() if cell not in cell_set
    }
    ranks.update(own_ranks)
    return _from_words(
        _combined_words(reduced_columns, own_columns, cell_set, layout.outside_columns),
        _combined_words(reduced_rows, own_rows, cell_set, layout.outside_rows),
        ranks,
    )

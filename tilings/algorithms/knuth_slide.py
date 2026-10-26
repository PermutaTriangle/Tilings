"""
The Knuth slide: a bijection between the gridded permutations of two tilings that
reverses a block of adjacent columns.

A block is a set of k >= 2 adjacent columns whose active cells are exactly the same
nonempty set of rows R in each column. The points of a gridded permutation in the
block form its block word w, the concatenation of the column words. With P(w) and
Q(w) its insertion and recording tableaux under RSK, and evac Schutzenberger's
evacuation, the slide replaces w by RSK^-1(P(w), evac(Q(w))), Permuta's
evacuate_recording_tableau, and reverses the columns: the block's first column gets
as many of the new word's first letters as its last column had points, the second
column as many of the next letters as the last but one had, and so on, each value
keeping its row. The new word has the same insertion tableau, so on every interval
of values it is Knuth equivalent to the old one; and every run of adjacent columns
gets the RSK shape of its mirror image, as evacuation is the recording tableau of
the reverse-complement (Schutzenberger). The map is an involution, as evacuation is.

The slide moves points between the block's columns, so it keeps a constraint on the
block's points when the constraint does not depend on how those points are split
among the columns and the rows: when every regridding of them, as below, is
forbidden too. An obstruction's points in the block, in the rows that they span,
form its window. The slide is a bijection onto the gridded permutations of the child
tiling when every constraint touching the block depends only on what the slide
keeps:

- Every obstruction with points in the block is not contradictory, that is, some
  gridded permutation can have it, and it is of window type or of run type. A
  contradictory obstruction may be all that keeps a cell of the block active, and
  it has no regriddings to keep the cell active in the child; Tilings makes none.
    - Window type: no other point of it has a value between two of its block
      values, and every regridding of its block points over the block's columns,
      and over the block's rows from its lowest block row to its highest, is
      forbidden. For each configuration of the other points and each set of rows
      that the block points span, the patterns that these obstructions see in the
      block must form a Knuth-closed set: one whose avoiders are closed under Knuth
      equivalence (Permuta's is_knuth_closed). The slide keeps the Knuth class of
      the block word on the window, so it keeps whether the window avoids them.
    - Run type: all its points are in the block, and every regridding over the run
      of columns it spans and all the block's rows is forbidden. For each run, the
      patterns must form a shape-closed set: one whose avoiders are determined by
      the RSK shape, such as a monotone pattern (Permuta's is_shape_closed). The
      slide gives the mirrored run that shape, so the mirrored run avoids them.
- Of every requirement, the gridded permutations with points in the block are
  single points, whose cells in the block make up whole columns of it, whole rows of
  it, or both; those with no points in the block may be of any length.
- Every assumption with points in the block counts points (TrackingAssumption) on
  whole columns of the block or on whole rows of it.
  The slide gives each column as many points as its mirror had, and each value
  keeps its row, so it keeps how many points those requirements and assumptions see.

The child has the obstructions with no block points, every regridding of the window
type ones, the run type ones regridded over the mirrored runs, and the requirements
and assumptions with the block's columns mirrored. A block of one row of cells is
the Knuth slide of adjacent cells. A block of several rows of cells is its Ferrers
version, which slides a shape of cells as Babson and West's sliding lemma slides a
Ferrers board.
"""

from collections import defaultdict
from itertools import combinations_with_replacement
from typing import (
    TYPE_CHECKING,
    Callable,
    DefaultDict,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
)

from permuta import Perm
from permuta.permutils import (
    evacuate_recording_tableau,
    is_knuth_closed,
    is_shape_closed,
)
from tilings.assumptions import TrackingAssumption
from tilings.griddedperm import GriddedPerm

if TYPE_CHECKING:
    from tilings import Tiling

__all__ = ["KnuthSlide"]

Cell = Tuple[int, int]
Gridding = Tuple[Perm, Tuple[Cell, ...]]


def _mirror_column(column: int, width: int, x: int) -> int:
    """The column that the slide of the block of the width from the column takes the
    column x of the block to."""
    return 2 * column + width - 1 - x


class _Block(NamedTuple):
    """A block's columns, its rows of cells, and its cells."""

    columns: Tuple[int, ...]
    rows: Tuple[int, ...]
    cells: FrozenSet[Cell]

    def indices(self, gridded_perm: GriddedPerm) -> List[int]:
        """The indices of the gridded permutation's points in the block."""
        return [i for i, cell in enumerate(gridded_perm.pos) if cell in self.cells]

    def pattern(self, gridded_perm: GriddedPerm) -> Perm:
        """The pattern of the gridded permutation's points in the block."""
        return gridded_perm.get_gridded_perm_in_cells(self.cells).patt

    @classmethod
    def of(cls, column: int, width: int, rows: Tuple[int, ...]) -> "_Block":
        """The block of the width from the column, in the rows of cells."""
        columns = tuple(range(column, column + width))
        return cls(columns, rows, frozenset((x, y) for x in columns for y in rows))


class _WindowKey(NamedTuple):
    """What tells a block's windows apart: the pattern of an obstruction's points
    outside the block and their cells, how many of them lie below its block points,
    and the rows of the block that its block points span."""

    outside_pattern: Tuple[int, ...]
    outside_cells: Tuple[Cell, ...]
    below: int
    rows: Tuple[int, ...]


class _Constraints:
    """A block's obstructions as window and run constraints, with the patterns that
    each window and each run of columns sees in the block."""

    def __init__(self) -> None:
        self.windows: List[Tuple[GriddedPerm, Tuple[int, ...]]] = []
        self.window_patterns: DefaultDict[_WindowKey, Set[Perm]] = defaultdict(set)
        # each run's obstructions, each with its pattern in the block
        self.runs: DefaultDict[Tuple[int, int], Dict[GriddedPerm, Perm]] = defaultdict(
            dict
        )

    def add_window(
        self, obstruction: GriddedPerm, key: _WindowKey, pattern: Perm
    ) -> None:
        self.windows.append((obstruction, key.rows))
        self.window_patterns[key].add(pattern)

    def add_run(
        self, obstruction: GriddedPerm, span: Tuple[int, int], pattern: Perm
    ) -> None:
        self.runs[span][obstruction] = pattern

    def run_patterns(self, span: Tuple[int, int]) -> Set[Perm]:
        """The patterns of the run of the span of columns, none if it has none."""
        return set(self.runs[span].values()) if span in self.runs else set()


class _Analysis:
    """Why a block does not slide, or how it slides: the obstructions to regrid in
    the child, each with the columns and the rows of cells to regrid it over, and
    whether the slide is the identity."""

    def __init__(
        self,
        reason: Optional[str],
        rows: Tuple[int, ...] = tuple(),
        to_regrid: Sequence[
            Tuple[GriddedPerm, Tuple[int, ...], Tuple[int, ...]]
        ] = tuple(),
        identity: bool = False,
    ) -> None:
        self.reason = reason
        self.rows = rows
        self.to_regrid = tuple(to_regrid)
        self.identity = identity


class KnuthSlide:
    """
    The Knuth slides of a tiling's blocks of columns. A block is given by its first
    column and its width. For the slides of blocks of rows, use the inverse tiling.
    """

    def __init__(self, tiling: "Tiling") -> None:
        self._tiling = tiling
        self._obstruction_keys = frozenset(
            (obstruction.patt, obstruction.pos) for obstruction in tiling.obstructions
        )
        self._rows_of_column = _lines(tiling.active_cells)
        # a tiling that keeps an empty row or column would lose it in the child, and
        # the map's coordinates would no longer fit; searches never make one
        width, height = tiling.dimensions
        self._reduced = (
            len({x for x, _ in tiling.active_cells}) == width
            and len({y for _, y in tiling.active_cells}) == height
        )
        self._forbidden: Dict[Gridding, bool] = {}
        self._complete_families: Dict[Tuple, bool] = {}
        self._analyses: Dict[Tuple[int, int], _Analysis] = {}

    @staticmethod
    def has_blocks(
        tiling: "Tiling", transpose: bool = False, one_line_only: bool = False
    ) -> bool:
        """Could the tiling have a block of columns, or with transpose of rows? A
        cheap test, to avoid computing the inverse tiling for nothing."""
        cells = tiling.active_cells
        if transpose:
            cells = frozenset((y, x) for x, y in cells)
        lines = _lines(cells)
        return any(
            lines.get(x) == lines.get(x + 1)
            and (not one_line_only or len(lines[x]) == 1)
            for x in lines
        )

    def blocks(
        self, max_width: int = 3, one_line_only: bool = False
    ) -> Iterator[Tuple[int, int]]:
        """Yield every block (first column, width) of width 2 to max_width. With
        one_line_only, only blocks within one row of cells."""
        width = self._tiling.dimensions[0]
        start = 0
        while start < width:
            block_rows = self._rows_of_column.get(start)
            end = start + 1
            while end < width and self._rows_of_column.get(end) == block_rows:
                end += 1
            if block_rows and (not one_line_only or len(block_rows) == 1):
                for size in range(2, min(max_width, end - start) + 1):
                    for first in range(start, end - size + 1):
                        yield first, size
            start = end

    def why_not(self, column: int, width: int) -> Optional[str]:
        """Return None if the block slides, and otherwise why it does not."""
        return self._cached_analysis(column, width).reason

    def is_identity(self, column: int, width: int) -> bool:
        """Return True if the block slides and the patterns of each of its runs, and
        the requirements and assumptions, are the same with the block mirrored. Its
        window constraints are regridded over the whole block, so they are the same
        mirrored. The child is then the tiling itself, and the factory skips the
        slide without making the child."""
        analysis = self._cached_analysis(column, width)
        return analysis.reason is None and analysis.identity

    def slide(self, column: int, width: int) -> "Tiling":
        """Return the child of the slide of the block. Raise ValueError if the block
        does not slide (why_not)."""
        analysis = self._cached_analysis(column, width)
        if analysis.reason is not None:
            raise ValueError(f"the block does not slide: {analysis.reason}")
        block = _Block.of(column, width, analysis.rows)
        obstructions: Set[GriddedPerm] = {
            obstruction
            for obstruction in self._tiling.obstructions
            if not block.indices(obstruction)
        }
        for obstruction, columns, rows in analysis.to_regrid:
            obstructions.update(
                GriddedPerm(pattern, positions)
                for pattern, positions in _regriddings(
                    obstruction, block.indices(obstruction), columns, rows
                )
            )
        mirror = self.mirror(column, width)
        requirements = [
            [gridded_perm.apply_map(mirror) for gridded_perm in requirement]
            for requirement in self._tiling.requirements
        ]
        assumptions = [
            assumption.__class__(
                gridded_perm.apply_map(mirror) for gridded_perm in assumption.gps
            )
            for assumption in self._tiling.assumptions
        ]
        return self._tiling.__class__(obstructions, requirements, assumptions)

    @staticmethod
    def mirror(column: int, width: int) -> Callable[[Cell], Cell]:
        """Return the map of cells that mirrors the columns of the block of the width
        from the column, and keeps every other cell: with GriddedPerm.apply_map, it
        mirrors a requirement's or an assumption's point."""

        def mirrored(cell: Cell) -> Cell:
            x, y = cell
            if column <= x < column + width:
                return (_mirror_column(column, width, x), y)
            return cell

        return mirrored

    @staticmethod
    def slide_gridded_perm(
        gridded_perm: GriddedPerm, column: int, width: int
    ) -> GriddedPerm:
        """Return the image of a gridded permutation under the slide of the block of
        the width from the column. The slide is an involution."""
        indices = [
            i
            for i, (x, _) in enumerate(gridded_perm.pos)
            if column <= x < column + width
        ]
        if not indices:
            return gridded_perm
        word = [gridded_perm.patt[i] for i in indices]
        sizes = [0] * width
        for i in indices:
            sizes[gridded_perm.pos[i][0] - column] += 1
        row_of = {gridded_perm.patt[i]: gridded_perm.pos[i][1] for i in indices}
        new_word = evacuate_recording_tableau(word)
        columns = [
            column + offset
            for offset in range(width)
            for _ in range(sizes[width - 1 - offset])
        ]
        pattern = list(gridded_perm.patt)
        positions = list(gridded_perm.pos)
        for offset, i in enumerate(indices):
            pattern[i] = new_word[offset]
            positions[i] = (columns[offset], row_of[new_word[offset]])
        return GriddedPerm(Perm(pattern), positions)

    def _cached_analysis(self, column: int, width: int) -> _Analysis:
        key = (column, width)
        if key not in self._analyses:
            self._analyses[key] = self._analyze(column, width)
        return self._analyses[key]

    def _analyze(self, column: int, width: int) -> _Analysis:
        """Decide whether the block slides. No obstruction with points in the block
        may be contradictory, and each is the first of these that it can be:
        - a run constraint of its column: it lies in one column of the block, and
          every regridding there is forbidden, as it is when the block has one row;
        - a window constraint: no other point of it lies between its block points
          in value, and every regridding of them over the block's columns, in the
          rows they span, is forbidden;
        - a run constraint of the columns it spans: it lies in the block, and every
          regridding over those columns is forbidden.
        A constraint of one column, such as a cell's basis, is taken as a run of that
        column first: it then moves to the mirrored column, whose points the slide
        gives the RSK shape that this column's points had. One across columns is a
        window's when it can be, as a window needs only that its patterns be closed
        under Knuth moves, where a run needs them determined by the shape, a
        stronger condition. A run whose patterns are not determined by the shape
        leaves out those of its obstructions that are window constraints, which the
        windows hold already (_classify). Then the patterns of each run must
        be determined by the shape, those of each window must be closed under Knuth
        moves, and the requirements and assumptions must be on whole columns or whole
        rows of the block."""
        rows = self._rows_of_column.get(column, tuple())
        if (
            width < 2
            or not rows
            or any(
                self._rows_of_column.get(x) != rows
                for x in range(column, column + width)
            )
        ):
            return _Analysis("the columns are not a block")
        if not self._reduced:
            return _Analysis("the tiling has an empty row or column")
        block = _Block.of(column, width, rows)
        constraints = _Constraints()
        reason = (
            self._classify(constraints, block)
            or self._check_closures(constraints)
            or self._requirements_and_assumptions(block)
        )
        if reason is not None:
            return _Analysis(reason)
        identity = all(
            constraints.run_patterns(span)
            == constraints.run_patterns(_mirrored_span(column, width, span))
            for span in constraints.runs
        ) and self._symmetric(column, width)
        # a window is regridded over the block's columns, in the rows it spans, and
        # a run over the mirrored run, in all the block's rows
        to_regrid = [
            (obstruction, block.columns, window_rows)
            for obstruction, window_rows in constraints.windows
        ]
        for span, run in constraints.runs.items():
            low, high = _mirrored_span(column, width, span)
            mirrored_columns = tuple(range(low, high + 1))
            to_regrid.extend(
                (obstruction, mirrored_columns, block.rows) for obstruction in run
            )
        return _Analysis(None, rows, to_regrid, identity)

    def _classify(self, constraints: _Constraints, block: _Block) -> Optional[str]:
        """Put each obstruction with points in the block into the constraints, as
        _analyze says, or return why one does not fit. A run whose patterns are not
        determined by the shape then leaves out its window constraints."""
        rows = block.rows
        for obstruction in self._tiling.obstructions:
            indices = block.indices(obstruction)
            if not indices:
                continue
            # a gridding no gridded permutation has: it may be all that keeps a cell
            # of the block active, and it has no regriddings to keep it in the child
            if obstruction.contradictory():
                return "an obstruction with points in the block is contradictory"
            obstruction_columns = {obstruction.pos[i][0] for i in indices}
            low, high = min(obstruction_columns), max(obstruction_columns)
            inside = len(indices) == len(obstruction)
            if (
                inside
                and low == high
                and (
                    len(rows) == 1 or self._complete(obstruction, indices, (low,), rows)
                )
            ):
                constraints.add_run(obstruction, (low, low), block.pattern(obstruction))
                continue
            window_key = self._window_constraint_key(obstruction, indices, block)
            if window_key is not None:
                constraints.add_window(
                    obstruction, window_key, block.pattern(obstruction)
                )
            elif (
                inside
                and low < high
                and self._complete(
                    obstruction, indices, tuple(range(low, high + 1)), rows
                )
            ):
                constraints.add_run(
                    obstruction, (low, high), block.pattern(obstruction)
                )
            else:
                return "an obstruction depends on how the block's points are split"
        # A run whose patterns are not determined by the shape leaves out those of
        # its obstructions that are window constraints, as the windows hold them
        # already. Such an obstruction lies in one column. Its gridding with its last
        # point in the next column of the block, or its first point in the column
        # before, is forbidden, and as the tiling's obstructions are minimal, that
        # gridding is an obstruction itself, of the same pattern and the same rows:
        # a window constraint of the same window, whose regriddings are its own.
        for span, run in list(constraints.runs.items()):
            if not is_shape_closed(run.values()):
                constraints.runs[span] = {
                    obstruction: pattern
                    for obstruction, pattern in run.items()
                    if self._window_constraint_key(
                        obstruction, block.indices(obstruction), block
                    )
                    is None
                }
        return None

    @staticmethod
    def _check_closures(constraints: _Constraints) -> Optional[str]:
        """Return why the patterns of a run are not determined by the RSK shape, or
        why those of a window are not closed under Knuth moves; None if neither."""
        for run in constraints.runs.values():
            if not is_shape_closed(run.values()):
                return "a run's patterns are not determined by the RSK shape"
        for patterns in constraints.window_patterns.values():
            if not is_knuth_closed(patterns):
                return "a window's patterns are not closed under Knuth moves"
        return None

    def _window_constraint_key(
        self, obstruction: GriddedPerm, indices: Sequence[int], block: _Block
    ) -> Optional[_WindowKey]:
        """Return the window key of the obstruction if it is a window constraint,
        and None if it is not."""
        window_key = self._window_key(obstruction, indices, block.rows)
        if window_key is None or not self._complete(
            obstruction, indices, block.columns, window_key.rows
        ):
            return None
        return window_key

    def _symmetric(self, column: int, width: int) -> bool:
        """Are the requirements and assumptions the same with the block mirrored?"""
        mirror = self.mirror(column, width)
        requirements = {
            frozenset(requirement) for requirement in self._tiling.requirements
        }
        mirrored_requirements = {
            frozenset(gridded_perm.apply_map(mirror) for gridded_perm in requirement)
            for requirement in self._tiling.requirements
        }
        assumptions = {
            frozenset(assumption.gps) for assumption in self._tiling.assumptions
        }
        mirrored_assumptions = {
            frozenset(gridded_perm.apply_map(mirror) for gridded_perm in assumption.gps)
            for assumption in self._tiling.assumptions
        }
        return (
            requirements == mirrored_requirements
            and assumptions == mirrored_assumptions
        )

    def _requirements_and_assumptions(self, block: _Block) -> Optional[str]:
        """Return why a requirement or an assumption with points in the block is not
        on whole columns or whole rows of it, as points it counts; None if none is."""
        block_columns, rows = block.columns, block.rows
        for requirement in self._tiling.requirements:
            cells = _point_cells(requirement, block)
            if cells is None:
                return "a requirement other than points has points in the block"
            if cells and not _columns_or_rows(cells, block_columns, rows):
                return "a requirement is on part of a column of the block"
        for assumption in self._tiling.assumptions:
            cells = _point_cells(assumption.gps, block)
            if cells is None:
                return "an assumption on more than a point has points in the block"
            if not cells:
                continue
            # only plain TrackingAssumptions: the component assumptions, its
            # subclasses, count something the slide does not keep
            if assumption.__class__ is not TrackingAssumption:
                return "an assumption that does not count points covers the block"
            whole_columns = {(x, y) for x, _ in cells for y in rows}
            whole_rows = {(x, y) for _, y in cells for x in block_columns}
            if cells not in (whole_columns, whole_rows):
                return "an assumption covers part of the block's columns and rows"
        return None

    @staticmethod
    def _window_key(
        obstruction: GriddedPerm, indices: Sequence[int], rows: Tuple[int, ...]
    ) -> Optional[_WindowKey]:
        """The key of the window that the obstruction's block points, at the
        indices, form in the block's rows; None if a point of it outside the block
        lies between two of them in value."""
        inside = set(indices)
        values = [obstruction.patt[i] for i in indices]
        low, high = min(values), max(values)
        rest = [i for i in range(len(obstruction)) if i not in inside]
        if any(low < obstruction.patt[i] < high for i in rest):
            return None
        outside = tuple(Perm.to_standard([obstruction.patt[i] for i in rest]))
        below = sum(1 for i in rest if obstruction.patt[i] < low)
        block_rows = [obstruction.pos[i][1] for i in indices]
        lowest, highest = min(block_rows), max(block_rows)
        return _WindowKey(
            outside,
            tuple(obstruction.pos[i] for i in rest),
            below,
            tuple(y for y in rows if lowest <= y <= highest),
        )

    def _complete(
        self,
        obstruction: GriddedPerm,
        indices: Sequence[int],
        columns: Tuple[int, ...],
        rows: Tuple[int, ...],
    ) -> bool:
        """Is every regridding of the obstruction's block points over the cells of
        the columns and rows forbidden? The same for all its regriddings, so it is
        cached by their family."""
        inside = set(indices)
        family = (
            obstruction.patt,
            tuple(cell for i, cell in enumerate(obstruction.pos) if i not in inside),
            tuple(indices),
            columns,
            rows,
        )
        if family not in self._complete_families:
            self._complete_families[family] = all(
                self._is_forbidden(gridding)
                for gridding in _regriddings(obstruction, indices, columns, rows)
            )
        return self._complete_families[family]

    def _is_forbidden(self, gridding: Gridding) -> bool:
        if gridding in self._obstruction_keys:
            return True
        if gridding not in self._forbidden:
            self._forbidden[gridding] = GriddedPerm(*gridding).contains(
                *self._tiling.obstructions
            )
        return self._forbidden[gridding]


def _regriddings(
    obstruction: GriddedPerm,
    indices: Sequence[int],
    columns: Tuple[int, ...],
    rows: Tuple[int, ...],
) -> Iterator[Gridding]:
    """Yield every regridding of the obstruction's block points, at the indices,
    over the cells of the columns and rows, as (pattern, cells). The points keep
    their order: in columns, by position, and in rows, by value. The other points
    keep their cells.

    Each regridding is a valid gridding when the obstruction is not contradictory
    and each of its other points lies below all its block points, in value and in a
    row no higher than any of the rows, or above them all, in a row no lower than any
    of them. A window's obstructions are so, over the rows their block points span,
    and a run's have no other points."""
    pattern = obstruction.patt
    by_value = sorted(indices, key=lambda i: pattern[i])
    row_choices = list(combinations_with_replacement(rows, len(indices)))
    for column_sequence in combinations_with_replacement(columns, len(indices)):
        for row_sequence in row_choices:
            positions = list(obstruction.pos)
            row_of = dict(zip(by_value, row_sequence))
            for i, x in zip(indices, column_sequence):
                positions[i] = (x, row_of[i])
            yield pattern, tuple(positions)


def _mirrored_span(column: int, width: int, span: Tuple[int, int]) -> Tuple[int, int]:
    """The span of columns that the slide of the block of the width from the column
    takes the span of columns of the block to."""
    low, high = span
    return _mirror_column(column, width, high), _mirror_column(column, width, low)


def _point_cells(
    gridded_perms: Iterable[GriddedPerm], block: _Block
) -> Optional[Set[Cell]]:
    """The cells of those of the gridded permutations with points in the block, if
    each of those is a single point; None if one is not."""
    cells: Set[Cell] = set()
    for gridded_perm in gridded_perms:
        if not block.indices(gridded_perm):
            continue
        if len(gridded_perm) != 1:
            return None
        cells.add(gridded_perm.pos[0])
    return cells


def _lines(cells: Iterable[Cell]) -> Dict[int, Tuple[int, ...]]:
    """The rows of the active cells of each column."""
    rows: DefaultDict[int, Set[int]] = defaultdict(set)
    for x, y in cells:
        rows[x].add(y)
    return {x: tuple(sorted(column_rows)) for x, column_rows in rows.items()}


def _columns_or_rows(
    cells: Set[Cell], columns: Tuple[int, ...], rows: Tuple[int, ...]
) -> bool:
    """Are the cells those of some whole columns and some whole rows of the block?"""
    whole_columns = {x for x in columns if all((x, y) in cells for y in rows)}
    whole_rows = {y for y in rows if all((x, y) in cells for x in columns)}
    return cells == {
        (x, y) for x in columns for y in rows if x in whole_columns or y in whole_rows
    }

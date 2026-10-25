"""
The Knuth slide: a bijection between the gridded permutations of two tilings that
reverses a block of adjacent columns.

A block is a set of k >= 2 adjacent columns whose active cells are exactly the same
nonempty set of rows R in each column. The points of a gridded permutation in the
block form its block word w, the concatenation of the column words. The slide
replaces w by RSK^-1(P(w), evac(Q(w))), Permuta's evacuate_recording_tableau, and
reverses the columns: column c gets as many of the first letters as the last column
had, and so on, each value keeping its row.
The new word has the same insertion tableau, so on every interval of values it is
Knuth equivalent to the old one, and every run of adjacent columns gets the RSK shape
of its mirror image (Schutzenberger: evacuation is the recording tableau of the
reverse-complement).

So the slide is a bijection onto the gridded permutations of the child tiling when:

- every obstruction with points in the block is not contradictory, that is a
  gridding some gridded permutation can have, and is of window type or of run
  type.
    - Window type: no other point of it has a value between two of its block
      values, and every regridding of its block points over the block's columns,
      and over the block's rows from its lowest block row to its highest, is
      forbidden. For each configuration of the other points, the patterns that
      these obstructions see in the block must form a Knuth-closed set: one whose
      avoiders are closed under Knuth equivalence (Permuta's is_knuth_closed).
    - Run type: all its points are in the block, and every regridding over the run
      of columns it spans and all the block's rows is forbidden. For each run, the
      patterns must form a shape-closed set: one whose avoiders are determined by
      the RSK shape, such as a monotone pattern (Permuta's is_shape_closed).
- every requirement with points in the block is a list of points whose block cells
  are whole columns or whole rows of the block, or both;
- every assumption with points in the block counts points (TrackingAssumption), on
  whole columns of the block or on whole rows of it.

The child has the obstructions with no block points, every regridding of the window
type ones, the run type ones regridded over the mirrored runs, and the requirements
and assumptions with the block's columns mirrored. A block of one row is the Knuth
slide of adjacent cells; a block of several rows is its Ferrers version, after
Babson and West's sliding lemma.
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
        self.runs: DefaultDict[Tuple[int, int], List[GriddedPerm]] = defaultdict(list)
        self.run_patterns: DefaultDict[Tuple[int, int], Set[Perm]] = defaultdict(set)

    def add_window(
        self, obstruction: GriddedPerm, key: _WindowKey, pattern: Perm
    ) -> None:
        self.windows.append((obstruction, key.rows))
        self.window_patterns[key].add(pattern)

    def add_run(
        self, obstruction: GriddedPerm, span: Tuple[int, int], pattern: Perm
    ) -> None:
        self.runs[span].append(obstruction)
        self.run_patterns[span].add(pattern)


class _Analysis:
    """How a block's obstructions are classified, or why it does not slide."""

    def __init__(
        self,
        reason: Optional[str],
        rows: Tuple[int, ...] = tuple(),
        window: Sequence[Tuple[GriddedPerm, Tuple[int, ...]]] = tuple(),
        run: Sequence[Tuple[GriddedPerm, Tuple[int, int]]] = tuple(),
        identity: bool = False,
    ) -> None:
        self.reason = reason
        self.rows = rows
        self.window = tuple(window)
        self.run = tuple(run)
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
        tiling: "Tiling", transpose: bool = False, rows: bool = True
    ) -> bool:
        """Could the tiling have a block of columns, or with transpose of rows? A
        cheap test, to avoid computing the inverse tiling for nothing."""
        cells = tiling.active_cells
        if transpose:
            cells = frozenset((y, x) for x, y in cells)
        lines = _lines(cells)
        return any(
            lines.get(x) == lines.get(x + 1) and (rows or len(lines[x]) == 1)
            for x in lines
        )

    def blocks(
        self, max_width: int = 3, rows: bool = True
    ) -> Iterator[Tuple[int, int]]:
        """Yield every block (first column, width) of width 2 to max_width. With rows
        False, only blocks of one row."""
        width = self._tiling.dimensions[0]
        start = 0
        while start < width:
            block_rows = self._rows_of_column.get(start)
            end = start + 1
            while end < width and self._rows_of_column.get(end) == block_rows:
                end += 1
            if block_rows and (rows or len(block_rows) == 1):
                for size in range(2, min(max_width, end - start) + 1):
                    for first in range(start, end - size + 1):
                        yield first, size
            start = end

    def why_not(self, column: int, width: int) -> Optional[str]:
        """Return None if the block slides, and otherwise why it does not."""
        return self._analysis(column, width).reason

    def is_identity(self, column: int, width: int) -> bool:
        """Return True if the block slides and the patterns of each of its runs, and
        the requirements and assumptions, are the same with the block mirrored, as
        the window constraints always are: the child is then the tiling itself, and
        the factory skips the slide without making the child."""
        analysis = self._analysis(column, width)
        return analysis.reason is None and analysis.identity

    def slide(self, column: int, width: int) -> "Tiling":
        """Return the child of the slide of the block."""
        analysis = self._analysis(column, width)
        if analysis.reason is not None:
            raise ValueError(f"the block does not slide: {analysis.reason}")
        block_columns = tuple(range(column, column + width))
        block = frozenset((x, y) for x in block_columns for y in analysis.rows)
        obstructions: Set[GriddedPerm] = {
            obstruction
            for obstruction in self._tiling.obstructions
            if not _block_indices(obstruction, block)
        }
        for obstruction, rows in analysis.window:
            obstructions.update(
                GriddedPerm(pattern, positions)
                for pattern, positions in _regriddings(
                    obstruction, _block_indices(obstruction, block), block_columns, rows
                )
            )
        for obstruction, (low, high) in analysis.run:
            mirrored = tuple(
                range(2 * column + width - 1 - high, 2 * column + width - low)
            )
            obstructions.update(
                GriddedPerm(pattern, positions)
                for pattern, positions in _regriddings(
                    obstruction,
                    _block_indices(obstruction, block),
                    mirrored,
                    analysis.rows,
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
        last = column + width - 1

        def mirrored(cell: Cell) -> Cell:
            x, y = cell
            return (column + last - x, y) if column <= x <= last else cell

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

    def _analysis(self, column: int, width: int) -> _Analysis:
        key = (column, width)
        if key not in self._analyses:
            self._analyses[key] = self._analyze(column, width)
        return self._analyses[key]

    def _analyze(self, column: int, width: int) -> _Analysis:
        """Decide whether the block slides, choosing as the proof does. No
        obstruction with points in the block may be contradictory, and each is the
        first of these that it can be:
        - a run constraint of its column: it lies in one column of the block, and
          every regridding there is forbidden, as it is when the block has one row;
        - a window constraint: no other point of it lies between its block points
          in value, and every regridding of them over the block's columns, in the
          rows they span, is forbidden;
        - a run constraint of the columns it spans: it lies in the block, and every
          regridding over those columns is forbidden.
        A run whose patterns are not determined by the RSK shape gives the windows
        those of its obstructions that are window constraints. Then the patterns of
        each run must be determined by the shape, those of each window must be
        closed under Knuth moves, and the requirements and assumptions must be on
        whole columns or whole rows of the block."""
        block_columns = tuple(range(column, column + width))
        rows = self._rows_of_column.get(column, tuple())
        if (
            width < 2
            or not rows
            or any(self._rows_of_column.get(x) != rows for x in block_columns)
        ):
            return _Analysis("the columns are not a block")
        if not self._reduced:
            return _Analysis("the tiling has an empty row or column")
        block = frozenset((x, y) for x in block_columns for y in rows)
        constraints = _Constraints()
        reason = (
            self._classify(constraints, block_columns, rows, block)
            or self._closure(constraints, block_columns, rows, block)
            or self._requirements_and_assumptions(block_columns, rows, block)
        )
        if reason is not None:
            return _Analysis(reason)
        last = 2 * column + width - 1
        identity = all(
            patterns == constraints.run_patterns.get((last - high, last - low), set())
            for (low, high), patterns in constraints.run_patterns.items()
        ) and self._symmetric(column, width)
        return _Analysis(
            None,
            rows,
            constraints.windows,
            [
                (obstruction, span)
                for span, obstructions in constraints.runs.items()
                for obstruction in obstructions
            ],
            identity,
        )

    def _classify(
        self,
        constraints: _Constraints,
        block_columns: Tuple[int, ...],
        rows: Tuple[int, ...],
        block: FrozenSet[Cell],
    ) -> Optional[str]:
        """Put each obstruction with points in the block into the constraints, as
        _analyze says, or return why one does not fit."""
        for obstruction in self._tiling.obstructions:
            indices = _block_indices(obstruction, block)
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
                constraints.add_run(
                    obstruction,
                    (low, low),
                    obstruction.get_gridded_perm_in_cells(block).patt,
                )
                continue
            window_key = self._window(obstruction, indices, block_columns, rows)
            if window_key is not None:
                constraints.add_window(
                    obstruction,
                    window_key,
                    obstruction.get_gridded_perm_in_cells(block).patt,
                )
            elif (
                inside
                and low < high
                and self._complete(
                    obstruction, indices, tuple(range(low, high + 1)), rows
                )
            ):
                constraints.add_run(
                    obstruction,
                    (low, high),
                    obstruction.get_gridded_perm_in_cells(block).patt,
                )
            else:
                return "an obstruction depends on how the block's points are split"
        return None

    def _closure(
        self,
        constraints: _Constraints,
        block_columns: Tuple[int, ...],
        rows: Tuple[int, ...],
        block: FrozenSet[Cell],
    ) -> Optional[str]:
        """Return why the patterns of a run are not determined by the RSK shape, once
        the run has given the windows its window constraints, or why those of a
        window are not closed under Knuth moves; None if neither."""
        for span, patterns in list(constraints.run_patterns.items()):
            if is_shape_closed(patterns):
                continue
            kept: List[GriddedPerm] = []
            for obstruction in constraints.runs[span]:
                indices = _block_indices(obstruction, block)
                window_key = self._window(obstruction, indices, block_columns, rows)
                if window_key is None:
                    kept.append(obstruction)
                else:
                    constraints.add_window(
                        obstruction,
                        window_key,
                        obstruction.get_gridded_perm_in_cells(block).patt,
                    )
            constraints.runs[span] = kept
            constraints.run_patterns[span] = {
                obstruction.get_gridded_perm_in_cells(block).patt
                for obstruction in kept
            }
            if not is_shape_closed(constraints.run_patterns[span]):
                return "a run's patterns are not determined by the RSK shape"
        for patterns in constraints.window_patterns.values():
            if not is_knuth_closed(patterns):
                return "a window's patterns are not closed under Knuth moves"
        return None

    def _window(
        self,
        obstruction: GriddedPerm,
        indices: Sequence[int],
        block_columns: Tuple[int, ...],
        rows: Tuple[int, ...],
    ) -> Optional[_WindowKey]:
        """The window key of the obstruction if it is a window constraint, and None
        if it is not."""
        window_key = self._window_key(obstruction, indices, rows)
        if window_key is None or not self._complete(
            obstruction, indices, block_columns, window_key.rows
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

    def _requirements_and_assumptions(
        self,
        block_columns: Tuple[int, ...],
        rows: Tuple[int, ...],
        block: FrozenSet[Cell],
    ) -> Optional[str]:
        """Return why a requirement or an assumption with points in the block is not
        on whole columns or whole rows of it, as points it counts; None if none is."""
        for requirement in self._tiling.requirements:
            cells = set()
            for gridded_perm in requirement:
                if not _block_indices(gridded_perm, block):
                    continue
                if len(gridded_perm) != 1:
                    return "a requirement other than points has points in the block"
                cells.add(gridded_perm.pos[0])
            if cells and not _columns_or_rows(cells, block_columns, rows):
                return "a requirement is on part of a column of the block"
        for assumption in self._tiling.assumptions:
            cells = set()
            for gridded_perm in assumption.gps:
                if not _block_indices(gridded_perm, block):
                    continue
                if len(gridded_perm) != 1:
                    return "an assumption on more than a point has points in the block"
                cells.add(gridded_perm.pos[0])
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
    """Every regridding, as (pattern, cells), of the obstruction's block points, at
    the indices and consecutive in position, over the cells of the columns and rows,
    in the order of their positions and of their values; the other points keep their
    cells. Each is a valid gridding when the obstruction is not contradictory and
    each of its other points is below all its block points in value and in a row no
    higher than any of the rows, or above them all and in a row no lower: as a
    window's obstructions are, over the rows their block points span, and a run's,
    which have no other points."""
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


def _block_indices(gridded_perm: GriddedPerm, block: FrozenSet[Cell]) -> List[int]:
    """The indices of the gridded permutation's points in the block."""
    return [i for i, cell in enumerate(gridded_perm.pos) if cell in block]

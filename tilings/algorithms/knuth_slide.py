"""
The Knuth slide: a bijection between the gridded permutations of two tilings that
reverses a block of adjacent columns.

A block is a set of k >= 2 adjacent columns whose active cells are exactly the same
nonempty set of rows R in each column. The points of a gridded permutation in the
block form its block word w, the concatenation of the column words. The slide
replaces w by RSK^-1(P(w), evac(Q(w))) and reverses the columns: column c gets as many
of the first letters as the last column had, and so on, each value keeping its row.
The new word has the same insertion tableau, so on every interval of values it is
Knuth equivalent to the old one, and every run of adjacent columns gets the RSK shape
of its mirror image (Schutzenberger: evacuation is the recording tableau of the
reverse-complement).

So the slide is a bijection onto the gridded permutations of the child tiling when:

- every obstruction with points in the block is of window type or of run type.
    - Window type: no other point of it has a value between two of its block
      values, and every regridding of its block points over the block's columns,
      and over the block's rows from its lowest block row to its highest, is
      forbidden. For each configuration of the other points, the patterns that
      these obstructions see in the block must form a Knuth-closed set: one whose
      avoiders are closed under Knuth equivalence.
    - Run type: all its points are in the block, and every regridding over the run
      of columns it spans and all the block's rows is forbidden. For each run, the
      patterns must form a shape-closed set: one whose avoiders are determined by
      the RSK shape, such as a monotone pattern.
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

from bisect import bisect_left
from collections import defaultdict
from functools import lru_cache
from itertools import combinations_with_replacement
from typing import (
    TYPE_CHECKING,
    DefaultDict,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
)

from permuta import Perm
from tilings.assumptions import TrackingAssumption
from tilings.griddedperm import GriddedPerm

if TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from tilings import Tiling

__all__ = [
    "KnuthSlide",
    "evacuation",
    "is_knuth_closed",
    "is_shape_closed",
    "knuth_slide_word",
    "rsk",
    "rsk_inverse",
]

Cell = Tuple[int, int]
Tableau = List[List[int]]
Gridding = Tuple[Perm, Tuple[Cell, ...]]
WindowKey = Tuple[Tuple[int, ...], Tuple[Cell, ...], int, Tuple[int, ...]]


def rsk(word: Sequence[int]) -> Tuple[Tableau, Tableau]:
    """Return the insertion and recording tableaux of a word of distinct letters,
    by row insertion."""
    insertion_tableau: Tableau = []
    recording_tableau: Tableau = []
    for step, letter in enumerate(word, 1):
        for insertion_row, recording_row in zip(insertion_tableau, recording_tableau):
            position = bisect_left(insertion_row, letter)
            if position == len(insertion_row):
                insertion_row.append(letter)
                recording_row.append(step)
                break
            letter, insertion_row[position] = insertion_row[position], letter
        else:
            insertion_tableau.append([letter])
            recording_tableau.append([step])
    return insertion_tableau, recording_tableau


def rsk_inverse(
    insertion_tableau: Sequence[Sequence[int]],
    recording_tableau: Sequence[Sequence[int]],
) -> List[int]:
    """Return the word whose insertion and recording tableaux are the given ones, of
    the same shape, the recording tableau standard."""
    insertion_rows = [list(row) for row in insertion_tableau]
    recording_rows = [list(row) for row in recording_tableau]
    row_of = {
        step: row_index for row_index, row in enumerate(recording_rows) for step in row
    }
    word = [0] * len(row_of)
    for step in range(len(word), 0, -1):
        row_index = row_of[step]
        recording_rows[row_index].pop()
        letter = insertion_rows[row_index].pop()
        for upper in range(row_index - 1, -1, -1):
            insertion_row = insertion_rows[upper]
            position = bisect_left(insertion_row, letter) - 1
            letter, insertion_row[position] = insertion_row[position], letter
        word[step - 1] = letter
    return word


def evacuation(tableau: Sequence[Sequence[int]]) -> Tableau:
    """Return Schutzenberger's evacuation of a standard Young tableau: delete the
    smallest entry and slide the hole out by jeu de taquin, n times, writing n, n - 1,
    ... in the cells vacated."""
    current = [list(row) for row in tableau]
    result: Tableau = [[0] * len(row) for row in current]
    size = sum(len(row) for row in current)
    for label in range(size, 0, -1):
        row, column = 0, 0
        while True:
            right = current[row][column + 1] if column + 1 < len(current[row]) else None
            below = (
                current[row + 1][column]
                if row + 1 < len(current) and column < len(current[row + 1])
                else None
            )
            if right is None and below is None:
                break
            if below is None or (right is not None and right < below):
                assert right is not None
                current[row][column] = right
                column += 1
            else:
                assert below is not None
                current[row][column] = below
                row += 1
        current[row].pop()
        if not current[row]:
            current.pop()
        result[row][column] = label
    return result


def knuth_slide_word(word: Sequence[int]) -> List[int]:
    """Return RSK^-1(P(w), evac(Q(w))) for the word w of distinct letters: it has the
    same insertion tableau, and its factor at positions m + 1 - j to m + 1 - i has
    the RSK shape of w's factor at positions i to j. It is an involution."""
    insertion_tableau, recording_tableau = rsk(word)
    return rsk_inverse(insertion_tableau, evacuation(recording_tableau))


def _knuth_neighbours(perm: Perm) -> Iterator[Perm]:
    """Yield the permutations one elementary Knuth move from perm: y z x <-> y x z and
    x z y <-> z x y, for x < y < z."""
    word = list(perm)
    for i in range(len(word) - 2):
        first, second, third = word[i], word[i + 1], word[i + 2]
        if min(second, third) < first < max(second, third):
            yield Perm(word[: i + 1] + [third, second] + word[i + 3 :])
        if min(first, second) < third < max(first, second):
            yield Perm(word[:i] + [second, first] + word[i + 2 :])


def _containers(pattern: Perm) -> Set[Perm]:
    """The pattern itself and the permutations one entry longer that contain it."""
    containers = {pattern}
    for index in range(len(pattern) + 1):
        for value in range(len(pattern) + 1):
            containers.add(pattern.insert(index, value))
    return containers


@lru_cache(maxsize=1 << 16)
def is_knuth_closed(patterns: FrozenSet[Perm]) -> bool:
    """Return True if the permutations avoiding every pattern in patts are closed
    under Knuth equivalence. It is decided locally: an occurrence that a Knuth move
    destroys uses both letters it swaps, and with the letter that allows the move
    it lies in a permutation at most one entry longer than the pattern."""
    basis = tuple(patterns)
    return not any(
        neighbour.avoids(*basis)
        for pattern in basis
        for container in _containers(pattern)
        for neighbour in _knuth_neighbours(container)
    )


@lru_cache(maxsize=1 << 16)
def is_shape_closed(patterns: FrozenSet[Perm]) -> bool:
    """Return True if whether a permutation avoids patts depends only on its RSK
    shape: the patterns and their inverses are both Knuth-closed. Monotone patterns
    are."""
    return is_knuth_closed(patterns) and is_knuth_closed(
        frozenset(pattern.inverse() for pattern in patterns)
    )


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
        """Is the slide's child the tiling itself? True when the block slides and its
        constraints, requirements and assumptions are symmetric under the mirror."""
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
        requirements = [
            [mirror_gp(gridded_perm, column, width) for gridded_perm in requirement]
            for requirement in self._tiling.requirements
        ]
        assumptions = [
            assumption.__class__(
                mirror_gp(gridded_perm, column, width)
                for gridded_perm in assumption.gps
            )
            for assumption in self._tiling.assumptions
        ]
        return self._tiling.__class__(obstructions, requirements, assumptions)

    @staticmethod
    def slide_gp(gridded_perm: GriddedPerm, column: int, width: int) -> GriddedPerm:
        """Return the image of a gridded permutation under the slide of the block
        (col, width). The slide is an involution."""
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
        new_word = knuth_slide_word(word)
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
            self._analyses[key] = self._analyse(column, width)
        return self._analyses[key]

    # pylint: disable=too-many-locals,too-many-branches,too-many-return-statements
    def _analyse(self, column: int, width: int) -> _Analysis:
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
        window_groups: DefaultDict[WindowKey, Set[Perm]] = defaultdict(set)
        window: List[Tuple[GriddedPerm, Tuple[int, ...]]] = []
        run_groups: DefaultDict[Tuple[int, int], Set[Perm]] = defaultdict(set)
        run: DefaultDict[Tuple[int, int], List[GriddedPerm]] = defaultdict(list)
        for obstruction in self._tiling.obstructions:
            indices = _block_indices(obstruction, block)
            if not indices:
                continue
            # a gridding no gridded permutation has: it may be all that keeps a cell
            # of the block active, and it has no regriddings to keep it in the child
            if obstruction.contradictory():
                return _Analysis(
                    "an obstruction with points in the block is contradictory"
                )
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
                run_groups[(low, low)].add(_pattern(obstruction, indices))
                run[(low, low)].append(obstruction)
                continue
            window_key = self._window_key(obstruction, indices, rows)
            if window_key is not None and self._complete(
                obstruction, indices, block_columns, window_key[3]
            ):
                window_groups[window_key].add(_pattern(obstruction, indices))
                window.append((obstruction, window_key[3]))
                continue
            if (
                inside
                and low < high
                and self._complete(
                    obstruction, indices, tuple(range(low, high + 1)), rows
                )
            ):
                run_groups[(low, high)].add(_pattern(obstruction, indices))
                run[(low, high)].append(obstruction)
                continue
            return _Analysis(
                "an obstruction depends on how the block's points are split"
            )
        for span in list(run_groups):
            if is_shape_closed(frozenset(run_groups[span])):
                continue
            # what is not shape-closed in a column may still be a window constraint
            kept: List[GriddedPerm] = []
            for obstruction in run[span]:
                indices = _block_indices(obstruction, block)
                window_key = self._window_key(obstruction, indices, rows)
                if window_key is not None and self._complete(
                    obstruction, indices, block_columns, window_key[3]
                ):
                    window_groups[window_key].add(_pattern(obstruction, indices))
                    window.append((obstruction, window_key[3]))
                else:
                    kept.append(obstruction)
            run[span] = kept
            run_groups[span] = {
                _pattern(obstruction, _block_indices(obstruction, block))
                for obstruction in kept
            }
            if not is_shape_closed(frozenset(run_groups[span])):
                return _Analysis("a run's patterns are not determined by the RSK shape")
        for patterns in window_groups.values():
            if not is_knuth_closed(frozenset(patterns)):
                return _Analysis("a window's patterns are not closed under Knuth moves")
        reason = self._requirements_and_assumptions(block_columns, rows, block)
        if reason is not None:
            return _Analysis(reason)
        last = 2 * column + width - 1
        identity = all(
            patterns == run_groups.get((last - high, last - low), set())
            for (low, high), patterns in run_groups.items()
        ) and self._symmetric(column, width)
        return _Analysis(
            None,
            rows,
            window,
            [
                (obstruction, span)
                for span, obstructions in run.items()
                for obstruction in obstructions
            ],
            identity,
        )

    def _symmetric(self, column: int, width: int) -> bool:
        """Are the requirements and assumptions the same with the block mirrored?"""
        requirements = {
            frozenset(requirement) for requirement in self._tiling.requirements
        }
        mirrored_requirements = {
            frozenset(
                mirror_gp(gridded_perm, column, width) for gridded_perm in requirement
            )
            for requirement in self._tiling.requirements
        }
        assumptions = {
            frozenset(assumption.gps) for assumption in self._tiling.assumptions
        }
        mirrored_assumptions = {
            frozenset(
                mirror_gp(gridded_perm, column, width)
                for gridded_perm in assumption.gps
            )
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
    ) -> Optional[WindowKey]:
        """The obstruction's points outside the block, how many of them lie below
        the block points, and the block rows its block points span; None if a point
        outside lies between two block points in value."""
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
        return (
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
        """Is every regridding of the obstruction's block points over the cells
        cols x rows forbidden? The same for all its regriddings, so it is cached by
        their family."""
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


def mirror_gp(gridded_perm: GriddedPerm, column: int, width: int) -> GriddedPerm:
    """Mirror the block's columns in a gridded permutation with at most one point
    in the block (a requirement's or an assumption's point)."""
    if not any(column <= x < column + width for x, _ in gridded_perm.pos):
        return gridded_perm
    return GriddedPerm(
        gridded_perm.patt,
        (
            (2 * column + width - 1 - x, y) if column <= x < column + width else (x, y)
            for x, y in gridded_perm.pos
        ),
    )


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
    return [i for i, cell in enumerate(gridded_perm.pos) if cell in block]


def _pattern(gridded_perm: GriddedPerm, indices: Iterable[int]) -> Perm:
    return Perm.to_standard([gridded_perm.patt[i] for i in indices])

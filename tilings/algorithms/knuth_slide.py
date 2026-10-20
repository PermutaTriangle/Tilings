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
    p_tab: Tableau = []
    q_tab: Tableau = []
    for step, letter in enumerate(word, 1):
        for p_row, q_row in zip(p_tab, q_tab):
            idx = bisect_left(p_row, letter)
            if idx == len(p_row):
                p_row.append(letter)
                q_row.append(step)
                break
            letter, p_row[idx] = p_row[idx], letter
        else:
            p_tab.append([letter])
            q_tab.append([step])
    return p_tab, q_tab


def rsk_inverse(
    p_tab: Sequence[Sequence[int]], q_tab: Sequence[Sequence[int]]
) -> List[int]:
    """Return the word whose insertion and recording tableaux are the given ones, of
    the same shape, the recording tableau standard."""
    p_rows = [list(row) for row in p_tab]
    q_rows = [list(row) for row in q_tab]
    row_of = {step: r for r, row in enumerate(q_rows) for step in row}
    word = [0] * len(row_of)
    for step in range(len(word), 0, -1):
        row = row_of[step]
        q_rows[row].pop()
        letter = p_rows[row].pop()
        for upper in range(row - 1, -1, -1):
            p_row = p_rows[upper]
            idx = bisect_left(p_row, letter) - 1
            letter, p_row[idx] = p_row[idx], letter
        word[step - 1] = letter
    return word


def evacuation(tab: Sequence[Sequence[int]]) -> Tableau:
    """Return Schutzenberger's evacuation of a standard Young tableau: delete the
    smallest entry and slide the hole out by jeu de taquin, n times, writing n, n - 1,
    ... in the cells vacated."""
    current = [list(row) for row in tab]
    result: Tableau = [[0] * len(row) for row in current]
    size = sum(len(row) for row in current)
    for label in range(size, 0, -1):
        row, col = 0, 0
        while True:
            right = current[row][col + 1] if col + 1 < len(current[row]) else None
            below = (
                current[row + 1][col]
                if row + 1 < len(current) and col < len(current[row + 1])
                else None
            )
            if right is None and below is None:
                break
            if below is None or (right is not None and right < below):
                assert right is not None
                current[row][col] = right
                col += 1
            else:
                assert below is not None
                current[row][col] = below
                row += 1
        current[row].pop()
        if not current[row]:
            current.pop()
        result[row][col] = label
    return result


def knuth_slide_word(word: Sequence[int]) -> List[int]:
    """Return RSK^-1(P(w), evac(Q(w))) for the word w of distinct letters: it has the
    same insertion tableau, and its factor at positions m + 1 - j to m + 1 - i has
    the RSK shape of w's factor at positions i to j. It is an involution."""
    p_tab, q_tab = rsk(word)
    return rsk_inverse(p_tab, evacuation(q_tab))


def _knuth_neighbours(perm: Perm) -> Iterator[Perm]:
    """Yield the permutations one elementary Knuth move from perm: y z x <-> y x z and
    x z y <-> z x y, for x < y < z."""
    word = list(perm)
    for i in range(len(word) - 2):
        a, b, c = word[i], word[i + 1], word[i + 2]
        if min(b, c) < a < max(b, c):
            yield Perm(word[: i + 1] + [c, b] + word[i + 3 :])
        if min(a, b) < c < max(a, b):
            yield Perm(word[:i] + [b, a] + word[i + 2 :])


def _containers(patt: Perm) -> Set[Perm]:
    """The pattern itself and the permutations one entry longer that contain it."""
    out = {patt}
    for index in range(len(patt) + 1):
        for value in range(len(patt) + 1):
            out.add(patt.insert(index, value))
    return out


@lru_cache(maxsize=1 << 16)
def is_knuth_closed(patts: FrozenSet[Perm]) -> bool:
    """Return True if the permutations avoiding every pattern in patts are closed
    under Knuth equivalence. It is decided locally: an occurrence that a Knuth move
    destroys uses both letters it swaps, and with the letter that allows the move
    it lies in a permutation at most one entry longer than the pattern."""
    basis = tuple(patts)
    return not any(
        neighbour.avoids(*basis)
        for patt in basis
        for container in _containers(patt)
        for neighbour in _knuth_neighbours(container)
    )


@lru_cache(maxsize=1 << 16)
def is_shape_closed(patts: FrozenSet[Perm]) -> bool:
    """Return True if whether a permutation avoids patts depends only on its RSK
    shape: the patterns and their inverses are both Knuth-closed. Monotone patterns
    are."""
    return is_knuth_closed(patts) and is_knuth_closed(
        frozenset(patt.inverse() for patt in patts)
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
            (ob.patt, ob.pos) for ob in tiling.obstructions
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

    def why_not(self, col: int, width: int) -> Optional[str]:
        """Return None if the block slides, and otherwise why it does not."""
        return self._analysis(col, width).reason

    def is_identity(self, col: int, width: int) -> bool:
        """Is the slide's child the tiling itself? True when the block slides and its
        constraints, requirements and assumptions are symmetric under the mirror."""
        analysis = self._analysis(col, width)
        return analysis.reason is None and analysis.identity

    def slide(self, col: int, width: int) -> "Tiling":
        """Return the child of the slide of the block."""
        analysis = self._analysis(col, width)
        if analysis.reason is not None:
            raise ValueError(f"the block does not slide: {analysis.reason}")
        cols = tuple(range(col, col + width))
        block = frozenset((x, y) for x in cols for y in analysis.rows)
        obstructions: Set[GriddedPerm] = {
            ob for ob in self._tiling.obstructions if not _block_indices(ob, block)
        }
        for ob, rows in analysis.window:
            obstructions.update(
                GriddedPerm(patt, pos)
                for patt, pos in _regriddings(ob, _block_indices(ob, block), cols, rows)
            )
        for ob, (low, high) in analysis.run:
            mirrored = tuple(range(2 * col + width - 1 - high, 2 * col + width - low))
            obstructions.update(
                GriddedPerm(patt, pos)
                for patt, pos in _regriddings(
                    ob, _block_indices(ob, block), mirrored, analysis.rows
                )
            )
        requirements = [
            [mirror_gp(gp, col, width) for gp in req]
            for req in self._tiling.requirements
        ]
        assumptions = [
            ass.__class__(mirror_gp(gp, col, width) for gp in ass.gps)
            for ass in self._tiling.assumptions
        ]
        return self._tiling.__class__(obstructions, requirements, assumptions)

    @staticmethod
    def slide_gp(gp: GriddedPerm, col: int, width: int) -> GriddedPerm:
        """Return the image of a gridded permutation under the slide of the block
        (col, width). The slide is an involution."""
        idx = [i for i, (x, _) in enumerate(gp.pos) if col <= x < col + width]
        if not idx:
            return gp
        word = [gp.patt[i] for i in idx]
        sizes = [0] * width
        for i in idx:
            sizes[gp.pos[i][0] - col] += 1
        row_of = {gp.patt[i]: gp.pos[i][1] for i in idx}
        new_word = knuth_slide_word(word)
        columns = [col + t for t in range(width) for _ in range(sizes[width - 1 - t])]
        patt = list(gp.patt)
        pos = list(gp.pos)
        for t, i in enumerate(idx):
            patt[i] = new_word[t]
            pos[i] = (columns[t], row_of[new_word[t]])
        return GriddedPerm(Perm(patt), pos)

    def _analysis(self, col: int, width: int) -> _Analysis:
        key = (col, width)
        if key not in self._analyses:
            self._analyses[key] = self._analyse(col, width)
        return self._analyses[key]

    # pylint: disable=too-many-locals,too-many-branches,too-many-return-statements
    def _analyse(self, col: int, width: int) -> _Analysis:
        cols = tuple(range(col, col + width))
        rows = self._rows_of_column.get(col, tuple())
        if (
            width < 2
            or not rows
            or any(self._rows_of_column.get(x) != rows for x in cols)
        ):
            return _Analysis("the columns are not a block")
        if not self._reduced:
            return _Analysis("the tiling has an empty row or column")
        block = frozenset((x, y) for x in cols for y in rows)
        window_groups: DefaultDict[WindowKey, Set[Perm]] = defaultdict(set)
        window: List[Tuple[GriddedPerm, Tuple[int, ...]]] = []
        run_groups: DefaultDict[Tuple[int, int], Set[Perm]] = defaultdict(set)
        run: DefaultDict[Tuple[int, int], List[GriddedPerm]] = defaultdict(list)
        for ob in self._tiling.obstructions:
            idx = _block_indices(ob, block)
            if not idx:
                continue
            columns = {ob.pos[i][0] for i in idx}
            low, high = min(columns), max(columns)
            inside = len(idx) == len(ob)
            if (
                inside
                and low == high
                and (len(rows) == 1 or self._complete(ob, idx, (low,), rows))
            ):
                run_groups[(low, low)].add(_pattern(ob, idx))
                run[(low, low)].append(ob)
                continue
            key = self._window_key(ob, idx, rows)
            if key is not None and self._complete(ob, idx, cols, key[3]):
                window_groups[key].add(_pattern(ob, idx))
                window.append((ob, key[3]))
                continue
            if (
                inside
                and low < high
                and self._complete(ob, idx, tuple(range(low, high + 1)), rows)
            ):
                run_groups[(low, high)].add(_pattern(ob, idx))
                run[(low, high)].append(ob)
                continue
            return _Analysis(
                "an obstruction depends on how the block's points are split"
            )
        for span in list(run_groups):
            if is_shape_closed(frozenset(run_groups[span])):
                continue
            # what is not shape-closed in a column may still be a window constraint
            kept: List[GriddedPerm] = []
            for ob in run[span]:
                idx = _block_indices(ob, block)
                key = self._window_key(ob, idx, rows)
                if key is not None and self._complete(ob, idx, cols, key[3]):
                    window_groups[key].add(_pattern(ob, idx))
                    window.append((ob, key[3]))
                else:
                    kept.append(ob)
            run[span] = kept
            run_groups[span] = {_pattern(ob, _block_indices(ob, block)) for ob in kept}
            if not is_shape_closed(frozenset(run_groups[span])):
                return _Analysis("a run's patterns are not determined by the RSK shape")
        for patts in window_groups.values():
            if not is_knuth_closed(frozenset(patts)):
                return _Analysis("a window's patterns are not closed under Knuth moves")
        reason = self._requirements_and_assumptions(cols, rows, block)
        if reason is not None:
            return _Analysis(reason)
        last = 2 * col + width - 1
        identity = all(
            patts == run_groups.get((last - high, last - low), set())
            for (low, high), patts in run_groups.items()
        ) and self._symmetric(col, width)
        return _Analysis(
            None,
            rows,
            window,
            [(ob, span) for span, obs in run.items() for ob in obs],
            identity,
        )

    def _symmetric(self, col: int, width: int) -> bool:
        """Are the requirements and assumptions the same with the block mirrored?"""
        reqs = {frozenset(req) for req in self._tiling.requirements}
        mirrored_reqs = {
            frozenset(mirror_gp(gp, col, width) for gp in req)
            for req in self._tiling.requirements
        }
        asss = {frozenset(ass.gps) for ass in self._tiling.assumptions}
        mirrored_asss = {
            frozenset(mirror_gp(gp, col, width) for gp in ass.gps)
            for ass in self._tiling.assumptions
        }
        return reqs == mirrored_reqs and asss == mirrored_asss

    def _requirements_and_assumptions(
        self, cols: Tuple[int, ...], rows: Tuple[int, ...], block: FrozenSet[Cell]
    ) -> Optional[str]:
        for req in self._tiling.requirements:
            cells = set()
            for gp in req:
                if not _block_indices(gp, block):
                    continue
                if len(gp) != 1:
                    return "a requirement other than points has points in the block"
                cells.add(gp.pos[0])
            if cells and not _columns_or_rows(cells, cols, rows):
                return "a requirement is on part of a column of the block"
        for ass in self._tiling.assumptions:
            cells = set()
            for gp in ass.gps:
                if not _block_indices(gp, block):
                    continue
                if len(gp) != 1:
                    return "an assumption on more than a point has points in the block"
                cells.add(gp.pos[0])
            if not cells:
                continue
            # only plain TrackingAssumptions: the component assumptions, its
            # subclasses, count something the slide does not keep
            if ass.__class__ is not TrackingAssumption:
                return "an assumption that does not count points covers the block"
            whole_columns = {(x, y) for x, _ in cells for y in rows}
            whole_rows = {(x, y) for _, y in cells for x in cols}
            if cells not in (whole_columns, whole_rows):
                return "an assumption covers part of the block's columns and rows"
        return None

    @staticmethod
    def _window_key(
        ob: GriddedPerm, idx: Sequence[int], rows: Tuple[int, ...]
    ) -> Optional[WindowKey]:
        """The obstruction's points outside the block, how many of them lie below
        the block points, and the block rows its block points span; None if a point
        outside lies between two block points in value."""
        inside = set(idx)
        values = [ob.patt[i] for i in idx]
        low, high = min(values), max(values)
        rest = [i for i in range(len(ob)) if i not in inside]
        if any(low < ob.patt[i] < high for i in rest):
            return None
        outside = tuple(Perm.to_standard([ob.patt[i] for i in rest]))
        below = sum(1 for i in rest if ob.patt[i] < low)
        block_rows = [ob.pos[i][1] for i in idx]
        lowest, highest = min(block_rows), max(block_rows)
        return (
            outside,
            tuple(ob.pos[i] for i in rest),
            below,
            tuple(y for y in rows if lowest <= y <= highest),
        )

    def _complete(
        self,
        ob: GriddedPerm,
        idx: Sequence[int],
        cols: Tuple[int, ...],
        rows: Tuple[int, ...],
    ) -> bool:
        """Is every regridding of the obstruction's block points over the cells
        cols x rows forbidden? The same for all its regriddings, so it is cached by
        their family."""
        inside = set(idx)
        family = (
            ob.patt,
            tuple(cell for i, cell in enumerate(ob.pos) if i not in inside),
            tuple(idx),
            cols,
            rows,
        )
        if family not in self._complete_families:
            self._complete_families[family] = all(
                self._is_forbidden(gridding)
                for gridding in _regriddings(ob, idx, cols, rows)
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


def _regriddings(  # pylint: disable=too-many-locals
    ob: GriddedPerm,
    idx: Sequence[int],
    cols: Tuple[int, ...],
    rows: Tuple[int, ...],
) -> Iterator[Gridding]:
    """Every valid gridding, as (pattern, cells), with the obstruction's pattern and
    cells outside the block, and its block points (idx, consecutive in position) in
    the cells cols x rows."""
    patt = ob.patt
    inside = set(idx)
    rest = [i for i in range(len(ob)) if i not in inside]
    by_value = sorted(idx, key=lambda i: patt[i])
    lowest = {
        i: max((ob.pos[j][1] for j in rest if patt[j] < patt[i]), default=-1)
        for i in idx
    }
    highest = {
        i: min(
            (ob.pos[j][1] for j in rest if patt[j] > patt[i]),
            default=len(patt) + max(rows) + 1,
        )
        for i in idx
    }
    row_choices = [
        row_seq
        for row_seq in combinations_with_replacement(rows, len(idx))
        if all(lowest[i] <= y <= highest[i] for i, y in zip(by_value, row_seq))
    ]
    for col_seq in combinations_with_replacement(cols, len(idx)):
        for row_seq in row_choices:
            pos = list(ob.pos)
            row = dict(zip(by_value, row_seq))
            for i, x in zip(idx, col_seq):
                pos[i] = (x, row[i])
            yield patt, tuple(pos)


def _lines(cells: Iterable[Cell]) -> Dict[int, Tuple[int, ...]]:
    """The rows of the active cells of each column."""
    rows: DefaultDict[int, Set[int]] = defaultdict(set)
    for x, y in cells:
        rows[x].add(y)
    return {x: tuple(sorted(ys)) for x, ys in rows.items()}


def mirror_gp(gp: GriddedPerm, col: int, width: int) -> GriddedPerm:
    """Mirror the block's columns in a gridded permutation with at most one point
    in the block (a requirement's or an assumption's point)."""
    if not any(col <= x < col + width for x, _ in gp.pos):
        return gp
    return GriddedPerm(
        gp.patt,
        (
            (2 * col + width - 1 - x, y) if col <= x < col + width else (x, y)
            for x, y in gp.pos
        ),
    )


def _columns_or_rows(
    cells: Set[Cell], cols: Tuple[int, ...], rows: Tuple[int, ...]
) -> bool:
    """Are the cells those of some whole columns and some whole rows of the block?"""
    whole_columns = {x for x in cols if all((x, y) in cells for y in rows)}
    whole_rows = {y for y in rows if all((x, y) in cells for x in cols)}
    return cells == {
        (x, y) for x in cols for y in rows if x in whole_columns or y in whole_rows
    }


def _block_indices(gp: GriddedPerm, block: FrozenSet[Cell]) -> List[int]:
    return [i for i, cell in enumerate(gp.pos) if cell in block]


def _pattern(gp: GriddedPerm, idx: Iterable[int]) -> Perm:
    return Perm.to_standard([gp.patt[i] for i in idx])

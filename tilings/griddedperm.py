import json
from itertools import chain, combinations, islice, product, tee
from typing import Callable, Dict, FrozenSet, Iterable, Iterator, List, Optional, Tuple

from comb_spec_searcher import CombinatorialObject
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, HTMLViewer, UnionFind

Cell = Tuple[int, int]
Position = Tuple[Cell, ...]


class GriddedPerm(CombinatorialObject):
    def __init__(
        self, pattern: Iterable[int] = (), positions: Iterable[Cell] = ()
    ) -> None:
        self._patt = Perm(pattern)
        self._pos = tuple(positions)
        if len(self._patt) != len(self._pos):
            raise ValueError("Pattern and position list have unequal lengths.")
        self._cells: FrozenSet[Cell] = frozenset(self._pos)

    @classmethod
    def single_cell(cls, pattern: Iterable[int], cell: Cell) -> "GriddedPerm":
        """Construct a gridded permutation where the cells are all located in a
        single cell."""
        pattern = Perm(pattern)
        return cls(pattern, (cell for _ in range(len(pattern))))

    @classmethod
    def empty_perm(cls) -> "GriddedPerm":
        """Construct the empty gridded permutation."""
        return cls((), ())

    @classmethod
    def point_perm(cls, cell: Cell) -> "GriddedPerm":
        """Construct the point gridded permutation using the cell."""
        return cls((0,), (cell,))

    def contradictory(self) -> bool:
        """Checks if the points of the griddedperm contradict the permutation.

        Checks if for every 0 <= i < j < n
            patt[i] <= patt[j]
            if patt[i] < patt[j] then pos[i] <= pos[j]
            if patt[i] > patt[j] then pos[i] >= pos[j]
        """
        return any(
            (l_x > r_x or (l_v < r_v and l_y > r_y) or (l_v > r_v and l_y < r_y))
            for j, (r_v, (r_x, r_y)) in enumerate(self)
            for l_v, (l_x, l_y) in islice(self, j)
        )

    def occupies(self, cell: Cell) -> bool:
        """Checks if the gridded permutation has a point in the given cell."""
        return cell in self._cells

    def occurrences_in(self, other: "GriddedPerm") -> Iterator[Tuple[int, ...]]:
        """Returns all occurrences of self in other."""
        yield from self._patt.occurrences_in(other.patt, self.pos, other.pos)

    def occurs_in(self, other: "GriddedPerm") -> bool:
        """Checks if self occurs in other."""
        return any(self.occurrences_in(other))

    def avoids(self, *patts: "GriddedPerm") -> bool:
        """Return true if self avoids all of the patts."""
        return not self.contains(*patts)

    def contains(self, *patts: "GriddedPerm") -> bool:
        """Return true if self contains an occurrence of any of patts."""
        return any(any(True for _ in patt.occurrences_in(self)) for patt in patts)

    def remove_cells(self, cells: Iterable[Cell]) -> "GriddedPerm":
        """Remove any points in the cell given and return a new gridded
        permutation."""
        cells = set(cells)
        remaining = [i for i, (_, pos) in enumerate(self) if pos not in cells]
        return type(self)(
            Perm.to_standard(self._patt[i] for i in remaining),
            (self._pos[i] for i in remaining),
        )

    def points_in_cell(self, cell: Cell) -> Iterator[int]:
        """Yields the indices of the points in the cell given."""
        return (i for i, (_, pos) in enumerate(self) if pos == cell)

    def isolated_cells(self) -> Iterator[Cell]:
        """Yields the cells that contain only one point of the gridded
        permutation and are in their own row and column."""
        return (
            (x1, y1)
            for i, (_, (x1, y1)) in enumerate(self)
            if not any(
                x1 == x2 or y1 == y2 for j, (_, (x2, y2)) in enumerate(self) if i != j
            )
        )

    def is_isolated(self, indices: Iterable[int]) -> bool:
        """Checks if the cells at the indices do not share a row or column with
        any other cell in the gridded permutation."""
        indices = set(indices)
        return not any(
            x == self._pos[j][0] or y == self._pos[j][1]
            for j in indices
            for i, (_, (x, y)) in enumerate(self)
            if i not in indices
        )

    def forced_point_index(self, cell: Cell, direction: int) -> int:
        """Search in the cell given for the point with the strongest force with
        respect to the given force."""
        if self.occupies(cell):
            indices = self.points_in_cell(cell)
            if direction == DIR_EAST:
                return max(indices)
            if direction == DIR_NORTH:
                return max((self._patt[idx], idx) for idx in indices)[1]
            if direction == DIR_WEST:
                return min(indices)
            if direction == DIR_SOUTH:
                return min((self._patt[idx], idx) for idx in indices)[1]
            raise ValueError("You're lost, no valid direction")

    def forced_point_of_requirement(
        self, gps: Tuple["GriddedPerm", ...], indices: Tuple[int, ...], direction: int
    ) -> Optional[Tuple[int, int]]:
        """
        Return the pair (x, y) where x is the gridded perm in gps that is
        farthest in the given direction, and y is index of the forced point
        with respect to the gps and indices. If gps is avoided, then
        return None.
        """

        def directionmost(i1: int, i2: int) -> int:
            """return the directionmost between i1 and i2."""
            if direction == DIR_EAST:
                return max(i1, i2)
            if direction == DIR_NORTH:
                return max((self._patt[p], p) for p in (i1, i2))[1]
            if direction == DIR_WEST:
                return min(i1, i2)
            if direction == DIR_SOUTH:
                return min((self._patt[p], p) for p in (i1, i2))[1]
            raise ValueError("You're lost, no valid direction")

        res: Optional[Tuple[int, int]] = None
        for idx, gp in enumerate(gps):
            forced_index_in_patt = indices[idx]
            for occurrence in gp.occurrences_in(self):
                if res is None:
                    res = idx, occurrence[forced_index_in_patt]
                else:
                    new_res = directionmost(res[1], occurrence[forced_index_in_patt])
                    if res[1] != new_res:
                        res = idx, new_res
        return res

    def get_points_col(self, col: int) -> Iterator[Tuple[int, int]]:
        """Yields all points of the gridded permutation in the column col."""
        return ((i, val) for i, (val, (x, _)) in enumerate(self) if x == col)

    def get_points_row(self, row: int) -> Iterator[Tuple[int, int]]:
        """Yields all points of the gridded permutation in the row."""
        return ((i, val) for i, (val, (_, y)) in enumerate(self) if y == row)

    def get_points_below_row(self, row: int) -> Iterator[Tuple[int, int]]:
        """Yields all points of the gridded permutation below the row."""
        return ((i, val) for i, (val, (_, y)) in enumerate(self) if y < row)

    def get_points_above_row(self, row: int) -> Iterator[Tuple[int, int]]:
        """Yields all points of the gridded permutation above the row."""
        return ((i, val) for i, (val, (_, y)) in enumerate(self) if y > row)

    def get_points_left_col(self, col) -> Iterator[Tuple[int, int]]:
        """Yields all points of the gridded permutation left of column col."""
        return ((i, val) for i, (val, (x, _)) in enumerate(self) if x < col)

    def get_subperm_left_col(self, col: int) -> "GriddedPerm":
        """Returns the gridded subpermutation of points left of column col."""
        gen1, gen2 = tee((i for i, _ in self.get_points_left_col(col)), 2)
        return type(self)(
            Perm.to_standard(self.patt[i] for i in gen1), (self.pos[i] for i in gen2)
        )

    def get_points_right_col(self, col: int) -> Iterator[Tuple[int, int]]:
        """Yields all points of the gridded permutation right of column col."""
        return ((i, val) for i, (val, (x, _)) in enumerate(self) if x > col)

    def get_gridded_perm_at_indices(self, indices: Iterable[int]) -> "GriddedPerm":
        """
        Returns the subgridded perm that contains only the point at the given
        indices. Indices must be sorted.
        """
        gen1, gen2 = tee(indices, 2)
        return type(self)(
            Perm.to_standard(self.patt[i] for i in gen1),
            (self.pos[i] for i in gen2),
        )

    def get_gridded_perm_in_cells(self, cells: Iterable[Cell]) -> "GriddedPerm":
        """Returns the subgridded permutation of points in cells."""
        cells = set(cells)
        return type(self)(
            Perm.to_standard(val for val, pos in self if pos in cells),
            (pos for pos in self.pos if pos in cells),
        )

    def get_bounding_box(self, cell: Cell) -> Tuple[int, int, int, int]:
        """Determines the indices and values of the gridded permutation in
        which a point that is being inserted into the cell given."""
        row = list(self.get_points_row(cell[1]))
        col = list(self.get_points_col(cell[0]))
        if not row:
            above = list(self.get_points_above_row(cell[1]))
            if not above:
                maxval = len(self)
            else:
                maxval = min(p[1] for p in above)
            below = list(self.get_points_below_row(cell[1]))
            if not below:
                minval = 0
            else:
                minval = max(p[1] for p in below) + 1
        else:
            maxval = max(p[1] for p in row) + 1
            minval = min(p[1] for p in row)
        if not col:
            right = list(self.get_points_right_col(cell[0]))
            if not right:
                maxdex = len(self)
            else:
                maxdex = min(p[0] for p in right)
            left = list(self.get_points_left_col(cell[0]))
            if not left:
                mindex = 0
            else:
                mindex = max(p[0] for p in left) + 1
        else:
            maxdex = max(p[0] for p in col) + 1
            mindex = min(p[0] for p in col)
        return (mindex, maxdex, minval, maxval)

    def insert_point(self, cell: Cell) -> Iterator["GriddedPerm"]:
        """Insert a new point into cell of the gridded perm, such that the
        point is added to the underlying pattern with the position at the cell.
        Yields all gridded perms where the point has been mixed into the points
        in the cell."""
        mindex, maxdex, minval, maxval = self.get_bounding_box(cell)
        for idx, val in product(range(mindex, maxdex + 1), range(minval, maxval + 1)):
            yield self.insert_specific_point(cell, idx, val)

    def insert_specific_point(self, cell: Cell, idx: int, val: int) -> "GriddedPerm":
        """Insert a point in the given cell with the given idx and val."""
        return type(self)(
            self._patt.insert(idx, val), self._pos[:idx] + (cell,) + self._pos[idx:]
        )

    def remove_point(self, index: int) -> "GriddedPerm":
        """Remove the point at index from the gridded permutation."""
        patt = Perm.to_standard(self.patt[:index] + self.patt[index + 1 :])
        pos = self.pos[:index] + self.pos[index + 1 :]
        return type(self)(patt, pos)

    def all_subperms(self, proper: bool = True) -> Iterator["GriddedPerm"]:
        """Yields all gridded subpermutations."""
        for r in range(len(self) if proper else len(self) + 1):
            for subidx in combinations(range(len(self)), r):
                yield type(self)(
                    Perm.to_standard(self._patt[i] for i in subidx),
                    (self._pos[i] for i in subidx),
                )

    def extend(self, c: int, r: int) -> Iterator["GriddedPerm"]:
        """Add n+1 to all possible positions in perm and all allowed positions given that
        placement."""
        n = len(self)
        if n == 0:
            yield from (
                GriddedPerm((0,), ((x, y),)) for x in range(c) for y in range(r)
            )
        else:
            min_y = max(y for _, (_, y) in self)
            yield from (
                self.insert_specific_point((x, y), index, n)
                for index in range(n + 1)
                for x in range(
                    self.pos[index - 1][0] if index > 0 else 0,
                    self.pos[index][0] + 1 if index < n else c,
                )
                for y in range(min_y, r)
            )

    def apply_map(self, cell_mapping: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Map the coordinates to a new list of coordinates according to the
        cell_mapping given."""
        return type(self)(self._patt, [cell_mapping(cell) for cell in self._pos])

    def is_point_perm(self) -> bool:
        """Checks if the gridded permutation is of length 1."""
        return len(self) == 1

    def is_localized(self) -> bool:
        """Check if the gridded permutation occupies only a single cell."""
        return self.is_single_cell()

    def is_single_cell(self) -> bool:
        """Check if the gridded permutation occupies only a single cell."""
        return len(self._cells) == 1

    def is_single_row(self) -> bool:
        """Check if the gridded permutation occupies only a single row."""
        return len(set(y for (_, y) in self._cells)) == 1

    def is_empty(self) -> bool:
        """Check if the gridded permutation is the gridded permutation."""
        return not bool(self._patt)

    def is_interleaving(self) -> bool:
        """Check if the gridded permutation occupies two cells that are in the
        same row or column."""
        xs: Dict[int, int] = {}
        ys: Dict[int, int] = {}
        for x, y in self._cells:
            if xs.get(x, y) != y or ys.get(y, x) != x:
                return True
            xs[x] = y
            ys[y] = x
        return False

    def factors(self) -> List["GriddedPerm"]:
        """Return a list containing the factors of a gridded permutation.
        A factor is a sub gridded permutation that is isolated on its own rows
        and columns."""
        uf = UnionFind(len(self.pos))
        for j, (_, (x_r, y_r)) in enumerate(self):
            for i, (_, (x_l, y_l)) in enumerate(islice(self, j)):
                if x_l == x_r or y_l == y_r:
                    uf.unite(i, j)
        # Collect the connected factors of the cells
        all_factors: Dict[int, List[Cell]] = {}
        for i, cell in enumerate(self.pos):
            x = uf.find(i)
            if x in all_factors:
                all_factors[x].append(cell)
            else:
                all_factors[x] = [cell]
        factor_cells = list(set(cells) for cells in all_factors.values())
        return [self.get_gridded_perm_in_cells(comp) for comp in factor_cells]

    def compress(self) -> List[int]:
        """Compresses the gridded permutation into a list of integers.
        It starts with a list of the values in the permutation. The rest is
        the list of positions flattened."""
        return list(chain(self._patt, chain.from_iterable(self._pos)))

    @classmethod
    def decompress(cls, array: List[int]) -> "GriddedPerm":
        """Decompresses a list of integers in the form outputted by the
        compress method and constructs an Obstruction."""
        n, it = len(array) // 3, iter(array)
        return cls(
            Perm(next(it) for _ in range(n)), ((next(it), next(it)) for _ in range(n))
        )

    # Symmetries
    def reverse(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """
        Reverses the tiling within its boundary. Every cell and obstruction
        gets flipped over the vertical middle axis."""
        return type(self)(self._patt.reverse(), reversed(list(map(transf, self._pos))))

    def complement(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Flip over the horizontal axis."""
        return type(self)(self._patt.complement(), map(transf, self._pos))

    def inverse(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Flip over the diagonal."""
        flipped = self._patt.inverse()
        pos = self._patt.inverse().apply(self._pos)
        return type(self)(flipped, map(transf, pos))

    def antidiagonal(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Flip over the anti-diagonal"""
        flipped = self._patt.flip_antidiagonal()
        pos = self._patt.rotate(-1).apply(self._pos)
        return type(self)(flipped, map(transf, pos))

    def rotate270(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Rotate 270 degrees"""
        rotated = self._patt.rotate(-1)
        pos = rotated.apply(self._pos)
        return type(self)(rotated, map(transf, pos))

    def rotate180(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Rotate 180 degrees"""
        return type(self)(self._patt.rotate(2), reversed(list(map(transf, self._pos))))

    def rotate90(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Rotate 90 degrees"""
        return type(self)(
            self._patt.rotate(), map(transf, self._patt.inverse().apply(self._pos))
        )

    def column_reverse(self, column: int) -> "GriddedPerm":
        """Reverse the part of the gridded perm that belongs to a given column."""
        parts: Tuple[List[Tuple[int, Tuple[int, int]]], ...] = ([], [], [])
        for v, (x, y) in self:
            parts[(x >= column) + (x > column)].append((v, (x, y)))
        return type(self)(*zip(*chain(parts[0], reversed(parts[1]), parts[2])))

    def row_complement(self, row: int) -> "GriddedPerm":
        """Replace the part of the gridded perm that belongs to a row with its
        complement."""
        indices, vals = set(), []
        for i, (val, (_, y)) in enumerate(self):
            if y == row:
                indices.add(i)
                vals.append(val)
        st = Perm.to_standard(vals)
        unstandardized = dict(zip(st, vals))
        in_row = (unstandardized[val] for val in st.complement())
        return type(self)(
            Perm(
                next(in_row) if i in indices else val for i, val in enumerate(self.patt)
            ),
            self.pos,
        )

    def permute_columns(self, perm: Iterable[int]) -> "GriddedPerm":
        """Given an initial state of columns 12...n, permute them using the provided
        permutation.
        """
        if not isinstance(perm, Perm):
            perm = Perm(perm)
        assert len(perm) > max(x for x, y in self.pos)
        cols: List[List[Tuple[int, int]]] = [[] for _ in range(len(perm))]
        for v, (x, y) in self:
            cols[x].append((v, y))
        patt, positions = [], []
        for x, col in enumerate(perm.apply(cols)):
            for v, y in col:
                patt.append(v)
                positions.append((x, y))
        return type(self)(patt, positions)

    def permute_rows(self, perm: Iterable[int]) -> "GriddedPerm":
        """Given an initial state of rows 12...n, permute them using the provided
        permutation.
        """
        if not isinstance(perm, Perm):
            perm = Perm(perm)
        assert len(perm) > max(x for x, y in self.pos)
        back_map = dict(zip(perm, range(len(perm))))
        positions = [(x, back_map[y]) for x, y in self.pos]
        occ: List[List[int]] = [[] for _ in range(len(perm))]
        for val, (_, y) in zip(self.patt, positions):
            occ[y].append(val)
        offset, val_map = 0, {}
        for lis in occ:
            for a, b in zip(lis, Perm.to_standard(lis)):
                val_map[a] = b + offset
            offset += len(lis)
        return type(self)((val_map[val] for val in self.patt), positions)

    def apply_perm_map_to_cell(
        self, perm_mapping: Callable[[Perm], Perm], cell: Cell
    ) -> "GriddedPerm":
        """Apply a permutation map to the subperm within a cell."""
        subperm = [val for val, pos in self if pos == cell]
        st = Perm.to_standard(subperm)
        back_map = dict(zip(st, subperm))
        new_subperm = (back_map[val] for val in perm_mapping(st))
        return type(self)(
            (next(new_subperm) if pos == cell else val for val, pos in self), self.pos
        )

    def to_jsonable(self) -> dict:
        """Returns a dictionary object which is JSON serializable representing
        a GriddedPerm."""
        return {"patt": self._patt, "pos": self._pos}

    @classmethod
    def from_json(cls, jsonstr: str) -> "GriddedPerm":
        """Returns a GriddedPerm object from JSON string."""
        jsondict = json.loads(jsonstr)
        return cls.from_dict(jsondict)

    @classmethod
    def from_dict(cls, jsondict: dict) -> "GriddedPerm":
        """Returns a GriddedPerm object from a dictionary loaded from a JSON
        serialized GriddedPerm object."""
        return cls(jsondict["patt"], map(tuple, jsondict["pos"]))  # type: ignore

    @property
    def patt(self) -> Perm:
        return self._patt

    @property
    def pos(self) -> Tuple[Cell, ...]:
        return self._pos

    def ascii_plot(self) -> str:
        max_x = max(cell[0] for cell in self.pos)
        max_y = max(cell[1] for cell in self.pos)
        res = ""

        def points_in_col(i):
            return sum(1 for cell in self.pos if cell[0] == i)

        def points_in_row(j):
            return sum(1 for cell in self.pos if cell[1] == j)

        row_boundary = (
            "+" + "+".join("-" * points_in_col(i) for i in range(max_x + 1)) + "+"
        )
        col_boundary = (
            "|" + "|".join(" " * points_in_col(i) for i in range(max_x + 1)) + "|"
        )

        for j in range(max_y, -1, -1):
            res += (
                "\n".join(
                    [row_boundary] + [col_boundary for i in range(points_in_row(j))]
                )
                + "\n"
            )
        res += row_boundary

        for (idx, val) in enumerate(self.patt):
            x, y = self.pos[idx]
            # insert into this spot:
            # (idx + x + 1) is the horizontal index. idx is points to left, and
            #               x + 1 counts number of col boundaries to left
            # (len(self) + max_y) - (val + y) is vertical index.
            #               val is points below, and y + 1 counts number of - below
            insert = (idx + x + 1) + ((len(self) + max_y) - (val + y)) * (
                len(col_boundary) + 1
            )
            res = res[:insert] + "●" + res[insert + 1 :]
        return res

    def to_tex(self, one_line_notation: bool = True, one_based: bool = True) -> str:
        """Return the GriddedPerm in LaTeX math mode."""
        if one_line_notation:
            return "".join(f"{val + one_based}^{{({x},{y})}}" for val, (x, y) in self)
        perm = (
            "".join(
                (f"({val + one_based})" for val in self.patt)
                if len(self) > 9
                else (f"{val + one_based}" for val in self.patt)
            )
            if one_based
            else f"{self.patt}"
        )
        return f"({perm}, {self.pos})"

    def _get_plot_pos(self) -> Tuple[Dict[int, Tuple[float, float]], Tuple[int, int]]:
        """Helper that positions visualization points of GriddedPerm."""
        dim = (1 + max(x for _, (x, _) in self), 1 + max(y for _, (_, y) in self))
        col_to_val: List[List[Tuple[int, int]]] = [[] for i in range(dim[0])]
        row_to_val: List[List[Tuple[int, int]]] = [[] for i in range(dim[1])]
        val_to_pos = {}
        for val, (x, y) in self:
            col_to_val[x].append((val, len(col_to_val[x])))
            row_to_val[y].append((val, len(row_to_val[y])))
            val_to_pos[val] = (x, y)
        return {
            val: (
                next(
                    (
                        x + (k + 1) * (1 / (len(col_to_val[x]) + 1))
                        for j, k in sorted(col_to_val[x])
                        if j == val
                    )
                ),
                next(
                    (
                        y + (i + 1) * (1 / (len(row_to_val[y]) + 1))
                        for i, (j, _) in enumerate(sorted(row_to_val[y]))
                        if j == val
                    )
                ),
            )
            for val, (x, y) in val_to_pos.items()
        }, dim

    def to_tikz(self, tab: str = "  ") -> str:
        """Return the tikz code to plot the GriddedPerm."""
        val_to_pos, (max_x, max_y) = self._get_plot_pos()
        return "".join(
            (
                "\\begin{tikzpicture}\n",
                f"{tab}\\def\\xs{{1.0}}\n",
                f"{tab}\\def\\ys{{1.0}}\n",
                f"{tab}\\def\\ps{{1.0}}\n",
                (
                    f"{tab}\\draw (0,0) grid[xscale=\\xs,yscale=\\ys] "
                    f"({max_x}, {max_y});\n"
                ),
                "\n".join(
                    (
                        f"{tab}\\coordinate (p{i}) at "
                        f"({val_to_pos[v][0]}*\\xs,{val_to_pos[v][1]}*\\ys);"
                    )
                    for i, v in enumerate(self.patt)
                ),
                f'\n{tab}\\draw {"--".join(f"(p{i})" for i in range(len(self)))};\n',
                "\n".join(
                    f"{tab}\\fill (p{i}) circle (0.1*\\ps);" for i in range(len(self))
                ),
                "\n\\end{tikzpicture}",
            )
        )

    def to_svg(self, image_scale: float = 10.0) -> str:
        """Return the svg code to plot the GriddedPerm."""
        i_scale = int(image_scale * 10)
        val_to_pos, (m_x, m_y) = self._get_plot_pos()
        return "".join(
            [
                (
                    '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width='
                    f'"{m_x * i_scale}" height="{m_y * i_scale}" '
                    f'viewBox="0 0 {m_x*10} {m_y*10}">\n'
                ),
                "\n".join(
                    (
                        f'<line x1="{i*10}" y1="0" x2="{i*10}" y2="{m_y*10}" '
                        'style="stroke:rgb(0,0,0);stroke-width:0.5" />'
                    )
                    for i in range(m_x + 1)
                ),
                "\n",
                "\n".join(
                    (
                        f'<line x1="0" y1="{i*10}" x2="{m_x*10}" y2="{i*10}" '
                        'style="stroke:rgb(0,0,0);stroke-width:0.5" />'
                    )
                    for i in range(m_y + 1)
                ),
                "\n",
                (
                    lambda path: (
                        f'<polyline points="{path}" fill="none" '
                        'stroke="black" stroke-width="0.65" />\n'
                    )
                )(
                    " ".join(
                        f"{x * 10},{(m_y - y) * 10}"
                        for x, y in (val_to_pos[val] for val in self.patt)
                    )
                ),
                "\n".join(
                    (
                        f'<circle cx="{(10 * x):.4f}" cy="{(10 * (m_y - y)):.4f}" '
                        'r="0.5" stroke="black" fill="rgb(0,0,0)" />'
                    )
                    for x, y in (val_to_pos[val] for val in self.patt)
                ),
                "\n</svg>",
            ]
        )

    def show(self, scale: float = 10.0) -> None:
        """Open a browser tab and display GriddedPerm graphically. Image can be
        enlarged with scale parameter
        """
        HTMLViewer.open_svg(self.to_svg(image_scale=scale))

    def __len__(self) -> int:
        return len(self._patt)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({tuple(self._patt)!r}, {self.pos})"

    def __str__(self) -> str:
        return "{}: {}".format(str(self._patt), ", ".join(str(c) for c in self.pos))

    def __hash__(self) -> int:
        return hash(self._patt) ^ hash(self._pos)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self._patt == other.patt and self._pos == other.pos

    def __lt__(self, other: "GriddedPerm") -> bool:
        return (self._patt, self._pos) < (other.patt, other.pos)

    def __contains__(self, other: "GriddedPerm") -> bool:
        return next((True for _ in other.occurrences_in(self)), False)

    def __iter__(self) -> Iterator[Tuple[int, Cell]]:
        return zip(self.patt, self.pos)

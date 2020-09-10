import json
from itertools import chain, combinations, product
from typing import Callable, Dict, FrozenSet, Iterable, Iterator, List, Optional, Tuple

from comb_spec_searcher import CombinatorialObject
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, UnionFind

Cell = Tuple[int, int]
Position = Tuple[Cell, ...]


class GriddedPerm(CombinatorialObject):
    def __init__(self, pattern: Iterable[int], positions: Iterable[Cell]):
        if not pattern:
            self._patt: Perm = Perm(())
            self._pos: Position = tuple(positions)
            self._cells: FrozenSet[Cell] = frozenset()
            self._rows = 1
            self._columns = 1
        else:
            # Pattern should be a Perm of course
            self._patt = Perm(pattern)
            # Position is a tuple of (x, y) coordinates, where the ith (x, y)
            # corresponds to the i-th point in the pattern.
            self._pos = tuple(positions)

            if len(self._patt) != len(self._pos):
                raise ValueError(("Pattern and position list have unequal" "lengths."))

            # Immutable set of cells which the gridded permutation spans.
            self._cells = frozenset(self._pos)

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
        for i in range(len(self)):
            for j in range(i + 1, len(self)):
                if self.pos[i][0] > self.pos[j][0]:
                    return True
                if self.patt[i] < self.patt[j] and self.pos[i][1] > self.pos[j][1]:
                    return True
                if self.patt[i] > self.patt[j] and self.pos[i][1] < self.pos[j][1]:
                    return True
        return False

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
        remaining = [i for i in range(len(self)) if self._pos[i] not in cells]
        return self.__class__(
            Perm.to_standard(self._patt[i] for i in remaining),
            (self._pos[i] for i in remaining),
        )

    def points_in_cell(self, cell: Cell) -> Iterator[int]:
        """Yields the indices of the points in the cell given."""
        for i in range(len(self)):
            if self._pos[i] == cell:
                yield i

    def isolated_cells(self) -> Iterator[Cell]:
        """Yields the cells that contain only one point of the gridded
        permutation and are in their own row and column."""
        for i in range(len(self)):
            isolated = True
            for j in range(len(self)):
                if i == j:
                    continue
                if (
                    self._pos[i][0] == self._pos[j][0]
                    or self._pos[i][1] == self._pos[j][1]
                ):
                    isolated = False
                    break
            if isolated:
                yield self._pos[i]

    def is_isolated(self, indices: Iterable[int]) -> bool:
        """Checks if the cells at the indices do not share a row or column with
        any other cell in the gridded permutation."""
        for i in range(len(self)):
            if i in indices:
                continue
            if any(
                (
                    self._pos[i][0] == self._pos[j][0]
                    or self._pos[i][1] == self._pos[j][1]
                )
                for j in indices
            ):
                return False
        return True

    def forced_point_index(self, cell: Cell, direction: int) -> int:
        """Search in the cell given for the point with the strongest force with
        respect to the given force."""
        if self.occupies(cell):
            points = list(self.points_in_cell(cell))
            if direction == DIR_EAST:
                return max(points)
            if direction == DIR_NORTH:
                return max((self._patt[p], p) for p in points)[1]
            if direction == DIR_WEST:
                return min(points)
            if direction == DIR_SOUTH:
                return min((self._patt[p], p) for p in points)[1]
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
                return max((i1, i2))
            if direction == DIR_NORTH:
                return max((self._patt[p], p) for p in (i1, i2))[1]
            if direction == DIR_WEST:
                return min((i1, i2))
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
        for i in range(len(self)):
            if self._pos[i][0] == col:
                yield (i, self._patt[i])

    def get_points_row(self, row: int) -> Iterator[Tuple[int, int]]:
        """Yields all points of the gridded permutation in the row."""
        for i in range(len(self)):
            if self._pos[i][1] == row:
                yield (i, self._patt[i])

    def get_points_below_row(self, row: int) -> Iterator[Tuple[int, int]]:
        """Yields all points of the gridded permutation below the row."""
        for i in range(len(self)):
            if self._pos[i][1] < row:
                yield (i, self._patt[i])

    def get_points_above_row(self, row: int) -> Iterator[Tuple[int, int]]:
        """Yields all points of the gridded permutation above the row."""
        for i in range(len(self)):
            if self._pos[i][1] > row:
                yield (i, self._patt[i])

    def get_points_left_col(self, col) -> Iterator[Tuple[int, int]]:
        """Yields all points of the gridded permutation left of column col."""
        for i in range(len(self)):
            if self._pos[i][0] < col:
                yield (i, self._patt[i])

    def get_subperm_left_col(self, col: int) -> "GriddedPerm":
        """Returns the gridded subpermutation of points left of column col."""
        return self.__class__(
            Perm.to_standard(
                self.patt[i] for i in range(len(self)) if self.pos[i][0] < col
            ),
            (self.pos[i] for i in range(len(self)) if self.pos[i][0] < col),
        )

    def get_points_right_col(self, col: int) -> Iterator[Tuple[int, int]]:
        """Yields all points of the gridded permutation right of column col."""
        for i in range(len(self)):
            if self._pos[i][0] > col:
                yield (i, self._patt[i])

    def get_gridded_perm_at_indices(self, indices: Iterable[int]) -> "GriddedPerm":
        """
        Returns the subgridded perm that contains only the point at the given
        indices.

        Indices must be sorted.
        """
        return self.__class__(
            Perm.to_standard(self.patt[i] for i in indices),
            (self.pos[i] for i in indices),
        )

    def get_gridded_perm_in_cells(self, cells: Iterable[Cell]) -> "GriddedPerm":
        """Returns the subgridded permutation of points in cells."""
        return self.__class__(
            Perm.to_standard(
                self.patt[i] for i in range(len(self)) if self.pos[i] in cells
            ),
            (self.pos[i] for i in range(len(self)) if self.pos[i] in cells),
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
        return self.__class__(
            self._patt.insert(idx, val), self._pos[:idx] + (cell,) + self._pos[idx:]
        )

    def remove_point(self, index: int) -> "GriddedPerm":
        """Remove the point at index from the gridded permutation."""
        patt = Perm.to_standard(self.patt[:index] + self.patt[index + 1 :])
        pos = self.pos[:index] + self.pos[index + 1 :]
        return self.__class__(patt, pos)

    def all_subperms(self, proper: bool = True) -> Iterator["GriddedPerm"]:
        """Yields all gridded subpermutations."""
        for r in range(len(self) if proper else len(self) + 1):
            for subidx in combinations(range(len(self)), r):
                yield self.__class__(
                    Perm.to_standard(self._patt[i] for i in subidx),
                    (self._pos[i] for i in subidx),
                )

    def apply_map(self, cell_mapping: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Map the coordinates to a new list of coordinates according to the
        cell_mapping given."""
        return self.__class__(self._patt, [cell_mapping(cell) for cell in self._pos])

    def is_point_perm(self) -> bool:
        """Checks if the gridded permutation is of length 1."""
        return len(self) == 1

    def is_localized(self) -> bool:
        """Check if the gridded permutation occupies only a single cell."""
        return self.is_single_cell()

    def is_single_cell(self) -> bool:
        """Check if the gridded permutation occupies only a single cell."""
        return len(set(self._pos)) == 1

    def is_single_row(self) -> bool:
        """Check if the gridded permutation occupies only a single row."""
        return len(set(y for (x, y) in self._pos)) == 1

    def is_empty(self) -> bool:
        """Check if the gridded permutation is the gridded permutation."""
        return not bool(self._patt)

    def is_interleaving(self) -> bool:
        """Check if the gridded permutation occupies two cells that are in the
        same row or column."""
        seen: List[Cell] = []
        for cell in self._pos:
            for seen_cell in seen:
                if cell[0] == seen_cell[0]:
                    if cell[1] != seen_cell[1]:
                        return True
                else:
                    if cell[1] == seen_cell[1]:
                        return True
            seen.append(cell)
        return False

    def factors(self) -> List["GriddedPerm"]:
        """Return a list containing the factors of a gridded permutation.
        A factor is a sub gridded permutation that is isolated on its own rows
        and columns."""
        uf = UnionFind(len(self.pos))
        for i in range(len(self.pos)):
            for j in range(i + 1, len(self.pos)):
                c1, c2 = self.pos[i], self.pos[j]
                if c1[0] == c2[0] or c1[1] == c2[1]:
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

    def compress(self):
        """Compresses the gridded permutation into a list of integers.
        It starts with a list of the values in the permutation. The rest is
        the list of positions flattened.
        # TODO: type annotate"""
        array = list(self._patt)
        array.extend(chain.from_iterable(self._pos))
        return array

    @classmethod
    def decompress(cls, array) -> "GriddedPerm":
        """Decompresses a list of integers in the form outputted by the
        compress method and constructs an Obstruction."""
        n = len(array)
        patt = Perm(array[i] for i in range(n // 3))
        pos = zip(array[n // 3 :: 2], array[n // 3 + 1 :: 2])
        return cls(patt, pos)

    # Symmetries
    def reverse(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """
        Reverses the tiling within its boundary. Every cell and obstruction
        gets flipped over the vertical middle axis."""
        return self.__class__(
            self._patt.reverse(), reversed(list(map(transf, self._pos)))
        )

    def complement(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Flip over the horizontal axis."""
        return self.__class__(self._patt.complement(), map(transf, self._pos))

    def inverse(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Flip over the diagonal."""
        flipped = self._patt.inverse()
        pos = self._patt.inverse().apply(self._pos)
        return self.__class__(flipped, map(transf, pos))

    def antidiagonal(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """ \\
        Flip over the diagonal"""
        flipped = self._patt.flip_antidiagonal()
        pos = self._patt.rotate(-1).apply(self._pos)
        return self.__class__(flipped, map(transf, pos))

    def rotate270(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Rotate 270 degrees"""
        rotated = self._patt.rotate(-1)
        pos = rotated.apply(self._pos)
        return self.__class__(rotated, map(transf, pos))

    def rotate180(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Rotate 180 degrees"""
        return self.__class__(
            self._patt.rotate(2), reversed(list(map(transf, self._pos)))
        )

    def rotate90(self, transf: Callable[[Cell], Cell]) -> "GriddedPerm":
        """Rotate 90 degrees"""
        return self.__class__(
            self._patt.rotate(), map(transf, self._patt.inverse().apply(self._pos))
        )

    def to_jsonable(self) -> dict:
        """Returns a dictionary object which is JSON serializable representing
        a GriddedPerm."""
        output: dict = dict()
        output["patt"] = self._patt
        output["pos"] = self._pos
        return output

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

    def __len__(self) -> int:
        return len(self._patt)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({tuple(self._patt)!r}, {self.pos})"

    def __str__(self) -> str:
        return "{}: {}".format(str(self._patt), ", ".join(str(c) for c in self.pos))

    def __hash__(self) -> int:
        return hash(self._patt) ^ hash(self._pos)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._patt == other.patt and self._pos == other.pos

    def __lt__(self, other: "GriddedPerm") -> bool:
        return (self._patt, self._pos) < (other.patt, other.pos)

    def __contains__(self, other: "GriddedPerm") -> bool:
        try:
            next(other.occurrences_in(self))
            return True
        except StopIteration:
            return False

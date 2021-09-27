import itertools
from typing import TYPE_CHECKING, Dict, Iterator, Optional, Tuple

from tilings.exception import InvalidOperationError

if TYPE_CHECKING:
    from tilings.griddedperm import GriddedPerm

Cell = Tuple[int, int]


class RowColMap:
    """
    A class to combine a row and a column map together and map different object related
    to tiling in accordance to those row and columns map.

    INPUT:
      - `row_map`: the row map given as a dictionary.
      - `col_map`: the column map given as a dictionary.
      - `is_identity`: A boolean that indicate if the map is the identity.
    """

    def __init__(
        self,
        row_map: Dict[int, int],
        col_map: Dict[int, int],
        is_identity: Optional[bool] = None,
    ) -> None:
        self._row_map = row_map
        self._col_map = col_map
        self._is_identity = is_identity

    @classmethod
    def identity(cls, dimensions: Tuple[int, int]) -> "RowColMap":
        """
        Build a map that is the identity for a tiling of the given dimensions.

        If one of the dimensions is 0 then the corresponding row/column map will
        be an empty dictionary.
        """
        col_map = {i: i for i in range(dimensions[0])}
        row_map = {i: i for i in range(dimensions[1])}
        return RowColMap(row_map=row_map, col_map=col_map, is_identity=True)

    def reverse(self) -> "RowColMap":
        """
        Return the reverse map if possible.
        Otherwise raise an InvalidOperationError.
        """
        row_map = {v: k for k, v in self._row_map.items()}
        col_map = {v: k for k, v in self._col_map.items()}
        if len(row_map) != len(self._row_map) or len(col_map) != len(self._col_map):
            raise InvalidOperationError("The map is not reversible.")
        return RowColMap(
            row_map=row_map, col_map=col_map, is_identity=self._is_identity
        )

    def compose(self, other: "RowColMap") -> "RowColMap":
        """
        The return the new map that is obtained by the applying first self and then
        other.

        If self maps a -> b and other maps b -> c than the resulting map maps a -> c.
        """
        col_map = {k: other.map_col(v) for k, v in self._col_map.items()}
        row_map = {k: other.map_row(v) for k, v in self._row_map.items()}
        return RowColMap(row_map=row_map, col_map=col_map)

    def is_identity(self) -> bool:
        """
        Indicate if the map is the identity map.
        """
        if self._is_identity is None:
            kv_pairs = itertools.chain(self._col_map.items(), self._row_map.items())
            self._is_identity = all(k == v for k, v in kv_pairs)
        return self._is_identity

    def is_non_crossing(self) -> bool:
        """
        Check that the row map and col map map interval to interval.
        """
        cols = [b for _, b in sorted(self._col_map.items())]
        rows = [b for _, b in sorted(self._row_map.items())]
        return cols == sorted(cols) and rows == sorted(rows)

    # Mapping method
    def is_mappable_gp(self, gp: "GriddedPerm") -> bool:
        """
        Return True if all the cell used by the gridded perm can be mapped.
        """
        return all(self.is_mappable_cell(cell) for cell in gp.pos)

    def map_gp(self, gp: "GriddedPerm") -> "GriddedPerm":
        """
        Map the gridded permutation according to the map.
        """
        return gp.__class__(gp.patt, map(self.map_cell, gp.pos))

    def is_mappable_cell(self, cell: Cell) -> bool:
        """
        Return True if the cell can be mapped, i.e. if the image of the row
        and the column of the are defined by the map.
        """
        return self.is_mappable_col(cell[0]) and self.is_mappable_row(cell[1])

    def map_cell(self, cell: Cell) -> Cell:
        """
        Map the cell according to the map.
        """
        return (self.map_col(cell[0]), self.map_row(cell[1]))

    def is_mappable_row(self, row: int) -> bool:
        """
        Return True if the image of the row is defined.
        """
        return row in self._row_map

    def map_row(self, row: int) -> int:
        """
        Map the row according to the map.
        """
        return self._row_map[row]

    def is_mappable_col(self, col: int) -> bool:
        """
        Return True if the image of the column is defined.
        """
        return col in self._col_map

    def map_col(self, col: int) -> int:
        """
        Map the column according to the map.
        """
        return self._col_map[col]

    # Pre-image method
    def preimage_row(self, row: int) -> Iterator[int]:
        """Returns all the preimages of the given row."""
        return (k for k, v in self._row_map.items() if v == row)

    def preimage_col(self, col: int) -> Iterator[int]:
        """Returns all the preimages of the given column."""
        return (k for k, v in self._col_map.items() if v == col)

    def preimage_cell(self, cell: Cell) -> Iterator[Cell]:
        """Returns all the preimages of the given cell."""
        col, row = cell
        return itertools.product(self.preimage_col(col), self.preimage_row(row))

    def preimage_gp(self, gp: "GriddedPerm") -> Iterator["GriddedPerm"]:
        """
        Returns all the preimages of the given gridded permutation.

        Gridded permutations that are contradictory are filtered out.
        """
        for pos in itertools.product(*(self.preimage_cell(cell) for cell in gp.pos)):
            new_gp = gp.__class__(gp.patt, pos)
            if not new_gp.contradictory():
                yield new_gp

    # Other method
    def max_row(self) -> int:
        """Return the biggest row index in the image."""
        return max(self._row_map.values())

    def max_col(self) -> int:
        """Return the biggest column index in the image."""
        return max(self._col_map.values())

    def __str__(self) -> str:
        s = "RowColMap\n"
        rows = [f"{k}: {v}" for k, v in sorted(self._row_map.items())]
        cols = [f"{k}: {v}" for k, v in sorted(self._col_map.items())]
        row_str = ", ".join(rows)
        col_str = ", ".join(cols)
        s += f"    row map: {{{row_str}}}\n"
        s += f"    col map: {{{col_str}}}"
        return s

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RowColMap):
            return NotImplemented
        return self._col_map == other._col_map and self._row_map == other._row_map

    def __hash__(self) -> int:
        row_map = tuple(sorted(self._row_map.items()))
        col_map = tuple(sorted(self._col_map.items()))
        return hash((col_map, row_map))

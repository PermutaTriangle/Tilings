import itertools
from typing import TYPE_CHECKING, Dict, Optional, Tuple

from tilings.exception import InvalidOperationError

if TYPE_CHECKING:
    from tilings.assumptions import TrackingAssumption
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

    def is_identity(self) -> bool:
        """
        Indicate if the map is the identity map.
        """
        if self.is_identity is None:
            kv_pairs = itertools.chain(self._col_map.items(), self._row_map.items())
            self._is_identity = all(k == v for k, v in kv_pairs)
        assert self._is_identity is not None
        return self._is_identity

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

    def map_assumption(self, assumption: "TrackingAssumption") -> "TrackingAssumption":
        """
        Map the assumption according to the map.

        If some of the gridded permutation tracked by the assumption cannot be mapped
        they are removed from the assumption.
        """
        gps = tuple(self.map_gp(gp) for gp in assumption.gps if self.is_mappable_gp(gp))
        return assumption.__class__(gps)

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

    def max_row(self) -> int:
        """Return the biggest row index in the image."""
        return max(self._row_map.values())

    def max_col(self) -> int:
        """Return the biggest column index in the image."""
        return max(self._col_map.values())

    def __str__(self) -> str:
        s = "RowColMap\n"
        s += f"    row map: {self._row_map}\n"
        s += f"    col map: {self._col_map}\n"
        return s

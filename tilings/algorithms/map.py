import itertools
from typing import TYPE_CHECKING, Callable, Dict, Iterable, Iterator, List, Tuple

from tilings.exception import InvalidOperationError

if TYPE_CHECKING:
    from tilings.assumptions import Tiling, TrackingAssumption
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
        self, row_map: Dict[int, int], col_map: Dict[int, int], is_identity: bool
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

    @staticmethod
    def _preimage_gp_col(
        gp_cols: Tuple[int, ...], preimage_func: Callable[[int], Iterator[int]]
    ) -> Iterator[Tuple[int, ...]]:
        """
        Return all the possible sequence of column for a preimage of the gridded
        permutation using the given preimage_func.
        """
        possible_col = [sorted(preimage_func(col)) for col in gp_cols]
        partial_pos: List[int] = []
        partial_pos_indices: List[int] = []
        while True:
            # Padding the current solution with the leftmost options
            while len(partial_pos) < len(gp_cols):
                last_col = partial_pos[-1] if partial_pos else 0
                for new_col_idx, col in enumerate(possible_col[len(partial_pos)]):
                    if last_col <= col:
                        partial_pos.append(col)
                        partial_pos_indices.append(new_col_idx)
                        break
                else:
                    break
            else:
                yield tuple(partial_pos)
            # increasing the rightmost pos that can be increased.
            while partial_pos:
                partial_pos.pop()
                partial_pos_last_index = partial_pos_indices.pop()
                if partial_pos_last_index + 1 < len(possible_col[len(partial_pos)]):
                    break
            else:
                break
            partial_pos.append(
                possible_col[len(partial_pos)][partial_pos_last_index + 1]
            )
            partial_pos_indices.append(partial_pos_last_index + 1)

    def preimage_gp(self, gp: "GriddedPerm") -> Iterator["GriddedPerm"]:
        """
        Returns all the preimages of the given gridded permutation.
        Gridded permutations that are contradictory are filtered out.
        """
        gp_cols = tuple(col for col, _ in gp.pos)
        preimage_col_pos = self._preimage_gp_col(gp_cols, self.preimage_col)
        gp_rows = gp.patt.inverse().apply(row for _, row in gp.pos)
        preimage_row_pos: Iterator[Tuple[int, ...]] = map(
            gp.patt.apply, self._preimage_gp_col(gp_rows, self.preimage_row)
        )
        for pos in itertools.product(preimage_col_pos, preimage_row_pos):
            new_gp = gp.__class__(gp.patt, zip(*pos))
            yield new_gp

    def preimage_gps(self, gps: Iterable["GriddedPerm"]) -> Iterator["GriddedPerm"]:
        """
        Returns all the preimages of the given gridded permutations.
        Gridded permutations that are contradictory are filtered out.
        """
        for gp in gps:
            yield from self.preimage_gp(gp)

    def preimage_obstruction_and_requirements(
        self, tiling: "Tiling"
    ) -> Tuple[List["GriddedPerm"], List[List["GriddedPerm"]]]:
        if tiling.assumptions:
            raise NotImplementedError("Not implemented for tilings with assumptions")
        obs = itertools.chain.from_iterable(
            self.preimage_gp(ob) for ob in tiling.obstructions
        )
        reqs = (
            itertools.chain.from_iterable(self.preimage_gp(req) for req in req_list)
            for req_list in tiling.requirements
        )
        return list(obs), list(list(r) for r in reqs)

    def preimage_tiling(self, tiling: "Tiling") -> "Tiling":
        return tiling.__class__(*self.preimage_obstruction_and_requirements(tiling))

    # Other method
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

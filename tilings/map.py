import itertools
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
)

from tilings.exception import InvalidOperationError
from tilings.griddedperm import GriddedPerm

if TYPE_CHECKING:
    from tilings.parameter_counter import ParameterCounter, PreimageCounter
    from tilings.tiling import Tiling

Cell = Tuple[int, int]


class CellMap:
    def __init__(self, cell_map: Dict[Cell, Cell]) -> None:
        self._map = cell_map

    @classmethod
    def identity(cls, dimensions: Tuple[int, int]) -> "CellMap":
        cells = itertools.product(range(dimensions[0]), range(dimensions[1]))
        return CellMap({c: c for c in cells})

    def domain(self) -> Iterator[Cell]:
        """
        Return the domain of the map.
        """
        return iter(self._map)

    def inverse(self) -> "CellMap":
        """
        Return the inverse map if possible.
        Otherwise raise an InvalidOperationError.
        """
        inverse_map = {v: k for k, v in self._map.items()}
        if len(inverse_map) != len(self._map):
            raise InvalidOperationError("The map is not reversible.")
        return CellMap(inverse_map)

    def restriction(self, cells: Set[Cell]):
        """
        Return the cell map where the domain is restricted to cells.
        """
        return CellMap({a: b for a, b in self._map.items() if a in cells})

    def to_row_col_map(self) -> "RowColMap":
        """
        Convert the CellMap object into an equivalent RowColMap object.

        Raises InvalidOperationError if the columns or row are not mapped consistently
        and therefore the conversion can't be completed.
        """
        col_map, row_map = {}, {}
        for (col, row), (new_col, new_row) in self._map.items():
            if col not in col_map:
                col_map[col] = new_col
            elif col_map[col] != new_col:
                raise InvalidOperationError("Not mapping column consistently.")
            if row not in row_map:
                row_map[row] = new_row
            elif row_map[row] != new_row:
                raise InvalidOperationError("Not mapping row consistently.")
        return RowColMap(col_map=col_map, row_map=row_map)

    def compose(self, other: "CellMap") -> "CellMap":
        """
        The return the new map that is obtained by the applying first self and then
        other.

        If self maps a -> b and other maps b -> c than the resulting map maps a -> c.
        """
        return CellMap(
            {
                k: other.map_cell(v)
                for k, v in self._map.items()
                if other.is_mappable_cell(v)
            }
        )

    # Mapping method
    def map_tiling(self, tiling: "Tiling") -> "Tiling":
        """
        Map the tiling according to the map.

        Point obstruction that cannot be mapped are ignored.
        """
        mapped_obs = (
            self.map_gp(ob)
            for ob in tiling.obstructions
            if not ob.is_point_perm() or self.is_mappable_gp(ob)
        )
        obs = itertools.filterfalse(GriddedPerm.contradictory, mapped_obs)
        reqs = (
            itertools.filterfalse(GriddedPerm.contradictory, map(self.map_gp, req_list))
            for req_list in tiling.requirements
        )
        params = map(self.map_param, tiling.parameters)
        return tiling.__class__(obs, reqs, params)

    def map_param(self, param: "ParameterCounter") -> "ParameterCounter":
        """
        Map the parameter of according to the map.
        """
        return param.__class__(
            (self.map_preimage_counter(preimg_counter) for preimg_counter in param)
        )

    def map_preimage_counter(
        self,
        preimg_counter: "PreimageCounter",
    ) -> "PreimageCounter":
        """
        Maps the given counter according to the map.

        NOTE: This works if the map is bijective. Not sure about other cases.
        """
        cols_added_before: Dict[int, int] = {}
        rows_added_before: Dict[int, int] = {}
        for cell in self.domain():
            col_pos = self.map_cell(cell)[0] - cell[0]
            row_pos = self.map_cell(cell)[1] - cell[1]
            cols_added_before[cell[0]] = min(
                cols_added_before.get(cell[0], col_pos), col_pos
            )
            rows_added_before[cell[1]] = min(
                rows_added_before.get(cell[1], row_pos), row_pos
            )
        cell_pos_in_col, cell_pos_in_row = {}, {}
        col_split = [0 for _ in range(preimg_counter.tiling.dimensions[0])]
        row_split = [0 for _ in range(preimg_counter.tiling.dimensions[1])]
        for cell in self.domain():
            col_pos = self.map_cell(cell)[0] - cell[0] - cols_added_before[cell[0]]
            row_pos = self.map_cell(cell)[1] - cell[1] - rows_added_before[cell[1]]
            for pre_cell in preimg_counter.map.preimage_cell(cell):
                cell_pos_in_col[pre_cell] = col_pos
                cell_pos_in_row[pre_cell] = row_pos
                col_split[pre_cell[0]] = max(col_pos + 1, col_split[pre_cell[0]])
                row_split[pre_cell[1]] = max(row_pos + 1, row_split[pre_cell[1]])

        cell_to_col_map = {
            k: v + sum(col_split[: k[0]]) for k, v in cell_pos_in_col.items()
        }
        cell_to_row_map = {
            k: v + sum(row_split[: k[1]]) for k, v in cell_pos_in_row.items()
        }
        preimg_map = CellMap(
            {
                cell: (cell_to_col_map[cell], cell_to_row_map[cell])
                for cell in preimg_counter.tiling.active_cells
            }
        )
        return preimg_counter.__class__(
            preimg_map.map_tiling(preimg_counter.tiling),
            preimg_map.inverse()
            .compose(preimg_counter.map)
            .compose(self)
            .to_row_col_map(),
        )

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

    def map_gps(self, gps: Iterable["GriddedPerm"]) -> FrozenSet["GriddedPerm"]:
        return frozenset(self.map_gp(gp) for gp in gps)

    def is_mappable_cell(self, cell: Cell) -> bool:
        """
        Return True if the cell can be mapped.
        """
        return cell in self._map

    def map_cell(self, cell: Cell) -> Cell:
        """
        Map the cell according to the map.
        """
        return self._map[cell]

    def __str__(self) -> str:
        cells = [f"{k}: {v}" for k, v in sorted(self._map.items())]
        cells_str = ", ".join(cells)
        return f"Cell Map: {{{cells_str}}}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CellMap):
            return NotImplemented
        return self._map == other._map

    def __hash__(self) -> int:
        return hash(tuple(sorted(self._map.items())))


class RowColMap(CellMap):
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
        super().__init__(
            {
                cell: (col_map[cell[0]], row_map[cell[1]])
                for cell in itertools.product(self._col_map, self._row_map)
            }
        )

    @property
    def row_map(self) -> Dict[int, int]:
        return self._row_map

    @property
    def col_map(self) -> Dict[int, int]:
        return self._col_map

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

    def inverse(self) -> "RowColMap":
        """
        Return the inverse map if possible.
        Otherwise raise an InvalidOperationError.
        """
        row_map = {v: k for k, v in self._row_map.items()}
        col_map = {v: k for k, v in self._col_map.items()}
        if len(row_map) != len(self._row_map) or len(col_map) != len(self._col_map):
            raise InvalidOperationError("The map is not reversible.")
        return RowColMap(
            row_map=row_map, col_map=col_map, is_identity=self._is_identity
        )

    def to_row_col_map(self) -> "RowColMap":
        return self

    def compose(self, other: "CellMap") -> "RowColMap":
        """
        The return the new map that is obtained by the applying first self and then
        other.

        If self maps a -> b and other maps b -> c than the resulting map maps a -> c.
        """
        if not isinstance(other, RowColMap):
            raise NotImplementedError
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
    ) -> Tuple[List[GriddedPerm], List[List[GriddedPerm]]]:
        if tiling.parameters:
            raise NotImplementedError("Not implemented for tilings with parameter")
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
        rows = [f"{k}: {v}" for k, v in sorted(self._row_map.items())]
        cols = [f"{k}: {v}" for k, v in sorted(self._col_map.items())]
        row_str = ", ".join(rows)
        col_str = ", ".join(cols)
        s += f"    row map: {{{row_str}}}\n"
        s += f"    col map: {{{col_str}}}"
        return s

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._row_map!r}, {self._col_map!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RowColMap):
            return NotImplemented
        return self._col_map == other._col_map and self._row_map == other._row_map

    def __hash__(self) -> int:
        row_map = tuple(sorted(self._row_map.items()))
        col_map = tuple(sorted(self._col_map.items()))
        return hash((col_map, row_map))

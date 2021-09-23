import abc
from collections import defaultdict
from importlib import import_module
from itertools import chain, product
from typing import (
    TYPE_CHECKING,
    Callable,
    DefaultDict,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
)

from permuta import Perm

from .griddedperm import GriddedPerm
from .map import RowColMap

Cell = Tuple[int, int]

if TYPE_CHECKING:
    from tilings.tiling import Tiling


class GriddingsCounter:
    """Counts the number of griddings that the subgridded perm of a gp using
    the active cells has onto the tiling with respect to the mapping.
    The active cells are the values of the cell map."""

    def __init__(self, tiling: "Tiling", cell_map: Callable[[Cell], Cell]):
        self.tiling = tiling
        self.cell_map = cell_map
        self._active_cells: Optional[FrozenSet[Cell]] = None
        self.GP_CACHE: Dict[int, DefaultDict[GriddedPerm, Set[GriddedPerm]]] = {}

    @property
    def active_cells(self) -> FrozenSet[Cell]:
        if self._active_cells is None:
            self._active_cells = frozenset(
                self.cell_map(cell) for cell in self.tiling.active_cells
            )
        return self._active_cells

    def _griddings(self, size: int) -> DefaultDict[GriddedPerm, Set[GriddedPerm]]:
        if size not in self.GP_CACHE:
            res: DefaultDict[GriddedPerm, Set[GriddedPerm]] = defaultdict(set)
            for gp in self.tiling.objects_of_size(size):
                mapped_gp = gp.apply_map(self.cell_map)
                res[mapped_gp].add(gp)
            self.GP_CACHE[size] = res
        return self.GP_CACHE[size]

    def count_griddings(self, gp: GriddedPerm):
        subgp = gp.get_gridded_perm_in_cells(self.active_cells)
        return len(self._griddings(len(subgp))[subgp])

    def preimage(self, gp: GriddedPerm) -> Set[GriddedPerm]:
        return self._griddings(len(gp))[gp]


class TrackingAssumption:
    """
    An assumption used to keep track of the griddings of a tiling.
    """

    def __init__(
        self,
        tiling: "Tiling",
        row_col_map: RowColMap,
    ):
        assert not tiling.assumptions
        self.tiling = tiling
        self.map = row_col_map
        self.remove_empty_rows_and_cols()
        self._init_checked()
        self.gridding_counter = GriddingsCounter(self.tiling, self.map.map_cell)
        self._ignore_reqs_gridding_counter = GriddingsCounter(
            self.tiling.remove_requirements(), self.map.map_cell
        )

    def _init_checked(self):
        """
        Ensure that intervals are preseved with respect to row and col maps.
        """
        cols = [b for _, b in sorted(self.col_map.items())]
        assert cols == sorted(cols)
        rows = [b for _, b in sorted(self.row_map.items())]
        assert rows == sorted(rows)

    def remove_empty_rows_and_cols(self) -> None:
        """
        Update the col and row maps after removing cols and rows that
        became empty when tiling was created.
        """
        self.map = self.tiling.backward_map.compose(self.map)

    def apply_row_col_map(self, row_col_map: "RowColMap") -> "TrackingAssumption":
        """
        Modify in place the map with respect to the given row_col_map. Return self.
        """
        self.map = self.map.compose(row_col_map)
        return self

    def backward_map_gridded_perm(
        self, gp: GriddedPerm, ignore_reqs: bool = False
    ) -> Set[GriddedPerm]:
        """Yield the gridded perms that map to gp according to the col and row maps."""
        if ignore_reqs:
            return self._ignore_reqs_gridding_counter.preimage(gp)
        return self.gridding_counter.preimage(gp)

    def forward_map_gridded_perm(self, gp: GriddedPerm) -> GriddedPerm:
        """Map the gridded perm according to the col and row maps."""
        assert gp.avoids(*self.tiling.obstructions) and all(
            gp.contains(*req) for req in self.tiling.requirements
        )
        return self.map.map_gp(gp)

    def add_obstructions(self, obs: Tuple[GriddedPerm, ...]) -> "TrackingAssumption":
        new_obs = chain.from_iterable(
            self.backward_map_gridded_perm(gp, False) for gp in obs
        )
        return TrackingAssumption(self.tiling.add_obstructions(new_obs), self.map)

    def add_obstructions_and_requirements(
        self, obs: Iterable[GriddedPerm], reqs: Iterable[Iterable[GriddedPerm]]
    ) -> "TrackingAssumption":
        new_obs = chain.from_iterable(
            self.backward_map_gridded_perm(gp, False) for gp in obs
        )
        new_reqs = chain.from_iterable(
            chain.from_iterable(self.backward_map_gridded_perm(gp, False) for gp in req)
            for req in reqs
        )
        return TrackingAssumption(
            self.tiling.add_obstructions_and_requirements(new_obs, new_reqs), self.map
        )

    def add_list_requirement(
        self, req_list: Iterable[GriddedPerm]
    ) -> "TrackingAssumption":
        new_req = chain.from_iterable(
            self.backward_map_gridded_perm(gp, False) for gp in req_list
        )
        return TrackingAssumption(self.tiling.add_list_requirement(new_req), self.map)

    def is_identity(self):
        raise NotImplementedError

    def get_value(self, gp: GriddedPerm) -> int:
        """
        Return the number of griddings corresponding to gp.
        """
        return self.gridding_counter.count_griddings(gp)

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the assumption."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> "TrackingAssumption":
        """Return the assumption from the json dict representation."""
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrackingAssumption):
            return NotImplemented
        return self.tiling == other.tiling and self.map == other.map

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, TrackingAssumption):
            return NotImplemented
        key_self = (
            self.__class__.__name__,
            self.tiling.obstructions,
            self.tiling.requirements,
            self.map,
        )
        key_other = (
            other.__class__.__name__,
            other.tiling.obstructions,
            other.tiling.requirements,
            self.map,
        )
        return key_self < key_other

    def __hash__(self) -> int:
        return hash((self.tiling, self.map))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.tiling!r}), {self.map!r})"

    def __str__(self):
        map_str = "   " + str(self.map).replace("\n", "\n   ")
        tiling_str = "   " + str(self.tiling).replace("\n", "\n   ")
        return (
            "Counting the griddings with respect to the "
            + f"map\n{map_str}\non the tiling:\n{tiling_str}"
        )

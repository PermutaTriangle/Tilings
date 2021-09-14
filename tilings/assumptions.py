import abc
from collections import defaultdict
from importlib import import_module
from itertools import chain, product
from typing import (
    TYPE_CHECKING,
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

Cell = Tuple[int, int]

if TYPE_CHECKING:
    from tilings import Tiling


class GriddingsCounter:
    """Counts the number of griddings that the subgridded perm of a gp using
    the active cells has onto the tiling with respect to the mapping.
    The active cells are the values of the cell map."""

    def __init__(self, tiling: "Tiling", cell_map: Dict[Cell, Cell]):
        self.tiling = tiling
        self.cell_map = cell_map
        self._active_cells: Optional[FrozenSet[Cell]] = None
        self.GP_CACHE: Dict[int, DefaultDict[GriddedPerm, Set[GriddedPerm]]] = {}

    @property
    def active_cells(self) -> FrozenSet[Cell]:
        if self._active_cells is None:
            self._active_cells = frozenset(
                self.cell_map[cell] for cell in self.tiling.active_cells
            )
        return self._active_cells

    def _cell_map(self, cell: Cell) -> Cell:
        return self.cell_map[cell]

    def _griddings(self, size: int) -> DefaultDict[GriddedPerm, Set[GriddedPerm]]:
        if size not in self.GP_CACHE:
            res: DefaultDict[GriddedPerm, Set[GriddedPerm]] = defaultdict(set)
            for gp in self.tiling.objects_of_size(size):
                mapped_gp = gp.apply_map(self._cell_map)
                res[mapped_gp].add(gp)
            self.GP_CACHE[size] = res
        return self.GP_CACHE[size]

    def count_griddings(self, gp: GriddedPerm):
        subgp = gp.get_gridded_perm_in_cells(self.active_cells)
        return len(self._griddings(len(subgp))[subgp])


class TrackingAssumption:
    """
    An assumption used to keep track of the griddings of a tiling.
    """

    def __init__(
        self,
        tiling: "Tiling",
        col_map: Dict[int, int],
        row_map: Dict[int, int],
    ):
        self.tiling = tiling
        self.col_map = col_map
        self.row_map = row_map
        self._cell_map: Optional[Dict[Cell, Cell]] = None
        self.gridding_counter = GriddingsCounter(self.tiling, self.cell_map)
        self._ignore_reqs_gridding_counter = GriddingsCounter(
            self.tiling.remove_requirements(), self.cell_map
        )

    @property
    def cell_map(self) -> Dict[Cell, Cell]:
        if self._cell_map is None:
            self._cell_map = dict()
            for (x1, x2), (y1, y2) in product(
                self.col_map.items(), self.row_map.items()
            ):
                self._cell_map[(x1, y1)] = (x2, y2)
        return self._cell_map

    def backward_map_gridded_perm(
        self, gp: GriddedPerm, ignore_reqs: bool = False
    ) -> Set[GriddedPerm]:
        """Yield the gridded perms that map to gp according to the col and row maps."""
        if ignore_reqs:
            return self._ignore_reqs_gridding_counter.GP_CACHE[len(gp)][gp]
        return self.gridding_counter.GP_CACHE[len(gp)][gp]

    def forward_map_gridded_perm(self, gp: GriddedPerm) -> GriddedPerm:
        """Map the gridded perm according to the col and row maps."""
        assert gp.avoids(*self.tiling.obstructions) and all(
            gp.contains(*req) for req in self.tiling.requirements
        )
        return gp.apply_map(self.gridding_counter._cell_map)

    def is_identity(self):
        raise NotImplementedError

    def get_value(self, gp: GriddedPerm) -> int:
        """
        Return the number of griddings corresponding to gp.
        """
        return self.gridding_counter.count_griddings(gp)

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the assumption."""
        c = self.__class__
        return {
            "class_module": c.__module__,
            "assumption": c.__name__,
            "tiling": self.tiling.to_jsonable(),
            "col_map": [(a, b) for a, b in self.col_map.items()],
            "row_map": [(a, b) for a, b in self.row_map.items()],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TrackingAssumption":
        """Return the assumption from the json dict representation."""
        module = import_module(d["class_module"])
        AssClass: Type["TrackingAssumption"] = getattr(module, d["assumption"])
        assert issubclass(
            AssClass, TrackingAssumption
        ), "Not a valid TrackingAssumption"
        tiling = Tiling.from_dict(d["tiling"])
        row_map = {a: b for a, b in d["row_map"]}
        col_map = {a: b for a, b in d["col_map"]}
        return AssClass(tiling, col_map, row_map)

    def __eq__(self, other) -> bool:
        if other.__class__ == TrackingAssumption:
            return bool(self.tiling == other.tiling) and bool(
                self.cell_map == other.cell_map
            )
        return NotImplemented

    def __lt__(self, other) -> bool:
        if isinstance(other, TrackingAssumption):
            key_self = (
                self.__class__.__name__,
                self.tiling.obstructions,
                self.tiling.requirements,
                tuple(sorted(self.cell_map.items())),
            )
            key_other = (
                other.__class__.__name__,
                other.tiling.obstructions,
                other.tiling.requirements,
                tuple(sorted(other.cell_map.items())),
            )
            return key_self < key_other
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.tiling, tuple(sorted(self.cell_map.items()))))

    def __repr__(self) -> str:
        return self.__class__.__name__ + "({}, {})".format(
            repr(self.tiling), repr(self.cell_map)
        )

    def __str__(self):
        map_str = "\n".join(
            "   {}: {}".format(c1, c2) for c1, c2 in sorted(self.cell_map.items())
        )
        tiling_str = "   " + str(self.tiling).replace("\n", "\n   ")
        return (
            "Counting the griddings with respect to the "
            + f"map\n{map_str}\non the tiling:\n{tiling_str}"
        )

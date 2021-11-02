import itertools
from typing import TYPE_CHECKING, Iterable, Iterator, List, Set, Tuple

from .algorithms.factor import Factor
from .griddedperm import GriddedPerm
from .map import RowColMap

Cell = Tuple[int, int]

if TYPE_CHECKING:
    from tilings import Tiling


class PreimageCounter:
    def __init__(
        self,
        tiling: "Tiling",
        row_col_map: RowColMap,
    ):
        self.tiling = tiling
        self.map = row_col_map
        self.remove_empty_rows_and_cols()
        self._init_checked()

    def _init_checked(self):
        """
        Some sanity check on the counter.
        """
        assert not self.tiling.parameters

    def remove_empty_rows_and_cols(self) -> None:
        """
        Update the col and row maps after removing cols and rows that
        became empty when tiling was created.
        """
        self.map = self.tiling.backward_map.compose(self.map)

    def apply_row_col_map(self, row_col_map: "RowColMap") -> "PreimageCounter":
        """
        Modify in place the map with respect to the given row_col_map. Return self.

        If some of the row/col from the preimage tiling can't be mapped by the
        composition, then they'll be made empty on the preimage tiling.
        """
        empty_cells = [
            cell
            for cell in self.tiling.active_cells
            if not row_col_map.is_mappable_cell(self.map.map_cell(cell))
        ]
        if empty_cells:
            new_obs = map(GriddedPerm.point_perm, empty_cells)
            self.tiling = self.tiling.add_obstructions(new_obs)
            self.map = self.tiling.backward_map.compose(self.map)
        self.map = self.map.compose(row_col_map)
        return self

    def active_region(self, tiling: "Tiling") -> Set[Cell]:
        """
        Yield the active region of the preimage counter.
        """
        res = set()
        for cell in self.tiling.active_cells:
            if sum(1 for _ in self.map.preimage_cell(cell)) > 1:
                res.add(cell)
        extra_obs, extra_reqs = self.extra_obs_and_reqs(tiling)
        for gp in itertools.chain(extra_obs, *extra_reqs):
            res.update(gp.pos)
        return res

    def sub_preimage(self, cells: Set[Cell]) -> "PreimageCounter":
        precells = set(
            itertools.chain.from_iterable(
                self.map.preimage_cell(cell) for cell in cells
            )
        )
        sub_tiling = Factor(self.tiling).factor(precells)
        sub_map = self.map.restricted_by(precells)
        return PreimageCounter(sub_tiling, sub_map.to_row_col_map())

    def extra_obs_and_reqs(
        self, tiling: "Tiling"
    ) -> Tuple[List[GriddedPerm], List[Tuple[GriddedPerm, ...]]]:
        extra_obs, extra_reqs = [], []
        for ob in self.tiling.obstructions:
            if self.map.map_gp(ob) not in tiling.obstructions:
                extra_obs.append(ob)
        for req in self.tiling.requirements:
            if tuple(sorted(self.map.map_gps(req))) not in tiling.requirements:
                extra_reqs.append(req)
        return extra_obs, extra_reqs

    def num_preimage(self, gp: GriddedPerm) -> int:
        """
        Return the number of preimage for the given gridded permutation.
        """
        return sum(1 for _ in self.preimage(gp))

    def preimage(self, gp: GriddedPerm) -> Iterator[GriddedPerm]:
        """Return the preimage of the given gridded permutation on the tiling."""
        return filter(self.tiling.__contains__, self.map.preimage_gp(gp))

    def add_obstructions_and_requirements(
        self, obs: Iterable[GriddedPerm], reqs: Iterable[Iterable[GriddedPerm]]
    ) -> "PreimageCounter":
        """
        Add the given obstructions and requirements to the tiling.
        """
        new_obs = itertools.chain.from_iterable(self.map.preimage_gp(gp) for gp in obs)
        new_reqs = (
            itertools.chain.from_iterable(self.map.preimage_gp(gp) for gp in req)
            for req in reqs
        )
        return PreimageCounter(
            self.tiling.add_obstructions_and_requirements(new_obs, new_reqs), self.map
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PreimageCounter):
            return NotImplemented
        return self.tiling == other.tiling and self.map == other.map

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, PreimageCounter):
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
        return f"{self.__class__.__name__}({self.tiling!r}, {self.map!r})"

    def __str__(self):
        map_str = "   " + str(self.map).replace("\n", "\n   ")
        tiling_str = "   " + str(self.tiling).replace("\n", "\n   ")
        return (
            "Counting the griddings with respect to the "
            + f"map\n{map_str}\non the tiling:\n{tiling_str}"
        )


class ParameterCounter:
    """
    An aggregation of PreimageCounter.
    """

    def __init__(self, counters: Iterable[PreimageCounter]):
        self.counters = tuple(sorted(counters))

    def active_regions(self, tiling: "Tiling") -> Iterator[Set[Cell]]:
        """
        Yield the active regions of the preimage counters.
        """
        for preimage in self:
            yield set(
                preimage.map.map_cell(cell) for cell in preimage.active_region(tiling)
            )

    def sub_param(
        self, cells: Set[Cell], underlying_tiling: "Tiling"
    ) -> "ParameterCounter":
        res = []
        for preimage in self.counters:
            if preimage.active_region(underlying_tiling) <= cells:
                res.append(preimage.sub_preimage(cells))
        return ParameterCounter(res)

    def get_value(self, gp: GriddedPerm) -> int:
        """
        Return the value of the parameter for the given gridded permutation.
        """
        return sum(counter.num_preimage(gp) for counter in self.counters)

    def to_jsonable(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> "ParameterCounter":
        raise NotImplementedError

    def apply_row_col_map(self, row_col_map: "RowColMap") -> "ParameterCounter":
        """
        Modify in place the map with of each counter with respect to the given
        row_col_map. Return self.
        """
        for counter in self.counters:
            counter.apply_row_col_map(row_col_map)
        return self

    def add_obstructions_and_requirements(
        self, obs: Iterable[GriddedPerm], reqs: Iterable[Iterable[GriddedPerm]]
    ) -> "ParameterCounter":
        """
        Add the given obstructions and requirement to all the tilings of the preimage
        counters.
        """
        return ParameterCounter(
            (
                counter.add_obstructions_and_requirements(obs, reqs)
                for counter in self.counters
            )
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ParameterCounter):
            return NotImplemented
        return self.counters == other.counters

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ParameterCounter):
            return NotImplemented
        return self.counters < other.counters

    def __hash__(self) -> int:
        return hash(self.counters)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.counters!r})"

    def __str__(self):
        return "\n".join(map(str, self.counters))

    def __iter__(self) -> Iterator[PreimageCounter]:
        return iter(self.counters)

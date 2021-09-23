import itertools
from typing import TYPE_CHECKING, Iterable, Iterator, Tuple

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
        assert not tiling.assumptions
        self.tiling = tiling
        self.map = row_col_map
        self.remove_empty_rows_and_cols()
        self._init_checked()

    def _init_checked(self):
        """
        Some sanity check on the counter.
        """
        assert self.map.is_non_crossing()
        assert not self.tiling.assumptions

    def remove_empty_rows_and_cols(self) -> None:
        """
        Update the col and row maps after removing cols and rows that
        became empty when tiling was created.
        """
        self.map = self.tiling.backward_map.compose(self.map)

    def apply_row_col_map(self, row_col_map: "RowColMap") -> "Pre image Counter":
        """
        Modify in place the map with respect to the given row_col_map. Return self.
        """
        self.map = self.map.compose(row_col_map)
        return self

    def num_preimage(self, gp: GriddedPerm) -> int:
        """
        Return the number of preimage for the given gridded permutation.
        """
        return sum(1 for _ in self.preimage(gp))

    def preimage(
        self, gp: GriddedPerm, ignore_reqs: bool = False
    ) -> Iterator[GriddedPerm]:
        """
        Return the preimage of the given gridded on the tiling.
        """
        raise NotImplementedError

    def add_obstructions_and_requirements(
        self, obs: Iterable[GriddedPerm], reqs: Iterable[Iterable[GriddedPerm]]
    ) -> "PreimageCounter":
        """
        Add the given obstructions and requirements to the tiling.
        """
        new_obs = itertools.chain.from_iterable(self.preimage(gp, False) for gp in obs)
        new_reqs = (
            itertools.chain.from_iterable(self.preimage(gp, False) for gp in req)
            for req in reqs
        )
        return PreimageCounter(
            self.tiling.add_obstructions_and_requirements(new_obs, new_reqs), self.map
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, PreimageCounter):
            return NotImplemented
        raise NotImplementedError


class ParameterCounter:
    """
    An aggregation of PreimageCounter.
    """

    def __init__(self, counters: Iterable[PreimageCounter]):
        self.counters = tuple(sorted(set(counters)))

    def active_region(self) -> Iterator[Cell]:
        """
        Return the region of the assumption considered active.
        """
        raise NotImplementedError

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
        return "".join(map(str, self.counters))

from typing import TYPE_CHECKING, Iterable, List, Optional, Tuple

from tilings.griddedperm import GriddedPerm
from tilings.map import RowColMap

if TYPE_CHECKING:
    from tilings import Tiling
    from tilings.parameter_counter import ParameterCounter


Cell = Tuple[int, int]
ReqList = Tuple[GriddedPerm, ...]
UninitializedTiling = Tuple[
    Tuple[GriddedPerm, ...], Tuple[ReqList, ...], Tuple["ParameterCounter", ...]
]


class Fusion:
    def __init__(
        self,
        tiling: "Tiling",
        row_idx: Optional[int] = None,
        col_idx: Optional[int] = None,
        tracked: bool = False,
        isolation_level: Optional[str] = None,
    ):
        if isolation_level is not None:
            raise NotImplementedError("Good luck Jay!")
        self.tiling = tiling
        self.tracked = tracked
        if row_idx is None and col_idx is not None:
            self._col_idx = col_idx
            self._fuse_row = False
        elif col_idx is None and row_idx is not None:
            self._row_idx = row_idx
            self._fuse_row = True
        else:
            raise RuntimeError("Cannot specify a row and a columns")
        self._fused_tiling: Optional["Tiling"] = None
        self.fuse_map = self._fuse_map()

    def _fuse_map(self) -> RowColMap:
        num_col, num_row = self.tiling.dimensions
        row_map = {i: i for i in range(num_row)}
        if self._fuse_row:
            for i in range(self._row_idx + 1, num_row + 1):
                row_map[i] = i - 1
        col_map = {i: i for i in range(num_col)}
        if not self._fuse_row:
            for i in range(self._col_idx + 1, num_col + 1):
                col_map[i] = i - 1
        return RowColMap(row_map, col_map)

    def _fuse_gps(self, gps: Iterable["GriddedPerm"]):
        return self.upward_closure(self.fuse_map.map_gps(gps))

    @staticmethod
    def upward_closure(gps: Iterable[GriddedPerm]) -> List[GriddedPerm]:
        """
        Return the upward closure of the gps.
        That is, only those which are not contained in any gp but itself.
        TODO: make this the upward closure in the actual perm poset.
        """
        return [gp1 for gp1 in gps if all(gp1 not in gp2 for gp2 in gps if gp2 != gp1)]

    def fused_obs_reqs_and_params(self) -> UninitializedTiling:
        """
        Return the fused obs, reqs, and params."""
        if self.tiling.parameters:
            raise NotImplementedError
        return (
            tuple(self._fuse_gps(self.tiling.obstructions)),
            tuple(tuple(self._fuse_gps(req)) for req in self.tiling.requirements),
            tuple(),
        )

    def unfused_fused_obs_reqs_and_params(self) -> UninitializedTiling:
        """
        Return the tiling that is created by fusing and then unfusing the tiling.
        """
        if self.tiling.parameters:
            raise NotImplementedError
        obs, reqs, _ = self.fused_obs_reqs_and_params()
        return (
            tuple(self.fuse_map.preimage_gps(obs)),
            tuple(tuple(self.fuse_map.preimage_gps(req)) for req in reqs),
            tuple(),
        )

    def fusable(self):
        """
        Return True if tiling is fusable.
        """
        obs, reqs, _ = self.unfused_fused_obs_reqs_and_params()
        return self.tiling == self.tiling.add_obstructions_and_requirements(obs, reqs)

    def fused_tiling(self) -> "Tiling":
        if self.tracked:
            raise NotImplementedError
        obs, reqs, _ = self.fused_obs_reqs_and_params()
        return self.tiling.__class__(obs, reqs)

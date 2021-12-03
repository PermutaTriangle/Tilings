"""
 The implementation of the fusion algorithm
"""
import functools
import itertools
from typing import TYPE_CHECKING, Iterable, Iterator, List, Optional, Tuple

from tilings.griddedperm import GriddedPerm
from tilings.map import RowColMap
from tilings.parameter_counter import ParameterCounter, PreimageCounter

if TYPE_CHECKING:
    from tilings import Tiling


Cell = Tuple[int, int]
ReqList = Tuple[GriddedPerm, ...]
UninitializedTiling = Tuple[
    Tuple[GriddedPerm, ...], Tuple[ReqList, ...], Tuple["ParameterCounter", ...]
]


class Fusion:
    MAX_NUMBER_EXTRA = 2
    MAX_NUMBER_EXTRA_LOCAL = 2
    MAX_NUMBER_EXTRA_CROSSING = 2
    MAX_NUMBER_EXTRA_LEAVING = 2
    MAX_LENGTH_EXTRA = 2
    MAX_LENGTH_EXTRA_LOCAL = 2
    MAX_LENGTH_EXTRA_CROSSING = 2
    MAX_LENGTH_EXTRA_LEAVING = 2
    MAX_NUM_PARAMS = 2

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
            for i in range(self._row_idx + 1, num_row):
                row_map[i] = i - 1
        col_map = {i: i for i in range(num_col)}
        if not self._fuse_row:
            for i in range(self._col_idx + 1, num_col):
                col_map[i] = i - 1
        return RowColMap(row_map, col_map)

    def _fuse_gps(self, gps: Iterable["GriddedPerm"]) -> List[GriddedPerm]:
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
        return (
            tuple(self._fuse_gps(self.tiling.obstructions)),
            tuple(tuple(self._fuse_gps(req)) for req in self.tiling.requirements),
            tuple(self.fused_param(param) for param in self.tiling.parameters),
        )

    def is_fusable_param(self, parameter_counter: ParameterCounter) -> bool:
        return all(
            not self._active_region_of_preimage_intersects_fuse_region(preimage)
            for preimage in parameter_counter.counters
        ) or (
            len(parameter_counter.counters) == 1
            and parameter_counter.counters[0].tiling == self.allowed_preimage
        )

    def _active_region_of_preimage_intersects_fuse_region(
        self, preimage: PreimageCounter
    ) -> bool:
        if self._fuse_row:
            fuse_region = self.tiling.cells_in_row(self._row_idx).union(
                self.tiling.cells_in_row(self._row_idx + 1)
            )
        else:
            fuse_region = self.tiling.cells_in_col(self._col_idx).union(
                self.tiling.cells_in_col(self._col_idx + 1)
            )
        return bool(preimage.active_region(self.tiling).intersection(fuse_region))

    @functools.cached_property
    def allowed_preimage(self) -> "Tiling":
        obs: List[GriddedPerm] = []
        reqs: List[List[GriddedPerm]] = []
        unfuse_map = list(self._unfuse_maps())
        for rowcolmap in unfuse_map:
            obs.extend(rowcolmap.preimage_gps(self.tiling.obstructions))
        for req in self.tiling.requirements:
            new_req = []
            for rowcolmap in unfuse_map:
                new_req.extend(list(rowcolmap.preimage_gps(req)))
            reqs.append(new_req)
        return self.tiling.__class__(obs, reqs)

    def _unfuse_maps(self) -> Iterator[RowColMap]:
        if self._fuse_row:
            num_col, num_row = self.tiling.dimensions
            col_map = {i: i for i in range(num_col)}
            num_row += 1
            for row in (self._row_idx, self._row_idx + 1):
                row_map = {i: i for i in range(num_row)}
                for i in range(row + 1, num_row):
                    row_map[i] = i - 1
                yield RowColMap(row_map, col_map)
        else:
            num_col, num_row = self.tiling.dimensions
            row_map = {i: i for i in range(num_row)}
            num_col += 1
            for col in (self._col_idx, self._col_idx + 1):
                col_map = {i: i for i in range(num_col)}
                for i in range(col + 1, num_col):
                    col_map[i] = i - 1
                yield RowColMap(row_map, col_map)

    def get_preimage_fuse_indices(
        self, preimage: PreimageCounter
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Return the max of the preimage of self._row_idx, and min of the preimage
        of self._row_idx + 1. If either is None, it means this column is empty
        on the preimage tiling.
        """
        if self._fuse_row:
            row1 = max(preimage.map.preimage_row(self._row_idx), default=None)
            row2 = min(preimage.map.preimage_row(self._row_idx + 1), default=None)
        else:
            row1 = max(preimage.map.preimage_col(self._col_idx), default=None)
            row2 = min(preimage.map.preimage_col(self._col_idx + 1), default=None)
        return row1, row2

    def fused_preimage(self, preimage: PreimageCounter) -> PreimageCounter:
        """Return the fused preimage."""
        row_idx, col_idx = None, None
        row1, row2 = self.get_preimage_fuse_indices(preimage)
        if row1 is None or row2 is None:
            return PreimageCounter(
                self.tiling.__class__(
                    preimage.tiling.obstructions, preimage.tiling.requirements
                ),
                preimage.map.compose(self.fuse_map),
            )
        if self._fuse_row:
            row_idx = row1
        else:
            col_idx = row1
        fuse_algo = Fusion(preimage.tiling, row_idx, col_idx, False)
        fused_tiling = fuse_algo.fused_tiling()
        fused_map = RowColMap(
            {
                fuse_algo.fuse_map.map_row(a): self.fuse_map.map_row(b)
                for a, b in preimage.map.row_map.items()
            },
            {
                fuse_algo.fuse_map.map_col(a): self.fuse_map.map_col(b)
                for a, b in preimage.map.col_map.items()
            },
        )
        return PreimageCounter(fused_tiling, fused_map)

    def fused_param(self, parameter: ParameterCounter) -> ParameterCounter:
        counters = [self.fused_preimage(preimage) for preimage in parameter.counters]
        newpreimage = self.new_parameter().counters[0]
        # The following ensures that the new preimage appears at most once in a
        # parameter.
        removed = False
        while True:
            try:
                counters.remove(newpreimage)
                removed = True
            except ValueError:
                break
        if removed:
            counters.append(newpreimage)
        return ParameterCounter(counters)

    def unfused_fused_obs_reqs_and_params(self) -> UninitializedTiling:
        """
        Return the tiling that is created by fusing and then unfusing the tiling.
        """
        obs, reqs, _ = self.fused_obs_reqs_and_params()
        return (
            tuple(self.fuse_map.preimage_gps(obs)),
            tuple(tuple(self.fuse_map.preimage_gps(req)) for req in reqs),
            tuple(),
        )

    def fusable(self) -> bool:
        """
        Return True if tiling is fusable.
        """
        if (self._fuse_row and self._row_idx > self.tiling.dimensions[1] - 2) or (
            not self._fuse_row and self._col_idx > self.tiling.dimensions[0] - 2
        ):
            # Cannot fuse if the row or column index is too big.
            return False
        if any(
            not self.is_fusable_param(parameter) for parameter in self.tiling.parameters
        ):
            return False
        obs, reqs, _ = self.unfused_fused_obs_reqs_and_params()
        unfused_fused_tiling = (
            self.tiling.remove_parameters().add_obstructions_and_requirements(obs, reqs)
        )
        return (
            self.tiling.remove_parameters() == unfused_fused_tiling
            and self._check_fusion_restriction()
        )

    def _check_fusion_restriction(self) -> bool:
        ft = self.fused_tiling()
        if len(ft.parameters) > self.MAX_NUM_PARAMS:
            return False
        eobs, ereqs = self.extra_obs_and_reqs()
        eobs_local = frozenset(filter(GriddedPerm.is_localized, eobs))
        eobs_crossing = frozenset(filter(self._is_crossing, eobs))
        eobs_leaving = frozenset(
            gp for gp in eobs if gp not in eobs_local and gp not in eobs_crossing
        )
        return (
            not ereqs
            and len(eobs) <= self.MAX_NUMBER_EXTRA
            and len(eobs_local) <= self.MAX_NUMBER_EXTRA_LOCAL
            and len(eobs_crossing) <= self.MAX_NUMBER_EXTRA_CROSSING
            and len(eobs_leaving) <= self.MAX_NUMBER_EXTRA_LEAVING
            and max(map(len, eobs), default=0) <= self.MAX_LENGTH_EXTRA
            and max(map(len, eobs_local), default=0) <= self.MAX_LENGTH_EXTRA_LOCAL
            and max(map(len, eobs_crossing), default=0)
            <= self.MAX_LENGTH_EXTRA_CROSSING
            and max(map(len, eobs_leaving), default=0) <= self.MAX_LENGTH_EXTRA_LEAVING
        )

    def _is_crossing(self, gp: GriddedPerm) -> bool:
        """
        Check if the gridded permutation is not localized but stays only in the fuse
        region.
        """
        if self._fuse_row:
            rows = (cell[1] for cell in gp.pos)
            good_rows = (self._row_idx, self._row_idx + 1)
        else:
            rows = (cell[0] for cell in gp.pos)
            good_rows = (self._col_idx, self._col_idx + 1)
        return not gp.is_localized() and all(r in good_rows for r in rows)

    def fused_tiling(self) -> "Tiling":
        """
        Return the fused tiling after applying the fuse map.
        """
        obs, reqs, params = self.fused_obs_reqs_and_params()
        if self.tracked:
            params += (self.new_parameter(),)
        return self.tiling.__class__(obs, reqs, params)

    def new_parameter(self) -> ParameterCounter:
        """
        Return the parameter needed in order to count the fusion.
        """
        return ParameterCounter(
            [PreimageCounter(self.tiling.remove_parameters(), self.fuse_map)]
        )

    def min_left_right_points(self) -> Tuple[int, int]:
        """Return if the left side is positive, else 0 otherwise."""
        left, right = 0, 0
        if self._fuse_row:
            if all(
                cell in self.tiling.positive_cells
                for cell in self.tiling.cells_in_row(self._row_idx)
            ):
                left += 1
            if all(
                cell in self.tiling.positive_cells
                for cell in self.tiling.cells_in_row(self._row_idx + 1)
            ):
                right += 1
        else:
            if all(
                cell in self.tiling.positive_cells
                for cell in self.tiling.cells_in_col(self._col_idx)
            ):
                left += 1
            if all(
                cell in self.tiling.positive_cells
                for cell in self.tiling.cells_in_col(self._col_idx + 1)
            ):
                right += 1
        return left, right

    def is_left_sided_parameter(self, parameter: ParameterCounter) -> bool:
        """
        Return True if active region doesn't overlap the right column/row being fused
        """
        if self._fuse_row:
            return all(
                y != self._row_idx + 1
                for _, y in itertools.chain.from_iterable(
                    parameter.active_regions(self.tiling, True)
                )
            )
        return all(
            x != self._col_idx + 1
            for x, _ in itertools.chain.from_iterable(
                parameter.active_regions(self.tiling, True)
            )
        )

    def is_right_sided_parameter(self, parameter: ParameterCounter) -> bool:
        """
        Return True if active region doesn't overlap the left column/row being fused
        """
        if self._fuse_row:
            return all(
                y != self._row_idx
                for _, y in itertools.chain.from_iterable(
                    parameter.active_regions(self.tiling, True)
                )
            )
        return all(
            x != self._col_idx
            for x, _ in itertools.chain.from_iterable(
                parameter.active_regions(self.tiling, True)
            )
        )

    def extra_obs_and_reqs(
        self,
    ) -> Tuple[List[GriddedPerm], List[Tuple[GriddedPerm, ...]]]:
        ft = self.fused_tiling()
        return self.new_parameter().counters[0].extra_obs_and_reqs(ft)

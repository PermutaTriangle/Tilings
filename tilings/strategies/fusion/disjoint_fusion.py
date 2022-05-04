from typing import Iterator, Optional, Tuple

from comb_spec_searcher import DisjointUnionStrategy, StrategyFactory
from permuta.misc import DIR_NONE
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Fusion


class DisjointFusionStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    def __init__(self, row_idx=None, col_idx=None):
        self.col_idx = col_idx
        self.row_idx = row_idx
        super().__init__(
            ignore_parent=False, inferrable=True, possibly_empty=False, workable=True
        )

    def fusion_algorithm(self, tiling: Tiling) -> Fusion:
        return Fusion(tiling, row_idx=self.row_idx, col_idx=self.col_idx, tracked=False)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        algo = self.fusion_algorithm(comb_class)
        if algo.fusable():
            fused_tiling = algo.fused_tiling()
            res = [fused_tiling]
            for gp in algo.new_assumption().gps:
                cell = gp.pos[0]
                res.append(fused_tiling.place_point_in_cell(cell, DIR_NONE))
            return tuple(res)

    def formal_step(self) -> str:
        if self.row_idx is not None:
            return f"fuse rows {self.row_idx} and {self.row_idx + 1}"
        return f"fuse cols {self.col_idx} and {self.col_idx + 1}"

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        if children is None:
            children = self.decomposition_function(comb_class)
        raise NotImplementedError

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        raise NotImplementedError

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["row"] = self.row_idx
        d["col"] = self.col_idx
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "DisjointFusionStrategy":
        return cls(row_idx=d["row"], col_idx=d["col"])

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + f"(row_idx={self.row_idx}, col_idx={self.col_idx})"
        )


class DisjointFusionFactory(StrategyFactory[Tiling]):
    def __call__(self, comb_class: Tiling) -> Iterator[DisjointFusionStrategy]:
        cols, rows = comb_class.dimensions
        for row_idx in range(rows - 1):
            yield DisjointFusionStrategy(row_idx=row_idx)
        for col_idx in range(cols - 1):
            yield DisjointFusionStrategy(col_idx=col_idx)

    def __str__(self) -> str:
        return "disjoint fusion strategy"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d: dict) -> "DisjointFusionFactory":
        return cls()

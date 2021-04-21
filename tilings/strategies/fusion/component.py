from typing import Iterator, Optional, Tuple

from comb_spec_searcher import StrategyFactory
from comb_spec_searcher.strategies import Rule
from tilings import GriddedPerm, Tiling
from tilings.algorithms import ComponentFusion, Fusion

from .fusion import FusionStrategy


class ComponentFusionStrategy(FusionStrategy):
    def fusion_algorithm(self, tiling: Tiling) -> Fusion:
        return ComponentFusion(
            tiling, row_idx=self.row_idx, col_idx=self.col_idx, tracked=self.tracked
        )

    def formal_step(self) -> str:
        fusing = "rows" if self.row_idx is not None else "columns"
        idx = self.row_idx if self.row_idx is not None else self.col_idx
        return "component fuse {} {} and {}".format(fusing, idx, idx + 1)

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
        left_points: Optional[int] = None,
    ) -> Iterator[GriddedPerm]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        raise NotImplementedError


class ComponentFusionFactory(StrategyFactory[Tiling]):
    def __init__(self, tracked: bool = False, isolation_level: Optional[str] = None):
        self.tracked = tracked
        self.isolation_level = isolation_level

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[Rule]:
        if comb_class.requirements:
            return
        cols, rows = comb_class.dimensions
        for row_idx in range(rows - 1):
            algo = ComponentFusion(
                comb_class,
                row_idx=row_idx,
                tracked=self.tracked,
                isolation_level=self.isolation_level,
            )
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield ComponentFusionStrategy(row_idx=row_idx, tracked=self.tracked)(
                    comb_class, (fused_tiling,)
                )
        for col_idx in range(cols - 1):
            algo = ComponentFusion(
                comb_class,
                col_idx=col_idx,
                tracked=self.tracked,
                isolation_level=self.isolation_level,
            )
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield ComponentFusionStrategy(col_idx=col_idx, tracked=self.tracked)(
                    comb_class, (fused_tiling,)
                )

    def __str__(self) -> str:
        return f"{'tracked ' if self.tracked else ''}component fusion"

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + f"(tracked={self.tracked}, isolation_level={self.isolation_level})"
        )

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["tracked"] = self.tracked
        d["isolation_level"] = self.isolation_level
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ComponentFusionFactory":
        return cls(**d)

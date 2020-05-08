from itertools import chain
from sympy import Eq, Function
from typing import Iterator, Optional, Tuple, Type

from comb_spec_searcher import (
    CombinatorialObject,
    Constructor,
    StrategyGenerator,
    Strategy,
)
from comb_spec_searcher.strategies.constructor import (
    RelianceProfile,
    SubGens,
    SubRecs,
    SubSamplers,
)
from tilings import GriddedPerm, Tiling
from tilings.algorithms import ComponentFusion, Fusion

__all__ = ["FusionStrategy", "ComponentFusionStrategy"]


class FusionConstructor(Constructor):
    # def __init__(self):
    #     super().__init__()

    def is_equivalence(self) -> bool:
        return False

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        raise NotImplementedError

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
        raise NotImplementedError

    def get_sub_objects(
        self, subgens: SubGens, n: int, **parameters: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        raise NotImplementedError

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int
    ):
        raise NotImplementedError

    @staticmethod
    def get_eq_symbol() -> str:
        # return "\u2192"
        # return "╬"
        # return "\u27fc"
        # return "⤅"
        return "↣"


class FusionStrategy(Strategy[Tiling]):
    def __init__(self, row_idx=None, col_idx=None):
        self.col_idx = col_idx
        self.row_idx = row_idx
        if not sum(1 for x in (self.col_idx, self.row_idx) if x is not None) == 1:
            raise RuntimeError("Cannot specify a row and a columns")
        super().__init__(
            ignore_parent=False, inferrable=True, possibly_empty=False, workable=True
        )

    def fusion_algorithm(self, tiling: Tiling) -> Fusion:
        return Fusion(tiling, row_idx=self.row_idx, col_idx=self.col_idx)

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, ...]:
        algo = self.fusion_algorithm(tiling)
        if algo.fusable():
            return (algo.fused_tiling(),)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        return FusionConstructor()

    def formal_step(self) -> str:
        fusing = "rows" if self.row_idx is not None else "columns"
        idx = self.row_idx if self.row_idx is not None else self.col_idx
        return "fuse {} {} and {}".format(fusing, idx, idx + 1)

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[GriddedPerm, ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> GriddedPerm:
        """
        The forward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)
        raise NotImplementedError

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm, ...]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)
        raise NotImplementedError

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["row_idx"] = self.row_idx
        d["col_dix"] = self.col_idx

    @classmethod
    def from_dict(cls, d: dict) -> "FusionStrategy":
        return cls(row_idx=d.get("row_idx"), col_idx="col_idx")


class ComponentFusionConstructor(FusionConstructor):
    pass


class ComponentFusionStrategy(FusionStrategy):
    def fusion_algorithm(self, tiling: Tiling) -> Fusion:
        return ComponentFusion(tiling, row_idx=self.row_idx, col_idx=self.col_idx)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        return ComponentFusionConstructor()

    def formal_step(self) -> str:
        fusing = "rows" if self.row_idx is not None else "columns"
        idx = self.row_idx if self.row_idx is not None else self.col_idx
        return "fuse component {} {} and {}".format(fusing, idx, idx + 1)


class FusionStrategyGenerator(StrategyGenerator[Tiling]):
    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[FusionStrategy]:
        cols, rows = comb_class.dimensions
        for row_idx in range(rows - 1):
            algo = Fusion(comb_class, row_idx=row_idx)
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield FusionStrategy(row_idx=row_idx)(comb_class, (fused_tiling,))
        for col_idx in range(cols - 1):
            algo = Fusion(comb_class, col_idx=col_idx)
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield FusionStrategy(col_idx=col_idx)(comb_class, (fused_tiling,))

    def __str__(self) -> str:
        return "fusion"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d: dict) -> "FusionStrategyGenerator":
        return cls()


class ComponentFusionStrategyGenerator(StrategyGenerator[Tiling]):
    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[FusionStrategy]:
        if comb_class.requirements:
            return
        cols, rows = comb_class.dimensions
        for row_idx in range(rows - 1):
            algo = ComponentFusion(comb_class, row_idx=row_idx)
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield FusionStrategy(row_idx=row_idx)(comb_class, (fused_tiling,))
        for col_idx in range(cols - 1):
            algo = ComponentFusion(comb_class, col_idx=col_idx)
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield FusionStrategy(col_idx=col_idx)(comb_class, (fused_tiling,))

    def __str__(self) -> str:
        return "fusion"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d: dict) -> "ComponentFusionStrategyGenerator":
        return cls()

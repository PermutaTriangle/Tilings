from itertools import chain
from typing import Iterator, Type

from comb_spec_searcher import Rule
from tilings import Tiling
from tilings.algorithms import ComponentFusion, Fusion
from tilings.strategies.abstract_strategy import Strategy

__all__ = ["FusionStrategy", "ComponentFusionStrategy"]


def _general_fusion_iterator(
    tiling: Tiling, fusion_class: Type[Fusion]
) -> Iterator[Rule]:
    """
    Generator over rules found by fusing rows or columns of `tiling` using
    the fusion defined by `fusion_class`.
    """
    assert issubclass(fusion_class, Fusion)
    ncol = tiling.dimensions[0]
    nrow = tiling.dimensions[1]
    possible_fusion = chain(
        (fusion_class(tiling, row_idx=r) for r in range(nrow - 1)),
        (fusion_class(tiling, col_idx=c) for c in range(ncol - 1)),
    )
    return (fusion.rule() for fusion in possible_fusion if fusion.fusable())


class FusionStrategy(Strategy):
    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Rule]:
        return _general_fusion_iterator(tiling, Fusion)

    def __str__(self) -> str:
        return "fusion"

    def __repr__(self) -> str:
        return "FusionStrategy()"

    @classmethod
    def from_dict(cls, d: dict) -> "FusionStrategy":
        return cls()


class ComponentFusionStrategy(Strategy):
    """
    Yield rules found by fusing rows and columns of a tiling, where the
    unfused tiling obtained by drawing a line through certain heights/indices
    of the row/column.
    """

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Rule]:
        if tiling.requirements:
            return iter([])
        return _general_fusion_iterator(tiling, ComponentFusion)

    def __str__(self) -> str:
        return "component fusion"

    def __repr__(self) -> str:
        return "ComponentFusion()"

    @classmethod
    def from_dict(cls, d: dict) -> "ComponentFusionStrategy":
        return cls()

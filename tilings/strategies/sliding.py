from typing import Iterator, Optional, Tuple

from comb_spec_searcher.strategies.strategy import (
    DisjointUnionStrategy,
    StrategyFactory,
)
from tilings import GriddedPerm, Tiling
from tilings.algorithms import get_col_info, slidable_pairs, slide_column


class SliddingStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    """
    A class for a specific slidding strategy. The init probably gets the index of both
    column you slidding.
    """

    def __init__(self, av_12_column: int, av_123_column: int, col_info):
        self.av_12 = av_12_column
        self.av_123 = av_123_column
        self.col_info = col_info

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling]:
        """Return the slidded tiling if it slides, otherwise None."""
        return (slide_column(tiling, self.av_12, self.av_123, self.col_info),)

    def formal_step(self) -> str:
        return f"slide {self.av_123} through {self.av_12}"

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm]:
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, d: dict) -> "SliddingStrategy":
        raise NotImplementedError()


class SliddingFactory(StrategyFactory[Tiling]):
    """
    A strategy factory is producing all the valid strategies of a given type that can
    apply to the given tiling.

    Here you want the call the method to return all the valid sliding strategy for the
    given tiling.
    """

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[SliddingStrategy]:
        col_info = get_col_info(comb_class)
        return (
            SliddingStrategy(*pair, col_info)
            for pair in slidable_pairs(comb_class, col_info)
        )

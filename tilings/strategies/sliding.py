from typing import DefaultDict, Dict, Iterator, List, Optional, Tuple

from comb_spec_searcher.strategies.strategy import (
    DisjointUnionStrategy,
    StrategyFactory,
)
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import (
    get_col_info,
    gp_slide,
    gp_slide_inverse,
    slidable_pairs,
    slide_assumption,
    slide_column,
)


class SlidingStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    """
    A class for a specific slidding strategy. The init probably gets the index of both
    column you slidding.
    """

    def __init__(
        self,
        av_12_column: int,
        av_123_column: int,
        col_info: DefaultDict[int, DefaultDict[int, Dict[GriddedPerm, List[int]]]],
    ):
        super().__init__(possibly_empty=True)
        self.av_12 = av_12_column
        self.av_123 = av_123_column
        self.col_info = col_info

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling]:
        """Return the slidded tiling if it slides, otherwise None."""
        return (slide_column(tiling, self.av_12, self.av_123, self.col_info),)

    def formal_step(self) -> str:
        return f"slide {self.av_123} through {self.av_12}"

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        # TODO: generalize gp_slide to disregard order
        if self.av_12 < self.av_123:
            yield from (
                gp_slide_inverse(gp, self.av_12, self.av_123)
                for gp in gps
                if gp is not None
            )
        else:
            for gp in gps:
                if gp is None:
                    continue
                p = list(range(len(gp)))
                p[self.av_123] = self.av_12
                p[self.av_12] = self.av_123
                perm = Perm(p)
                yield gp_slide_inverse(
                    gp.permute_columns(perm), self.av_123, self.av_12
                ).permute_columns(perm.inverse())

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm]:
        # TODO: generalize gp_slide_inv to disregard order
        if self.av_123 < self.av_12:
            return (gp_slide(gp, self.av_123, self.av_12),)
        p = list(range(len(gp)))
        p[self.av_123] = self.av_12
        p[self.av_12] = self.av_123
        perm = Perm(p)
        gp.permute_columns(perm)
        return (gp_slide(gp, self.av_12, self.av_123).permute_columns(perm.inverse()),)

    @classmethod
    def from_dict(cls, d: dict) -> "SlidingStrategy":
        raise NotImplementedError()

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if not comb_class.extra_parameters:
            return super().extra_parameters(comb_class, children)
        if children is None:
            children = self.decomposition_function(comb_class)
        child = children[0]
        return (
            {
                comb_class.get_assumption_parameter(
                    ass
                ): child.get_assumption_parameter(
                    slide_assumption(ass, self.av_12, self.av_123)
                )
                for ass in comb_class.assumptions
            },
        )


class SlidingFactory(StrategyFactory[Tiling]):
    """
    A strategy factory is producing all the valid strategies of a given type that can
    apply to the given tiling.

    Here you want the call the method to return all the valid sliding strategy for the
    given tiling.
    """

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[SlidingStrategy]:
        col_info = get_col_info(comb_class)
        for pair in slidable_pairs(comb_class, col_info):
            print(comb_class, flush=True)
            yield SlidingStrategy(*pair, col_info)

    def __repr__(self) -> str:
        return "--SlideFactoryPlaceholderRepr--"

    def __str__(self) -> str:
        return "--SlideFactoryPlaceholderStr--"

    @classmethod
    def from_dict(cls, d: dict) -> "SlidingFactory":
        """
        Return the strategy from the json representation.
        """
        raise NotImplementedError()

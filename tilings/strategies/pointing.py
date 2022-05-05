"""
The directionless point placement strategy that is counted
by the 'pointing' constructor.
"""
from typing import Dict, Iterator, Optional, Tuple

from comb_spec_searcher import Strategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from permuta.misc import DIR_NONE
from tilings import GriddedPerm, Tiling

from .unfusion import DivideByN, ReverseDivideByN


class PointingStrategy(Strategy[Tiling, GriddedPerm]):
    def can_be_equivalent(self) -> bool:
        return False

    def is_two_way(self, comb_class: Tiling) -> bool:
        return True

    def is_reversible(self, comb_class: Tiling) -> bool:
        return True

    def shifts(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]],
    ) -> Tuple[int, ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        assert children is not None
        return tuple(0 for _ in children)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        cells = comb_class.active_cells - comb_class.point_cells
        if cells:
            return tuple(
                comb_class.place_point_in_cell(cell, DIR_NONE) for cell in cells
            )
        raise StrategyDoesNotApply("The tiling is just point cells!")

    def formal_step(self) -> str:
        return "directionless point placement"

    def constructor(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> DivideByN:
        if children is None:
            children = self.decomposition_function(comb_class)
        return DivideByN(comb_class, children, -len(comb_class.point_cells))

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> ReverseDivideByN:
        if children is None:
            children = self.decomposition_function(comb_class)
        return ReverseDivideByN(comb_class, children, idx, -len(comb_class.point_cells))

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

    def extra_parameters(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Dict[str, str], ...]:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> "PointingStrategy":
        return cls(**d)

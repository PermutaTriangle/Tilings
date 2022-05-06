"""
The directionless point placement strategy that is counted
by the 'pointing' constructor.
"""
from typing import Dict, Iterator, Optional, Tuple

from comb_spec_searcher import Strategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from permuta.misc import DIR_NONE
from tilings import GriddedPerm, Tiling
from tilings.algorithms import RequirementPlacement

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
                comb_class.place_point_in_cell(cell, DIR_NONE) for cell in sorted(cells)
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
        return DivideByN(
            comb_class,
            children,
            -len(comb_class.point_cells),
            self.extra_parameters(comb_class, children),
        )

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> ReverseDivideByN:
        if children is None:
            children = self.decomposition_function(comb_class)
        return ReverseDivideByN(
            comb_class,
            children,
            idx,
            -len(comb_class.point_cells),
            self.extra_parameters(comb_class, children),
        )

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
        if children is None:
            children = self.decomposition_function(comb_class)
        cells = comb_class.active_cells - comb_class.point_cells
        algo = RequirementPlacement(comb_class, True, True)
        res = []
        for child, cell in zip(children, sorted(cells)):
            params: Dict[str, str] = {}
            mapped_assumptions = [
                child.forward_map.map_assumption(ass).avoiding(child.obstructions)
                for ass in algo.stretched_assumptions(cell)
            ]
            for ass, mapped_ass in zip(comb_class.assumptions, mapped_assumptions):
                if mapped_ass.gps:
                    params[
                        comb_class.get_assumption_parameter(ass)
                    ] = child.get_assumption_parameter(mapped_ass)
            res.append(params)
        return tuple(res)

    @classmethod
    def from_dict(cls, d: dict) -> "PointingStrategy":
        return cls(**d)

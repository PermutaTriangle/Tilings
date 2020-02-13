from typing import Iterator

from comb_spec_searcher import Rule
from tilings import Tiling
from tilings.algorithms import RequirementPlacement
from tilings.strategies.abstract_strategy import Strategy

__all__ = ['RequirementPlacementStrategy']


class RequirementPlacementStrategy(Strategy):
    """
    Strategy that places a single forced point of a requirement.
    Yield all possible rules coming from placing a point of a pattern that
    occurs as a subpattern of requirement containing a single pattern.

    INPUTS:
        - `point_only`: only place point for length 1 subpattern.
        - `partial`: places only the point on its own row or its own column.
    """
    def __init__(self, point_only: bool, partial: bool = False):
        self.point_only = point_only
        self.partial = partial

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Rule]:
        if self.partial:
            req_placements = [RequirementPlacement(tiling, own_row=False),
                              RequirementPlacement(tiling, own_col=False)]
        else:
            req_placements = [RequirementPlacement(tiling)]
        for req_placement in req_placements:
            if self.point_only:
                yield from req_placement.all_point_placement_rules()
            else:
                yield from req_placement.all_requirement_placement_rules()

    def __str__(self) -> str:
        s = 'partial ' if self.partial else ''
        s += 'point' if self.point_only else 'requirement'
        s += 'placement'
        return s

    def __repr__(self) -> str:
        return ('RequirementPlacementStrategy(point_only={}, partial={})'
                .format(self.point_only, self.partial))

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d['point_only'] = self.point_only
        d['partial'] = self.partial
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'RequirementPlacementStrategy':
        return cls(**d)

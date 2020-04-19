from typing import Iterator, List, Optional

from comb_spec_searcher import Strategy
from permuta import Av, Perm
from tilings import Tiling
from tilings.algorithms import (
    CellInsertion,
    CrossingInsertion,
    FactorInsertion,
    RequirementCorroboration,
    RequirementExtension,
    RequirementPlacement,
)

__all__ = [
    "RowAndColumnPlacementStrategy",
    "AllPlacementsStrategy",
]


class RowAndColumnPlacementStrategy(Strategy):
    def __init__(self, place_row: bool, place_col: bool, partial: bool = False) -> None:
        assert place_col or place_row, "Must place column or row"
        self.place_row = place_row
        self.place_col = place_col
        self.partial = partial

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        if self.partial:
            req_placements = [
                RequirementPlacement(tiling, own_row=False),
                RequirementPlacement(tiling, own_col=False),
            ]
        else:
            req_placements = [RequirementPlacement(tiling)]
        for req_placement in req_placements:
            if self.place_row:
                yield from req_placement.all_row_placement_rules()
            if self.place_col:
                yield from req_placement.all_col_placement_rules()

    def __str__(self) -> str:
        s = "{} placement"
        if self.place_col and self.place_col:
            s = s.format("row and column")
        elif self.place_row:
            s = s.format("row")
        else:
            s = s.format("column")
        if self.partial:
            s = " ".join(["partial", s])
        return s

    def __repr__(self) -> str:
        return (
            "RowAndColumnPlacementStrategy(place_row={}, "
            "place_col={}, partial={})".format(
                self.place_row, self.place_col, self.partial
            )
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["place_row"] = self.place_row
        d["place_col"] = self.place_col
        d["partial"] = self.partial
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RowAndColumnPlacementStrategy":
        return cls(**d)


class AllPlacementsStrategy(Strategy):
    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        req_placements = (
            RequirementPlacement(tiling),
            RequirementPlacement(tiling, own_row=False),
            RequirementPlacement(tiling, own_col=False),
        )
        for req_placement in req_placements:
            yield from req_placement.all_point_placement_rules()
            yield from req_placement.all_requirement_placement_rules()
            yield from req_placement.all_col_placement_rules()
            yield from req_placement.all_row_placement_rules()

    def __str__(self) -> str:
        return "all placements"

    def __repr__(self) -> str:
        return "AllPlacementsStrategy()"

    @classmethod
    def from_dict(cls, d: dict) -> "AllPlacementsStrategy":
        return AllPlacementsStrategy()

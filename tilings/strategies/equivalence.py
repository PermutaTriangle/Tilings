from typing import Iterable, Iterator

from comb_spec_searcher import Rule
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import Tiling
from tilings.algorithms import RequirementPlacement
from tilings.strategies.abstract_strategy import Strategy

__all__ = ["RequirementPlacementStrategy"]


class RequirementPlacementStrategy(Strategy):
    """
    Strategy that places a single forced point of a requirement.
    Yield all possible rules coming from placing a point of a pattern that
    occurs as a subpattern of requirement containing a single pattern.

    INPUTS:
        - `point_only`: only place point for length 1 subpattern.
        - `partial`: places only the point on its own row or its own column.
        - `ignore_parent`: indicate if the rule should ignore parent
        - `dirs`: The directions used for placement (default to all
          directions).
          The possible directions are:
            - `permuta.misc.DIR_NORTH`
            - `permuta.misc.DIR_SOUTH`
            - `permuta.misc.DIR_EAST`
            - `permuta.misc.DIR_WEST`
    """

    def __init__(
        self,
        point_only: bool = False,
        partial: bool = False,
        ignore_parent: bool = False,
        dirs: Iterable[int] = tuple(DIRS),
    ):
        assert all(d in DIRS for d in dirs), "Got an invalid direction"
        self.point_only = point_only
        self.partial = partial
        self.ignore_parent = ignore_parent
        self.dirs = tuple(dirs)

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Rule]:
        if self.partial:
            req_placements = [
                RequirementPlacement(tiling, own_row=False, dirs=self.dirs),
                RequirementPlacement(tiling, own_col=False, dirs=self.dirs),
            ]
        else:
            req_placements = [RequirementPlacement(tiling, dirs=self.dirs)]
        for req_placement in req_placements:
            if self.point_only:
                yield from req_placement.all_point_placement_rules(self.ignore_parent)
            else:
                yield from req_placement.all_requirement_placement_rules(
                    self.ignore_parent
                )

    def __str__(self) -> str:
        s = "partial " if self.partial else ""
        s += "point" if self.point_only else "requirement"
        s += " placement"
        if len(self.dirs) < 4:
            dir_str = {
                DIR_NORTH: "north",
                DIR_SOUTH: "south",
                DIR_EAST: "east",
                DIR_WEST: "west",
            }
            if len(self.dirs) == 1:
                s += " in direction {}".format(dir_str[self.dirs[0]])
            else:
                s += " in directions ".format()
                s += ", ".join(dir_str[d] for d in self.dirs[:-1])
                s += " and {}".format(dir_str[self.dirs[-1]])
        if self.ignore_parent:
            s += " (ignore parent)"
        return s

    def __repr__(self) -> str:
        dir_repr = {
            DIR_NORTH: "DIR_NORTH",
            DIR_SOUTH: "DIR_SOUTH",
            DIR_WEST: "DIR_WEST",
            DIR_EAST: "DIR_EAST",
        }
        if len(self.dirs) < 4:
            dir_arg = ", dirs=({},)".format(", ".join(dir_repr[d] for d in self.dirs))
        else:
            dir_arg = ""
        return (
            "RequirementPlacementStrategy(point_only={}, partial={},"
            " ignore_parent={}{})".format(
                self.point_only, self.partial, self.ignore_parent, dir_arg
            )
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["point_only"] = self.point_only
        d["partial"] = self.partial
        d["ignore_parent"] = self.ignore_parent
        d["dirs"] = self.dirs
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementPlacementStrategy":
        return cls(**d)

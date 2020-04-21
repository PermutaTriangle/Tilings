from typing import Dict, FrozenSet, Iterable, Iterator, Optional, Tuple

from comb_spec_searcher import DisjointUnionStrategy, Rule, Strategy, StrategyGenerator
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import GriddedPerm, Tiling
from tilings.algorithms import RequirementPlacement

__all__ = [
    "RequirementPlacementStrategy",
    "RowAndColumnPlacementStrategy",
    "AllPlacementsStrategy",
]

Cell = Tuple[int, int]


class RequirementPlacementStrategy(DisjointUnionStrategy):
    def __init__(
        self,
        gps: Tuple[GriddedPerm, ...],
        indices: Tuple[int, ...],
        direction: int,
        own_col: bool = True,
        own_row: bool = True,
        ignore_parent: bool = False,
    ):
        self.gps = gps
        self.indices = indices
        self.direction = direction
        self.own_row, self.own_col = own_row, own_col
        super().__init__(ignore_parent=ignore_parent)

    def placement_class(self, tiling: Tiling):
        return RequirementPlacement(tiling, own_col=self.own_col, own_row=self.own_row)

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, ...]:
        placement_class = self.placement_class(tiling)
        return placement_class.place_point_of_req(
            self.gps, self.indices, self.direction
        )

    def direction_string(self):
        if self.direction == DIR_EAST:
            return "rightmost"
        if self.direction == DIR_NORTH:
            return "topmost"
        if self.direction == DIR_WEST:
            return "leftmost"
        if self.direction == DIR_SOUTH:
            return "bottommost"

    def formal_step(self):
        if len(self.gps) == 1:
            gp = self.gps[0]
            if len(gp) == 1:
                return "Placing the {} point in cell {}.".format(
                    self.direction_string(), self.gp.pos[self.index]
                )
            if self.gp.is_localized():
                return "Placing the {} {} point in {} in cell {}.".format(
                    self.direction_string(),
                    (self.index, self.gp.patt[self.index]),
                    self.gp.patt,
                    self.gp.pos[self.index],
                )
            return "Placing the {} {} point in {}.".format(
                self.direction_string(), (self.index, self.gp.patt[self.index]), self.gp
            )
        else:
            return "Placing the {} point at indices {} from the requirement ({}).".format(
                self.direction_string(),
                self.indices,
                ", ".join(str(gp) for gp in self.gps),
            )

    def backward_cell_map(self, tiling: Tiling) -> Dict[Cell, Cell]:
        return {
            c: cell
            for cell in tiling.active_cells
            for c in self.forward_cell_map(tiling, cell)
        }

    def forward_cell_map(self, tiling: Tiling, cell: Cell) -> FrozenSet[Cell]:
        x, y = self.gp.pos[self.index]
        minx = cell[0] if cell[0] <= x else cell[0] + 3
        maxx = cell[0] + 3 if cell[0] >= x else cell[0]
        miny = cell[1] if cell[1] <= y else cell[1] + 3
        maxy = cell[1] + 3 if cell[1] >= y else cell[1]
        return frozenset((i, j) for i in range(minx, maxx) for j in range(miny, maxy))

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[GriddedPerm, ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> GriddedPerm:
        if children is None:
            children = self.decomposition_function(tiling)
        gp = gps[0]
        gp = children[0].backward_map(gp)
        backmap = self.backward_cell_map(tiling)
        return GriddedPerm(gp.patt, [backmap[cell] for cell in gp.pos])

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm, ...]:
        if children is None:
            children = self.decomposition_function(tiling)
        placement_class = self.placement_class(tiling)
        forced_index = None  # TODO: compute index of point being placed
        placed_gp = placement_class._gridded_perm_translation_with_point(
            self.gp, forced_index
        )
        return children[0].forward_map(placed_gp)


class RequirementPlacementStrategyGenerator(StrategyGenerator):
    """
    Base class for requirement placement on tilings.

    It will create batch rules based on placing the direction most points
    at indices i1, ..., ik in the gridded perms g1, ..., gk, respectively.

    The point placements yielded are determined by the
    'req_indices_and_directions_to_place' function.
    """

    def __init__(
        self,
        partial: bool = False,
        ignore_parent: bool = False,
        dirs: Iterable[int] = tuple(DIRS),
    ):
        assert all(d in DIRS for d in dirs), "Got an invalid direction"
        self.partial = partial
        self.ignore_parent = ignore_parent
        self.dirs = tuple(dirs)

    @abc.abstractmethod
    def req_indices_and_directions_to_place(
        self, tiling: Tiling
    ) -> Iterable[Tuple[Tuple[GriddedPerm, ...], Tuple[int, ...], int]]:
        """
        Iterator over all requirement lists, indices and directions to place.
        """

    def req_placements(self, tiling: Tiling):
        """
        Return the RequiremntPlacement classes used to place the points.
        """
        if self.partial:
            req_placements = (
                RequirementPlacement(tiling, own_row=False),
                RequirementPlacement(tiling, own_col=False),
            )
        else:
            req_placements = (RequirementPlacement(tiling),)
        return req_placements

    def __call__(self, tiling: Tiling) -> Iterator[Rule]:
        for req_placement, (gps, indices, direction) in zip(
            self.req_placements(tiling),
            self.req_indices_and_directions_to_place(tiling),
        ):
            strategy = req_placement(
                gps, indices, direction, ignore_parent=self.ignore_parent
            )
            children = req_placement.place_point_of_req_list(gps, indices, direction)
            yield strategy(tiling, children)


class RequirementPlacementStrategy(RequirementPlacementStrategyGenerator):
    """
    Strategy that places a single forced point of a gridded permutation.
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
        super().__init__(partial=partial, ignore_parent=ignore_parent, dirs=dirs)

    def req_indices_and_directions_to_place(self, tiling: Tiling):
        # TODO: continue here, need the req placement class to use the _already placed method

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
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


# class RowAndColumnPlacementStrategy(Strategy):
#     def __init__(self, place_row: bool, place_col: bool, partial: bool = False) -> None:
#         assert place_col or place_row, "Must place column or row"
#         self.place_row = place_row
#         self.place_col = place_col
#         self.partial = partial

#     def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
#         if self.partial:
#             req_placements = [
#                 RequirementPlacement(tiling, own_row=False),
#                 RequirementPlacement(tiling, own_col=False),
#             ]
#         else:
#             req_placements = [RequirementPlacement(tiling)]
#         for req_placement in req_placements:
#             if self.place_row:
#                 yield from req_placement.all_row_placement_rules()
#             if self.place_col:
#                 yield from req_placement.all_col_placement_rules()

#     def __str__(self) -> str:
#         s = "{} placement"
#         if self.place_col and self.place_col:
#             s = s.format("row and column")
#         elif self.place_row:
#             s = s.format("row")
#         else:
#             s = s.format("column")
#         if self.partial:
#             s = " ".join(["partial", s])
#         return s

#     def __repr__(self) -> str:
#         return (
#             "RowAndColumnPlacementStrategy(place_row={}, "
#             "place_col={}, partial={})".format(
#                 self.place_row, self.place_col, self.partial
#             )
#         )

#     def to_jsonable(self) -> dict:
#         d = super().to_jsonable()
#         d["place_row"] = self.place_row
#         d["place_col"] = self.place_col
#         d["partial"] = self.partial
#         return d

#     @classmethod
#     def from_dict(cls, d: dict) -> "RowAndColumnPlacementStrategy":
#         return cls(**d)


# class AllPlacementsStrategy(Strategy):
#     def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
#         req_placements = (
#             RequirementPlacement(tiling),
#             RequirementPlacement(tiling, own_row=False),
#             RequirementPlacement(tiling, own_col=False),
#         )
#         for req_placement in req_placements:
#             yield from req_placement.all_point_placement_rules()
#             yield from req_placement.all_requirement_placement_rules()
#             yield from req_placement.all_col_placement_rules()
#             yield from req_placement.all_row_placement_rules()

#     def __str__(self) -> str:
#         return "all placements"

#     def __repr__(self) -> str:
#         return "AllPlacementsStrategy()"

#     @classmethod
#     def from_dict(cls, d: dict) -> "AllPlacementsStrategy":
#         return AllPlacementsStrategy()

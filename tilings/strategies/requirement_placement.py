from collections import defaultdict
from itertools import chain, product
from typing import Dict, FrozenSet, Iterable, Iterator, Optional, Tuple
import abc

from comb_spec_searcher import DisjointUnionStrategy, Rule, Strategy, StrategyGenerator
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import GriddedPerm, Tiling
from tilings.algorithms import RequirementPlacement

__all__ = [
    "PatternPlacementStrategy",
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
        include_empty: bool = False,
    ):
        self.gps = gps
        self.indices = indices
        self.direction = direction
        self.own_row, self.own_col = own_row, own_col
        self.include_empty = include_empty
        super().__init__(ignore_parent=ignore_parent)

    def placement_class(self, tiling: Tiling):
        return RequirementPlacement(tiling, own_col=self.own_col, own_row=self.own_row)

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, ...]:
        placement_class = self.placement_class(tiling)
        return (
            (tiling.add_obstructions(self.gps),) if self.include_empty else tuple()
        ) + placement_class.place_point_of_req(self.gps, self.indices, self.direction)

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
        placing = "{}lacing the {} ".format(
            "P" if (self.own_col and self.own_row) else "Partially p",
            self.direction_string(),
        )
        if len(self.gps) == 1:
            gp = self.gps[0]
            index = self.indices[0]
            if len(gp) == 1:
                return placing + "point in cell {}.".format(gp.pos[index])
            if gp.is_localized():
                return placing + "{} point in {} in cell {}.".format(
                    (index, gp.patt[index]), gp.patt, gp.pos[index],
                )
            return placing + "{} point in {}.".format((index, gp.patt[index]), gp)
        if all(len(gp) == 1 for gp in self.gps):
            row_indices = set(x for x, _ in [gp.pos[0] for gp in self.gps])
            if len(row_indices) == 1:
                return placing + "point in col {}.".format(row_indices.pop())
            col_indices = set(y for _, y in [gp.pos[0] for gp in self.gps])
            if len(col_indices) == 1:
                return placing + "point in row {}.".format(row_indices.pop())
        return placing + "point at indices {} from the requirement ({}).".format(
            self.indices, ", ".join(str(gp) for gp in self.gps),
        )

    def backward_cell_map(self, tiling: Tiling, placed_cell: Cell) -> Dict[Cell, Cell]:
        return {
            x: cell
            for cell in tiling.active_cells
            for x in self.forward_cell_map(tiling, placed_cell, cell)
        }

    def forward_cell_map(
        self, tiling: Tiling, placed_cell: Cell, cell: Cell
    ) -> FrozenSet[Cell]:
        x, y = placed_cell
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
        idx = DisjointUnionStrategy.backward_map_index(gps)
        gp = children[idx].backward_map(gps[idx])
        if self.include_empty:
            if idx == 0:
                return gp
            idx -= 1
        placed_cell = self.gps[idx].pos[self.indices[idx]]
        backmap = self.backward_cell_map(tiling, placed_cell)
        return GriddedPerm(gp.patt, [backmap[cell] for cell in gp.pos])

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm, ...]:
        raise NotImplementedError

    #     if children is None:
    #         children = self.decomposition_function(tiling)
    #     placement_class = self.placement_class(tiling)
    #     forced_index = None  # TODO: compute index of point being placed
    #     placed_gp = placement_class._gridded_perm_translation_with_point(
    #         self.gp, forced_index
    #     )
    #     return children[0].forward_map(placed_gp)


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
        include_empty: bool = False,
    ):
        assert all(d in DIRS for d in dirs), "Got an invalid direction"
        self.partial = partial
        self.ignore_parent = ignore_parent
        self.dirs = tuple(dirs)
        self.include_empty = include_empty

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

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Rule]:
        for req_placement, (gps, indices, direction) in zip(
            self.req_placements(tiling),
            self.req_indices_and_directions_to_place(tiling),
        ):
            if (
                direction in req_placement.directions
                and not req_placement.already_placed(gps, indices)
            ):
                strategy = RequirementPlacementStrategy(
                    gps,
                    indices,
                    direction,
                    own_row=req_placement.own_row,
                    own_col=req_placement.own_col,
                    ignore_parent=self.ignore_parent,
                    include_empty=self.include_empty,
                )
                children = (
                    (tiling.add_obstructions(gps),) if self.include_empty else tuple()
                ) + req_placement.place_point_of_req(gps, indices, direction)
                yield strategy(tiling, children)

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["partial"] = self.partial
        d["ignore_parent"] = self.ignore_parent
        d["dirs"] = self.dirs
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementPlacementStrategyGenerator":
        return cls(**d)


class PatternPlacementStrategy(RequirementPlacementStrategyGenerator):
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

    def req_indices_and_directions_to_place(
        self, tiling: Tiling
    ) -> Iterable[Tuple[Tuple[GriddedPerm, ...], Tuple[int, ...], int]]:
        """
        If point_only, then yield all size one gps, in order to
        """
        if self.point_only:
            for cell in tiling.positive_cells:
                gps = (GriddedPerm(Perm((0,)), (cell,)),)
                indices = (0,)
                for direction in self.dirs:
                    yield gps, indices, direction
        else:
            subgps = set(
                chain.from_iterable(
                    req[0].all_subperms(proper=False)
                    for req in tiling.requirements
                    if len(req) == 1
                )
            )
            for gp in subgps:
                for index, direction in product(range(len(gp)), self.dirs):
                    yield (gp,), (index,), direction

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
            "PatternPlacementStrategy(point_only={}, partial={},"
            " ignore_parent={}{})".format(
                self.point_only, self.partial, self.ignore_parent, dir_arg
            )
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["point_only"] = self.point_only
        return d


class RowAndColumnPlacementStrategy(RequirementPlacementStrategyGenerator):
    def __init__(
        self,
        place_row: bool,
        place_col: bool,
        partial: bool = False,
        ignore_parent: bool = False,
        dirs: Iterable[int] = tuple(DIRS),
    ) -> None:
        assert place_col or place_row, "Must place column or row"
        self.place_row = place_row
        self.place_col = place_col
        super().__init__(
            partial=partial, ignore_parent=ignore_parent, dirs=dirs, include_empty=True
        )

    def req_indices_and_directions_to_place(
        self, tiling: Tiling
    ) -> Iterable[Tuple[Tuple[GriddedPerm, ...], Tuple[int, ...], int]]:
        """
        For each row, yield the gps with size one req for each cell in a row.
        """
        cols = defaultdict(set)
        rows = defaultdict(set)
        for cell in tiling.active_cells:
            gp = GriddedPerm(Perm((0,)), (cell,))
            cols[cell[0]].add(gp)
            rows[cell[1]].add(gp)
        if self.place_col:
            col_dirs = tuple(d for d in self.dirs if d in (DIR_EAST, DIR_WEST))
            for gps, direction in zip(cols.values(), col_dirs):
                gps = tuple(gps)
                indices = tuple(0 for _ in gps)
                yield gps, indices, direction
        if self.place_row:
            row_dirs = tuple(d for d in self.dirs if d in (DIR_NORTH, DIR_SOUTH))
            for gps, direction in zip(rows.values(), row_dirs):
                gps = tuple(gps)
                indices = tuple(0 for _ in gps)
                yield gps, indices, direction

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
            "place_col={}, partial={}, ignore_parent={}, dirs={})".format(
                self.place_row,
                self.place_col,
                self.partial,
                self.ignore_parent,
                self.dirs,
            )
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["place_row"] = self.place_row
        d["place_col"] = self.place_col
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RowAndColumnPlacementStrategy":
        return cls(**d)


class AllPlacementsStrategy(RequirementPlacementStrategyGenerator):
    def __init__(
        self, ignore_parent: bool = False,
    ):
        super().__init__(ignore_parent=ignore_parent)

    def req_placements(self, tiling: Tiling):
        """
        Return the RequiremntPlacement classes used to place the points.
        """
        return (
            RequirementPlacement(tiling),
            RequirementPlacement(tiling, own_row=False),
            RequirementPlacement(tiling, own_col=False),
        )

    def __call__(self, tiling: Tiling, **kwargs):
        include_empty_for = (
            RowAndColumnPlacementStrategy(place_col=True, place_row=True),
        )
        for other_strat in self.other_strats():
            for req_placement, (gps, indices, direction) in zip(
                self.req_placements(tiling),
                self.req_indices_and_directions_to_place(tiling, other_strat),
            ):
                if (
                    direction in req_placement.directions
                    and not req_placement.already_placed(gps, indices)
                ):
                    strategy = RequirementPlacementStrategy(
                        gps,
                        indices,
                        direction,
                        own_row=req_placement.own_row,
                        own_col=req_placement.own_col,
                        ignore_parent=self.ignore_parent,
                        include_empty=other_strat in include_empty_for,
                    )
                    children = (
                        (tiling.add_obstructions(gps),)
                        if other_strat in include_empty_for
                        else tuple()
                    ) + req_placement.place_point_of_req(gps, indices, direction)
                    yield strategy(tiling, children)

    def other_strats(self):
        return (
            PatternPlacementStrategy(point_only=False),
            PatternPlacementStrategy(point_only=True),
            RowAndColumnPlacementStrategy(place_col=True, place_row=True),
        )

    def req_indices_and_directions_to_place(
        self, tiling: Tiling, other_strat: RequirementPlacementStrategyGenerator
    ) -> Iterable[Tuple[Tuple[GriddedPerm, ...], Tuple[int, ...], int]]:
        """
        Iterator over all requirement lists, indices and directions to place.
        """
        yield from other_strat.req_indices_and_directions_to_place(tiling)

    def __str__(self) -> str:
        return "all placements"

    def __repr__(self) -> str:
        return "AllPlacementsStrategy()"

    @classmethod
    def from_dict(cls, d: dict) -> "AllPlacementsStrategy":
        return AllPlacementsStrategy()

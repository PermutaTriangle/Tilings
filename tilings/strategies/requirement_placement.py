import abc
from collections import defaultdict
from functools import reduce
from itertools import chain, product
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple, cast

from comb_spec_searcher import DisjointUnionStrategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import GriddedPerm, Tiling
from tilings.algorithms import RequirementPlacement

__all__ = [
    "PatternPlacementFactory",
    "RequirementPlacementFactory",
    "RowAndColumnPlacementFactory",
    "AllPlacementsFactory",
]

Cell = Tuple[int, int]


class RequirementPlacementStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    def __init__(
        self,
        gps: Iterable[GriddedPerm],
        indices: Iterable[int],
        direction: int,
        own_col: bool = True,
        own_row: bool = True,
        ignore_parent: bool = False,
        include_empty: bool = False,
    ):
        self.gps = tuple(gps)
        self.indices = tuple(indices)
        self.direction = direction
        self.own_row, self.own_col = own_row, own_col
        self.include_empty = include_empty
        self._placed_cells = tuple(
            sorted(set(gp.pos[idx] for idx, gp in zip(self.indices, self.gps)))
        )
        possibly_empty = self.include_empty or len(self.gps) > 1
        super().__init__(ignore_parent=ignore_parent, possibly_empty=possibly_empty)

    def _placed_cell(self, idx: int) -> Cell:
        """Return the cell placed given the index of the child."""
        return self._placed_cells[idx]

    def _child_idx(self, idx: int):
        """Return the index of the child given the index of gps placed into."""
        return self._placed_cells.index(self.gps[idx].pos[self.indices[idx]])

    def placement_class(self, tiling: Tiling) -> RequirementPlacement:
        return RequirementPlacement(tiling, own_col=self.own_col, own_row=self.own_row)

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, ...]:
        placement_class = self.placement_class(tiling)
        placed_tilings = placement_class.place_point_of_req(
            self.gps, self.indices, self.direction
        )
        if self.include_empty:
            return (tiling.add_obstructions(self.gps),) + placed_tilings
        return placed_tilings

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if not comb_class.extra_parameters:
            return super().extra_parameters(comb_class, children)
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        algo = self.placement_class(comb_class)
        extra_parameters: Tuple[Dict[str, str], ...] = tuple({} for _ in children)
        if self.include_empty:
            child = children[0]
            for assumption in comb_class.assumptions:
                mapped_assumption = child.forward_map_assumption(assumption).avoiding(
                    child.obstructions
                )
                if mapped_assumption.gps:
                    parent_var = comb_class.get_assumption_parameter(assumption)
                    child_var = child.get_assumption_parameter(mapped_assumption)
                    extra_parameters[0][parent_var] = child_var
        for idx, (cell, child) in enumerate(
            zip(self._placed_cells, children[1:] if self.include_empty else children)
        ):
            mapped_assumptions = [
                child.forward_map_assumption(ass)
                for ass in algo.stretched_assumptions(cell)
            ]
            for assumption, mapped_assumption in zip(
                comb_class.assumptions, mapped_assumptions
            ):
                if mapped_assumption.gps:
                    parent_var = comb_class.get_assumption_parameter(assumption)
                    child_var = child.get_assumption_parameter(mapped_assumption)
                    extra_parameters[idx + 1 if self.include_empty else idx][
                        parent_var
                    ] = child_var
        return extra_parameters

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
            "p" if (self.own_col and self.own_row) else "partially p",
            self.direction_string(),
        )
        if len(self.gps) == 1:
            gp = self.gps[0]
            index = self.indices[0]
            if len(gp) == 1:
                return placing + "point in cell {}".format(gp.pos[index])
            if gp.is_localized():
                return placing + "{} point in {} in cell {}".format(
                    (index, gp.patt[index]), gp.patt, gp.pos[index]
                )
            return placing + "{} point in {}".format((index, gp.patt[index]), gp)
        if all(len(gp) == 1 for gp in self.gps):
            col_indices = set(x for x, _ in [gp.pos[0] for gp in self.gps])
            if len(col_indices) == 1:
                return placing + "point in column {}".format(col_indices.pop())
            row_indices = set(y for _, y in [gp.pos[0] for gp in self.gps])
            if len(row_indices) == 1:
                return placing + "point in row {}".format(row_indices.pop())
        return placing + "point at indices {} from the requirement ({})".format(
            self.indices, ", ".join(str(gp) for gp in self.gps)
        )

    def backward_cell_map(self, placed_cell: Cell, cell: Cell) -> Cell:
        x, y = cell
        if self.own_col and x > placed_cell[0] + 1:
            x -= 2
        elif self.own_col and x == placed_cell[0] + 1:
            x -= 1
        if self.own_row and y > placed_cell[1] + 1:
            y -= 2
        elif self.own_row and y == placed_cell[1] + 1:
            y -= 1
        return x, y

    def forward_gp_map(self, gp: GriddedPerm, forced_index: int) -> GriddedPerm:
        new_pos: List[Cell] = []
        forced_val = gp.patt[forced_index]
        for idx, (x, y) in enumerate(gp.pos):
            if idx == forced_index:
                if self.own_col:
                    x += 1
                if self.own_row:
                    y += 1
                new_pos.append((x, y))
            else:
                val = gp.patt[idx]
                if self.own_col and idx >= forced_index:
                    x += 2
                if self.own_row and val >= forced_val:
                    y += 2
                new_pos.append((x, y))
        return GriddedPerm(gp.patt, new_pos)

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        if children is None:
            children = self.decomposition_function(tiling)
        idx = DisjointUnionStrategy.backward_map_index(gps)
        gp: GriddedPerm = children[idx].backward_map(cast(GriddedPerm, gps[idx]))
        if self.include_empty:
            if idx == 0:
                yield gp
                return
            idx -= 1
        placed_cell = self._placed_cell(idx)
        yield GriddedPerm(
            gp.patt, [self.backward_cell_map(placed_cell, cell) for cell in gp.pos]
        )

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        indices = gp.forced_point_of_requirement(self.gps, self.indices, self.direction)
        if children is None:
            children = self.decomposition_function(tiling)
        if indices is None:
            return (children[0].forward_map(gp),) + tuple(
                None for _ in range(len(children) - 1)
            )
        gps_index, forced_index = indices
        child_index = self._child_idx(gps_index)
        if self.include_empty:
            child_index += 1
        gp = self.forward_gp_map(gp, forced_index)
        return (
            tuple(None for _ in range(child_index))
            + (children[child_index].forward_map(gp),)
            + tuple(None for _ in range(len(children) - 1))
        )

    def __str__(self) -> str:
        return "requirement placement strategy"

    def __repr__(self) -> str:
        return (
            f"RequirementPlacementStrategy(gps={self.gps}, "
            f"indices={self.indices}, direction={self.direction}, "
            f"own_col={self.own_col}, own_row={self.own_row}, "
            f"ignore_parent={self.ignore_parent}, "
            f"include_empty={self.include_empty})"
        )

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the strategy."""
        d: dict = super().to_jsonable()
        d.pop("workable")
        d.pop("inferrable")
        d.pop("possibly_empty")
        d["gps"] = tuple(gp.to_jsonable() for gp in self.gps)
        d["indices"] = self.indices
        d["direction"] = self.direction
        d["own_col"] = self.own_col
        d["own_row"] = self.own_row
        d["include_empty"] = self.include_empty
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementPlacementStrategy":
        gps = tuple(GriddedPerm.from_dict(gp) for gp in d.pop("gps"))
        return cls(gps=gps, **d)


class AbstractRequirementPlacementFactory(StrategyFactory[Tiling]):
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
    ) -> Iterator[Tuple[Tuple[GriddedPerm, ...], Tuple[int, ...], int]]:
        """
        Iterator over all requirement lists, indices and directions to place.
        """

    def req_placements(self, tiling: Tiling) -> Tuple[RequirementPlacement, ...]:
        """
        Return the RequiremntPlacement classes used to place the points.
        """
        if self.partial:
            req_placements: Tuple[RequirementPlacement, ...] = (
                RequirementPlacement(tiling, own_row=False),
                RequirementPlacement(tiling, own_col=False),
            )
        else:
            req_placements = (RequirementPlacement(tiling),)
        return req_placements

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[Rule]:
        for req_placement, (gps, indices, direction) in product(
            self.req_placements(comb_class),
            self.req_indices_and_directions_to_place(comb_class),
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
                children = req_placement.place_point_of_req(gps, indices, direction)
                if self.include_empty:
                    children = (comb_class.add_obstructions(gps),) + children
                yield strategy(comb_class, children)

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["partial"] = self.partial
        d["ignore_parent"] = self.ignore_parent
        d["dirs"] = self.dirs
        d["include_empty"] = self.include_empty
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AbstractRequirementPlacementFactory":
        return cls(**d)


class PatternPlacementFactory(AbstractRequirementPlacementFactory):
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
    ) -> Iterator[Tuple[Tuple[GriddedPerm, ...], Tuple[int, ...], int]]:
        """
        If point_only, then yield all size one gps, in order to
        """
        if self.point_only:
            for cell in tiling.positive_cells:
                gps = (GriddedPerm((0,), (cell,)),)
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
        d.pop("include_empty")
        d["point_only"] = self.point_only
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "PatternPlacementFactory":
        return cls(**d)


class RequirementPlacementFactory(AbstractRequirementPlacementFactory):
    """
    Strategy that places a single forced point of a requirement (a set of
    gridded permutations).
    Yield all possible rules coming from placing a point of a pattern that
    occurs as a subrequirement of a requirement on the tiling.

    INPUTS:
        - `partial`: places only the point on its own row or its own column.
        - `ignore_parent`: indicate if the rule should ignore parent
        - `dirs`: The directions used for placement (default to all
          directions).
          The possible directions are:
            - `permuta.misc.DIR_NORTH`
            - `permuta.misc.DIR_SOUTH`
            - `permuta.misc.DIR_EAST`
            - `permuta.misc.DIR_WEST`
        - `max_rules_per_req`: The limit on the size of the requirements that can
        be placed. If the product of the length of the gridded perms
        in the requirement and the number of direction is greater than the max,
        then no placements is performed for that req.
    """

    def __init__(
        self,
        subreqs: bool = False,
        partial: bool = False,
        ignore_parent: bool = False,
        dirs: Iterable[int] = tuple(DIRS),
        max_rules_per_req: Optional[int] = None,
    ):
        assert all(d in DIRS for d in dirs), "Got an invalid direction"
        self.subreqs = subreqs
        self.max_rules_per_req = max_rules_per_req
        super().__init__(partial=partial, ignore_parent=ignore_parent, dirs=dirs)

    @staticmethod
    def downward_sets(tiling: Tiling) -> Set[Tuple[GriddedPerm, ...]]:
        """Yield all requirements contained in some requirement on the tiling."""
        queue = set(tuple(sorted(req)) for req in tiling.requirements)
        # TODO: should we consider minimal gridded perms?
        #           Optimal is minimal on the factors of the tiling which
        #           contains only the requirement,
        all_reqs: Set[Tuple[GriddedPerm, ...]] = set()
        while queue:
            req = queue.pop()
            if req not in all_reqs:
                all_reqs.add(req)
                subgps = set(
                    subgp
                    for subgp in chain.from_iterable(
                        gp.all_subperms(proper=True) for gp in req
                    )
                    if len(subgp) >= 1
                )
                for subgp in subgps:
                    rest_of_req = tuple(gp for gp in req if gp.avoids(subgp))
                    newreq = tuple(sorted(rest_of_req + (subgp,)))
                    if newreq not in all_reqs:
                        queue.add(newreq)
        return all_reqs

    def req_indices_and_directions_to_place(
        self, tiling: Tiling
    ) -> Iterator[Tuple[Tuple[GriddedPerm, ...], Tuple[int, ...], int]]:
        all_reqs: Iterable[Tuple[GriddedPerm, ...]]
        if self.subreqs:
            all_reqs = self.downward_sets(tiling)
        else:
            all_reqs = tiling.requirements
        for req in all_reqs:
            if self.max_rules_per_req is not None:
                num_rule = len(self.dirs) * reduce(
                    lambda prod, req: prod * len(req), req, 1
                )
                if num_rule > self.max_rules_per_req:
                    continue
            for indices, direction in product(
                product(*[range(len(gp)) for gp in req]), self.dirs
            ):
                yield req, tuple(indices), direction

    def __str__(self) -> str:
        s = "partial " if self.partial else ""
        s += "requirement placement"
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
        if self.max_rules_per_req:
            s += f" (at most {self.max_rules_per_req} rule per req)"
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
            "AllRequirementPlacementStrategy(subreqs={},partial={},"
            " ignore_parent={}{}, max_rules_per_req={})".format(
                self.subreqs,
                self.partial,
                self.ignore_parent,
                dir_arg,
                self.max_rules_per_req,
            )
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d.pop("include_empty")
        d["subreqs"] = self.subreqs
        d["max_rules_per_req"] = self.max_rules_per_req
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementPlacementFactory":
        max_rules_per_req = d.pop("max_rules_per_req", None)
        return cls(max_rules_per_req=max_rules_per_req, **d)


class RowAndColumnPlacementFactory(AbstractRequirementPlacementFactory):
    def __init__(
        self,
        place_row: bool = True,
        place_col: bool = True,
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
    ) -> Iterator[Tuple[Tuple[GriddedPerm, ...], Tuple[int, ...], int]]:
        """
        For each row, yield the gps with size one req for each cell in a row.
        """
        cols: Dict[int, Set[GriddedPerm]] = defaultdict(set)
        rows: Dict[int, Set[GriddedPerm]] = defaultdict(set)
        for cell in tiling.active_cells:
            gp = GriddedPerm((0,), (cell,))
            cols[cell[0]].add(gp)
            rows[cell[1]].add(gp)
        if self.place_col:
            col_dirs = tuple(d for d in self.dirs if d in (DIR_EAST, DIR_WEST))
            for gps, direction in product(cols.values(), col_dirs):
                indices = tuple(0 for _ in gps)
                yield tuple(gps), indices, direction
        if self.place_row:
            row_dirs = tuple(d for d in self.dirs if d in (DIR_NORTH, DIR_SOUTH))
            for gps, direction in product(rows.values(), row_dirs):
                indices = tuple(0 for _ in gps)
                yield tuple(gps), indices, direction

    def __str__(self) -> str:
        s = "{} placement"
        if self.place_col and self.place_row:
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
        d.pop("include_empty")
        d["place_row"] = self.place_row
        d["place_col"] = self.place_col
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RowAndColumnPlacementFactory":
        return cls(**d)


class AllPlacementsFactory(AbstractRequirementPlacementFactory):

    PLACEMENT_STRATS: Tuple[AbstractRequirementPlacementFactory, ...] = (
        PatternPlacementFactory(point_only=False),
        # subreqs=True covers everything but it blows up massively!
        RequirementPlacementFactory(subreqs=False),
        RowAndColumnPlacementFactory(place_col=True, place_row=True),
    )

    def __init__(self, ignore_parent: bool = False):
        super().__init__(ignore_parent=ignore_parent, include_empty=True)

    def req_placements(self, tiling: Tiling):
        """
        Return the RequiremntPlacement classes used to place the points.
        """
        return (
            RequirementPlacement(tiling),
            RequirementPlacement(tiling, own_row=False),
            RequirementPlacement(tiling, own_col=False),
        )

    def req_indices_and_directions_to_place(
        self, tiling: Tiling
    ) -> Iterator[Tuple[Tuple[GriddedPerm, ...], Tuple[int, ...], int]]:
        """
        Iterator over all requirement lists, indices and directions to place.
        """
        res = frozenset(
            chain.from_iterable(
                other_strat.req_indices_and_directions_to_place(tiling)
                for other_strat in AllPlacementsFactory.PLACEMENT_STRATS
            )
        )
        yield from res

    def __str__(self) -> str:
        return "all placements"

    def __repr__(self) -> str:
        return "AllPlacementsStrategy(ignore_parent={})".format(self.ignore_parent)

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d.pop("partial")
        d.pop("dirs")
        d.pop("include_empty")
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AllPlacementsFactory":
        return cls(**d)

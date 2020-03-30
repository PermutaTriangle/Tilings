from itertools import chain
from typing import (TYPE_CHECKING, Dict, FrozenSet, Iterable, Iterator, List,
                    Tuple, TypeVar)

from comb_spec_searcher import BatchRule, Rule
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS

from ..obstruction import Obstruction
from ..requirement import Requirement

if TYPE_CHECKING:
    from tilings import Tiling

Cell = Tuple[int, int]
Dir = int
ListRequirement = List[Requirement]
GriddedPerm = TypeVar('GriddedPerm', Obstruction, Requirement)
ObsCache = Dict[Cell, List[Obstruction]]
ReqsCache = Dict[Cell, List[ListRequirement]]


class RequirementPlacement():
    """
    The requirement placement container class.

    Places points onto own row, own col, or both.

    INPUTS:
        - `tiling`: The tilings to perform the placement with
        - `own_row`: Indiciate the place the point on its own row
        - `own_col`: Indiciate the place the point on its own column
        - `dirs`: The directions used for placement (default to all
          directions).
          The possible directions are:
            - `permuta.misc.DIR_NORTH`
            - `permuta.misc.DIR_SOUTH`
            - `permuta.misc.DIR_EAST`
            - `permuta.misc.DIR_WEST`
    """
    def __init__(self, tiling: 'Tiling', own_row: bool = True,
                 own_col: bool = True, dirs: Iterable[int] = tuple(DIRS)):
        if not own_row and not own_col:
            raise ValueError("Must place on own row or on own column.")
        assert all(d in DIRS for d in dirs), "Got an invalid direction"
        self._tiling = tiling
        self._point_row_cells = self._tiling_point_row_cells()
        self._point_col_cells = self._tiling_point_col_cells()
        self._own_row = own_row
        self._own_col = own_col
        self._stretched_obstructions_cache = {}  # type: ObsCache
        self._stretched_requirements_cache = {}  # type: ReqsCache
        if self._own_row and self._own_col:
            self.directions = frozenset(DIRS)
        elif self._own_row:
            self.directions = frozenset((DIR_NORTH, DIR_SOUTH))
        elif self._own_col:
            self.directions = frozenset((DIR_EAST, DIR_WEST))
        self.directions = frozenset(dirs).intersection(self.directions)
        assert self.directions, "No direction to place"

    def _tiling_point_col_cells(self) -> FrozenSet[Cell]:
        """
        The point cells of the tilings that are the only active cell in there
        column.
        """
        return frozenset(filter(
            self._tiling.only_cell_in_col, self._tiling.point_cells
        ))

    def _tiling_point_row_cells(self) -> FrozenSet[Cell]:
        """
        The point cells of the tilings that are the only active cell in there
        row.
        """
        return frozenset(filter(
            self._tiling.only_cell_in_row, self._tiling.point_cells
        ))

    def _already_placed(self, cell) -> bool:
        """
        Determine if this cell is already placed.
        """
        full_placement = self._own_row and self._own_col
        if full_placement:
            return (cell in self._point_col_cells and
                    cell in self._point_row_cells)
        if self._own_row:  # Only placing in own row
            return cell in self._point_row_cells
        if self._own_col:  # Only placing in own column
            return cell in self._point_col_cells
        raise Exception('Not placing at all!!')

    def _point_translation(self, gp: GriddedPerm, index: int,
                           placed_cell: Cell) -> Cell:
        """
        Return the translated position of the cell at the given index.

        The translation assumes that there has been a point placed in the
        position (i, j) = placed_cell where this corresponds to the index and
        value within the pattern of the gridded permutation gp.

        If the newly placed point is assumed to put on the the new column we
        have that the cell is expanded like:
            -      - - -
           | | -> | |o| |
            -      - - -
        meaning that indices to the right of i are shifted by 2.
        Similarly, for new rows we have
                   -
                  | |
            -      -
           | | -> |o|
            -      -
                  | |
                   -
        meaning that values above j are shifted by 2.
        """
        x, y = gp.pos[index]
        return (x + 2 if self._own_col and index >= placed_cell[0] else x,
                y + 2 if (self._own_row and
                          gp.patt[index] >= placed_cell[1]) else y)

    def _gridded_perm_translation(self, gp: GriddedPerm,
                                  placed_cell: Cell) -> GriddedPerm:
        """
        Return the gridded permutation with all of the cells translated
        assuming that the point was placed at placed cell
        """
        newpos = [self._point_translation(gp, index, placed_cell)
                  for index in range(len(gp))]
        return gp.__class__(gp.patt, newpos)

    def _gridded_perm_translation_with_point(
        self, gp: GriddedPerm, point_index: int
    ) -> GriddedPerm:
        """
        Return the stretched gridded permutation obtained when the point at
        point_index in gp is placed.
        """
        # TODO: to prepare for intervals consider all ways of drawing a
        #       rectangle around point in cell.
        new_pos = [self._point_translation(
                                    gp, i, (point_index, gp.patt[point_index]))
                   if i != point_index else self._placed_cell(
                                                         gp.pos[point_index])
                   for i in range(len(gp))]
        return gp.__class__(gp.patt, new_pos)

    def _placed_cell(self, cell: Cell) -> Cell:
        """
        Return the cell in which the point will be added in the placed tiling.

        If placed on its own row, then the y coordinate is shifted by 1.
        If placed on its own column, then the x coordinate is shifted by 1.
        """
        x, y = cell
        return (x + 1 if self._own_col else x, y + 1 if self._own_row else y)

    def _point_obstructions(self, cell: Cell) -> List[Obstruction]:
        """
        Return the localised 12 and 21 obstruction required to ensure the
        newly placed point is a point.
        """
        placed_cell = self._placed_cell(cell)
        return [Obstruction(Perm((0, 1)), (placed_cell, placed_cell)),
                Obstruction(Perm((1, 0)), (placed_cell, placed_cell))]

    def _point_requirements(self, cell: Cell) -> List[ListRequirement]:
        """
        Return the requirement required to ensure that the newly placed point
        is a point.
        """
        placed_cell = self._placed_cell(cell)
        return [[Requirement(Perm((0,)), (placed_cell,))]]

    def _stretch_gridded_perm(self, gp: GriddedPerm,
                              cell: Cell) -> Iterable[GriddedPerm]:
        """
        Return all of the possible ways that a gridded permutation can be
        stretched assuming that a point is placed into the given cell.
        """
        mindex, maxdex, minval, maxval = gp.get_bounding_box(cell)
        if not self._own_col:
            maxdex = mindex
        elif not self._own_row:
            maxval = minval
        res = [self._gridded_perm_translation(gp, (i, j))
               for i in range(mindex, maxdex + 1)
               for j in range(minval, maxval + 1)]
        for i in gp.points_in_cell(cell):
            res.append(self._gridded_perm_translation_with_point(gp, i))
        return res

    def _stretch_gridded_perms(self, gps: Iterable[GriddedPerm],
                               cell: Cell) -> List[GriddedPerm]:
        """
        Return all strected gridded permuations for an iterable of gridded
        permutations, assuming a point is placed in the given cell.
        """
        return list(chain.from_iterable(self._stretch_gridded_perm(gp, cell)
                                        for gp in gps))

    def _stretched_obstructions(self, cell: Cell) -> List[Obstruction]:
        """
        Return all of the stretched obstructions that are created if placing a
        point in the given cell.
        """
        if cell not in self._stretched_obstructions_cache:
            self._stretched_obstructions_cache[cell] = \
                self._stretch_gridded_perms(self._tiling.obstructions, cell)
        return self._stretched_obstructions_cache[cell]

    def _stretched_requirements(self, cell: Cell) -> List[ListRequirement]:
        """
        Return all of the stretched requirements that are created if placing a
        point in the given cell.
        """
        if cell not in self._stretched_requirements_cache:
            self._stretched_requirements_cache[cell] = \
                        [self._stretch_gridded_perms(req_list, cell)
                         for req_list in self._tiling.requirements]
        return self._stretched_requirements_cache[cell]

    def _stretched_obstructions_and_requirements(
        self, cell: Cell
    ) -> Tuple[List[Obstruction], List[ListRequirement]]:
        """
        Return all of the stretched obstruction and requirements assuming that
        a point is placed in cell.
        """
        stretched_obs = self._stretched_obstructions(cell)
        stretched_reqs = self._stretched_requirements(cell)
        point_obs = self._point_obstructions(cell)
        point_req = self._point_requirements(cell)
        return stretched_obs + point_obs, stretched_reqs + point_req

    @staticmethod
    def _farther(c1: Cell, c2: Cell, direction: Dir) -> bool:
        """Return True if c1 is farther in the given direction than c2."""
        if direction == DIR_EAST:
            return c1[0] > c2[0]
        if direction == DIR_WEST:
            return c1[0] < c2[0]
        if direction == DIR_NORTH:
            return c1[1] > c2[1]
        if direction == DIR_SOUTH:
            return c1[1] < c2[1]
        raise Exception('Invalid direction')

    def _forced_obstructions_from_patt(self, gp: GriddedPerm, idx: int,
                                       direction: Dir) -> List[Obstruction]:
        """
        Return the obstructions required to ensure that the placed point is
        the direction most occurence of the idx point of gp.

        In particular, this returns the list of obstructions that are stretched
        from gp in which the point at idx is farther in the given direction
        than the placed cell.
        """
        placed_cell = self._placed_cell(gp.pos[idx])
        ob = Obstruction(gp.patt, gp.pos)
        return [stretched_gp
                for stretched_gp in self._stretch_gridded_perm(ob, ob.pos[idx])
                if self._farther(stretched_gp.pos[idx], placed_cell,
                                 direction)]

    def _forced_obstructions_from_list(
        self, gp_list: List[GriddedPerm], cell: Cell, direction: Dir
    ) -> List[Obstruction]:
        """
        Return the obstructions required to ensure that the placed point is
        the direction most occurence of a point used in an occurrence of any
        gridded permutation in gp_list.

        In particular, this returns the list of obstructions that are stretched
        from any gridded permutation in gp_list in which the point at idx is
        farther in the given direction than the placed cell.
        """
        placed_cell = self._placed_cell(cell)
        return [stretched_gp
                for stretched_gp in chain.from_iterable(
                       self._stretch_gridded_perm(Obstruction(gp.patt, gp.pos),
                                                  cell) for gp in gp_list)
                if any(self._farther(c1, placed_cell, direction)
                       for c1 in stretched_gp.pos)]

    def place_point_of_req(self, gp: GriddedPerm, idx: int,
                           direction: Dir) -> 'Tiling':
        """
        Return the tiling where the placed point correspond to the
        directionmost (the furtest in the given direction, ex: leftmost point)
        occurrence of the idx point in gp.
        """
        cell = gp.pos[idx]
        obs, reqs = self._stretched_obstructions_and_requirements(cell)
        forced_obs = self._forced_obstructions_from_patt(gp, idx, direction)
        rem_reqs = [[self._gridded_perm_translation_with_point(
                                        Requirement(gp.patt, gp.pos), idx)]]
        return self._tiling.__class__(obs + forced_obs, reqs + rem_reqs)

    def place_point_in_cell(self, cell: Cell, direction: Dir) -> 'Tiling':
        """
        Return the tiling in which a point is placed in the given direction and
        cell.
        """
        point_req = Requirement(Perm((0,)), (cell,))
        return self.place_point_of_req(point_req, 0, direction)

    def place_point_of_req_list(self, req_list: ListRequirement,
                                direction: Dir) -> List['Tiling']:
        """
        Return a list of tilings, in which each tiling corresponds to a
        possible way in which a direction most point can occur of any gridded
        permutation in req_list in the original tiling.
        """
        cells = set(chain.from_iterable(req.pos for req in req_list))
        tilings = []
        for cell in cells:
            obs, reqs = self._stretched_obstructions_and_requirements(cell)
            forced_obs = self._forced_obstructions_from_list(req_list, cell,
                                                             direction)
            tilings.append(self._tiling.__class__(obs + forced_obs, reqs))
        return tilings

    def col_placement(self, index: int, direction: Dir) -> List['Tiling']:
        """
        Return the list corresponding the index column being placed in the
        given direction.
        """
        assert direction in (DIR_EAST, DIR_WEST)
        req_list = [Requirement(Perm((0,)), (cell,))
                    for cell in self._tiling.cells_in_col(index)]
        return self.place_point_of_req_list(req_list, direction)

    def row_placement(self, index: int, direction: Dir) -> List['Tiling']:
        """
        Return the list corresponding the index row being placed in the given
        direction.
        """
        assert direction in (DIR_NORTH, DIR_SOUTH)
        req_list = [Requirement(Perm((0,)), (cell,))
                    for cell in self._tiling.cells_in_row(index)]
        return self.place_point_of_req_list(req_list, direction)

    def empty_col(self, index: int) -> 'Tiling':
        """
        Return the tiling in which the index row is empty.
        """
        newobs = tuple(Obstruction(Perm((0,)), (cell,))
                       for cell in self._tiling.cells_in_col(index))
        return self._tiling.__class__(self._tiling.obstructions + newobs,
                                      self._tiling.requirements)

    def empty_row(self, index: int) -> 'Tiling':
        """
        Return the tiling in which the index row is empty.
        """
        newobs = tuple(Obstruction(Perm((0,)), (cell,))
                       for cell in self._tiling.cells_in_row(index))
        return self._tiling.__class__(self._tiling.obstructions + newobs,
                                      self._tiling.requirements)

    def all_col_placement_rules(self) -> Iterator[Rule]:
        """
        Yield all possible rules coming from placing points in a column.
        """
        if not self._own_col:
            return
        unplaced_col = (idx for idx in range(self._tiling.dimensions[0]) if not
                        any(cell[0] == idx for cell in self._point_col_cells))
        for index in unplaced_col:
            for direction in self.directions:
                if direction in (DIR_EAST, DIR_WEST):
                    tilings = ([self.empty_col(index)] +
                               self.col_placement(index, direction))
                    formal_step = self._col_placement_formal_step(
                                                            index, direction)
                    yield BatchRule(formal_step, tilings)

    def all_row_placement_rules(self) -> Iterator[Rule]:
        """
        Yield all possible rules coming from placing points in a row.
        """
        if not self._own_row:
            return
        unplaced_row = (idx for idx in range(self._tiling.dimensions[1]) if not
                        any(cell[1] == idx for cell in self._point_row_cells))
        for index in unplaced_row:
            for direction in self.directions:
                if direction in (DIR_NORTH, DIR_SOUTH):
                    tilings = ([self.empty_row(index)] +
                               self.row_placement(index, direction))
                    formal_step = self._row_placement_formal_step(
                                                            index, direction)
                    yield BatchRule(formal_step, tilings)

    def all_point_placement_rules(
        self, ignore_parent: bool = False
    ) -> Iterator[Rule]:
        """
        Yield all posible rules coming from placing a point in a positive cell
        of the tiling.
        """
        for cell in self._tiling.positive_cells:
            if self._already_placed(cell):
                continue
            for direction in self.directions:
                placed_tiling = self.place_point_in_cell(cell, direction)
                formal_step = self._point_placement_formal_step(
                                                            cell, direction)
                yield Rule(formal_step, [placed_tiling], [True], [False],
                           [True], ignore_parent=ignore_parent,
                           constructor='equiv')

    def all_requirement_placement_rules(
        self, ignore_parent: bool = False
    ) -> Iterator[Rule]:
        """
        Yield all possible rules coming from placing a point of a pattern that
        occurs as a subpattern of requirement containing a single pattern.
        """
        subgps = set(chain.from_iterable(req[0].all_subperms(proper=False)
                                         for req in self._tiling.requirements
                                         if len(req) == 1))
        for gp in subgps:
            for idx in range(len(gp)):
                cell = gp.pos[idx]
                if self._already_placed(cell):
                    continue
                for direction in self.directions:
                    placed_tiling = self.place_point_of_req(gp, idx, direction)
                    formal_step = self._pattern_placement_formal_step(
                        idx, gp, direction)
                    yield Rule(formal_step, [placed_tiling], [True], [False],
                               workable=[True], ignore_parent=ignore_parent,
                               constructor='equiv')

    def _col_placement_formal_step(self, idx: int, direction: Dir) -> str:
        dir_str = self._direction_string(direction)
        s = 'Placing '
        if not (self._own_col and self._own_row):
            s += 'partially '
        s += '{} points in column {}.'.format(dir_str, idx)
        return s

    def _row_placement_formal_step(self, idx: int, direction: Dir) -> str:
        dir_str = self._direction_string(direction)
        s = 'Placing '
        if not (self._own_col and self._own_row):
            s += 'partially '
        s += '{} points in row {}.'.format(dir_str, idx)
        return s

    def _point_placement_formal_step(self, cell: Cell, direction: Dir) -> str:
        dir_str = self._direction_string(direction)
        s = 'Placing '
        if not (self._own_col and self._own_row):
            s += 'partially '
        s += '{} point in cell {}.'.format(dir_str, cell)
        return s

    def _pattern_placement_formal_step(self, idx: int, gp: GriddedPerm,
                                       direction: Dir) -> str:
        dir_str = self._direction_string(direction)
        s = 'Placing '
        if not (self._own_col and self._own_row):
            s += 'partially '
        s += 'the {} point of ({}, {}) in {}.'.format(
            dir_str, idx, gp.patt[idx], gp)
        return s

    @staticmethod
    def _direction_string(direction: Dir) -> str:
        if direction == DIR_EAST:
            return "rightmost"
        if direction == DIR_WEST:
            return "leftmost"
        if direction == DIR_NORTH:
            return "topmost"
        if direction == DIR_SOUTH:
            return "bottommost"
        raise Exception('Invalid direction')

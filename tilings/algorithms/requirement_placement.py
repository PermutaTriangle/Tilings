from itertools import chain
from typing import TYPE_CHECKING, Dict, FrozenSet, Iterable, List, Tuple

from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import GriddedPerm
from tilings.assumptions import TrackingAssumption

if TYPE_CHECKING:
    from tilings import Tiling

Cell = Tuple[int, int]
Dir = int
ListRequirement = List[GriddedPerm]
ObsCache = Dict[Cell, List[GriddedPerm]]
ReqsCache = Dict[Cell, List[ListRequirement]]
AssCache = Dict[Cell, List[TrackingAssumption]]


class RequirementPlacement:
    """
    The requirement placement container class.

    Places points onto own row, own col, or both.

    INPUTS:
        - `tiling`: The tilings to perform the placement with
        - `own_row`: Indiciate to place the point on its own row
        - `own_col`: Indiciate to place the point on its own column
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
        tiling: "Tiling",
        own_row: bool = True,
        own_col: bool = True,
        dirs: Iterable[int] = tuple(DIRS),
    ):
        if not own_row and not own_col:
            raise ValueError("Must place on own row or on own column.")
        assert all(d in DIRS for d in dirs), "Got an invalid direction"
        self._tiling = tiling
        self._point_row_cells = self._tiling_point_row_cells()
        self._point_col_cells = self._tiling_point_col_cells()
        self.own_row = own_row
        self.own_col = own_col
        self._stretched_obstructions_cache: ObsCache = {}
        self._stretched_requirements_cache: ReqsCache = {}
        self._stretched_assumptions_cache: AssCache = {}
        if self.own_row and self.own_col:
            self.directions = frozenset(DIRS)
        elif self.own_row:
            self.directions = frozenset((DIR_NORTH, DIR_SOUTH))
        elif self.own_col:
            self.directions = frozenset((DIR_EAST, DIR_WEST))
        self.directions = frozenset(dirs).intersection(self.directions)
        assert self.directions, "No direction to place"

    def _tiling_point_col_cells(self) -> FrozenSet[Cell]:
        """
        The point cells of the tilings that are the only active cell in there
        column.
        """
        return frozenset(
            filter(self._tiling.only_cell_in_col, self._tiling.point_cells)
        )

    def _tiling_point_row_cells(self) -> FrozenSet[Cell]:
        """
        The point cells of the tilings that are the only active cell in there
        row.
        """
        return frozenset(
            filter(self._tiling.only_cell_in_row, self._tiling.point_cells)
        )

    def already_placed(
        self, gps: Iterable[GriddedPerm], indices: Iterable[int]
    ) -> bool:
        """
        Determine if this gps is already placed.
        """
        cells = set(gp.pos[idx] for gp, idx in zip(gps, indices))
        if len(cells) != 1:
            return False
        cell = cells.pop()
        full_placement = self.own_row and self.own_col
        if full_placement:
            return cell in self._point_col_cells and cell in self._point_row_cells
        if self.own_row:  # Only placing in own row
            return cell in self._point_row_cells
        if self.own_col:  # Only placing in own column
            return cell in self._point_col_cells
        raise Exception("Not placing at all!!")

    def _point_translation(
        self, gp: GriddedPerm, index: int, placed_cell: Cell
    ) -> Cell:
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
        return (
            x + 2 if self.own_col and index >= placed_cell[0] else x,
            y + 2 if (self.own_row and gp.patt[index] >= placed_cell[1]) else y,
        )

    def _gridded_perm_translation(
        self, gp: GriddedPerm, placed_cell: Cell
    ) -> GriddedPerm:
        """
        Return the gridded permutation with all of the cells translated
        assuming that the point was placed at placed cell
        """
        newpos = [
            self._point_translation(gp, index, placed_cell) for index in range(len(gp))
        ]
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
        new_pos = [
            self._point_translation(gp, i, (point_index, gp.patt[point_index]))
            if i != point_index
            else self._placed_cell(gp.pos[point_index])
            for i in range(len(gp))
        ]
        return gp.__class__(gp.patt, new_pos)

    def _placed_cell(self, cell: Cell) -> Cell:
        """
        Return the cell in which the point will be added in the placed tiling.

        If placed on its own row, then the y coordinate is shifted by 1.
        If placed on its own column, then the x coordinate is shifted by 1.
        """
        x, y = cell
        return (x + 1 if self.own_col else x, y + 1 if self.own_row else y)

    def _point_obstructions(self, cell: Cell) -> List[GriddedPerm]:
        """
        Return the localised 12 and 21 obstruction required to ensure the
        newly placed point is a point.
        """
        placed_cell = self._placed_cell(cell)
        return [
            GriddedPerm((0, 1), (placed_cell, placed_cell)),
            GriddedPerm((1, 0), (placed_cell, placed_cell)),
        ]

    def _point_requirements(self, cell: Cell) -> List[ListRequirement]:
        """
        Return the requirement required to ensure that the newly placed point
        is a point.
        """
        placed_cell = self._placed_cell(cell)
        return [[GriddedPerm((0,), (placed_cell,))]]

    def _stretch_gridded_perm(
        self, gp: GriddedPerm, cell: Cell
    ) -> Iterable[GriddedPerm]:
        """
        Return all of the possible ways that a gridded permutation can be
        stretched assuming that a point is placed into the given cell.
        """
        mindex, maxdex, minval, maxval = gp.get_bounding_box(cell)
        if not self.own_col:
            maxdex = mindex
        elif not self.own_row:
            maxval = minval
        res = [
            self._gridded_perm_translation(gp, (i, j))
            for i in range(mindex, maxdex + 1)
            for j in range(minval, maxval + 1)
        ]
        for i in gp.points_in_cell(cell):
            res.append(self._gridded_perm_translation_with_point(gp, i))
        return res

    def _stretch_gridded_perms(
        self, gps: Iterable[GriddedPerm], cell: Cell
    ) -> List[GriddedPerm]:
        """
        Return all stretched gridded permuations for an iterable of gridded
        permutations, assuming a point is placed in the given cell.
        """
        return list(
            chain.from_iterable(self._stretch_gridded_perm(gp, cell) for gp in gps)
        )

    def stretched_obstructions(self, cell: Cell) -> List[GriddedPerm]:
        """
        Return all of the stretched obstructions that are created if placing a
        point in the given cell.
        """
        if cell not in self._stretched_obstructions_cache:
            self._stretched_obstructions_cache[cell] = self._stretch_gridded_perms(
                self._tiling.obstructions, cell
            )
        return self._stretched_obstructions_cache[cell]

    def stretched_requirements(self, cell: Cell) -> List[ListRequirement]:
        """
        Return all of the stretched requirements that are created if placing a
        point in the given cell.
        """
        if cell not in self._stretched_requirements_cache:
            self._stretched_requirements_cache[cell] = [
                self._stretch_gridded_perms(req_list, cell)
                for req_list in self._tiling.requirements
            ]
        return self._stretched_requirements_cache[cell]

    def stretched_assumptions(self, cell: Cell) -> List[TrackingAssumption]:
        """
        Return all of the stretched assumptions that are created if placing a
        point in the given cell.
        """
        if cell not in self._stretched_assumptions_cache:
            self._stretched_assumptions_cache[cell] = [
                ass.__class__(self._stretch_gridded_perms(ass.gps, cell))
                for ass in self._tiling.assumptions
            ]
        return self._stretched_assumptions_cache[cell]

    def _stretched_obstructions_requirements_and_assumptions(
        self, cell: Cell
    ) -> Tuple[List[GriddedPerm], List[ListRequirement], List[TrackingAssumption]]:
        """
        Return all of the stretched obstruction and requirements assuming that
        a point is placed in cell.
        """
        stretched_obs = self.stretched_obstructions(cell)
        stretched_reqs = self.stretched_requirements(cell)
        stretched_ass = self.stretched_assumptions(cell)
        point_obs = self._point_obstructions(cell)
        point_req = self._point_requirements(cell)
        return stretched_obs + point_obs, stretched_reqs + point_req, stretched_ass

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
        raise Exception("Invalid direction")

    def forced_obstructions_from_requirement(
        self,
        gps: Iterable[GriddedPerm],
        indices: Iterable[int],
        cell: Cell,
        direction: Dir,
    ) -> List[GriddedPerm]:
        """
        Return the obstructions required to ensure that the placed point is
        the direction most occurence of a point used in an occurrence of any
        gridded permutation in gp_list.

        In particular, this returns the list of obstructions that are stretched
        from any gridded permutation in gp_list in which the point at idx is
        farther in the given direction than the placed cell.
        """
        placed_cell = self._placed_cell(cell)
        res = []
        for idx, gp in zip(indices, gps):
            # if cell is farther in the direction than gp[idx], then don't need
            # to avoid any of the stretched grided perms
            if not self._farther(cell, gp.pos[idx], direction):
                for stretched_gp in self._stretch_gridded_perm(gp, cell):
                    if self._farther(stretched_gp.pos[idx], placed_cell, direction):
                        res.append(stretched_gp)
        return res

    def _remaining_requirement_from_requirement(
        self, gps: Iterable[GriddedPerm], indices: Iterable[int], cell: Cell
    ) -> List[GriddedPerm]:
        """
        Return the requirements required to ensure that the placed point can be
        extended to be direction most occurrece of a point at the index of the
        gp in gps.

        In particulur, this returns the requirements that come from stretching
        a gridded permutation in gps, such that the point at idx is the placed
        cell.
        """
        placed_cell = self._placed_cell(cell)
        res = []
        for idx, gp in zip(indices, gps):
            if gp.pos[idx] == cell:
                for stretched_gp in self._stretch_gridded_perm(gp, cell):
                    if stretched_gp.pos[idx] == placed_cell:
                        res.append(stretched_gp)
        return res

    def place_point_of_gridded_permutation(
        self, gp: GriddedPerm, idx: int, direction: Dir
    ) -> "Tiling":
        """
        Return the tiling where the placed point correspond to the
        directionmost (the furtest in the given direction, ex: leftmost point)
        occurrence of the idx point in gp.
        """
        return self.place_point_of_req((gp,), (idx,), direction)[0]

    def place_point_of_req(
        self, gps: Iterable[GriddedPerm], indices: Iterable[int], direction: Dir
    ) -> Tuple["Tiling", ...]:
        """
        Return the tilings, where the placed point corresponds to the directionmost
        (the furtest in the given direction, ex: leftmost point) of an occurrence
        of any point idx, gp(idx) for gridded perms in gp, and idx in indices
        """
        cells = frozenset(gp.pos[idx] for idx, gp in zip(indices, gps))
        res = []
        for cell in sorted(cells):
            stretched = self._stretched_obstructions_requirements_and_assumptions(cell)
            (obs, reqs, ass) = stretched
            forced_obs = self.forced_obstructions_from_requirement(
                gps, indices, cell, direction
            )

            reduced_obs = [o1 for o1 in obs if not any(o2 in o1 for o2 in forced_obs)]
            new_obs = reduced_obs + forced_obs

            rem_req = self._remaining_requirement_from_requirement(gps, indices, cell)

            res.append(
                self._tiling.__class__(
                    new_obs,
                    reqs + [rem_req],
                    assumptions=ass,
                    already_minimized_obs=True,
                )
            )
        return tuple(res)

    def place_point_in_cell(self, cell: Cell, direction: Dir) -> "Tiling":
        """
        Return the tiling in which a point is placed in the given direction and
        cell.
        """
        point_req = GriddedPerm((0,), (cell,))
        return self.place_point_of_req((point_req,), (0,), direction)[0]

    def col_placement(self, index: int, direction: Dir) -> Tuple["Tiling", ...]:
        """
        Return the list corresponding the index column being placed in the
        given direction.
        """
        assert direction in (DIR_EAST, DIR_WEST)
        req = [GriddedPerm((0,), (cell,)) for cell in self._tiling.cells_in_col(index)]
        return self.place_point_of_req(req, tuple(0 for _ in req), direction)

    def row_placement(self, index: int, direction: Dir) -> Tuple["Tiling", ...]:
        """
        Return the list corresponding the index row being placed in the given
        direction.
        """
        assert direction in (DIR_NORTH, DIR_SOUTH)
        req = [GriddedPerm((0,), (cell,)) for cell in self._tiling.cells_in_row(index)]
        return self.place_point_of_req(req, tuple(0 for _ in req), direction)

    def empty_col(self, index: int) -> "Tiling":
        """
        Return the tiling in which the index row is empty.
        """
        return self._tiling.add_obstructions(
            tuple(
                GriddedPerm((0,), (cell,)) for cell in self._tiling.cells_in_col(index)
            )
        )

    def empty_row(self, index: int) -> "Tiling":
        """
        Return the tiling in which the index row is empty.
        """
        return self._tiling.add_obstructions(
            tuple(
                GriddedPerm((0,), (cell,)) for cell in self._tiling.cells_in_row(index)
            )
        )

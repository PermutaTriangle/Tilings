import itertools
from itertools import chain
from types import resolve_bases
from typing import TYPE_CHECKING, Dict, FrozenSet, Iterable, List, Tuple

from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings.griddedperm import GriddedPerm
from tilings.map import RowColMap
from tilings.parameter_counter import ParameterCounter, PreimageCounter

if TYPE_CHECKING:
    from tilings import Tiling

Cell = Tuple[int, int]
Dir = int
ListRequirement = List[GriddedPerm]
ObsCache = Dict[Cell, List[GriddedPerm]]
ReqsCache = Dict[Cell, List[ListRequirement]]
ParamCache = Dict[Cell, List[ParameterCounter]]


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

    def empty_row_and_col_obs(
        self, cell: Cell, width: int, height: int
    ) -> List[GriddedPerm]:
        """
        Return the obstructions needed to ensure point is the only on a the row
        and/or column
        """
        res: List[GriddedPerm] = []
        empty_col, empty_row = self._placed_cell(cell)
        if self.own_row:
            for i in range(width):
                if i != empty_col:
                    res.append(GriddedPerm.point_perm((i, empty_row)))
        if self.own_col:
            for j in range(height):
                if j != empty_row:
                    res.append(GriddedPerm.point_perm((empty_col, j)))
        return res

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
        row_col_map = self.multiplex_map(*self._tiling.dimensions, cell)
        placed_cell = self._placed_cell(cell)
        res = []
        for idx, gp in zip(indices, gps):
            # if cell is farther in the direction than gp[idx], then don't need
            # to avoid any of the stretched grided perms
            if not self._farther(cell, gp.pos[idx], direction):
                for stretched_gp in row_col_map.preimage_gp(gp):
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
        row_col_map = self.multiplex_map(*self._tiling.dimensions, cell)
        placed_cell = self._placed_cell(cell)
        res = []
        for idx, gp in zip(indices, gps):
            if gp.pos[idx] == cell:
                for stretched_gp in row_col_map.preimage_gp(gp):
                    if stretched_gp.pos[idx] == placed_cell:
                        res.append(stretched_gp)
        return res

    def multiplex_map(self, width: int, height: int, cell: Cell) -> RowColMap:
        """Return the RowColMap when cell is stretched into a 3x3."""
        # TODO: cache this?
        x, y = cell
        row_map = dict()
        col_map = dict()
        for i in range(width):
            xs = (
                [i]
                if i < x or not self.own_col
                else [i, i + 1, i + 2]
                if i == x
                else [i + 2]
            )
            for a in xs:
                col_map[a] = i

        for j in range(height):
            ys = (
                [j]
                if j < y or not self.own_row
                else [j, j + 1, j + 2]
                if j == y
                else [j + 2]
            )
            for b in ys:
                row_map[b] = j
        return RowColMap(row_map, col_map)

    def multiplex_tiling(self, tiling: "Tiling", cell: Cell) -> "Tiling":
        """
        Return the tiling created by 'multipexing' in cell.
        That is stretching the cell to be a 3x3 square.
        """
        # TODO: cache this?
        row_col_map = self.multiplex_map(*tiling.dimensions, cell)
        # TODO: should we optimise this to stop adding gps that are in cells we will
        # later mark as empty?
        underlying = row_col_map.preimage_tiling(tiling.remove_parameters())
        params = [self.multiplex_parameter(param, cell) for param in tiling.parameters]
        return underlying.add_obstructions_and_requirements(
            self.empty_row_and_col_obs(cell, *underlying.dimensions)
            + self._point_obstructions(cell),
            self._point_requirements(cell),
        ).add_parameters(params)

    def multiplex_preimage(
        self, preimage: PreimageCounter, cell: Cell
    ) -> List[PreimageCounter]:
        """
        Return the list of preimages whose sum count the number of preimages
        when cell is multiplexed into a 3x3.
        """
        res: List[PreimageCounter] = []
        for precell in preimage.map.preimage_cell(cell):
            preimage_multiplex_map = self.multiplex_map(
                *preimage.tiling.dimensions, cell
            )
            multiplex_tiling = self.multiplex_tiling(preimage.tiling, precell)
            col_map = {}
            for x in range(multiplex_tiling.dimensions[0]):
                shift = 0 if x <= precell[0] else 1 if x == precell[0] + 1 else 2
                col_map[x] = (
                    preimage.map.map_col(preimage_multiplex_map.map_col(x)) + shift
                )
            row_map = {}
            for y in range(multiplex_tiling.dimensions[1]):
                shift = 0 if y <= precell[1] else 1 if y == precell[1] + 1 else 2
                row_map[y] = (
                    preimage.map.map_row(preimage_multiplex_map.map_row(y)) + shift
                )
            res.append(PreimageCounter(multiplex_tiling, RowColMap(row_map, col_map)))
        return res

    def multiplex_parameter(
        self, parameter: ParameterCounter, cell: Cell
    ) -> ParameterCounter:
        """
        Return the parameter when cell has been multiplexed into a 3x3.
        """
        return ParameterCounter(
            itertools.chain.from_iterable(
                self.multiplex_preimage(preimage, cell) for preimage in parameter
            )
        )

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
            multiplex_tiling = self.multiplex_tiling(self._tiling, cell)
            forced_obs = self.forced_obstructions_from_requirement(
                gps, indices, cell, direction
            )
            rem_req = self._remaining_requirement_from_requirement(gps, indices, cell)
            res.append(
                multiplex_tiling.add_obstructions_and_requirements(
                    forced_obs, [rem_req]
                )
            )
        return tuple(res)

    def place_point_of_gridded_permutation(
        self, gp: GriddedPerm, idx: int, direction: Dir
    ) -> "Tiling":
        """
        Return the tiling where the placed point correspond to the
        directionmost (the furtest in the given direction, ex: leftmost point)
        occurrence of the idx point in gp.
        """
        return self.place_point_of_req((gp,), (idx,), direction)[0]

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

from ..griddedperm import GriddedPerm, Obstruction, Requirement
from .tiling import Tiling
from permuta import Perm
from permuta.misc import (DIR_EAST, DIR_NONE, DIR_NORTH, DIR_SOUTH, DIR_WEST)


class RequirementPlacement(object):
    """
    The requirement placement container class.

    Check if a placement is a valid and then places points onto own row,
    own col, or both.
    """
    directions = (DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST)
    row_directions = (DIR_NORTH, DIR_SOUTH)
    col_directions = (DIR_EAST, DIR_WEST)

    def __init__(self, tiling):
        self.tiling = tiling

    def partial_point_placements(self):
        yield from self.point_placements(partial=True)

    def point_placements(self, partial=False):
        for cell in self.tiling.positive_cells:
            for direction in self.directions:
                yield self._place_point_in_cell(cell, direction, partial)

    def _place_point_in_cell(self, cell, direction, partial=False):
        point_req = GriddedPerm(Perm((0,)), (cell,))
        return self._place_point_of_req(point_req, 0, direction, partial)

    def partial_requirement_placements(self, length):
        yield from self.requirement_placements(length, partial=True)

    def requirement_placements(self, length, partial=False):
        req_tiling = Tiling(requirement=self.tiling.requirements)
        for gp in req_tiling.gridded_perms_of_length(length):
            if len(gp.factors()) == 1:
                for idx in range(length):
                    for direction in self.directions:
                        yield self._place_point_of_req(
                                                gp, idx, direction, partial)

    def _place_point_of_req(self, gp, idx, direction, partial=False):
        pass

    def partial_row_placements(self, check=False):
        yield from self.row_placements(check=check, partial=True)

    def row_placements(self, check=False, partial=False):
        for i in range(self.tiling.dimensions[1]):
            req_list = [GriddedPerm(Perm((0,)), cell)
                        for cell in self.tiling.cells_in_row(i)]
            if check:
                # TODO: add req_list, check if empty
                raise NotImplementedError("Check if contain list req")
            for direction in self.row_directions:
                yield self._place_point_of_req_list(
                                                req_list, direction, partial)

    def partial_col_placements(self, check=False):
        yield from self.col_placements(check=check, partial=True)

    def col_placements(self, check=False):
        for i in range(self.tiling.dimesions[0]):
            req_list = [GriddedPerm(Perm((0,)), cell)
                        for cell in self.tiling.cells_in_col(i)]
            if check:
                # TODO: add req_list, check if empty
                raise NotImplementedError("Check if contain list req")
            for direction in self.col_directions:
                yield self._place_point_of_req_list(
                                                req_list, direction, partial)

    def _place_point_of_req_list(self, req_list, direction, partial=False):
        pass

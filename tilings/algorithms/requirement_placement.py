from ..griddedperm import GriddedPerm, Obstruction, Requirement
from .tiling import Tiling
from itertools import chain
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
        self._stretched_obstructions = {}
        self._stretched_requirements = {}

    def _point_translation(self, gp, index, cell, own_row=True, own_col=True):
        # TODO: move to gridded perm?
        x, y = gp[index]
        return (x + 2 if own_col and index >= cell[0] else x,
                y + 2 if own_row and gp.patt[index] >= cell[1] else y)

    def _stretch_gridded_perm(self, gp, cell, own_row=True, own_col=True):
        # TODO: move to gridded perm?
        if not own_row and not own_col:
            raise ValueError("Must place at least on own row or on own column.")
        mindex, maxdex, minval, maxval = gp.get_bounding_box(cell)
        if not own_col:
            maxdex = mindex
        elif not own_row:
            maxval = minval

        # TODO: apply point translation to every cell
        res = [self._point_translation(gp, (i, j), own_row, own_col)
               for i in range(mindex, maxdex + 1)
               for j in range(minval, maxval + 1)]
        for index in gp.points_in_cell(cell):
            new_patt = Perm.to_standard(gp.patt[i]
                                        for i in range(len(gp)), if i != index)
            new_pos = [???]
            res.append(gp.__class__(new_patt, new_pos))

    def _stretch_gridded_perms(self, gps, cell, own_row=True, own_col=True):
        return list(chain.from_iterable(self._stretch_gridded_perm(
                                                    gp, cell, own_row, own_col)
                                        for gp in gps))

    def stretched_obstructions(self, cell, own_row=True, own_col=True):
        if (cell, own_row, own_col) not in self._stretched_obstructions:
            self._stretched_obstructions[(cell, own_row, own_col)] = \
                self._stretch_gridded_perms(
                            self.tiling.obstructions, cell, own_row, own_col)
        return self._stretched_obstructions[(cell, own_row, own_col)]

    def stretched_requirements(self, cell, own_row=True, own_col=True):
        if (cell, own_row, own_col) not in self._stretched_requirements:
            self._stretched_requirements[(cell, own_row, own_col)] = \
                        [self._stretch_gridded_perms(req_list,
                                                     cell, own_row, own_col)
                         for req_list in self.tiling.requirements]
        return self._stretched_requirements[(cell, own_row, own_col)]

    def forced_obstructions(self, gp, idx, direction, own_row, own_col):
        def farther(c1, c2):
            """Return True if c1 is farther in direction than c2."""
            if direction == DIR_EAST:
                return c1[0] > c2[0]
            elif direction == DIR_WEST:
                return c1[0] < c2[0]
            elif direction == DIR_NORTH:
                return c1[1] > c2[1]
            elif direction == DIR_SOUTH:
                return c1[1] < c2[1]
        return [stretched_gp for stretched_gp in self._stretch_gridded_perm(
                                             gp, gp.pos[idx], own_row, own_col)
                if farther(stretched_gp.pos[idx], gp.pos[idx])]

    def partial_point_placements(self):
        yield from self.point_placements(own_row=False, own_col=True)
        yield from self.point_placements(own_row=True, own_col=False)

    def point_placements(self, own_row=True, own_col=True):
        for cell in self.tiling.positive_cells:
            for direction in self.directions:
                yield self._place_point_in_cell(cell, direction, own_row, own_col)

    def _place_point_in_cell(self, cell, direction, own_row=True, own_col=True):
        point_req = GriddedPerm(Perm((0,)), (cell,))
        return self._place_point_of_req(point_req, 0, direction, own_row, own_col)

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

    def _place_point_of_req(self, gp, idx, direction, own_row=True, own_col=True):
        cell = gp[idx]
        stretched_obs = self.stretched_obstructions(cell, own_row, own_col)
        stretched_reqs = self.stretched_requirements(cell, own_row, own_col)
        forced_obs = self.forced_obstructions(gp, idx, direction, own_row, own_col)
        return Tiling(stretched_obs + forced_obs, stretched_reqs)

    # def partial_row_placements(self, check=False):
    #     yield from self.row_placements(check=check, partial=True)

    # def row_placements(self, check=False, partial=False):
    #     for i in range(self.tiling.dimensions[1]):
    #         req_list = [GriddedPerm(Perm((0,)), cell)
    #                     for cell in self.tiling.cells_in_row(i)]
    #         if check:
    #             # TODO: add req_list, check if empty
    #             raise NotImplementedError("Check if contain list req")
    #         for direction in self.row_directions:
    #             yield self._place_point_of_req_list(
    #                                             req_list, direction, partial)

    # def partial_col_placements(self, check=False):
    #     yield from self.col_placements(check=check, partial=True)

    # def col_placements(self, check=False):
    #     for i in range(self.tiling.dimesions[0]):
    #         req_list = [GriddedPerm(Perm((0,)), cell)
    #                     for cell in self.tiling.cells_in_col(i)]
    #         if check:
    #             # TODO: add req_list, check if empty
    #             raise NotImplementedError("Check if contain list req")
    #         for direction in self.col_directions:
    #             yield self._place_point_of_req_list(
    #                                             req_list, direction, partial)

    # def _place_point_of_req_list(self, req_list, direction, partial=False):
    #     pass

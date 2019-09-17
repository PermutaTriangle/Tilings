from tilings import GriddedPerm, Obstruction, Requirement, Tiling
from itertools import chain
from permuta import Perm
from permuta.misc import (DIR_EAST, DIR_NONE, DIR_NORTH, DIR_SOUTH, DIR_WEST)


class RequirementPlacement(object):
    """
    The requirement placement container class.

    Check if a placement is a valid and then places points onto own row,
    own col, or both.
    """


    def __init__(self, tiling, own_row=True, own_col=True):
        if not own_row and not own_col:
            raise ValueError("Must place at least on own row or on own column.")
        self.tiling = tiling
        self._own_row = own_row
        self._own_col = own_col
        self._stretched_obstructions_cache = {}
        self._stretched_requirements_cache = {}
        if self._own_row and self._own_col:
            self.directions = (DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST)
        elif self._own_row:
            self.directions = (DIR_NORTH, DIR_SOUTH)
        elif self._own_col:
            self.directions = (DIR_EAST, DIR_WEST)

    def _point_translation(self, gp, index, placed_cell):
        # TODO: move to gridded perm?
        x, y = gp.pos[index]
        return (x + 2 if self._own_col and index >= placed_cell[0] else x,
                y + 2 if self._own_row and gp.patt[index] >= placed_cell[1] else y)

    def _gridded_perm_translation(self, gp, placed_cell):
        # TODO: move to gridded perm?
        newpos = [self._point_translation(gp, index, placed_cell)
                  for index in range(len(gp))]
        return gp.__class__(gp.patt, newpos)

    def _placed_cell(self, cell):
        x, y = cell
        if self._own_col:
            x += 1
        if self._own_row:
            y += 1
        return x, y

    def _point_obstructions(self, cell):
        placed_cell = self._placed_cell(cell)
        return [Obstruction(Perm((0, 1)), (placed_cell, placed_cell)),
                Obstruction(Perm((1, 0)), (placed_cell, placed_cell))]

    def _point_requirements(self, cell):
        placed_cell = self._placed_cell(cell)
        return [[Requirement(Perm((0, )), (placed_cell, ))]]

    def _stretch_gridded_perm(self, gp, cell):
        # TODO: move to gridded perm?
        mindex, maxdex, minval, maxval = gp.get_bounding_box(cell)
        if not self._own_col:
            maxdex = mindex
        elif not self._own_row:
            maxval = minval
        res = [self._gridded_perm_translation(gp, (i, j))
               for i in range(mindex, maxdex + 1)
               for j in range(minval, maxval + 1)]
        for index in gp.points_in_cell(cell):
            # TODO: to prepare for intervals consider all ways of drawing a
            #       rectangle around point in cell.
            new_pos = [self._point_translation(gp, i, (index, gp.patt[index]))
                       if i != index else self._placed_cell(cell)
                       for i in range(len(gp))]
            res.append(gp.__class__(gp.patt, new_pos))
        return res

    def _stretch_gridded_perms(self, gps, cell):
        return list(chain.from_iterable(self._stretch_gridded_perm(gp, cell)
                                        for gp in gps))

    def stretched_obstructions(self, cell):
        if cell not in self._stretched_obstructions_cache:
            self._stretched_obstructions_cache[cell] = \
                self._stretch_gridded_perms(self.tiling.obstructions, cell)
        return self._stretched_obstructions_cache[cell]

    def stretched_requirements(self, cell):
        if cell not in self._stretched_requirements_cache:
            self._stretched_requirements_cache[cell] = \
                        [self._stretch_gridded_perms(req_list, cell)
                         for req_list in self.tiling.requirements]
        return self._stretched_requirements_cache[cell]

    def farther(self, c1, c2, direction):
        """Return True if c1 is farther in direction than c2."""
        if direction == DIR_EAST:
            return c1[0] > c2[0]
        elif direction == DIR_WEST:
            return c1[0] < c2[0]
        elif direction == DIR_NORTH:
            return c1[1] > c2[1]
        elif direction == DIR_SOUTH:
            return c1[1] < c2[1]

    def forced_obstructions_from_patt(self, gp, idx, direction):
        placed_cell = self._placed_cell(gp.pos[idx])
        gp = Obstruction(gp.patt, gp.pos)
        return [stretched_gp
                for stretched_gp in self._stretch_gridded_perm(gp, gp.pos[idx])
                if self.farther(stretched_gp.pos[idx], placed_cell, direction)]

    def forced_obstructions_from_list(self, gp_list, cell, direction):
        placed_cell = self._placed_cell(cell)
        return [stretched_gp
                for stretched_gp in chain.from_iterable(
                       self._stretch_gridded_perm(Obstruction(gp.patt, gp.pos),
                                                  cell) for gp in gp_list)
                if any(self.farther(c1, placed_cell, direction)
                       for c1 in stretched_gp.pos)]

    def _place_point_in_cell(self, cell, direction):
        point_req = GriddedPerm(Perm((0,)), (cell,))
        return self._place_point_of_req(point_req, 0, direction)

    def placed_obstructions_and_requirements(self, cell):
        stretched_obs = self.stretched_obstructions(cell)
        stretched_reqs = self.stretched_requirements(cell)
        point_obs = self._point_obstructions(cell)
        point_req = self._point_requirements(cell)
        return stretched_obs + point_obs, stretched_reqs + point_req

    def _place_point_of_req(self, gp, idx, direction):
        cell = gp.pos[idx]
        obs, reqs = self.placed_obstructions_and_requirements(cell)
        forced_obs = self.forced_obstructions_from_patt(gp, idx, direction)
        return Tiling(obs + forced_obs, reqs)

    def _place_point_of_req_list(self, req_list, direction):
        cells = set(chain.from_iterable(req.pos for req in req_list))
        tilings = []
        for cell in cells:
            obs, reqs = self.placed_obstructions_and_requirements(cell)
            forced_obs = self.forced_obstructions_from_list(req_list, cell, direction)
            tilings.append(Tiling(obs + forced_obs, reqs))
        return tilings

    def point_placements(self):
        for cell in self.tiling.positive_cells:
            for direction in self.directions:
                print("Placing:", cell, "Direction:", direction)
                yield self._place_point_in_cell(cell, direction)

    # def requirement_placements(self, length):
    #     obs_tiling = Tiling(self.tiling.obstructions)
    #     for gp in obs_tiling.gridded_perms_of_length(length):
    #         if len(gp.factors()) == 1:
    #             if Tiling(self.tiling.obstruction + (gp, ),
    #                       self.tiling.requirements).is_empty():
    #                 for idx in range(length):
    #                     for direction in self.directions:
    #                         yield self._place_point_of_req(gp, idx, direction)

    def requirement_placements(self):
        for req in self.tiling.requirements:
            if len(req) == 1:
                for gp in req[0].all_subperms(proper=False):
                    for idx in range(len(gp)):
                        for direction in self.directions:
                            yield self._place_point_of_req(gp, idx, direction)

    def row_placements(self, check=False):
        if not self._own_row:
            raise ValueError("Row placements must be onto own row.")
        for i in range(self.tiling.dimensions[1]):
            req_list = [Requirement(Perm((0,)), (cell,))
                        for cell in self.tiling.cells_in_row(i)]
            if check:
                # TODO: add req_list, check if empty
                raise NotImplementedError("Check if contain list req")
            for direction in self.directions:
                print("ROW:", i, "DIRECTION:", direction)
                yield self._place_point_of_req_list(req_list, direction)

    def col_placements(self, check=False):
        if not self._own_col:
            raise ValueError("Col placements must be onto own col.")
        for i in range(self.tiling.dimensions[0]):
            req_list = [Requirement(Perm((0,)), (cell,))
                        for cell in self.tiling.cells_in_col(i)]
            if check:
                # TODO: add req_list, check if empty
                raise NotImplementedError("Check if contain list req")
            for direction in self.directions:
                print("COL:", i, "DIRECTION:", direction)
                yield self._place_point_of_req_list(req_list, direction)

if __name__ == "__main__":
    t = Tiling.from_string("123").insert_cell((0, 0))

    algorithm = RequirementPlacement(t, own_row=True, own_col=False)
    for placed_tiling in algorithm.point_placements():
        print(placed_tiling)

    for strategy in algorithm.row_placements():
        for tiling in strategy:
            print(tiling)

    for strategy in algorithm.col_placements():
        for tiling in strategy:
            print(tiling)
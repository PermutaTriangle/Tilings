from .griddedperm import GriddedPerm
from .obstruction import Obstruction
from permuta.misc import DIR_EAST, DIR_NONE, DIR_WEST, DIR_NORTH, DIR_SOUTH
from permuta import Perm


class Requirement(GriddedPerm):
    def __init__(self, pattern, positions):
        super(Requirement, self).__init__(pattern, positions)

    def forced_point(self, cell, direction, forced_index):
        return self.place_forced_point(forced_index, cell)

    def place_forced_point(self, forced_index, direction):
        """Places the point at forced_index in the requirement with the given
        direction of force.

        In a gridded permutation satisfying the requirement, the placed point
        will correspond to a point in an occurrence of the requirement, such
        that the point at the index in the occurrence is forced to the
        direction given.  in an occurrence of the requirement

        Returns two lists, the remaining requirement and a list of obstructions
        that were created."""
        # If the gridded permutation does not span the cell, the resulting list
        # of new obstructions would contain only the gridded permutation
        # itself.
        cell = self._pos[forced_index]
        obstruction_list = []
        req_list = []
        # If the gridded permutation contains a point in the cell (occupies)
        mindex, maxdex, minval, maxval = self.get_bounding_box(cell)
        if self.occupies(cell):
            if direction != DIR_NONE:
                forced_val = self.patt[forced_index]
                newpatt = Perm.to_standard(
                    self.patt[i] for i in range(len(self))
                    if i != forced_index)
                newposition = [
                    self.point_translation(p, (forced_index, forced_val))
                    for p in range(len(self)) if p != forced_index]
                req_list.append(self.__class__(newpatt, newposition))
            else:
                raise ValueError("Must apply some force!")

            if direction == DIR_WEST:
                mindex = forced_index + 1
            elif direction == DIR_SOUTH:
                minval = forced_val + 1
            elif direction == DIR_EAST:
                maxdex = forced_index
            elif direction == DIR_NORTH:
                maxval = forced_val
        for i in range(mindex, maxdex + 1):
            for j in range(minval, maxval + 1):
                grid = self.stretch_gridding((i, j))
                obstruction_list.append(Obstruction(grid.patt, grid.pos))
        return req_list, obstruction_list

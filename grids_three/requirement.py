from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NONE, DIR_NORTH, DIR_SOUTH, DIR_WEST

from .griddedperm import GriddedPerm
from .obstruction import Obstruction


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
        if direction == DIR_NONE:
            raise ValueError("Must apply some force!")
        # If the gridded permutation does not span the cell, the resulting list
        # of new obstructions would contain only the gridded permutation
        # itself.
        cell = self._pos[forced_index]
        obstruction_list = []
        req_list = []
        mindex, maxdex, minval, maxval = self.get_bounding_box(cell)

        # Construct the requirement that remains after using the point
        forced_val = self.patt[forced_index]
        newpatt = Perm.to_standard(
            self.patt[i] for i in range(len(self))
            if i != forced_index)
        newposition = [
            self.point_translation(i, (forced_index, forced_val))
            for i in range(len(self)) if i != forced_index]
        req_list.append(self.__class__(newpatt, newposition))

        if direction == DIR_WEST:
            mindex = forced_index + 1
        elif direction == DIR_SOUTH:
            minval = forced_val + 1
        elif direction == DIR_EAST:
            maxdex = forced_index
        elif direction == DIR_NORTH:
            maxval = forced_val

        # Try to use the placed point as each of the points in the requirement
        for p in range(mindex, maxdex):
            if self.patt[p] >= minval and self.patt[p] < maxval:
                newpatt = Perm.to_standard(
                    self.patt[i] for i in range(len(self)) if i != p)
                newposition = [
                    self.point_translation(i, (p, self.patt[p]))
                    for i in range(len(self)) if i != p]
                obstruction_list.append(Obstruction(newpatt, newposition))

        for i in range(mindex, maxdex + 1):
            for j in range(minval, maxval + 1):
                grid = self.stretch_gridding((i, j))
                obstruction_list.append(Obstruction(grid.patt, grid.pos))
        return req_list, obstruction_list

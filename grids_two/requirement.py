from .griddedperm import GriddedPerm
from .obstruction import Obstruction

class Requirement(GriddedPerm):
    def __init__(self, pattern, positions):
        super(Requirement, self).__init__(pattern, positions)
    
    def forced_point(self, cell, direction, forced_index):
        """Places the point in the given requirement located at forced_index in 
        with force that is equal to the direction.
        
        Returns two lists, the remaining requirement and a list of obstructions
        that were created."""
        # If the gridded permutation does not span the cell, the resulting list
        # of new obstructions would contain only the gridded permutation
        # itself.
        obstruction_list = []
        req_list = []
        # If the gridded permutation contains a point in the cell (occupies)
        mindex, maxdex, minval, maxval = self.get_bounding_box(cell)
        # We want the force to be in the opposite direction
        if direction == DIR_EAST:
            direction = DIR_WEST
        elif direction == DIR_NORTH:
            direction = DIR_SOUTH
        elif direction == DIR_WEST:
            direction = DIR_EAST
        elif direction == DIR_SOUTH:
            direction = DIR_NORTH
        
        if self.occupies(cell):
            if direction != DIR_NONE:
                forced_val = self.patt[forced_index]
                newpatt = Perm.to_standard(
                    self.patt[i] for i in range(len(self))
                    if i != forced_index)
                newposition = [
                    self.point_translation(p, (forced_index, forced_val))
                    for p in range(len(self)) if p != forced_index]
                res.append(self.__class__(newpatt, newposition))
            else:
                for index in self.points_in_cell(cell):
                    newpatt = Perm.to_standard(
                        self.patt[i] for i in range(len(self)) 
                        if i != index)
                    newposition = [
                        self.point_translation(p, (index, self.patt[index]))
                        for p in range(len(self)) if p != index]
                    req_list.append(self.__class__(newpatt, newposition))
        # Gridded permutation spans the cell, find the bounding box of all the
        # possible locations for the placed point in relation to the pattern.
            if direction == DIR_EAST:
                mindex = forced_index + 1
            elif direction == DIR_NORTH:
                minval = forced_val + 1
            elif direction == DIR_WEST:
                maxdex = forced_index
            elif direction == DIR_SOUTH:
                maxval = forced_val
        for i in range(mindex, maxdex + 1):
            for j in range(minval, maxval + 1):
                grid = self.stretch_gridding((i,j))
                obstruction_list.append(Obstruction(grid.patt, grid.pos))
        return req_list, obstruction_list

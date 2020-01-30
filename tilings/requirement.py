from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NONE, DIR_NORTH, DIR_SOUTH, DIR_WEST

from .griddedperm import GriddedPerm
from .obstruction import Obstruction


class Requirement(GriddedPerm):
    def __init__(self, pattern, positions):
        super(Requirement, self).__init__(pattern, positions)

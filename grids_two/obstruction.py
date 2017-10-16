from .griddedperm import GriddedPerm


class Obstruction(GriddedPerm):
    def __init__(self, pattern, positions):
        super(Obstruction, self).__init__(pattern, positions)

    def is_point_obstr(self):
        return super(Obstruction, self).is_point_perm()

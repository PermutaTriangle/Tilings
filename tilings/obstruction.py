from .griddedperm import GriddedPerm


class Obstruction(GriddedPerm):
    def is_point_obstr(self):
        return super(Obstruction, self).is_point_perm()

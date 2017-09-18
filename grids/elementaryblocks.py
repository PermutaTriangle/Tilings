from permuta import Perm
from permuta import PermSet

from .positiveclass import PositiveClass

"""Different blocks for Tilings, for convenience."""

point_or_empty = PermSet.avoiding([Perm((1, 0)), Perm((0, 1))])
point = PositiveClass(point_or_empty)
increasing = PermSet.avoiding(Perm((1, 0)))
decreasing = PermSet.avoiding(Perm((0, 1)))

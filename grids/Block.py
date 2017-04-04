from permuta import Perm
from permuta import PermSet

from .PositiveClass import PositiveClass


__all__ = ["Block"]


class Block(object):
    """Different blocks for Tilings, for convenience."""
    all = PermSet()
    point_or_empty = PermSet.avoiding([Perm((1, 0)), Perm((0, 1))])
    point = PositiveClass(point_or_empty)
    increasing = PermSet.avoiding(Perm((1, 0)))
    decreasing = PermSet.avoiding(Perm((0, 1)))

    def __new__(_cls):
        raise RuntimeError("Block class should not be instantiated")

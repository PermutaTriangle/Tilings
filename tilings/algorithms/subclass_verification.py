"""
The main algorithm for detecting when the underlying ungridded permutations on a tiling
are contained one of a given set of subclasses.

NOTES:
    - I suspect this algorithm will perform much better when <GriddedPermsOnTiling> is
      replaced by a non-minimal version of <MinimalGriddedPerms>, both because of its
      intense optimization and its breadth-first approach.
    - This will be both more effective, and faster, if you don't do it until after any
      points have been factored away.
    - It may be possible to be smarter, and consider variable upper bounds on max_length
      depending on which requirement in a list you're placing.
"""

from typing import TYPE_CHECKING, FrozenSet, List

from permuta import Perm
from tilings.algorithms import GriddedPermsOnTiling

if TYPE_CHECKING:
    from tilings import Tiling


class SubclassVerificationAlgorithm:
    def __init__(self, tiling: "Tiling", perms_to_check: FrozenSet[Perm]) -> None:
        self.tiling = tiling
        self.perms_to_check = perms_to_check

    def verified(self) -> bool:
        max_length = self.tiling.maximum_length_of_minimum_gridded_perm() + max(
            map(len, self.perms_to_check)
        )

        GP = GriddedPermsOnTiling(self.tiling, max_length)
        perms_left = set(self.perms_to_check)

        for gp in GP:
            to_remove: List[Perm] = []
            for perm in perms_left:
                if gp.patt.contains(perm):
                    to_remove.append(perm)
            for perm_to_remove in to_remove:
                perms_left.remove(perm_to_remove)
            if len(perms_left) == 0:
                return False
        return True

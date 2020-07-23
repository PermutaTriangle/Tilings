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

from time import time
from typing import TYPE_CHECKING, List, Set

from permuta import Perm
from tilings.algorithms import GriddedPermsOnTiling

if TYPE_CHECKING:
    from tilings import Tiling


class SubclassVerificationAlgorithm:
    def __init__(self, tiling: "Tiling", perms_to_check: Set[Perm]) -> None:
        self.tiling = tiling
        self.perms_to_check = perms_to_check

    def quick_pare(self) -> Set[Perm]:

        if len(self.tiling.requirements) == 0:
            perms_leftover = set()

            cell_basis = self.tiling.cell_basis()
            all_bases = set(tuple(obs) for obs, _ in cell_basis.values())
            max_base_len = {base: max(len(b) for b in base) for base in all_bases}
            for perm in self.perms_to_check:
                if not any(
                    len(perm) < max_base_len[base] or perm.avoids(*base)
                    for base in all_bases
                ):
                    perms_leftover.add(perm)
            return perms_leftover

        if (
            len(self.tiling.requirements) == 1
            and len(self.tiling.requirements[0]) == 1
            and len(self.tiling.requirements[0][0]) == 1
        ):
            pos_cell = self.tiling.requirements[0][0].pos[0]
            pos_basis = self.tiling.cell_basis()[pos_cell][0]
            max_pos_basis_len = max(len(b) for b in pos_basis)
            perms_leftover = set()
            for perm in self.perms_to_check:
                if not (len(perm) < max_pos_basis_len or perm.avoids(*pos_basis)):
                    perms_leftover.add(perm)
            return perms_leftover

        return self.perms_to_check

    def verified(self) -> bool:
        # print(self.tiling)
        # if len(self.tiling.point_cells) > 0:
        #     return False

        tt = time()

        # print("=" * 100)
        # print(self.tiling)
        # traceback.print_stack()
        perms_to_check = self.quick_pare()
        pare_time = time() - tt
        # print(perms_to_check)
        if len(perms_to_check) == 0:
            return False

        max_len_of_perms_to_check = max(map(len, perms_to_check))
        max_length = (
            self.tiling.maximum_length_of_minimum_gridded_perm()
            + max_len_of_perms_to_check
        )

        GP = GriddedPermsOnTiling(self.tiling).gridded_perms(
            max_length, place_at_most=max_len_of_perms_to_check
        )
        perms_left = set(perms_to_check)

        for gp in GP:
            to_remove: List[Perm] = []
            for perm in perms_left:
                if gp.patt.contains(perm):
                    to_remove.append(perm)
            for perm_to_remove in to_remove:
                perms_left.remove(perm_to_remove)
            if len(perms_left) == 0:
                total_time = time() - tt
                # print("=" * 100)
                # print(self.tiling)
                # print(pare_time)
                # print(total_time)
                # print(False)
                return False
        total_time = time() - tt
        # print("=" * 100)
        # print(self.tiling)
        # print(pare_time)
        # print(total_time)
        # print(True)
        return True

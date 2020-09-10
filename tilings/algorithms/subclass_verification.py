"""
The main algorithm for detecting when the underlying ungridded permutations on a tiling
are contained in one of a given set of subclasses.
"""

from typing import TYPE_CHECKING, List, Optional, Set, Tuple, cast

from permuta import Perm
from tilings.algorithms import GriddedPermsOnTiling

if TYPE_CHECKING:
    from tilings import Tiling


class SubclassVerificationAlgorithm:
    def __init__(self, tiling: "Tiling", perms_to_check: Set[Perm]) -> None:
        self.tiling = tiling
        self.perms_to_check = perms_to_check
        self._subclasses: Optional[Tuple[Perm, ...]] = None

    def quick_pare(self) -> Set[Perm]:
        """
        Quickly eliminates some subclasses that need to be checked before generating
        gridded perms. Often this is able to eliminate all subclasses.
        """

        # First pare: The local gridded permutations on a tiling with no requirements
        # are those contained in some cell basis.
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

        # Second pare: If a tiling has a single list requirement, which contains a
        # single requirement, which is a point, then the cell basis of that particular
        # positive cell can be used to rule out subclasses.
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

    def is_verified(self) -> bool:
        return bool(self.subclasses)

    @property
    def subclasses(self) -> Tuple[Perm, ...]:
        if self._subclasses is None:
            self.compute_subclasses()
        return cast(Tuple[Perm, ...], self._subclasses)

    def compute_subclasses(self) -> None:

        self._subclasses = tuple()

        perms_to_check = self.quick_pare()
        if len(perms_to_check) == 0:
            return

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
            perms_left.difference_update(to_remove)
            if len(perms_left) == 0:
                return
        self._subclasses = tuple(sorted(perms_left))

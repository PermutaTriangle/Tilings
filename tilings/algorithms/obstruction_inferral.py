import abc
from typing import TYPE_CHECKING, Iterable, List, Optional, Set, Tuple

from tilings import GriddedPerm
from tilings.algorithms.gridded_perm_generation import GriddedPermsOnTiling

if TYPE_CHECKING:
    from tilings import Tiling

Cell = Tuple[int, int]


class ObstructionInferral(abc.ABC):
    """
    Algorithm to compute the tiling created by adding all obstructions from
    `self.potential_new_obs()` that can be added to the tiling.
    """

    def __init__(self, tiling: "Tiling"):
        self._tiling = tiling
        self._new_obs: Optional[List[GriddedPerm]] = None

    @abc.abstractmethod
    def potential_new_obs(self) -> Iterable[GriddedPerm]:
        """
        Return an iterable of new obstructions that should be added to the
        tiling if possible.
        """

    def new_obs(self, yield_non_minimal=False) -> List[GriddedPerm]:
        """
        Returns the list of new obstructions that can be added to the tiling.
        """
        if self._new_obs is not None:
            return self._new_obs

        perms_to_check = tuple(self.potential_new_obs())
        if not perms_to_check:
            self._new_obs = []
            return self._new_obs

        max_len_of_perms_to_check = max(map(len, perms_to_check))
        max_length = (
            self._tiling.maximum_length_of_minimum_gridded_perm()
            + max_len_of_perms_to_check
        )
        GP = GriddedPermsOnTiling(
            self._tiling, yield_non_minimal=yield_non_minimal
        ).gridded_perms(max_length, place_at_most=max_len_of_perms_to_check)
        perms_left = set(perms_to_check)
        for gp in GP:
            to_remove: List[GriddedPerm] = []
            for perm in perms_left:
                if gp.contains(perm):
                    to_remove.append(perm)
            perms_left.difference_update(to_remove)
            if not perms_left:
                break
        self._new_obs = sorted(perms_left)
        return self._new_obs

    @staticmethod
    def can_add_obstruction(obstruction: GriddedPerm, tiling: "Tiling") -> bool:
        """Return true if `obstruction` can be added to `tiling`."""
        return tiling.add_requirement(obstruction.patt, obstruction.pos).is_empty()

    def obstruction_inferral(self) -> "Tiling":
        """
        Return the tiling with the new obstructions.
        """
        return self._tiling.add_obstructions(self.new_obs())

    # TODO: move to strategy class

    def formal_step(self):
        """Return a string describing the operation performed."""
        return f"Added the obstructions {self.new_obs()}."


class SubobstructionInferral(ObstructionInferral):
    """
    Algorithm to compute the tiling created by adding all
    subobstructions which can be added.
    """

    def potential_new_obs(self) -> Set[GriddedPerm]:
        """
        Return the set of all subobstructions of the tiling.
        """
        subobs: Set[GriddedPerm] = set()
        for ob in self._tiling.obstructions:
            subobs.update(ob.all_subperms(proper=True))
        subobs.remove(GriddedPerm.empty_perm())
        return subobs


class AllObstructionInferral(ObstructionInferral):
    """
    Algorithm to compute the tiling created by adding all
    obstruction of length up to obstruction_length which can be added.
    """

    def __init__(self, tiling: "Tiling", obstruction_length: int) -> None:
        super().__init__(tiling)
        self._obs_len = obstruction_length

    @property
    def obstruction_length(self) -> int:
        return self._obs_len

    def not_required(self, gp: GriddedPerm) -> bool:
        """
        Returns True if the gridded perm `gp` is not required by any
        requirement list of the tiling.
        """
        return all(
            any(gp not in req for req in req_list)
            for req_list in self._tiling.requirements
        )

    def potential_new_obs(self) -> List[GriddedPerm]:
        """
        Iterator over all possible obstruction of `self.obstruction_length`.
        """
        if not self._tiling.requirements:
            return []
        no_req_tiling = self._tiling.__class__(self._tiling.obstructions)
        n = self._obs_len
        pot_obs = filter(self.not_required, no_req_tiling.gridded_perms(n))
        return list(GriddedPerm(gp.patt, gp.pos) for gp in pot_obs)


class EmptyCellInferral(AllObstructionInferral):
    """
    Try to add a point obstruction to all the active non positive cell
    """

    def __init__(self, tiling: "Tiling"):
        super().__init__(tiling, 1)

    def empty_cells(self) -> List[Cell]:
        """
        Return an iterator over all cell that where discovered to be empty.
        """
        return list(ob.pos[0] for ob in self.new_obs())

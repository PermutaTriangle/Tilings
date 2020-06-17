import abc
from typing import TYPE_CHECKING, Iterable, List, Optional, Set, Tuple

from tilings import GriddedPerm

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

    def new_obs(self) -> List[GriddedPerm]:
        """
        Returns the list of new obstructions that can be added to the tiling.
        """
        if self._new_obs is not None:
            return self._new_obs
        newobs: List[GriddedPerm] = []
        for ob in sorted(self.potential_new_obs(), key=len):
            cont_newob = any(newob in ob for newob in newobs)
            if not cont_newob and self.can_add_obstruction(ob, self._tiling):
                newobs.append(ob)
        self._new_obs = newobs
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
        """ Return a string describing the operation performed. """
        return "Added the obstructions {}.".format(self.new_obs())


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

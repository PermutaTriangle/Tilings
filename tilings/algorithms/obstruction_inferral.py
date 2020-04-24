import abc
from itertools import chain

from permuta import Perm
from tilings import Obstruction


class ObstructionInferral(abc.ABC):
    """
    Algorithm to compute the tiling created by adding all obstructions from
    `self.potential_new_obs()` that can be added to the tiling.
    """

    def __init__(self, tiling):
        self._tiling = tiling
        self._new_obs = None

    @abc.abstractmethod
    def potential_new_obs(self):
        """
        Return an iterable of new obstructions that should be added to the
        tiling if possible.
        """

    def new_obs(self):
        """
        Returns the list of new obstructions that can be added to the tiling.
        """
        if self._new_obs is not None:
            return self._new_obs
        newobs = []
        for ob in sorted(self.potential_new_obs(), key=len):
            cont_newob = any(newob in ob for newob in newobs)
            if not cont_newob and self.can_add_obstruction(ob, self._tiling):
                newobs.append(ob)
        self._new_obs = newobs
        return self._new_obs

    @staticmethod
    def can_add_obstruction(obstruction, tiling):
        """Return true if `obstruction` can be added to `tiling`."""
        return tiling.add_requirement(obstruction.patt, obstruction.pos).is_empty()

    def obstruction_inferral(self):
        """
        Return the tiling with the new obstructions.
        """
        obs = chain(self._tiling.obstructions, self.new_obs())
        reqs = self._tiling.requirements
        return self._tiling.__class__(obs, reqs)

    # TODO: move to strategy class

    def formal_step(self):
        """ Return a string describing the operation performed. """
        return "Added the obstructions {}.".format(self.new_obs())

    def rule(self):
        """
        Return a comb_spec_searcher Rule for the new tiling.

        If no new obstruction is added, returns None.
        """
        if self.new_obs():
            return InferralRule(self.formal_step(), self.obstruction_inferral())


class SubobstructionInferral(ObstructionInferral):
    """
    Algorithm to compute the tiling created by adding all
    subobstructions which can be added.
    """

    def potential_new_obs(self):
        """
        Return the set of all subobstructions of the tiling.
        """
        subobs = set()
        for ob in self._tiling.obstructions:
            subobs.update(ob.all_subperms(proper=True))
        subobs.remove(Obstruction(Perm(), []))
        return subobs


class AllObstructionInferral(ObstructionInferral):
    """
    Algorithm to compute the tiling created by adding all
    obstruction of length up to obstruction_length which can be added.
    """

    def __init__(self, tiling, obstruction_length):
        super().__init__(tiling)
        self._obs_len = obstruction_length

    @property
    def obstruction_length(self):
        return self._obs_len

    def not_required(self, gp):
        """
        Returns True if the gridded perm `gp` is not required by any
        requirement list of the tiling.
        """
        return all(
            any(gp not in req for req in req_list)
            for req_list in self._tiling.requirements
        )

    def potential_new_obs(self):
        """
        Iterator over all possible obstruction of `self.obstruction_length`.
        """
        if not self._tiling.requirements:
            return []
        no_req_tiling = self._tiling.__class__(self._tiling.obstructions)
        n = self._obs_len
        pot_obs = filter(self.not_required, no_req_tiling.gridded_perms(n))
        return (Obstruction(gp.patt, gp.pos) for gp in pot_obs)


class EmptyCellInferral(AllObstructionInferral):
    """
    Try to add a point obstruction to all the active non positive cell
    """

    def __init__(self, tiling):
        super().__init__(tiling, 1)

    def empty_cells(self):
        """
        Return an iterator over all cell that where discovered to be empty.
        """
        return (ob.pos[0] for ob in self.new_obs())

import abc
from itertools import chain

from comb_spec_searcher import InferralRule
from tilings import Obstruction


class ObstructionInferral(abc.ABC):
    """
    Algorithm to compute the tiling created by adding all obstructions from
    `self.potential_new_obs()` that can be added to the tiling.
    """
    def __init__(self, tiling):
        self._tiling = tiling

    @abc.abstractmethod
    def potential_new_obs(self):
        """
        Return an iterable of new obstruction that should be added to the
        tiling if possible
        """
        pass

    def new_obs(self):
        """
        Returns the list of new obstruction that can be added to the tiling.
        """
        if hasattr(self, '_new_obs'):
            return self._new_obs
        newobs = []
        merged_tiling = self._tiling.merge()
        for ob in sorted(self.potential_new_obs(), key=len):
            if self.can_add_obstruction(ob, merged_tiling):
                newobs.append(ob)
                merged_tiling = merged_tiling.__class__(
                    obstructions=chain(merged_tiling.obstructions, (ob,)),
                    requirements=merged_tiling.requirements,
                    remove_empty=False)
        self._new_obs = newobs
        return self._new_obs

    @staticmethod
    def can_add_obstruction(obstruction, tiling):
        """Return true if obstruction can be added to tiling."""
        return (tiling.add_requirement(obstruction.patt, obstruction.pos)
                .merge().is_empty())

    def obstruction_inferral(self):
        """
        Return the tiling with the new obstructions.
        """
        obs = chain(self._tiling.obstructions, self.new_obs())
        reqs = self._tiling.requirements
        return self._tiling.__class__(obs, reqs)

    def formal_step(self):
        """ Return a string describing the operation performed. """
        return "Added the obstructions {}.".format(self.new_obs())

    def rule(self):
        """ Return a comb_spec_searcher Rule for the new tiling. """
        return InferralRule(self.formal_step(),
                            self.subobstruction_inferral())


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
            subobs.update(ob.all_subperms())
        return subobs


class EmptyCellInferral(ObstructionInferral):
    def potential_new_obs(self):
        """
        Return an iterator over point obstructions in non-positive cells.
        """
        active = set(tiling.active_cells)
        positive = set(tiling.positive_cells)
        return (cell for cell in active - positive)

    def empty_cells(self):
        """
        Return an iterator over all cell that where discovered to be empty.
        """
        return (ob.pos[0] for ob in self.new_obs())

    def formal_step(self):
        """ Return a string describing the operation performed. """
        empty_cells_str - ", ".join(map(str, self.empty_cells()))
        return "the cells {} are empty".format(empty_cells_str)

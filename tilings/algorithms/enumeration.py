import abc
from itertools import chain
import sympy

from tilescopethree import TileScopeTHREE
from tilescopethree.strategies import (factor,
                                       requirement_corroboration,
                                       all_factor_insertions,
                                       subset_verified)
from comb_spec_searcher import StrategyPack, VerificationRule
from tilings.exception import InvalidOperationError

class Enumeration(abc.ABC):
    """
    General representation of a strategy to enumerate tilings.
    """

    def __init__(self, tiling):
        self.tiling = tiling

    @abc.abstractproperty
    def pack(self):
        """
        Returns a TileScope pack that fines a proof tree for the tilings in
        which the verification strategy used are "simpler".

        The pack is assumed to produce a finite universe.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def verified(self):
        """
        Returns True if enumeration strategy works for the tiling.
        """
        raise NotImplementedError

    @abc.abstractproperty
    def formal_step(self):
        """
        Return a string that describe the verification strategy.
        """
        raise NotImplementedError

    def verification_rule(self):
        if self.verified():
            return VerificationRule(formal_step=self.formal_step)

    def get_tree(self, **kwargs):
        """
        Returns a tree for the tilings. Raises an `InvalidOperationError` if no
        tree can be found.

        All the kwargs are past to the `auto_search` method of the TileScope
        instance that search for the tree.

        Raises an InvalidOperationError if the tiling is not verified.
        """
        if not self.verified():
            raise InvalidOperationError('The tiling is not verified')
        searcher = TileScopeTHREE(self.tiling, self.pack)
        tree = searcher.auto_search(**kwargs)
        if tree is None:
            raise InvalidOperationError('Cannot find a tree')
        return tree

    def get_genf(self, **kwargs):
        """
        Returns the generating function for the tiling.

        All the kwargs are passed to `self.get_tree`.

        Raises an InvalidOperationError if the tiling is not verified.
        """
        if not self.verified():
            raise InvalidOperationError('The tiling is not verified')
        return self.get_tree(**kwargs).get_genf()


class BasicEnumeration(Enumeration):

    formal_step = 'Base cases'

    @property
    def pack(self):
        raise InvalidOperationError('Cannot get a tree for a basic enumeration')

    def get_tree(self, **kwargs):
        raise InvalidOperationError('Cannot get a tree for a basic '
                                  'enumeration')

    def get_genf(self, **kwargs):
        if self.tiling.is_epsilon():
            return sympy.sympify('1')
        elif self.tiling.is_point_tiling():
            return sympy.sympify('x')
        raise InvalidOperationError('Not an atom')

    def verified(self):
        return self.tiling.is_epsilon() or self.tiling.is_point_tiling()


class LocallyFactorableEnumeration(Enumeration):
    """
    Enumeration strategy for a locally factorable tiling.

    A tiling is locally factorable if all its obstructions and requirements are
    locally factorable, i.e. each obstruction or requirement use at most one
    cell on each row and column.

    A locally factorable tiling can be describe with a tree with only subset
    verified tiling.
    """

    def __init__(self, tiling, basis):
        super().__init__(tiling)
        # TODO: The basis attribute is unused
        self.basis = basis

    pack = StrategyPack(
        name="LocallyFactorable",
        initial_strats=[factor, requirement_corroboration],
        inferral_strats=[],
        expansion_strats=[all_factor_insertions],
        ver_strats=[subset_verified]
    )

    formal_step = "Tiling is locally factorable"

    def _possible_tautology(self):
        """
        Return True if possibly equivalent to a 1x1 tiling through empty
        cell inferral. It just checks if two cells are non-empty.
        """
        if len(self.tiling.positive_cells) > 1:
            return False
        cells = set()
        maxlen = max(self.tiling.maximum_length_of_minimum_gridded_perm(), 1) + 1
        for gp in tiling.gridded_perms(maxlen=maxlen):
            cells.update(gp.pos)
            if len(cells) > 1:
                return False
        return True

    def _locally_factorable_obstructions(self):
        """
        Check if all the obstructions of the tiling are locally factorable.
        """
        return all(not ob.is_interleaving()
                   for ob in self.tiling.obstructions)

    def _locally_factorable_requirements(self):
        """
        Check if all the requirements of the tiling are locally factorable.
        """
        reqs = chain.from_iterable(tilings.requirements)
        return all(not r.is_interleaving() for r in reqs)

    def verified(self):
        return (not self.tiling.dimensions == (1, 1) and
                self._locally_factorable_obstructions() and
                self._locally_factorable_requirements() and
                not self._possible_tautology())

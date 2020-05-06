import abc
from collections import deque
from itertools import chain
from typing import TYPE_CHECKING, FrozenSet, Iterable

import requests
import sympy

from comb_spec_searcher import ProofTree, StrategyPack
from comb_spec_searcher.utils import taylor_expand
from permuta import Perm
from permuta.permutils.symmetry import all_symmetry_sets
from tilings.exception import InvalidOperationError
from tilings.misc import is_tree

if TYPE_CHECKING:
    from tilings import Tiling

x = sympy.Symbol("x")


class Enumeration(abc.ABC):
    """
    General representation of a strategy to enumerate tilings.
    """

    def __init__(self, tiling: "Tiling"):
        self.tiling = tiling

    @abc.abstractproperty
    def pack(self) -> StrategyPack:
        """
        Returns a TileScope pack that fines a proof tree for the tilings in
        which the verification strategy used are "simpler".

        The pack is assumed to produce a finite universe.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def verified(self) -> bool:
        """
        Returns True if enumeration strategy works for the tiling.
        """
        raise NotImplementedError

    @abc.abstractproperty
    def formal_step(self) -> str:
        """
        Return a string that describe the verification strategy.
        """
        raise NotImplementedError

    def get_tree(self, **kwargs) -> ProofTree:
        """
        Returns a tree for the tilings. Raises an `InvalidOperationError` if no
        tree can be found.

        All the kwargs are past to the `auto_search` method of the TileScope
        instance that search for the tree.

        Raises an InvalidOperationError if the tiling is not verified.
        """
        if not self.verified():
            raise InvalidOperationError("The tiling is not verified")
        # searcher = TileScopeTHREE(self.tiling, self.pack)
        # tree = searcher.auto_search(**kwargs)
        # if tree is None:
        #     raise InvalidOperationError('Cannot find a tree')
        # return tree

    def get_genf(self, **kwargs):
        """
        Returns the generating function for the tiling.

        All the kwargs are passed to `self.get_tree`.

        Raises an InvalidOperationError if the tiling is not verified.
        """
        if not self.verified():
            raise InvalidOperationError("The tiling is not verified")
        return self.get_tree(**kwargs).get_genf()

    def __repr__(self) -> str:
        return "Enumeration for:\n" + str(self.tiling)


class BasicEnumeration(Enumeration):

    formal_step = "Base cases"

    @property
    def pack(self):
        raise InvalidOperationError("Cannot get a tree for a basic " "enumeration")

    def get_tree(self, **kwargs):
        raise InvalidOperationError("Cannot get a tree for a basic " "enumeration")

    def get_genf(self, **kwargs):
        if self.tiling.is_epsilon():
            return sympy.sympify("1")
        if self.tiling.is_point_tiling():
            return x
        if self.tiling.is_point_or_empty():
            return x + 1
        raise InvalidOperationError("Not an atom")

    def verified(self):
        return (
            self.tiling.is_epsilon()
            or self.tiling.is_point_tiling()
            or self.tiling.is_point_or_empty()
        )


class LocallyFactorableEnumeration(Enumeration):
    """
    Enumeration strategy for a locally factorable tiling.

    A tiling is locally factorable if all its obstructions and requirements are
    locally factorable, i.e. each obstruction or requirement use at most one
    cell on each row and column. To be locally factorable, a tiling
    should not be equivalent to a 1x1 tiling.

    A locally factorable tiling can be describe with a tree with only subset
    verified tiling.
    """

    # pack = StrategyPack(
    #     name="LocallyFactorable",
    #     initial_strats=[factor, requirement_corroboration],
    #     inferral_strats=[],
    #     expansion_strats=[all_factor_insertions],
    #     ver_strats=[subset_verified]
    # )
    @property
    def pack(self):
        raise NotImplementedError

    formal_step = "Tiling is locally factorable"

    def _locally_factorable_obstructions(self):
        """
        Check if all the obstructions of the tiling are locally factorable.
        """
        return all(not ob.is_interleaving() for ob in self.tiling.obstructions)

    def _locally_factorable_requirements(self):
        """
        Check if all the requirements of the tiling are locally factorable.
        """
        reqs = chain.from_iterable(self.tiling.requirements)
        return all(not r.is_interleaving() for r in reqs)

    def verified(self):
        return (
            not self.tiling.dimensions == (1, 1)
            and self._locally_factorable_obstructions()
            and self._locally_factorable_requirements()
        )


class LocalEnumeration(Enumeration):
    """
    Enumeration strategy for a locally enumerable tiling.

    A tiling is locally enumerable if the tiling has no crossing obstructions
    or requirements. To be locally enumerable, a tiling also should not be
    equivalent to a 1x1 tiling.


    There's not universal way of describing a tiling that is locally enumerable
    with a tree.
    """

    def __init__(self, tiling, no_req=False):
        super().__init__(tiling)
        self.no_req = no_req

    pack = None

    formal_step = "Tiling is locally enumerable"

    def get_tree(self, **kwargs):
        if not self.verified():
            raise InvalidOperationError("The tiling is not verified")
        error = (
            "There is no known way of getting the tree for a locally "
            "enumerable tiling in general"
        )
        raise NotImplementedError(error)

    def get_genf(self, **kwargs):
        if not self.verified():
            raise InvalidOperationError("The tiling is not verified")
        error = (
            "There is no known way of getting the generating function "
            "for a locally enumerable tiling in general"
        )
        raise NotImplementedError(error)

    def verified(self):
        if self.no_req and self.tiling.requirements:
            return False
        if self.tiling.dimensions == (1, 1):
            return False
        obs = self.tiling.obstructions
        reqs = chain.from_iterable(self.tiling.requirements)
        all_gp = chain(obs, reqs)
        return all(gp.is_single_cell() for gp in all_gp)


class MonotoneTreeEnumeration(Enumeration):
    """
    Enumeration strategy for a monotone tree tiling.

    A tiling is a monotone tree if it is local, its cell graph is a tree and
    all but possibly one cell are monotone.

    A monotone tree tiling can be described by a tree where the verified object
    are the cells of the tiling.
    """

    @property
    def pack(self):
        raise NotImplementedError

    formal_step = "Tiling is a monotone tree"
    _tracking_var = sympy.var("t")

    def verified(self):
        local_verified = LocalEnumeration(self.tiling).verified()
        no_req_list = all(len(rl) == 1 for rl in self.tiling.requirements)
        num_non_monotone = sum(
            1 for c in self.tiling.active_cells if not self.tiling.is_monotone_cell(c)
        )
        return (
            local_verified
            and no_req_list
            and num_non_monotone <= 1
            and is_tree(self.tiling.active_cells, self.tiling.cell_graph())
        )

    def _cell_tree_traversal(self, start):
        """
        Traverse the tree by starting at `start` and always visiting an entire
        row or column before going somewhere else.

        The start vertices is not yielded.
        """
        queue = deque(
            chain(
                self.tiling.cells_in_col(start[1]), self.tiling.cells_in_row(start[0])
            )
        )
        visited = set([start])
        while queue:
            cell = queue.popleft()
            if cell not in visited:
                yield cell
                visited.add(cell)
                queue.extend(self.tiling.cells_in_row(cell[1]))
                queue.extend(self.tiling.cells_in_col(cell[0]))

    def _visted_cells_aligned(self, cell, visited):
        """
        Return the cells that are in visited and in the same row or column as
        `cell`.
        """
        row_cells = self.tiling.cells_in_row(cell[1])
        col_cells = self.tiling.cells_in_col(cell[0])
        return (c for c in visited if (c in row_cells or c in col_cells))

    def get_genf(self, **kwargs):
        if not self.verified():
            raise InvalidOperationError("The tiling is not verified")
        try:
            start = next(
                c
                for c in self.tiling.active_cells
                if not self.tiling.is_monotone_cell(c)
            )
        except StopIteration:
            start = next(iter(self.tiling.active_cells))
        start_basis = self.tiling.cell_basis()[start][0]
        start_reqs = [[p] for p in self.tiling.cell_basis()[start][1]]
        start_tiling = self.tiling.from_perms(
            obstructions=start_basis, requirements=start_reqs
        )
        start_gf = start_tiling.get_genf()
        F = start_gf.subs({x: x * self._cell_variable(start)})
        visited = set([start])
        for cell in self._cell_tree_traversal(start):
            interleaving_cells = self._visted_cells_aligned(cell, visited)
            substitutions = {
                scv: scv * self._tracking_var
                for scv in map(self._cell_variable, interleaving_cells)
            }
            F_tracked = F.subs(substitutions)
            minlen, maxlen = self._cell_num_point(cell)
            if maxlen is None:
                F = self._interleave_any_length(F_tracked, cell)
                if minlen > 0:
                    F -= self._interleave_fixed_lengths(F_tracked, cell, 0, minlen - 1)
            else:
                F = self._interleave_fixed_lengths(F_tracked, cell, minlen, maxlen)
            visited.add(cell)
        F = sympy.simplify(F.subs({v: 1 for v in F.free_symbols if v != x}))
        # A simple test to warn us if the code is wrong
        assert taylor_expand(F) == [
            len(list(self.tiling.objects_of_size(i))) for i in range(11)
        ], "Bad genf"
        return F

    @staticmethod
    def _cell_variable(cell):
        """
        Return the appropriate variable to track the number of point in the
        given cell.
        """
        return sympy.var("y_{}_{}".format(*cell))

    def _interleave_any_length(self, F, cell):
        """
        Return the generating function for interleaving any number of point of
        a monotone sequence into the region tracked by
        `MonotoneTreeEnumeration._tracking_var` in `F`.
        A variable is added to track the number of point in cell.
        """
        cell_var = self._cell_variable(cell)
        gap_filler = 1 / (1 - x * cell_var)
        return F.subs({self._tracking_var: gap_filler}) * gap_filler

    def _interleave_fixed_lengths(self, F, cell, min_length, max_length):
        """
        Return the generating function for interleaving between min_point and
        max_point (both included) number of point of
        a monotone sequence into the region tracked by
        `MonotoneTreeEnumeration._tracking_var` in `F`.
        A variable is added to track the number of point in cell.
        """
        return sum(
            self._interleave_fixed_length(F, cell, i)
            for i in range(min_length, max_length + 1)
        )

    def _interleave_fixed_length(self, F, cell, num_point):
        """
        Return the generating function for interleaving num_point
        number of point of a monotone sequence into the region tracked by
        `MonotoneTreeEnumeration._tracking_var` in `F`.
        A variable is added to track the number of point in cell.
        """
        new_genf = self._tracking_var ** num_point * F
        for i in range(1, num_point + 1):
            new_genf = sympy.diff(new_genf, self._tracking_var) / i
        new_genf *= self._cell_variable(cell) ** num_point
        new_genf *= x ** num_point
        return new_genf.subs({self._tracking_var: 1})

    def _cell_num_point(self, cell):
        """
        Return a pair of integer `(min, max)` that describe the possible
        number of point in the cell. If the number of point is unbounded,
        `max` is None.

        We assume that the cell is monotone
        """
        obs, reqs = self.tiling.cell_basis()[cell]
        ob_lens = sorted(map(len, obs))
        assert ob_lens[0] == 2, "Unexpected obstruction"
        assert len(reqs) <= 1, "Unexpected number of requirement"
        if len(obs) == 1:
            maxlen = None
        elif len(obs) == 2:
            maxlen = ob_lens[1] - 1
        else:
            raise RuntimeError("Unexpected number of obstructions")
        if not reqs:
            minlen = 0
        elif len(reqs) == 1:
            minlen = len(reqs[0])
        else:
            raise RuntimeError("Unexpected number of requirements")
        return minlen, maxlen


class ElementaryEnumeration(Enumeration):
    """
    Enumeration strategy for a elementary tiling.

    A tiling is elementary if each active cell is on its own row and column.
    To be elementary, a tiling should not be equivalent to a 1x1
    tiling.

    By definition an elementary tiling is locally factorable.

    A elementary tiling can be describe with a tree with only one by one
    verified tiling.
    """

    # pack = StrategyPack(
    #     name="LocallyFactorable",
    #     initial_strats=[factor, requirement_corroboration],
    #     inferral_strats=[],
    #     expansion_strats=[all_factor_insertions],
    #     ver_strats=[subset_verified]
    # )
    @property
    def pack(self):
        raise NotImplementedError

    formal_step = "Tiling is elementary"

    def verified(self):
        return self.tiling.fully_isolated() and not self.tiling.dimensions == (1, 1)


class DatabaseEnumeration(Enumeration):
    """
    Enumeration strategy for a tilings that are in the database.

    There is not always a tree for a tiling in the database but you can always
    find the generating function and the minimal polynomial in the database.
    """

    API_ROOT_URL = "https://api.combopal.ru.is/"
    all_verified_tilings: FrozenSet[bytes] = frozenset()
    num_verified_request = 0

    @classmethod
    def load_verified_tiling(cls):
        """
        Load all the verified tiling in the attribute `all_verified_tilings` of
        the class.

        That speeds up the verification test.
        """
        if not DatabaseEnumeration.all_verified_tilings:
            uri = cls.API_ROOT_URL + "all_verified_tilings"
            response = requests.get(uri)
            response.raise_for_status()
            compressed_tilings = map(bytes.fromhex, response.json())
            cls.all_verified_tilings = frozenset(compressed_tilings)

    def _get_tiling_entry(self):
        """
        Retrieve the tiling entry from the database. Returns None if the tiling
        is not in the database.
        """
        key = self.tiling.to_bytes().hex()
        search_url = DatabaseEnumeration.API_ROOT_URL + "verified_tiling/key/{}".format(
            key
        )
        r = requests.get(search_url)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    def verified(self):
        """
        Check if a tiling is verified.

        After a 100 checks it loads all the saved tiling from the database to
        speed up future requests.
        """
        DatabaseEnumeration.num_verified_request += 1
        if DatabaseEnumeration.all_verified_tilings:
            return self.tiling.to_bytes() in DatabaseEnumeration.all_verified_tilings
        if DatabaseEnumeration.num_verified_request > 100:
            DatabaseEnumeration.load_verified_tiling()
        return self._get_tiling_entry() is not None

    formal_step = "Tiling is in the database"

    @property
    def pack(self):
        raise NotImplementedError("No standard pack for a database verified " "tiling.")

    def get_tree(self, **kwargs):
        if not self.verified():
            raise InvalidOperationError("The tiling is not verified")
        raise NotImplementedError(
            "No standard way of getting a tree for a " "tiling in the database."
        )

    def get_genf(self, **kwargs):
        if not self.verified():
            raise InvalidOperationError("The tiling is not verified")
        return sympy.sympify(self._get_tiling_entry()["genf"])


class OneByOneEnumeration(Enumeration):
    """
    Enumeration a tiling that consist of a single cell and is a subclass of the
    basis.
    """

    def __init__(self, tiling, basis: Iterable[Perm] = None, symmetry: bool = False):
        if basis is not None:
            assert all(
                isinstance(p, Perm) for p in basis
            ), "Element of the basis must be Perm"
            if symmetry:
                self.symmetries = set(frozenset(b) for b in all_symmetry_sets(basis))
            else:
                self.symmetries = set([frozenset(basis)])
        else:
            self.symmetries = set()
        super().__init__(tiling)

    formal_step = "This tiling is a subclass of the original tiling."

    @property
    def pack(self):
        """
        Make it return all the strategies
        """
        raise NotImplementedError

    def verified(self):
        if not self.tiling.dimensions == (1, 1):
            return False
        return (
            frozenset(ob.patt for ob in self.tiling.obstructions) not in self.symmetries
        )

    def get_genf(self, **kwargs):
        """
        TODO: This function should:
            - check if the basis is in the database
            - try to run tilescope on the tiling
        """
        # pylint: disable=useless-super-delegation
        return super().get_genf(**kwargs)

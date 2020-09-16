import abc
from collections import deque
from itertools import chain
from typing import TYPE_CHECKING, Dict, FrozenSet, Iterable, Optional

import requests
from sympy import Expr, Function, Symbol, diff, simplify, sympify, var

from comb_spec_searcher.utils import taylor_expand
from tilings.exception import InvalidOperationError
from tilings.griddedperm import GriddedPerm
from tilings.misc import is_tree

if TYPE_CHECKING:
    from tilings import Tiling

x = Symbol("x")


class Enumeration(abc.ABC):
    """
    General representation of a strategy to enumerate tilings.
    """

    def __init__(self, tiling: "Tiling"):
        self.tiling = tiling

    @abc.abstractmethod
    def verified(self) -> bool:
        """
        Returns True if enumeration strategy works for the tiling.
        """
        raise NotImplementedError

    def get_genf(self, **kwargs) -> Expr:
        """
        Returns the generating function for the tiling.

        Raises an InvalidOperationError if the tiling is not verified.
        """
        if not self.verified():
            raise InvalidOperationError("The tiling is not verified")

    def __repr__(self) -> str:
        return "Enumeration for:\n" + str(self.tiling)


class LocalEnumeration(Enumeration):
    """
    Enumeration strategy for a locally enumerable tiling.

    A tiling is locally enumerable if the tiling has no crossing obstructions
    or requirements.

    There's not universal way of describing a tiling that is locally enumerable
    with a specification.
    """

    def __init__(self, tiling, no_req=False):
        super().__init__(tiling)
        self.no_req = no_req

    def verified(self) -> bool:
        if self.no_req and self.tiling.requirements:
            return False
        return (
            all(gp.is_single_cell() for gp in self.tiling.obstructions)
            and all(self._req_is_single_cell(req) for req in self.tiling.requirements)
            and all(
                gp.is_single_cell()
                for gp in chain.from_iterable(
                    ass.gps for ass in self.tiling.assumptions
                )
            )
        )

    @staticmethod
    def _req_is_single_cell(req: Iterable[GriddedPerm]) -> bool:
        """
        Returns True if all the gridded perm in the iterable are single cell and in
        the same cell.
        """
        req_iter = iter(req)
        gp0 = next(req_iter)
        if not gp0.is_single_cell():
            return False
        cell = gp0.pos[0]
        all_cells = chain.from_iterable(gp.pos for gp in req_iter)
        return all(c == cell for c in all_cells)

    def get_genf(self, **kwargs) -> Expr:
        # pylint: disable=too-many-return-statements
        if not self.verified():
            raise InvalidOperationError("The tiling is not verified")

        funcs: Optional[Dict["Tiling", Function]] = kwargs.get("funcs")
        if funcs is None:
            funcs = dict()
        if self.tiling.requirements:
            reqs = self.tiling.requirements[0]
            avoided = self.tiling.__class__(
                self.tiling.obstructions + reqs,
                self.tiling.requirements[1:],
                self.tiling.assumptions,
            )
            without = self.tiling.__class__(
                self.tiling.obstructions,
                self.tiling.requirements[1:],
                self.tiling.assumptions,
            )
            avgf = LocalEnumeration(avoided).get_genf(funcs=funcs)
            wogf = LocalEnumeration(without).get_genf(funcs=funcs)
            return wogf - avgf
        if self.tiling in funcs:
            return funcs[self.tiling]
        # also return something entirely different if the root class/not verified
        if self.tiling.dimensions == (1, 1):
            if self.tiling.is_epsilon():
                return 1
            if self.tiling == self.tiling.__class__.from_string("01_10"):
                return 1 + x
            if self.tiling in (
                self.tiling.__class__.from_string("01"),
                self.tiling.__class__.from_string("10"),
            ):
                return 1 / (1 - x)
            if self.tiling in (
                self.tiling.__class__.from_string("123"),
                self.tiling.__class__.from_string("321"),
            ):
                return sympify("-1/2*(sqrt(-4*x + 1) - 1)/x")
            # TODO: should this create a spec as in the strategy?
            raise NotImplementedError(
                f"Look up the combopal database for:\n{self.tiling}"
            )
        gf = None
        if MonotoneTreeEnumeration(self.tiling).verified():
            gf = MonotoneTreeEnumeration(self.tiling).get_genf()
        if DatabaseEnumeration(self.tiling).verified():
            gf = DatabaseEnumeration(self.tiling).get_genf()
        if gf is not None:
            funcs[self.tiling] = gf
            return gf
        # TODO: should this create a spec as in the strategy?
        raise NotImplementedError(
            "Not sure how to enumerate the tiling:\n{}".format(self.tiling)
        )


class MonotoneTreeEnumeration(Enumeration):
    """
    Enumeration strategy for a monotone tree tiling.

    A tiling is a monotone tree if it is local, its cell graph is a tree and
    all but possibly one cell are monotone.

    A monotone tree tiling can be described by a tree where the verified object
    are the cells of the tiling.
    """

    _tracking_var = var("t")

    def verified(self):
        no_req_list = all(len(rl) == 1 for rl in self.tiling.requirements)
        num_non_monotone = sum(
            1 for c in self.tiling.active_cells if not self.tiling.is_monotone_cell(c)
        )
        return (
            self.tiling.dimensions != (1, 1)
            and LocalEnumeration(self.tiling).verified()
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
                self.tiling.cells_in_col(start[0]), self.tiling.cells_in_row(start[1])
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

    def get_genf(self, **kwargs) -> Expr:
        # pylint: disable=too-many-locals
        if not self.verified():
            raise InvalidOperationError("The tiling is not verified")
        if self.tiling.extra_parameters:
            raise NotImplementedError(
                "Not implemented monotone verified with extra parameters."
            )
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
        F = simplify(F.subs({v: 1 for v in F.free_symbols if v != x}))
        # A simple test to warn us if the code is wrong
        if __debug__:
            lhs = taylor_expand(F, n=6)
            rhs = [len(list(self.tiling.objects_of_size(i))) for i in range(7)]
        assert lhs == rhs, f"Bad genf\n{lhs}\n{rhs}"
        return F

    @staticmethod
    def _cell_variable(cell):
        """
        Return the appropriate variable to track the number of point in the
        given cell.
        """
        return var("y_{}_{}".format(*cell))

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
            new_genf = diff(new_genf, self._tracking_var) / i
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


class DatabaseEnumeration(Enumeration):
    """
    Enumeration strategy for a tilings that are in the database.

    There is not always a specification for a tiling in the database but you can always
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
        if DatabaseEnumeration.num_verified_request > 10:
            DatabaseEnumeration.load_verified_tiling()
        return self._get_tiling_entry() is not None

    def get_genf(self, **kwargs) -> Expr:
        if not self.verified():
            raise InvalidOperationError("The tiling is not verified")
        return sympify(self._get_tiling_entry()["genf"])

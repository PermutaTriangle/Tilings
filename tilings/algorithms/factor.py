from collections import defaultdict
from itertools import chain, combinations

from comb_spec_searcher import Rule
from permuta.misc import UnionFind
from tilings.misc import partitions_iterator


class Factor():
    """
    Algorithm to compute the factorisation of a tiling.

    Two active cells are in the same factor if they are in the same row
    or column, or they share an obstruction or a requirement.
    """

    def __init__(self, tiling):
        self._tiling = tiling
        self._active_cells = tiling.active_cells
        nrow = tiling.dimensions[1]
        ncol = tiling.dimensions[0]
        self._cell_unionfind = UnionFind(nrow * ncol)
        self._components = None
        self._factors_obs_and_reqs = None

    def _cell_to_int(self, cell):
        nrow = self._tiling.dimensions[1]
        return cell[0] * nrow + cell[1]

    def _int_to_cell(self, i):
        nrow = self._tiling.dimensions[1]
        return (i // nrow, i % nrow)

    def _get_cell_representative(self, cell):
        """
        Return the representative of a cell in the union find.
        """
        i = self._cell_to_int(cell)
        return self._cell_unionfind.find(i)

    def _unite_cells(self, cells):
        """
        Put all the cells of `cells` in the same component of the UnionFind.
        """
        cell_iterator = iter(cells)
        c1 = next(cell_iterator)
        c1_int = self._cell_to_int(c1)
        for c2 in cell_iterator:
            c2_int = self._cell_to_int(c2)
            self._cell_unionfind.unite(c1_int, c2_int)

    def _unite_obstructions(self):
        """
        For each obstruction unite all the position of the obstruction.
        """
        for ob in self._tiling.obstructions:
            self._unite_cells(ob.pos)

    def _unite_requirements(self):
        """
        For each requirement unite all the cell in all the requirements of the
        list.
        """
        for req_list in self._tiling.requirements:
            req_cells = chain.from_iterable(req.pos for req in req_list)
            self._unite_cells(req_cells)

    @staticmethod
    def _same_row_or_col(cell1, cell2):
        """
        Test if `cell1` and `cell2` or in the same row or columns
        """
        return cell1[0] == cell2[0] or cell1[1] == cell2[1]

    def _unite_rows_and_cols(self):
        """
        Unite all the active cell that are on the same row or column.
        """
        cell_pair_to_unite = (c for c in combinations(self._active_cells, r=2)
                              if self._same_row_or_col(c[0], c[1]))
        for c1, c2 in cell_pair_to_unite:
            self._unite_cells((c1, c2))

    def _unite_all(self):
        """
        Unite all the cells that share an obstruction, a requirement list,
        a row or a column.
        """
        self._unite_obstructions()
        self._unite_requirements()
        self._unite_rows_and_cols()

    def _get_components(self):
        """
        Returns the tuple of all the components. Each component is set of
        cells.
        """
        if self._components is not None:
            return self._components
        self._unite_all()
        all_components = defaultdict(set)
        for cell in self._active_cells:
            rep = self._get_cell_representative(cell)
            all_components[rep].add(cell)
        self._components = tuple(all_components.values())
        return self._components

    def _get_factors_obs_and_reqs(self):
        """
        Returns a list of all the irreducible factors of the tiling.
        Each factor is a tuple (obstructions, requirements)
        """
        if self._factors_obs_and_reqs is not None:
            return self._factors_obs_and_reqs
        factors = []
        for component in self._get_components():
            obstructions = tuple(ob for ob in self._tiling.obstructions
                                 if ob.pos[0] in component)
            requirements = tuple(req for req in self._tiling.requirements
                                 if req[0].pos[0] in component)
            factors.append((obstructions, requirements))
        self._factors_obs_and_reqs = factors
        return self._factors_obs_and_reqs

    def factorable(self):
        """
        Returns `True` if the tiling has more than one factor.
        """
        return len(self._get_components()) > 1

    def factors(self):
        """
        Returns all the irreducible factors of the tiling.
        """
        return [self._tiling.__class__(obstructions=f[0], requirements=f[1],
                                       minimize=False)
                for f in self._get_factors_obs_and_reqs()]

    def reducible_factorisations(self):
        """
        Iterator over all reducible factorisation that can be obtained by
        grouping of irreducible factors.

        Each factorisation is a list of tiling.

        For example if T = T1 x T2 x T3 then (T1 x T3) x T2 is a possible
        reducible factorisation.
        """
        min_comp = self._get_factors_obs_and_reqs()
        for partition in partitions_iterator(min_comp):
            factors = []
            for part in partition:
                obstructions, requirements = zip(*part)
                factors.append(self._tiling.__class__(
                    obstructions=chain(*obstructions),
                    requirements=chain(*requirements),
                    minimize=False)
                )
            yield factors

    @staticmethod
    def formal_step(union=False):
        """
        Return a string that describe the operation performed on the tiling.
        """
        union_str = 'unions of ' if union else ''
        return 'The {}factors of the tiling.'.format(union_str)

    @property
    def constructor(self):
        """
        Returns the type of constructor for the factorisation
        """
        return 'cartesian'

    def _rule(self, factors, formal_step, workable):
        """
        Return the comb_spec_searcher rule for the factorisation where the list
        of factors is given as a list of tilings.

        If workable=True,  then we expand the  children, and want to  ignore
        the parent. If workable=False, then we do  not expand the children,
        and want to keep working on the parent (perhaps placing points into
        cells or something).
        """
        if not self.factorable():
            return
        assert isinstance(workable, bool)
        return Rule(formal_step,
                    factors,
                    inferable=[False for _ in factors],
                    workable=[workable for _ in factors],
                    possibly_empty=[False for _ in factors],
                    ignore_parent=workable,
                    constructor=self.constructor)

    def rule(self, workable=True):
        """
        Return the comb_spec_searcher rule for the irreducible factorisation.

        If workable=True,  then we expand the  children, and want to  ignore
        the parent. If workable=False, then we do  not expand the children,
        and want to keep working on the parent (perhaps placing points into
        cells or something).
        """
        return self._rule(self.factors(), self.formal_step(), workable)

    def all_union_rules(self, workable=False):
        """
        Iterator over the rule for all possible union of factors.

        A rule is yielded for each reducible factorisations

        If workable=True,  then we expand the  children, and want to  ignore
        the parent. If workable=False, then we do  not expand the children,
        and want to keep working on the parent (perhaps placing points into
        cells or something).
        """
        for factorisation in self.reducible_factorisations():
            yield self._rule(
                factorisation,
                self.formal_step(union=True),
                workable=workable
            )


class FactorWithMonotoneInterleaving(Factor):
    """
    Algorithm to compute the factorisation with monotone interleaving of a
    tiling.

    Two active cells are in the same factor if they share an obstruction or
    a requirement or if they are on the same row or column and are both
    non-monotone.
    """

    def _unite_rows_and_cols(self):
        """
        Unite all active cell that are on the same row or column if both of
        them are not monotone.

        Override `Factor._unite_rows_and_cols`.
        """
        cell_pair_to_unite = (c for c in combinations(self._active_cells, r=2)
                              if (self._same_row_or_col(c[0], c[1]) and
                                  not self._tiling.is_monotone_cell(c[0]) and
                                  not self._tiling.is_monotone_cell(c[1])))
        for c1, c2 in cell_pair_to_unite:
            self._unite_cells((c1, c2))

    def formal_step(self, union=False):
        """
        Return a string that describe the operation performed on the tiling.
        """
        union_str = 'unions of ' if union else ''
        return ("The {}factors with monotone interleaving of the "
                "tiling.".format(union_str))

    @property
    def constructor(self):
        """
        Returns the type of constructor for the factorisation
        """
        return 'other'


class FactorWithInterleaving(Factor):
    """
    Algorithm to compute the factorisation with interleaving of a tiling.

    Two non-empty cells are in the same factor if they share an obstruction or
    a requirement.
    """

    def _unite_rows_and_cols(self):
        """
        Override the `Factor._unite_rows_and_cols` to do nothing since
        interleaving is allowed on row and column.
        """

    def _unite_all(self):
        """
        Unite all the cells that share an obstruction or a requirement list.
        """
        self._unite_obstructions()
        self._unite_requirements()

    def formal_step(self, union=False):
        """
        Return a string that describe the operation performed on the tiling.
        """
        union_str = 'unions of ' if union else ''
        return ("The {}factors with interleaving of the "
                "tiling.".format(union_str))

    @property
    def constructor(self):
        """
        Returns the type of constructor for the factorisation
        """
        return 'other'

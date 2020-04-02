from collections import defaultdict
from itertools import chain, product

from comb_spec_searcher import InferralRule
from permuta import Perm
from tilings import Obstruction


class ObstructionTransitivity:
    """
    The obstruction transitivity algorithm.

    The obstruction transitivity considers all length 2 obstructions with both
    points in the same row or same column. By considering these length 2
    obstructions in similar manner as the row and column separation, as
    inequality relations. When the obstructions use a positive cell,
    transitivity applies, i.e. if a < b < c and b is positive, then a < c.
    """

    def __init__(self, tiling):
        self._tiling = tiling
        self._colineq = None
        self._rowineq = None
        self._positive_cells_col = None
        self._positive_cells_row = None
        self._new_ineq = None

    def positive_cells_col(self, col_index):
        """
        Return the row index of all positive cells in the columns.

        OUTPUT:

            List of integers.
        """
        if self._positive_cells_col is None:
            self._init_positive_cells()
        return self._positive_cells_col[col_index]

    def positive_cells_row(self, row_index):
        """
        Return the column index of all positive cells in the row.

        OUTPUT:

            List of integers.
        Return a dictionary of positive cells for each column.
        """
        if self._positive_cells_row is None:
            self._init_positive_cells()
        return self._positive_cells_row[row_index]

    def ineq_col(self, col_index):
        """
        Returns a set of inequalities in the specified column.

        An inequality is a tuple of integer (r1, r2) such that r1 < r2.
        """
        if self._colineq is None:
            self._init_ineq()
        return self._colineq[col_index]

    def ineq_row(self, row_index):
        """
        Returns a set of inequalities in the specified row.

        An inequality is a tuple of integer (c1, c2) such that c1 < c2.
        """
        if self._rowineq is None:
            self._init_ineq()
        return self._rowineq[row_index]

    def _init_positive_cells(self):
        """
        Fill the dictionary of positive cells by rows and columns.
        """
        self._positive_cells_row = defaultdict(list)
        self._positive_cells_col = defaultdict(list)
        for cell in self._tiling.positive_cells:
            self._positive_cells_col[cell[0]].append(cell[1])
            self._positive_cells_row[cell[1]].append(cell[0])

    def _init_ineq(self):
        """
        Fill the dictionary of row and column inequalities.
        """
        self._colineq = defaultdict(set)
        self._rowineq = defaultdict(set)
        len2_obs = (ob for ob in self._tiling.obstructions if len(ob) == 2)
        ineq_obs = (ob for ob in len2_obs if not ob.is_localized())
        for ob in ineq_obs:
            leftcol, rightcol = ob.pos[0][0], ob.pos[1][0]
            leftrow, rightrow = ob.pos[0][1], ob.pos[1][1]
            # In same column
            if leftcol == rightcol:
                self._colineq[leftcol].add((rightrow, leftrow))
            # In same row
            elif ob.pos[0][1] == ob.pos[1][1]:
                if ob.patt == Perm((0, 1)):
                    self._rowineq[leftrow].add((rightcol, leftcol))
                else:
                    self._rowineq[leftrow].add((leftcol, rightcol))

    @staticmethod
    def ineq_ob(ineq):
        """
        Given an inequality of cells compute an obstruction.

        The inequalities are given as tuple `(cell1, cell2)` where `cell1` is
        strictly smaller than `cell2`.
        """
        left, right = ineq
        if left == right:
            return Obstruction(Perm((0,)), (left,))
        if left[0] == right[0]:
            # same column
            if left[1] < right[1]:
                return Obstruction(Perm((1, 0)), [right, left])
            return Obstruction(Perm((0, 1)), [right, left])
        if left[1] == right[1]:
            # same row
            if left[0] < right[0]:
                return Obstruction(Perm((1, 0)), [left, right])
            return Obstruction(Perm((0, 1)), [right, left])
        raise ValueError(
            ("Can not construct an obstruction from inequality {} < {}").format(
                left, right
            )
        )

    @staticmethod
    def ineq_closure(positive_cells, ineqs):
        """
        Computes the transitive closure over positive cells.

        Given a list of inequalities and positive cells, a new set of
        inequalities is computed. For every positive cell c, when g < c < l the
        relation g < l is added if not already there.

        The list of new inequalities is returned.
        """
        gtlist = defaultdict(list)
        ltlist = defaultdict(list)
        for left, right in ineqs:
            ltlist[left].append(right)
            gtlist[right].append(left)
        to_analyse = set(positive_cells)
        ineqs = set(ineqs)
        newineqs = set()
        while to_analyse:
            cur = to_analyse.pop()
            not_existing_ineq = filter(
                lambda x: x not in ineqs, product(gtlist[cur], ltlist[cur])
            )
            for gt, lt in not_existing_ineq:
                gtlist[lt].append(gt)
                ltlist[gt].append(lt)
                ineqs.add((gt, lt))
                newineqs.add((gt, lt))
                if lt in positive_cells:
                    to_analyse.add(lt)
                if gt in positive_cells:
                    to_analyse.add(gt)
        return newineqs

    def new_ineq(self):
        """
        Compute the new inequalities.
        """
        if self._new_ineq is not None:
            return self._new_ineq
        newineqs = []
        ncol, nrow = self._tiling.dimensions
        for col in range(ncol):
            ineqs = self.ineq_col(col)
            pos_cells = self.positive_cells_col(col)
            for left, right in self.ineq_closure(pos_cells, ineqs):
                newineqs.append(((col, left), (col, right)))
        for row in range(nrow):
            ineqs = self.ineq_row(row)
            pos_cells = self.positive_cells_row(row)
            for left, right in self.ineq_closure(pos_cells, ineqs):
                newineqs.append(((left, row), (right, row)))
        self._new_ineq = newineqs
        return self._new_ineq

    def obstruction_transitivity(self):
        """
        Return the tiling with the new obstructions.
        """
        obs = chain(self._tiling.obstructions, map(self.ineq_ob, self.new_ineq()))
        return self._tiling.__class__(
            obstructions=obs, requirements=self._tiling.requirements
        )

    def rule(self):
        """
        Return a comb_spec_searcher Rule for the obstruction transitivity.

        If no new obstruction is added return None.
        """
        if not self.new_ineq():
            return None
        return InferralRule(
            "Computing transitivity of inequalities.", self.obstruction_transitivity()
        )

    def __str__(self):
        s = "ObstructionTransitivity object for the tiling:\n"
        s += self._tiling.__str__()
        return s

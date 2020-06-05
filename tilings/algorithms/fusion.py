"""
The implementation of the fusion algorithm

# TODO: this file needs to be type checked!
"""
from collections import Counter
from itertools import chain
from typing import TYPE_CHECKING

from permuta import Perm
from tilings.assumptions import TrackingAssumption
from tilings.griddedperm import GriddedPerm

if TYPE_CHECKING:
    from tilings import Tiling


class Fusion:
    """
    Fusion algorithm container class.

    Check if a fusion is valid and compute the fused tiling.

    If `row_idx` is provided it attempts to fuse row `row_idx` with row
    `row_idx+1`.

    If incited `col_ids` is provided it attempts to fuse column `col_idx` with
    column `col_idx+1`.
    """

    def __init__(self, tiling, row_idx=None, col_idx=None, tracked: bool = False):
        self._tiling: "Tiling" = tiling
        self._assumptions_fuse_counters = None
        self._obstruction_fuse_counter = None
        self._requirements_fuse_counters = None
        self._tracked = tracked  # add a TrackingAssumption to the region being tracked.
        if row_idx is None and col_idx is not None:
            self._col_idx = col_idx
            self._fuse_row = False
        elif col_idx is None and row_idx is not None:
            self._row_idx = row_idx
            self._fuse_row = True
        else:
            raise RuntimeError("Cannot specify a row and a columns")

    def _fuse_gridded_perm(self, gp):
        """
        Fuse the gridded permutation `gp`.
        """
        fused_pos = []
        for x, y in gp.pos:
            if self._fuse_row and y > self._row_idx:
                y -= 1
            elif not self._fuse_row and x > self._col_idx:
                x -= 1
            fused_pos.append((x, y))
        return gp.__class__(gp.patt, fused_pos)

    def _unfuse_gridded_perm(self, gp):
        """
        Generator of all the possible ways to unfuse a gridded permutations.
        """

        def stretch_above(p):
            return p if p[1] < self._row_idx else (p[0], p[1] + 1)

        def stretch_left(p):
            return p if p[0] < self._col_idx else (p[0] + 1, p[1])

        if self._fuse_row:
            stretch = stretch_above
            editable_pos_idx = [
                i for i, p in enumerate(gp.pos) if p[1] == self._row_idx
            ]
            editable_pos_idx.sort(key=lambda i: gp.patt[i])
        else:
            stretch = stretch_left
            editable_pos_idx = [
                i for i, p in enumerate(gp.pos) if p[0] == self._col_idx
            ]
            editable_pos_idx.sort()
        pos = list(map(stretch, gp.pos))
        yield gp.__class__(gp.patt, pos)
        row_shift = int(self._fuse_row)
        col_shift = 1 - int(self._fuse_row)
        for i in editable_pos_idx:
            pos[i] = (pos[i][0] - col_shift, pos[i][1] - row_shift)
            yield gp.__class__(gp.patt, pos)

    def _fuse_counter(self, gridded_perms):
        """
        Count the multiplicities of a set of gridded permutations after the
        fusion.

        Return a Counter of gridded permutations with their multiplicities.
        """
        fuse_counter = Counter()
        for gp in gridded_perms:
            fused_perm = self._fuse_gridded_perm(gp)
            fuse_counter[fused_perm] += 1
        return fuse_counter

    @property
    def obstruction_fuse_counter(self):
        """
        Counter of multiplicities of fused obstructions.
        """
        if self._obstruction_fuse_counter is not None:
            return self._obstruction_fuse_counter
        fuse_counter = self._fuse_counter(self._tiling.obstructions)
        self._obstruction_fuse_counter = fuse_counter
        return self._obstruction_fuse_counter

    @property
    def requirements_fuse_counters(self):
        """
        List of fuse counters for each of the requirements list of the tiling.
        """
        if self._requirements_fuse_counters is not None:
            return self._requirements_fuse_counters
        counters = [
            self._fuse_counter(req_list) for req_list in self._tiling.requirements
        ]
        self._requirements_fuse_counters = counters
        return self._requirements_fuse_counters

    @property
    def assumptions_fuse_counters(self):
        """
        List of fuse counters for each of the TrackedAssumptions of the tiling.
        """
        if self._assumptions_fuse_counters is not None:
            return self._assumptions_fuse_counters
        counters = [
            self._fuse_counter(assumption.gps)
            for assumption in self._tiling.assumptions
        ]
        self._assumptions_fuse_counters = counters
        return self._assumptions_fuse_counters

    def _can_fuse_set_of_gridded_perms(self, fuse_counter):
        """
        Check if a set of gridded permutations can be fused.
        """
        return all(
            self._is_valid_count(count, gp) for gp, count in fuse_counter.items()
        )

    def _is_valid_count(self, count, gp):
        """
        Check if the fuse count `count` for a given gridded permutation `gp` is
        valid.
        """
        return self._point_in_fuse_region(gp) + 1 == count

    def _point_in_fuse_region(self, fused_gp):
        """
        Return the number of point of the gridded permutation `fused_gp` in the
        fused row or column.
        """
        if self._fuse_row:
            return sum(1 for cell in fused_gp.pos if cell[1] == self._row_idx)
        return sum(1 for cell in fused_gp.pos if cell[0] == self._col_idx)

    def _can_fuse_assumption(self, assumption, fuse_counter):
        """
        Return True if an assumption can be fused. That is, prefusion, the gps
        are all contained entirely on the left of the fusion region, entirely
        on the right, or split in every possible way.
        """
        return self._can_fuse_set_of_gridded_perms(fuse_counter) or (
            all(count == 1 for gp, count in fuse_counter.items())
            and self._is_one_sided_assumption(assumption)
        )

    def _is_one_sided_assumption(self, assumption):
        """
        Return True if all of the assumption is contained either entirely on
        the left, or entirely on the right.
        """
        if self._fuse_row:
            return all(
                y != self._row_idx for gp in assumption.gps for _, y in gp.pos
            ) or all(y != self._row_idx + 1 for gp in assumption.gps for _, y in gp.pos)
        return all(
            x != self._col_idx for gp in assumption.gps for x, _ in gp.pos
        ) or all(x != self._col_idx + 1 for gp in assumption.gps for x, _ in gp.pos)

    def is_left_sided_assumption(self, assumption):
        if self._fuse_row:
            return all(
                y != self._row_idx + 1 for gp in assumption.gps for _, y in gp.pos
            )
        return all(x != self._col_idx + 1 for gp in assumption.gps for x, _ in gp.pos)

    def is_right_sided_assumption(self, assumption):
        if self._fuse_row:
            return all(y != self._row_idx for gp in assumption.gps for _, y in gp.pos)
        return all(x != self._col_idx for gp in assumption.gps for x, _ in gp.pos)

    def new_assumption(self):
        """
        Return the assumption that needs to counted in order to enumerate.
        """
        return TrackingAssumption(
            GriddedPerm.single_cell(Perm((0,)), cell)
            for cell in self._tiling.active_cells
            if (self._fuse_row and cell[1] == self._row_idx)
            or (not self._fuse_row and cell[0] == self._col_idx)
        )

    def fusable(self):
        """
        Check if the fusion is possible.
        """
        obs_fusable = self._can_fuse_set_of_gridded_perms(self.obstruction_fuse_counter)
        req_fusable = all(
            self._can_fuse_set_of_gridded_perms(counter)
            for counter in self.requirements_fuse_counters
        )
        ass_fusable = all(
            self._can_fuse_assumption(assumption, counter)
            for assumption, counter in zip(
                self._tiling.assumptions, self.assumptions_fuse_counters
            )
        )
        return obs_fusable and req_fusable and ass_fusable

    def fused_tiling(self) -> "Tiling":
        """
        Return the fused tiling.
        """
        assumptions = [
            TrackingAssumption(gps) for gps in self.assumptions_fuse_counters
        ]
        if self._tracked:
            assumptions.append(self.new_assumption())
        return self._tiling.__class__(
            obstructions=self.obstruction_fuse_counter.keys(),
            requirements=self.requirements_fuse_counters,
            assumptions=assumptions,
        )


class ComponentFusion(Fusion):
    """
    Component Fusion algorithm container class.

    Fuse tiling it it can be unfused by drawing a line between any component.

    Check if a fusion is valid and compute the fused tiling.

    If `row_idx` is provided it attempts to fuse row `row_idx` with row
    `row_idx+1`.

    If `col_idx` is provided it attempts to fuse column `col_idx` with
    column `col_idx+1`.
    """

    def __init__(self, tiling, *, row_idx=None, col_idx=None, tracked: bool = False):
        if tiling.requirements:
            raise NotImplementedError(
                "Component fusion does not handle " "requirements at the moment"
            )
        assert not tracked, "tracking not implemented for component fusion"
        super().__init__(tiling, row_idx=row_idx, col_idx=col_idx, tracked=tracked)
        self._first_cell = None
        self._second_cell = None

    def _pre_check(self):
        """
        Make a preliminary check before testing if the actual fusion is
        possible.

        Selects the two active cells to be fused. Rows or columns with more
        than one active cell cannot be fused. Sets the attribute
        `self._first_cell` and `self._second_cell`.
        """
        if self._fuse_row:
            rows = (
                self._tiling.cells_in_row(self._row_idx),
                self._tiling.cells_in_row(self._row_idx + 1),
            )
        else:
            rows = (
                self._tiling.cells_in_col(self._col_idx),
                self._tiling.cells_in_col(self._col_idx + 1),
            )
        has_a_long_row = any(len(row) > 1 for row in rows)
        if has_a_long_row:
            return False
        first_cell = next(iter(rows[0]))
        second_cell = next(iter(rows[1]))
        cells_are_adjacent = (
            first_cell[0] == second_cell[0] or first_cell[1] == second_cell[1]
        )
        if not cells_are_adjacent:
            return False
        same_basis = (
            self._tiling.cell_basis()[first_cell][0]
            == self._tiling.cell_basis()[second_cell][0]
        )
        if not same_basis:
            return False
        self._first_cell = first_cell
        self._second_cell = second_cell
        return True

    @property
    def first_cell(self):
        """
        The first cell of the fusion. This cell is in the bottommost row or the
        leftmost column of the fusion.
        """
        if self._first_cell is not None:
            return self._first_cell
        if not self._pre_check():
            raise RuntimeError(
                "Pre-check failed. No component fusion " "possible and no first cell"
            )
        return self._first_cell

    @property
    def second_cell(self):
        """
        The second cell of the fusion. This cell is in the topmost row or the
        rightmost column of the fusion.
        """
        if self._second_cell is not None:
            return self._second_cell
        if not self._pre_check():
            raise RuntimeError(
                "Pre-check failed. No component fusion " "possible and no second cell"
            )
        return self._second_cell

    def has_crossing_len2_ob(self):
        """
        Return True if the tiling contains a crossing length 2 obstruction
        between `self.first_cell` and `self.second_cell`.
        """
        fcell = self.first_cell
        scell = self.second_cell
        if self._fuse_row:
            possible_obs = [
                GriddedPerm(Perm((0, 1)), (fcell, scell)),
                GriddedPerm(Perm((1, 0)), (scell, fcell)),
            ]
        else:
            possible_obs = [
                GriddedPerm(Perm((0, 1)), (fcell, scell)),
                GriddedPerm(Perm((1, 0)), (fcell, scell)),
            ]
        return any(ob in possible_obs for ob in self._tiling.obstructions)

    def is_crossing_len2(self, gp):
        """
        Return True if the gridded permutation `gp` is a length 2 obstruction
        crossing between the first and second cell.
        """
        return (
            len(gp) == 2
            and gp.occupies(self.first_cell)
            and gp.occupies(self.second_cell)
        )

    @property
    def obstruction_fuse_counter(self):
        """
        Counter of multiplicities of fused obstructions.

        Crossing length 2 obstructions between first cell and second cell
        are ignored.
        """
        if self._obstruction_fuse_counter is not None:
            return self._obstruction_fuse_counter
        obs = (ob for ob in self._tiling.obstructions if not self.is_crossing_len2(ob))
        fuse_counter = self._fuse_counter(obs)
        self._obstruction_fuse_counter = fuse_counter
        return self._obstruction_fuse_counter

    def obstructions_to_add(self):
        """
        Iterator over all the obstructions obtained by fusing obstructions of
        the tiling and then unfusing it in all possible ways. Crossing length 2
        obstructions between first cell and second cell are not processed.
        """
        return chain.from_iterable(
            self._unfuse_gridded_perm(ob) for ob in self.obstruction_fuse_counter
        )

    def _can_fuse_set_of_gridded_perms(self, fuse_counter):
        raise NotImplementedError

    def _is_valid_count(self, count, gp):
        raise NotImplementedError

    def fusable(self):
        """
        Return True if adjacent rows can be viewed as one row where you draw a
        horizontal line through the components.
        """
        if not self._pre_check() or not self.has_crossing_len2_ob():
            return False
        new_tiling = self._tiling.add_obstructions(self.obstructions_to_add())
        return self._tiling == new_tiling

    def __str__(self):
        s = "ComponentFusion Algorithm for:\n"
        s += str(self._tiling)
        return s

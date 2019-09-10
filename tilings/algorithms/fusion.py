"""The implementation of the fusion algorithm"""
from comb_spec_searcher import Rule


class Fusion(object):
    """
    Fusion algorithm container class.

    Check if a fusion is valid and compute the fused tiling.

    If `row_idx` is provided it attempts to fuse row `row_idx` with row
    `row_idx+1`.

    If incited `col_ids` is provided it attempts to fuse column `col_idx` with
    column `col_idx+1`.
    """

    def __init__(self, tiling, row_idx=None, col_idx=None):
        self._tiling = tiling
        if row_idx is None and col_idx is not None:
            self._col_idx = col_idx
            self._fuse_row = False
        elif col_idx is None and row_idx is not None:
            self._row_idx = row_idx
            self._fuse_row = True
        else:
            raise RuntimeError('Cannot specify a row and a columns')

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
        stretch_above = (lambda p: p if p[1] < self._row_idx
                         else (p[0], p[1]+1))
        stretch_left = (lambda p: p if p[0] < self._col_idx
                        else (p[0]+1, p[1]))
        if self._fuse_row:
            stretch = stretch_above
            editable_pos_idx = [i for i, p in enumerate(gp.pos) if
                                p[1] == self._row_idx]
            editable_pos_idx.sort(key=lambda i: gp.patt[i])
        else:
            stretch = stretch_left
            editable_pos_idx = [i for i, p in enumerate(gp.pos) if
                                p[0] == self._col_idx]
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

        Return a dictionary of gridded permutations with their multiplicities.
        """
        fuse_counter = dict()
        for gp in gridded_perms:
            fused_perm = self._fuse_gridded_perm(gp)
            fuse_counter[fused_perm] = fuse_counter.get(fused_perm, 0) + 1
        return fuse_counter

    @property
    def obstruction_fuse_counter(self):
        """
        Dictionary of multiplicities of fused obstructions.
        """
        if hasattr(self, '_obstruction_fuse_counter'):
            return self._obstruction_fuse_counter
        fuse_counter = self._fuse_counter(self._tiling.obstructions)
        self._obstruction_fuse_counter = fuse_counter
        return self._obstruction_fuse_counter

    @property
    def requirements_fuse_counters(self):
        """
        List of fuse counters for each of the requirements list of the tiling.
        """
        if hasattr(self, '_requirements_fuse_counters'):
            return self._requirements_fuse_counters
        counters = [self._fuse_counter(req_list) for req_list in
                    self._tiling.requirements]
        self._requirements_fuse_counters = counters
        return self._requirements_fuse_counters

    def _can_fuse_set_of_gridded_perms(self, fuse_counter):
        """
        Check if a set of gridded permutations can be fused.
        """
        return all(self._is_valid_count(count, gp) for gp, count in
                   fuse_counter.items())

    def _is_valid_count(self, count, gp):
        """
        Check if the fuse count `count` for a given gridded permutation `gp` is
        valid.
        """
        return (self._point_in_fuse_region(gp) + 1 == count)

    def _point_in_fuse_region(self, fused_gp):
        """
        Return the number of point of the gridded permutation `fused_gp` in the
        fused row or column.
        """
        if self._fuse_row:
            return sum(1 for cell in fused_gp.pos if cell[1] == self._row_idx)
        else:
            return sum(1 for cell in fused_gp.pos if cell[0] == self._col_idx)

    def fusable(self):
        """
        Check if the fusion is possible.
        """
        obs_fusable = self._can_fuse_set_of_gridded_perms(
            self.obstruction_fuse_counter)
        req_fusable = all(self._can_fuse_set_of_gridded_perms(counter)
                          for counter in self.requirements_fuse_counters)
        return obs_fusable and req_fusable

    def fused_tiling(self):
        """
        Return the fused tiling.
        """
        return self._tiling.__class__(
            obstructions=self.obstruction_fuse_counter.keys(),
            requirements=map(dict.keys, self.requirements_fuse_counters),
        )

    def formal_step(self):
        """
        Return a string describing the operation performed on the tiling.
        """
        fusing = 'rows' if self._fuse_row else 'columns'
        idx = self._row_idx if self._fuse_row else self._col_idx
        return "Fuse {} {} and {}.".format(fusing, idx, idx+1)

    def rule(self):
        """
        Return a comb_spec_searcher rule for the fusion.

        If the tiling is not fusable, return None.
        """
        if self.fusable():
            return Rule(formal_step=self.formal_step(),
                        comb_classes=[self.fused_tiling()],
                        inferable=[True],
                        workable=[True],
                        possibly_empty=[False],
                        constructor='other')

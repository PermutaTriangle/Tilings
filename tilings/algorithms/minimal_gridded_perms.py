from collections import Counter
from heapq import heapify, heappop, heappush
from itertools import chain, product
from typing import Iterator, List, Optional, Tuple

from permuta import Perm
from tilings import GriddedPerm
from tilings.misc import union_reduce

Cell = Tuple[int, int]


class Info(tuple):
    def __lt__(self, other):
        return self[0].__lt__(other[0])


class MinimalGriddedPerms(object):
    def __init__(self, tiling):
        self.obstructions = tiling.obstructions
        self.requirements = tiling.requirements
        self.seen = set()
        self.yielded = set()
        self.queue = []
        heapify(self.queue)

    def satisfies_obstructions(self, gp: GriddedPerm) -> bool:
        """Check if a gridded permutation avoids all obstructions."""
        return gp.avoids(*self.obstructions)

    def satisfies_requirements(self, gp: GriddedPerm) -> bool:
        """Check if a gridded permutation contains all requirements."""
        return all(gp.contains(*req) for req in self.requirements)

    def yielded_subgridded_perm(self, gp: GriddedPerm) -> bool:
        """Return True if a subgridded perm was yielded."""
        return gp.contains(*self.yielded)

    def prepare_queue(self) -> None:
        """Add cell counters with gridded permutations to the queue."""
        if len(self.requirements) <= 1:
            return
        for gps in product(*self.requirements):
            max_cell_count = self.cell_counter(*gps)
            new_info = Info([self.initial_gp(*gps), max_cell_count])
            heappush(self.queue, new_info)

    @staticmethod
    def initial_gp(*gps):
        """
        Return the gridded perm that initialises with the first argument,
        then adds as many points as possible from the left to right, such that
        the cells don't share a row or column. In this instance, to contain
        both you must contain the respective subgridded perm in the independent
        cell.
        """
        res = gps[0]
        active_cols = set(i for i, j in res.pos)
        active_rows = set(j for i, j in res.pos)
        for gp in gps[1:]:
            indep_cells = [(i, j) for i, j in gp.pos
                           if i not in active_cols and j not in active_rows]
            if indep_cells:
                subgp = gp.get_gridded_perm_in_cells(indep_cells)
                active_cols.update(i for i, j in subgp.pos)
                active_rows.update(j for i, j in subgp.pos)
                temp = ([(cell, (idx, val))
                         for (idx, val), cell in zip(enumerate(res.patt),
                                                     res.pos)] +
                        [(cell, (idx, val))
                         for (idx, val), cell in zip(enumerate(subgp.patt),
                                                     subgp.pos)])
                temp.sort()
                new_pos = [cell for cell, _ in temp]
                new_patt = Perm.to_standard(temp)
                res = GriddedPerm(new_patt, new_pos)
        return res

    @staticmethod
    def cell_counter(*gps: GriddedPerm) -> Counter:
        """Returns a counter of the sum of number of cells used by the gridded
        permutations. If 'counter' is given, will update this Counter."""
        return Counter(chain.from_iterable(gp.pos for gp in gps))

    def get_cells_to_try(
                         self, gp: GriddedPerm,
                         max_cell_count: Counter
                        ) -> Iterator[Cell]:
        """Yield cells that a gridded permutation could be extended by."""
        currcellcounts = self.cell_counter(gp)
        for cell, count in max_cell_count.items():
            if count > currcellcounts[cell]:
                yield cell

    def minimal_gridded_perms(self) -> Iterator[GriddedPerm]:
        """Yield all minimal gridded perms on the tiling."""
        if not self.requirements:
            if GriddedPerm.empty_perm() not in self.obstructions:
                yield GriddedPerm.empty_perm()
            return
        if len(self.requirements) == 1:
            yield from iter(self.requirements[0])
            return
        self.prepare_queue()
        while self.queue:
            startgp, max_cell_count = heappop(self.queue)
            for cell in self.get_cells_to_try(startgp, max_cell_count):
                for gp in startgp.insert_point(cell):
                    if gp not in self.seen:
                        self.seen.add(gp)
                        if (self.satisfies_obstructions(gp) and
                                not self.yielded_subgridded_perm(gp)):
                            if self.satisfies_requirements(gp):
                                self.yielded.add(gp)
                                yield gp
                            else:
                                heappush(self.queue,
                                         Info([gp, max_cell_count]))

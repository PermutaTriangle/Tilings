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
        # a priority queue sorted by length of the gridded perm. This is
        # ensured by overwriting the __lt__ operator in the Info class.
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
            # max_cell_count is the theoretical bound on the size of the
            # largest minimal gridded permutation that contains each gridded
            # permutation in gps.
            max_cell_count = self.cell_counter(*gps)
            # we pass on this information, together with the target gps. This
            # will be used to guide us in choosing smartly which cells to
            # insert into - see the 'get_cells_to_try' method.
            new_info = Info([self.initial_gp(*gps), max_cell_count, list(gps)])
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
        # initialise with the first gridded permutation in gps.
        res = gps[0]
        active_cols = set(i for i, j in res.pos)
        active_rows = set(j for i, j in res.pos)
        for gp in gps[1:]:
            # for each subsequent gridded perm in gps, find all the cells
            # not on the same row or column
            indep_cells = [(i, j) for i, j in gp.pos
                           if i not in active_cols and j not in active_rows]
            if indep_cells:
                # take the subgp using the independent cells.
                # we will now glue together the result, and the new independent
                # cell in the unique way that this can be done
                subgp = gp.get_gridded_perm_in_cells(indep_cells)
                # update future active rows and cols
                active_cols.update(i for i, j in subgp.pos)
                active_rows.update(j for i, j in subgp.pos)
                # after sorting temp, the cells will indicate the future
                # positions and upon standardising we will get the underlying
                # permutation
                temp = ([(cell, (idx, val))
                         for (idx, val), cell in zip(enumerate(res.patt),
                                                     res.pos)] +
                        [(cell, (idx, val))
                         for (idx, val), cell in zip(enumerate(subgp.patt),
                                                     subgp.pos)])
                temp.sort()
                # update the res
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
                         self, gp: GriddedPerm, max_cell_count: Counter,
                         gps: List[GriddedPerm]
                        ) -> Iterator[Cell]:
        """Yield cells that a gridded permutation could be extended by."""
        # Only insert into cells in the requirements that are not already
        # satisfied.
        cells = set(chain.from_iterable(g.pos for g, req in zip(
                                                gps[1:], self.requirements[1:])
                                        if gp.avoids(*req)))
        currcellcounts = self.cell_counter(gp)
        for cell in cells:
            # Only insert into cells if we have not gone above the theoretical
            # bound on the number of points needed to contains all gridded
            # permutations in gps.
            if max_cell_count[cell] > currcellcounts[cell]:
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
            # take the next gridded permutation of the queue, together with the
            # theoretical counts to create a gridded permutation containing
            # each of gps.
            startgp, max_cell_count, gps = heappop(self.queue)
            for cell in self.get_cells_to_try(startgp, max_cell_count, gps):
                # this function places a new point into the cell in every
                # possible way.
                for gp in startgp.insert_point(cell):
                    # if the newly created gridded permutation has been seen
                    # then skip it
                    if gp not in self.seen:
                        self.seen.add(gp)
                        # if we the gridded perm doesn't avoid the obstructions
                        # then it, and all that can be reached by adding
                        # further points will not be on the tiling.
                        if (self.satisfies_obstructions(gp) and
                                # if a subgridded perm has been yielded then
                                # the new gridded perm is not minimal.
                                not self.yielded_subgridded_perm(gp)):
                            # if it satisfies all the requirements it is
                            # minimal, and inserting a further point will break
                            # the minimality condition
                            if self.satisfies_requirements(gp):
                                self.yielded.add(gp)
                                yield gp
                            else:
                                # the gridded permutation still doesn't contain
                                # all of the requirement, so add to the queue
                                # in order to insert another point.
                                heappush(self.queue,
                                         Info([gp, max_cell_count, gps]))

from collections import defaultdict
from heapq import heapify, heappop, heappush
from itertools import chain, product

from typing import DefaultDict, Iterator, List, Optional, Tuple
from tilings import GriddedPerm
from tilings.misc import union_reduce

Cell = Tuple[int, int]
Counter = DefaultDict[Cell, int]

class Info(tuple):
    def __lt__(self, other):
        return self[0].__lt__(other[0])

class MinimalGriddedPerms(object):
    def __init__(self, tiling):
        self.obstructions = tiling.obstructions
        self.requirements = tiling.requirements
        self.active_cells = union_reduce(union_reduce(gp.pos for gp in req)
                                         for req in self.requirements)
        self.seen = set()
        self.yielded = set()
        self.queue = []
        heapify(self.queue)

    def pop(self) -> Info:
        """Return next Info on the queue."""
        info = heappop(self.queue)
        return info

    def put(self, info: Info) -> None:
        """Put into onto the queue."""
        heappush(self.queue, info)

    def empty_queue(self) -> bool:
        """Return true if the queue is empty."""
        return not bool(self.queue)

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
        first_req = self.requirements[0]

        for gp in first_req:
            max_cell_counts = []
            cells = set()
            for gps in product(*self.requirements[1:]):
                max_cell_count = defaultdict(int)
                for othergp in gps:
                    max_cell_count = self.cell_counter(othergp, max_cell_count)
                max_cell_count = self.cell_counter(gp, max_cell_count)
                max_cell_counts.append(max_cell_count)
                cells.update(max_cell_count)

            new_info = Info([gp, max_cell_counts, cells])
            self.put(new_info)

    @staticmethod
    def cell_counter(
                     gp: GriddedPerm, counter: Optional[Counter] = None
                     ) -> Counter:
        """Returns a counter of the number of cells used by the gridded
        permutation. If 'counter' is given, will update this Counter."""
        if counter is None:
            counter = defaultdict(int)
        for cell in gp.pos:
            counter[cell] += 1
        return counter

    def get_cells_to_try(
                         self, gp: GriddedPerm, max_cell_counts: List[Counter],
                         cells: List[Cell]) -> Iterator[Cell]:
        """Yield cells that a gridded permutation could be extended by."""
        currcellcounts = self.cell_counter(gp)
        if any(all(count >= max_cell_count[cell]
                   for cell, count in currcellcounts.items())
               for max_cell_count in max_cell_counts):
            return
        for cell in cells:
            if any(currcellcounts[cell] < max_cell_count[cell]
                   for max_cell_count in max_cell_counts):
                yield cell

    def minimal_gridded_perms(self) -> Iterator[GriddedPerm]:
        """Yield all minimal gridded perms on the tiling."""
        if not self.requirements:
            return
        if len(self.requirements) == 1:
            yield from iter(self.requirements[0])
            return

        self.prepare_queue()
        while not self.empty_queue():
            startgp, max_cell_counts, cells = self.pop()
            for cell in self.get_cells_to_try(startgp, max_cell_counts, cells):
                for gp in startgp.insert_point(cell):
                    if gp not in self.seen:
                        self.seen.add(gp)
                        if (self.satisfies_obstructions(gp) and
                                not self.yielded_subgridded_perm(gp)):
                            if self.satisfies_requirements(gp):
                                self.yielded.add(gp)
                                yield gp
                            else:
                                self.put(Info([gp, max_cell_counts, cells]))





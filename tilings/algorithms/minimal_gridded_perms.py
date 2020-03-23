from collections import Counter, defaultdict
from heapq import heapify, heappop, heappush
from itertools import chain, product
from typing import TYPE_CHECKING, Dict, Iterator, List, Set, Tuple

from permuta import Perm
from tilings import GriddedPerm

if TYPE_CHECKING:
    from tilings import Tiling

Cell = Tuple[int, int]


class Info(tuple):
    def __lt__(self, other):
        return self[0].__lt__(other[0])


class MinimalGriddedPerms():
    def __init__(self, tiling: 'Tiling'):
        self.obstructions = tiling.obstructions
        self.requirements = tiling.requirements
        self.yielded = set()  # type: Set[GriddedPerm]
        self.queue = []  # type: List[Info]
        self.cells_tried = defaultdict(set)  # type: Dict[Cell, Set[Cell]]
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
            # upward clousure
            upward_closure = self.upward_closure(*gps)
            # try to stitch together as much of the independent cells of the
            # gridded permutation together first
            initial_gp = self.initial_gp(*upward_closure)
            # collect the localised subgridded perms as we will insert into
            # cells not containing thest first as they are needed.
            localised_patts = self.localised_patts(*upward_closure)
            # max_cell_count is the theoretical bound on the size of the
            # largest minimal gridded permutation that contains each
            # gridded permutation in gps.
            max_cell_count = self.cell_counter(*upward_closure)
            # we pass on this information, together with the target gps
            # will be used to guide us in choosing smartly which cells to
            # insert into - see the 'get_cells_to_try' method.
            new_info = Info([initial_gp, localised_patts,
                             max_cell_count, tuple(gps), (-1, -1)])
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
        # the sort here is a heuristic. the idea is to try avoid having to
        # insert into more cells in the future.
        # gps = sorted(gps, key=lambda x: -len(x))
        res = GriddedPerm(gps[0].patt, gps[0].pos)
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
                # temp will be sorted, and standardised to create the unique
                # minimal gridded permutation containing both res and subgp.
                # We want cells at lower index front - if they are in the same
                # column, then they come from the same gridded permutation, so
                # we sort second by the index of its original gridded perm.
                # We will standardise based on values. Those in lower cells
                # will have smaller value, and if they are in the same row then
                # they come from the same gridded permutation so the second
                # entry is the value from its original gridded perm.
                temp = ([((cell[0], idx), (cell[1], val))
                         for (idx, val), cell in zip(enumerate(res.patt),
                                                     res.pos)] +
                        [((cell[0], idx), (cell[1], val))
                         for (idx, val), cell in zip(enumerate(subgp.patt),
                                                     subgp.pos)])
                temp.sort()
                # update the res
                new_pos = [(idx[0], val[0]) for idx, val in temp]
                new_patt = Perm.to_standard(val for _, val in temp)
                res = GriddedPerm(new_patt, new_pos)
        return res

    @staticmethod
    def cell_counter(*gps: GriddedPerm) -> Counter:
        """Returns a counter of the sum of number of cells used by the gridded
        permutations. If 'counter' is given, will update this Counter."""
        return Counter(chain.from_iterable(gp.pos for gp in gps))

    @staticmethod
    def localised_patts(*gps: GriddedPerm) -> Dict[Cell, List[GriddedPerm]]:
        """Return the localised patts that gps must contain."""
        res = defaultdict(set)  # type: Dict[Cell, Set[GriddedPerm]]
        # for each gp, and cell find the localised subgridded perm in the cell
        for gp in gps:
            for cell in set(gp.pos):
                res[cell].add(gp.get_gridded_perm_in_cells([cell]))
        # Only keep the upward closure for each cell.
        return {cell: MinimalGriddedPerms.upward_closure(*patts)
                for cell, patts in res.items()}

    @staticmethod
    def upward_closure(*gps: GriddedPerm) -> List[GriddedPerm]:
        """Return list of gridded perms such that every gridded perm contained
        in another is removed."""
        res = []  # type: List[GriddedPerm]
        for gp in sorted(gps, key=len, reverse=True):
            if all(gp not in g for g in res):
                res.append(gp)
        return res

    def get_cells_to_try(
                         self,
                         gp: GriddedPerm,
                         localised_patts: Dict[Cell, List[GriddedPerm]],
                         max_cell_count: Counter,
                         gps: List[GriddedPerm]
                        ) -> Iterator[Cell]:
        """Yield cells that a gridded permutation could be extended by."""
        cells = set()  # type: Set[Cell]
        for g, req in zip(gps, self.requirements):
            if gp.avoids(*req):
                # Only insert into cells in the requirements that are not
                # already satisfied.
                cells.update(g.pos)
            elif gp.avoids(g):
                # If any requirement contains a requirement, but not the target
                # gridded perm from that requirement in gps, then inserting
                # further will not result in a minimal gridded perm that will
                # not be found by another target.
                return
        currcellcounts = self.cell_counter(gp)

        def try_yield(*cells):
            # Only insert into cells if we have not gone above the theoretical
            # bound on the number of points needed to contains all gridded
            # permutations in gps, and not yielded before.
            for cell in cells:
                if (max_cell_count[cell] > currcellcounts[cell] and
                        cell not in self.cells_tried[(gp, gps)]):
                    yield cell
                    # store this to prevent yielding same cell twice.
                    self.cells_tried[(gp, gps)].add(cell)
        for cell in cells:
            # try to insert into a cell that doesn't contain all of the
            # localised patterns frist
            if gp.avoids(*localised_patts[cell]):
                yield from try_yield(cell)
                return
        # otherwise, we are non the wiser which cell to insert into so try
        # all possible cells
        yield from try_yield(*cells)

    def minimal_gridded_perms(self) -> Iterator[GriddedPerm]:
        """Yield all minimal gridded perms on the tiling."""
        if not self.requirements:
            if GriddedPerm.empty_perm() not in self.obstructions:
                yield GriddedPerm.empty_perm()
            return
        if len(self.requirements) == 1:
            yield from iter(self.requirements[0])
            return
        # will yield any that satisfy all the requirements.
        self.prepare_queue()
        while self.queue:
            # take the next gridded permutation of the queue, together with the
            # theoretical counts to create a gridded permutation containing
            # each of gps.
            gp, localised_patts, max_cell_count, gps, last_cell = heappop(self.queue)
            # only consider gridded perms where a subgridded perm has not been
            # yielded.
            if (not self.yielded_subgridded_perm(gp) and
                    self.satisfies_obstructions(gp)):
                if self.satisfies_requirements(gp):
                    # if it satisfies all the requirements it is
                    # minimal, and inserting a further point will break
                    # the minimality condition
                    self.yielded.add(gp)
                    yield gp
                else:
                    # otherwise we must try to insert a new point into a cell
                    for cell in self.get_cells_to_try(gp, localised_patts,
                                                      max_cell_count, gps):
                        if cell < last_cell:
                            continue
                        # this function places a new point into the cell in
                        # possible way.
                        for nextgp in set(gp.insert_point(cell)):
                            # if we the gridded perm doesn't avoid the
                            # obstructions then it, and all that can be reached
                            # by adding further points will not be on the
                            # tiling.
                            heappush(self.queue,
                                     Info([nextgp, localised_patts,
                                           max_cell_count, gps, cell]))

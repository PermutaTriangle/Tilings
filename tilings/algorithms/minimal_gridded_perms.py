from collections import Counter
from heapq import heapify, heappop, heappush
from itertools import chain, product
from typing import TYPE_CHECKING, Dict, FrozenSet, Iterator, Tuple

from permuta import Perm
from tilings import GriddedPerm, Obstruction

if TYPE_CHECKING:
    from tilings import Tiling
    from typing import List, Set  # Only used in comments


Cell = Tuple[int, int]
GPTuple = Tuple[GriddedPerm, ...]
Reqs = Tuple[GPTuple, ...]
WorkPackets = Tuple[GriddedPerm, GPTuple, Cell]


class Info(tuple):
    def __lt__(self, other):
        return self[0].__lt__(other[0])


class MinimalGriddedPerms():
    def __init__(self, tiling: 'Tiling'):
        self.obstructions = tiling.obstructions
        self.requirements = tiling.requirements
        self.yielded = set()  # type: Set[GriddedPerm]
        self.queue = []  # type: List[Info]
        self.work_packets_done = set()  # Set[WorkPackets]
        self.relevant_obstructions = dict()  # Dict[GPTuple, GPTuple]
        self.relevant_requirements = dict()  # Dict[GPTuple, Reqs]
        self.relevant_obstructions_by_cell = dict()  # Dict[Tuple[Cell, GPTuple], GPTuple]
        self.requirements_up_to_cell = dict()  # Dict[Tuple[Cell, GPTuple], GPTuple]
        self.initial_gps_to_auto_yield = set()  # Set[GriddedPerm]
        # Delay computing until needed - these could all be stored on
        # MinimalGriddedPerms, as none of these are tiling specific.
        self.localised_patts = dict()  # Dict[GPTuple, GPTuple]
        self.max_cell_counts = dict()  # Dict[GPTuple, Dict[Cell, int]]
        self.upward_closures = dict()  # Dict[GPTuple, GPTuple]
        # a priority queue sorted by length of the gridded perm. This is
        # ensured by overwriting the __lt__ operator in the Info class.
        heapify(self.queue)

    def get_requirements_up_to_cell(self, cell: Cell, gps: GPTuple) -> GPTuple:
        """Given a goal gps and cell (x,y), return the truncations of the reqs
        in gps to the cells < (x, y) in normal sort order."""
        res = self.requirements_up_to_cell.get((cell, gps))
        if res is None:
            res = tuple(req.get_gridded_perm_in_cells(
                                    frozenset(c for c in req.pos if c < cell))
                        for req in gps)
            self.requirements_up_to_cell[(cell, gps)] = res
        return res

    def get_relevant_obstructions(self, gp: GriddedPerm) -> GPTuple:
        """Get the requirements that involve only cells in the gp."""
        cells = frozenset(gp.pos)
        res = self.relevant_obstructions.get(cells)
        if res is None:
            res = tuple(ob for ob in self.obstructions
                        if all(c in cells for c in ob.pos))
            self.relevant_obstructions[cells] = res
        return res

    def get_relevant_obstructions_by_cell(
                                          self, gp: GriddedPerm, cell: Cell
                                         ) -> GPTuple:
        """ Get the obstructions that involve only cells in gp
        and involve cell"""
        cells = frozenset(gp.pos)
        res = self.relevant_obstructions_by_cell.get((cell, cells))
        if res is None:
            relevant_obstructions = self.get_relevant_obstructions(gp)
            res = tuple(ob for ob in relevant_obstructions if cell in ob.pos)
            self.relevant_obstructions_by_cell[(cell, cells)] = res
        return res

    def get_relevant_requirements(self, gp: GriddedPerm) -> Reqs:
        """Get the requirements that involve only cells in gp."""
        cells = frozenset(gp.pos)
        res = self.relevant_requirements.get(cells)
        if res is None:
            res = tuple(tuple(req for req in reqlist
                              if all(c in cells for c in req.pos))
                        for reqlist in self.requirements)
            self.relevant_requirements[cells] = res
        return res

    def satisfies_obstructions(self, gp: GriddedPerm,
                               must_contain: Cell = None) -> bool:
        """Check if a gridded permutation avoids the obstructions."""
        if must_contain is None:
            obs = self.get_relevant_obstructions(gp)
        else:
            obs = self.get_relevant_obstructions_by_cell(gp, must_contain)
        return gp.avoids(*obs)

    def satisfies_requirements(self, gp: GriddedPerm) -> bool:
        """Check if a gridded permutation contains all requirements."""
        reqs = self.get_relevant_requirements(gp)
        return all(reqs) and all(gp.contains(*req) for req in reqs)

    def yielded_subgridded_perm(self, gp: GriddedPerm) -> bool:
        """Return True if a subgridded perm was yielded."""
        return gp.contains(*self.yielded, *self.initial_gps_to_auto_yield)

    def prepare_queue(
                      self, yield_non_minimal: bool = False
                     ) -> Iterator[GriddedPerm]:
        """Add cell counters with gridded permutations to the queue."""
        if len(self.requirements) <= 1:
            return
        for gps in product(*self.requirements):
            # try to stitch together as much of the independent cells of the
            # gridded permutation together first
            initial_gp = self.initial_gp(*gps)

            # EDIT: initial_gp.avoids(*self.get_relevant_obstructions(gps)):
            if self.satisfies_obstructions(initial_gp):
                # We will now prepare to add it to the queue.
                if self.satisfies_requirements(initial_gp):
                    if yield_non_minimal:
                        yield initial_gp
                    else:
                        # even if [initial_gp] meets the requirements, we can't
                        # yield it yet, because it might not be minimal
                        # so, we add it to a list, and yield it when we see it
                        # later if it is actually is minimal
                        self.initial_gps_to_auto_yield.add(initial_gp)

                # we pass on this information, together with the target gps
                # will be used to guide us in choosing smartly which cells to
                # insert into - see the 'get_cells_to_try' method.
                cells = frozenset(chain.from_iterable(gp.pos for gp in gps))
                # mindices ensure we insert left to right in each cell
                mindices = {cell: -1 for cell in cells}
                # last_cell ensures that we insert into cells in order after
                # we have satisfied the local patterns needed
                last_cell = (-1, -1)
                # this flag ensures we first make sure we contain all local
                # patterns
                localised = True
                # add all of this information the queue. The Info class ensures
                # we sort by initial_gp only.
                new_info = Info([initial_gp, tuple(gps), last_cell, localised,
                                 mindices])
                heappush(self.queue, new_info)

    def initial_gp(self, *gps: GriddedPerm) -> GriddedPerm:
        """
        Return the gridded perm that initialises with the first argument,
        then adds as many points as possible from the left to right, such that
        the cells don't share a row or column. In this instance, to contain
        both you must contain the respective subgridded perm in the independent
        cell.
        """
        # We work with the upward closure.
        gps = self.get_upward_closure(gps)
        # Initialise with the first gridded permutation in gps.
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
    def cell_counter(*gps: GriddedPerm) -> Dict[Cell, int]:
        """Returns a counter of the sum of number of cells used by the gridded
        permutations. If 'counter' is given, will update this Counter."""
        return Counter(chain.from_iterable(gp.pos for gp in gps))

    def get_max_cell_count(self, gps: GPTuple) -> Dict[Cell, int]:
        """Return the theoretical maximum number of points needed in each cell.
        It assumes that gps is closed upwards."""
        res = self.max_cell_counts.get(gps)
        if res is None:
            # we work with the upward closure.
            gps = self.get_upward_closure(gps)
            res = MinimalGriddedPerms.cell_counter(*gps)
            # now we look for any cells containing more than one full req and
            # are not involved with any other requirements, because we may be
            # able to apply a better upper bound to the number of points
            # required in the cell
            for cell in set(chain.from_iterable(gp.pos for gp in gps)):
                in_this_cell = set()
                for req in gps:
                    # we ignore point requirements
                    if len(req) > 1 and cell in req.pos:
                        if req.is_single_cell():
                            # [req] is entirely in [cell]
                            in_this_cell.add(req.patt)
                        else:
                            # [req] involves [cell], but also some other cell,
                            # so this cell won't have a usable upper bound
                            break
                else:
                    # if we get here, then we can use the precomputed bounds
                    # for this cell
                    better_bounds = MinimalGriddedPerms.better_bounds()
                    # the bounds can only be better if there are two or more
                    # patterns
                    if len(in_this_cell) >= 2:
                        in_this_cell = frozenset(in_this_cell)
                        # the dictionary is patt: v, where v is the number we
                        # can subtract from the naive bound
                        res[cell] -= better_bounds.get(in_this_cell, 0)
            self.max_cell_counts[gps] = res
        return res

    _better_bounds = None

    @staticmethod
    def better_bounds() -> Dict[FrozenSet[Perm], int]:
        """
        Return a dictionary. The entry k:v means that if a cell contains
        the full requirments in k, and no others touch it, then the upper
        bound for the number of points that will need to be placed in that
        cell is the sum of the lenths of the perms in k, minus v.

        Example: a cell containing 01 and 10 has an upper bound of 3, not 4
        """
        if MinimalGriddedPerms._better_bounds is None:
            from .better_bounds import better_bounds
            MinimalGriddedPerms._better_bounds = better_bounds
        return MinimalGriddedPerms._better_bounds

    def get_localised_patts(self, cell: Cell, gps: GPTuple) -> GPTuple:
        """Return the localised patts that gps must contain."""
        res = self.localised_patts.get((cell, gps))
        if res is None:
            res = set()
            for gp in gps:
                res.add(gp.get_gridded_perm_in_cells([cell]))
            # Only keep the upward closure.
            res = self.get_upward_closure(tuple(res))
            self.localised_patts[(cell, gps)] = res
        return res

    def get_upward_closure(self, gps: GPTuple) -> GPTuple:
        """Return list of gridded perms such that every gridded perm contained
        in another is removed."""
        res = self.upward_closures.get(gps)
        if res is None:
            res = []
            for gp in sorted(gps, key=len, reverse=True):
                if all(gp not in g for g in res):
                    res.append(gp)
            res = tuple(res)
            self.upward_closures[gps] = res
        return res

    def get_cells_to_try(
                         self,
                         gp: GriddedPerm,
                         gps: GPTuple,
                         last_cell: Cell,
                         try_localised: bool
                        ) -> Iterator[Cell]:
        """Yield cells that a gridded permutation could be extended by."""
        cells = set()  # type: Set[Cell]
        for g, req in zip(gps, self.get_relevant_requirements(gp)):
            if gp.avoids(*req):
                # Only insert into cells in the requirements that are not
                # already satisfied.
                cells.update(g.pos)
            elif g not in req or gp.avoids(g):
                # If any requirement contains a requirement, but not the target
                # gridded perm from that requirement in gps, then inserting
                # further will not result in a minimal gridded perm that will
                # not be found by another target.
                return
        # Ensure we insert into the smallest cell possible first.
        currcellcounts = self.cell_counter(gp)
        max_cell_count = self.get_max_cell_count(gps)

        def can_insert(cell):
            """only consider cells which don't already have the maximum number
            of points inserted into them"""
            return max_cell_count[cell] > currcellcounts[cell]
        cells = sorted(filter(can_insert, cells))

        def try_yield(cells, localised):
            for cell in cells:
                # if this comes from a localised pattern, then yield
                # otherwise we can only insert into a cell greater or equal to
                # the last cell inserted into, to avoid duplicate work.
                if localised or cell == last_cell:
                    yield (cell, localised)
                # if it is greater, then we must ensure that we can satisfy the
                # the requirements we are aiming for in gps, and contain all of
                # the gps restricted to smaller cells
                elif cell > last_cell:
                    prior_reqs = self.get_requirements_up_to_cell(cell, gps)
                    if all(gp.contains(req) for req in prior_reqs):
                        yield (cell, localised)
        if try_localised:
            for cell in cells:
                # try to insert into a cell that doesn't contain all of the
                # localised patterns frist
                if gp.avoids(*self.get_localised_patts(cell, gps)):
                    yield from try_yield([cell], True)
                    return
        # otherwise, we are none the wiser which cell to insert into so try
        # all possible cells
        yield from try_yield(cells, False)

    def minimal_gridded_perms(
                              self, yield_non_minimal: bool = False
                             ) -> Iterator[GriddedPerm]:
        """
        Yield all minimal gridded perms on the tiling.

        If `yield_non_minimal` is True, then it will yield some gridded perms
        that are non-minimal, found by the initial_gp method. Even though it
        may not be minimal, this is useful when trying to determine whether or
        not a tiling is empty.
        """
        if not self.requirements:
            if Obstruction.empty_perm() not in self.obstructions:
                yield GriddedPerm.empty_perm()
            return
        if len(self.requirements) == 1:
            for req in self.requirements[0]:
                yield GriddedPerm.from_gridded_perm(req)
            return

        yield from self.prepare_queue(yield_non_minimal=yield_non_minimal)

        while self.queue:
            # take the next gridded permutation of the queue, together with the
            # theoretical counts to create a gridded permutation containing
            # each of gps.
            (gp, gps, last_cell,
             still_localising, last_mindices) = heappop(self.queue)
            # if gp was one of the initial_gps that satisfied obs/reqs, but
            # we weren't sure at the time if it was minimal, then now is the
            # time to check and yield
            if gp in self.initial_gps_to_auto_yield:
                # removing this speed up a later check by a tiny bit
                self.initial_gps_to_auto_yield.remove(gp)
                if not self.yielded_subgridded_perm(gp):
                    self.yielded.add(gp)
                    yield gp
                # We move onto the next gridded permutation
                continue
            # now we try inserting a new point into the cell
            for (cell, localised) in self.get_cells_to_try(gp, gps, last_cell,
                                                           still_localising):
                # Find the bounding box of where the point can be inserted.
                mindex, maxdex, minval, maxval = gp.get_bounding_box(cell)
                # We make sure we only insert to the right of where the last
                # point was inserted into the cell.
                mindex = max(mindex, last_mindices[cell])
                for idx, val in product(range(maxdex, mindex - 1, -1),
                                        range(minval, maxval + 1)):
                    nextgp = gp.insert_specific_point(cell, idx, val)
                    # Only work with gridded permutations avoiding the
                    # obstructions, and those which we haven't yielded a
                    # subgridded permutation.
                    if (self.satisfies_obstructions(nextgp,
                                                    must_contain=cell) and
                            not self.yielded_subgridded_perm(nextgp)):
                        # If it satisfies the requirements, then it is a
                        # a minimal gridded permutation
                        if self.satisfies_requirements(nextgp):
                            # Keep track to ensure we don't yield a gridded
                            # perm containing it.
                            self.yielded.add(nextgp)
                            yield nextgp
                        else:
                            # The `localised` bool tells us if we inserted into
                            # a cell as it didn't contain the patterns in the
                            # cell. If not, then we update the last cell, to
                            # ensure we only insert into greater or equal cells
                            next_cell = last_cell if localised else cell
                            # The work_packets_done is used to ensure the same
                            # task is not added to the queue twice.
                            key = (nextgp, gps, next_cell)
                            if key not in self.work_packets_done:
                                # Update the minimum index that we inserted a
                                # a point into each cell.
                                next_mindices = {
                                        c: i if i <= idx else i + 1
                                        for c, i in last_mindices.items()
                                        if c != cell}
                                next_mindices[cell] = idx + 1
                                self.work_packets_done.add(key)
                                # Add the work to the queue
                                heappush(self.queue,
                                         Info([nextgp, gps, next_cell,
                                               localised, next_mindices]))

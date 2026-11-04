from collections import Counter, defaultdict
from heapq import heapify, heappop, heappush
from itertools import chain, combinations, product
from typing import Dict, FrozenSet, Iterator, List, Optional, Set, Tuple

from permuta import Perm
from tilings import GriddedPerm

__all__ = ["MinimalGriddedPerms"]

Cell = Tuple[int, int]
GPTuple = Tuple[GriddedPerm, ...]
Reqs = Tuple[GPTuple, ...]
WorkPackets = Tuple[GriddedPerm, GPTuple, Cell]


class QueuePacket:
    def __init__(
        self,
        gp: GriddedPerm,
        gps: GPTuple,
        last_cell: Cell,
        still_localising: bool,
        mindices: Dict[Cell, int],
    ):
        self.gp = gp
        self.gps = gps
        self.last_cell = last_cell
        self.still_localising = still_localising
        self.mindices = mindices

    def __lt__(self, other: "QueuePacket"):
        return len(self.gp) < len(other.gp)


class MinimalGriddedPerms:
    def __init__(self, obstructions: GPTuple, requirements: Reqs):
        self.obstructions = obstructions
        self.requirements = requirements
        self.relevant_obstructions: Dict[FrozenSet[Cell], GPTuple] = {}
        self.relevant_requirements: Dict[FrozenSet[Cell], Reqs] = {}
        self.relevant_obstructions_by_cell: Dict[
            Tuple[Cell, FrozenSet[Cell]], GPTuple
        ] = {}
        self.requirements_up_to_cell: Dict[Tuple[Cell, GPTuple], GPTuple] = {}
        # Delay computing until needed - these could all be stored on
        # MinimalGriddedPerms, as none of these are tiling specific.
        self.localised_patts: Dict[Tuple[Cell, GPTuple], GPTuple] = {}
        self.max_cell_counts: Dict[GPTuple, Dict[Cell, int]] = {}
        self.upward_closures: Dict[GPTuple, GPTuple] = {}
        self.known_patts: Dict[GriddedPerm, Set[GriddedPerm]] = defaultdict(set)
        # Caches for find_gridded_perm's _points_lacking_by_patterns.
        self.requirement_patterns: Dict[GriddedPerm, Dict[Cell, Perm]] = {}
        self.points_in_common: Dict[Tuple[Perm, Perm], int] = {}

    def get_requirements_up_to_cell(self, cell: Cell, gps: GPTuple) -> GPTuple:
        """Given a goal gps and cell (x,y), return the truncations of the reqs
        in gps to the cells < (x, y) in normal sort order."""
        res = self.requirements_up_to_cell.get((cell, gps))
        if res is None:
            res = tuple(
                req.get_gridded_perm_in_cells(frozenset(c for c in req.pos if c < cell))
                for req in gps
            )
            self.requirements_up_to_cell[(cell, gps)] = res
        return res

    def get_relevant_obstructions(self, gp: GriddedPerm) -> GPTuple:
        """Get the obstructions that involve only cells in the gp."""
        cells = frozenset(gp.pos)
        res = self.relevant_obstructions.get(cells)
        if res is None:
            res = tuple(
                ob for ob in self.obstructions if all(c in cells for c in ob.pos)
            )
            self.relevant_obstructions[cells] = res
        return res

    def get_relevant_obstructions_by_cell(self, gp: GriddedPerm, cell: Cell) -> GPTuple:
        """Get the obstructions that involve only cells in gp
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
            res = tuple(
                tuple(req for req in reqlist if all(c in cells for c in req.pos))
                for reqlist in self.requirements
            )
            self.relevant_requirements[cells] = res
        return res

    def satisfies_obstructions(
        self, gp: GriddedPerm, must_contain: Optional[Cell] = None
    ) -> bool:
        """Check if a gridded permutation avoids the obstructions."""
        if must_contain is None:
            obs = self.get_relevant_obstructions(gp)
        else:
            obs = self.get_relevant_obstructions_by_cell(gp, must_contain)
        return gp.avoids(*obs)

    def satisfies_requirements(self, gp: GriddedPerm) -> bool:
        """Check if a gridded permutation contains all requirements."""
        reqs = self.get_relevant_requirements(gp)
        return all(reqs) and all(self.contains(gp, *req) for req in reqs)

    def avoids(self, gp: GriddedPerm, *patts: GriddedPerm) -> bool:
        """An avoidance check. See contains method."""
        return not self.contains(gp, *patts)

    def contains(self, gp: GriddedPerm, *patts: GriddedPerm) -> bool:
        """This is a an alternative containment check.
        It will return True if any element of patts is contained in gp, and add
        it to the known_patts. Only use this if it is worth caching, so in the
        usage case, if the check is related to the target gps requirement."""
        known_patts = self.known_patts[gp]
        if any(patt in known_patts for patt in patts):
            return True
        for patt in patts:
            if gp.contains(patt):
                known_patts.add(patt)
                return True
        return False

    def _product_requirements(
        self, max_length_to_build: Optional[int] = None
    ) -> Iterator[GPTuple]:
        if max_length_to_build is None:
            yield from product(*self.requirements)
            return

        def _rec_product_requirements(
            requirements: Reqs, counter: Dict[Cell, int]
        ) -> Iterator[GPTuple]:
            if len(requirements) == 0:
                yield tuple()
                return
            reqs = requirements[0]
            rest = requirements[1:]
            for gp in reqs:
                gpcounter = Counter(gp.pos)
                new_counter = Counter(
                    {
                        cell: max(gpcounter[cell], counter[cell])
                        for cell in chain(gpcounter, counter)
                    }
                )
                assert max_length_to_build is not None
                if sum(new_counter.values()) <= max_length_to_build:
                    for gps in _rec_product_requirements(rest, new_counter):
                        yield (gp,) + gps

        yield from _rec_product_requirements(self.requirements, Counter())

    def _prepare_queue(
        self, queue: List[QueuePacket], max_length_to_build: Optional[int] = None
    ) -> Iterator[GriddedPerm]:
        """Add cell counters with gridded permutations to the queue.
        The function yields all initial_gp that satisfy the requirements."""
        if len(self.requirements) <= 1:
            return
        for gps in self._product_requirements(max_length_to_build):
            # try to stitch together as much of the independent cells of the
            # gridded permutation together first
            initial_gp = self.initial_gp(*gps)
            if self.satisfies_obstructions(initial_gp):
                # We will now prepare to add it to the queue.
                if self.satisfies_requirements(initial_gp):
                    yield initial_gp
                    continue
                # we pass on this information, together with the target gps
                # will be used to guide us in choosing smartly which cells to
                # insert into - see the 'get_cells_to_try' method.
                # mindices ensure we insert left to right in each cell
                mindices: Dict[Cell, int] = {}
                # last_cell ensures that we insert into cells in order after
                # we have satisfied the local patterns needed
                last_cell = (-1, -1)
                # this flag ensures we first make sure we contain all local
                # patterns
                localised = True
                # add all of this information the queue. The Info class ensures
                # we sort by initial_gp only.
                new_info = QueuePacket(
                    initial_gp, tuple(gps), last_cell, localised, mindices
                )
                heappush(queue, new_info)

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
            indep_cells = [
                (i, j)
                for i, j in gp.pos
                if i not in active_cols and j not in active_rows
            ]
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
                temp = [
                    ((cell[0], idx), (cell[1], val))
                    for (idx, val), cell in zip(enumerate(res.patt), res.pos)
                ] + [
                    ((cell[0], idx), (cell[1], val))
                    for (idx, val), cell in zip(enumerate(subgp.patt), subgp.pos)
                ]
                temp.sort()
                # update the res
                new_pos = [(idx[0], val[0]) for idx, val in temp]
                new_patt = Perm.to_standard(val for _, val in temp)
                res = GriddedPerm(new_patt, new_pos)
        return res

    @staticmethod
    def cell_counter(*gps: GriddedPerm) -> Dict[Cell, int]:
        """Returns a counter of the sum of number of cells used by the gridded
        permutations."""
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
            for cell in res.keys():
                in_this_cell: Set[Perm] = set()
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
                        # the dictionary is patt: v, where v is the number we
                        # can subtract from the naive bound
                        res[cell] -= better_bounds.get(frozenset(in_this_cell), 0)
            self.max_cell_counts[gps] = res
        return res

    _better_bounds: Optional[Dict[FrozenSet[Perm], int]] = None

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
            # pylint: disable=import-outside-toplevel
            from .better_bounds import better_bounds

            MinimalGriddedPerms._better_bounds = better_bounds
        return MinimalGriddedPerms._better_bounds

    def get_localised_patts(self, cell: Cell, gps: GPTuple) -> GPTuple:
        """Return the localised patts that gps must contain."""
        res = self.localised_patts.get((cell, gps))
        if res is None:
            local_patts = set()
            for gp in gps:
                local_patts.add(gp.get_gridded_perm_in_cells([cell]))
            # Only keep the upward closure.
            res = self.get_upward_closure(tuple(local_patts))
            self.localised_patts[(cell, gps)] = res
        return res

    def get_upward_closure(self, gps: GPTuple) -> GPTuple:
        """Return list of gridded perms such that every gridded perm contained
        in another is removed."""
        res = self.upward_closures.get(gps)
        if res is None:
            upward_closure: List[GriddedPerm] = []
            for gp in sorted(gps, key=len, reverse=True):
                if all(gp not in g for g in upward_closure):
                    upward_closure.append(gp)
            res = tuple(upward_closure)
            self.upward_closures[gps] = res
        return res

    def _get_cells_to_try(self, qpacket: QueuePacket) -> Iterator[Tuple[Cell, bool]]:
        """Yield cells that a gridded permutation could be extended by."""
        cells: Set[Cell] = set()
        for g, req in zip(qpacket.gps, self.get_relevant_requirements(qpacket.gp)):
            if not self.contains(qpacket.gp, *req):
                # Only insert into cells in the requirements that are not
                # already satisfied.
                cells.update(g.pos)
            elif g not in req or self.avoids(qpacket.gp, g):
                # If any requirement contains a requirement, but not the target
                # gridded perm from that requirement in gps, then inserting
                # further will not result in a minimal gridded perm that will
                # not be found by another target.
                return
        # Ensure we insert into the smallest cell possible first.
        currcellcounts = self.cell_counter(qpacket.gp)
        max_cell_count = self.get_max_cell_count(qpacket.gps)

        def can_insert(cell: Cell) -> bool:
            """only consider cells which don't already have the maximum number
            of points inserted into them"""
            return max_cell_count[cell] > currcellcounts[cell]

        possible_cells = sorted(filter(can_insert, cells))

        def try_yield(
            cells: List[Cell], localised: bool
        ) -> Iterator[Tuple[Cell, bool]]:
            for cell in cells:
                # if this comes from a localised pattern, then yield
                # otherwise we can only insert into a cell greater or equal to
                # the last cell inserted into, to avoid duplicate work.
                if localised or cell == qpacket.last_cell:
                    yield (cell, localised)
                # if it is greater, then we must ensure that we can satisfy the
                # the requirements we are aiming for in gps, and contain all of
                # the gps restricted to smaller cells
                elif cell > qpacket.last_cell:
                    prior_reqs = self.get_requirements_up_to_cell(cell, qpacket.gps)
                    if all(self.contains(qpacket.gp, req) for req in prior_reqs):
                        yield (cell, localised)

        if qpacket.still_localising:
            for cell in possible_cells:
                # try to insert into a cell that doesn't contain all of the
                # localised patterns frist
                if self.avoids(
                    qpacket.gp, *self.get_localised_patts(cell, qpacket.gps)
                ):
                    yield from try_yield([cell], True)
                    return
        # otherwise, we are none the wiser which cell to insert into so try
        # all possible cells
        yield from try_yield(possible_cells, False)

    @staticmethod
    def insert_point(
        gp: GriddedPerm, cell: Cell, minimumdex: int
    ) -> Iterator[Tuple[int, GriddedPerm]]:
        """Yield all possible gridded perms where a point is inserted into
        the given cell, where the minimum index is mindex if given. We insert
        right to left, to ensure that if a gp is made twice, that with the
        largest index is yielded first.

        Each gridded perm is yielded as a tuple, consisting of the idx of the
        newly inserted point and the gp."""
        # Find the bounding box of where the point can be inserted.
        mindex, maxdex, minval, maxval = gp.get_bounding_box(cell)
        # We make sure we only insert to the right of where the last
        # point was inserted into the cell.
        mindex = max(mindex, minimumdex)
        for idx, val in product(
            range(maxdex, mindex - 1, -1), range(minval, maxval + 1)
        ):
            nextgp = gp.insert_specific_point(cell, idx, val)
            yield idx, nextgp

    def minimal_gridded_perms(
        self, yield_non_minimal: bool = False, max_length_to_build: Optional[int] = None
    ) -> Iterator[GriddedPerm]:
        """
        Yield all minimal gridded perms on the tiling.

        If `yield_non_minimal` is True, then it will yield some gridded perms
        that are non-minimal, found by the initial_gp method. Even though it
        may not be minimal, it is a gridded perm on the tiling. To find just
        one gridded perm, `Tiling.is_empty` uses `find_gridded_perm` instead.

        If `max_length_to_build` it will only try to build minimal gridded
        perms of size shorter than this.
        """
        if not self.requirements:
            if GriddedPerm.empty_perm() not in self.obstructions:
                yield GriddedPerm.empty_perm()
            return
        if len(self.requirements) == 1:
            yield from self.requirements[0]
            return

        # a priority queue sorted by length of the gridded perm. This is
        # ensured by overwriting the __lt__ operator in the Info class.
        queue: List[QueuePacket] = []
        heapify(queue)

        initial_gps_to_auto_yield: Dict[int, Set[GriddedPerm]] = defaultdict(set)
        yielded: Set[GriddedPerm] = set()
        for gp in self._prepare_queue(queue, max_length_to_build):
            if yield_non_minimal:
                yielded.add(gp)
                yield gp
            else:
                initial_gps_to_auto_yield[len(gp)].add(gp)

        def yielded_subgridded_perm(gp: GriddedPerm) -> bool:
            """Return True if a subgridded perm was yielded."""
            return gp.contains(*yielded)

        def _process_work_packet(
            qpacket: QueuePacket, queue: List[QueuePacket]
        ) -> Iterator[GriddedPerm]:
            # find_gridded_perm makes packets by the same steps, in
            # _packets_made_in_cell: keep the two in step.
            # now we try inserting a new point into the cell
            for cell, localised in self._get_cells_to_try(qpacket):
                # The `localised` bool tells us if we inserted into
                # a cell as it didn't contain the patterns in the
                # cell. If not, then we update the last cell, to
                # ensure we only insert into greater or equal cells
                next_cell = qpacket.last_cell if localised else cell
                # Insert a point in every way possible into cell, to the right
                # of any previously placed points in that cell.
                for idx, nextgp in self.insert_point(
                    qpacket.gp, cell, qpacket.mindices.get(cell, 0)
                ):
                    # The work_packets_done is used to ensure the same
                    # task is not processed twice.
                    key = (nextgp, qpacket.gps, next_cell)
                    if key in work_packets_done:
                        continue
                    work_packets_done.add(key)
                    # Only work with gridded permutations avoiding the
                    # obstructions, and those which we haven't yielded a
                    # subgridded permutation.
                    if yielded_subgridded_perm(
                        nextgp
                    ) or not self.satisfies_obstructions(nextgp, must_contain=cell):
                        continue
                    # Update the nextgp about the patterns that are
                    # contained in the subgridded permutation gp.
                    self.known_patts[nextgp].update(self.known_patts[qpacket.gp])
                    # If it satisfies the requirements, then it is a
                    # a minimal gridded permutation
                    if self.satisfies_requirements(nextgp):
                        # Keep track to ensure we don't yield a gridded
                        # perm containing it.
                        yielded.add(nextgp)
                        yield nextgp
                    elif (
                        max_length_to_build is None or len(nextgp) < max_length_to_build
                    ):
                        # Update the minimum index that we inserted a
                        # a point into each cell.
                        next_mindices = self._next_minimum_indices(
                            qpacket.mindices, cell, idx
                        )
                        # Add the work to the queue
                        heappush(
                            queue,
                            QueuePacket(
                                nextgp,
                                qpacket.gps,
                                next_cell,
                                localised,
                                next_mindices,
                            ),
                        )

        work_packets_done: Set[WorkPackets] = set()
        curr_len = -1
        while queue:
            # take the next gridded permutation of the queue, together with the
            # theoretical counts to create a gridded permutation containing
            # each of gps.
            qpacket = heappop(queue)
            # if gp was one of the initial_gps that satisfied obs/reqs, but
            # we weren't sure at the time if it was minimal, then now is the
            # time to check and yield
            if curr_len != len(qpacket.gp):
                new_len = len(qpacket.gp)
                initial_to_yield = chain.from_iterable(
                    initial_gps_to_auto_yield.pop(i, tuple())
                    for i in range(curr_len + 1, new_len + 2)
                )
                for gp in initial_to_yield:
                    if not yielded_subgridded_perm(gp):
                        yielded.add(gp)
                        yield gp
                curr_len = len(qpacket.gp)
            yield from _process_work_packet(qpacket, queue)
        # We yield any initial left after working on the work packet.
        # This happens in particular if you don't have any WP.
        initial_to_yield = chain.from_iterable(
            initial_gps_to_auto_yield.pop(i, tuple())
            for i in sorted(initial_gps_to_auto_yield)
        )
        for gp in initial_to_yield:
            if not yielded_subgridded_perm(gp):
                yielded.add(gp)
                yield gp

    # find_gridded_perm prunes only after this many packets: most searches end sooner.
    PACKETS_TAKEN_BEFORE_PRUNING = 8

    def find_gridded_perm(self) -> Optional[GriddedPerm]:
        """
        Return a gridded perm that avoids the obstructions and contains the
        requirements, or None if there is none. It need not be minimal or the
        shortest: an initial gridded perm that contains the requirements is
        returned at once, and so, with one requirement list, is its first
        requirement that avoids the obstructions.

        It takes the work packets of `minimal_gridded_perms`, made by the
        same rules, in another order, and stops at the first gridded perm that
        contains the requirements. `minimal_gridded_perms` takes the shortest
        packet first, so it builds every shorter gridded perm before it yields
        one: for a row of n cells, each with a point requirement, that is
        every one of the (n - 1)! orders of the points in the first n - 1
        cells that avoids the obstructions.

        Here a packet's bound is the length of its gridded perm, plus the
        points it lacks in each cell, and at least one: a gridded perm that
        contains the requirements has, in each cell, at least as many points
        as some requirement list asks of every gridded perm in it, so every
        gridded perm made from the packet is at least as long as its bound.
        The packet of least bound is taken first, and of those the longest,
        so that where each point inserted is one the packet lacks, as in that
        row, the search goes straight to a gridded perm; packets alike in both
        are taken as the heap leaves them, as in `minimal_gridded_perms`.
        While none is found, some packet on the heap has a shortest gridded
        perm made from it, of length L say, so no packet is taken whose bound
        is more than L, and none whose length is L or more.

        After the first `PACKETS_TAKEN_BEFORE_PRUNING` packets, a packet taken
        is dropped if no gridded perm made from it contains the requirements,
        and goes back on the heap if their patterns give it a higher bound,
        which is again a lower bound (`_points_lacking_by_patterns`).

        A packet's open cells are those that it, and the packets made from it,
        may still insert into: the cells not yet holding the most points its
        goal can need, and not before its last cell. A packet is skipped if
        one made before had its gridded perm, goal and last cell, and minimum
        indices no larger in each of its open cells. The last cell says
        whether a packet is still localising, as only the initial packets and
        those made by localising have the last cell (-1, -1), which is before
        every cell. The cells to try depend only on the gridded perm, the goal
        and the last cell, so whatever is made from the skipped packet is made
        from the earlier one, with minimum indices no larger again.
        `minimal_gridded_perms` skips such a packet whatever its minimum
        indices. So for every packet that `minimal_gridded_perms` takes, one
        with its gridded perm, goal and last cell that makes all it makes is
        taken here, or dropped, unless a gridded perm is found first, and this
        finds a gridded perm whenever `minimal_gridded_perms` yields one.
        """
        if not self.requirements:
            if GriddedPerm.empty_perm() in self.obstructions:
                return None
            return GriddedPerm.empty_perm()
        if len(self.requirements) == 1:
            return next(
                (
                    requirement
                    for requirement in self.requirements[0]
                    if requirement.avoids(*self.obstructions)
                ),
                None,
            )
        queue: List[QueuePacket] = []
        # An initial gridded perm that contains the requirements is yielded,
        # and the other initial packets are put on the queue.
        for initial_gridded_perm in self._prepare_queue(queue):
            return initial_gridded_perm
        return self._search_by_bound(queue)

    def _search_by_bound(self, packets: List[QueuePacket]) -> Optional[GriddedPerm]:
        """Take the packets, and those made from them, least bound first, and
        of those the longest, and return the first gridded perm made that
        avoids the obstructions and contains the requirements, or None."""
        points_needed = self._points_needed()
        heap = [
            self._heap_entry(packet, self._points_lacking(packet.gp, points_needed))
            for packet in packets
        ]
        heapify(heap)
        # For each gridded perm, goal and last cell made so far: None if the
        # gridded perm contains an obstruction, and otherwise the minimum
        # indices of the packets made with them that were kept. Whether a
        # gridded perm avoids the obstructions does not depend on the packet
        # it was made from, as that packet's own gridded perm avoids them. A
        # gridded perm made again does not contain the requirements, or it
        # would have been returned when it was first made.
        made_before: Dict[WorkPackets, Optional[List[Dict[Cell, int]]]] = {}
        for packet, points_lacking in self._packets_taken(heap):
            for cell, localised in self._get_cells_to_try(packet):
                found, next_packets = self._packets_made_in_cell(
                    packet, cell, localised, made_before
                )
                if found is not None:
                    return found
                # A point inserted into a cell that lacks points is one of them.
                next_points_lacking = points_lacking
                if packet.gp.pos.count(cell) < points_needed.get(cell, 0):
                    next_points_lacking -= 1
                for next_packet in next_packets:
                    heappush(heap, self._heap_entry(next_packet, next_points_lacking))
        return None

    def _packets_taken(
        self, heap: List[Tuple[int, int, QueuePacket, int, bool]]
    ) -> Iterator[Tuple[QueuePacket, int]]:
        """Pop the heap's packets in turn and yield each with the points it
        lacks, but drop or put back, as `find_gridded_perm` says, one popped
        after the first `PACKETS_TAKEN_BEFORE_PRUNING`."""
        packets_taken = 0
        while heap:
            bound, negative_length, packet, points_lacking, sharpened = heappop(heap)
            packets_taken += 1
            if not sharpened and packets_taken > self.PACKETS_TAKEN_BEFORE_PRUNING:
                points_lacking_by_patterns = self._points_lacking_by_patterns(packet)
                if points_lacking_by_patterns is None:
                    continue
                sharper_bound = -negative_length + max(1, points_lacking_by_patterns)
                if sharper_bound > bound:
                    heappush(
                        heap,
                        (sharper_bound, negative_length, packet, points_lacking, True),
                    )
                    continue
            yield packet, points_lacking

    @staticmethod
    def _heap_entry(
        packet: QueuePacket, points_lacking: int
    ) -> Tuple[int, int, QueuePacket, int, bool]:
        """The packet's bound, the negative of its length, the packet, the
        points it lacks and False (the bound not sharpened), in the order the
        heap compares them. Of two alike in bound and length neither is less,
        by `QueuePacket.__lt__`, so the heap leaves them in its own order."""
        length = len(packet.gp)
        return length + max(1, points_lacking), -length, packet, points_lacking, False

    def _packets_made_in_cell(
        self,
        packet: QueuePacket,
        cell: Cell,
        localised: bool,
        made_before: Dict[WorkPackets, Optional[List[Dict[Cell, int]]]],
    ) -> Tuple[Optional[GriddedPerm], List[QueuePacket]]:
        """Insert a point into cell of the packet's gridded perm in every way
        possible, and return a pair: a gridded perm so made that avoids the
        obstructions and contains the requirements, or None, and the packets
        made that are not skipped. Each gridded perm made is entered in
        made_before, with the packet's goal and the next last cell.

        It makes packets by the steps of `_process_work_packet` in
        `minimal_gridded_perms`, and differs in the packets it skips: keep the
        two in step."""
        # The `localised` bool tells us if we inserted into a cell as it
        # didn't contain the patterns in the cell. If not, then we update the
        # last cell, to ensure we only insert into greater or equal cells.
        next_cell = packet.last_cell if localised else cell
        next_packets: List[QueuePacket] = []
        # The open cells depend on the goal, the next last cell and the number
        # of points in each cell, which are the same for every point inserted
        # into cell, so they are worked out once, at the first gridded perm
        # made again.
        open_cells: Optional[Set[Cell]] = None
        # Insert a point in every way possible into cell, to the right of any
        # previously placed points in that cell.
        for index, next_gridded_perm in self.insert_point(
            packet.gp, cell, packet.mindices.get(cell, 0)
        ):
            packet_key = (next_gridded_perm, packet.gps, next_cell)
            if packet_key in made_before:
                minimum_indices_before = made_before[packet_key]
                # The gridded perm contains an obstruction.
                if minimum_indices_before is None:
                    continue
                next_minimum_indices = self._next_minimum_indices(
                    packet.mindices, cell, index
                )
                if open_cells is None:
                    open_cells = self._open_cells(
                        packet.gps, next_gridded_perm, next_cell
                    )
                # Skip the packet if one kept before has minimum indices no
                # larger in each open cell.
                if self._made_with_no_larger(
                    minimum_indices_before, next_minimum_indices, open_cells
                ):
                    continue
                minimum_indices_before.append(next_minimum_indices)
            else:
                # Only work with gridded permutations avoiding the
                # obstructions.
                if not self.satisfies_obstructions(
                    next_gridded_perm, must_contain=cell
                ):
                    made_before[packet_key] = None
                    continue
                # Update the next gridded perm about the patterns that are
                # contained in the gridded perm it was made from.
                self.known_patts[next_gridded_perm].update(self.known_patts[packet.gp])
                if self.satisfies_requirements(next_gridded_perm):
                    return next_gridded_perm, next_packets
                # Update the minimum index that we inserted a point into each
                # cell.
                next_minimum_indices = self._next_minimum_indices(
                    packet.mindices, cell, index
                )
                made_before[packet_key] = [next_minimum_indices]
            next_packets.append(
                QueuePacket(
                    next_gridded_perm,
                    packet.gps,
                    next_cell,
                    localised,
                    next_minimum_indices,
                )
            )
        return None, next_packets

    def _points_needed(self) -> Dict[Cell, int]:
        """For each cell, the most points that one requirement list asks of
        every gridded perm in it: every gridded perm that contains the
        requirements has at least that many points in the cell."""
        points_needed: Dict[Cell, int] = {}
        for requirement_list in self.requirements:
            if not requirement_list:
                continue
            cells_of_every_requirement = set(requirement_list[0].pos).intersection(
                *(requirement.pos for requirement in requirement_list[1:])
            )
            for cell in cells_of_every_requirement:
                points_needed[cell] = max(
                    points_needed.get(cell, 0),
                    min(
                        requirement.pos.count(cell) for requirement in requirement_list
                    ),
                )
        return points_needed

    @staticmethod
    def _points_lacking(
        gridded_perm: GriddedPerm, points_needed: Dict[Cell, int]
    ) -> int:
        """The points that the gridded perm lacks of those needed."""
        return sum(
            max(0, needed - gridded_perm.pos.count(cell))
            for cell, needed in points_needed.items()
        )

    def _points_lacking_by_patterns(self, packet: QueuePacket) -> Optional[int]:
        """The points that a gridded perm made from the packet lacks to
        contain the requirements, by their patterns in each cell, or None if
        none contains them. In each cell, the points of an occurrence of a
        requirement in such a gridded perm that come from the packet form a
        pattern of both the requirement's points there and the packet's, and
        the rest are new: so the new points there are at least the most, over
        the lists, of the least in a list of a requirement's points there less
        the most of them that form a pattern the packet's points there
        contain. Nothing made from the packet inserts into a cell that is not
        open (`_open_cells`), so in those cells an occurrence has no new
        points, and a requirement whose points in them, as a gridded perm, the
        packet's do not contain is left out of its list."""
        if not self.requirement_patterns:
            self.requirement_patterns = {
                requirement: self._cell_patterns(requirement)
                for requirement in chain.from_iterable(self.requirements)
            }
        open_cells = self._open_cells(packet.gps, packet.gp, packet.last_cell)
        packet_patterns = self._cell_patterns(packet.gp)
        most_lacking: Dict[Cell, int] = defaultdict(int)
        for requirement_list in self.requirements:
            lacking_in_list: List[Dict[Cell, int]] = []
            for requirement in requirement_list:
                lacking = {
                    cell: len(pattern)
                    - self._most_points_in_common(pattern, packet_patterns[cell])
                    for cell, pattern in self.requirement_patterns[requirement].items()
                }
                closed_cells = [cell for cell in lacking if cell not in open_cells]
                if not any(lacking[cell] for cell in closed_cells) and (
                    len(closed_cells) < 2
                    or packet.gp.get_gridded_perm_in_cells(closed_cells).contains(
                        requirement.get_gridded_perm_in_cells(closed_cells)
                    )
                ):
                    lacking_in_list.append(lacking)
            if not lacking_in_list:
                return None
            for cell in lacking_in_list[0]:
                least = min(lacking.get(cell, 0) for lacking in lacking_in_list)
                most_lacking[cell] = max(most_lacking[cell], least)
        return sum(most_lacking.values())

    @staticmethod
    def _cell_patterns(gridded_perm: GriddedPerm) -> Dict[Cell, Perm]:
        """The pattern of the gridded perm's points in each cell, empty if none."""
        values_in_cells: Dict[Cell, List[int]] = defaultdict(list)
        for value, cell in gridded_perm:
            values_in_cells[cell].append(value)
        cell_patterns: Dict[Cell, Perm] = defaultdict(Perm)
        for cell, values in values_in_cells.items():
            cell_patterns[cell] = Perm.to_standard(values)
        return cell_patterns

    def _most_points_in_common(self, pattern: Perm, perm: Perm) -> int:
        """The most points of the pattern that form a pattern the perm contains."""
        key = (pattern, perm)
        if key not in self.points_in_common:
            self.points_in_common[key] = next(
                size
                for size in range(min(len(pattern), len(perm)), -1, -1)
                if any(
                    perm.contains(Perm.to_standard(pattern[index] for index in indices))
                    for indices in combinations(range(len(pattern)), size)
                )
            )
        return self.points_in_common[key]

    def _open_cells(
        self, goal: GPTuple, gridded_perm: GriddedPerm, last_cell: Cell
    ) -> Set[Cell]:
        """The open cells of a packet with the goal, the gridded perm and the
        last cell: those that it, and the packets made from it, may still
        insert into, the cells not yet holding the most points the goal can
        need, and not before the last cell. They hold every cell that
        `_get_cells_to_try` may give the packet or one made from it, by its
        `can_insert` and its rule for the last cell, which the skipping in
        `_packets_made_in_cell` relies on."""
        return {
            cell
            for cell, most_points in self.get_max_cell_count(goal).items()
            if cell >= last_cell and gridded_perm.pos.count(cell) < most_points
        }

    @staticmethod
    def _made_with_no_larger(
        minimum_indices_before: List[Dict[Cell, int]],
        minimum_indices: Dict[Cell, int],
        open_cells: Set[Cell],
    ) -> bool:
        """Whether a packet was kept before with minimum indices no larger
        than these in each of the open cells. A cell missing from minimum
        indices has 0, and one in them at least 1."""
        return any(
            all(
                minimum_indices.get(open_cell, 0) >= minimum_index
                for open_cell, minimum_index in earlier_minimum_indices.items()
                if open_cell in open_cells
            )
            for earlier_minimum_indices in minimum_indices_before
        )

    @staticmethod
    def _next_minimum_indices(
        minimum_indices: Dict[Cell, int], cell: Cell, index: int
    ) -> Dict[Cell, int]:
        """The minimum indices of the packet made by inserting a point into
        cell at index, from a packet with the given minimum indices: a point
        goes into a cell to the right of the last point inserted into it."""
        next_minimum_indices = {
            other_cell: minimum_index if minimum_index <= index else minimum_index + 1
            for other_cell, minimum_index in minimum_indices.items()
            if other_cell != cell
        }
        next_minimum_indices[cell] = index + 1
        return next_minimum_indices

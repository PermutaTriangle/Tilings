from collections import Counter, defaultdict
from typing import (
    DefaultDict,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
)

from tilings.griddedperm import GriddedPerm

__all__ = ["GriddedPermSearch"]

Cell = Tuple[int, int]
Images = Tuple[int, ...]
ReqList = Tuple[GriddedPerm, ...]
# A state: its gridded perm; the requirement being placed in it, or None at a rest;
# the indices of the points of the gridded perm that the requirement's leftmost
# points went to; the indices of the lists the gridded perm is known to satisfy;
# and the index of the list being placed, or at a rest of the list last placed.
State = Tuple[GriddedPerm, Optional[GriddedPerm], Images, FrozenSet[int], int]
Placing = Tuple[GriddedPerm, GriddedPerm, Images]


class _OverBudget(Exception):
    """The first pass took all the states it may take."""


def _bounding_box(gp: GriddedPerm, cell: Cell) -> Tuple[int, int, int, int]:
    """Return the least and the most index, and the least and the most value, that
    a point inserted into the cell of gp can have. GriddedPerm.get_bounding_box
    gives the same, more slowly."""
    x, y = cell
    left = in_column = below = in_row = 0
    for column, row in gp.pos:
        if column < x:
            left += 1
        elif column == x:
            in_column += 1
        if row < y:
            below += 1
        elif row == y:
            in_row += 1
    return left, left + in_column, below, below + in_row


class GriddedPermSearch:
    """A search for a gridded perm on the tiling of the obstructions and requirement
    lists given: a gridded perm that avoids every obstruction and contains a gridded
    perm of each list. It looks for one, not for the minimal ones.

    A state is a gridded perm g that avoids the obstructions (a rest), or such a g
    with a requirement r being placed in it, and the points of g that r's first t
    points, from the left, went to. At a rest, the first list g does not satisfy is
    placed, each of its gridded perms in turn; a rest that satisfies every list is
    returned. Point t of r goes to a point of g in its cell, or to a new point
    inserted into g there, to the right of where r's point t - 1 went, above the
    points that r's points below it went to, and below those that r's points above
    it went to. If r is placed in full, the gridded perm is a rest again.

    If a gridded perm on the tiling contains the gridded perm of a state, and holds
    r with its first t points where g's went, then it contains the gridded perm of a
    child too, with r's first t + 1 points where the child's went: the point of the
    tiling's gridded perm that r's point t went to is a point of g, or g with that
    point inserted, which avoids the obstructions as the tiling's gridded perm does.
    So the search finds a gridded perm whenever there is one. The children of a
    state depend on the state alone, so a state made before is skipped, and nothing
    depends on the order in which states are taken.

    The search is depth first, a state's children made as they are taken, the points
    of g before new points. If the first pass has not finished after a few states,
    each pair of lists is searched alone, as the tiling has no gridded perm if a pair
    has none. Then the search starts again, dropping a rest that no gridded perm on
    the tiling contains: one with a list it does not satisfy that cannot be placed in
    it alone, or that needs, in each of its gridded perms, more points in a cell than
    the rest has there, where no point can be inserted into it.
    """

    # The states the first pass may take. Most tilings are decided within it, and
    # the look-aheads would cost them more than they save.
    _FIRST_PASS_STATES = 64

    def __init__(
        self,
        obstructions: Iterable[GriddedPerm],
        requirements: Iterable[Iterable[GriddedPerm]],
    ) -> None:
        self.obstructions = tuple(obstructions)
        # The lists whose gridded perms are each in one cell first, then those with
        # the longest gridded perms; in a list, its shortest gridded perm first.
        self.requirements: Tuple[ReqList, ...] = tuple(
            sorted(
                (tuple(sorted(reqlist, key=len)) for reqlist in requirements),
                key=lambda reqlist: (
                    not all(req.is_single_cell() for req in reqlist),
                    -max(map(len, reqlist), default=0),
                ),
            )
        )
        # The obstructions by the cells they use, for each cell they use.
        self._obstructions_by_cell: Optional[
            DefaultDict[Cell, List[Tuple[FrozenSet[Cell], List[GriddedPerm]]]]
        ] = None
        # The obstructions to check for a point inserted into a cell, by that cell
        # and the cells of the gridded perm it was inserted into.
        self._obstructions_to_check: Dict[
            Tuple[Cell, FrozenSet[Cell]], Tuple[GriddedPerm, ...]
        ] = {}
        # The number of points in each cell of each gridded perm of a list.
        self._cell_counts: Dict[ReqList, List[Counter]] = {}

    def find(self) -> Optional[GriddedPerm]:
        """Return a gridded perm on the tiling, or None if there is none. It need not
        be minimal."""
        if any(ob.is_empty() for ob in self.obstructions):
            return None
        return self._find(self.requirements)

    def _find(self, lists: Tuple[ReqList, ...]) -> Optional[GriddedPerm]:
        """A gridded perm that avoids the obstructions and contains a gridded perm of
        each of the lists given, or None: the first pass, then the pairs of lists,
        then the search with the look-aheads."""
        try:
            return self._search(lists, self._FIRST_PASS_STATES, look_ahead=False)
        except _OverBudget:
            pass
        if len(lists) > 2 and any(
            self._find((first, second)) is None
            for i, first in enumerate(lists)
            for second in lists[i + 1 :]
        ):
            return None
        return self._search(lists, None, look_ahead=True)

    def _search(
        self, lists: Tuple[ReqList, ...], budget: Optional[int], look_ahead: bool
    ) -> Optional[GriddedPerm]:
        """Search depth first from the empty gridded perm, with the look-aheads if
        look_ahead, and raise _OverBudget after budget states, if one is given."""
        rests_made: Set[GriddedPerm] = set()
        placings_made: Set[Placing] = set()
        start: State = (GriddedPerm.empty_perm(), None, (), frozenset(), -1)
        stack: List[Iterator[State]] = [iter((start,))]
        states = 0
        while stack:
            # The next state of the iterator on top, or the iterator is done. This
            # is faster than next() with a default.
            for gp, req, images, satisfied, index in stack[-1]:
                break
            else:
                stack.pop()
                continue
            states += 1
            if budget is not None and states > budget:
                raise _OverBudget
            if req is not None:
                stack.append(
                    self._unmade_children(
                        (gp, req, images), satisfied, index, rests_made, placings_made
                    )
                )
                continue
            if index >= 0:
                satisfied = satisfied | {index}
            unsatisfied, satisfied = self._unsatisfied(gp, satisfied, lists)
            if not unsatisfied:
                return gp
            if look_ahead and self._dropped(gp, [lists[i] for i in unsatisfied]):
                continue
            index = unsatisfied[0]
            stack.append(
                iter([(gp, first, (), satisfied, index) for first in lists[index]])
            )
        return None

    def _unmade_children(
        self,
        placing: Placing,
        satisfied: FrozenSet[int],
        index: int,
        rests_made: Set[GriddedPerm],
        placings_made: Set[Placing],
    ) -> Iterator[State]:
        """The children of a placing that were not made before: a rest when its
        requirement is placed in full, and otherwise a placing."""
        _, req, _ = placing
        for child, child_images in self._children(*placing):
            if len(child_images) == len(req):
                if child not in rests_made:
                    rests_made.add(child)
                    yield child, None, (), satisfied, index
            else:
                key = (child, req, child_images)
                if key not in placings_made:
                    placings_made.add(key)
                    yield child, req, child_images, satisfied, index

    def _children(
        self, gp: GriddedPerm, req: GriddedPerm, images: Images
    ) -> Iterator[Tuple[GriddedPerm, Images]]:
        """The gridded perm and the indices of the placed points after the next point
        of req is placed in gp: first at the points of gp it can go to, from left to
        right, then at the new points, by index and then by value."""
        cell, left, low, high = self._window(gp, req, images)
        patt, pos = gp.patt, gp.pos
        for idx in range(left + 1, len(patt)):
            if pos[idx] == cell and low < patt[idx] < high:
                yield gp, images + (idx,)
        for child, idx in self._new_points(gp, cell, left, low, high):
            yield child, images + (idx,)

    def _new_points(
        self, gp: GriddedPerm, cell: Cell, left: int, low: int, high: int
    ) -> Iterator[Tuple[GriddedPerm, int]]:
        """The gridded perms made by inserting a point into the cell of gp, right of
        the point at index left, and above the value low and below the value high,
        that avoid the obstructions, each with the new point's index. The points left
        of the new one keep their indices."""
        mindex, maxdex, minval, maxval = _bounding_box(gp, cell)
        cells = frozenset(gp.pos).union((cell,))
        for idx in range(max(mindex, left + 1), maxdex + 1):
            for val in range(max(minval, low + 1), min(maxval, high) + 1):
                child = gp.insert_specific_point(cell, idx, val)
                if self._avoids(child, cell, cells):
                    yield child, idx

    @staticmethod
    def _window(
        gp: GriddedPerm, req: GriddedPerm, images: Images
    ) -> Tuple[Cell, int, int, int]:
        """The cell of the next point of req, the index of the point of gp that the
        point before it went to (-1 if none did), and the values of the points that
        req's points below and above it went to (-1 and the length of gp if none)."""
        t = len(images)
        value = req.patt[t]
        low, high = -1, len(gp)
        for s in range(t):
            image_value = gp.patt[images[s]]
            if req.patt[s] < value:
                low = max(low, image_value)
            else:
                high = min(high, image_value)
        return req.pos[t], images[t - 1] if t else -1, low, high

    def _avoids(self, gp: GriddedPerm, cell: Cell, cells: FrozenSet[Cell]) -> bool:
        """Whether gp, whose cells are those given, avoids the obstructions, if gp
        less one of its points in the cell does. An occurrence of an obstruction
        that gp less the point avoids uses the cell, and no cell gp does not use."""
        obs = self._obstructions_to_check.get((cell, cells))
        if obs is None:
            if self._obstructions_by_cell is None:
                by_cells: DefaultDict[FrozenSet[Cell], List[GriddedPerm]] = defaultdict(
                    list
                )
                for ob in self.obstructions:
                    by_cells[frozenset(ob.pos)].append(ob)
                self._obstructions_by_cell = defaultdict(list)
                for ob_cells, group in by_cells.items():
                    for ob_cell in ob_cells:
                        self._obstructions_by_cell[ob_cell].append((ob_cells, group))
            obs = tuple(
                ob
                for ob_cells, group in self._obstructions_by_cell[cell]
                if ob_cells <= cells
                for ob in group
            )
            self._obstructions_to_check[(cell, cells)] = obs
        return not any(gp.contains_patt(ob) for ob in obs)

    @staticmethod
    def _unsatisfied(
        gp: GriddedPerm, satisfied: FrozenSet[int], lists: Tuple[ReqList, ...]
    ) -> Tuple[List[int], FrozenSet[int]]:
        """The indices of the lists gp does not satisfy, and of those it does."""
        unsatisfied = []
        for index, reqlist in enumerate(lists):
            if index in satisfied:
                continue
            if gp.contains(*reqlist):
                satisfied = satisfied | {index}
            else:
                unsatisfied.append(index)
        return unsatisfied, satisfied

    def _dropped(self, gp: GriddedPerm, unsatisfied: List[ReqList]) -> bool:
        """Whether no gridded perm on the tiling contains gp, by the look-aheads: a
        list gp does not satisfy needs more points in a cell than any gridded perm on
        the tiling containing gp can have there, or cannot be placed in gp alone."""
        return self._closed_out(gp, unsatisfied) or not all(
            self._can_place(gp, reqlist) for reqlist in unsatisfied
        )

    def _closed_out(self, gp: GriddedPerm, unsatisfied: List[ReqList]) -> bool:
        """Whether a list gp does not satisfy needs, in each of its gridded perms,
        more points in a cell than gp has there, in a cell where no point can be
        inserted into gp. A gridded perm on the tiling that contains gp, and a
        gridded perm of the list, has more points in that cell than gp has, so it
        contains gp with one of them, which is gp with a point inserted into the
        cell, and so it contains an obstruction."""
        counts = Counter(gp.pos)
        closed: Dict[Cell, bool] = {}
        for reqlist in unsatisfied:
            if reqlist not in self._cell_counts:
                self._cell_counts[reqlist] = [Counter(req.pos) for req in reqlist]
            for req_counts in self._cell_counts[reqlist]:
                for cell, number in req_counts.items():
                    if number > counts[cell]:
                        if cell not in closed:
                            closed[cell] = not self._takes_a_point(gp, cell)
                        if closed[cell]:
                            break
                else:
                    # This gridded perm of the list is not closed out.
                    break
            else:
                return True
        return False

    def _takes_a_point(self, gp: GriddedPerm, cell: Cell) -> bool:
        """Whether a point can be inserted into the cell of gp without making an
        occurrence of an obstruction: anywhere in the cell, as nothing is left of
        index -1, above the value -1 or below the value len(gp)."""
        return any(True for _ in self._new_points(gp, cell, -1, -1, len(gp)))

    def _can_place(self, gp: GriddedPerm, reqlist: ReqList) -> bool:
        """Whether a gridded perm of the list can be placed in gp: the search's
        placing of the list alone, without the other lists. A gridded perm on the
        tiling that contains gp contains such a placement, by the argument of the
        class's docstring."""
        made: Set[Placing] = set()
        stack: List[Iterator[Placing]] = [iter([(gp, req, ()) for req in reqlist])]
        while stack:
            for placing in stack[-1]:
                break
            else:
                stack.pop()
                continue
            _, req, images = placing
            if len(images) == len(req):
                return True
            stack.append(self._unmade_placings(placing, made))
        return False

    def _unmade_placings(
        self, placing: Placing, made: Set[Placing]
    ) -> Iterator[Placing]:
        """The children of a placing in _can_place that were not made before."""
        _, req, _ = placing
        for child, child_images in self._children(*placing):
            key = (child, req, child_images)
            if len(child_images) == len(req) or key not in made:
                made.add(key)
                yield key

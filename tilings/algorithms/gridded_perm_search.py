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
RequirementList = Tuple[GriddedPerm, ...]
# A state of a search: its gridded perm; the requirement being placed in it, or None
# at a rest; the indices of the points of the gridded perm that the requirement's
# leftmost points went to; the indices of the lists the gridded perm is known to
# satisfy; and the index of the list being placed, or at a rest of the list last
# placed.
State = Tuple[GriddedPerm, Optional[GriddedPerm], Images, FrozenSet[int], int]
Placing = Tuple[GriddedPerm, GriddedPerm, Images]


class _OverBudget(Exception):
    """A search took all the states it may take."""


def _bounding_box(gridded_perm: GriddedPerm, cell: Cell) -> Tuple[int, int, int, int]:
    """Return the least and the most index, and the least and the most value, that
    a point inserted into the cell of the gridded perm can have, as
    GriddedPerm.get_bounding_box does, counted from the positions alone."""
    x, y = cell
    left = in_column = below = in_row = 0
    for column, row in gridded_perm.pos:
        if column < x:
            left += 1
        elif column == x:
            in_column += 1
        if row < y:
            below += 1
        elif row == y:
            in_row += 1
    return left, left + in_column, below, below + in_row


def _combined(gridded_perms: Iterable[GriddedPerm]) -> GriddedPerm:
    """The gridded perm made of the points of the gridded perms given, whose cells
    are apart: in each column, the points of an earlier gridded perm are left of
    those of a later one, and in each row below them. Its points in the cells of one
    of the gridded perms given are that gridded perm."""
    points = []
    for number, gridded_perm in enumerate(gridded_perms):
        for index, (value, (column, row)) in enumerate(gridded_perm):
            points.append(((column, number, index), (row, number, value)))
    # By column, then by gridded perm, then by index in it.
    points.sort()
    by_value = sorted(range(len(points)), key=lambda point: points[point][1])
    patt = [0] * len(points)
    for value, point in enumerate(by_value):
        patt[point] = value
    return GriddedPerm(patt, ((column, row) for (column, _, _), (row, _, _) in points))


class GriddedPermSearch:
    """A search for one gridded perm on a tiling, given by its obstructions and
    requirement lists: a gridded perm that avoids every obstruction and contains a
    gridded perm of each list.

        GriddedPermSearch(obstructions, requirements).find()

    returns such a gridded perm, or None if there is none; Tiling.is_empty asks it
    whether there is one. MinimalGriddedPerms lists the minimal gridded perms of a
    tiling; this search stops at the first gridded perm it finds, of any length.
    Whether it finds one does not depend on the order of the obstructions or of the
    lists, but which one it finds can. Deciding whether a tiling has a gridded perm
    can take time exponential in the size of the tiling, and so can the search.

    The search
    ----------
    A rest is a gridded perm that avoids the obstructions. A rest that contains a
    gridded perm of each list is returned. Any other rest places the first list it
    does not satisfy: it has a placing for each gridded perm of that list.

    A placing is a rest gridded_perm, a requirement being placed in it, and images,
    the indices of the points of gridded_perm that the requirement's leftmost points
    went to. Its children place the requirement's next point, at a point of
    gridded_perm in that point's cell, or at a new point inserted into gridded_perm
    there, if that avoids the obstructions. The point goes right of the point that
    the requirement's point before it went to, above the points that the
    requirement's points below it went to, and below those that its points above it
    went to (_window). When the requirement is placed in full, the child is a rest.

    Why it finds a gridded perm when there is one
    ---------------------------------------------
    Let G be a gridded perm on the tiling. Say G holds a placing if G has an
    occurrence of its gridded_perm, and an occurrence of its requirement whose first
    len(images) points are the points of the first occurrence at images.

    - If G holds a placing, it holds one of its children. The point of G that the
      requirement's next point is at is the image of a point of gridded_perm, and so
      a child reuses that point; or it is not, and then G contains gridded_perm with
      that point inserted, which so avoids the obstructions, and is a child.
    - If G contains a rest that does not satisfy every list, G contains a gridded
      perm of the list the rest places, and so holds one of the rest's placings.
    - G contains the empty gridded perm, the first rest. So from it, the states G
      holds lead to a rest that satisfies every list.

    A state made before is skipped. That is right in whatever order the states are
    taken, as the children of a state depend on the state alone: on a rest's
    gridded perm, and on a placing's gridded perm, requirement and images. The other
    two things a state keeps, the lists its gridded perm is known to satisfy and the
    list it places, follow from these, as the order of the lists is fixed in a
    search.

    Making it fast
    --------------
    - The search is depth first, each state's children made as they are taken, the
      points of gridded_perm before new points.
    - The first pass takes at most _FIRST_PASS_STATES states, with no look-ahead.
    - If it does not finish, the lists are split into groups whose cells are apart
      and that no obstruction joins, each searched alone (_groups), and the
      gridded perms found for them put together (_combined).
    - The lists of a group are then searched again and again with the look-aheads,
      each search taking twice the states of the one before, until one finishes,
      which gives the answer. Each search starts afresh, and places first the
      lists that have met the most dead ends so far: a list that keeps failing late
      is so placed early, and what it rules out is then ruled out as the points of
      the other lists are placed.
    - The look-aheads drop a rest that no gridded perm on the tiling contains: one
      with a list it does not satisfy that cannot be placed in it alone, or that
      needs, in each of its gridded perms, more points in a cell than the rest has
      there, in a cell where no point can be inserted into the rest (_dropped).
    """

    # The states the first pass may take. Most tilings are decided within it, and
    # the look-aheads would cost them more than they save.
    _FIRST_PASS_STATES = 64

    def __init__(
        self,
        obstructions: Iterable[GriddedPerm],
        requirements: Iterable[Iterable[GriddedPerm]],
    ) -> None:
        # The lists in the order the search places them: those whose gridded perms
        # are each in one cell first, then those with the longest gridded perms; in
        # a list, its shortest gridded perm first.
        self.requirements: Tuple[RequirementList, ...] = tuple(
            sorted(
                (
                    tuple(sorted(requirement_list, key=len))
                    for requirement_list in requirements
                ),
                key=lambda requirement_list: (
                    not all(
                        requirement.is_single_cell() for requirement in requirement_list
                    ),
                    -max(map(len, requirement_list), default=0),
                ),
            )
        )
        self._obstructions = tuple(obstructions)
        # The sets of cells the obstructions use, and the obstructions by the cells
        # they use, for each cell they use.
        self._obstruction_cells: List[FrozenSet[Cell]] = []
        self._obstructions_by_cell: DefaultDict[
            Cell, List[Tuple[FrozenSet[Cell], List[GriddedPerm]]]
        ] = defaultdict(list)
        # Whether an obstruction is the empty perm, which every gridded perm contains.
        self._empty_obstruction = False
        self._group_obstructions()
        # The obstructions to check for a point inserted into a cell, by that cell
        # and the cells of the gridded perm it was inserted into.
        self._obstructions_to_check: Dict[
            Tuple[Cell, FrozenSet[Cell]], Tuple[GriddedPerm, ...]
        ] = {}
        # The number of points in each cell of each gridded perm of a list.
        self._cell_counts: Dict[RequirementList, List[Counter]] = {}
        # The dead ends each list has met: its placings whose next point could go
        # nowhere, and the rests the look-aheads dropped for it.
        self._dead_ends: Counter = Counter()

    def find(self) -> Optional[GriddedPerm]:
        """Return a gridded perm on the tiling, or None if there is none. It need not
        be minimal."""
        if self._empty_obstruction:
            return None
        # Each call starts afresh, so that it finds what the call before found.
        self._dead_ends.clear()
        return self._find(self.requirements)

    def _find(self, lists: Tuple[RequirementList, ...]) -> Optional[GriddedPerm]:
        """A gridded perm that avoids the obstructions and contains a gridded perm of
        each of the lists given, or None if there is none: the first pass; if it
        does not finish, each group of the lists alone; and for a group, searches
        with the look-aheads, the lists with the most dead ends first, each taking
        twice the states of the one before, until one finishes."""
        try:
            return self._search(lists, self._FIRST_PASS_STATES, look_ahead=False)
        except _OverBudget:
            pass
        groups = self._groups(lists)
        if len(groups) > 1:
            found = []
            for group in groups:
                gridded_perm = self._find(group)
                if gridded_perm is None:
                    return None
                found.append(gridded_perm)
            return _combined(found)
        budget = max(self._FIRST_PASS_STATES, 1)
        while True:
            budget *= 2
            # A stable sort: lists with as many dead ends keep their order.
            ordered = tuple(
                sorted(
                    lists,
                    key=lambda requirement_list: -self._dead_ends[requirement_list],
                )
            )
            try:
                return self._search(ordered, budget, look_ahead=True)
            except _OverBudget:
                pass

    def _search(
        self,
        lists: Tuple[RequirementList, ...],
        budget: Optional[int],
        look_ahead: bool,
        start: Optional[GriddedPerm] = None,
    ) -> Optional[GriddedPerm]:
        """Search depth first from the rest start, the empty gridded perm if None,
        placing the lists in their order, with the look-aheads if look_ahead. Return
        a gridded perm that avoids the obstructions and contains start and a gridded
        perm of each list, or None if there is none; raise _OverBudget after budget
        states, if a budget is given."""
        if start is None:
            start = GriddedPerm.empty_perm()
        rests_made: Set[GriddedPerm] = set()
        placings_made: Set[Placing] = set()
        stack: List[Iterator[State]] = [iter(((start, None, (), frozenset(), -1),))]
        states = 0
        while stack:
            # The next state of the iterator on top, or the iterator is done. This
            # is faster than next() with a default.
            for state in stack[-1]:
                break
            else:
                stack.pop()
                continue
            states += 1
            if budget is not None and states > budget:
                raise _OverBudget
            gridded_perm, requirement, _, satisfied, list_index = state
            if requirement is not None:
                stack.append(
                    self._unmade_children(state, lists, rests_made, placings_made)
                )
                continue
            if list_index >= 0:
                satisfied = satisfied | {list_index}
            unsatisfied, satisfied = self._unsatisfied(gridded_perm, satisfied, lists)
            if not unsatisfied:
                return gridded_perm
            if look_ahead and self._dropped(
                gridded_perm, [lists[i] for i in unsatisfied]
            ):
                continue
            # A placing of each gridded perm of the first list not satisfied.
            stack.append(
                iter(
                    [
                        (gridded_perm, requirement, (), satisfied, unsatisfied[0])
                        for requirement in lists[unsatisfied[0]]
                    ]
                )
            )
        return None

    def _unmade_children(
        self,
        state: State,
        lists: Tuple[RequirementList, ...],
        rests_made: Set[GriddedPerm],
        placings_made: Set[Placing],
    ) -> Iterator[State]:
        """The children of a placing that were not made before: a rest when its
        requirement is placed in full, and otherwise a placing. A placing with no
        child at all is a dead end of the list it places."""
        gridded_perm, requirement, images, satisfied, list_index = state
        assert requirement is not None
        dead_end = True
        for child, child_images in self._children(gridded_perm, requirement, images):
            dead_end = False
            if len(child_images) == len(requirement):
                if child not in rests_made:
                    rests_made.add(child)
                    yield child, None, (), satisfied, list_index
            else:
                # The requirement is part of the key: two gridded perms of a list
                # can place their first points alike and go on differently.
                key = (child, requirement, child_images)
                if key not in placings_made:
                    placings_made.add(key)
                    yield child, requirement, child_images, satisfied, list_index
        if dead_end:
            self._dead_ends[lists[list_index]] += 1

    def _children(
        self, gridded_perm: GriddedPerm, requirement: GriddedPerm, images: Images
    ) -> Iterator[Tuple[GriddedPerm, Images]]:
        """The gridded perm and the images of the placed points after the
        requirement's next point is placed in the gridded perm: first at the points
        it can go to, from left to right, then at new points, by index and then by
        value."""
        cell, index_left, value_below, value_above = self._window(
            gridded_perm, requirement, images
        )
        patt, pos = gridded_perm.patt, gridded_perm.pos
        for index in range(index_left + 1, len(patt)):
            if pos[index] == cell and value_below < patt[index] < value_above:
                yield gridded_perm, images + (index,)
        for child, index in self._new_points(
            gridded_perm, cell, index_left, value_below, value_above
        ):
            yield child, images + (index,)

    def _new_points(
        self,
        gridded_perm: GriddedPerm,
        cell: Cell,
        index_left: int,
        value_below: int,
        value_above: int,
    ) -> Iterator[Tuple[GriddedPerm, int]]:
        """The gridded perms made by inserting a point into the cell of the gridded
        perm, right of the point at index_left, and above the point with value
        value_below and below the point with value value_above, that avoid the
        obstructions, each with the new point's index. The points left of the new one
        keep their indices. A point inserted at value value_above goes below the
        point that had that value, as insert_specific_point moves it up."""
        least_index, most_index, least_value, most_value = _bounding_box(
            gridded_perm, cell
        )
        cells = frozenset(gridded_perm.pos).union((cell,))
        for index in range(max(least_index, index_left + 1), most_index + 1):
            for value in range(
                max(least_value, value_below + 1), min(most_value, value_above) + 1
            ):
                child = gridded_perm.insert_specific_point(cell, index, value)
                if self._avoids(child, cell, cells):
                    yield child, index

    @staticmethod
    def _window(
        gridded_perm: GriddedPerm, requirement: GriddedPerm, images: Images
    ) -> Tuple[Cell, int, int, int]:
        """The cell of the requirement's next point; the index of the point of the
        gridded perm that the requirement's point before it went to, or -1; and the
        values of the points that the requirement's points below and above it went
        to, the nearest of each, or -1 and the length of the gridded perm if none
        did."""
        placed = len(images)
        value = requirement.patt[placed]
        value_below, value_above = -1, len(gridded_perm)
        for earlier, image in enumerate(images):
            image_value = gridded_perm.patt[image]
            if requirement.patt[earlier] < value:
                value_below = max(value_below, image_value)
            else:
                value_above = min(value_above, image_value)
        index_left = images[-1] if images else -1
        return (requirement.pos[placed], index_left, value_below, value_above)

    def _avoids(
        self, gridded_perm: GriddedPerm, cell: Cell, cells: FrozenSet[Cell]
    ) -> bool:
        """Whether the gridded perm, whose cells are those given, avoids the
        obstructions, when it does with one of its points in the cell taken out. An
        occurrence of an obstruction that uses that point is of an obstruction that
        uses the cell, and no cell the gridded perm does not."""
        obstructions = self._obstructions_to_check.get((cell, cells))
        if obstructions is None:
            obstructions = tuple(
                obstruction
                for obstruction_cells, group in self._obstructions_by_cell[cell]
                if obstruction_cells <= cells
                for obstruction in group
            )
            self._obstructions_to_check[(cell, cells)] = obstructions
        for obstruction in obstructions:
            if gridded_perm.contains_patt(obstruction):
                return False
        return True

    def _group_obstructions(self) -> None:
        """Group the obstructions by the cells they use, for each cell they use, and
        note whether one is the empty perm."""
        by_cells: DefaultDict[FrozenSet[Cell], List[GriddedPerm]] = defaultdict(list)
        for obstruction in self._obstructions:
            # A gridded perm keeps the set of its cells, and a set keeps its hash.
            # On tilings of about a thousand obstructions, making a set of each
            # obstruction's cells, or grouping them by their positions, made a
            # call about 1.8 times as long.
            obstruction_cells = obstruction._cells  # pylint: disable=protected-access
            by_cells[obstruction_cells].append(obstruction)
        self._obstruction_cells = list(by_cells)
        self._empty_obstruction = frozenset() in by_cells
        for obstruction_cells, group in by_cells.items():
            for cell in obstruction_cells:
                self._obstructions_by_cell[cell].append((obstruction_cells, group))

    def _groups(
        self, lists: Tuple[RequirementList, ...]
    ) -> List[Tuple[RequirementList, ...]]:
        """The lists in groups, two lists in one group if their cells meet, or an
        obstruction uses cells of both. A gridded perm found for one group has its
        points in that group's cells. Gridded perms found for each, put together by
        _combined, give a gridded perm that avoids the obstructions, as an
        occurrence of an obstruction is in the cells of one group alone, and so in
        that group's gridded perm. So the lists have a gridded perm if and only if
        each group does."""
        # A union-find of the lists' indices.
        parents = list(range(len(lists)))

        def root(i: int) -> int:
            while parents[i] != i:
                parents[i] = parents[parents[i]]
                i = parents[i]
            return i

        owners: Dict[Cell, int] = {}
        for i, requirement_list in enumerate(lists):
            for requirement in requirement_list:
                for cell in requirement.pos:
                    parents[root(owners.setdefault(cell, i))] = root(i)
        for obstruction_cells in self._obstruction_cells:
            joined = [owners[cell] for cell in obstruction_cells if cell in owners]
            for i in joined[1:]:
                parents[root(i)] = root(joined[0])
        groups: DefaultDict[int, List[RequirementList]] = defaultdict(list)
        for i, requirement_list in enumerate(lists):
            groups[root(i)].append(requirement_list)
        return [tuple(group) for group in groups.values()]

    @staticmethod
    def _unsatisfied(
        gridded_perm: GriddedPerm,
        satisfied: FrozenSet[int],
        lists: Tuple[RequirementList, ...],
    ) -> Tuple[List[int], FrozenSet[int]]:
        """The indices of the lists the gridded perm does not satisfy, and of those
        it does."""
        unsatisfied = []
        for list_index, requirement_list in enumerate(lists):
            if list_index in satisfied:
                continue
            if gridded_perm.contains(*requirement_list):
                satisfied = satisfied | {list_index}
            else:
                unsatisfied.append(list_index)
        return unsatisfied, satisfied

    def _dropped(
        self, gridded_perm: GriddedPerm, unsatisfied_lists: List[RequirementList]
    ) -> bool:
        """Whether the look-aheads find a list the gridded perm does not satisfy
        that no gridded perm on the tiling containing it satisfies, which so meets a
        dead end: a list that needs more points in a cell than any such gridded perm
        has there (_closed_out), or that cannot be placed in the gridded perm alone.
        A gridded perm on the tiling that contains it contains such a placing, by
        the class's argument with that list only."""
        dropped_for = self._closed_out(gridded_perm, unsatisfied_lists)
        if dropped_for is None:
            dropped_for = next(
                (
                    requirement_list
                    for requirement_list in unsatisfied_lists
                    if not self._can_place(gridded_perm, requirement_list)
                ),
                None,
            )
        if dropped_for is None:
            return False
        self._dead_ends[dropped_for] += 1
        return True

    def _can_place(
        self, gridded_perm: GriddedPerm, requirement_list: RequirementList
    ) -> bool:
        """Whether a gridded perm of the list can be placed in the gridded perm."""
        return (
            self._search((requirement_list,), None, False, start=gridded_perm)
            is not None
        )

    def _closed_out(
        self, gridded_perm: GriddedPerm, unsatisfied_lists: List[RequirementList]
    ) -> Optional[RequirementList]:
        """The first list the gridded perm does not satisfy each of whose gridded
        perms needs more points in some cell than the gridded perm has there, in a
        cell where no point can be inserted into the gridded perm; or None. A gridded
        perm on the tiling that contains the gridded perm, and more points in such a
        cell, contains it with one of those points too, which is the gridded perm
        with a point inserted into the cell, and so it contains an obstruction."""
        counts = Counter(gridded_perm.pos)
        closed: Dict[Cell, bool] = {}
        for requirement_list in unsatisfied_lists:
            if requirement_list not in self._cell_counts:
                self._cell_counts[requirement_list] = [
                    Counter(requirement.pos) for requirement in requirement_list
                ]
            if all(
                self._needs_a_closed_cell(
                    gridded_perm, counts, requirement_counts, closed
                )
                for requirement_counts in self._cell_counts[requirement_list]
            ):
                return requirement_list
        return None

    def _needs_a_closed_cell(
        self,
        gridded_perm: GriddedPerm,
        counts: Counter,
        requirement_counts: Counter,
        closed: Dict[Cell, bool],
    ) -> bool:
        """Whether a gridded perm of a list, with requirement_counts points in each
        cell, needs more points in a cell than the gridded perm, with counts points
        in each, has there, in a cell where no point can be inserted into the gridded
        perm. Whether a cell is closed so is kept in closed."""
        for cell, number in requirement_counts.items():
            if number > counts[cell]:
                if cell not in closed:
                    closed[cell] = not self._takes_a_point(gridded_perm, cell)
                if closed[cell]:
                    return True
        return False

    def _takes_a_point(self, gridded_perm: GriddedPerm, cell: Cell) -> bool:
        """Whether a point can be inserted into the cell of the gridded perm without
        making an occurrence of an obstruction: anywhere in the cell, as nothing is
        left of index -1, above the value -1 or below the value len(gridded_perm)."""
        return any(
            True
            for _ in self._new_points(gridded_perm, cell, -1, -1, len(gridded_perm))
        )

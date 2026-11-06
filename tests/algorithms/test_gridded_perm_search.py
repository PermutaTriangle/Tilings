"""Tests of GriddedPermSearch. Many read or patch its private parts: the dead ends,
the searches it makes with their budgets and look-aheads, the states it takes and
the obstructions it checks. Those pin how the search works, and not only what it
finds, so a change to how it works may need them changed with it."""

import random
from itertools import combinations, combinations_with_replacement, permutations, product

import pytest

from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import GriddedPermSearch
from tilings.algorithms.gridded_perm_search import _bounding_box, _combined, _OverBudget

# A loop that never ends fails its test, rather than holding up the run.
pytestmark = pytest.mark.timeout(10)

A, B, C = (0, 0), (1, 0), (2, 0)


def is_gridded_perm_on(gridded_perm, obstructions, requirements):
    """Whether gridded_perm is a gridded perm whose points fit their cells, that
    avoids the obstructions and contains a gridded perm of each list."""
    return (
        gridded_perm is not None
        and not gridded_perm.contradictory()
        and gridded_perm.avoids(*obstructions)
        and all(
            gridded_perm.contains(*requirement_list)
            for requirement_list in requirements
        )
    )


def gridded_perms_on_a_grid(length, columns, rows):
    """Every gridded perm of the given length on a grid of the given numbers of
    columns and rows."""
    columns_of_indices = list(combinations_with_replacement(range(columns), length))
    rows_of_values = list(combinations_with_replacement(range(rows), length))
    for patt in Perm.of_length(length):
        for column_of_index in columns_of_indices:
            for row_of_value in rows_of_values:
                yield GriddedPerm(
                    patt,
                    tuple(
                        (column_of_index[index], row_of_value[value])
                        for index, value in enumerate(patt)
                    ),
                )


def has_gridded_perm_by_brute_force(obstructions, requirements, columns, rows):
    """Whether a gridded perm on the grid avoids the obstructions and contains a
    gridded perm of each list. A minimal one is a union of a gridded perm of each
    list, so it is no longer than the longest of each list together."""
    longest = sum(
        max(map(len, requirement_list), default=0) for requirement_list in requirements
    )
    return any(
        is_gridded_perm_on(gridded_perm, obstructions, requirements)
        for length in range(longest + 1)
        for gridded_perm in gridded_perms_on_a_grid(length, columns, rows)
    )


def random_gridded_perm(rng, length, columns, rows):
    patt = list(range(length))
    rng.shuffle(patt)
    column_of_index = sorted(rng.randrange(columns) for _ in range(length))
    row_of_value = sorted(rng.randrange(rows) for _ in range(length))
    return GriddedPerm(
        patt,
        tuple(
            (column_of_index[index], row_of_value[value])
            for index, value in enumerate(patt)
        ),
    )


def small_tilings(seed, count):
    """Obstructions, requirement lists and the grid of random small tilings, two or
    three lists of one or two gridded perms of one to three points, no more than
    five points in a minimal gridded perm, and up to three obstructions of two or
    three points."""
    rng = random.Random(seed)
    made = 0
    while made < count:
        columns, rows = rng.choice([(1, 1), (2, 1), (1, 2), (2, 2), (3, 1)])
        obstructions = tuple(
            random_gridded_perm(rng, rng.randint(2, 3), columns, rows)
            for _ in range(rng.randint(0, 3))
        )
        requirements = tuple(
            tuple(
                random_gridded_perm(rng, rng.randint(1, 3), columns, rows)
                for _ in range(rng.randint(1, 2))
            )
            for _ in range(rng.randint(2, 3))
        )
        if (
            sum(max(map(len, requirement_list)) for requirement_list in requirements)
            <= 5
        ):
            made += 1
            yield obstructions, requirements, columns, rows


def searches_recorded(monkeypatch):
    """The lists, budget and look-ahead of each search that GriddedPermSearch makes
    from here on, but for those of _can_place, which start from a rest."""
    searched = []
    original = GriddedPermSearch._search

    def search_recorded(self, lists, budget, look_ahead, start=None):
        if start is None:
            searched.append((lists, budget, look_ahead))
        return original(self, lists, budget, look_ahead, start)

    monkeypatch.setattr(GriddedPermSearch, "_search", search_recorded)
    return searched


def outcomes_recorded(monkeypatch):
    """The lists, budget and look-ahead of each search that GriddedPermSearch makes
    from here on, but for those of _can_place, each with how it ended: the gridded
    perm it found, None, or "over budget"."""
    outcomes = []
    original = GriddedPermSearch._search

    def search_recorded(self, lists, budget, look_ahead, start=None):
        if start is not None:
            return original(self, lists, budget, look_ahead, start)
        try:
            found = original(self, lists, budget, look_ahead, start)
        except _OverBudget:
            outcomes.append((lists, budget, look_ahead, "over budget"))
            raise
        outcomes.append((lists, budget, look_ahead, found))
        return found

    monkeypatch.setattr(GriddedPermSearch, "_search", search_recorded)
    return outcomes


@pytest.mark.parametrize("first_pass_states", [64, 0])
def test_find_against_a_brute_force(first_pass_states, monkeypatch):
    """With the first pass as it is, and with none, so that every tiling is also
    split into groups and searched with the restarts and the look-aheads; with the
    lists, and the gridded perms in each, in the search's order and reversed."""
    monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", first_pass_states)
    empty = 0
    for obstructions, requirements, columns, rows in small_tilings(1, 60):
        expected = has_gridded_perm_by_brute_force(
            obstructions, requirements, columns, rows
        )
        empty += not expected
        search = GriddedPermSearch(obstructions, requirements)
        for lists in (
            search.requirements,
            tuple(
                tuple(reversed(requirement_list))
                for requirement_list in reversed(search.requirements)
            ),
        ):
            search = GriddedPermSearch(obstructions, requirements)
            search.requirements = lists
            found = search.find()
            assert (found is not None) == expected, (obstructions, lists)
            if found is not None:
                assert is_gridded_perm_on(found, obstructions, requirements)
        assert Tiling(obstructions, requirements).is_empty() == (not expected)
    assert 0 < empty < 60


def test_find_every_order_of_the_lists():
    """Two cells in a row, four lists, and a gridded perm of eight points: each of
    the 24 orders of the lists finds one."""
    obstructions = (
        GriddedPerm((0, 1, 2), (A, B, B)),
        GriddedPerm((2, 1, 0), (B, B, B)),
    )
    requirements = (
        (GriddedPerm((1, 0, 2), (A, A, B)), GriddedPerm((0, 1), (B, B))),
        (GriddedPerm((2, 0, 1), (A, A, A)),),
        (GriddedPerm((1, 2, 0), (A, B, B)),),
        (GriddedPerm((0, 2, 1), (A, A, B)), GriddedPerm((1, 0), (A, B))),
    )
    for lists in permutations(requirements):
        search = GriddedPermSearch(obstructions, requirements)
        search.requirements = lists
        assert is_gridded_perm_on(search.find(), obstructions, requirements)


def orders_in_a_row(length):
    cells = tuple((column, 0) for column in range(length))
    return cells, [GriddedPerm(patt, cells) for patt in Perm.of_length(length)]


def orders_in_a_column(length):
    cells = tuple((0, row) for row in range(length))
    return cells, [
        GriddedPerm(patt, tuple(cells[value] for value in patt))
        for patt in Perm.of_length(length)
    ]


@pytest.mark.parametrize("orders", [orders_in_a_row, orders_in_a_column])
def test_find_every_order_but_one(orders):
    """A point in each of four cells, in a row or in a column, and every order of
    the points but one an obstruction: that order is the only gridded perm."""
    cells, every_order = orders(4)
    points = tuple((GriddedPerm.point_perm(cell),) for cell in cells)
    for allowed in every_order:
        obstructions = tuple(order for order in every_order if order != allowed)
        assert GriddedPermSearch(obstructions, points).find() == allowed
    assert GriddedPermSearch(tuple(every_order), points).find() is None


def test_find_a_column_of_two_cells():
    """A column of two cells, with a cell right of the upper one, whose lists put
    points of the two cells of the column in turn from left to right."""
    obstructions = (GriddedPerm((1, 0, 2), ((0, 1), (0, 0), (1, 1))),)
    requirements = (
        (GriddedPerm((0, 2, 1), ((0, 0), (0, 1), (0, 0))),),
        (GriddedPerm((1, 0, 2), ((0, 1), (0, 1), (1, 1))),),
        (GriddedPerm((1, 0), ((0, 0), (0, 0))),),
    )
    gridded_perm = GriddedPermSearch(obstructions, requirements).find()
    assert is_gridded_perm_on(gridded_perm, obstructions, requirements)


# A point in (0, 0) or 01 in (1, 1), and a point in (0, 1), which shares a column
# with the first and a row with the second.
POINT_OR_INCREASING = (
    (GriddedPerm.point_perm((0, 0)), GriddedPerm((0, 1), ((1, 1), (1, 1)))),
    (GriddedPerm.point_perm((0, 1)),),
)
# Every gridded perm with points in both (0, 0) and (0, 1) contains one of these.
NOT_BOTH_IN_THE_COLUMN = (
    GriddedPerm((0, 1), ((0, 0), (0, 1))),
    GriddedPerm((1, 0), ((0, 1), (0, 0))),
)
# Every gridded perm with points in both (0, 1) and (1, 1) contains one of these.
NOT_BOTH_IN_THE_ROW = (
    GriddedPerm((0, 1), ((0, 1), (1, 1))),
    GriddedPerm((1, 0), ((0, 1), (1, 1))),
)


def test_find_the_second_gridded_perm_of_a_list():
    """The first gridded perm of the first list cannot be placed with the second
    list; the second one can."""
    assert is_gridded_perm_on(
        GriddedPermSearch((), POINT_OR_INCREASING).find(), (), POINT_OR_INCREASING
    )
    gridded_perm = GriddedPermSearch(NOT_BOTH_IN_THE_COLUMN, POINT_OR_INCREASING).find()
    assert is_gridded_perm_on(gridded_perm, NOT_BOTH_IN_THE_COLUMN, POINT_OR_INCREASING)
    assert gridded_perm.contains(GriddedPerm((0, 1), ((1, 1), (1, 1))))
    obstructions = NOT_BOTH_IN_THE_COLUMN + NOT_BOTH_IN_THE_ROW
    assert GriddedPermSearch(obstructions, POINT_OR_INCREASING).find() is None
    assert Tiling(obstructions, POINT_OR_INCREASING).is_empty()


def test_find_a_list_whose_gridded_perms_start_alike():
    """One cell avoiding 01 and 102: a point, and 210 or 01. The search places 01
    first, as the shorter, and 01 cannot go; 210 begins as 01 does, with a point
    at the same image, and its placings must not be taken as made before."""
    obstructions = (GriddedPerm((0, 1), (A, A)), GriddedPerm((1, 0, 2), (A, A, A)))
    decreasing = GriddedPerm((2, 1, 0), (A, A, A))
    requirements = (
        (GriddedPerm.point_perm(A),),
        (decreasing, GriddedPerm((0, 1), (A, A))),
    )
    assert GriddedPermSearch(obstructions, requirements).find() == decreasing


def test_find_a_point_of_the_gridded_perm_used_twice():
    """One cell avoiding 102 and 3201 and containing 01 and 210: placing 210 and
    then 01 at a point of it, at its 2 with a new point above, gives 2310, as the
    points of a gridded perm are tried before new points."""
    obstructions = (
        GriddedPerm((1, 0, 2), (A,) * 3),
        GriddedPerm((3, 2, 0, 1), (A,) * 4),
    )
    requirements = (
        (GriddedPerm((0, 1), (A,) * 2),),
        (GriddedPerm((2, 1, 0), (A,) * 3),),
    )
    assert GriddedPermSearch(obstructions, requirements).find() == GriddedPerm(
        (2, 3, 1, 0), (A,) * 4
    )


def test_find_none():
    point = GriddedPerm.point_perm(A)
    increasing = GriddedPerm((0, 1), (A, A))
    # An empty list.
    assert GriddedPermSearch((), ((), (point,))).find() is None
    assert GriddedPermSearch((), ((point,), ())).find() is None
    # The empty perm as an obstruction.
    requirements = ((point,), (GriddedPerm.point_perm((1, 1)),))
    assert GriddedPermSearch((), requirements).find() is not None
    assert GriddedPermSearch((GriddedPerm.empty_perm(),), requirements).find() is None
    assert GriddedPermSearch((GriddedPerm.empty_perm(),), ()).find() is None
    # A list whose one gridded perm contains an obstruction.
    assert GriddedPermSearch((point,), ((increasing,),)).find() is None
    assert (
        GriddedPermSearch(
            (point,), ((increasing,), (GriddedPerm.point_perm(B),))
        ).find()
        is None
    )
    # A gridded perm whose points cannot be in their cells.
    contradictory = GriddedPerm((0, 1), (B, A))
    assert GriddedPermSearch((), ((contradictory,), (point,))).find() is None


def test_find_one_list_or_none():
    decreasing = GriddedPerm((1, 0), (B, B))
    empty_cell = GriddedPerm.point_perm(A)
    increasing = GriddedPerm((0, 1), (A, A))
    assert GriddedPermSearch((empty_cell,), ((increasing, decreasing),)).find() == (
        decreasing
    )
    assert GriddedPermSearch((), ()).find() == GriddedPerm.empty_perm()
    assert GriddedPermSearch((), ((GriddedPerm.empty_perm(), increasing),)).find() == (
        GriddedPerm.empty_perm()
    )


def test_find_in_a_cell_no_list_needs_in_full():
    """A column of three cells: 01 in the bottom cell or 01 in the top cell, and
    012 in the middle cell."""
    requirements = (
        (
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 2), (0, 2))),
        ),
        (GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 1))),),
    )
    assert is_gridded_perm_on(
        GriddedPermSearch((), requirements).find(), (), requirements
    )


def test_find_twice_on_one_search():
    """Each call starts afresh: the second finds what the first found, after the
    same dead ends."""
    obstructions, requirements = three_lists_that_cannot_all_hold(8, joined=True)
    obstructions = obstructions[1:]
    search = GriddedPermSearch(obstructions, requirements)
    found = search.find()
    dead_ends = dict(search._dead_ends)
    assert dead_ends and is_gridded_perm_on(found, obstructions, requirements)
    assert search.find() == found
    assert search._dead_ends == dead_ends


def test_search_makes_a_rest_and_a_placing_once(monkeypatch):
    """The cell holds a point before 012 is placed in it, so a rest and placings
    are reached in more than one way; a point in C is an obstruction, so the search
    makes every state. It looks at each rest once and expands each placing once."""
    point = GriddedPerm.point_perm
    lists = ((point(A),), (GriddedPerm((0, 1, 2), (A,) * 3),), (point(C),))
    search = GriddedPermSearch((point(C),), lists)
    rests, expanded = [], []
    unsatisfied, children = GriddedPermSearch._unsatisfied, GriddedPermSearch._children

    def unsatisfied_recorded(gridded_perm, satisfied, lists):
        rests.append(gridded_perm)
        return unsatisfied(gridded_perm, satisfied, lists)

    def children_recorded(self, gridded_perm, requirement, images):
        expanded.append((gridded_perm, requirement, images))
        return children(self, gridded_perm, requirement, images)

    monkeypatch.setattr(
        GriddedPermSearch, "_unsatisfied", staticmethod(unsatisfied_recorded)
    )
    monkeypatch.setattr(GriddedPermSearch, "_children", children_recorded)
    assert search._search(lists, None, look_ahead=False) is None
    assert len(rests) == len(set(rests)) > 1
    assert len(expanded) == len(set(expanded)) > 1


def test_can_place_makes_a_placing_once(monkeypatch):
    """Placing 012 in a gridded perm with a point, 012 an obstruction: 01 is made
    in two ways, with the point as its 0 or as its 1."""
    increasing = GriddedPerm((0, 1, 2), (A,) * 3)
    search = GriddedPermSearch((increasing,), ((increasing,),))
    expanded = []
    children = GriddedPermSearch._children

    def children_recorded(self, gridded_perm, requirement, images):
        expanded.append((gridded_perm, requirement, images))
        return children(self, gridded_perm, requirement, images)

    monkeypatch.setattr(GriddedPermSearch, "_children", children_recorded)
    assert not search._can_place(GriddedPerm.point_perm(A), (increasing,))
    assert len(expanded) == len(set(expanded)) > 1


def test_search_counts_its_states():
    """The first rest, the placing of A, the rest with A, the placing of B, and the
    rest with both."""
    in_a, in_b = (GriddedPerm.point_perm(A),), (GriddedPerm.point_perm(B),)
    search = GriddedPermSearch((), (in_a, in_b))
    assert search._search(search.requirements, 5, look_ahead=False) is not None
    with pytest.raises(_OverBudget):
        search._search(search.requirements, 4, look_ahead=False)


def test_avoids_keeps_the_obstructions_to_check():
    inside = GriddedPerm((0, 1), (A, B))
    outside = GriddedPerm((0, 1), (A, C))
    search = GriddedPermSearch((inside, outside), ())
    cells = frozenset((A, B))
    assert not search._avoids(inside, B, cells)
    kept = search._obstructions_to_check[(B, cells)]
    # Not an obstruction that uses a cell the gridded perm does not.
    assert kept == (inside,)
    assert not search._avoids(inside, B, cells)
    assert search._obstructions_to_check[(B, cells)] is kept


def test_unsatisfied_returns_the_lists_it_checked():
    lists = tuple((GriddedPerm.point_perm(cell),) for cell in (A, B, C))
    gridded_perm = GriddedPerm((0, 1), (A, B))
    assert GriddedPermSearch._unsatisfied(gridded_perm, frozenset(), lists) == (
        [2],
        frozenset({0, 1}),
    )
    assert GriddedPermSearch._unsatisfied(gridded_perm, frozenset({0}), lists) == (
        [2],
        frozenset({0, 1}),
    )


def test_search_remembers_the_lists_a_rest_satisfies(monkeypatch):
    seen, original = [], GriddedPermSearch._unsatisfied

    def recorded(gridded_perm, satisfied, lists):
        seen.append(satisfied)
        return original(gridded_perm, satisfied, lists)

    monkeypatch.setattr(GriddedPermSearch, "_unsatisfied", staticmethod(recorded))
    lists = ((GriddedPerm.point_perm(A),), (GriddedPerm.point_perm(B),))
    assert GriddedPermSearch((), lists).find() is not None
    assert seen == [frozenset(), frozenset({0}), frozenset({0, 1})]


def test_the_lists_and_each_list_are_sorted():
    point = GriddedPerm.point_perm(A)
    decreasing = GriddedPerm((1, 0), (A, A))
    increasing = GriddedPerm((0, 1, 2), (A,) * 3)
    across, longer_across = GriddedPerm((0, 1), (A, B)), GriddedPerm(
        (0, 1, 2), (A, B, B)
    )
    search = GriddedPermSearch(
        (), ((across,), (point,), (longer_across,), (increasing, decreasing))
    )
    assert search.requirements == (
        (decreasing, increasing),
        (point,),
        (longer_across,),
        (across,),
    )


def test_each_list_is_sorted_by_length_alone():
    """GriddedPerm's own order puts the shorter first, so only gridded perms of one
    length tell a sort by length from a sort by that order."""
    first = GriddedPerm((1, 0), (C, C))
    second = GriddedPerm((0, 1), (A, A))
    longer = GriddedPerm((0, 1, 2), (A, A, A))
    search = GriddedPermSearch([], [[longer, first, second]])
    assert search.requirements == ((first, second, longer),)


def test_bounding_box_is_get_bounding_box():
    rng = random.Random(0)
    for _ in range(200):
        gridded_perm = random_gridded_perm(rng, rng.randint(0, 6), 3, 3)
        for cell in product(range(4), range(4)):
            assert _bounding_box(gridded_perm, cell) == gridded_perm.get_bounding_box(
                cell
            )


# The cells (0, 0) and (1, 0) cannot both hold a point, and the first list needs a
# point in one, the last in the other: each list can be placed alone, but these two
# lists together cannot, and the first pass, which places the lists in turn, fails
# only at the last list, for each way of placing the two between them.
TWO_CELLS_NOT_BOTH = (
    (
        GriddedPerm((0, 1), (A, B)),
        GriddedPerm((1, 0), (A, B)),
        GriddedPerm((1, 3, 2, 0), (A, A, C, C)),
    ),
    (
        (GriddedPerm((1, 0), (A, C)),),
        (GriddedPerm((1, 0), (C, C)),),
        (GriddedPerm((2, 1, 0), (C, C, C)), GriddedPerm((3, 1, 0, 2), (B, B, C, C))),
        (GriddedPerm((1, 2, 0), (B, B, C)),),
    ),
)
# The first gridded perm of the first list cannot be placed with the third list,
# by the two obstructions in a chain, and many gridded perms of the other two
# lists can be placed between them.
A_CHAIN_OF_OBSTRUCTIONS = (
    (GriddedPerm((0, 1, 2), (A, C, C)), GriddedPerm((1, 2, 0), (B, B, C))),
    (
        (GriddedPerm((1, 0, 2), (B, C, C)), GriddedPerm((3, 1, 2, 0), (A, B, B, B))),
        (GriddedPerm((1, 2, 0), (A, B, C)),),
        (GriddedPerm((1, 3, 2, 0), (A, A, A, C)),),
        (GriddedPerm((3, 0, 1, 2), (A, A, B, B)),),
    ),
)


@pytest.mark.timeout(1)
@pytest.mark.parametrize(
    "tiling, empty",
    [(TWO_CELLS_NOT_BOTH, True), (A_CHAIN_OF_OBSTRUCTIONS, False)],
    ids=["two cells not both", "a chain of obstructions"],
)
def test_find_past_the_first_pass(tiling, empty, monkeypatch):
    """Each goes past the first pass, to the searches with the look-aheads, which
    decide it in a few milliseconds."""
    obstructions, requirements = tiling
    searched = searches_recorded(monkeypatch)
    found = GriddedPermSearch(obstructions, requirements).find()
    assert (found is None) == empty
    assert empty or is_gridded_perm_on(found, obstructions, requirements)
    assert any(look_ahead for _, _, look_ahead in searched)
    assert Tiling(obstructions, requirements).is_empty() == empty


def test_look_aheads_cut_the_search():
    """With the lists in their own order, the look-aheads drop each rest whose
    first gridded perm of the first list rules out the third list, and the search
    takes about a hundred states, its look-aheads' among them; without them, it
    takes tens of thousands."""
    obstructions, requirements = A_CHAIN_OF_OBSTRUCTIONS
    search = GriddedPermSearch(obstructions, requirements)
    assert search._search(search.requirements, 200, look_ahead=True) is not None
    with pytest.raises(_OverBudget):
        search._search(search.requirements, 10_000, look_ahead=False)


def test_dropped_counts_a_dead_end():
    obstructions, requirements = A_CHAIN_OF_OBSTRUCTIONS
    search = GriddedPermSearch(obstructions, requirements)
    first = requirements[0][0]
    assert not search._dropped(first, [requirements[1], requirements[2]])
    assert not search._dead_ends
    # The dead ends of placing the list alone, and the rest dropped for it.
    assert search._dropped(first, [requirements[1], requirements[3]])
    assert list(search._dead_ends) == [requirements[3]]
    # A list closed out, which no gridded perm on the tiling can hold.
    obstructions = (GriddedPerm((0, 1), (A, B)), GriddedPerm((1, 0), (A, B)))
    in_b = (GriddedPerm.point_perm(B),)
    search = GriddedPermSearch(obstructions, ((GriddedPerm.point_perm(A),), in_b))
    assert search._dropped(GriddedPerm.point_perm(A), [in_b])
    assert search._dead_ends == {in_b: 1}


def test_can_place():
    obstructions, requirements = A_CHAIN_OF_OBSTRUCTIONS
    search = GriddedPermSearch(obstructions, requirements)
    first = requirements[0][0]
    assert not search._can_place(first, requirements[3])
    assert search._can_place(first, requirements[1])
    assert search._can_place(first, requirements[2])
    assert search._can_place(GriddedPerm.empty_perm(), requirements[3])
    assert search._can_place(requirements[0][1], requirements[3])


def test_closed_out():
    """A point in (0, 0) closes (1, 0), as the cells cannot both hold a point."""
    obstructions = (GriddedPerm((0, 1), (A, B)), GriddedPerm((1, 0), (A, B)))
    requirements = ((GriddedPerm.point_perm(A),), (GriddedPerm.point_perm(B),))
    in_a, in_b = requirements
    search = GriddedPermSearch(obstructions, requirements)
    assert search._closed_out(GriddedPerm.point_perm(A), [in_b]) == in_b
    # A list closed out after one that is not.
    assert search._closed_out(GriddedPerm.point_perm(A), [in_a, in_b]) == in_b
    assert search._closed_out(GriddedPerm.point_perm(A), []) is None
    assert search._closed_out(GriddedPerm.empty_perm(), [in_a, in_b]) is None
    assert search._closed_out(GriddedPerm((0, 1), (A, A)), [in_a]) is None
    # A list closed out in one of its gridded perms only.
    in_b_or_c = (GriddedPerm.point_perm(B), GriddedPerm.point_perm(C))
    assert search._closed_out(GriddedPerm.point_perm(A), [in_b_or_c]) is None
    assert search.find() is None
    assert GriddedPermSearch(obstructions, (in_a, in_b_or_c)).find() is not None


def test_closed_out_a_cell_with_the_points_the_list_needs(monkeypatch):
    """(0, 0) holds at most one point, and 01 across (0, 0) and (1, 0) needs one
    there: a point in (0, 0) closes the cell, but the list can use that point."""
    obstructions = (GriddedPerm((0, 1), (A, A)), GriddedPerm((1, 0), (A, A)))
    across = (GriddedPerm((0, 1), (A, B)),)
    requirements = ((GriddedPerm.point_perm(A),), across)
    search = GriddedPermSearch(obstructions, requirements)
    assert not search._takes_a_point(GriddedPerm.point_perm(A), A)
    assert search._closed_out(GriddedPerm.point_perm(A), [across]) is None
    two_in_a = (GriddedPerm((0, 1), (A, A)),)
    assert search._closed_out(GriddedPerm.point_perm(A), [two_in_a]) == two_in_a
    monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", 0)
    assert GriddedPermSearch(obstructions, requirements).find() == across[0]


def three_lists_that_cannot_all_hold(cells_above, joined=False):
    """The cells (0, 0), (1, 0) and (2, 0), a point required in each, and every
    order of a point in each an obstruction: each pair of the three lists has a
    gridded perm, and the three do not. Beside them, cells in a row above, each
    needing 01. If joined, each cell above is joined to (0, 0) by an obstruction
    that needs two points in (0, 0), which no gridded perm the search makes has."""
    obstructions = tuple(
        GriddedPerm(patt, (A, B, C)) for patt in permutations(range(3))
    )
    above = [(3 + column, 1) for column in range(cells_above)]
    if joined:
        obstructions += tuple(GriddedPerm((0, 1, 2), (A, A, cell)) for cell in above)
    requirements = tuple((GriddedPerm.point_perm(cell),) for cell in (A, B, C)) + tuple(
        (GriddedPerm((0, 1), (cell, cell)),) for cell in above
    )
    return obstructions, requirements


def test_groups():
    """Two lists are in one group if their cells meet, or an obstruction uses cells
    of both; not if each of two obstructions uses a cell of one of them and a cell
    no list uses."""
    in_a, in_b, in_c = ((GriddedPerm.point_perm(cell),) for cell in (A, B, C))
    increasing_in_a = (GriddedPerm((0, 1), (A, A)),)
    lists = (in_a, in_b, in_c, increasing_in_a)

    def groups(obstructions):
        search = GriddedPermSearch(obstructions, lists)
        return sorted(search._groups(lists))

    alone = sorted([(in_a, increasing_in_a), (in_b,), (in_c,)])
    assert groups(()) == alone
    assert groups((GriddedPerm((0, 1), (A, B)),)) == sorted(
        [(in_a, in_b, increasing_in_a), (in_c,)]
    )
    unused = (0, 1)
    assert (
        groups((GriddedPerm((0, 1), (A, unused)), GriddedPerm((1, 0), (unused, B))))
        == alone
    )


def test_combined():
    """A gridded perm cut into gridded perms on cells apart, and put together again:
    each is what the result has in its cells."""
    rng = random.Random(0)
    for _ in range(200):
        gridded_perm = random_gridded_perm(rng, rng.randint(0, 7), 3, 3)
        cells = sorted(set(gridded_perm.pos))
        rng.shuffle(cells)
        cuts = sorted(rng.randint(0, len(cells)) for _ in range(2))
        parts_cells = [cells[: cuts[0]], cells[cuts[0] : cuts[1]], cells[cuts[1] :]]
        parts = [gridded_perm.get_gridded_perm_in_cells(part) for part in parts_cells]
        combined = _combined(parts)
        assert not combined.contradictory()
        assert len(combined) == len(gridded_perm)
        for part, part_cells in zip(parts, parts_cells):
            assert combined.get_gridded_perm_in_cells(part_cells) == part


def test_find_groups_alone(monkeypatch):
    """The three lists that cannot all hold, and four lists in cells apart from
    them: past the first pass, the group of the three is searched alone. With one
    of the obstructions taken out, each group has a gridded perm, and together
    they make one of the tiling."""
    obstructions, requirements = three_lists_that_cannot_all_hold(4)
    searched = searches_recorded(monkeypatch)
    assert GriddedPermSearch(obstructions, requirements).find() is None
    points = tuple(sorted(requirements[:3]))
    assert any(tuple(sorted(lists)) == points for lists, _, _ in searched)
    obstructions = obstructions[1:]
    found = GriddedPermSearch(obstructions, requirements).find()
    assert is_gridded_perm_on(found, obstructions, requirements)


@pytest.mark.timeout(1)
def test_find_with_the_dead_ends_first():
    """The three lists that cannot all hold, with eight lists above that the
    search places first, each joined to them by an obstruction: one group. The
    first pass fails at the last point, for each way of placing the lists above;
    the searches after it place first the lists that fail."""
    obstructions, requirements = three_lists_that_cannot_all_hold(8, joined=True)
    assert GriddedPermSearch(obstructions, requirements).find() is None


def test_restarts_double_their_budget(monkeypatch):
    obstructions, requirements = three_lists_that_cannot_all_hold(8, joined=True)
    searched = searches_recorded(monkeypatch)
    assert GriddedPermSearch(obstructions, requirements).find() is None
    budgets = [budget for _, budget, look_ahead in searched if look_ahead]
    assert len(budgets) > 1
    first_pass = GriddedPermSearch._FIRST_PASS_STATES
    assert budgets == [first_pass * 2 ** (i + 1) for i in range(len(budgets))]


def test_dead_ends_put_a_list_first(monkeypatch):
    """If B has a point, A is monotone; the lists n...21 in A, 12...m in A or in C,
    and a point in B. The first pass places 12...m in A in every way, and each time
    fails at the point in B; the search after it places the point first."""
    obstructions = tuple(
        GriddedPerm(
            tuple(p if p < value else p + 1 for p in patt) + (value,), (A, A, A, B)
        )
        for patt in ((0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1))
        for value in range(4)
    )
    in_b = (GriddedPerm.point_perm(B),)
    requirements = (
        (GriddedPerm((5, 4, 3, 2, 1, 0), (A,) * 6),),
        (GriddedPerm((0, 1, 2, 3), (A,) * 4), GriddedPerm((0, 1, 2, 3), (C,) * 4)),
        in_b,
    )
    searched = searches_recorded(monkeypatch)
    found = GriddedPermSearch(obstructions, requirements).find()
    assert is_gridded_perm_on(found, obstructions, requirements)
    first_lists, _, look_ahead = searched[0]
    assert not look_ahead and first_lists[-1] == in_b
    later = [lists for lists, _, look_ahead in searched if look_ahead]
    assert later and later[0][0] == in_b


def unique_gridded_perm_tiling(target):
    """The obstructions of the tiling on a row of two cells whose only gridded perm
    is the target: those the target does not contain whose every one-point deletion
    it does. A gridded perm avoids them if and only if the target contains it."""
    contained = {
        target.get_gridded_perm_at_indices(
            [index for index in range(len(target)) if mask >> index & 1]
        )
        for mask in range(2 ** len(target))
    }
    obstructions = set()
    for gridded_perm in contained:
        for index in range(len(gridded_perm) + 1):
            for cell in (A, B):
                if any(other > cell for other in gridded_perm.pos[:index]) or any(
                    other < cell for other in gridded_perm.pos[index:]
                ):
                    continue
                for value in range(len(gridded_perm) + 1):
                    bigger = gridded_perm.insert_specific_point(cell, index, value)
                    if bigger not in contained and all(
                        bigger.remove_point(point) in contained
                        for point in range(len(bigger))
                    ):
                        obstructions.add(bigger)
    return tuple(sorted(obstructions))


def test_find_the_only_gridded_perm():
    """The tiling whose only gridded perm is 516374280 on two cells, its first five
    points in (0, 0), with lists of one gridded perm each, in three orders."""
    target = GriddedPerm((5, 1, 6, 3, 7, 4, 2, 8, 0), (A,) * 5 + (B,) * 4)
    requirements = tuple(
        (GriddedPerm(patt, cells),)
        for patt, cells in [
            ((1, 2, 0), (A, B, B)),
            ((2, 1, 0), (B, B, B)),
            ((1, 0, 2), (A, A, B)),
            ((2, 0, 1), (A, A, A)),
            ((0, 2, 1), (A, A, A)),
            ((0, 1, 2), (A, A, A)),
        ]
    )
    obstructions = unique_gridded_perm_tiling(target)
    assert len(obstructions) == 44
    for lists in (
        requirements,
        requirements[::-1],
        requirements[3:] + requirements[:3],
    ):
        search = GriddedPermSearch(obstructions, requirements)
        search.requirements = lists
        assert search.find() == target
    assert not Tiling(obstructions, requirements).is_empty()


def test_find_two_lists_that_cannot_both_hold(monkeypatch):
    """Points in each of three to five cells in a row, and each pair of the cells in
    turn unable to hold a point each; with no first pass."""
    monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", 0)
    for count in (3, 4, 5):
        cells = [(column, 0) for column in range(count)]
        requirements = tuple((GriddedPerm.point_perm(cell),) for cell in cells)
        for first, second in combinations(cells, 2):
            obstructions = (
                GriddedPerm((0, 1), (first, second)),
                GriddedPerm((1, 0), (first, second)),
            )
            assert GriddedPermSearch(obstructions, requirements).find() is None


def test_search_counts_the_states_of_its_look_aheads():
    """A point in A and a point in B, as in test_search_counts_its_states: five
    states without the look-aheads. With them, each rest also places each list it
    does not satisfy alone, from the rest, a placing and a rest: twice at the first
    rest and once at the rest with A, nine states more."""
    in_a, in_b = (GriddedPerm.point_perm(A),), (GriddedPerm.point_perm(B),)
    search = GriddedPermSearch((), (in_a, in_b))
    assert search._search(search.requirements, 14, look_ahead=True) is not None
    with pytest.raises(_OverBudget):
        search._search(search.requirements, 13, look_ahead=True)


def test_can_place_takes_the_states_left():
    """A look-ahead's search takes its states from those left to the search under
    way, and stops when none are left."""
    in_a = (GriddedPerm.point_perm(A),)
    search = GriddedPermSearch((), (in_a,))
    search._states_left = 3
    assert search._can_place(GriddedPerm.empty_perm(), in_a)
    assert search._states_left == 0
    search._states_left = 2
    with pytest.raises(_OverBudget):
        search._can_place(GriddedPerm.empty_perm(), in_a)


def test_groups_are_searched_in_rounds(monkeypatch):
    """The three lists that cannot all hold, and two lists above them that the
    search places first, each a group of its own; with no first pass. Each round
    searches every group not yet decided, so no search has a smaller budget than
    one before it, the first round searches all three groups, a group once
    decided is not searched again, and the search of the three is the last."""
    monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", 0)
    obstructions, requirements = three_lists_that_cannot_all_hold(2)
    search = GriddedPermSearch(obstructions, requirements)
    assert len(search._groups(search.requirements)) == 3
    outcomes = outcomes_recorded(monkeypatch)
    assert search.find() is None
    rounds = [
        (lists, budget, found)
        for lists, budget, look_ahead, found in outcomes
        if look_ahead
    ]
    budgets = [budget for _, budget, _ in rounds]
    assert budgets == sorted(budgets)
    assert budgets[:3] == [2, 2, 2]
    assert len({lists for lists, _, _ in rounds[:3]}) == 3
    decided = [
        number for number, (_, _, found) in enumerate(rounds) if found != "over budget"
    ]
    for number in decided:
        assert all(lists != rounds[number][0] for lists, _, _ in rounds[number + 1 :])
    assert decided[-1] == len(rounds) - 1 and rounds[-1][2] is None


def test_each_group_has_a_first_pass(monkeypatch):
    """The three lists that cannot all hold, and four lists above them in groups of
    their own: the first pass of all the lists does not finish, and those of the
    groups decide them, the group of the three last, with no search with the
    look-aheads."""
    obstructions, requirements = three_lists_that_cannot_all_hold(4)
    outcomes = outcomes_recorded(monkeypatch)
    assert GriddedPermSearch(obstructions, requirements).find() is None
    first_pass = GriddedPermSearch._FIRST_PASS_STATES
    assert len(outcomes) == 6
    assert all(
        budget == first_pass and not look_ahead for _, budget, look_ahead, _ in outcomes
    )
    assert outcomes[0][3] == "over budget" and outcomes[-1][3] is None


def test_unmade_children_counts_each_dead_end():
    """A placing none of whose points can go anywhere is a dead end of its list, each
    one counted; a placing whose children were all made before is not one."""
    point = GriddedPerm.point_perm
    in_a, in_b = (point(A),), (point(B),)
    search = GriddedPermSearch((point(B),), (in_a, in_b))
    lists = search.requirements
    shut = (GriddedPerm.empty_perm(), point(B), (), frozenset(), lists.index(in_b))
    for expected in (1, 2, 3):
        assert list(search._unmade_children(shut, lists, set(), set())) == []
        assert search._dead_ends == {in_b: expected}
    free = (GriddedPerm.empty_perm(), point(A), (), frozenset(), lists.index(in_a))
    rests_made = set()
    assert len(list(search._unmade_children(free, lists, rests_made, set()))) == 1
    assert list(search._unmade_children(free, lists, rests_made, set())) == []
    # Made before is no dead end.
    assert search._dead_ends == {in_b: 3}


def test_dropped_counts_each_dead_end():
    """test_dropped_counts_a_dead_end's last case, dropped twice."""
    obstructions = (GriddedPerm((0, 1), (A, B)), GriddedPerm((1, 0), (A, B)))
    in_b = (GriddedPerm.point_perm(B),)
    search = GriddedPermSearch(obstructions, ((GriddedPerm.point_perm(A),), in_b))
    assert search._dropped(GriddedPerm.point_perm(A), [in_b])
    assert search._dead_ends == {in_b: 1}
    assert search._dropped(GriddedPerm.point_perm(A), [in_b])
    assert search._dead_ends == {in_b: 2}


def test_can_place_counts_the_dead_ends_it_meets():
    """The dead ends of a look-ahead's search are its list's: they say the list is
    hard to place, which is what the order of the restarts asks."""
    shut = GriddedPerm.point_perm(B)
    increasing = GriddedPerm((0, 1), (A, A))
    search = GriddedPermSearch(
        (shut,), ((shut, increasing), (GriddedPerm.point_perm(C),))
    )
    placeable = (shut, increasing)
    assert search._can_place(GriddedPerm.empty_perm(), placeable)
    assert search._dead_ends == {placeable: 1}


@pytest.mark.parametrize(
    "dead_ends, order",
    [({1: 1, 2: 3}, (2, 1, 0)), ({0: 2, 2: 2}, (0, 2, 1)), ({1: 1}, (1, 0, 2))],
    ids=["more first", "ties keep their order", "one dead end before none"],
)
def test_find_places_the_lists_with_the_most_dead_ends_first(
    dead_ends, order, monkeypatch
):
    """The dead ends as the searches before would leave them; no first pass, so the
    first search with the look-aheads shows the order. All three lists share a
    cell."""
    monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", 0)
    lists = tuple(
        (GriddedPerm(tuple(range(length)), (A,) * length),) for length in (3, 2, 1)
    )
    search = GriddedPermSearch((), lists)
    assert search.requirements == lists
    for index, count in dead_ends.items():
        search._dead_ends[lists[index]] = count
    searched = searches_recorded(monkeypatch)
    assert search._find(lists) is not None
    first = next(ordered for ordered, _, look_ahead in searched if look_ahead)
    assert first == tuple(lists[index] for index in order)


def test_find_two_groups_apart_are_searched_alone(monkeypatch):
    monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", 0)
    lists = ((GriddedPerm.point_perm(A),), (GriddedPerm.point_perm(C),))
    searched = searches_recorded(monkeypatch)
    assert is_gridded_perm_on(GriddedPermSearch((), lists).find(), (), lists)
    assert {len(searched_lists) for searched_lists, _, _ in searched[1:]} == {1}


def test_restarts_with_no_first_pass_start_at_two_states(monkeypatch):
    monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", 0)
    obstructions, requirements = three_lists_that_cannot_all_hold(2, joined=True)
    searched = searches_recorded(monkeypatch)
    assert GriddedPermSearch(obstructions, requirements).find() is None
    budgets = [budget for _, budget, look_ahead in searched if look_ahead]
    assert budgets[:3] == [2, 4, 8]


def test_an_empty_list_is_sorted_after_the_others_in_its_kind():
    point = GriddedPerm.point_perm(A)
    pair = GriddedPerm((0, 1), (A, A))
    search = GriddedPermSearch((), ((), (point,), (pair,)))
    assert search.requirements == ((pair,), (point,), ())


def test_small_tilings_split_into_groups(monkeypatch):
    """The brute force's tilings reach lists split into groups, with no first
    pass."""
    monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", 0)
    splits = []
    original_groups = GriddedPermSearch._groups

    def groups_recorded(self, lists):
        groups = original_groups(self, lists)
        splits.append(len(groups))
        return groups

    monkeypatch.setattr(GriddedPermSearch, "_groups", groups_recorded)
    for obstructions, requirements, _, _ in small_tilings(1, 60):
        GriddedPermSearch(obstructions, requirements).find()
    assert max(splits) > 1


def test_find_few_lists_past_the_first_pass(monkeypatch):
    monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", 0)
    point = GriddedPerm.point_perm(A)
    assert GriddedPermSearch((), ()).find() == GriddedPerm.empty_perm()
    assert GriddedPermSearch((), ((point,),)).find() == point
    assert GriddedPermSearch((), ((),)).find() is None
    assert GriddedPermSearch((), ((), (point,))).find() is None
    assert GriddedPermSearch((point,), ((point,),)).find() is None
    requirements = ((GriddedPerm.empty_perm(),), (point,))
    assert is_gridded_perm_on(
        GriddedPermSearch((), requirements).find(), (), requirements
    )


def test_combined_puts_an_earlier_gridded_perm_left_and_below():
    low, high = GriddedPerm.point_perm((0, 0)), GriddedPerm.point_perm((0, 1))
    assert _combined([low, high]) == GriddedPerm((0, 1), ((0, 0), (0, 1)))
    assert _combined([high, low]) == GriddedPerm((1, 0), ((0, 1), (0, 0)))
    left, right = GriddedPerm.point_perm((0, 0)), GriddedPerm.point_perm((1, 0))
    assert _combined([left, right]) == GriddedPerm((0, 1), ((0, 0), (1, 0)))
    assert _combined([right, left]) == GriddedPerm((1, 0), ((0, 0), (1, 0)))
    # Both points of the first are left of the point above them, and below the
    # point right of them.
    two_points = GriddedPerm((0, 1), ((0, 0), (0, 0)))
    assert _combined([two_points, high]) == GriddedPerm(
        (0, 1, 2), ((0, 0),) * 2 + ((0, 1),)
    )
    assert _combined([two_points, right]) == GriddedPerm(
        (0, 1, 2), ((0, 0),) * 2 + ((1, 0),)
    )


def test_find_stops_at_the_first_group_with_none(monkeypatch):
    """01 in each of three cells, every order of a point in each an obstruction,
    sorted before two point lists above them, each a group of its own; with no
    first pass. The search that finds the group of the three has no gridded perm
    is the last."""
    monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", 0)
    cells = (A, B, C)
    obstructions = tuple(GriddedPerm(patt, cells) for patt in permutations(range(3)))
    increasing = tuple((GriddedPerm((0, 1), (cell, cell)),) for cell in cells)
    points_above = tuple(
        (GriddedPerm.point_perm((3 + column, 1)),) for column in range(2)
    )
    outcomes = outcomes_recorded(monkeypatch)
    assert GriddedPermSearch(obstructions, increasing + points_above).find() is None
    last_lists, _, _, last_found = outcomes[-1]
    assert set(last_lists) == set(increasing) and last_found is None
    assert all(found is not None for _, _, _, found in outcomes[:-1])

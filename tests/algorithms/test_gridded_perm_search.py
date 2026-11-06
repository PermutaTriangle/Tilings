import random
from itertools import combinations, combinations_with_replacement, permutations

import pytest

from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import GriddedPermSearch

A, B, C = (0, 0), (1, 0), (2, 0)


def is_gridded_perm_on(gridded_perm, obstructions, requirements):
    """Whether gridded_perm is a gridded perm whose points fit their cells, that
    avoids the obstructions and contains a gridded perm of each list."""
    return (
        gridded_perm is not None
        and not gridded_perm.contradictory()
        and gridded_perm.avoids(*obstructions)
        and all(gridded_perm.contains(*reqlist) for reqlist in requirements)
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
    longest = sum(max(map(len, reqlist), default=0) for reqlist in requirements)
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
        if sum(max(map(len, reqlist)) for reqlist in requirements) <= 5:
            made += 1
            yield obstructions, requirements, columns, rows


def find(obstructions, requirements, first_pass_states=None, monkeypatch=None):
    if first_pass_states is not None:
        monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", first_pass_states)
    return GriddedPermSearch(obstructions, requirements).find()


@pytest.mark.parametrize("first_pass_states", [64, 0])
def test_find_against_a_brute_force(first_pass_states, monkeypatch):
    """With the first pass as it is, and with none, so that every tiling is also
    searched by pairs and with the look-aheads; with the lists, and the gridded
    perms in each, in the search's order and reversed."""
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
                tuple(reversed(reqlist)) for reqlist in reversed(search.requirements)
            ),
        ):
            search = GriddedPermSearch(obstructions, requirements)
            search.requirements = lists
            found = search.find()
            assert (found is not None) == expected, (obstructions, lists)
            if found is not None:
                assert is_gridded_perm_on(found, obstructions, requirements)
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
    """A tiling on which a fault in the minimum indices of develop's search of
    minimal gridded perms lost every gridded perm."""
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


def test_find_a_point_of_the_gridded_perm_used_twice():
    """One cell avoiding 102 and 3201 and containing 01 and 210: placing 210 and
    then 01 at a point of it, at its 2 with a new point above, gives 2310."""
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


# The cells (0, 0) and (1, 0) cannot both hold a point, and the first list needs a
# point in one, the last in the other: each list can be placed alone, but these two
# lists together cannot (round 2's hunt, 101:607).
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
# lists can be placed between them (round 2's hunt, 102:264).
A_CHAIN_OF_OBSTRUCTIONS = (
    (GriddedPerm((0, 1, 2), (A, C, C)), GriddedPerm((1, 2, 0), (B, B, C))),
    (
        (GriddedPerm((1, 0, 2), (B, C, C)), GriddedPerm((3, 1, 2, 0), (A, B, B, B))),
        (GriddedPerm((1, 2, 0), (A, B, C)),),
        (GriddedPerm((1, 3, 2, 0), (A, A, A, C)),),
        (GriddedPerm((3, 0, 1, 2), (A, A, B, B)),),
    ),
)


def test_find_pairs_of_lists(monkeypatch):
    """Each list can be placed alone, and each pair of lists but the first and the
    last has a gridded perm; with no first pass, the pairs find that the tiling has
    none."""
    obstructions, requirements = TWO_CELLS_NOT_BOTH
    search = GriddedPermSearch(obstructions, requirements)
    for reqlist in requirements:
        assert search._can_place(GriddedPerm.empty_perm(), reqlist)
    for first, second in combinations(requirements, 2):
        found = search._find((first, second))
        if (first, second) == (requirements[0], requirements[-1]):
            assert found is None
        else:
            assert is_gridded_perm_on(found, obstructions, (first, second))
    searched = []

    def search_recorded(self, lists, budget, look_ahead):
        searched.append((len(lists), look_ahead))
        return original(self, lists, budget, look_ahead)

    original = GriddedPermSearch._search
    monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", 0)
    monkeypatch.setattr(GriddedPermSearch, "_search", search_recorded)
    assert GriddedPermSearch(obstructions, requirements).find() is None
    assert (4, True) not in searched


@pytest.mark.timeout(1)
@pytest.mark.parametrize(
    "tiling, empty",
    [(TWO_CELLS_NOT_BOTH, True), (A_CHAIN_OF_OBSTRUCTIONS, False)],
    ids=["two cells not both", "a chain of obstructions"],
)
def test_find_past_the_first_pass(tiling, empty):
    """Depth first alone, the search took 0.16 s on the first and over 20 s on the
    second, where develop's search of minimal gridded perms takes 1 ms and 0.2 s."""
    obstructions, requirements = tiling
    found = GriddedPermSearch(obstructions, requirements).find()
    assert (found is None) == empty
    assert empty or is_gridded_perm_on(found, obstructions, requirements)
    assert Tiling(obstructions, requirements).is_empty() == empty


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
    assert search._closed_out(GriddedPerm.point_perm(A), [in_b])
    assert not search._closed_out(GriddedPerm.point_perm(A), [])
    assert not search._closed_out(GriddedPerm.empty_perm(), [in_a, in_b])
    assert not search._closed_out(GriddedPerm((0, 1), (A, A)), [in_a])
    # A list closed out in one of its gridded perms only.
    in_b_or_c = (GriddedPerm.point_perm(B), GriddedPerm.point_perm(C))
    assert not search._closed_out(GriddedPerm.point_perm(A), [in_b_or_c])
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
    assert not search._closed_out(GriddedPerm.point_perm(A), [across])
    two_in_a = (GriddedPerm((0, 1), (A, A)),)
    assert search._closed_out(GriddedPerm.point_perm(A), [two_in_a])
    monkeypatch.setattr(GriddedPermSearch, "_FIRST_PASS_STATES", 0)
    assert GriddedPermSearch(obstructions, requirements).find() == across[0]


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
                if any(c > cell for c in gridded_perm.pos[:index]) or any(
                    c < cell for c in gridded_perm.pos[index:]
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
    points in (0, 0), with lists of one gridded perm each. With these lists in this
    order, not sorted as Tiling sorts them, develop's minimal_gridded_perms yields
    nothing; the search finds the gridded perm in each order of the lists."""
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

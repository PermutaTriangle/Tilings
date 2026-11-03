import pytest

from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import MinimalGriddedPerms

tilings = [
    # Testing glueing indep cells
    Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((1, 1), (1, 1))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 2))),
            GriddedPerm((0, 2, 1), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 2))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 2), (0, 0))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 0))),
            GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((1, 0, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((1, 3, 0, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((1, 3, 2, 0), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 3, 0, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 3, 0, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
        ),
        requirements=(
            (GriddedPerm((0,), ((1, 1),)),),
            (
                GriddedPerm((1, 0), ((0, 2), (0, 2))),
                GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((2, 1, 0), ((0, 2), (0, 0), (0, 0))),
            ),
        ),
    ),
    # Make sure you generate all minimal gridded perms
    Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((0, 2),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0,), ((1, 3),)),
            GriddedPerm((0,), ((2, 0),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0,), ((2, 2),)),
            GriddedPerm((0,), ((3, 1),)),
            GriddedPerm((0,), ((3, 2),)),
            GriddedPerm((0,), ((3, 3),)),
            GriddedPerm((0, 1), ((1, 2), (1, 2))),
            GriddedPerm((0, 1), ((2, 3), (2, 3))),
            GriddedPerm((0, 1), ((3, 0), (3, 0))),
            GriddedPerm((1, 0), ((1, 2), (1, 2))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 3))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 3), (0, 3))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 3), (2, 3))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 3), (0, 3))),
            GriddedPerm((0, 2, 1), ((0, 1), (2, 3), (2, 3))),
            GriddedPerm((1, 0, 2), ((0, 3), (0, 1), (0, 3))),
            GriddedPerm((1, 2, 0), ((0, 3), (2, 3), (2, 3))),
            GriddedPerm((2, 0, 1), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((2, 0, 1), ((0, 3), (0, 1), (0, 3))),
            GriddedPerm((2, 1, 0), ((0, 3), (2, 3), (2, 3))),
            GriddedPerm((2, 1, 0), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 3), (0, 3), (0, 3), (2, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 3), (0, 3), (2, 3), (2, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 2, 1, 3), ((0, 3), (0, 3), (0, 3), (2, 3))),
            GriddedPerm((0, 2, 3, 1), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 2, 3, 1), ((0, 3), (0, 3), (0, 3), (2, 3))),
            GriddedPerm((0, 3, 2, 1), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 3, 2, 1), ((0, 3), (0, 3), (0, 3), (2, 3))),
            GriddedPerm((2, 0, 3, 1), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((2, 0, 3, 1), ((0, 3), (0, 3), (0, 3), (2, 3))),
            GriddedPerm((3, 0, 2, 1), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((3, 0, 2, 1), ((0, 3), (0, 3), (0, 3), (2, 3))),
        ),
        requirements=(
            (GriddedPerm((0,), ((1, 2),)),),
            (GriddedPerm((0,), ((2, 3),)),),
            (
                GriddedPerm((1, 0), ((0, 3), (0, 1))),
                GriddedPerm((1, 0), ((0, 3), (2, 3))),
                GriddedPerm((2, 0, 1), ((0, 3), (0, 3), (0, 3))),
            ),
        ),
    ),
    # Avoid duplicate work
    Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((1, 1), (1, 1))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 3, 2), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 2, 1, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 2, 3, 1), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 3, 1, 2), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((1, 0, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((1, 2, 0, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((1, 2, 3, 0), ((2, 0), (2, 0), (2, 0), (2, 0))),
        ),
        requirements=(
            (GriddedPerm((0,), ((1, 1),)),),
            (GriddedPerm((0,), ((2, 0),)),),
            (GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),),
        ),
    ),
    # Skips a level
    Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((0, 2),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0,), ((1, 3),)),
            GriddedPerm((0,), ((2, 0),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0,), ((2, 2),)),
            GriddedPerm((0,), ((3, 1),)),
            GriddedPerm((0,), ((3, 2),)),
            GriddedPerm((0,), ((3, 3),)),
            GriddedPerm((0, 1), ((0, 3), (0, 3))),
            GriddedPerm((0, 1), ((1, 2), (1, 2))),
            GriddedPerm((0, 1), ((2, 3), (2, 3))),
            GriddedPerm((0, 1), ((3, 0), (3, 0))),
            GriddedPerm((1, 0), ((1, 2), (1, 2))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 3), (2, 3))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1), ((0, 3), (2, 3), (2, 3))),
            GriddedPerm((1, 0, 2), ((0, 1), (0, 1), (0, 3))),
            GriddedPerm((1, 2, 0), ((0, 3), (2, 3), (2, 3))),
            GriddedPerm((2, 0, 1), ((0, 3), (0, 1), (0, 3))),
            GriddedPerm((2, 1, 0), ((0, 3), (2, 3), (2, 3))),
            GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 1), (2, 3), (2, 3))),
        ),
        requirements=(
            (GriddedPerm((0,), ((1, 2),)),),
            (GriddedPerm((0,), ((2, 3),)),),
            (
                GriddedPerm((0,), ((3, 0),)),
                GriddedPerm((1, 2, 0), ((0, 1), (0, 1), (0, 1))),
                GriddedPerm((1, 2, 0), ((0, 1), (0, 3), (0, 1))),
            ),
        ),
    ),
    # careful about skipping undone work!
    Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0,), ((2, 2),)),
            GriddedPerm((0,), ((3, 0),)),
            GriddedPerm((0,), ((3, 1),)),
            GriddedPerm((0, 1), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((1, 1), (1, 1))),
            GriddedPerm((1, 0), ((2, 0), (2, 0))),
            GriddedPerm((1, 0), ((3, 2), (3, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (3, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (3, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (3, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (3, 2), (3, 2))),
            GriddedPerm((0, 1, 2), ((0, 2), (0, 2), (3, 2))),
            GriddedPerm((0, 1, 2), ((3, 2), (3, 2), (3, 2))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 2), (3, 2))),
            GriddedPerm((1, 0, 2), ((0, 0), (2, 0), (3, 2))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (3, 2))),
            GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (3, 2), (3, 2))),
            GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (0, 2), (3, 2))),
            GriddedPerm((0, 3, 1, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 1, 2), ((0, 2), (0, 2), (3, 2), (3, 2))),
            GriddedPerm((1, 2, 0, 3), ((0, 2), (0, 2), (0, 0), (0, 2))),
            GriddedPerm((1, 2, 0, 3), ((0, 2), (0, 2), (0, 2), (0, 2))),
        ),
        requirements=(
            (GriddedPerm((0,), ((1, 1),)),),
            (GriddedPerm((0,), ((2, 0),)),),
            (
                GriddedPerm((0, 1), ((2, 0), (2, 0))),
                GriddedPerm((1, 0), ((0, 2), (0, 0))),
                GriddedPerm((1, 0), ((0, 2), (3, 2))),
                GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (2, 0))),
                GriddedPerm((2, 0, 1), ((0, 2), (0, 2), (0, 2))),
            ),
        ),
    ),
    Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0, 1), ((0, 1), (0, 1))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((0, 1), (0, 1))),
            GriddedPerm((1, 0), ((0, 2), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 2), (0, 2), (0, 2))),
        ),
        requirements=((GriddedPerm((1, 0), ((0, 2), (0, 1))),),),
    ),
]

expected_mgps = [
    frozenset(
        [
            GriddedPerm((2, 1, 0), ((0, 2), (0, 2), (1, 1))),
            GriddedPerm((2, 1, 0, 3), ((0, 0), (0, 0), (0, 0), (1, 1))),
            GriddedPerm((3, 1, 0, 2), ((0, 2), (0, 0), (0, 0), (1, 1))),
        ]
    ),
    frozenset(
        [
            GriddedPerm((2, 0, 1), ((0, 3), (1, 2), (2, 3))),
            GriddedPerm((2, 0, 1, 3), ((0, 3), (0, 1), (1, 2), (2, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 3), (0, 3), (1, 2), (2, 3))),
        ]
    ),
    frozenset(
        [
            GriddedPerm((2, 1, 0, 4, 3), ((0, 0), (0, 0), (0, 0), (1, 1), (2, 0))),
            GriddedPerm((3, 1, 0, 4, 2), ((0, 0), (0, 0), (0, 0), (1, 1), (2, 0))),
            GriddedPerm((3, 2, 0, 4, 1), ((0, 0), (0, 0), (0, 0), (1, 1), (2, 0))),
            GriddedPerm((3, 2, 1, 4, 0), ((0, 0), (0, 0), (0, 0), (1, 1), (2, 0))),
        ]
    ),
    frozenset(
        [
            GriddedPerm((1, 2, 0), ((1, 2), (2, 3), (3, 0))),
            GriddedPerm((1, 2, 0, 3, 4), ((0, 1), (0, 1), (0, 1), (1, 2), (2, 3))),
            GriddedPerm((1, 4, 0, 2, 3), ((0, 1), (0, 3), (0, 1), (1, 2), (2, 3))),
        ]
    ),
    frozenset(
        [
            GriddedPerm((2, 0, 1), ((1, 1), (2, 0), (2, 0))),
            GriddedPerm((2, 0, 3, 1), ((0, 0), (0, 0), (1, 1), (2, 0))),
            GriddedPerm((3, 0, 2, 1), ((0, 2), (0, 0), (1, 1), (2, 0))),
            GriddedPerm((3, 1, 0, 2), ((0, 2), (1, 1), (2, 0), (3, 2))),
            GriddedPerm((3, 1, 2, 0), ((0, 2), (0, 0), (1, 1), (2, 0))),
            GriddedPerm((4, 2, 3, 1, 0), ((0, 2), (0, 2), (0, 2), (1, 1), (2, 0))),
        ]
    ),
    frozenset([GriddedPerm((1, 0), ((0, 2), (0, 1)))]),
]


@pytest.mark.parametrize(("tiling", "expected_mgps"), zip(tilings, expected_mgps))
def test_minimal_gridded_perms(tiling, expected_mgps):
    mgps = []
    for gp in MinimalGriddedPerms(
        tiling.obstructions, tiling.requirements
    ).minimal_gridded_perms():
        assert gp not in mgps
        for old in mgps:
            assert gp not in old
            assert old not in gp
        mgps.append(gp)
    assert frozenset(mgps) == expected_mgps
    assert len(mgps) == len(expected_mgps)
    curr_len = len(mgps[0])
    # We check that they are in increasing length order
    for gp in mgps:
        assert len(gp) >= curr_len, mgps
        curr_len = len(gp)


@pytest.mark.parametrize("tiling", tilings)
def test_find_gridded_perm(tiling):
    gridded_perm = MinimalGriddedPerms(
        tiling.obstructions, tiling.requirements
    ).find_gridded_perm()
    assert gridded_perm is not None
    assert gridded_perm.avoids(*tiling.obstructions)
    assert all(
        gridded_perm.contains(*requirement) for requirement in tiling.requirements
    )


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
def test_find_gridded_perm_every_order_but_one(orders):
    """A point in each of four cells, in a row or in a column, and every order
    of the points but one an obstruction: that order is the only gridded perm.
    In a column, a point inserted moves the minimum indices of the other
    cells."""
    cells, every_order = orders(4)
    points = tuple((GriddedPerm.point_perm(cell),) for cell in cells)
    for allowed in every_order:
        obstructions = tuple(order for order in every_order if order != allowed)
        assert MinimalGriddedPerms(obstructions, points).find_gridded_perm() == allowed
    assert MinimalGriddedPerms(tuple(every_order), points).find_gridded_perm() is None


def test_find_gridded_perm_column_minimum_indices():
    """Found by checking every gridded perm on random tilings: a point inserted
    just after the last point inserted into another cell of its column leaves
    that cell's minimum index as it is, or no gridded perm is found."""
    obstructions = (
        GriddedPerm((1, 0, 2), ((0, 1), (0, 0), (1, 1))),
        GriddedPerm((2, 0, 1), ((0, 1), (0, 1), (0, 1))),
        GriddedPerm((2, 0, 1, 3), ((0, 0), (0, 0), (0, 0), (0, 1))),
    )
    requirements = (
        (GriddedPerm((0, 2, 1), ((0, 0), (0, 1), (0, 0))),),
        (GriddedPerm((1, 0, 2), ((0, 1), (0, 1), (1, 1))),),
        (GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (1, 0))),),
    )
    gridded_perm = MinimalGriddedPerms(obstructions, requirements).find_gridded_perm()
    assert gridded_perm is not None
    assert gridded_perm.avoids(*obstructions)
    assert all(gridded_perm.contains(*requirement) for requirement in requirements)


def test_find_gridded_perm_none():
    empty_cell = GriddedPerm((0,), ((0, 0),))
    increasing = GriddedPerm((0, 1), ((0, 0), (0, 0)))
    decreasing = GriddedPerm((1, 0), ((1, 0), (1, 0)))
    point = GriddedPerm.point_perm((1, 0))
    # A requirement that contains an obstruction, alone in its list.
    assert (
        MinimalGriddedPerms(
            (empty_cell,), ((increasing,), (point,))
        ).find_gridded_perm()
        is None
    )
    assert (
        MinimalGriddedPerms((empty_cell,), ((increasing,),)).find_gridded_perm() is None
    )
    assert (
        MinimalGriddedPerms(
            (empty_cell,), ((increasing, decreasing),)
        ).find_gridded_perm()
        == decreasing
    )
    assert MinimalGriddedPerms((), ()).find_gridded_perm() == GriddedPerm.empty_perm()
    assert (
        MinimalGriddedPerms((GriddedPerm.empty_perm(),), ()).find_gridded_perm() is None
    )


def test_order():
    """
    We expect the gps to be always from the shortest to the longest one.
    """
    t = Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((0, 2),)),
            GriddedPerm((0,), ((0, 3),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0,), ((1, 3),)),
            GriddedPerm((0,), ((2, 0),)),
            GriddedPerm((0,), ((2, 2),)),
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((1, 2), (1, 2))),
            GriddedPerm((0, 1), ((2, 1), (2, 3))),
            GriddedPerm((1, 0), ((0, 0), (0, 0))),
            GriddedPerm((1, 0), ((1, 2), (1, 2))),
            GriddedPerm((0, 1, 2), ((2, 1), (2, 1), (2, 1))),
            GriddedPerm((0, 2, 1), ((0, 0), (2, 3), (2, 1))),
            GriddedPerm((0, 2, 1), ((0, 0), (2, 3), (2, 3))),
            GriddedPerm((0, 2, 1), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm((1, 2, 0), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm((0, 1, 3, 2), ((0, 0), (2, 1), (2, 1), (2, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (2, 1), (2, 1), (2, 1))),
            GriddedPerm((1, 0, 2, 3), ((2, 3), (2, 3), (2, 3), (2, 3))),
            GriddedPerm((3, 0, 1, 2), ((2, 3), (2, 3), (2, 3), (2, 3))),
        ),
        requirements=(
            (GriddedPerm((0,), ((1, 2),)),),
            (GriddedPerm((0,), ((2, 1),)),),
            (
                GriddedPerm((1, 0, 2), ((2, 1), (2, 1), (2, 1))),
                GriddedPerm((1, 0, 2), ((2, 3), (2, 3), (2, 3))),
            ),
        ),
    )
    mgps = list(
        MinimalGriddedPerms(t.obstructions, t.requirements).minimal_gridded_perms()
    )
    assert mgps == [
        GriddedPerm(Perm([3, 1, 0, 2]), [(1, 2), (2, 1), (2, 1), (2, 1)]),
        GriddedPerm(Perm([1, 3, 2, 4, 0]), [(1, 2), (2, 3), (2, 3), (2, 3), (2, 1)]),
    ]

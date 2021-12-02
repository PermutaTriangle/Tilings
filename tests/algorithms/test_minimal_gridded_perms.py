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

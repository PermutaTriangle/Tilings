from heapq import heapify
from itertools import combinations_with_replacement

import pytest

from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import MinimalGriddedPerms
from tilings.algorithms.minimal_gridded_perms import QueuePacket

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


def is_gridded_perm_on(gridded_perm, obstructions, requirements):
    """Whether gridded_perm is a gridded perm that avoids the obstructions and
    contains the requirements."""
    return (
        gridded_perm is not None
        and gridded_perm.avoids(*obstructions)
        and all(gridded_perm.contains(*requirement) for requirement in requirements)
    )


def gridded_perms_on_a_grid(length, columns, rows):
    """Every gridded perm of the given length on a grid of the given numbers
    of columns and rows."""
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


def minimal_gridded_perms_by_brute_force(obstructions, requirements):
    """Every gridded perm that avoids the obstructions and contains the
    requirements, of which no gridded perm made by removing one point
    contains them: every proper gridded subperm lies in one of those. A
    minimal gridded perm is the union of a requirement from each list, so it
    is no longer than the longest of each list together, and its cells are
    those of the requirements."""
    cells = [
        cell
        for requirement_list in requirements
        for requirement in requirement_list
        for cell in requirement.pos
    ]
    columns = max(x for x, _ in cells) + 1
    rows = max(y for _, y in cells) + 1
    longest = sum(max(map(len, requirement_list)) for requirement_list in requirements)
    minimal = set()
    for length in range(longest + 1):
        for gridded_perm in gridded_perms_on_a_grid(length, columns, rows):
            if is_gridded_perm_on(gridded_perm, obstructions, requirements) and not any(
                all(
                    gridded_perm.remove_point(index).contains(*requirement_list)
                    for requirement_list in requirements
                )
                for index in range(length)
            ):
                minimal.add(gridded_perm)
    return minimal


# Found by a search of small tilings: on each, minimal gridded perms are lost if
# the minimum indices are worked out as if each point inserted were one place
# further right.
TILINGS_FOR_THE_BRUTE_FORCE = {
    "a row of two cells, three lists": (
        (),
        (
            (GriddedPerm((1, 0), ((1, 0), (1, 0))),),
            (GriddedPerm.point_perm((1, 0)),),
            (GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),),
        ),
    ),
    "a row of two cells, an obstruction": (
        (GriddedPerm((1, 3, 0, 2), ((0, 0), (1, 0), (1, 0), (1, 0))),),
        (
            (GriddedPerm((0, 1), ((0, 0), (0, 0))),),
            (GriddedPerm((1, 0), ((1, 0), (1, 0))),),
            (GriddedPerm.point_perm((1, 0)),),
        ),
    ),
    "a column of three cells": (
        (
            GriddedPerm((0, 2, 3, 1), ((0, 1),) * 4),
            GriddedPerm((1, 0), ((0, 0),) * 2),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0),) * 4),
            GriddedPerm((1, 2, 0, 3), ((0, 2),) * 4),
        ),
        (
            (GriddedPerm((0, 1), ((0, 2), (0, 2))),),
            (GriddedPerm((0, 1), ((0, 1), (0, 1))),),
        ),
    ),
}


@pytest.mark.parametrize("name", TILINGS_FOR_THE_BRUTE_FORCE)
def test_minimal_gridded_perms_against_a_brute_force(name):
    """Every minimal gridded perm, each once, and the shortest first."""
    obstructions, requirements = TILINGS_FOR_THE_BRUTE_FORCE[name]
    expected = minimal_gridded_perms_by_brute_force(obstructions, requirements)
    assert expected
    found = list(
        MinimalGriddedPerms(obstructions, requirements).minimal_gridded_perms()
    )
    assert len(found) == len(set(found))
    assert set(found) == expected
    lengths = [len(gridded_perm) for gridded_perm in found]
    assert lengths == sorted(lengths)


@pytest.mark.parametrize("tiling", tilings)
def test_find_gridded_perm(tiling):
    gridded_perm = MinimalGriddedPerms(
        tiling.obstructions, tiling.requirements
    ).find_gridded_perm()
    assert is_gridded_perm_on(gridded_perm, tiling.obstructions, tiling.requirements)


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
    obstructions = (GriddedPerm((1, 0, 2), ((0, 1), (0, 0), (1, 1))),)
    requirements = (
        (GriddedPerm((0, 2, 1), ((0, 0), (0, 1), (0, 0))),),
        (GriddedPerm((1, 0, 2), ((0, 1), (0, 1), (1, 1))),),
        (GriddedPerm((1, 0), ((0, 0), (0, 0))),),
    )
    gridded_perm = MinimalGriddedPerms(obstructions, requirements).find_gridded_perm()
    assert is_gridded_perm_on(gridded_perm, obstructions, requirements)


# Two ways to contain the first requirement list, a point in (0, 0) or 01 in
# (1, 1), and a point in (0, 1), which shares a column with the first and a row
# with the second: neither initial gridded perm contains it, so the search
# starts with two packets.
TWO_INITIAL_PACKETS = (
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


def test_find_gridded_perm_two_initial_packets():
    gridded_perm = MinimalGriddedPerms((), TWO_INITIAL_PACKETS).find_gridded_perm()
    assert is_gridded_perm_on(gridded_perm, (), TWO_INITIAL_PACKETS)


def test_find_gridded_perm_two_initial_packets_the_second_holds_it():
    """The shorter packet holds no gridded perm; the longer one does."""
    gridded_perm = MinimalGriddedPerms(
        NOT_BOTH_IN_THE_COLUMN, TWO_INITIAL_PACKETS
    ).find_gridded_perm()
    assert is_gridded_perm_on(gridded_perm, NOT_BOTH_IN_THE_COLUMN, TWO_INITIAL_PACKETS)
    assert gridded_perm.contains(GriddedPerm((0, 1), ((1, 1), (1, 1))))


def test_find_gridded_perm_two_initial_packets_none():
    obstructions = NOT_BOTH_IN_THE_COLUMN + NOT_BOTH_IN_THE_ROW
    assert (
        MinimalGriddedPerms(obstructions, TWO_INITIAL_PACKETS).find_gridded_perm()
        is None
    )
    assert Tiling(obstructions, TWO_INITIAL_PACKETS).is_empty()
    assert not Tiling(requirements=TWO_INITIAL_PACKETS).is_empty()


def test_is_empty_two_initial_gridded_perms():
    """Two initial gridded perms, a point with 10 above it and 01 with 10 in the
    top cell, neither containing the requirements: the search starts with
    both."""
    tiling = Tiling(
        requirements=(
            (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0, 1), ((0, 1), (0, 1)))),
            (GriddedPerm((1, 0), ((0, 1), (0, 1))),),
        )
    )
    assert len(tiling.requirements) == 2
    assert not tiling.is_empty()


def test_find_gridded_perm_after_an_initial_gridded_perm_with_an_obstruction():
    """The first choice from each list gives an initial gridded perm that
    contains an obstruction: the next choice must still be tried."""
    obstructions = (GriddedPerm.point_perm((0, 0)),)
    requirements = (
        (GriddedPerm.point_perm((0, 0)), GriddedPerm.point_perm((1, 0))),
        (GriddedPerm.point_perm((1, 1)),),
    )
    gridded_perm = MinimalGriddedPerms(obstructions, requirements).find_gridded_perm()
    assert is_gridded_perm_on(gridded_perm, obstructions, requirements)


def test_find_gridded_perm_after_a_gridded_perm_with_an_obstruction_made_again():
    """One cell avoiding 102 and 3201 and containing 01 and 210: a gridded perm
    that contains an obstruction is made again from the same packet, and the
    insertions after it must still be tried."""
    cell = (0, 0)
    obstructions = (
        GriddedPerm((1, 0, 2), (cell,) * 3),
        GriddedPerm((3, 2, 0, 1), (cell,) * 4),
    )
    requirements = (
        (GriddedPerm((0, 1), (cell,) * 2),),
        (GriddedPerm((2, 1, 0), (cell,) * 3),),
    )
    assert is_gridded_perm_on(
        GriddedPerm((0, 3, 2, 1), (cell,) * 4), obstructions, requirements
    )
    gridded_perm = MinimalGriddedPerms(obstructions, requirements).find_gridded_perm()
    assert is_gridded_perm_on(gridded_perm, obstructions, requirements)


def test_find_gridded_perm_empty_requirement_list_among_two():
    point = GriddedPerm.point_perm((0, 0))
    assert MinimalGriddedPerms((), ((), (point,))).find_gridded_perm() is None
    assert MinimalGriddedPerms((), ((point,), ())).find_gridded_perm() is None


def test_find_gridded_perm_empty_perm_obstruction_and_two_requirement_lists():
    requirements = (
        (GriddedPerm.point_perm((0, 0)),),
        (GriddedPerm.point_perm((1, 1)),),
    )
    assert MinimalGriddedPerms((), requirements).find_gridded_perm() is not None
    assert (
        MinimalGriddedPerms(
            (GriddedPerm.empty_perm(),), requirements
        ).find_gridded_perm()
        is None
    )


# A column of three cells. One list is 01 in the bottom cell or 01 in the top
# cell, so no cell is used by every requirement in it, and the other is 012 in
# the middle cell, which the initial gridded perm holds: the search inserts the
# points of the first list into a cell that no list needs points in.
POINTS_NO_LIST_NEEDS = (
    (
        GriddedPerm((0, 1), ((0, 0), (0, 0))),
        GriddedPerm((0, 1), ((0, 2), (0, 2))),
    ),
    (GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 1))),),
)


def test_find_gridded_perm_points_no_list_needs():
    gridded_perm = MinimalGriddedPerms((), POINTS_NO_LIST_NEEDS).find_gridded_perm()
    assert is_gridded_perm_on(gridded_perm, (), POINTS_NO_LIST_NEEDS)


def test_is_empty_points_no_list_needs():
    tiling = Tiling(requirements=POINTS_NO_LIST_NEEDS)
    assert tiling.requirements == POINTS_NO_LIST_NEEDS
    assert not tiling.is_empty()


EMPTY_CELL = GriddedPerm((0,), ((0, 0),))
INCREASING = GriddedPerm((0, 1), ((0, 0), (0, 0)))


def test_find_gridded_perm_none():
    # A requirement that contains an obstruction, alone in its list.
    assert (
        MinimalGriddedPerms(
            (EMPTY_CELL,), ((INCREASING,), (GriddedPerm.point_perm((1, 0)),))
        ).find_gridded_perm()
        is None
    )
    assert (
        MinimalGriddedPerms((EMPTY_CELL,), ((INCREASING,),)).find_gridded_perm() is None
    )
    assert (
        MinimalGriddedPerms((GriddedPerm.empty_perm(),), ()).find_gridded_perm() is None
    )


def test_find_gridded_perm_one_requirement_list_or_none():
    """With one requirement list, its first requirement that avoids the
    obstructions, and with none, the empty perm."""
    decreasing = GriddedPerm((1, 0), ((1, 0), (1, 0)))
    assert (
        MinimalGriddedPerms(
            (EMPTY_CELL,), ((INCREASING, decreasing),)
        ).find_gridded_perm()
        == decreasing
    )
    assert MinimalGriddedPerms((), ()).find_gridded_perm() == GriddedPerm.empty_perm()


def test_points_lacking_by_patterns():
    """10 in a cell lacks two points of 012 there by the pattern, where the
    count says one, and a point in another cell lacks one."""
    increasing = GriddedPerm((0, 1, 2), ((0, 0),) * 3)
    point = GriddedPerm.point_perm((1, 0))
    mgp = MinimalGriddedPerms((), ((increasing,), (point,)))
    packet = QueuePacket(
        GriddedPerm((1, 0), ((0, 0),) * 2), (increasing, point), (-1, -1), True, {}
    )
    assert mgp._points_lacking_by_patterns(packet) == 3


def test_points_lacking_by_patterns_least_in_a_list_most_over_lists():
    """A point in a cell: the first list, 012 there or a point in another cell,
    lacks no point there, and 01 and 10, in lists of their own, lack one each,
    so the packet lacks one."""
    point = GriddedPerm.point_perm((1, 0))
    decreasing = GriddedPerm((1, 0), ((0, 0),) * 2)
    requirements = (
        (GriddedPerm((0, 1, 2), ((0, 0),) * 3), point),
        (INCREASING,),
        (decreasing,),
    )
    mgp = MinimalGriddedPerms((), requirements)
    packet = QueuePacket(
        GriddedPerm.point_perm((0, 0)),
        (point, INCREASING, decreasing),
        (-1, -1),
        True,
        {},
    )
    assert mgp._points_lacking_by_patterns(packet) == 1


def test_points_lacking_by_patterns_closed_cell():
    """10 in a cell that holds the most points the goal can need there: no
    gridded perm made from the packet contains 01 in it."""
    increasing = GriddedPerm((0, 1), ((0, 0),) * 2)
    point = GriddedPerm.point_perm((1, 0))
    mgp = MinimalGriddedPerms((), ((increasing,), (point,)))
    packet = QueuePacket(
        GriddedPerm((1, 0), ((0, 0),) * 2), (increasing, point), (-1, -1), True, {}
    )
    assert mgp._points_lacking_by_patterns(packet) is None


def test_points_lacking_by_patterns_across_closed_cells():
    """A point in each of two cells before the last cell, as 10: no gridded
    perm made from the packet contains 01 across them, though each cell holds
    its point; as 01, the packet lacks only the point in the last cell."""
    across = GriddedPerm((0, 1), ((0, 0), (1, 0)))
    point = GriddedPerm.point_perm((2, 0))
    mgp = MinimalGriddedPerms((), ((across,), (point,)))
    for patt, points_lacking in (((1, 0), None), ((0, 1), 1)):
        packet = QueuePacket(
            GriddedPerm(patt, ((0, 0), (1, 0))), (across, point), (2, 0), False, {}
        )
        assert mgp._points_lacking_by_patterns(packet) == points_lacking


def test_packets_taken(monkeypatch):
    """Taking no packets before it prunes: 210 in a cell before the last cell
    is dropped, and 210 in an open cell, of bound 5 by the counts and 7 by the
    pattern 0123, is taken after the packets of bound 5, 6 and 7 that are
    longer."""
    monkeypatch.setattr(MinimalGriddedPerms, "PACKETS_TAKEN_BEFORE_PRUNING", 0)
    increasing = GriddedPerm((0, 1, 2, 3), ((0, 0),) * 4)
    point = GriddedPerm.point_perm((1, 0))
    mgp = MinimalGriddedPerms((), ((increasing,), (point,)))

    def packet(patt, last_cell=(-1, -1)):
        return QueuePacket(
            GriddedPerm(patt, ((0, 0),) * len(patt)),
            (increasing, point),
            last_cell,
            last_cell == (-1, -1),
            {},
        )

    raised, dropped = packet((2, 1, 0)), packet((2, 1, 0), (1, 0))
    longer = [packet(tuple(range(length))) for length in (4, 5, 6)]
    points_needed = mgp._points_needed()
    heap = [
        mgp._heap_entry(packet, mgp._points_lacking(packet.gp, points_needed))
        for packet in [raised, dropped] + longer
    ]
    heapify(heap)
    taken = [packet for packet, _ in mgp._packets_taken(heap)]
    assert taken == longer + [raised]


# Found by checking every gridded perm on random tilings: taking no packets
# before it prunes, find_gridded_perm drops a packet as a requirement lacks a
# point in a closed cell, or only by the check across closed cells, or puts one
# back with a sharper bound.
TILINGS_WHERE_FIND_GRIDDED_PERM_PRUNES = {
    "a point lacking in a closed cell": (
        (
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (1, 1), (1, 0))),
        ),
        (
            (GriddedPerm((0, 1), ((0, 1), (1, 1))),),
            (GriddedPerm((0, 1), ((1, 0), (1, 0))),),
            (GriddedPerm((1, 0), ((1, 1), (1, 1))),),
        ),
    ),
    "a point lacking in a closed cell, empty": (
        (
            GriddedPerm((0, 2, 1), ((0, 1), (0, 2), (0, 2))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 2), (0, 0))),
            GriddedPerm((2, 1, 0), ((0, 2), (0, 1), (0, 0))),
            GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 2), (0, 1))),
            GriddedPerm((2, 3, 0, 1), ((0, 2), (0, 2), (0, 0), (0, 0))),
            GriddedPerm((2, 3, 1, 0), ((0, 0), (0, 1), (0, 0), (0, 0))),
        ),
        (
            (GriddedPerm((1, 0), ((0, 2), (0, 2))),),
            (GriddedPerm((1, 2, 0), ((0, 1), (0, 1), (0, 0))),),
        ),
    ),
    "across closed cells, and a sharper bound": (
        (
            GriddedPerm((0, 1), ((0, 0), (0, 1))),
            GriddedPerm((1, 0, 2), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 3, 0, 2), ((0, 2), (0, 2), (0, 0), (0, 2))),
        ),
        (
            (GriddedPerm((0, 1), ((0, 1), (0, 1))),),
            (GriddedPerm((1, 0), ((0, 1), (0, 1))),),
            (GriddedPerm((1, 0), ((0, 2), (0, 0))),),
        ),
    ),
    "across closed cells, empty": (
        (
            GriddedPerm((1, 0), ((0, 1), (0, 0))),
            GriddedPerm((1, 0), ((0, 2), (0, 2))),
            GriddedPerm((2, 0, 1), ((0, 2), (0, 0), (0, 1))),
        ),
        (
            (GriddedPerm((1, 0), ((0, 2), (0, 0))),),
            (GriddedPerm((1, 2, 0), ((0, 1), (0, 1), (0, 1))),),
        ),
    ),
    "a sharper bound": (
        (
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((2, 0, 1), ((1, 1), (1, 0), (1, 0))),
        ),
        (
            (GriddedPerm((0,), ((1, 0),)),),
            (GriddedPerm((0, 1), ((0, 0), (0, 1))),),
            (GriddedPerm((0, 1), ((0, 1), (0, 1))),),
        ),
    ),
}


@pytest.mark.parametrize("name", TILINGS_WHERE_FIND_GRIDDED_PERM_PRUNES)
@pytest.mark.parametrize("packets_taken_before_pruning", [0, 8])
def test_find_gridded_perm_pruning(name, packets_taken_before_pruning, monkeypatch):
    monkeypatch.setattr(
        MinimalGriddedPerms,
        "PACKETS_TAKEN_BEFORE_PRUNING",
        packets_taken_before_pruning,
    )
    obstructions, requirements = TILINGS_WHERE_FIND_GRIDDED_PERM_PRUNES[name]
    gridded_perm = MinimalGriddedPerms(obstructions, requirements).find_gridded_perm()
    if name.endswith("empty"):
        assert gridded_perm is None
        assert not minimal_gridded_perms_by_brute_force(obstructions, requirements)
    else:
        assert is_gridded_perm_on(gridded_perm, obstructions, requirements)


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

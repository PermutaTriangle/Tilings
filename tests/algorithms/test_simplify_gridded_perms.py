from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import GriddedPermReduction


def test_duplicate_req_lists():
    a = Tiling(
        obstructions=(
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 1))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (1, 2), (1, 0))),
            GriddedPerm((1, 2, 0), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 1), (0, 2), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (1, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((1, 2), (1, 2), (1, 2))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 1), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 2), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 2), (1, 2), (1, 0))),
        ),
        requirements=(
            (
                GriddedPerm((0,), ((0, 1),)),
                GriddedPerm((0,), ((0, 2),)),
                GriddedPerm((0,), ((1, 2),)),
            ),
        ),
    )
    b = Tiling(
        obstructions=(
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 1))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (1, 2), (1, 0))),
            GriddedPerm((1, 2, 0), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 1), (0, 2), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (1, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((1, 2), (1, 2), (1, 2))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 1), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 2), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 2), (1, 2), (1, 0))),
        ),
        requirements=(
            (
                GriddedPerm((0,), ((0, 1),)),
                GriddedPerm((0,), ((0, 2),)),
                GriddedPerm((0,), ((1, 2),)),
            ),
            (
                GriddedPerm((0,), ((0, 1),)),
                GriddedPerm((0,), ((0, 2),)),
                GriddedPerm((0,), ((1, 2),)),
            ),
        ),
    )

    assert a == b


def test_remove_subset_req():
    a = Tiling(
        obstructions=(
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 1))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (1, 2), (1, 0))),
            GriddedPerm((1, 2, 0), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 1), (0, 2), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (1, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((1, 2), (1, 2), (1, 2))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 1), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 2), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 2), (1, 2), (1, 0))),
        ),
        requirements=(
            (
                GriddedPerm((0,), ((0, 1),)),
                GriddedPerm((0,), ((0, 2),)),
            ),
        ),
    )
    b = Tiling(
        obstructions=(
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 1))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (1, 2), (1, 0))),
            GriddedPerm((1, 2, 0), ((0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 1), (0, 2), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 1))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (1, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((1, 2), (1, 2), (1, 2))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 1), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 2), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 2), (1, 2), (1, 0))),
        ),
        requirements=(
            (
                GriddedPerm((0,), ((0, 1),)),
                GriddedPerm((0,), ((0, 2),)),
            ),
            (
                GriddedPerm((0,), ((0, 1),)),
                GriddedPerm((0,), ((0, 2),)),
                GriddedPerm((0,), ((1, 2),)),
            ),
        ),
    )

    assert a == b


def test_req_list_implies_empty():
    tiling = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 1))),
            GriddedPerm((0, 1), ((0, 0), (1, 2))),
            GriddedPerm((0, 1), ((0, 0), (1, 3))),
            GriddedPerm((0, 1), ((0, 3), (0, 3))),
            GriddedPerm((0, 1), ((0, 3), (1, 3))),
            GriddedPerm((0, 1), ((1, 3), (1, 3))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 3))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (0, 3))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 2), (1, 2))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 2), (1, 3))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (2, 2), (2, 0))),
            GriddedPerm((0, 2, 1), ((0, 0), (2, 3), (2, 0))),
            GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 2, 1), ((1, 0), (2, 2), (2, 0))),
            GriddedPerm((0, 2, 1), ((1, 0), (2, 3), (2, 0))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 2), (2, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 3), (0, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 3), (1, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (0, 3), (2, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (1, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (1, 2), (2, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (1, 3), (1, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (1, 3), (2, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (2, 2), (2, 2))),
            GriddedPerm((1, 2, 0), ((0, 2), (2, 3), (2, 2))),
            GriddedPerm((1, 2, 0), ((0, 3), (2, 3), (2, 2))),
            GriddedPerm((1, 2, 0), ((0, 3), (2, 3), (2, 3))),
            GriddedPerm((1, 2, 0), ((1, 2), (1, 2), (1, 2))),
            GriddedPerm((1, 2, 0), ((1, 2), (1, 2), (2, 2))),
            GriddedPerm((1, 2, 0), ((1, 2), (1, 3), (1, 2))),
            GriddedPerm((1, 2, 0), ((1, 2), (1, 3), (2, 2))),
            GriddedPerm((1, 2, 0), ((1, 2), (2, 2), (2, 2))),
            GriddedPerm((1, 2, 0), ((1, 2), (2, 3), (2, 2))),
            GriddedPerm((1, 2, 0), ((1, 3), (2, 3), (2, 2))),
            GriddedPerm((1, 2, 0), ((1, 3), (2, 3), (2, 3))),
            GriddedPerm((1, 2, 0), ((2, 2), (2, 2), (2, 2))),
            GriddedPerm((1, 2, 0), ((2, 2), (2, 3), (2, 2))),
            GriddedPerm((1, 2, 0), ((2, 3), (2, 3), (2, 2))),
            GriddedPerm((1, 2, 0), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 3), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 2), (0, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 3), (0, 1))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 2), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 3), (1, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 2, 3, 1), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 2, 3, 1), ((2, 0), (2, 0), (2, 2), (2, 0))),
            GriddedPerm((0, 2, 3, 1), ((2, 0), (2, 0), (2, 3), (2, 0))),
            GriddedPerm((0, 2, 3, 1), ((2, 0), (2, 2), (2, 2), (2, 0))),
            GriddedPerm((0, 2, 3, 1), ((2, 0), (2, 2), (2, 3), (2, 0))),
            GriddedPerm((0, 2, 3, 1), ((2, 0), (2, 3), (2, 3), (2, 0))),
        ),
        requirements=(
            (
                GriddedPerm((0,), ((0, 3),)),
                GriddedPerm((0,), ((1, 3),)),
                GriddedPerm((0,), ((2, 3),)),
            ),
            (GriddedPerm((0,), ((1, 2),)), GriddedPerm((0,), ((1, 3),))),
            (GriddedPerm((0,), ((2, 2),)),),
        ),
    )

    assert (0, 0) not in tiling.active_cells


def test_reduce_but_keep_bigger_sub_ob():
    obs1 = GriddedPerm((0, 1), ((0, 0), (1, 2)))
    obs2 = GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (2, 1)))
    req1 = GriddedPerm((0,), ((1, 2),))
    req2 = GriddedPerm((0,), ((2, 1),))
    t = Tiling([obs1, obs2], [[req1, req2]])
    expected = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (1, 2))),
            GriddedPerm((1, 0), ((0, 0), (0, 0))),
        ),
        requirements=((GriddedPerm((0,), ((1, 2),)), GriddedPerm((0,), ((2, 1),))),),
        assumptions=(),
    )
    assert t == expected


def test_reduce_to_join_of_subobs():
    obs1 = GriddedPerm((0, 1, 2), ((0, 0), (1, 2), (3, 3)))
    obs2 = GriddedPerm((0, 1, 2), ((0, 0), (2, 1), (3, 3)))
    req1 = GriddedPerm((0, 1), ((1, 2), (3, 3)))
    req2 = GriddedPerm((0, 1), ((0, 0), (2, 1)))
    t = Tiling([obs1, obs2], [[req1, req2]])
    expected = Tiling(
        obstructions=(GriddedPerm((0, 1), ((0, 0), (3, 3))),),
        requirements=(
            (
                GriddedPerm((0, 1), ((0, 0), (2, 1))),
                GriddedPerm((0, 1), ((1, 2), (3, 3))),
            ),
        ),
    )
    assert t == expected


def test_minimal_req_duplicate():
    assert Tiling(
        obstructions=(
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 1), (1, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (1, 1), (1, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (1, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (1, 1), (1, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 0, 2, 3), ((1, 0), (1, 0), (1, 1), (1, 1))),
            GriddedPerm((1, 0, 3, 2), ((1, 0), (1, 0), (1, 1), (1, 1))),
            GriddedPerm((1, 2, 0, 3), ((1, 0), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((1, 2, 3, 0), ((1, 0), (1, 1), (1, 1), (1, 0))),
            GriddedPerm((1, 3, 0, 2), ((1, 0), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((1, 3, 2, 0), ((1, 0), (1, 1), (1, 1), (1, 0))),
            GriddedPerm((2, 0, 3, 1), ((0, 1), (0, 1), (0, 1), (1, 1))),
            GriddedPerm((2, 0, 3, 1), ((0, 1), (0, 1), (1, 1), (1, 1))),
            GriddedPerm((2, 1, 0, 3), ((0, 1), (1, 0), (1, 0), (1, 1))),
            GriddedPerm((2, 1, 0, 3), ((1, 1), (1, 0), (1, 0), (1, 1))),
            GriddedPerm((2, 1, 3, 0), ((0, 1), (1, 0), (1, 1), (1, 0))),
            GriddedPerm((2, 1, 3, 0), ((1, 1), (1, 0), (1, 1), (1, 0))),
            GriddedPerm((1, 0, 3, 4, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 0, 3, 4, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 0, 3, 4, 2), ((1, 0), (1, 0), (1, 0), (1, 1), (1, 0))),
            GriddedPerm((1, 0, 3, 4, 2), ((1, 1), (1, 0), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 0, 3, 4, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 0, 4, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 0, 4, 3, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 0, 4, 3, 2), ((1, 0), (1, 0), (1, 1), (1, 0), (1, 0))),
            GriddedPerm((1, 0, 4, 3, 2), ((1, 1), (1, 0), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 0, 4, 3, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 3, 0, 4, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 3, 0, 4, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 3, 0, 4, 2), ((1, 0), (1, 0), (1, 0), (1, 1), (1, 0))),
            GriddedPerm((1, 3, 0, 4, 2), ((1, 1), (1, 1), (1, 0), (1, 1), (1, 1))),
            GriddedPerm((1, 3, 0, 4, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 3, 4, 0, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 3, 4, 0, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 3, 4, 0, 2), ((1, 0), (1, 0), (1, 1), (1, 0), (1, 0))),
            GriddedPerm((1, 3, 4, 0, 2), ((1, 1), (1, 1), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((1, 3, 4, 0, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 4, 0, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 4, 0, 3, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 4, 0, 3, 2), ((1, 0), (1, 1), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 4, 0, 3, 2), ((1, 1), (1, 1), (1, 0), (1, 1), (1, 1))),
            GriddedPerm((1, 4, 0, 3, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 4, 3, 0, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 4, 3, 0, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 4, 3, 0, 2), ((1, 0), (1, 1), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 4, 3, 0, 2), ((1, 1), (1, 1), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((1, 4, 3, 0, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((3, 1, 0, 4, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((3, 1, 0, 4, 2), ((0, 1), (1, 1), (1, 0), (1, 1), (1, 1))),
            GriddedPerm((3, 1, 0, 4, 2), ((0, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((3, 1, 0, 4, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((3, 1, 0, 4, 2), ((1, 0), (1, 0), (1, 0), (1, 1), (1, 0))),
            GriddedPerm((3, 1, 0, 4, 2), ((1, 1), (1, 1), (1, 0), (1, 1), (1, 1))),
            GriddedPerm((3, 1, 0, 4, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((3, 1, 4, 0, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((3, 1, 4, 0, 2), ((0, 1), (1, 1), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((3, 1, 4, 0, 2), ((0, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((3, 1, 4, 0, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((3, 1, 4, 0, 2), ((1, 0), (1, 0), (1, 1), (1, 0), (1, 0))),
            GriddedPerm((3, 1, 4, 0, 2), ((1, 1), (1, 1), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((3, 1, 4, 0, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
        ),
        requirements=((GriddedPerm((1, 0), ((1, 0), (1, 0))),),),
        assumptions=(),
    ) == Tiling(
        obstructions=(
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 1), (1, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (1, 1), (1, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (1, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (1, 1), (1, 1))),
            GriddedPerm((0, 3, 2, 1), ((0, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 0, 2, 3), ((1, 0), (1, 0), (1, 1), (1, 1))),
            GriddedPerm((1, 0, 3, 2), ((1, 0), (1, 0), (1, 1), (1, 1))),
            GriddedPerm((1, 2, 0, 3), ((1, 0), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((1, 2, 3, 0), ((1, 0), (1, 1), (1, 1), (1, 0))),
            GriddedPerm((1, 3, 0, 2), ((1, 0), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((1, 3, 2, 0), ((1, 0), (1, 1), (1, 1), (1, 0))),
            GriddedPerm((2, 0, 3, 1), ((0, 1), (0, 1), (0, 1), (1, 1))),
            GriddedPerm((2, 0, 3, 1), ((0, 1), (0, 1), (1, 1), (1, 1))),
            GriddedPerm((2, 1, 0, 3), ((0, 1), (1, 0), (1, 0), (1, 1))),
            GriddedPerm((2, 1, 0, 3), ((1, 1), (1, 0), (1, 0), (1, 1))),
            GriddedPerm((2, 1, 3, 0), ((0, 1), (1, 0), (1, 1), (1, 0))),
            GriddedPerm((2, 1, 3, 0), ((1, 1), (1, 0), (1, 1), (1, 0))),
            GriddedPerm((1, 0, 3, 4, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 0, 3, 4, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 0, 3, 4, 2), ((1, 0), (1, 0), (1, 0), (1, 1), (1, 0))),
            GriddedPerm((1, 0, 3, 4, 2), ((1, 1), (1, 0), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 0, 3, 4, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 0, 4, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 0, 4, 3, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 0, 4, 3, 2), ((1, 0), (1, 0), (1, 1), (1, 0), (1, 0))),
            GriddedPerm((1, 0, 4, 3, 2), ((1, 1), (1, 0), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 0, 4, 3, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 3, 0, 4, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 3, 0, 4, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 3, 0, 4, 2), ((1, 0), (1, 0), (1, 0), (1, 1), (1, 0))),
            GriddedPerm((1, 3, 0, 4, 2), ((1, 1), (1, 1), (1, 0), (1, 1), (1, 1))),
            GriddedPerm((1, 3, 0, 4, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 3, 4, 0, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 3, 4, 0, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 3, 4, 0, 2), ((1, 0), (1, 0), (1, 1), (1, 0), (1, 0))),
            GriddedPerm((1, 3, 4, 0, 2), ((1, 1), (1, 1), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((1, 3, 4, 0, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 4, 0, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 4, 0, 3, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 4, 0, 3, 2), ((1, 0), (1, 1), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 4, 0, 3, 2), ((1, 1), (1, 1), (1, 0), (1, 1), (1, 1))),
            GriddedPerm((1, 4, 0, 3, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((1, 4, 3, 0, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 4, 3, 0, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 4, 3, 0, 2), ((1, 0), (1, 1), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((1, 4, 3, 0, 2), ((1, 1), (1, 1), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((1, 4, 3, 0, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((3, 1, 0, 4, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((3, 1, 0, 4, 2), ((0, 1), (1, 1), (1, 0), (1, 1), (1, 1))),
            GriddedPerm((3, 1, 0, 4, 2), ((0, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((3, 1, 0, 4, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((3, 1, 0, 4, 2), ((1, 0), (1, 0), (1, 0), (1, 1), (1, 0))),
            GriddedPerm((3, 1, 0, 4, 2), ((1, 1), (1, 1), (1, 0), (1, 1), (1, 1))),
            GriddedPerm((3, 1, 0, 4, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((3, 1, 4, 0, 2), ((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((3, 1, 4, 0, 2), ((0, 1), (1, 1), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((3, 1, 4, 0, 2), ((0, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
            GriddedPerm((3, 1, 4, 0, 2), ((1, 0), (1, 0), (1, 0), (1, 0), (1, 0))),
            GriddedPerm((3, 1, 4, 0, 2), ((1, 0), (1, 0), (1, 1), (1, 0), (1, 0))),
            GriddedPerm((3, 1, 4, 0, 2), ((1, 1), (1, 1), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((3, 1, 4, 0, 2), ((1, 1), (1, 1), (1, 1), (1, 1), (1, 1))),
        ),
        requirements=((GriddedPerm((1, 0), ((1, 0), (1, 0))),),),
        assumptions=(),
    )


def test_req_lists_that_imply_each_other():
    pattern_12 = GriddedPerm((0, 1), ((0, 0), (0, 0)))
    pattern_123 = GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0)))
    pattern_1234 = GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 0)))
    pattern_321 = GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0)))
    expected = Tiling([pattern_321], [[pattern_12]])
    counts = [len(list(expected.objects_of_size(size))) for size in range(6)]
    assert counts == [0, 0, 1, 5, 14, 42]
    assert Tiling([pattern_321], [[pattern_12], [pattern_12, pattern_123]]) == expected
    assert (
        Tiling(
            [pattern_321],
            [[pattern_12], [pattern_12, pattern_123], [pattern_12, pattern_1234]],
        )
        == expected
    )
    assert (
        Tiling([pattern_321], [[pattern_12]]).add_list_requirement(
            [pattern_12, pattern_123]
        )
        == expected
    )


def test_from_perms_with_req_lists_that_imply_each_other():
    tiling = Tiling.from_perms(
        [Perm((2, 1, 0))], [[Perm((0, 1))], [Perm((0, 1)), Perm((0, 1, 2))]]
    )
    assert tiling == Tiling.from_perms([Perm((2, 1, 0))], [[Perm((0, 1))]])


def test_req_list_that_sorts_before_the_list_it_implies_and_is_implied_by():
    pattern_12 = GriddedPerm((0, 1), ((0, 0), (0, 0)))
    pattern_123 = GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0)))
    pattern_321 = GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0)))
    assert Tiling(
        [], [[pattern_12, pattern_123, pattern_321], [pattern_12, pattern_321]]
    ) == Tiling([], [[pattern_12, pattern_321]])


def test_req_lists_that_imply_each_other_in_two_cells():
    left_point = GriddedPerm((0,), ((0, 0),))
    right_point = GriddedPerm((0,), ((1, 0),))
    point_in_each_cell = GriddedPerm((0, 1), ((0, 0), (1, 0)))
    assert Tiling(
        [], [[left_point, right_point], [left_point, right_point, point_in_each_cell]]
    ) == Tiling([], [[left_point, right_point]])


def test_req_lists_that_imply_each_other_in_an_empty_cell():
    point = GriddedPerm((0,), ((0, 0),))
    pattern_132 = GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0)))
    assert Tiling([point], [[pattern_132, point], [point]]).is_empty()


def test_req_lists_that_imply_each_other_in_a_cell_that_is_not_empty():
    point = GriddedPerm((0,), ((0, 0),))
    pattern_132 = GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0)))
    tiling = Tiling([], [[pattern_132, point], [point]])
    assert tiling == Tiling([], [[point]])
    assert not tiling.is_empty()


def test_remove_redundant_keeps_the_later_of_two_that_imply_each_other():
    pattern_12 = GriddedPerm((0, 1), ((0, 0), (0, 0)))
    pattern_123 = GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0)))
    reduction = GriddedPermReduction((), (), manual=True)
    assert reduction.remove_redundant([(pattern_12,), (pattern_12, pattern_123)]) == [
        (pattern_12, pattern_123)
    ]
    assert reduction.remove_redundant([(pattern_12, pattern_123), (pattern_12,)]) == [
        (pattern_12,)
    ]
    assert reduction.remove_redundant([(pattern_12,), (pattern_12,)]) == [(pattern_12,)]


def test_remove_redundant_with_the_empty_gridded_perm():
    empty_gridded_perm = GriddedPerm.empty_perm()
    pattern_12 = GriddedPerm((0, 1), ((0, 0), (0, 0)))
    pattern_123 = GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0)))
    reduction = GriddedPermReduction((), (), manual=True)
    assert reduction.remove_redundant([]) == []
    assert reduction.remove_redundant([(empty_gridded_perm, pattern_12)]) == []
    assert reduction.remove_redundant(
        [(pattern_12,), (empty_gridded_perm, pattern_123), (pattern_12, pattern_123)]
    ) == [(pattern_12, pattern_123)]


def test_remove_redundant_with_a_weaker_list_and_two_groups():
    pattern_12 = GriddedPerm((0, 1), ((0, 0), (0, 0)))
    pattern_123 = GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0)))
    pattern_21 = GriddedPerm((1, 0), ((0, 0), (0, 0)))
    pattern_321 = GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0)))
    reduction = GriddedPermReduction((), (), manual=True)
    assert reduction.remove_redundant(
        [(pattern_12,), (pattern_12, pattern_123), (pattern_12, pattern_321)]
    ) == [(pattern_12, pattern_123)]
    assert reduction.remove_redundant(
        [
            (pattern_12,),
            (pattern_21,),
            (pattern_12, pattern_123),
            (pattern_21, pattern_321),
        ]
    ) == [(pattern_12, pattern_123), (pattern_21, pattern_321)]


def test_remove_redundant_with_chains_out_of_order_and_a_stronger_list():
    pattern_12 = GriddedPerm((0, 1), ((0, 0), (0, 0)))
    pattern_123 = GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0)))
    pattern_1234 = GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 0)))
    reduction = GriddedPermReduction((), (), manual=True)
    assert reduction.remove_redundant(
        [(pattern_12, pattern_123), (pattern_12, pattern_1234), (pattern_12,)]
    ) == [(pattern_12,)]
    assert reduction.remove_redundant(
        [(pattern_12, pattern_123), (pattern_12,), (pattern_12, pattern_1234)]
    ) == [(pattern_12, pattern_1234)]
    assert reduction.remove_redundant(
        [(pattern_12,), (pattern_12, pattern_123), (pattern_123,)]
    ) == [(pattern_123,)]

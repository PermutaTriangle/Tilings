from tilings import GriddedPerm, Tiling


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

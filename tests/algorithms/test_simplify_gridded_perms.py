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

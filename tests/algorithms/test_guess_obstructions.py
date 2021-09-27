from tilings import GriddedPerm, Tiling


def test_guess_obstruction():
    tilings = [
        (
            Tiling(
                obstructions=(GriddedPerm((0, 1), ((0, 0), (0, 0))),),
            ),
            5,
        ),
        (
            Tiling(
                obstructions=(GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),),
            ),
            3,
        ),
        (
            Tiling(
                obstructions=(
                    GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                    GriddedPerm((1, 0, 2), ((1, 0), (1, 0), (1, 0))),
                    GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
                    GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (1, 0))),
                    GriddedPerm((2, 1, 0, 3), ((0, 0), (1, 0), (1, 0), (2, 0))),
                    GriddedPerm((2, 0, 1, 3), ((0, 0), (1, 0), (1, 0), (2, 0))),
                ),
            ),
            4,
        ),
        (
            Tiling(
                obstructions=(
                    GriddedPerm(
                        (0, 1, 2, 4, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (0, 1, 4, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (0, 2, 1, 4, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (0, 2, 4, 1, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (0, 4, 1, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (0, 4, 2, 1, 3), ((0, 0), (1, 0), (1, 0), (1, 0), (2, 0))
                    ),
                ),
            ),
            5,
        ),
        (
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                    GriddedPerm((0, 1), ((1, 0), (2, 0))),
                    GriddedPerm((0, 1), ((2, 0), (2, 0))),
                    GriddedPerm((0, 1), ((3, 1), (3, 1))),
                    GriddedPerm((1, 0), ((3, 1), (3, 1))),
                    GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
                    GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
                    GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
                    GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
                    GriddedPerm((3, 2, 1, 0), ((1, 1), (2, 0), (2, 0), (2, 0))),
                ),
            ),
            4,
        ),
        (
            Tiling(
                obstructions=(
                    GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),
                    GriddedPerm(
                        (0, 3, 1, 2, 4), ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0))
                    ),
                    GriddedPerm(
                        (0, 3, 1, 4, 5, 2),
                        ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                    ),
                    GriddedPerm(
                        (0, 2, 4, 5, 1, 6, 3),
                        ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                    ),
                ),
            ),
            7,
        ),
    ]

    for tiling, gen_up_to in tilings:
        # Test for the generated gps of the tiling
        set_of_perms = set(tiling.gridded_perms(gen_up_to))
        assert Tiling.guess_from_gridded_perms(set_of_perms) == tiling
        to_rem_len = max(len(gp) for gp in tiling.obstructions) - 1
        if to_rem_len < 1:
            continue
        to_rem = next((gp for gp in set_of_perms if len(gp) == to_rem_len), None)
        if to_rem is None:
            continue
        # Remove any and make sure it fails
        # This requires the set of gps to have no larger gps than the largest obs
        set_of_perms.remove(to_rem)
        try:
            Tiling.guess_from_gridded_perms(set_of_perms)
            assert False
        except ValueError:
            assert True

from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import Obstruction, Requirement, Tiling
from tilings.strategies import RequirementPlacementStrategy

pytest_plugins = [
    "tests.fixtures.obstructions_requirements",
    "tests.fixtures.simple_tiling",
    "tests.fixtures.diverse_tiling",
    "tests.fixtures.no_point_tiling",
]


def test_point_placement(diverse_tiling, no_point_tiling):
    point_placement = RequirementPlacementStrategy(point_only=True)
    requirement_placement = RequirementPlacementStrategy(point_only=False)
    strats = list(point_placement(diverse_tiling))
    assert len(strats) == 5 * len(DIRS)
    strats = list(requirement_placement(no_point_tiling))
    assert len(strats) == 9 * len(DIRS)
    strats = list(point_placement(no_point_tiling))
    assert len(strats) == 3 * len(DIRS)


def test_place_point_of_requirement_point_only(diverse_tiling):
    tiling = diverse_tiling.place_point_of_gridded_permutation(
        diverse_tiling.requirements[0][0], 0, DIR_WEST
    )
    assert tiling == Tiling(
        obstructions=[
            Obstruction(Perm((0,)), [(1, 0)]),
            Obstruction(Perm((0,)), [(1, 2)]),
            Obstruction(Perm((0,)), [(2, 0)]),
            Obstruction(Perm((0,)), [(2, 2)]),
            Obstruction(Perm((0, 1)), [(2, 1), (2, 1)]),
            Obstruction(Perm((0, 1)), [(4, 3), (4, 3)]),
            Obstruction(Perm((1, 0)), [(2, 1), (2, 1)]),
            Obstruction(Perm((1, 0)), [(4, 3), (4, 3)]),
            Obstruction(Perm((0, 2, 3, 1)), [(0, 0), (1, 3), (1, 3), (4, 0)]),
            Obstruction(Perm((0, 2, 3, 1)), [(0, 0), (1, 3), (1, 3), (4, 2)]),
            Obstruction(Perm((0, 2, 3, 1)), [(0, 0), (1, 3), (3, 3), (4, 0)]),
            Obstruction(Perm((0, 2, 3, 1)), [(0, 0), (1, 3), (3, 3), (4, 2)]),
            Obstruction(Perm((0, 2, 3, 1)), [(0, 0), (3, 3), (3, 3), (4, 0)]),
            Obstruction(Perm((0, 2, 3, 1)), [(0, 0), (3, 3), (3, 3), (4, 2)]),
            Obstruction(Perm((0, 2, 3, 1)), [(0, 2), (1, 3), (1, 3), (4, 2)]),
            Obstruction(Perm((0, 2, 3, 1)), [(0, 2), (1, 3), (3, 3), (4, 2)]),
            Obstruction(Perm((0, 2, 3, 1)), [(0, 2), (3, 3), (3, 3), (4, 2)]),
        ],
        requirements=[
            [Requirement(Perm((0,)), [(2, 1)])],
            [Requirement(Perm((0,)), [(4, 3)])],
            [Requirement(Perm((0,)), [(4, 0)]), Requirement(Perm((0,)), [(4, 2)])],
            [
                Requirement(Perm((1, 0)), [(0, 4), (0, 3)]),
                Requirement(Perm((0, 2, 1)), [(0, 3), (0, 4), (1, 4)]),
                Requirement(Perm((0, 2, 1)), [(0, 3), (0, 4), (3, 4)]),
            ],
        ],
    )

    assert tiling == diverse_tiling.place_point_of_gridded_permutation(
        diverse_tiling.requirements[0][0], 0, DIR_EAST
    )
    assert tiling == diverse_tiling.place_point_of_gridded_permutation(
        diverse_tiling.requirements[0][0], 0, DIR_NORTH
    )
    assert tiling == diverse_tiling.place_point_of_gridded_permutation(
        diverse_tiling.requirements[0][0], 0, DIR_SOUTH
    )

    print(
        Tiling(
            obstructions=[
                Obstruction(Perm((0,)), [(2, 0)]),
                Obstruction(Perm((0,)), [(2, 2)]),
                Obstruction(Perm((0, 1)), [(1, 0), (1, 0)]),
                Obstruction(Perm((0, 1)), [(1, 0), (1, 2)]),
                Obstruction(Perm((0, 1)), [(1, 2), (1, 2)]),
                Obstruction(Perm((0, 1)), [(3, 1), (3, 1)]),
                Obstruction(Perm((0, 1)), [(2, 3), (2, 3)]),
                Obstruction(Perm((0, 1)), [(2, 3), (4, 3)]),
                Obstruction(Perm((0, 1)), [(4, 3), (4, 3)]),
                Obstruction(Perm((1, 0)), [(1, 0), (1, 0)]),
                Obstruction(Perm((1, 0)), [(1, 2), (1, 0)]),
                Obstruction(Perm((1, 0)), [(1, 2), (1, 2)]),
                Obstruction(Perm((1, 0)), [(3, 1), (3, 1)]),
                Obstruction(Perm((1, 0)), [(2, 3), (2, 3)]),
                Obstruction(Perm((1, 0)), [(2, 3), (4, 3)]),
                Obstruction(Perm((1, 0)), [(4, 3), (4, 3)]),
                Obstruction(Perm((0, 1, 2)), [(0, 0), (1, 3), (1, 3)]),
                Obstruction(Perm((0, 2, 3, 1)), [(0, 2), (1, 3), (1, 3), (4, 2)]),
            ],
            requirements=[
                [Requirement(Perm((0,)), [(3, 1)])],
                [Requirement(Perm((0,)), [(1, 0)]), Requirement(Perm((0,)), [(1, 2)])],
                [Requirement(Perm((0,)), [(2, 3)]), Requirement(Perm((0,)), [(4, 3)])],
                [
                    Requirement(Perm((1, 0)), [(0, 4), (0, 3)]),
                    Requirement(Perm((0, 2, 1)), [(0, 3), (0, 4), (1, 4)]),
                ],
            ],
        )
    )
    tiling = diverse_tiling.place_point_of_gridded_permutation(
        diverse_tiling.requirements[1][0], 0, DIR_WEST
    )
    assert tiling == Tiling(
        obstructions=[
            Obstruction(Perm((0,)), [(2, 0)]),
            Obstruction(Perm((0,)), [(2, 2)]),
            Obstruction(Perm((0, 1)), [(1, 0), (1, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (1, 2)]),
            Obstruction(Perm((0, 1)), [(1, 2), (1, 2)]),
            Obstruction(Perm((0, 1)), [(3, 1), (3, 1)]),
            Obstruction(Perm((0, 1)), [(2, 3), (2, 3)]),
            Obstruction(Perm((0, 1)), [(2, 3), (4, 3)]),
            Obstruction(Perm((0, 1)), [(4, 3), (4, 3)]),
            Obstruction(Perm((1, 0)), [(1, 0), (1, 0)]),
            Obstruction(Perm((1, 0)), [(1, 2), (1, 0)]),
            Obstruction(Perm((1, 0)), [(1, 2), (1, 2)]),
            Obstruction(Perm((1, 0)), [(3, 1), (3, 1)]),
            Obstruction(Perm((1, 0)), [(2, 3), (2, 3)]),
            Obstruction(Perm((1, 0)), [(2, 3), (4, 3)]),
            Obstruction(Perm((1, 0)), [(4, 3), (4, 3)]),
            Obstruction(Perm((0, 1, 2)), [(0, 0), (1, 3), (1, 3)]),
            Obstruction(Perm((0, 2, 3, 1)), [(0, 2), (1, 3), (1, 3), (4, 2)]),
        ],
        requirements=[
            [Requirement(Perm((0,)), [(3, 1)])],
            [Requirement(Perm((0,)), [(1, 0)]), Requirement(Perm((0,)), [(1, 2)])],
            [Requirement(Perm((0,)), [(2, 3)]), Requirement(Perm((0,)), [(4, 3)])],
            [
                Requirement(Perm((1, 0)), [(0, 4), (0, 3)]),
                Requirement(Perm((0, 2, 1)), [(0, 3), (0, 4), (1, 4)]),
            ],
        ],
    )

    tiling = Tiling(requirements=[[Requirement(Perm((0,)), [(0, 0)])]])
    assert tiling.place_point_of_gridded_permutation(
        tiling.requirements[0][0], 0, DIR_SOUTH
    ) == Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (0, 0)]),
            Obstruction(Perm((1, 0)), [(0, 0), (0, 0)]),
        ],
        requirements=[[Requirement(Perm((0,)), [(0, 0)])]],
    )


def test_place_point_of_requirement(no_point_tiling):
    tiling = no_point_tiling.place_point_of_gridded_permutation(
        no_point_tiling.requirements[2][0], 1, DIR_WEST
    )
    tiling2 = Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 1), (1, 3)]),
            Obstruction(Perm((0, 1)), [(2, 2), (2, 2)]),
            Obstruction(Perm((1, 0)), [(0, 1), (0, 1)]),
            Obstruction(Perm((1, 0)), [(0, 3), (0, 1)]),
            Obstruction(Perm((1, 0)), [(0, 3), (0, 3)]),
            Obstruction(Perm((1, 0)), [(2, 2), (2, 2)]),
            Obstruction(Perm((0, 1, 2)), [(0, 0), (1, 0), (1, 0)]),
            Obstruction(Perm((0, 1, 2)), [(0, 0), (1, 0), (3, 0)]),
            Obstruction(Perm((0, 1, 2)), [(0, 0), (3, 0), (3, 0)]),
            Obstruction(Perm((0, 1, 2)), [(1, 0), (1, 0), (4, 0)]),
            Obstruction(Perm((0, 1, 2)), [(1, 0), (3, 0), (4, 0)]),
            Obstruction(Perm((0, 1, 2)), [(3, 0), (3, 0), (4, 0)]),
            Obstruction(Perm((0, 2, 1)), [(0, 1), (1, 1), (1, 1)]),
            Obstruction(Perm((0, 2, 1)), [(0, 1), (1, 1), (3, 1)]),
            Obstruction(Perm((0, 2, 1)), [(0, 3), (1, 3), (1, 3)]),
            Obstruction(Perm((0, 2, 1)), [(0, 3), (1, 3), (3, 3)]),
            Obstruction(Perm((0, 2, 1)), [(0, 4), (0, 4), (1, 4)]),
            Obstruction(Perm((0, 2, 1)), [(0, 4), (0, 4), (3, 4)]),
            Obstruction(Perm((0, 2, 1)), [(0, 4), (1, 4), (1, 4)]),
            Obstruction(Perm((0, 2, 1)), [(0, 4), (1, 4), (3, 4)]),
            Obstruction(Perm((0, 2, 1)), [(0, 4), (3, 4), (3, 4)]),
        ],
        requirements=[
            [Requirement(Perm((0,)), [(2, 2)])],
            [
                Requirement(Perm((0, 1)), [(0, 0), (0, 0)]),
                Requirement(Perm((0, 1)), [(0, 0), (4, 0)]),
            ],
            [Requirement(Perm((0, 1)), [(0, 1), (3, 1)])],
            [
                Requirement(Perm((0, 1)), [(1, 1), (4, 1)]),
                Requirement(Perm((0,)), [(4, 3)]),
                Requirement(Perm((0,)), [(4, 4)]),
                Requirement(Perm((0, 1)), [(3, 1), (4, 1)]),
            ],
        ],
    )
    assert tiling == tiling2

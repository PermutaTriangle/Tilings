import pytest

from comb_spec_searcher import DisjointUnion
from comb_spec_searcher.strategies import Rule
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.strategies import (
    AllPlacementsFactory,
    PatternPlacementFactory,
    RowAndColumnPlacementFactory,
)
from tilings.strategies.requirement_placement import RequirementPlacementStrategy

pytest_plugins = [
    "tests.fixtures.obstructions_requirements",
    "tests.fixtures.simple_tiling",
    "tests.fixtures.diverse_tiling",
    "tests.fixtures.no_point_tiling",
]


@pytest.fixture
def tiling1():
    t = Tiling(
        obstructions=(
            GriddedPerm(Perm((2, 1, 0)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 2),) * 3),
            GriddedPerm(Perm((2, 0, 1)), ((3, 0),) * 3),
            GriddedPerm(Perm((1, 0)), ((1, 1),) * 2),
            GriddedPerm(Perm((1, 0)), ((2, 2),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 1), (2, 2))),
        )
    )
    return t


@pytest.fixture
def t_fully_placed():
    return Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 1), (1, 1))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (1, 1))),
        ],
        requirements=[[GriddedPerm(Perm((0,)), ((1, 1),))]],
    )


@pytest.fixture
def t_row_placed():
    return Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (0, 1))),
        ],
        requirements=[[GriddedPerm(Perm((0,)), ((0, 1),))]],
    )


@pytest.fixture
def t_row_placed2():
    return Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (0, 1))),
        ],
        requirements=[[GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1)))]],
    )


@pytest.fixture
def t_col_placed():
    return Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 0), (1, 0))),
        ],
        requirements=[[GriddedPerm(Perm((0,)), ((1, 0),))]],
    )


@pytest.fixture
def t_col_placed2():
    return Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 0), (1, 0))),
        ],
        requirements=[[GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0)))]],
    )


@pytest.fixture
def tiling2():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((3, 3),) * 2),
            GriddedPerm(Perm((0, 1)), ((4, 3),) * 2),
            GriddedPerm(Perm((0, 1)), ((4, 3),) * 2),
            GriddedPerm(Perm((0, 1, 2)), ((2, 3),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 2),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((3, 2),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((4, 2),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 1))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 2), (3, 2), (4, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (1, 1))),
        ],
        requirements=[
            [GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1)))],
            [
                GriddedPerm(Perm((0, 1)), ((2, 3), (3, 3))),
                GriddedPerm(Perm((0, 1)), ((3, 3), (4, 3))),
            ],
        ],
    )
    return t


@pytest.fixture
def placement1(tiling1):
    return list(PatternPlacementFactory()(tiling1))


@pytest.fixture
def placement1ownrow(tiling1):
    return list(
        PatternPlacementFactory(partial=True, dirs=(DIR_NORTH, DIR_SOUTH))(tiling1)
    )


@pytest.fixture
def placement1owncol(tiling1):
    return list(
        PatternPlacementFactory(partial=True, dirs=(DIR_WEST, DIR_EAST))(tiling1)
    )


@pytest.fixture
def placement2(tiling2):
    return list(PatternPlacementFactory()(tiling2))


@pytest.fixture
def placement2ownrow(tiling2):
    return list(
        PatternPlacementFactory(partial=True, dirs=(DIR_NORTH, DIR_SOUTH))(tiling2)
    )


@pytest.fixture
def placement2owncol(tiling2):
    return list(
        PatternPlacementFactory(partial=True, dirs=(DIR_WEST, DIR_EAST))(tiling2)
    )


@pytest.fixture
def placement_only_west():
    t = Tiling(
        obstructions=[GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3)],
        requirements=[[GriddedPerm(Perm((0,)), ((0, 0),))]],
    )
    return list(PatternPlacementFactory(dirs=[DIR_WEST])(t))


def test_row_placement():
    t = Tiling.from_string("132")
    row_placement = RowAndColumnPlacementFactory(
        place_col=False, place_row=True, partial=False
    )
    partial_row_placement = RowAndColumnPlacementFactory(
        place_col=False, place_row=True, partial=True
    )
    assert len(list(row_placement(t))) == 2
    assert len(list(partial_row_placement(t))) == 2


def test_col_placement():
    t = Tiling.from_string("132")
    col_placement = RowAndColumnPlacementFactory(
        place_col=True, place_row=False, partial=False
    )
    partial_col_placement = RowAndColumnPlacementFactory(
        place_col=True, place_row=False, partial=True
    )
    assert len(list(col_placement(t))) == 2
    assert len(list(partial_col_placement(t))) == 2


def test_row_col_placement():
    t = Tiling.from_string("132")
    cr_placement = RowAndColumnPlacementFactory(
        place_col=True, place_row=True, partial=False
    )
    partial_cr_placement = RowAndColumnPlacementFactory(
        place_col=True, place_row=True, partial=True
    )
    assert len(list(cr_placement(t))) == 4
    assert len(list(partial_cr_placement(t))) == 4


def test_all_placements():
    t = Tiling(
        obstructions=[GriddedPerm(Perm((0, 1)), ((0, 0),) * 2)],
        requirements=[[GriddedPerm(Perm((0,)), ((0, 0),))]],
    )
    rules = list(AllPlacementsFactory()(t))
    # for rule in rules:
    #     print(rule)
    assert len(rules) == 8


def test_point_placement(diverse_tiling, no_point_tiling):
    point_placement = PatternPlacementFactory(point_only=True)
    requirement_placement = PatternPlacementFactory(point_only=False)
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
            GriddedPerm(Perm((0,)), [(1, 0)]),
            GriddedPerm(Perm((0,)), [(1, 2)]),
            GriddedPerm(Perm((0,)), [(2, 0)]),
            GriddedPerm(Perm((0,)), [(2, 2)]),
            GriddedPerm(Perm((0, 1)), [(2, 1), (2, 1)]),
            GriddedPerm(Perm((0, 1)), [(4, 3), (4, 3)]),
            GriddedPerm(Perm((1, 0)), [(2, 1), (2, 1)]),
            GriddedPerm(Perm((1, 0)), [(4, 3), (4, 3)]),
            GriddedPerm(Perm((0, 2, 3, 1)), [(0, 0), (1, 3), (1, 3), (4, 0)]),
            GriddedPerm(Perm((0, 2, 3, 1)), [(0, 0), (1, 3), (1, 3), (4, 2)]),
            GriddedPerm(Perm((0, 2, 3, 1)), [(0, 0), (1, 3), (3, 3), (4, 0)]),
            GriddedPerm(Perm((0, 2, 3, 1)), [(0, 0), (1, 3), (3, 3), (4, 2)]),
            GriddedPerm(Perm((0, 2, 3, 1)), [(0, 0), (3, 3), (3, 3), (4, 0)]),
            GriddedPerm(Perm((0, 2, 3, 1)), [(0, 0), (3, 3), (3, 3), (4, 2)]),
            GriddedPerm(Perm((0, 2, 3, 1)), [(0, 2), (1, 3), (1, 3), (4, 2)]),
            GriddedPerm(Perm((0, 2, 3, 1)), [(0, 2), (1, 3), (3, 3), (4, 2)]),
            GriddedPerm(Perm((0, 2, 3, 1)), [(0, 2), (3, 3), (3, 3), (4, 2)]),
        ],
        requirements=[
            [GriddedPerm(Perm((0,)), [(2, 1)])],
            [GriddedPerm(Perm((0,)), [(4, 3)])],
            [GriddedPerm(Perm((0,)), [(4, 0)]), GriddedPerm(Perm((0,)), [(4, 2)])],
            [
                GriddedPerm(Perm((1, 0)), [(0, 4), (0, 3)]),
                GriddedPerm(Perm((0, 2, 1)), [(0, 3), (0, 4), (1, 4)]),
                GriddedPerm(Perm((0, 2, 1)), [(0, 3), (0, 4), (3, 4)]),
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
                GriddedPerm(Perm((0,)), [(2, 0)]),
                GriddedPerm(Perm((0,)), [(2, 2)]),
                GriddedPerm(Perm((0, 1)), [(1, 0), (1, 0)]),
                GriddedPerm(Perm((0, 1)), [(1, 0), (1, 2)]),
                GriddedPerm(Perm((0, 1)), [(1, 2), (1, 2)]),
                GriddedPerm(Perm((0, 1)), [(3, 1), (3, 1)]),
                GriddedPerm(Perm((0, 1)), [(2, 3), (2, 3)]),
                GriddedPerm(Perm((0, 1)), [(2, 3), (4, 3)]),
                GriddedPerm(Perm((0, 1)), [(4, 3), (4, 3)]),
                GriddedPerm(Perm((1, 0)), [(1, 0), (1, 0)]),
                GriddedPerm(Perm((1, 0)), [(1, 2), (1, 0)]),
                GriddedPerm(Perm((1, 0)), [(1, 2), (1, 2)]),
                GriddedPerm(Perm((1, 0)), [(3, 1), (3, 1)]),
                GriddedPerm(Perm((1, 0)), [(2, 3), (2, 3)]),
                GriddedPerm(Perm((1, 0)), [(2, 3), (4, 3)]),
                GriddedPerm(Perm((1, 0)), [(4, 3), (4, 3)]),
                GriddedPerm(Perm((0, 1, 2)), [(0, 0), (1, 3), (1, 3)]),
                GriddedPerm(Perm((0, 2, 3, 1)), [(0, 2), (1, 3), (1, 3), (4, 2)]),
            ],
            requirements=[
                [GriddedPerm(Perm((0,)), [(3, 1)])],
                [GriddedPerm(Perm((0,)), [(1, 0)]), GriddedPerm(Perm((0,)), [(1, 2)])],
                [GriddedPerm(Perm((0,)), [(2, 3)]), GriddedPerm(Perm((0,)), [(4, 3)])],
                [
                    GriddedPerm(Perm((1, 0)), [(0, 4), (0, 3)]),
                    GriddedPerm(Perm((0, 2, 1)), [(0, 3), (0, 4), (1, 4)]),
                ],
            ],
        )
    )
    tiling = diverse_tiling.place_point_of_gridded_permutation(
        diverse_tiling.requirements[1][0], 0, DIR_WEST
    )
    assert tiling == Tiling(
        obstructions=[
            GriddedPerm(Perm((0,)), [(2, 0)]),
            GriddedPerm(Perm((0,)), [(2, 2)]),
            GriddedPerm(Perm((0, 1)), [(1, 0), (1, 0)]),
            GriddedPerm(Perm((0, 1)), [(1, 0), (1, 2)]),
            GriddedPerm(Perm((0, 1)), [(1, 2), (1, 2)]),
            GriddedPerm(Perm((0, 1)), [(3, 1), (3, 1)]),
            GriddedPerm(Perm((0, 1)), [(2, 3), (2, 3)]),
            GriddedPerm(Perm((0, 1)), [(2, 3), (4, 3)]),
            GriddedPerm(Perm((0, 1)), [(4, 3), (4, 3)]),
            GriddedPerm(Perm((1, 0)), [(1, 0), (1, 0)]),
            GriddedPerm(Perm((1, 0)), [(1, 2), (1, 0)]),
            GriddedPerm(Perm((1, 0)), [(1, 2), (1, 2)]),
            GriddedPerm(Perm((1, 0)), [(3, 1), (3, 1)]),
            GriddedPerm(Perm((1, 0)), [(2, 3), (2, 3)]),
            GriddedPerm(Perm((1, 0)), [(2, 3), (4, 3)]),
            GriddedPerm(Perm((1, 0)), [(4, 3), (4, 3)]),
            GriddedPerm(Perm((0, 1, 2)), [(0, 0), (1, 3), (1, 3)]),
            GriddedPerm(Perm((0, 2, 3, 1)), [(0, 2), (1, 3), (1, 3), (4, 2)]),
        ],
        requirements=[
            [GriddedPerm(Perm((0,)), [(3, 1)])],
            [GriddedPerm(Perm((0,)), [(1, 0)]), GriddedPerm(Perm((0,)), [(1, 2)])],
            [GriddedPerm(Perm((0,)), [(2, 3)]), GriddedPerm(Perm((0,)), [(4, 3)])],
            [
                GriddedPerm(Perm((1, 0)), [(0, 4), (0, 3)]),
                GriddedPerm(Perm((0, 2, 1)), [(0, 3), (0, 4), (1, 4)]),
            ],
        ],
    )

    tiling = Tiling(requirements=[[GriddedPerm(Perm((0,)), [(0, 0)])]])
    assert tiling.place_point_of_gridded_permutation(
        tiling.requirements[0][0], 0, DIR_SOUTH
    ) == Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)]),
            GriddedPerm(Perm((1, 0)), [(0, 0), (0, 0)]),
        ],
        requirements=[[GriddedPerm(Perm((0,)), [(0, 0)])]],
    )


def test_place_point_of_requirement(no_point_tiling):
    tiling = no_point_tiling.place_point_of_gridded_permutation(
        no_point_tiling.requirements[2][0], 1, DIR_WEST
    )
    tiling2 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), [(0, 1), (1, 3)]),
            GriddedPerm(Perm((0, 1)), [(2, 2), (2, 2)]),
            GriddedPerm(Perm((1, 0)), [(0, 1), (0, 1)]),
            GriddedPerm(Perm((1, 0)), [(0, 3), (0, 1)]),
            GriddedPerm(Perm((1, 0)), [(0, 3), (0, 3)]),
            GriddedPerm(Perm((1, 0)), [(2, 2), (2, 2)]),
            GriddedPerm(Perm((0, 1, 2)), [(0, 0), (1, 0), (1, 0)]),
            GriddedPerm(Perm((0, 1, 2)), [(0, 0), (1, 0), (3, 0)]),
            GriddedPerm(Perm((0, 1, 2)), [(0, 0), (3, 0), (3, 0)]),
            GriddedPerm(Perm((0, 1, 2)), [(1, 0), (1, 0), (4, 0)]),
            GriddedPerm(Perm((0, 1, 2)), [(1, 0), (3, 0), (4, 0)]),
            GriddedPerm(Perm((0, 1, 2)), [(3, 0), (3, 0), (4, 0)]),
            GriddedPerm(Perm((0, 2, 1)), [(0, 1), (1, 1), (1, 1)]),
            GriddedPerm(Perm((0, 2, 1)), [(0, 1), (1, 1), (3, 1)]),
            GriddedPerm(Perm((0, 2, 1)), [(0, 3), (1, 3), (1, 3)]),
            GriddedPerm(Perm((0, 2, 1)), [(0, 3), (1, 3), (3, 3)]),
            GriddedPerm(Perm((0, 2, 1)), [(0, 4), (0, 4), (1, 4)]),
            GriddedPerm(Perm((0, 2, 1)), [(0, 4), (0, 4), (3, 4)]),
            GriddedPerm(Perm((0, 2, 1)), [(0, 4), (1, 4), (1, 4)]),
            GriddedPerm(Perm((0, 2, 1)), [(0, 4), (1, 4), (3, 4)]),
            GriddedPerm(Perm((0, 2, 1)), [(0, 4), (3, 4), (3, 4)]),
        ],
        requirements=[
            [GriddedPerm(Perm((0,)), [(2, 2)])],
            [
                GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)]),
                GriddedPerm(Perm((0, 1)), [(0, 0), (4, 0)]),
            ],
            [GriddedPerm(Perm((0, 1)), [(0, 1), (3, 1)])],
            [
                GriddedPerm(Perm((0, 1)), [(1, 1), (4, 1)]),
                GriddedPerm(Perm((0,)), [(4, 3)]),
                GriddedPerm(Perm((0,)), [(4, 4)]),
                GriddedPerm(Perm((0, 1)), [(3, 1), (4, 1)]),
            ],
        ],
    )
    assert tiling == tiling2


# # ------------------------------------------------------------
# #       Tests for RequirementPlacement Class
# # ------------------------------------------------------------


def test_formal_step():
    # row placements
    row_gps = [GriddedPerm(Perm((0,)), ((0, 0),)), GriddedPerm(Perm((0,)), ((1, 0),))]
    placement_class = RequirementPlacementStrategy(
        gps=row_gps, indices=(0, 0), direction=1, own_col=True, own_row=True,
    )
    assert placement_class.formal_step() == "placing the topmost point in row 0"
    placement_class = RequirementPlacementStrategy(
        gps=row_gps, indices=(0, 0), direction=3, own_col=True, own_row=True,
    )
    assert placement_class.formal_step() == "placing the bottommost point in row 0"
    placement_class = RequirementPlacementStrategy(
        gps=row_gps, indices=(0, 0), direction=1, own_col=False, own_row=True,
    )
    assert (
        placement_class.formal_step() == "partially placing the topmost point in row 0"
    )
    placement_class = RequirementPlacementStrategy(
        gps=row_gps, indices=(0, 0), direction=3, own_col=False, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the bottommost point in row 0"
    )

    # column placements
    col_gps = [GriddedPerm(Perm((0,)), ((2, 3),)), GriddedPerm(Perm((0,)), ((2, 1),))]
    placement_class = RequirementPlacementStrategy(
        gps=col_gps, indices=(0, 0), direction=0, own_col=True, own_row=True,
    )
    assert placement_class.formal_step() == "placing the rightmost point in column 2"
    placement_class = RequirementPlacementStrategy(
        gps=col_gps, indices=(0, 0), direction=2, own_col=True, own_row=True,
    )
    assert placement_class.formal_step() == "placing the leftmost point in column 2"
    placement_class = RequirementPlacementStrategy(
        gps=col_gps, indices=(0, 0), direction=0, own_col=True, own_row=False,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the rightmost point in column 2"
    )
    placement_class = RequirementPlacementStrategy(
        gps=col_gps, indices=(0, 0), direction=2, own_col=True, own_row=False,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the leftmost point in column 2"
    )

    # point placements
    point_gps = (GriddedPerm(Perm((0,)), ((2, 2),)),)
    placement_class = RequirementPlacementStrategy(
        gps=point_gps, indices=(0,), direction=0, own_col=True, own_row=True,
    )
    assert placement_class.formal_step() == "placing the rightmost point in cell (2, 2)"
    placement_class = RequirementPlacementStrategy(
        gps=point_gps, indices=(0,), direction=1, own_col=True, own_row=True,
    )
    assert placement_class.formal_step() == "placing the topmost point in cell (2, 2)"
    placement_class = RequirementPlacementStrategy(
        gps=point_gps, indices=(0,), direction=2, own_col=True, own_row=True,
    )
    assert placement_class.formal_step() == "placing the leftmost point in cell (2, 2)"
    placement_class = RequirementPlacementStrategy(
        gps=point_gps, indices=(0,), direction=3, own_col=True, own_row=True,
    )
    assert (
        placement_class.formal_step() == "placing the bottommost point in cell (2, 2)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=point_gps, indices=(0,), direction=0, own_col=True, own_row=False,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the rightmost point in cell (2, 2)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=point_gps, indices=(0,), direction=1, own_col=False, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the topmost point in cell (2, 2)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=point_gps, indices=(0,), direction=2, own_col=True, own_row=False,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the leftmost point in cell (2, 2)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=point_gps, indices=(0,), direction=3, own_col=False, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the bottommost point in cell (2, 2)"
    )

    # pattern placements
    pattern_gps = (GriddedPerm(Perm((1, 0, 2, 3)), ((0, 1), (0, 0), (1, 0), (1, 1))),)
    placement_class = RequirementPlacementStrategy(
        gps=pattern_gps, indices=(3,), direction=0, own_col=True, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "placing the rightmost (3, 3) point in 1023: (0, 1), (0, 0), (1, 0), (1, 1)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=pattern_gps, indices=(2,), direction=1, own_col=True, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "placing the topmost (2, 2) point in 1023: (0, 1), (0, 0), (1, 0), (1, 1)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=pattern_gps, indices=(1,), direction=2, own_col=True, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "placing the leftmost (1, 0) point in 1023: (0, 1), (0, 0), (1, 0), (1, 1)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=pattern_gps, indices=(0,), direction=3, own_col=True, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "placing the bottommost (0, 1) point in 1023: (0, 1), (0, 0), (1, 0), (1, 1)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=pattern_gps, indices=(3,), direction=0, own_col=True, own_row=False,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the rightmost (3, 3) point in "
        "1023: (0, 1), (0, 0), (1, 0), (1, 1)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=pattern_gps, indices=(2,), direction=1, own_col=False, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the topmost (2, 2) point in "
        "1023: (0, 1), (0, 0), (1, 0), (1, 1)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=pattern_gps, indices=(1,), direction=2, own_col=True, own_row=False,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the leftmost (1, 0) point in "
        "1023: (0, 1), (0, 0), (1, 0), (1, 1)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=pattern_gps, indices=(0,), direction=3, own_col=False, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the bottommost (0, 1) point in "
        "1023: (0, 1), (0, 0), (1, 0), (1, 1)"
    )

    # localised pattern placement
    localised_pattern_gps = (
        GriddedPerm(Perm((0, 2, 1, 3)), ((2, 2), (2, 2), (2, 2), (2, 2))),
    )
    placement_class = RequirementPlacementStrategy(
        gps=localised_pattern_gps,
        indices=(3,),
        direction=0,
        own_col=True,
        own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "placing the rightmost (3, 3) point in 0213 in cell (2, 2)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=localised_pattern_gps,
        indices=(2,),
        direction=1,
        own_col=True,
        own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "placing the topmost (2, 1) point in 0213 in cell (2, 2)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=localised_pattern_gps,
        indices=(1,),
        direction=2,
        own_col=True,
        own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "placing the leftmost (1, 2) point in 0213 in cell (2, 2)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=localised_pattern_gps,
        indices=(0,),
        direction=3,
        own_col=True,
        own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "placing the bottommost (0, 0) point in 0213 in cell (2, 2)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=localised_pattern_gps,
        indices=(3,),
        direction=0,
        own_col=True,
        own_row=False,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the rightmost (3, 3) point in 0213 in cell (2, 2)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=localised_pattern_gps,
        indices=(2,),
        direction=1,
        own_col=False,
        own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the topmost (2, 1) point in 0213 in cell (2, 2)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=localised_pattern_gps,
        indices=(1,),
        direction=2,
        own_col=True,
        own_row=False,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the leftmost (1, 2) point in 0213 in cell (2, 2)"
    )
    placement_class = RequirementPlacementStrategy(
        gps=localised_pattern_gps,
        indices=(0,),
        direction=3,
        own_col=False,
        own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the bottommost (0, 0) point in 0213 in cell (2, 2)"
    )
    # arbitrary requirement placements
    req_gps = [
        GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1))),
        GriddedPerm(Perm((1, 0)), ((1, 1), (2, 1))),
    ]
    placement_class = RequirementPlacementStrategy(
        gps=req_gps, indices=(0, 0), direction=0, own_col=True, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "placing the rightmost point at indices (0, 0) "
        "from the requirement (01: (0, 0), (1, 1), 10: (1, 1), (2, 1))"
    )
    placement_class = RequirementPlacementStrategy(
        gps=req_gps, indices=(0, 1), direction=1, own_col=True, own_row=True,
    )
    assert (
        placement_class.formal_step() == "placing the topmost point at indices (0, 1) "
        "from the requirement (01: (0, 0), (1, 1), 10: (1, 1), (2, 1))"
    )
    placement_class = RequirementPlacementStrategy(
        gps=req_gps, indices=(1, 0), direction=2, own_col=True, own_row=True,
    )
    assert (
        placement_class.formal_step() == "placing the leftmost point at indices (1, 0) "
        "from the requirement (01: (0, 0), (1, 1), 10: (1, 1), (2, 1))"
    )
    placement_class = RequirementPlacementStrategy(
        gps=req_gps, indices=(1, 1), direction=3, own_col=True, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "placing the bottommost point at indices (1, 1) "
        "from the requirement (01: (0, 0), (1, 1), 10: (1, 1), (2, 1))"
    )
    placement_class = RequirementPlacementStrategy(
        gps=req_gps, indices=(0, 0), direction=0, own_col=True, own_row=False,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the rightmost point at indices (0, 0) "
        "from the requirement (01: (0, 0), (1, 1), 10: (1, 1), (2, 1))"
    )
    placement_class = RequirementPlacementStrategy(
        gps=req_gps, indices=(0, 1), direction=1, own_col=False, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the topmost point at indices (0, 1) "
        "from the requirement (01: (0, 0), (1, 1), 10: (1, 1), (2, 1))"
    )
    placement_class = RequirementPlacementStrategy(
        gps=req_gps, indices=(1, 0), direction=2, own_col=True, own_row=False,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the leftmost point at indices (1, 0) "
        "from the requirement (01: (0, 0), (1, 1), 10: (1, 1), (2, 1))"
    )
    placement_class = RequirementPlacementStrategy(
        gps=req_gps, indices=(1, 1), direction=3, own_col=False, own_row=True,
    )
    assert (
        placement_class.formal_step()
        == "partially placing the bottommost point at indices (1, 1) "
        "from the requirement (01: (0, 0), (1, 1), 10: (1, 1), (2, 1))"
    )


def test_all_col_placement_rules(tiling1):
    print(tiling1)
    rules = list(RowAndColumnPlacementFactory(place_row=False)(tiling1))
    assert len(rules) == 8
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.children) > 1
        assert not rule.ignore_parent
        assert rule.workable
        assert isinstance(rule.constructor, DisjointUnion)
        assert rule.possibly_empty
    assert sorted(len(rule.children) for rule in rules) == [2, 2, 2, 2, 2, 2, 3, 3]


def test_all_col_placement_rules_partial(tiling1, t_col_placed):
    rules = list(RowAndColumnPlacementFactory(place_row=False, partial=True)(tiling1))
    assert len(rules) == 8
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.children) > 1
        assert not rule.ignore_parent
        assert rule.workable
        assert isinstance(rule.constructor, DisjointUnion)
        assert rule.possibly_empty
    assert sorted(len(rule.children) for rule in rules) == [2, 2, 2, 2, 2, 2, 3, 3]

    print(t_col_placed)
    rules = rules = list(
        RowAndColumnPlacementFactory(place_row=False, partial=True)(t_col_placed)
    )
    assert len(rules) == 2
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.children) > 1
        assert not rule.ignore_parent
        assert rule.workable
        assert isinstance(rule.constructor, DisjointUnion)
        assert rule.possibly_empty
    assert sorted(len(rule.children) for rule in rules) == [2, 2]


def test_all_row_placement_rules(tiling1):
    rules = list(RowAndColumnPlacementFactory(place_col=False)(tiling1))
    assert len(rules) == 6
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.children) > 1
        assert not rule.ignore_parent
        assert rule.workable
        assert isinstance(rule.constructor, DisjointUnion)
        assert rule.possibly_empty
    assert sorted(len(rule.children) for rule in rules) == [2, 2, 3, 3, 3, 3]


def test_all_row_placement_rules_partial(tiling1, t_row_placed):
    rules = list(RowAndColumnPlacementFactory(place_col=False, partial=True)(tiling1))
    assert len(rules) == 6
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.children) > 1
        assert not rule.ignore_parent
        assert rule.workable
        assert isinstance(rule.constructor, DisjointUnion)
        assert rule.possibly_empty
    assert sorted(len(rule.children) for rule in rules) == [2, 2, 3, 3, 3, 3]

    # Nothing to do if only not placing on own row
    print(t_row_placed)
    rules = list(
        RowAndColumnPlacementFactory(place_col=False, partial=True)(t_row_placed)
    )
    assert len(rules) == 2
    for rule in rules:
        print(rule)
        assert isinstance(rule, Rule)
        assert len(rule.children) > 1
        assert not rule.ignore_parent
        assert rule.workable
        assert isinstance(rule.constructor, DisjointUnion)
        assert rule.possibly_empty
    assert sorted(len(rule.children) for rule in rules) == [2, 2]


def test_all_point_placement_rules(tiling1, tiling2, placement_only_west):
    all_rules = []
    rules = list(PatternPlacementFactory(point_only=True)(tiling1))
    assert rules == []

    rules = list(PatternPlacementFactory(point_only=True)(tiling2))
    assert len(rules) == 12
    all_rules.extend(rules)

    rules = list(
        PatternPlacementFactory(
            point_only=True, partial=True, dirs=(DIR_NORTH, DIR_SOUTH)
        )(tiling2)
    )
    assert len(rules) == 6
    all_rules.extend(rules)
    rules = list(
        PatternPlacementFactory(
            point_only=True, partial=True, dirs=(DIR_EAST, DIR_WEST)
        )(tiling2)
    )
    assert len(rules) == 6
    all_rules.extend(rules)

    rules = placement_only_west
    assert len(rules) == 1
    assert rules[0].children[0] == Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 2))),
            GriddedPerm(Perm((0, 1)), ((1, 2), (1, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (0, 1))),
        ],
        requirements=[[GriddedPerm(Perm((0,)), ((0, 1),))]],
    )
    assert rules[0].formal_step == "placing the leftmost point in cell (0, 0)"
    all_rules.extend(rules)

    for rule in all_rules:
        assert isinstance(rule, Rule)
        assert len(rule.children) == 1
        assert not rule.ignore_parent
        assert rule.workable
        assert isinstance(rule.constructor, DisjointUnion)
        assert not rule.possibly_empty


def test_all_requirement_placement_rules():
    t = Tiling(
        obstructions=[GriddedPerm(Perm((1, 0)), ((0, 0),) * 2)],
        requirements=[[GriddedPerm(Perm((0, 1)), ((0, 0),) * 2)]],
    )
    rules = list(PatternPlacementFactory()(t))
    assert len(rules) == 12
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.children) == 1
        assert not rule.ignore_parent
        assert rule.workable
        assert isinstance(rule.constructor, DisjointUnion)
        assert not rule.possibly_empty
    comb_classes = set(rule.children[0] for rule in rules)
    assert len(comb_classes) == 4
    assert (
        Tiling(
            obstructions=[
                GriddedPerm(Perm((0,)), ((0, 1),)),
                GriddedPerm(Perm((0,)), ((0, 2),)),
                GriddedPerm(Perm((0,)), ((1, 0),)),
                GriddedPerm(Perm((0,)), ((1, 2),)),
                GriddedPerm(Perm((0,)), ((2, 0),)),
                GriddedPerm(Perm((0,)), ((2, 1),)),
                GriddedPerm(Perm((0, 1)), ((1, 1), (1, 1))),
                GriddedPerm(Perm((0, 1)), ((2, 2), (2, 2))),
                GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0))),
                GriddedPerm(Perm((1, 0)), ((1, 1), (1, 1))),
                GriddedPerm(Perm((1, 0)), ((2, 2), (2, 2))),
            ],
            requirements=[
                [GriddedPerm(Perm((0,)), ((1, 1),))],
                [GriddedPerm(Perm((0,)), ((2, 2),))],
            ],
        )
        in comb_classes
    )


def test_not_equivalent_to_itself(
    t_fully_placed, t_row_placed, t_row_placed2, t_col_placed, t_col_placed2
):
    """
    We don't want the rule to say the tiling is equivalent to itself.
    The opposite can create situation where the tiling is mark as unworkable
    because of the ignore parent flag.
    """
    placement_fully_placed = list(PatternPlacementFactory()(t_fully_placed))
    placement_fully_placed_partial_col = list(
        PatternPlacementFactory(partial=True, dirs=(DIR_WEST, DIR_EAST))(t_fully_placed)
    )
    placement_fully_placed_partial_row = list(
        PatternPlacementFactory(partial=True, dirs=(DIR_NORTH, DIR_SOUTH))(
            t_fully_placed
        )
    )
    placement_row_placed = list(PatternPlacementFactory()(t_row_placed))
    placement_row_placed_partial_col = list(
        PatternPlacementFactory(partial=True, dirs=(DIR_EAST, DIR_WEST))(t_row_placed)
    )
    placement_row_placed_partial_row = list(
        PatternPlacementFactory(partial=True, dirs=(DIR_NORTH, DIR_SOUTH))(t_row_placed)
    )
    placement_row_placed2 = list(PatternPlacementFactory()(t_row_placed2))
    placement_col_placed = list(PatternPlacementFactory()(t_col_placed))
    placement_col_placed_partial_col = list(
        PatternPlacementFactory(partial=True, dirs=(DIR_EAST, DIR_WEST))(t_col_placed)
    )
    placement_col_placed_partial_row = list(
        PatternPlacementFactory(partial=True, dirs=(DIR_NORTH, DIR_SOUTH))(t_col_placed)
    )
    placement_col_placed2 = list(PatternPlacementFactory()(t_col_placed2))
    print("fully placed")
    print(t_fully_placed)
    print("row placed")
    print(t_row_placed)
    print("row placed 2")
    print(t_row_placed2)
    print("col placed")
    print(t_col_placed)
    print("cold placed 2")
    print(t_col_placed2)
    # Requirement placements
    assert len(placement_fully_placed) == 0
    assert len(placement_fully_placed_partial_row) == 0
    assert len(placement_fully_placed_partial_col) == 0
    assert len(placement_row_placed) == 4
    assert len(placement_row_placed_partial_col) == 2
    assert len(placement_row_placed_partial_row) == 0
    assert len(placement_row_placed2) == 16
    assert len(placement_col_placed) == 4
    assert len(placement_col_placed_partial_col) == 0
    assert len(placement_col_placed_partial_row) == 2
    assert len(placement_col_placed2) == 16
    # Check that the class are correct
    assert all(r.children[0] != t_fully_placed for r in placement_fully_placed)
    assert all(r.children[0] != t_row_placed for r in placement_row_placed)
    assert all(r.children[0] != t_row_placed2 for r in placement_row_placed2)
    assert all(r.children[0] != t_col_placed for r in placement_col_placed)
    assert all(r.children[0] != t_col_placed2 for r in placement_col_placed2)

    placement_fully_placed = list(
        PatternPlacementFactory(point_only=True)(t_fully_placed)
    )
    placement_row_placed = list(PatternPlacementFactory(point_only=True)(t_row_placed))
    placement_row_placed2 = list(
        PatternPlacementFactory(point_only=True)(t_row_placed2)
    )
    placement_col_placed = list(PatternPlacementFactory(point_only=True)(t_col_placed))
    placement_col_placed2 = list(
        PatternPlacementFactory(point_only=True)(t_col_placed2)
    )
    # Point placements
    assert len(placement_fully_placed) == 0
    assert len(placement_row_placed) == 4
    assert len(placement_row_placed2) == 8
    assert len(placement_col_placed) == 4
    assert len(placement_col_placed2) == 8
    # Check that the class are correct
    assert all(r.children[0] != t_fully_placed for r in placement_fully_placed)
    assert all(r.children[0] != t_row_placed for r in placement_row_placed)
    assert all(r.children[0] != t_row_placed2 for r in placement_row_placed2)
    assert all(r.children[0] != t_col_placed for r in placement_col_placed)
    assert all(r.children[0] != t_col_placed2 for r in placement_col_placed2)

    placement_fully_placed = list(
        RowAndColumnPlacementFactory(place_col=False)(t_fully_placed)
    )
    placement_fully_placed_partial_col = list(
        RowAndColumnPlacementFactory(place_col=False, partial=True)(t_fully_placed)
    )
    placement_fully_placed_partial_row = list(
        RowAndColumnPlacementFactory(place_col=False, partial=True)(t_fully_placed)
    )
    placement_row_placed = list(
        RowAndColumnPlacementFactory(place_col=False)(t_row_placed)
    )
    placement_row_placed_partial_col = list(
        RowAndColumnPlacementFactory(place_col=False, partial=True)(t_row_placed)
    )
    placement_row_placed_partial_row = list(
        RowAndColumnPlacementFactory(place_col=False, partial=True)(t_col_placed)
    )
    placement_row_placed2 = list(
        RowAndColumnPlacementFactory(place_col=False)(t_row_placed2)
    )
    placement_col_placed = list(
        RowAndColumnPlacementFactory(place_col=False)(t_col_placed)
    )
    placement_col_placed2 = list(
        RowAndColumnPlacementFactory(place_col=False)(t_col_placed2)
    )
    # Row placement
    assert len(placement_fully_placed) == 2
    assert len(placement_fully_placed_partial_col) == 2
    assert len(placement_fully_placed_partial_row) == 2
    assert len(placement_row_placed) == 4
    assert len(placement_row_placed_partial_col) == 2
    assert len(placement_row_placed_partial_row) == 2
    assert len(placement_row_placed2) == 4
    assert len(placement_col_placed) == 2
    assert len(placement_col_placed2) == 2

    placement_fully_placed = list(
        RowAndColumnPlacementFactory(place_row=False)(t_fully_placed)
    )
    placement_fully_placed_partial_col = list(
        RowAndColumnPlacementFactory(place_row=False, partial=True)(t_fully_placed)
    )
    placement_fully_placed_partial_row = list(
        RowAndColumnPlacementFactory(place_row=False, partial=True)(t_fully_placed)
    )
    placement_row_placed = list(
        RowAndColumnPlacementFactory(place_row=False)(t_row_placed)
    )
    placement_row_placed2 = list(
        RowAndColumnPlacementFactory(place_row=False)(t_row_placed2)
    )
    placement_col_placed = list(
        RowAndColumnPlacementFactory(place_row=False)(t_col_placed)
    )
    placement_col_placed2 = list(
        RowAndColumnPlacementFactory(place_row=False)(t_col_placed2)
    )
    # Col placement
    assert len(placement_fully_placed) == 2
    assert len(placement_fully_placed_partial_col) == 2
    assert len(placement_fully_placed_partial_row) == 2
    assert len(placement_row_placed) == 2
    assert len(placement_row_placed2) == 2
    assert len(placement_col_placed) == 4
    assert len(placement_col_placed2) == 4


def test_all_requirement_placement_rules_partial(tiling2):
    rules = list(
        PatternPlacementFactory(partial=True, dirs=(DIR_WEST, DIR_EAST))(tiling2)
    )
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.children) == 1
        assert rule.workable
        assert isinstance(rule.constructor, DisjointUnion)
        assert not rule.possibly_empty
    rules = list(
        PatternPlacementFactory(partial=True, dirs=(DIR_NORTH, DIR_SOUTH))(tiling2)
    )
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.children) == 1
        assert rule.workable
        assert isinstance(rule.constructor, DisjointUnion)
        assert not rule.possibly_empty


def test_reverse_rule():
    tiling = Tiling(
        obstructions=(
            GriddedPerm(Perm((0, 2, 1, 3)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm(Perm((1, 2, 3, 0)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm(Perm((2, 0, 1, 3)), ((0, 0), (0, 0), (0, 0), (0, 0))),
        ),
        requirements=((GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),),),
    )
    strategy = RequirementPlacementStrategy(
        gps=(GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),),
        indices=(1,),
        direction=0,
        own_col=True,
        own_row=True,
        ignore_parent=False,
        include_empty=False,
    )
    rule = strategy(tiling)
    for i in range(6):
        rule.sanity_check(i)
    reverse_rule = rule.to_reverse_rule()
    for i in range(6):
        reverse_rule.sanity_check(i)


def test_reverse_rule_non_empty_children():
    strategy = RequirementPlacementStrategy(
        gps=(
            GriddedPerm(Perm((0,)), ((5, 1),)),
            GriddedPerm(Perm((1, 0)), ((2, 3), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((2, 6), (2, 0))),
        ),
        indices=(0, 1, 0),
        direction=2,
        own_col=True,
        own_row=True,
        ignore_parent=False,
        include_empty=False,
    )
    tiling = Tiling(
        obstructions=(
            GriddedPerm(Perm((0, 1)), ((1, 2), (1, 2))),
            GriddedPerm(Perm((0, 1)), ((2, 3), (2, 6))),
            GriddedPerm(Perm((0, 1)), ((2, 3), (4, 4))),
            GriddedPerm(Perm((0, 1)), ((2, 6), (2, 6))),
            GriddedPerm(Perm((0, 1)), ((3, 5), (3, 5))),
            GriddedPerm(Perm((0, 1)), ((4, 4), (4, 4))),
            GriddedPerm(Perm((0, 1)), ((5, 1), (5, 1))),
            GriddedPerm(Perm((1, 0)), ((0, 6), (4, 4))),
            GriddedPerm(Perm((1, 0)), ((0, 6), (5, 1))),
            GriddedPerm(Perm((1, 0)), ((1, 2), (1, 2))),
            GriddedPerm(Perm((1, 0)), ((2, 6), (2, 3))),
            GriddedPerm(Perm((1, 0)), ((3, 5), (3, 5))),
            GriddedPerm(Perm((1, 0)), ((5, 7), (5, 7))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 3), (0, 3), (0, 6))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 3), (0, 3), (2, 6))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 3), (0, 3), (4, 4))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 3), (0, 6), (0, 6))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 3), (0, 6), (2, 6))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 6))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (4, 4))),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (5, 1))),
            GriddedPerm(Perm((0, 2, 1)), ((0, 3), (0, 6), (0, 3))),
            GriddedPerm(Perm((0, 2, 1)), ((0, 3), (0, 6), (2, 3))),
            GriddedPerm(Perm((0, 2, 1)), ((2, 0), (2, 3), (5, 1))),
            GriddedPerm(Perm((0, 2, 1)), ((2, 0), (2, 6), (2, 0))),
            GriddedPerm(Perm((0, 2, 1)), ((2, 0), (5, 7), (5, 1))),
            GriddedPerm(Perm((0, 2, 1)), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm(Perm((1, 2, 0)), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((1, 2, 0)), ((2, 0), (2, 3), (2, 0))),
            GriddedPerm(Perm((1, 2, 0)), ((2, 0), (2, 6), (2, 0))),
            GriddedPerm(Perm((1, 2, 0)), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm(Perm((1, 2, 0)), ((5, 1), (5, 7), (5, 1))),
            GriddedPerm(Perm((2, 0, 1)), ((0, 3), (0, 3), (0, 3))),
            GriddedPerm(Perm((2, 0, 1)), ((0, 6), (0, 3), (0, 3))),
            GriddedPerm(Perm((2, 0, 1)), ((0, 6), (0, 3), (0, 6))),
            GriddedPerm(Perm((2, 0, 1)), ((0, 6), (0, 6), (0, 6))),
            GriddedPerm(Perm((2, 0, 1)), ((0, 6), (0, 6), (2, 6))),
            GriddedPerm(Perm((2, 0, 1)), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm(Perm((2, 0, 1)), ((2, 6), (2, 0), (4, 4))),
            GriddedPerm(Perm((2, 1, 0)), ((0, 3), (2, 3), (2, 0))),
            GriddedPerm(Perm((2, 1, 0)), ((0, 3), (2, 3), (5, 1))),
            GriddedPerm(Perm((2, 1, 0)), ((0, 6), (2, 3), (2, 0))),
            GriddedPerm(Perm((2, 1, 0)), ((0, 6), (2, 6), (2, 0))),
            GriddedPerm(Perm((0, 1, 3, 2)), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm(Perm((0, 1, 3, 2)), ((0, 3), (0, 3), (0, 3), (2, 3))),
            GriddedPerm(Perm((0, 1, 3, 2)), ((0, 3), (0, 3), (2, 3), (2, 3))),
            GriddedPerm(Perm((0, 1, 3, 2)), ((0, 6), (0, 6), (0, 6), (0, 6))),
            GriddedPerm(Perm((0, 1, 3, 2)), ((0, 6), (0, 6), (0, 6), (2, 6))),
            GriddedPerm(Perm((0, 1, 3, 2)), ((0, 6), (0, 6), (2, 6), (2, 6))),
            GriddedPerm(Perm((0, 1, 3, 2)), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((0, 1, 3, 2)), ((2, 0), (2, 0), (2, 3), (2, 0))),
            GriddedPerm(Perm((0, 1, 3, 2)), ((2, 0), (2, 0), (2, 3), (2, 3))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 3), (0, 3), (0, 3), (2, 3))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 3), (0, 3), (2, 3), (2, 3))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 6), (0, 6), (0, 6), (0, 6))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 6), (0, 6), (0, 6), (2, 6))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 6), (0, 6), (2, 6), (2, 6))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((2, 0), (2, 3), (2, 3), (2, 0))),
            GriddedPerm(Perm((0, 3, 1, 2)), ((0, 3), (0, 3), (0, 3), (2, 3))),
            GriddedPerm(Perm((0, 3, 1, 2)), ((0, 3), (0, 3), (2, 3), (2, 3))),
            GriddedPerm(Perm((0, 3, 1, 2)), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((0, 3, 1, 2)), ((2, 0), (2, 3), (2, 0), (2, 0))),
            GriddedPerm(Perm((0, 3, 1, 2)), ((2, 0), (2, 3), (2, 0), (2, 3))),
            GriddedPerm(Perm((3, 1, 2, 0)), ((0, 3), (0, 3), (2, 3), (2, 3))),
            GriddedPerm(Perm((3, 1, 2, 0)), ((0, 6), (0, 3), (2, 3), (2, 3))),
        ),
        requirements=(
            (
                GriddedPerm(Perm((0,)), ((0, 6),)),
                GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
                GriddedPerm(Perm((0, 1)), ((2, 0), (5, 1))),
                GriddedPerm(Perm((1, 0)), ((0, 3), (2, 3))),
                GriddedPerm(Perm((1, 0)), ((2, 6), (2, 0))),
                GriddedPerm(Perm((2, 0, 1)), ((2, 3), (2, 0), (2, 3))),
            ),
            (
                GriddedPerm(Perm((0,)), ((0, 6),)),
                GriddedPerm(Perm((1, 0)), ((2, 6), (2, 0))),
            ),
            (GriddedPerm(Perm((0,)), ((1, 2),)),),
            (GriddedPerm(Perm((0,)), ((3, 5),)),),
            (
                GriddedPerm(Perm((0,)), ((5, 1),)),
                GriddedPerm(Perm((1, 0)), ((2, 3), (2, 0))),
                GriddedPerm(Perm((1, 0)), ((2, 6), (2, 0))),
            ),
        ),
        assumptions=(),
    )
    rule = strategy(tiling)
    eqv_rule = rule.to_equivalence_rule()
    reverse_rule = eqv_rule.to_reverse_rule()
    for i in range(6):
        reverse_rule.sanity_check(i)


@pytest.mark.xfail(reason="needs updated sanity checker on multivariables")
def test_multiple_parent_parameters_to_same_child_parameter():
    tiling = Tiling(
        obstructions=(
            GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((3, 0), (3, 0))),
            GriddedPerm(Perm((1, 2, 0)), ((1, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((1, 2, 0)), ((1, 0), (2, 0), (3, 0))),
            GriddedPerm(Perm((1, 2, 0)), ((1, 0), (3, 0), (3, 0))),
            GriddedPerm(Perm((0, 1, 2, 3)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1, 2, 3)), ((0, 0), (0, 0), (0, 0), (1, 0))),
            GriddedPerm(Perm((0, 1, 2, 3)), ((0, 0), (0, 0), (0, 0), (2, 0))),
            GriddedPerm(Perm((0, 1, 2, 3)), ((0, 0), (0, 0), (0, 0), (3, 0))),
            GriddedPerm(Perm((0, 1, 2, 3)), ((0, 0), (0, 0), (1, 0), (2, 0))),
            GriddedPerm(Perm((0, 1, 2, 3)), ((0, 0), (0, 0), (1, 0), (3, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 0), (0, 0), (0, 0), (1, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 0), (0, 0), (0, 0), (2, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 0), (0, 0), (0, 0), (3, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 0), (0, 0), (1, 0), (1, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 0), (0, 0), (1, 0), (2, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 0), (0, 0), (1, 0), (3, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 0), (0, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 0), (0, 0), (2, 0), (3, 0))),
            GriddedPerm(Perm((0, 2, 3, 1)), ((0, 0), (0, 0), (3, 0), (3, 0))),
        ),
        requirements=(),
        assumptions=(
            TrackingAssumption((GriddedPerm(Perm((0,)), ((2, 0),)),)),
            TrackingAssumption(
                (GriddedPerm(Perm((0,)), ((2, 0),)), GriddedPerm(Perm((0,)), ((3, 0),)))
            ),
        ),
    )
    strategy = RequirementPlacementStrategy(
        gps=(
            GriddedPerm(Perm((0,)), ((1, 0),)),
            GriddedPerm(Perm((0,)), ((2, 0),)),
            GriddedPerm(Perm((0,)), ((3, 0),)),
            GriddedPerm(Perm((0,)), ((0, 0),)),
        ),
        indices=(0, 0, 0, 0),
        direction=3,
        own_col=True,
        own_row=True,
        ignore_parent=False,
        include_empty=True,
    )
    rule = strategy(tiling)
    for i in range(6):
        rule.sanity_check(i)

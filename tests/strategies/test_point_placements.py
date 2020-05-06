from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import GriddedPerm, Tiling
from tilings.strategies import (
    AllPlacementsStrategy,
    PatternPlacementStrategy,
    RequirementPlacementStrategy,
    RowAndColumnPlacementStrategy,
)

pytest_plugins = [
    "tests.fixtures.obstructions_requirements",
    "tests.fixtures.simple_tiling",
    "tests.fixtures.diverse_tiling",
    "tests.fixtures.no_point_tiling",
]


def test_row_placement():
    t = Tiling.from_string("132")
    row_placement = RowAndColumnPlacementStrategy(
        place_col=False, place_row=True, partial=False
    )
    partial_row_placement = RowAndColumnPlacementStrategy(
        place_col=False, place_row=True, partial=True
    )
    assert len(list(row_placement(t))) == 2
    assert len(list(partial_row_placement(t))) == 2


def test_col_placement():
    t = Tiling.from_string("132")
    col_placement = RowAndColumnPlacementStrategy(
        place_col=True, place_row=False, partial=False
    )
    partial_col_placement = RowAndColumnPlacementStrategy(
        place_col=True, place_row=False, partial=True
    )
    assert len(list(col_placement(t))) == 2
    assert len(list(partial_col_placement(t))) == 2


def test_row_col_placement():
    t = Tiling.from_string("132")
    cr_placement = RowAndColumnPlacementStrategy(
        place_col=True, place_row=True, partial=False
    )
    partial_cr_placement = RowAndColumnPlacementStrategy(
        place_col=True, place_row=True, partial=True
    )
    assert len(list(cr_placement(t))) == 4
    assert len(list(partial_cr_placement(t))) == 4


def test_all_placements():
    t = Tiling(
        obstructions=[GriddedPerm(Perm((0, 1)), ((0, 0),) * 2)],
        requirements=[[GriddedPerm(Perm((0,)), ((0, 0),))]],
    )
    rules = list(AllPlacementsStrategy()(t))
    for rule in rules:
        print(rule)
    assert len(rules) == 8


def test_point_placement(diverse_tiling, no_point_tiling):
    point_placement = PatternPlacementStrategy(point_only=True)
    requirement_placement = PatternPlacementStrategy(point_only=False)
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
    row_gps = [GriddedPerm(Perm((0,)), ((0, 0),)), GriddedPerm(Perm((0,)), ((1, 0),))]
    placement_class = RequirementPlacementStrategy(
        gps=row_gps, indices=(0, 0), direction=1, own_col=True, own_row=True,
    )
    assert placement_class.formal_step() == "placing the topmost point in row 0"

    assert (
        placement1._col_placement_formal_step(1, 0)
        == "Placing rightmost points in column 1."
    )
    assert (
        placement1._col_placement_formal_step(4, 1)
        == "Placing topmost points in column 4."
    )
    assert (
        placement1._col_placement_formal_step(2, 2)
        == "Placing leftmost points in column 2."
    )
    assert (
        placement1._col_placement_formal_step(3, 3)
        == "Placing bottommost points in column 3."
    )
    assert (
        placement1._row_placement_formal_step(2, 0)
        == "Placing rightmost points in row 2."
    )
    assert (
        placement1._row_placement_formal_step(0, 1)
        == "Placing topmost points in row 0."
    )
    assert (
        placement1._row_placement_formal_step(3, 2)
        == "Placing leftmost points in row 3."
    )
    assert (
        placement1._row_placement_formal_step(1, 3)
        == "Placing bottommost points in row 1."
    )
    assert (
        placement1._point_placement_formal_step((0, 1), 0)
        == "Placing rightmost point in cell (0, 1)."
    )
    assert (
        placement1._point_placement_formal_step((2, 3), 1)
        == "Placing topmost point in cell (2, 3)."
    )
    assert (
        placement1._point_placement_formal_step((1, 4), 2)
        == "Placing leftmost point in cell (1, 4)."
    )
    assert (
        placement1._point_placement_formal_step((2, 2), 3)
        == "Placing bottommost point in cell (2, 2)."
    )
    gp = GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0)))
    assert (
        placement1._pattern_placement_formal_step(1, gp, 0)
        == "Placing the rightmost point of (1, 1) in 01: (0, 0), (0, 0)."
    )
    gp = GriddedPerm(Perm((0, 2, 1)), ((0, 0), (0, 0), (2, 0)))
    assert placement1._pattern_placement_formal_step(2, gp, 1) == (
        "Placing the topmost point of (2, 1) in " "021: (0, 0), (0, 0), (2, 0)."
    )
    gp = GriddedPerm(Perm((2, 0, 1)), ((1, 1), (2, 0), (2, 0)))
    assert placement1._pattern_placement_formal_step(0, gp, 2) == (
        "Placing the leftmost point of (0, 2) in " "201: (1, 1), (2, 0), (2, 0)."
    )
    gp = GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 1), (1, 2)))
    assert placement1._pattern_placement_formal_step(1, gp, 3) == (
        "Placing the bottommost point of (1, 1) in " "012: (0, 0), (1, 1), (1, 2)."
    )


def test_all_col_placement_rules(placement1):
    print(placement1._tiling)
    rules = list(placement1.all_col_placement_rules())
    assert len(rules) == 8
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.comb_classes) > 1
        assert re.match(
            r"Placing ((leftmost)|(rightmost)) points in " r"column \d+\.",
            rule.formal_step,
        )
        assert not rule.ignore_parent
        assert all(rule.workable)
        assert rule.constructor == "disjoint"
        assert all(rule.possibly_empty)
    assert sorted(len(rule.comb_classes) for rule in rules) == [2, 2, 2, 2, 2, 2, 3, 3]


def test_all_col_placement_rules_partial(placement1owncol, placement1ownrow):
    print(placement1owncol._tiling)
    rules = list(placement1owncol.all_col_placement_rules())
    assert len(rules) == 8
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.comb_classes) > 1
        assert re.match(
            r"Placing partially ((leftmost)|(rightmost)) points " r"in column \d+\.",
            rule.formal_step,
        )
        assert not rule.ignore_parent
        assert all(rule.workable)
        assert rule.constructor == "disjoint"
        assert all(rule.possibly_empty)
    assert sorted(len(rule.comb_classes) for rule in rules) == [2, 2, 2, 2, 2, 2, 3, 3]

    # Nothing to do if not placing on own col
    rules = list(placement1ownrow.all_col_placement_rules())
    assert len(rules) == 0


def test_all_row_placement_rules(placement1):
    rules = list(placement1.all_row_placement_rules())
    assert len(rules) == 6
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.comb_classes) > 1
        assert re.match(
            r"Placing ((topmost)|(bottommost)) points in " r"row \d+\.",
            rule.formal_step,
        )
        assert not rule.ignore_parent
        assert all(rule.workable)
        assert rule.constructor == "disjoint"
        assert all(rule.possibly_empty)
    assert sorted(len(rule.comb_classes) for rule in rules) == [2, 2, 3, 3, 3, 3]


def test_all_row_placement_rules_partial(placement1owncol, placement1ownrow):
    print(placement1owncol._tiling)
    rules = list(placement1ownrow.all_row_placement_rules())
    assert len(rules) == 6
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.comb_classes) > 1
        assert re.match(
            r"Placing partially ((topmost)|(bottommost)) points " r"in row \d+\.",
            rule.formal_step,
        )
        assert not rule.ignore_parent
        assert all(rule.workable)
        assert rule.constructor == "disjoint"
        assert all(rule.possibly_empty)
    assert sorted(len(rule.comb_classes) for rule in rules) == [2, 2, 3, 3, 3, 3]

    # Nothing to do if only not placing on own row
    rules = list(placement1owncol.all_row_placement_rules())
    assert len(rules) == 0


def test_all_point_placement_rules(
    placement1, placement2, placement2owncol, placement2ownrow, placement_only_west
):
    assert list(placement1.all_point_placement_rules()) == []
    print(placement2._tiling)
    assert len(list(placement2.all_point_placement_rules())) == 12
    assert len(list(placement2owncol.all_point_placement_rules())) == 6
    assert len(list(placement2ownrow.all_point_placement_rules())) == 6
    assert len(list(placement_only_west.all_point_placement_rules())) == 1
    for rule in placement2.all_point_placement_rules():
        assert isinstance(rule, Rule)
        assert len(rule.comb_classes) == 1
        assert re.match(
            r"Placing (leftmost|rightmost|topmost|bottommost) "
            r"point in cell \(\d+, \d+\)\.",
            rule.formal_step,
        )
        assert not rule.ignore_parent
        assert rule.workable == [True]
        assert rule.constructor == "equiv"
        assert rule.possibly_empty == [False]
    for rule in placement2ownrow.all_point_placement_rules():
        assert isinstance(rule, Rule)
        assert len(rule.comb_classes) == 1
        assert re.match(
            r"Placing partially (topmost|bottommost) " r"point in cell \(\d+, \d+\)\.",
            rule.formal_step,
        )
        assert not rule.ignore_parent
        assert rule.workable == [True]
        assert rule.constructor == "equiv"
        assert rule.possibly_empty == [False]
    for rule in placement2owncol.all_point_placement_rules():
        assert isinstance(rule, Rule)
        assert len(rule.comb_classes) == 1
        assert re.match(
            r"Placing partially (rightmost|leftmost) " r"point in cell \(\d+, \d+\)\.",
            rule.formal_step,
        )
        assert not rule.ignore_parent
        assert rule.workable == [True]
        assert rule.constructor == "equiv"
        assert rule.possibly_empty == [False]
    for rule in placement_only_west.all_point_placement_rules():
        assert len(rule.comb_classes) == 1
        assert rule.formal_step == "Placing leftmost point in cell (0, 0)."
        rule.comb_classes[0] == Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 2))),
                GriddedPerm(Perm((0, 1)), ((1, 2), (1, 2))),
                GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
                GriddedPerm(Perm((1, 0)), ((0, 1), (0, 1))),
            ],
            requirements=[[GriddedPerm(Perm((0,)), ((0, 1),))]],
        )


def test_all_requirement_placement_rules():
    t = Tiling(
        obstructions=[GriddedPerm(Perm((1, 0)), ((0, 0),) * 2)],
        requirements=[[GriddedPerm(Perm((0, 1)), ((0, 0),) * 2)]],
    )
    rules = list(PatternPlacementStrategy(t))
    assert len(rules) == 12
    for rule in rules:
        assert isinstance(rule, Rule)
        assert len(rule.comb_classes) == 1
        assert isinstance(rule.formal_step, str) and len(rule.formal_step) > 0
        assert re.match(
            r"Placing the (leftmost|rightmost|topmost|bottommost) "
            r"point of \(\d+, \d+\) in \d+: (\(\d+, \d+\), )*"
            r"\(\d+, \d+\)\.",
            rule.formal_step,
        )
        assert not rule.ignore_parent
        assert rule.workable == [True]
        assert rule.constructor == "equiv"
        assert rule.possibly_empty == [False]
    comb_classes = set(rule.comb_classes[0] for rule in rules)
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


def test_not_equivalent_to_itself():
    """
    We don't want the rule to say the tiling is equivalent to itself.
    The opposite can create situation where the tiling is mark as unworkable
    because of the ignore parent flag.
    """
    t_fully_placed = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 1), (1, 1))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (1, 1))),
        ],
        requirements=[[GriddedPerm(Perm((0,)), ((1, 1),))]],
    )
    t_row_placed = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (0, 1))),
        ],
        requirements=[[GriddedPerm(Perm((0,)), ((0, 1),))]],
    )
    t_row_placed2 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (0, 1))),
        ],
        requirements=[[GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1)))]],
    )
    t_col_placed = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 0), (1, 0))),
        ],
        requirements=[[GriddedPerm(Perm((0,)), ((1, 0),))]],
    )
    t_col_placed2 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 0), (1, 0))),
        ],
        requirements=[[GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0)))]],
    )
    placement_fully_placed = list(PatternPlacementStrategy()(t_fully_placed))
    placement_fully_placed_partial_col = list(
        PatternPlacementStrategy(partial=True, dirs=(DIR_WEST, DIR_EAST))(
            t_fully_placed
        )
    )
    placement_fully_placed_partial_row = list(
        PatternPlacementStrategy(partial=True, dirs=(DIR_NORTH, DIR_SOUTH))(
            t_fully_placed
        )
    )
    placement_row_placed = list(PatternPlacementStrategy()(t_row_placed))
    placement_row_placed_partial_col = list(
        PatternPlacementStrategy(partial=True, dirs=(DIR_EAST, DIR_WEST))(t_row_placed)
    )
    placement_row_placed_partial_row = list(
        PatternPlacementStrategy(partial=True, dirs=(DIR_NORTH, DIR_SOUTH))(
            t_row_placed
        )
    )
    placement_row_placed2 = list(PatternPlacementStrategy()(t_row_placed2))
    placement_col_placed = list(PatternPlacementStrategy()(t_col_placed))
    placement_col_placed_partial_col = list(
        PatternPlacementStrategy(partial=True, dirs=(DIR_EAST, DIR_WEST))(t_col_placed)
    )
    placement_col_placed_partial_row = list(
        PatternPlacementStrategy(partial=True, dirs=(DIR_NORTH, DIR_SOUTH))(
            t_col_placed
        )
    )
    placement_col_placed2 = list(PatternPlacementStrategy()(t_col_placed2))
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
        PatternPlacementStrategy(point_only=True)(t_fully_placed)
    )
    placement_row_placed = list(PatternPlacementStrategy(point_only=True)(t_row_placed))
    placement_row_placed2 = list(
        PatternPlacementStrategy(point_only=True)(t_row_placed2)
    )
    placement_col_placed = list(PatternPlacementStrategy(point_only=True)(t_col_placed))
    placement_col_placed2 = list(
        PatternPlacementStrategy(point_only=True)(t_col_placed2)
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
        RowAndColumnPlacementStrategy(place_col=False)(t_fully_placed)
    )
    placement_fully_placed_partial_col = list(
        RowAndColumnPlacementStrategy(place_col=False, partial=True)(t_fully_placed)
    )
    placement_fully_placed_partial_row = list(
        RowAndColumnPlacementStrategy(place_col=False, partial=True)(t_fully_placed)
    )
    placement_row_placed = list(
        RowAndColumnPlacementStrategy(place_col=False)(t_row_placed)
    )
    placement_row_placed_partial_col = list(
        RowAndColumnPlacementStrategy(place_col=False, partial=True)(t_row_placed)
    )
    placement_row_placed_partial_row = list(
        RowAndColumnPlacementStrategy(place_col=False, partial=True)(t_col_placed)
    )
    placement_row_placed2 = list(
        RowAndColumnPlacementStrategy(place_col=False)(t_row_placed2)
    )
    placement_col_placed = list(
        RowAndColumnPlacementStrategy(place_col=False)(t_col_placed)
    )
    placement_col_placed2 = list(
        RowAndColumnPlacementStrategy(place_col=False)(t_col_placed2)
    )
    for rule in placement_col_placed:
        print("=" * 20)
        print(rule)
        print(repr(rule.strategy))
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
        RowAndColumnPlacementStrategy(place_row=False)(t_fully_placed)
    )
    placement_fully_placed_partial_col = list(
        RowAndColumnPlacementStrategy(place_row=False, partial=True)(t_fully_placed)
    )
    placement_fully_placed_partial_row = list(
        RowAndColumnPlacementStrategy(place_row=False, partial=True)(t_fully_placed)
    )
    placement_row_placed = list(
        RowAndColumnPlacementStrategy(place_row=False)(t_row_placed)
    )
    placement_row_placed2 = list(
        RowAndColumnPlacementStrategy(place_row=False)(t_row_placed2)
    )
    placement_col_placed = list(
        RowAndColumnPlacementStrategy(place_row=False)(t_col_placed)
    )
    placement_col_placed2 = list(
        RowAndColumnPlacementStrategy(place_row=False)(t_col_placed2)
    )
    # Col placement
    assert len(placement_fully_placed) == 2
    assert len(placement_fully_placed_partial_col) == 2
    assert len(placement_fully_placed_partial_row) == 2
    assert len(placement_row_placed) == 2
    assert len(placement_row_placed2) == 2
    assert len(placement_col_placed) == 4
    assert len(placement_col_placed2) == 4


def test_all_requirement_placement_rules_partial(placement2owncol, placement2ownrow):
    print(placement2owncol._tiling)
    for rule in placement2owncol.all_requirement_placement_rules():
        assert isinstance(rule, Rule)
        assert len(rule.comb_classes) == 1
        assert isinstance(rule.formal_step, str) and len(rule.formal_step) > 0
        assert re.match(
            r"Placing partially the (leftmost|rightmost) "
            r"point of \(\d+, \d+\) in \d+: (\(\d+, \d+\), )*"
            r"\(\d+, \d+\)\.",
            rule.formal_step,
        )
        assert rule.workable == [True]
        assert rule.constructor == "equiv"
        assert rule.possibly_empty == [False]
    for rule in placement2ownrow.all_requirement_placement_rules():
        assert isinstance(rule, Rule)
        assert len(rule.comb_classes) == 1
        assert isinstance(rule.formal_step, str) and len(rule.formal_step) > 0
        assert re.match(
            r"Placing partially the (topmost|bottommost) "
            r"point of \(\d+, \d+\) in \d+: (\(\d+, \d+\), )*"
            r"\(\d+, \d+\)\.",
            rule.formal_step,
        )
        assert rule.workable == [True]
        assert rule.constructor == "equiv"
        assert rule.possibly_empty == [False]

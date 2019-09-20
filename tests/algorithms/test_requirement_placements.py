
import pytest

from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST
from tilings import GriddedPerm, Obstruction, Requirement, Tiling
from tilings.algorithms import RequirementPlacement

# ------------------------------------------------
#      Fixture and utility
# ------------------------------------------------


@pytest.fixture
def tiling1():
    t = Tiling(obstructions=(
        Obstruction(Perm((2, 1, 0)), ((0, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((1, 2),)*3),
        Obstruction(Perm((2, 0, 1)), ((3, 0),)*3),
        Obstruction(Perm((1, 0)), ((1, 1),)*2),
        Obstruction(Perm((1, 0)), ((2, 2),)*2),
        Obstruction(Perm((0, 1)), ((1, 1), (2, 2))),
    ))
    return t


@pytest.fixture
def tiling2():
    t = Tiling(obstructions=[
        Obstruction(Perm((0, 1)), ((0, 0),)*2),
        Obstruction(Perm((0, 1)), ((0, 1),)*2),
        Obstruction(Perm((0, 1)), ((1, 0),)*2),
        Obstruction(Perm((0, 1)), ((1, 1),)*2),
        Obstruction(Perm((0, 1)), ((3, 3),)*2),
        Obstruction(Perm((0, 1)), ((4, 3),)*2),
        Obstruction(Perm((0, 1)), ((4, 3),)*2),
        Obstruction(Perm((0, 1, 2)), ((2, 3),)*3),
        Obstruction(Perm((0, 1, 2)), ((2, 2),)*3),
        Obstruction(Perm((0, 1, 2)), ((3, 2),)*3),
        Obstruction(Perm((0, 1, 2)), ((4, 2),)*3),
        Obstruction(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 1))),
        Obstruction(Perm((0, 1, 2)), ((2, 2), (3, 2), (4, 2))),
        Obstruction(Perm((0, 1)), ((0, 1), (1, 1))),
    ], requirements=[
        [Requirement(Perm((0, 1)), ((0, 0), (0, 1)))],
        [Requirement(Perm((0, 1)), ((2, 3), (3, 3))),
         Requirement(Perm((0, 1)), ((3, 3), (4, 3)))],
    ])
    return t


@pytest.fixture
def placement1(tiling1):
    return RequirementPlacement(tiling1)


@pytest.fixture
def placement1ownrow(tiling1):
    return RequirementPlacement(tiling1, own_row=True, own_col=False)


@pytest.fixture
def placement1owncol(tiling1):
    return RequirementPlacement(tiling1, own_row=False, own_col=True)


@pytest.fixture
def placement2(tiling2):
    return RequirementPlacement(tiling2)


@pytest.fixture
def placement2ownrow(tiling2):
    return RequirementPlacement(tiling2, own_row=True, own_col=False)


@pytest.fixture
def placement2owncol(tiling2):
    return RequirementPlacement(tiling2, own_row=False, own_col=True)


@pytest.fixture
def gp1():
    return GriddedPerm(Perm((3, 1, 2, 0, 4)),
                       ((0, 1), (0, 0), (1, 1), (1, 0), (1, 1)))


# ------------------------------------------------------------
#       Tests for RequirementPlacement Class
# ------------------------------------------------------------


def test_formal_step(placement1):
    assert (placement1._col_placement_formal_step(1, 0) ==
            "Placing rightmost points in column 1.")
    assert (placement1._col_placement_formal_step(4, 1) ==
            "Placing topmost points in column 4.")
    assert (placement1._col_placement_formal_step(2, 2) ==
            "Placing leftmost points in column 2.")
    assert (placement1._col_placement_formal_step(3, 3) ==
            "Placing bottommost points in column 3.")
    assert (placement1._row_placement_formal_step(2, 0) ==
            "Placing rightmost points in row 2.")
    assert (placement1._row_placement_formal_step(0, 1) ==
            "Placing topmost points in row 0.")
    assert (placement1._row_placement_formal_step(3, 2) ==
            "Placing leftmost points in row 3.")
    assert (placement1._row_placement_formal_step(1, 3) ==
            "Placing bottommost points in row 1.")
    assert (placement1._point_placement_formal_step((0, 1), 0) ==
            "Placing rightmost point in cell (0, 1).")
    assert (placement1._point_placement_formal_step((2, 3), 1) ==
            "Placing topmost point in cell (2, 3).")
    assert (placement1._point_placement_formal_step((1, 4), 2) ==
            "Placing leftmost point in cell (1, 4).")
    assert (placement1._point_placement_formal_step((2, 2), 3) ==
            "Placing bottommost point in cell (2, 2).")
    gp = Requirement(Perm((0, 1)), ((0, 0), (0, 0)))
    assert (placement1._pattern_placement_formal_step(1, gp, 0) ==
            "Placing the rightmost point of (1, 1) in 01: (0, 0), (0, 0).")
    gp = Requirement(Perm((0, 2, 1)), ((0, 0), (0, 0), (2, 0)))
    assert (placement1._pattern_placement_formal_step(2, gp, 1) ==
            ("Placing the topmost point of (2, 1) in "
             "021: (0, 0), (0, 0), (2, 0)."))
    gp = Requirement(Perm((2, 0, 1)), ((1, 1), (2, 0), (2, 0)))
    assert (placement1._pattern_placement_formal_step(0, gp, 2) ==
            ("Placing the leftmost point of (0, 2) in "
             "201: (1, 1), (2, 0), (2, 0)."))
    gp = Requirement(Perm((0, 1, 2)), ((0, 0), (1, 1), (1, 2)))
    assert (placement1._pattern_placement_formal_step(1, gp, 3) ==
            ("Placing the bottommost point of (1, 1) in "
             "012: (0, 0), (1, 1), (1, 2)."))


def test_col_placement():
    pass


def test_row_placement():
    pass


def test_empty_col():
    pass


def test_empty_row():
    pass


def test_all_col_placement_rules():
    pass


def test_all_row_placement_rules():
    pass


def test_all_point_placement_rules():
    pass


def test_all_requirement_placement_rules():
    pass


# ------------------------------------------------------------
#       Tests for RequirementPlacement Class
# ------------------------------------------------------------


def test_point_translation(gp1, placement1, placement1owncol,
                           placement1ownrow):
    assert placement1._point_translation(gp1, 2, (0, 3)) == (3, 1)
    assert placement1._point_translation(gp1, 2, (1, 2)) == (3, 3)
    assert placement1._point_translation(gp1, 2, (2, 2)) == (3, 3)
    assert placement1._point_translation(gp1, 2, (3, 0)) == (1, 3)
    assert placement1._point_translation(gp1, 2, (4, 4)) == (1, 1)

    assert placement1owncol._point_translation(gp1, 2, (0, 3)) == (3, 1)
    assert placement1owncol._point_translation(gp1, 2, (1, 2)) == (3, 1)
    assert placement1owncol._point_translation(gp1, 2, (2, 2)) == (3, 1)
    assert placement1owncol._point_translation(gp1, 2, (3, 0)) == (1, 1)
    assert placement1owncol._point_translation(gp1, 2, (4, 4)) == (1, 1)

    assert placement1ownrow._point_translation(gp1, 2, (0, 3)) == (1, 1)
    assert placement1ownrow._point_translation(gp1, 2, (1, 2)) == (1, 3)
    assert placement1ownrow._point_translation(gp1, 2, (2, 2)) == (1, 3)
    assert placement1ownrow._point_translation(gp1, 2, (3, 0)) == (1, 3)
    assert placement1ownrow._point_translation(gp1, 2, (4, 4)) == (1, 1)


def test_gridded_perm_translation(gp1, placement1, placement1owncol,
                                  placement1ownrow):
    assert (placement1._gridded_perm_translation(gp1, (0, 3)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((2, 3), (2, 0), (3, 1), (3, 0), (3, 3))))
    assert (placement1._gridded_perm_translation(gp1, (1, 1)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 3), (2, 2), (3, 3), (3, 0), (3, 3))))
    assert (placement1._gridded_perm_translation(gp1, (2, 2)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 3), (0, 0), (3, 3), (3, 0), (3, 3))))
    assert (placement1._gridded_perm_translation(gp1, (3, 0)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 3), (0, 2), (1, 3), (3, 2), (3, 3))))
    assert (placement1._gridded_perm_translation(gp1, (4, 4)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 1), (0, 0), (1, 1), (1, 0), (3, 3))))
    assert (placement1owncol._gridded_perm_translation(gp1, (0, 3)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((2, 1), (2, 0), (3, 1), (3, 0), (3, 1))))
    assert (placement1owncol._gridded_perm_translation(gp1, (1, 1)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 1), (2, 0), (3, 1), (3, 0), (3, 1))))
    assert (placement1owncol._gridded_perm_translation(gp1, (2, 2)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 1), (0, 0), (3, 1), (3, 0), (3, 1))))
    assert (placement1owncol._gridded_perm_translation(gp1, (3, 0)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 1), (0, 0), (1, 1), (3, 0), (3, 1))))
    assert (placement1owncol._gridded_perm_translation(gp1, (4, 4)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 1), (0, 0), (1, 1), (1, 0), (3, 1))))
    assert (placement1ownrow._gridded_perm_translation(gp1, (0, 3)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 3), (0, 0), (1, 1), (1, 0), (1, 3))))
    assert (placement1ownrow._gridded_perm_translation(gp1, (1, 1)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 3), (0, 2), (1, 3), (1, 0), (1, 3))))
    assert (placement1ownrow._gridded_perm_translation(gp1, (2, 2)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 3), (0, 0), (1, 3), (1, 0), (1, 3))))
    assert (placement1ownrow._gridded_perm_translation(gp1, (3, 0)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 3), (0, 2), (1, 3), (1, 2), (1, 3))))
    assert (placement1ownrow._gridded_perm_translation(gp1, (4, 4)) ==
            GriddedPerm(Perm((3, 1, 2, 0, 4)),
                        ((0, 1), (0, 0), (1, 1), (1, 0), (1, 3))))


def test_placed_cell(placement1, placement1owncol, placement1ownrow):
    assert placement1._placed_cell((0, 0)) == (1, 1)
    assert placement1._placed_cell((3, 2)) == (4, 3)
    assert placement1owncol._placed_cell((9, 7)) == (10, 7)
    assert placement1owncol._placed_cell((2, 1)) == (3, 1)
    assert placement1ownrow._placed_cell((0, 4)) == (0, 5)
    assert placement1ownrow._placed_cell((4, 2)) == (4, 3)


def test_point_obstructions(placement1, placement1owncol, placement1ownrow):
    assert (placement1._point_obstructions((0, 0)) ==
            [Obstruction(Perm((0, 1)), ((1, 1), (1, 1))),
             Obstruction(Perm((1, 0)), ((1, 1), (1, 1)))])
    assert (placement1owncol._point_obstructions((0, 0)) ==
            [Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
             Obstruction(Perm((1, 0)), ((1, 0), (1, 0)))])
    assert (placement1ownrow._point_obstructions((0, 0)) ==
            [Obstruction(Perm((0, 1)), ((0, 1), (0, 1))),
             Obstruction(Perm((1, 0)), ((0, 1), (0, 1)))])


def test_point_requirements(placement1, placement1owncol, placement1ownrow):
    assert (placement1._point_requirements((2, 3)) ==
            [[Requirement(Perm((0,)), ((3, 4),))]])
    assert (placement1ownrow._point_requirements((2, 3)) ==
            [[Requirement(Perm((0,)), ((2, 4),))]])
    assert (placement1owncol._point_requirements((2, 3)) ==
            [[Requirement(Perm((0,)), ((3, 3),))]])


def test_stretch_gridded_perm(gp1, placement1, placement1owncol,
                              placement1ownrow):
    assert (set(placement1._stretch_gridded_perm(gp1, (0, 0))) ==
            set([GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((2, 3), (2, 2), (3, 3), (3, 2), (3, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((2, 3), (2, 2), (3, 3), (3, 0), (3, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((2, 3), (2, 0), (3, 3), (3, 0), (3, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (2, 2), (3, 3), (3, 2), (3, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (2, 2), (3, 3), (3, 0), (3, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (2, 0), (3, 3), (3, 0), (3, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (0, 2), (3, 3), (3, 2), (3, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (0, 2), (3, 3), (3, 0), (3, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (0, 0), (3, 3), (3, 0), (3, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (1, 1), (3, 3), (3, 0), (3, 3)))]))
    assert (set(placement1owncol._stretch_gridded_perm(gp1, (1, 0))) ==
            set([GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 1), (0, 0), (3, 1), (3, 0), (3, 1))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 1), (0, 0), (1, 1), (3, 0), (3, 1))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 1), (0, 0), (1, 1), (1, 0), (3, 1))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 1), (0, 0), (1, 1), (1, 0), (1, 1))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 1), (0, 0), (1, 1), (2, 0), (3, 1)))]))
    assert (set(placement1ownrow._stretch_gridded_perm(gp1, (1, 1))) ==
            set([GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (0, 0), (1, 3), (1, 0), (1, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (0, 0), (1, 1), (1, 0), (1, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 1), (0, 0), (1, 1), (1, 0), (1, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 1), (0, 0), (1, 1), (1, 0), (1, 1))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (0, 0), (1, 2), (1, 0), (1, 3))),
                 GriddedPerm(Perm((3, 1, 2, 0, 4)),
                             ((0, 1), (0, 0), (1, 1), (1, 0), (1, 2)))]))


def test_stretch_gridded_perms():
    pass


def test_stretched_obstructions():
    pass


def test_stretched_requirements():
    pass


def test_stretched_obstructions_and_requirements():
    pass


def farther(placement1):
    assert placement1._farther((0, 0), (2, 0), DIR_EAST) is False
    assert placement1._farther((0, 0), (2, 0), DIR_NORTH) is False
    assert placement1._farther((0, 0), (2, 0), DIR_WEST) is True
    assert placement1._farther((0, 0), (2, 0), DIR_SOUTH) is False

    assert placement1._farther((2, 3), (2, 0), DIR_EAST) is False
    assert placement1._farther((2, 3), (2, 0), DIR_NORTH) is True
    assert placement1._farther((2, 3), (2, 0), DIR_WEST) is False
    assert placement1._farther((2, 3), (2, 0), DIR_SOUTH) is False

    assert placement1._farther((1, 1), (3, 4), DIR_EAST) is False
    assert placement1._farther((1, 1), (3, 4), DIR_NORTH) is False
    assert placement1._farther((1, 1), (3, 4), DIR_WEST) is True
    assert placement1._farther((1, 1), (3, 4), DIR_SOUTH) is True

    assert placement1._farther((1, 5), (3, 4), DIR_EAST) is False
    assert placement1._farther((1, 5), (3, 4), DIR_NORTH) is True
    assert placement1._farther((1, 5), (3, 4), DIR_WEST) is True
    assert placement1._farther((1, 5), (3, 4), DIR_SOUTH) is False

    assert placement1._farther((2, 2), (1, 1), DIR_EAST) is True
    assert placement1._farther((2, 2), (1, 1), DIR_NORTH) is True
    assert placement1._farther((2, 2), (1, 1), DIR_WEST) is False
    assert placement1._farther((2, 2), (1, 1), DIR_SOUTH) is False


def test_forced_obstructions_from_patt(gp1, placement1, placement1owncol,
                                       placement1ownrow):
    assert (set(placement1._forced_obstructions_from_patt(gp1, 2,
                                                          DIR_NORTH)) ==
            set([Obstruction(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (0, 0), (3, 3), (3, 0), (3, 3))),
                 Obstruction(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (0, 0), (1, 3), (3, 0), (3, 3))),
                 Obstruction(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (0, 0), (1, 3), (1, 0), (3, 3))),
                 Obstruction(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (0, 0), (1, 3), (1, 0), (1, 3)))]))

    assert (set(placement1owncol._forced_obstructions_from_patt(gp1, 1,
                                                                DIR_EAST)) ==
            set([Obstruction(Perm((3, 1, 2, 0, 4)),
                             ((2, 1), (2, 0), (3, 1), (3, 0), (3, 1))),
                 Obstruction(Perm((3, 1, 2, 0, 4)),
                             ((0, 1), (2, 0), (3, 1), (3, 0), (3, 1)))]))

    assert (set(placement1ownrow._forced_obstructions_from_patt(gp1, 3,
                                                                DIR_SOUTH)) ==
            set([Obstruction(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (0, 2), (1, 3), (1, 0), (1, 3))),
                 Obstruction(Perm((3, 1, 2, 0, 4)),
                             ((0, 3), (0, 0), (1, 3), (1, 0), (1, 3)))]))


def test_forced_obstructions_from_list(gp1, placement1, placement1owncol,
                                       placement1ownrow):
    req_list_row = [Requirement(Perm((0,)), ((0, 0),)),
                    Requirement(Perm((0,)), ((1, 0),))]
    assert (set(placement1._forced_obstructions_from_list(
                                        req_list_row, (0, 0), DIR_NORTH)) ==
            set([Obstruction(Perm((0,)), ((0, 2),)),
                 Obstruction(Perm((0,)), ((2, 2),)),
                 Obstruction(Perm((0,)), ((3, 2),))]))
    assert (set(placement1._forced_obstructions_from_list(
                                        req_list_row, (0, 0), DIR_SOUTH)) ==
            set([Obstruction(Perm((0,)), ((0, 0),)),
                 Obstruction(Perm((0,)), ((2, 0),)),
                 Obstruction(Perm((0,)), ((3, 0),))]))
    assert (set(placement1._forced_obstructions_from_list(
                                        req_list_row, (1, 0), DIR_NORTH)) ==
            set([Obstruction(Perm((0,)), ((0, 2),)),
                 Obstruction(Perm((0,)), ((1, 2),)),
                 Obstruction(Perm((0,)), ((3, 2),))]))
    assert (set(placement1._forced_obstructions_from_list(
                                        req_list_row, (1, 0), DIR_SOUTH)) ==
            set([Obstruction(Perm((0,)), ((0, 0),)),
                 Obstruction(Perm((0,)), ((1, 0),)),
                 Obstruction(Perm((0,)), ((3, 0),))]))
    assert (set(placement1ownrow._forced_obstructions_from_list(
                                        req_list_row, (0, 0), DIR_NORTH)) ==
            set([Obstruction(Perm((0,)), ((0, 2),)),
                 Obstruction(Perm((0,)), ((1, 2),))]))
    assert (set(placement1ownrow._forced_obstructions_from_list(
                                        req_list_row, (0, 0), DIR_SOUTH)) ==
            set([Obstruction(Perm((0,)), ((0, 0),)),
                 Obstruction(Perm((0,)), ((1, 0),))]))
    assert (set(placement1ownrow._forced_obstructions_from_list(
                                        req_list_row, (1, 0), DIR_NORTH)) ==
            set([Obstruction(Perm((0,)), ((0, 2),)),
                 Obstruction(Perm((0,)), ((1, 2),))]))
    assert (set(placement1ownrow._forced_obstructions_from_list(
                                        req_list_row, (1, 0), DIR_SOUTH)) ==
            set([Obstruction(Perm((0,)), ((0, 0),)),
                 Obstruction(Perm((0,)), ((1, 0),))]))

    req_list_col = [Requirement(Perm((0,)), ((0, 0),)),
                    Requirement(Perm((0,)), ((0, 1),))]
    assert (set(placement1._forced_obstructions_from_list(
                                        req_list_col, (0, 0), DIR_EAST)) ==
            set([Obstruction(Perm((0,)), ((2, 0),)),
                 Obstruction(Perm((0,)), ((2, 2),)),
                 Obstruction(Perm((0,)), ((2, 3),))]))
    assert (set(placement1._forced_obstructions_from_list(
                                        req_list_col, (0, 0), DIR_WEST)) ==
            set([Obstruction(Perm((0,)), ((0, 0),)),
                 Obstruction(Perm((0,)), ((0, 2),)),
                 Obstruction(Perm((0,)), ((0, 3),))]))
    assert (set(placement1._forced_obstructions_from_list(
                                        req_list_col, (0, 1), DIR_EAST)) ==
            set([Obstruction(Perm((0,)), ((2, 0),)),
                 Obstruction(Perm((0,)), ((2, 1),)),
                 Obstruction(Perm((0,)), ((2, 3),))]))
    assert (set(placement1._forced_obstructions_from_list(
                                        req_list_col, (0, 1), DIR_WEST)) ==
            set([Obstruction(Perm((0,)), ((0, 0),)),
                 Obstruction(Perm((0,)), ((0, 1),)),
                 Obstruction(Perm((0,)), ((0, 3),))]))
    assert (set(placement1owncol._forced_obstructions_from_list(
                                        req_list_col, (0, 0), DIR_EAST)) ==
            set([Obstruction(Perm((0,)), ((2, 0),)),
                 Obstruction(Perm((0,)), ((2, 1),))]))
    assert (set(placement1owncol._forced_obstructions_from_list(
                                        req_list_col, (0, 0), DIR_WEST)) ==
            set([Obstruction(Perm((0,)), ((0, 0),)),
                 Obstruction(Perm((0,)), ((0, 1),))]))
    assert (set(placement1owncol._forced_obstructions_from_list(
                                        req_list_col, (0, 1), DIR_EAST)) ==
            set([Obstruction(Perm((0,)), ((2, 0),)),
                 Obstruction(Perm((0,)), ((2, 1),))]))
    assert (set(placement1owncol._forced_obstructions_from_list(
                                        req_list_col, (0, 1), DIR_WEST)) ==
            set([Obstruction(Perm((0,)), ((0, 0),)),
                 Obstruction(Perm((0,)), ((0, 1),))]))

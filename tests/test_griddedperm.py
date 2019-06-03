import pytest

from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NONE, DIR_NORTH, DIR_SOUTH, DIR_WEST
from tilings import GriddedPerm


@pytest.fixture
def simpleob():
    return GriddedPerm(Perm((1, 0, 3, 2)),
                       ((0, 0), (0, 0), (2, 2), (2, 1)))


@pytest.fixture
def singlecellob():
    return GriddedPerm.single_cell(Perm((1, 0, 3, 2)), (2, 2))


@pytest.fixture
def everycellob():
    return GriddedPerm(Perm((0, 3, 6, 1, 4, 7, 2, 5, 8)),
                       ((0, 0), (0, 1), (0, 2),
                        (1, 0), (1, 1), (1, 2),
                        (2, 0), (2, 1), (2, 2)))


@pytest.fixture
def typicalob():
    return GriddedPerm(Perm((1, 0, 2, 4, 3)),
                       ((0, 0), (0, 0), (1, 0), (1, 1), (1, 1)))


@pytest.fixture
def isolatedob():
    return GriddedPerm(Perm((0, 1, 2)),
                       ((0, 0), (1, 1), (2, 2)))


def test_single_cell():
    gp = GriddedPerm.single_cell(Perm((0, 1, 2)), (2, 3))
    assert gp.patt == Perm((0, 1, 2))
    assert gp.pos == ((2, 3), (2, 3), (2, 3))

    gp = GriddedPerm.single_cell(Perm((0,)), (45, 64))
    assert gp.patt == Perm((0,))
    assert gp.pos == ((45, 64),)


def test_empty_perm():
    gp = GriddedPerm.empty_perm()
    assert gp.patt == Perm(())
    assert gp.pos == ()


def test_contradictory(simpleob, singlecellob, everycellob):
    assert not simpleob.contradictory()
    assert not singlecellob.contradictory()
    assert not everycellob.contradictory()
    gp = GriddedPerm(Perm((0, 1)), [(0, 1), (1, 0)])
    assert gp.contradictory()
    gp = GriddedPerm(Perm((0, 1)), [(1, 0), (0, 0)])
    assert gp.contradictory()


def test_occupies(simpleob):
    assert simpleob.occupies((0, 0))
    assert simpleob.occupies((2, 1))
    assert simpleob.occupies((2, 2))

    assert not simpleob.occupies((0, 1))
    assert not simpleob.occupies((3, 1))
    assert not simpleob.occupies((2, 0))


def test_occurrences_in(simpleob):
    ob = GriddedPerm(Perm((0, 2, 1)), ((0, 0), (2, 2), (2, 1)))
    assert list(ob.occurrences_in(simpleob)) == [(0, 2, 3), (1, 2, 3)]
    assert ob.occurs_in(simpleob)

    ob = GriddedPerm(Perm((1, 0, 2)), ((0, 0), (0, 0), (2, 1)))
    assert list(ob.occurrences_in(simpleob)) == [(0, 1, 3)]
    assert ob.occurs_in(simpleob)

    ob = GriddedPerm(Perm((1, 0, 2)), ((0, 0), (0, 0), (2, 2)))
    assert list(ob.occurrences_in(simpleob)) == [(0, 1, 2)]
    assert ob.occurs_in(simpleob)

    ob = GriddedPerm(Perm((0, 1, 2)), ((0, 0), (2, 2), (2, 1)))
    assert not any(ob.occurrences_in(simpleob))
    assert not ob.occurs_in(simpleob)

    ob = GriddedPerm(Perm((1, 0, 2)), ((0, 0), (2, 2), (2, 2)))
    assert not any(ob.occurrences_in(simpleob))
    assert not ob.occurs_in(simpleob)

    ob = GriddedPerm(Perm(tuple()), tuple())
    assert ob in ob


def test_remove_cells(simpleob):
    assert (simpleob.remove_cells([(0, 0)]) ==
            GriddedPerm(Perm((1, 0)), ((2, 2), (2, 1))))
    assert (simpleob.remove_cells([(0, 0), (2, 2)]) ==
            GriddedPerm(Perm((0,)), ((2, 1),)))
    assert simpleob.remove_cells([(0, 1), (1, 2)]) == simpleob


def test_points_in_cell(simpleob):
    assert list(simpleob.points_in_cell((0, 0))) == [0, 1]
    assert list(simpleob.points_in_cell((0, 1))) == []


def test_isolated_cells(simpleob, isolatedob):
    assert list(simpleob.isolated_cells()) == []
    assert list(isolatedob.isolated_cells()) == [(0, 0), (1, 1), (2, 2)]


def test_is_isolated(simpleob, isolatedob):
    assert simpleob.is_isolated([2, 3])
    assert simpleob.is_isolated([0, 1])
    assert not simpleob.is_isolated([0])
    assert not simpleob.is_isolated([2])
    assert not simpleob.is_isolated([1, 3])
    assert isolatedob.is_isolated([0, 1, 2])
    assert isolatedob.is_isolated([0, 1])
    assert isolatedob.is_isolated([0, 2])
    assert isolatedob.is_isolated([1, 2])
    assert isolatedob.is_isolated([0])
    assert isolatedob.is_isolated([1])
    assert isolatedob.is_isolated([2])


def test_forced_point_index(singlecellob):
    assert singlecellob.forced_point_index((1, 1), DIR_SOUTH) is None
    assert singlecellob.forced_point_index((2, 2), DIR_WEST) == 0
    assert singlecellob.forced_point_index((2, 2), DIR_SOUTH) == 1
    assert singlecellob.forced_point_index((2, 2), DIR_NORTH) == 2
    assert singlecellob.forced_point_index((2, 2), DIR_EAST) == 3


def test_get_rowcol(everycellob, simpleob, typicalob):
    assert list(simpleob.get_points_col(0)) == [(0, 1), (1, 0)]
    assert list(simpleob.get_points_col(1)) == []
    assert list(simpleob.get_points_col(2)) == [(2, 3), (3, 2)]

    assert list(typicalob.get_points_col(0)) == [(0, 1), (1, 0)]
    assert list(typicalob.get_points_col(1)) == [(2, 2), (3, 4), (4, 3)]
    assert list(typicalob.get_points_col(2)) == []

    assert list(simpleob.get_points_row(0)) == [(0, 1), (1, 0)]
    assert list(simpleob.get_points_row(1)) == [(3, 2)]
    assert list(simpleob.get_points_row(2)) == [(2, 3)]
    assert list(simpleob.get_points_row(3)) == []

    assert list(typicalob.get_points_row(0)) == [(0, 1), (1, 0), (2, 2)]
    assert list(typicalob.get_points_row(1)) == [(3, 4), (4, 3)]
    assert list(typicalob.get_points_row(2)) == []

    assert list(everycellob.get_points_row(1)) == [(1, 3), (4, 4), (7, 5)]
    assert list(everycellob.get_points_col(1)) == [(3, 1), (4, 4), (5, 7)]
    assert list(everycellob.get_points_above_row(2)) == []
    assert list(everycellob.get_points_below_row(2)) == [(0, 0), (1, 3),
                                                         (3, 1), (4, 4),
                                                         (6, 2), (7, 5)]
    assert (list(everycellob.get_points_right_col(1)) ==
            [(6, 2), (7, 5), (8, 8)])
    assert list(everycellob.get_points_left_col(1)) == [(0, 0), (1, 3), (2, 6)]


def test_get_subperm_left_col(everycellob, simpleob, typicalob):
    assert (everycellob.get_subperm_left_col(0) == GriddedPerm(Perm(()), ()))
    assert (everycellob.get_subperm_left_col(1) ==
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 1), (0, 2))))
    assert (everycellob.get_subperm_left_col(2) ==
            GriddedPerm(Perm((0, 2, 4, 1, 3, 5)),
                        ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2))))
    assert everycellob.get_subperm_left_col(3) == everycellob

    assert simpleob.get_subperm_left_col(1) == GriddedPerm(Perm((1, 0)),
                                                           ((0, 0), (0, 0)))
    assert simpleob.get_subperm_left_col(10) == simpleob

    assert typicalob.get_subperm_left_col(1) == GriddedPerm(Perm((1, 0)),
                                                            ((0, 0), (0, 0)))
    assert typicalob.get_subperm_left_col(100) == typicalob


def test_get_bounding_box(typicalob):
    assert typicalob.get_bounding_box((1, 0)) == (2, 5, 0, 3)
    assert typicalob.get_bounding_box((2, 2)) == (5, 5, 5, 5)


def test_point_translation(typicalob):
    assert typicalob.point_translation(0, (1, 1)) == (0, 2)
    assert typicalob.point_translation(1, (1, 1)) == (2, 0)
    assert typicalob.point_translation(2, (1, 1)) == (3, 2)
    assert typicalob.point_translation(3, (1, 1)) == (3, 3)
    assert typicalob.point_translation(4, (1, 1)) == (3, 3)

    assert typicalob.point_translation(0, (2, 3)) == (0, 0)
    assert typicalob.point_translation(1, (2, 3)) == (0, 0)
    assert typicalob.point_translation(2, (2, 3)) == (3, 0)
    assert typicalob.point_translation(3, (2, 3)) == (3, 3)
    assert typicalob.point_translation(4, (2, 3)) == (3, 3)


def test_partial_point_translation(typicalob):
    assert typicalob.partial_point_translation(0, (1, 1), True) == (0, 2)
    assert typicalob.partial_point_translation(1, (1, 1), True) == (0, 0)
    assert typicalob.partial_point_translation(2, (1, 1), True) == (1, 2)
    assert typicalob.partial_point_translation(3, (1, 1), True) == (1, 3)
    assert typicalob.partial_point_translation(4, (1, 1), True) == (1, 3)

    assert typicalob.partial_point_translation(0, (2, 3), True) == (0, 0)
    assert typicalob.partial_point_translation(1, (2, 3), True) == (0, 0)
    assert typicalob.partial_point_translation(2, (2, 3), True) == (1, 0)
    assert typicalob.partial_point_translation(3, (2, 3), True) == (1, 3)
    assert typicalob.partial_point_translation(4, (2, 3), True) == (1, 3)

    assert typicalob.partial_point_translation(0, (1, 1), False) == (0, 0)
    assert typicalob.partial_point_translation(1, (1, 1), False) == (2, 0)
    assert typicalob.partial_point_translation(2, (1, 1), False) == (3, 0)
    assert typicalob.partial_point_translation(3, (1, 1), False) == (3, 1)
    assert typicalob.partial_point_translation(4, (1, 1), False) == (3, 1)

    assert typicalob.partial_point_translation(0, (2, 3), False) == (0, 0)
    assert typicalob.partial_point_translation(1, (2, 3), False) == (0, 0)
    assert typicalob.partial_point_translation(2, (2, 3), False) == (3, 0)
    assert typicalob.partial_point_translation(3, (2, 3), False) == (3, 1)
    assert typicalob.partial_point_translation(4, (2, 3), False) == (3, 1)


def test_stretch_gridding(typicalob):
    assert (typicalob.stretch_gridding((2, 1)) ==
            GriddedPerm(Perm((1, 0, 2, 4, 3)),
                        ((0, 2), (0, 0), (3, 2), (3, 3), (3, 3))))
    assert (typicalob.stretch_gridding((3, 2)) ==
            GriddedPerm(Perm((1, 0, 2, 4, 3)),
                        ((0, 0), (0, 0), (1, 2), (3, 3), (3, 3))))
    assert (typicalob.stretch_gridding((4, 0)) ==
            GriddedPerm(Perm((1, 0, 2, 4, 3)),
                        ((0, 2), (0, 2), (1, 2), (1, 3), (3, 3))))


def test_partial_stretch_gridding(typicalob):
    assert (typicalob.partial_stretch_gridding((2, 1), True) ==
            GriddedPerm(Perm((1, 0, 2, 4, 3)),
                        ((0, 2), (0, 0), (1, 2), (1, 3), (1, 3))))
    assert (typicalob.partial_stretch_gridding((3, 2), True) ==
            GriddedPerm(Perm((1, 0, 2, 4, 3)),
                        ((0, 0), (0, 0), (1, 2), (1, 3), (1, 3))))
    assert (typicalob.partial_stretch_gridding((4, 0), True) ==
            GriddedPerm(Perm((1, 0, 2, 4, 3)),
                        ((0, 2), (0, 2), (1, 2), (1, 3), (1, 3))))

    assert (typicalob.partial_stretch_gridding((2, 1), False) ==
            GriddedPerm(Perm((1, 0, 2, 4, 3)),
                        ((0, 0), (0, 0), (3, 0), (3, 1), (3, 1))))
    assert (typicalob.partial_stretch_gridding((3, 2), False) ==
            GriddedPerm(Perm((1, 0, 2, 4, 3)),
                        ((0, 0), (0, 0), (1, 0), (3, 1), (3, 1))))
    assert (typicalob.partial_stretch_gridding((4, 0), False) ==
            GriddedPerm(Perm((1, 0, 2, 4, 3)),
                        ((0, 0), (0, 0), (1, 0), (1, 1), (3, 1))))


def test_place_point(typicalob):
    ob12 = GriddedPerm.single_cell(Perm((0, 1)), (0, 0))
    assert (list(sorted(ob12.place_point((0, 0), DIR_NORTH))) ==
            [GriddedPerm(Perm((0,)), ((0, 0),)),
             GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
             GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0)))])
    assert (list(sorted(ob12.place_point((0, 0), DIR_EAST))) ==
            [GriddedPerm(Perm((0,)), ((0, 0),)),
             GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (0, 2))),
             GriddedPerm(Perm((0, 1)), ((0, 2), (0, 2)))])
    assert (list(sorted(ob12.place_point((0, 0), DIR_SOUTH))) ==
            [GriddedPerm(Perm((0,)), ((2, 2),)),
             GriddedPerm(Perm((0, 1)), ((0, 2), (0, 2))),
             GriddedPerm(Perm((0, 1)), ((0, 2), (2, 2))),
             GriddedPerm(Perm((0, 1)), ((2, 2), (2, 2)))])
    assert (list(sorted(ob12.place_point((0, 0), DIR_WEST))) ==
            [GriddedPerm(Perm((0,)), ((2, 2),)),
             GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
             GriddedPerm(Perm((0, 1)), ((2, 0), (2, 2))),
             GriddedPerm(Perm((0, 1)), ((2, 2), (2, 2)))])

    assert (list(sorted(ob12.place_point((0, 0), DIR_NORTH,
                        partial=True, row=True))) ==
            [GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1)))])
    assert (list(sorted(ob12.place_point((0, 0), DIR_EAST,
                        partial=True, row=False))) ==
            [GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0)))])
    assert (list(sorted(ob12.place_point((0, 0), DIR_SOUTH,
                        partial=True, row=True))) ==
            [GriddedPerm(Perm((0, 1)), ((0, 1), (0, 2))),
             GriddedPerm(Perm((0, 1)), ((0, 2), (0, 2)))])
    assert (list(sorted(ob12.place_point((0, 0), DIR_WEST,
                        partial=True, row=False))) ==
            [GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
             GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0)))])
    assert (list(sorted(ob12.place_point((0, 0), DIR_NONE,
                        partial=True, row=True))) ==
            [GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (0, 2))),
             GriddedPerm(Perm((0, 1)), ((0, 1), (0, 2))),
             GriddedPerm(Perm((0, 1)), ((0, 2), (0, 2)))])
    assert (list(sorted(ob12.place_point((0, 0), DIR_NONE,
                        partial=True, row=False))) ==
            [GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (2, 0))),
             GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
             GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0)))])

    assert (
        list(sorted(typicalob.place_point((0, 1), DIR_WEST))) ==
        [GriddedPerm(Perm((1, 0, 2, 4, 3)),
                     ((0, 0), (0, 0), (3, 0), (3, 1), (3, 1))),
         GriddedPerm(Perm((1, 0, 2, 4, 3)),
                     ((0, 0), (0, 0), (3, 0), (3, 3), (3, 1))),
         GriddedPerm(Perm((1, 0, 2, 4, 3)),
                     ((0, 0), (0, 0), (3, 0), (3, 3), (3, 3))),
         GriddedPerm(Perm((1, 0, 2, 4, 3)),
                     ((0, 0), (2, 0), (3, 0), (3, 1), (3, 1))),
         GriddedPerm(Perm((1, 0, 2, 4, 3)),
                     ((0, 0), (2, 0), (3, 0), (3, 3), (3, 1))),
         GriddedPerm(Perm((1, 0, 2, 4, 3)),
                     ((0, 0), (2, 0), (3, 0), (3, 3), (3, 3))),
         GriddedPerm(Perm((1, 0, 2, 4, 3)),
                     ((2, 0), (2, 0), (3, 0), (3, 1), (3, 1))),
         GriddedPerm(Perm((1, 0, 2, 4, 3)),
                     ((2, 0), (2, 0), (3, 0), (3, 3), (3, 1))),
         GriddedPerm(Perm((1, 0, 2, 4, 3)),
                     ((2, 0), (2, 0), (3, 0), (3, 3), (3, 3)))])
    assert (
        list(sorted(typicalob.place_point((0, 1), DIR_EAST,
                                          partial=True, row=False))) ==
        [GriddedPerm(Perm((1, 0, 2, 4, 3)),
                     ((0, 0), (0, 0), (3, 0), (3, 1), (3, 1))),
         GriddedPerm(Perm((1, 0, 2, 4, 3)),
                     ((0, 0), (2, 0), (3, 0), (3, 1), (3, 1))),
         GriddedPerm(Perm((1, 0, 2, 4, 3)),
                     ((2, 0), (2, 0), (3, 0), (3, 1), (3, 1)))])

    assert (list(sorted(GriddedPerm(Perm((2, 1, 0, 4, 3)),
                                    ((0, 1), (0, 1), (1, 0), (2, 1), (2, 1))
                                    ).place_point((2, 1), DIR_SOUTH))) ==
            [GriddedPerm(Perm((2, 1, 0, 3)),
                         ((0, 1), (0, 1), (1, 0), (2, 3))),
             GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 1), (0, 1), (1, 0), (2, 3), (2, 3))),
             GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 1), (0, 1), (1, 0), (2, 3), (4, 3))),
             GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 1), (0, 1), (1, 0), (4, 3), (4, 3))),
             GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 3), (0, 1), (1, 0), (2, 3), (2, 3))),
             GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 3), (0, 1), (1, 0), (2, 3), (4, 3))),
             GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 3), (0, 1), (1, 0), (4, 3), (4, 3))),
             GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 3), (0, 3), (1, 0), (2, 3), (2, 3))),
             GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 3), (0, 3), (1, 0), (2, 3), (4, 3))),
             GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 3), (0, 3), (1, 0), (4, 3), (4, 3)))])
    assert (list(sorted(GriddedPerm(Perm((2, 1, 0, 4, 3)),
                                    ((0, 1), (0, 1), (1, 0), (2, 1), (2, 1))
                                    ).place_point((2, 1), DIR_SOUTH,
                                                  partial=True, row=True))) ==
            [GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 1), (0, 1), (1, 0), (2, 3), (2, 2))),
             GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 1), (0, 1), (1, 0), (2, 3), (2, 3))),
             GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 3), (0, 1), (1, 0), (2, 3), (2, 3))),
             GriddedPerm(Perm((2, 1, 0, 4, 3)),
                         ((0, 3), (0, 3), (1, 0), (2, 3), (2, 3)))])

    def minimize(obba):
        obba = sorted(obba)
        res = list()
        last = None
        for ob in obba:
            if ob == last:
                continue
            add = True
            for m in res:
                if m in ob:
                    add = False
                    break
            if add:
                res.append(ob)
        return res

    ob = GriddedPerm.single_cell(Perm((0, 1, 2)), (0, 0))
    obs = minimize(ob.place_point((0, 0), DIR_NONE))
    assert (obs == [GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
                    GriddedPerm(Perm((0, 1)), ((0, 0), (2, 2))),
                    GriddedPerm(Perm((0, 1)), ((2, 2), (2, 2))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 2), (0, 2))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 0), (2, 0), (2, 0))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 2), (0, 2), (0, 2))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 2), (0, 2), (2, 2))),
                    GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0))),
                    GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 2)))])
    assert (list(sorted(ob.place_point((0, 0), DIR_NONE,
                                       partial=True, row=True))) ==
            [GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))),
             GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 1))),
             GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 2))),
             GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 1), (0, 2))),
             GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 2), (0, 2))),
             GriddedPerm(Perm((0, 1, 2)), ((0, 1), (0, 2), (0, 2))),
             GriddedPerm(Perm((0, 1, 2)), ((0, 2), (0, 2), (0, 2)))])
    assert (list(sorted(ob.place_point((0, 0), DIR_NONE,
                                       partial=True, row=False))) ==
            [GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))),
             GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (1, 0))),
             GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (2, 0))),
             GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 0))),
             GriddedPerm(Perm((0, 1, 2)), ((0, 0), (2, 0), (2, 0))),
             GriddedPerm(Perm((0, 1, 2)), ((1, 0), (2, 0), (2, 0))),
             GriddedPerm(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0)))])


def test_is_point_perm(typicalob, singlecellob):
    assert typicalob.is_point_perm() is None
    assert singlecellob.is_point_perm() is None
    assert GriddedPerm(Perm((0,)), ((0, 0),)).is_point_perm() == (0, 0)
    assert GriddedPerm(Perm((0,)), ((3, 2),)).is_point_perm() == (3, 2)
    assert GriddedPerm(Perm((0,)), ((100, 10),)).is_point_perm() == (100, 10)


def test_is_single_cell(typicalob, simpleob, singlecellob):
    assert typicalob.is_single_cell() is None
    assert simpleob.is_single_cell() is None
    assert singlecellob.is_single_cell() == (2, 2)


def test_insert_point():
    ob = GriddedPerm(Perm((0, 4, 1, 2, 3, 5)),
                     [(0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (2, 2)])
    assert list(ob.insert_point((1, 1))) == [
        GriddedPerm(Perm((0, 5, 1, 2, 3, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        GriddedPerm(Perm((0, 5, 1, 3, 2, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        GriddedPerm(Perm((0, 5, 1, 4, 2, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        GriddedPerm(Perm((0, 4, 1, 5, 2, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        GriddedPerm(Perm((0, 5, 1, 3, 2, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        GriddedPerm(Perm((0, 5, 1, 2, 3, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        GriddedPerm(Perm((0, 5, 1, 2, 4, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        GriddedPerm(Perm((0, 4, 1, 2, 5, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        GriddedPerm(Perm((0, 5, 1, 3, 4, 2, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        GriddedPerm(Perm((0, 5, 1, 2, 4, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        GriddedPerm(Perm((0, 5, 1, 2, 3, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        GriddedPerm(Perm((0, 4, 1, 2, 3, 5, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)))]


def test_all_subperms(simpleob):
    assert (list(sorted(simpleob.all_subperms())) ==
            [GriddedPerm(Perm(()), ()),
             GriddedPerm(Perm((0, )), ((0, 0),)),
             GriddedPerm(Perm((0, )), ((0, 0),)),
             GriddedPerm(Perm((0, )), ((2, 1),)),
             GriddedPerm(Perm((0, )), ((2, 2),)),
             GriddedPerm(Perm((0, 1)), ((0, 0), (2, 1))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (2, 1))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (2, 2))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (2, 2))),
             GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0))),
             GriddedPerm(Perm((1, 0)), ((2, 2), (2, 1))),
             GriddedPerm(Perm((0, 2, 1)), ((0, 0), (2, 2), (2, 1))),
             GriddedPerm(Perm((0, 2, 1)), ((0, 0), (2, 2), (2, 1))),
             GriddedPerm(Perm((1, 0, 2)), ((0, 0), (0, 0), (2, 1))),
             GriddedPerm(Perm((1, 0, 2)), ((0, 0), (0, 0), (2, 2)))])
    assert (list(sorted(simpleob.all_subperms(proper=False))) ==
            [GriddedPerm(Perm(()), ()),
             GriddedPerm(Perm((0, )), ((0, 0),)),
             GriddedPerm(Perm((0, )), ((0, 0),)),
             GriddedPerm(Perm((0, )), ((2, 1),)),
             GriddedPerm(Perm((0, )), ((2, 2),)),
             GriddedPerm(Perm((0, 1)), ((0, 0), (2, 1))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (2, 1))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (2, 2))),
             GriddedPerm(Perm((0, 1)), ((0, 0), (2, 2))),
             GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0))),
             GriddedPerm(Perm((1, 0)), ((2, 2), (2, 1))),
             GriddedPerm(Perm((0, 2, 1)), ((0, 0), (2, 2), (2, 1))),
             GriddedPerm(Perm((0, 2, 1)), ((0, 0), (2, 2), (2, 1))),
             GriddedPerm(Perm((1, 0, 2)), ((0, 0), (0, 0), (2, 1))),
             GriddedPerm(Perm((1, 0, 2)), ((0, 0), (0, 0), (2, 2))),
             GriddedPerm(Perm((1, 0, 3, 2)),
                         ((0, 0), (0, 0), (2, 2), (2, 1)))])


def test_remove_point(typicalob, simpleob, singlecellob):
    assert simpleob.remove_point(0) == GriddedPerm(
        Perm((0, 2, 1)), [(0, 0), (2, 2), (2, 1)])
    assert simpleob.remove_point(1) == GriddedPerm(
        Perm((0, 2, 1)), [(0, 0), (2, 2), (2, 1)])
    assert simpleob.remove_point(2) == GriddedPerm(
        Perm((1, 0, 2)), [(0, 0), (0, 0), (2, 1)])
    assert simpleob.remove_point(3) == GriddedPerm(
        Perm((1, 0, 2)), [(0, 0), (0, 0), (2, 2)])

    assert typicalob.remove_point(0) == GriddedPerm(
        Perm((0, 1, 3, 2)), [(0, 0), (1, 0), (1, 1), (1, 1)])
    assert typicalob.remove_point(1) == GriddedPerm(
        Perm((0, 1, 3, 2)), [(0, 0), (1, 0), (1, 1), (1, 1)])
    assert typicalob.remove_point(2) == GriddedPerm(
        Perm((1, 0, 3, 2)), [(0, 0), (0, 0), (1, 1), (1, 1)])
    assert typicalob.remove_point(3) == GriddedPerm(
        Perm((1, 0, 2, 3)), [(0, 0), (0, 0), (1, 0), (1, 1)])
    assert typicalob.remove_point(4) == GriddedPerm(
        Perm((1, 0, 2, 3)), [(0, 0), (0, 0), (1, 0), (1, 1)])

    assert singlecellob.remove_point(0) == GriddedPerm(
        Perm((0, 2, 1)), [(2, 2), (2, 2), (2, 2)])
    assert singlecellob.remove_point(1) == GriddedPerm(
        Perm((0, 2, 1)), [(2, 2), (2, 2), (2, 2)])
    assert singlecellob.remove_point(2) == GriddedPerm(
        Perm((1, 0, 2)), [(2, 2), (2, 2), (2, 2)])
    assert singlecellob.remove_point(3) == GriddedPerm(
        Perm((1, 0, 2)), [(2, 2), (2, 2), (2, 2)])


def test_minimize(typicalob, simpleob):
    def cell_mapping(x):
        return (x[0] + 1, x[1] + 2)
    assert (typicalob.minimize(cell_mapping) ==
            GriddedPerm(Perm((1, 0, 2, 4, 3)),
                        ((1, 2), (1, 2), (2, 2), (2, 3), (2, 3))))
    assert (simpleob.minimize(cell_mapping) ==
            GriddedPerm(Perm((1, 0, 3, 2)),
                        ((1, 2), (1, 2), (3, 4), (3, 3))))


def test_compression(simpleob, singlecellob, everycellob, typicalob,
                     isolatedob):
    assert (simpleob ==
            GriddedPerm.decompress(simpleob.compress()))
    assert (singlecellob ==
            GriddedPerm.decompress(singlecellob.compress()))
    assert (everycellob ==
            GriddedPerm.decompress(everycellob.compress()))
    assert (typicalob ==
            GriddedPerm.decompress(typicalob.compress()))
    assert (isolatedob ==
            GriddedPerm.decompress(isolatedob.compress()))

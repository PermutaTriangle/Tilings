import pytest

from grids_two import Obstruction
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST  # , DIRS


@pytest.fixture
def simpleob():
    return Obstruction(Perm((1, 0, 3, 2)),
                       ((0, 0), (0, 0), (2, 2), (2, 1)))


@pytest.fixture
def singlecellob():
    return Obstruction.single_cell(Perm((1, 0, 3, 2)), (2, 2))


@pytest.fixture
def everycellob():
    return Obstruction(Perm((0, 3, 6, 1, 4, 7, 2, 5, 8)),
                       ((0, 0), (0, 1), (0, 2),
                        (1, 0), (1, 1), (1, 2),
                        (2, 0), (2, 1), (2, 2)))


@pytest.fixture
def typicalob():
    return Obstruction(Perm((1, 0, 2, 4, 3)),
                       ((0, 0), (0, 0), (1, 0), (1, 1), (1, 1)))


def test_spans_cell(simpleob):
    assert simpleob.spans_cell((1, 1))
    assert simpleob.spans_cell((0, 2))
    assert simpleob.spans_cell((2, 2))

    assert not simpleob.spans_cell((3, 2))
    assert not simpleob.spans_cell((0, 3))


def test_occupies_cell(simpleob):
    assert simpleob.occupies((0, 0))
    assert simpleob.occupies((2, 1))
    assert simpleob.occupies((2, 2))

    assert not simpleob.occupies((0, 1))
    assert not simpleob.occupies((3, 1))
    assert not simpleob.occupies((2, 0))


def test_occurrences_in(simpleob):
    ob = Obstruction(Perm((0, 2, 1)), ((0, 0), (2, 2), (2, 1)))
    assert list(ob.occurrences_in(simpleob)) == [(0, 2, 3), (1, 2, 3)]

    ob = Obstruction(Perm((1, 0, 2)), ((0, 0), (0, 0), (2, 1)))
    assert list(ob.occurrences_in(simpleob)) == [(0, 1, 3)]

    ob = Obstruction(Perm((1, 0, 2)), ((0, 0), (0, 0), (2, 2)))
    assert list(ob.occurrences_in(simpleob)) == [(0, 1, 2)]

    ob = Obstruction(Perm((0, 1, 2)), ((0, 0), (2, 2), (2, 1)))
    assert not any(ob.occurrences_in(simpleob))

    ob = Obstruction(Perm((1, 0, 2)), ((0, 0), (2, 2), (2, 2)))
    assert not ob.occurs_in(simpleob)


def test_remove_cells(simpleob):
    assert (simpleob.remove_cells([(0, 0)]) ==
            Obstruction(Perm((1, 0)), ((2, 2), (2, 1))))
    assert (simpleob.remove_cells([(0, 0), (2, 2)]) ==
            Obstruction(Perm((0,)), ((2, 1),)))
    assert simpleob.remove_cells([(0, 1), (1, 2)]) == simpleob


def test_points_in_cell(simpleob):
    assert list(simpleob.points_in_cell((0, 0))) == [0, 1]
    assert list(simpleob.points_in_cell((0, 1))) == []


def test_isolated_cells(simpleob):
    assert list(simpleob.isolated_cells()) == [(2, 2), (2, 1)]


def test_forced_point_index(singlecellob):
    assert singlecellob.forced_point_index((1, 1), DIR_SOUTH) is None
    assert singlecellob.forced_point_index((2, 2), DIR_WEST) == 0
    assert singlecellob.forced_point_index((2, 2), DIR_SOUTH) == 1
    assert singlecellob.forced_point_index((2, 2), DIR_NORTH) == 2
    assert singlecellob.forced_point_index((2, 2), DIR_EAST) == 3


def test_get_rowcol(everycellob):
    assert list(everycellob.get_points_row(1)) == [(1, 3), (4, 4), (7, 5)]
    assert list(everycellob.get_points_col(1)) == [(3, 1), (4, 4), (5, 7)]
    assert list(everycellob.get_points_above_row(2)) == []
    assert list(everycellob.get_points_below_row(2)) == [(0, 0), (1, 3),
                                                         (3, 1), (4, 4),
                                                         (6, 2), (7, 5)]
    assert (list(everycellob.get_points_right_col(1)) ==
            [(6, 2), (7, 5), (8, 8)])
    assert list(everycellob.get_points_left_col(1)) == [(0, 0), (1, 3), (2, 6)]


def test_get_bounding_box(typicalob):
    assert typicalob.get_bounding_box((1, 0)) == (2, 5, 0, 3)
    assert typicalob.get_bounding_box((2, 2)) == (5, 5, 5, 5)


def test_stretch_obstruction(typicalob):
    assert (typicalob.stretch_obstruction((2, 1)) ==
            Obstruction(Perm((1, 0, 2, 4, 3)),
                        ((0, 2), (0, 0), (3, 2), (3, 3), (3, 3))))
    assert (typicalob.stretch_obstruction((3, 2)) ==
            Obstruction(Perm((1, 0, 2, 4, 3)),
                        ((0, 0), (0, 0), (1, 2), (3, 3), (3, 3))))
    assert (typicalob.stretch_obstruction((4, 0)) ==
            Obstruction(Perm((1, 0, 2, 4, 3)),
                        ((0, 2), (0, 2), (1, 2), (1, 3), (3, 3))))


def test_place_point(typicalob):
    for ob in typicalob.place_point((1, 0), DIR_WEST):
        print(ob)

import pytest

from grids_two import Obstruction
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIR_NONE
from functools import partial


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


@pytest.fixture
def isolatedob():
    return Obstruction(Perm((0, 1, 2)),
                       ((0, 0), (1, 1), (2, 2)))


@pytest.fixture
def bigob():
    # Placed on a 17 by 21 tiling
    return Obstruction(Perm((3, 1, 6, 8, 0, 2, 9, 5, 7, 4)),
                       [(7, 4), (8, 2), (9, 7), (10, 9), (11, 1), (12, 2),
                        (13, 10), (13, 6), (14, 8), (15, 6)])


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


def test_isolated_cells(simpleob, isolatedob):
    assert list(simpleob.isolated_cells()) == []
    assert list(isolatedob.isolated_cells()) == [(0, 0), (1, 1), (2, 2)]


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
    ob12 = Obstruction.single_cell(Perm((0, 1)), (0, 0))
    assert (list(ob12.place_point((0, 0), DIR_NORTH, skip_redundant=True)) ==
            [Obstruction(Perm((0,)), ((0, 0),)),
             Obstruction(Perm((0, 1)), ((2, 0), (2, 0)))])
    assert (list(ob12.place_point((0, 0), DIR_EAST, skip_redundant=True)) ==
            [Obstruction(Perm((0,)), ((0, 0),)),
             Obstruction(Perm((0, 1)), ((0, 2), (0, 2)))])
    assert (list(ob12.place_point((0, 0), DIR_SOUTH, skip_redundant=True)) ==
            [Obstruction(Perm((0,)), ((2, 2),)),
             Obstruction(Perm((0, 1)), ((0, 2), (0, 2)))])
    assert (list(ob12.place_point((0, 0), DIR_WEST, skip_redundant=True)) ==
            [Obstruction(Perm((0,)), ((2, 2),)),
             Obstruction(Perm((0, 1)), ((2, 0), (2, 0)))])

    assert (list(typicalob.place_point((0, 1), DIR_WEST, skip_redundant=True))
            == [Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((2, 0), (2, 0), (3, 0), (3, 3), (3, 3))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((2, 0), (2, 0), (3, 0), (3, 3), (3, 1))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((2, 0), (2, 0), (3, 0), (3, 1), (3, 1))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((0, 0), (2, 0), (3, 0), (3, 3), (3, 3))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((0, 0), (2, 0), (3, 0), (3, 3), (3, 1))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((0, 0), (2, 0), (3, 0), (3, 1), (3, 1))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((0, 0), (0, 0), (3, 0), (3, 3), (3, 3))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((0, 0), (0, 0), (3, 0), (3, 3), (3, 1))),
                Obstruction(Perm((1, 0, 2, 4, 3)),
                            ((0, 0), (0, 0), (3, 0), (3, 1), (3, 1)))])
    assert (list(Obstruction(Perm((2, 1, 0, 4, 3)),
                             ((0, 1), (0, 1), (1, 0), (2, 1), (2, 1))
                             ).place_point(
                                 (2, 1), DIR_SOUTH, skip_redundant=True)) ==
            [Obstruction(Perm((2, 1, 0, 3)),
                         ((0, 1), (0, 1), (1, 0), (2, 3))),
             Obstruction(Perm((2, 1, 0, 4, 3)),
                         ((0, 3), (0, 3), (1, 0), (4, 3), (4, 3))),
             Obstruction(Perm((2, 1, 0, 4, 3)),
                         ((0, 3), (0, 1), (1, 0), (4, 3), (4, 3))),
             Obstruction(Perm((2, 1, 0, 4, 3)),
                         ((0, 1), (0, 1), (1, 0), (4, 3), (4, 3)))])

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

    obs = minimize(Obstruction.single_cell(
        Perm((0, 1, 2)), (0, 0)).place_point((0, 0), DIR_NONE))
    assert (obs == [Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
                    Obstruction(Perm((0, 1)), ((0, 0), (2, 2))),
                    Obstruction(Perm((0, 1)), ((2, 2), (2, 2))),
                    Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 2), (0, 2))),
                    Obstruction(Perm((0, 1, 2)), ((0, 0), (2, 0), (2, 0))),
                    Obstruction(Perm((0, 1, 2)), ((0, 2), (0, 2), (0, 2))),
                    Obstruction(Perm((0, 1, 2)), ((0, 2), (0, 2), (2, 2))),
                    Obstruction(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 0))),
                    Obstruction(Perm((0, 1, 2)), ((2, 0), (2, 0), (2, 2)))])


def test_is_point_obstr(typicalob, singlecellob):
    assert typicalob.is_point_obstr() is None
    assert singlecellob.is_point_obstr() is None
    assert Obstruction(Perm((0,)), ((0, 0),)).is_point_obstr() == (0, 0)
    assert Obstruction(Perm((0,)), ((3, 2),)).is_point_obstr() == (3, 2)
    assert Obstruction(Perm((0,)), ((100, 10),)).is_point_obstr() == (100, 10)


def test_is_single_cell(typicalob, simpleob, singlecellob):
    assert typicalob.is_single_cell() is None
    assert simpleob.is_single_cell() is None
    assert singlecellob.is_single_cell() == (2, 2)


def test_insert_point():
    ob = Obstruction(Perm((0, 4, 1, 2, 3, 5)),
                     [(0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (2, 2)])
    assert list(ob.insert_point((1, 1))) == [
        Obstruction(Perm((0, 5, 1, 2, 3, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 3, 2, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 4, 2, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 4, 1, 5, 2, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 3, 2, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 2, 3, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 2, 4, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 4, 1, 2, 5, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 3, 4, 2, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 2, 4, 3, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 5, 1, 2, 3, 4, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2))),
        Obstruction(Perm((0, 4, 1, 2, 3, 5, 6)),
                    ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)))]



def test_compression(simpleob, singlecellob, everycellob, typicalob,
                     isolatedob):
    patthash = {Perm((1, 0, 3, 2)): 0,
                Perm((0, 3, 6, 1, 4, 7, 2, 5, 8)): 1,
                Perm((1, 0, 2, 4, 3)): 4,
                Perm((0, 1, 2)): 17}
    revhash = {0: Perm((1, 0, 3, 2)),
               1: Perm((0, 3, 6, 1, 4, 7, 2, 5, 8)),
               4: Perm((1, 0, 2, 4, 3)),
               17: Perm((0, 1, 2))}

    assert (Obstruction.decompress(simpleob.compress(patthash), revhash)
            == simpleob)
    assert (Obstruction.decompress(singlecellob.compress(patthash), revhash)
            == singlecellob)
    assert (Obstruction.decompress(everycellob.compress(patthash), revhash)
            == everycellob)
    assert (Obstruction.decompress(typicalob.compress(patthash), revhash)
            == typicalob)
    assert (Obstruction.decompress(isolatedob.compress(patthash), revhash)
            == isolatedob)

    assert (Obstruction.decompress(simpleob.compress())
            == simpleob)
    assert (Obstruction.decompress(singlecellob.compress())
            == singlecellob)
    assert (Obstruction.decompress(everycellob.compress())
            == everycellob)
    assert (Obstruction.decompress(typicalob.compress())
            == typicalob)
    assert (Obstruction.decompress(isolatedob.compress())
            == isolatedob)


def test_isolated_point():
    ob = Obstruction(Perm((0, 1, 2)),
                     [(0, 1), (1, 1), (1, 2)])
    assert (list(ob.isolate_point_row((1, 1))) ==
            [Obstruction(Perm((0, 1, 2)),
                         [(0, 1), (1, 2), (1, 4)])])
    assert (list(ob.isolate_point_col((1, 1))) ==
            [Obstruction(Perm((0, 1, 2)),
                         [(0, 1), (2, 1), (3, 2)])])
    ob = Obstruction(Perm((0, 1)),
                     [(1, 2), (1, 2)])
    assert (sorted(ob.isolate_point_col((1, 1))) ==
            [Obstruction(Perm((0, 1)),
                         [(1, 2), (1, 2)]),
             Obstruction(Perm((0, 1)),
                         [(1, 2), (3, 2)]),
             Obstruction(Perm((0, 1)),
                         [(3, 2), (3, 2)])])
    assert (sorted(ob.isolate_point_row((1, 1))) ==
            [Obstruction(Perm((0, 1)),
                         [(1, 4), (1, 4)])])
    ob = Obstruction(Perm((3, 2, 0, 1)),
                     [(0, 1), (0, 1), (1, 0), (2, 1)])
    assert (sorted(ob.isolate_point_col((1, 1))) ==
            [Obstruction(Perm((3, 2, 0, 1)),
                         [(0, 1), (0, 1), (1, 0), (4, 1)]),
             Obstruction(Perm((3, 2, 0, 1)),
                         [(0, 1), (0, 1), (3, 0), (4, 1)])])
    assert (sorted(ob.isolate_point_row((1, 1))) ==
            [Obstruction(Perm((3, 2, 0, 1)),
                         [(0, 1), (0, 1), (1, 0), (2, 1)]),
             Obstruction(Perm((3, 2, 0, 1)),
                         [(0, 3), (0, 1), (1, 0), (2, 1)]),
             Obstruction(Perm((3, 2, 0, 1)),
                         [(0, 3), (0, 3), (1, 0), (2, 1)]),
             Obstruction(Perm((3, 2, 0, 1)),
                         [(0, 3), (0, 3), (1, 0), (2, 3)])])


def test_point_seperation():
    ob = Obstruction.single_cell(Perm((0, 2, 1)), (0, 0))
    assert list(ob.point_separation((0, 0), DIR_WEST)) == [
        Obstruction(Perm((0, 2, 1)), [(1, 0), (1, 0), (1, 0)]),
        Obstruction(Perm((0, 2, 1)), [(0, 0), (1, 0), (1, 0)])]
    assert list(ob.point_separation((0, 0), DIR_EAST)) == [
        Obstruction(Perm((0, 2, 1)), [(0, 0), (0, 0), (1, 0)]),
        Obstruction(Perm((0, 2, 1)), [(0, 0), (0, 0), (0, 0)])]
    assert list(ob.point_separation((0, 0), DIR_NORTH)) == [
        Obstruction(Perm((0, 2, 1)), [(0, 0), (0, 1), (0, 0)]),
        Obstruction(Perm((0, 2, 1)), [(0, 0), (0, 0), (0, 0)])]
    assert list(ob.point_separation((0, 0), DIR_SOUTH)) == [
        Obstruction(Perm((0, 2, 1)), [(0, 1), (0, 1), (0, 1)]),
        Obstruction(Perm((0, 2, 1)), [(0, 0), (0, 1), (0, 1)])]

    ob = Obstruction.single_cell(Perm((0, 2, 1, 3)), (0, 0))
    assert list(ob.point_separation((0, 0), DIR_WEST)) == [
        Obstruction(Perm((0, 2, 1, 3)), [(1, 0), (1, 0), (1, 0), (1, 0)]),
        Obstruction(Perm((0, 2, 1, 3)), [(0, 0), (1, 0), (1, 0), (1, 0)])]

    assert list(ob.point_separation((0, 0), DIR_NORTH)) == [
        Obstruction(Perm((0, 2, 1, 3)), [(0, 0), (0, 0), (0, 0), (0, 1)]),
        Obstruction(Perm((0, 2, 1, 3)), [(0, 0), (0, 0), (0, 0), (0, 0)])]

    ob = Obstruction(Perm((0, 2, 1, 3)),
                     [(0, 0), (1, 1), (1, 1), (2, 2)])
    assert list(ob.point_separation((1, 1), DIR_WEST)) == [
        Obstruction(Perm((0, 2, 1, 3)),
                    [(0, 0), (2, 1), (2, 1), (3, 2)]),
        Obstruction(Perm((0, 2, 1, 3)),
                    [(0, 0), (1, 1), (2, 1), (3, 2)])]
    assert list(ob.point_separation((1, 1), DIR_NORTH)) == [
        Obstruction(Perm((0, 2, 1, 3)),
                    [(0, 0), (1, 2), (1, 1), (2, 3)]),
        Obstruction(Perm((0, 2, 1, 3)),
                    [(0, 0), (1, 1), (1, 1), (2, 3)])]

    ob = Obstruction(Perm((0, 1, 2)),
                     [(0, 0), (2, 2), (2, 2)])
    assert list(ob.point_separation((1, 1), DIR_EAST)) == [
        Obstruction(Perm((0, 1, 2)),
                    [(0, 0), (3, 2), (3, 2)])]
    assert list(ob.point_separation((1, 1), DIR_SOUTH)) == [
        Obstruction(Perm((0, 1, 2)),
                    [(0, 0), (2, 3), (2, 3)])]


def test_rotatation(bigob):

    def rotate90_cell(cols, cell):
        return (cell[1],
                cols - cell[0] - 1)

    def rotate180_cell(cols, rows, cell):
        return (cols - cell[0] - 1,
                rows - cell[1] - 1)

    def rotate270_cell(rows, cell):
        return (rows - cell[1] - 1,
                cell[0])

    assert bigob.rotate90(partial(rotate90_cell, 17)) == Obstruction(
        Perm((5, 8, 4, 9, 0, 2, 7, 1, 6, 3)),
        [(1, 5), (2, 8), (2, 4), (4, 9), (6, 1),
         (6, 3), (7, 7), (8, 2), (9, 6), (10, 3)])

    assert bigob.rotate90(partial(rotate90_cell, 17)).rotate90(
        partial(rotate90_cell, 21)) == bigob.rotate180(
            partial(rotate180_cell, 17, 21))

    assert bigob.rotate90(partial(rotate90_cell, 17)).rotate90(
        partial(rotate90_cell, 21)).rotate90(
            partial(rotate90_cell, 17)) == bigob.rotate270(
                partial(rotate270_cell, 21))


def test_inverse(bigob):

    def inverse_cell(cell):
        return (cell[1], cell[0])

    assert bigob.inverse(inverse_cell) == Obstruction(
        Perm((4, 1, 5, 0, 9, 7, 2, 8, 3, 6)),
        [(1, 11), (2, 8), (2, 12), (4, 7), (6, 15),
         (6, 13), (7, 9), (8, 14), (9, 10), (10, 13)])

    assert bigob.inverse(inverse_cell).inverse(inverse_cell) == bigob


def test_complement(bigob):

    def complement_cell(cell):
        return (cell[0], 21 - cell[1] - 1)

    assert bigob.complement(complement_cell) == Obstruction(
        Perm((6, 8, 3, 1, 9, 7, 0, 4, 2, 5)),
        [(7, 16), (8, 18), (9, 13), (10, 11), (11, 19),
         (12, 18), (13, 10), (13, 14), (14, 12), (15, 14)])


def test_reverse(bigob):

    def reverse_cell(cell):
        return (17 - cell[0] - 1, cell[1])

    assert bigob.reverse(reverse_cell) == Obstruction(
        Perm((4, 7, 5, 9, 2, 0, 8, 6, 1, 3)),
        [(1, 6), (2, 8), (3, 6), (3, 10), (4, 2),
         (5, 1), (6, 9), (7, 7), (8, 2), (9, 4)])

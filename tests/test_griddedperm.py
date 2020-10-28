import pytest

from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST
from tilings import GriddedPerm


@pytest.fixture
def simpleob():
    return GriddedPerm((1, 0, 3, 2), ((0, 0), (0, 0), (2, 2), (2, 1)))


@pytest.fixture
def singlecellob():
    return GriddedPerm.single_cell((1, 0, 3, 2), (2, 2))


@pytest.fixture
def everycellob():
    return GriddedPerm(
        Perm((0, 3, 6, 1, 4, 7, 2, 5, 8)),
        ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)),
    )


@pytest.fixture
def typicalob():
    return GriddedPerm((1, 0, 2, 4, 3), ((0, 0), (0, 0), (1, 0), (1, 1), (1, 1)))


@pytest.fixture
def isolatedob():
    return GriddedPerm((0, 1, 2), ((0, 0), (1, 1), (2, 2)))


def test_from_iterable():
    pos = ((0, 0), (1, 1), (2, 1))
    gp = GriddedPerm(Perm((0, 1, 2)), pos)
    assert GriddedPerm((0, 1, 2), pos) == gp
    assert GriddedPerm([0, 1, 2], pos) == gp
    assert GriddedPerm(range(3), pos) == gp
    assert GriddedPerm((i for i in range(3)), pos) == gp
    assert GriddedPerm.single_cell((0, 1), (0, 0)) == GriddedPerm(
        Perm((0, 1)), ((0, 0), (0, 0))
    )
    assert GriddedPerm(
        (0, 2, 1, 3, 4), ((0, 0), (0, 1), (1, 0), (1, 1), (1, 1))
    )._cells == {
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    }


def test_single_cell():
    gp = GriddedPerm.single_cell((0, 1, 2), (2, 3))
    assert gp.patt == Perm((0, 1, 2))
    assert gp.pos == ((2, 3), (2, 3), (2, 3))

    gp = GriddedPerm.single_cell((0,), (45, 64))
    assert gp.patt == Perm((0,))
    assert gp.pos == ((45, 64),)


def test_empty_perm():
    gp = GriddedPerm.empty_perm()
    assert gp.patt == Perm(())
    assert gp.pos == ()
    assert len(gp._cells) == 0
    assert GriddedPerm() == gp == GriddedPerm((), ())


def test_contradictory(simpleob, singlecellob, everycellob):
    assert not simpleob.contradictory()
    assert not singlecellob.contradictory()
    assert not everycellob.contradictory()
    gp = GriddedPerm((0, 1), [(0, 1), (1, 0)])
    assert gp.contradictory()
    gp = GriddedPerm((0, 1), [(1, 0), (0, 0)])
    assert gp.contradictory()
    gp = GriddedPerm((1, 0), [(0, 0), (1, 1)])
    assert gp.contradictory()


def test_occupies(simpleob):
    assert simpleob.occupies((0, 0))
    assert simpleob.occupies((2, 1))
    assert simpleob.occupies((2, 2))

    assert not simpleob.occupies((0, 1))
    assert not simpleob.occupies((3, 1))
    assert not simpleob.occupies((2, 0))


def test_occurrences_in(simpleob):
    ob = GriddedPerm((0, 2, 1), ((0, 0), (2, 2), (2, 1)))
    assert list(ob.occurrences_in(simpleob)) == [(0, 2, 3), (1, 2, 3)]
    assert ob.occurs_in(simpleob)

    ob = GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (2, 1)))
    assert list(ob.occurrences_in(simpleob)) == [(0, 1, 3)]
    assert ob.occurs_in(simpleob)

    ob = GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (2, 2)))
    assert list(ob.occurrences_in(simpleob)) == [(0, 1, 2)]
    assert ob.occurs_in(simpleob)

    ob = GriddedPerm((0, 1, 2), ((0, 0), (2, 2), (2, 1)))
    assert not any(ob.occurrences_in(simpleob))
    assert not ob.occurs_in(simpleob)

    ob = GriddedPerm((1, 0, 2), ((0, 0), (2, 2), (2, 2)))
    assert not any(ob.occurrences_in(simpleob))
    assert not ob.occurs_in(simpleob)

    ob = GriddedPerm(Perm(tuple()), tuple())
    assert ob in ob


def test_avoids():
    gp = GriddedPerm(
        Perm((0, 5, 1, 4, 2, 3, 6)),
        ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
    )
    assert gp.avoids(GriddedPerm((0, 2, 1), ((0, 0),) * 3))
    assert gp.avoids(
        GriddedPerm((0, 2, 1), ((0, 0),) * 3),
        GriddedPerm((0, 2, 1), ((1, 1), (1, 1), (2, 2))),
    )


def test_contains():
    gp = GriddedPerm(
        Perm((0, 5, 1, 4, 2, 3, 6)),
        ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
    )
    assert gp.contains(GriddedPerm())
    assert all(gp.contains(GriddedPerm((0,), (pos,))) for pos in gp._cells)
    assert gp.contains(GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 2))))
    assert gp.contains(GriddedPerm((2, 0, 1), ((1, 1),) * 3))
    assert gp.contains(
        GriddedPerm((0, 2, 1), ((0, 0),) * 3),
        GriddedPerm((0, 2, 1), ((1, 1), (1, 1), (2, 2))),
        GriddedPerm((1, 0, 2), ((1, 1), (1, 1), (2, 2))),
    )
    assert GriddedPerm().contains(GriddedPerm())


def test_remove_cells(simpleob, everycellob):
    assert simpleob.remove_cells([(0, 0)]) == GriddedPerm((1, 0), ((2, 2), (2, 1)))
    assert simpleob.remove_cells([(0, 0), (2, 2)]) == GriddedPerm((0,), ((2, 1),))
    assert simpleob.remove_cells([(0, 1), (1, 2)]) == simpleob
    gen = (cell for cell in ((0, 1), (1, 0)))
    assert everycellob.remove_cells(gen) == GriddedPerm(
        Perm((0, 4, 2, 5, 1, 3, 6)),
        ((0, 0), (0, 2), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)),
    )


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
    assert list(everycellob.get_points_below_row(2)) == [
        (0, 0),
        (1, 3),
        (3, 1),
        (4, 4),
        (6, 2),
        (7, 5),
    ]
    assert list(everycellob.get_points_right_col(1)) == [(6, 2), (7, 5), (8, 8)]
    assert list(everycellob.get_points_left_col(1)) == [(0, 0), (1, 3), (2, 6)]


def test_get_subperm_left_col(everycellob, simpleob, typicalob):
    assert everycellob.get_subperm_left_col(0) == GriddedPerm((), ())
    assert everycellob.get_subperm_left_col(1) == GriddedPerm(
        (0, 1, 2), ((0, 0), (0, 1), (0, 2))
    )
    assert everycellob.get_subperm_left_col(2) == GriddedPerm(
        (0, 2, 4, 1, 3, 5), ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2))
    )
    assert everycellob.get_subperm_left_col(3) == everycellob

    assert simpleob.get_subperm_left_col(1) == GriddedPerm((1, 0), ((0, 0), (0, 0)))
    assert simpleob.get_subperm_left_col(10) == simpleob

    assert typicalob.get_subperm_left_col(1) == GriddedPerm((1, 0), ((0, 0), (0, 0)))
    assert typicalob.get_subperm_left_col(100) == typicalob


def test_get_bounding_box(typicalob):
    assert typicalob.get_bounding_box((1, 0)) == (2, 5, 0, 3)
    assert typicalob.get_bounding_box((2, 2)) == (5, 5, 5, 5)


def test_is_point_perm(typicalob, singlecellob):
    assert not typicalob.is_point_perm()
    assert not singlecellob.is_point_perm()
    assert GriddedPerm((0,), ((0, 0),)).is_point_perm()
    assert GriddedPerm((0,), ((3, 2),)).is_point_perm()
    assert GriddedPerm((0,), ((100, 10),)).is_point_perm()


def test_is_single_cell(typicalob, simpleob, singlecellob):
    assert not typicalob.is_single_cell()
    assert not simpleob.is_single_cell()
    assert singlecellob.is_single_cell()


def test_insert_point():
    ob = GriddedPerm(
        (0, 4, 1, 2, 3, 5), [(0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (2, 2)]
    )
    assert list(ob.insert_point((1, 1))) == [
        GriddedPerm(
            Perm((0, 5, 1, 2, 3, 4, 6)),
            ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
        ),
        GriddedPerm(
            Perm((0, 5, 1, 3, 2, 4, 6)),
            ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
        ),
        GriddedPerm(
            Perm((0, 5, 1, 4, 2, 3, 6)),
            ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
        ),
        GriddedPerm(
            Perm((0, 4, 1, 5, 2, 3, 6)),
            ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
        ),
        GriddedPerm(
            Perm((0, 5, 1, 3, 2, 4, 6)),
            ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
        ),
        GriddedPerm(
            Perm((0, 5, 1, 2, 3, 4, 6)),
            ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
        ),
        GriddedPerm(
            Perm((0, 5, 1, 2, 4, 3, 6)),
            ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
        ),
        GriddedPerm(
            Perm((0, 4, 1, 2, 5, 3, 6)),
            ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
        ),
        GriddedPerm(
            Perm((0, 5, 1, 3, 4, 2, 6)),
            ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
        ),
        GriddedPerm(
            Perm((0, 5, 1, 2, 4, 3, 6)),
            ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
        ),
        GriddedPerm(
            Perm((0, 5, 1, 2, 3, 4, 6)),
            ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
        ),
        GriddedPerm(
            Perm((0, 4, 1, 2, 3, 5, 6)),
            ((0, 0), (0, 1), (0, 0), (1, 1), (1, 1), (1, 1), (2, 2)),
        ),
    ]


def test_all_subperms(simpleob):
    assert list(sorted(simpleob.all_subperms())) == [
        GriddedPerm((), ()),
        GriddedPerm((0,), ((0, 0),)),
        GriddedPerm((0,), ((0, 0),)),
        GriddedPerm((0,), ((2, 1),)),
        GriddedPerm((0,), ((2, 2),)),
        GriddedPerm((0, 1), ((0, 0), (2, 1))),
        GriddedPerm((0, 1), ((0, 0), (2, 1))),
        GriddedPerm((0, 1), ((0, 0), (2, 2))),
        GriddedPerm((0, 1), ((0, 0), (2, 2))),
        GriddedPerm((1, 0), ((0, 0), (0, 0))),
        GriddedPerm((1, 0), ((2, 2), (2, 1))),
        GriddedPerm((0, 2, 1), ((0, 0), (2, 2), (2, 1))),
        GriddedPerm((0, 2, 1), ((0, 0), (2, 2), (2, 1))),
        GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (2, 1))),
        GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (2, 2))),
    ]
    assert list(sorted(simpleob.all_subperms(proper=False))) == [
        GriddedPerm((), ()),
        GriddedPerm((0,), ((0, 0),)),
        GriddedPerm((0,), ((0, 0),)),
        GriddedPerm((0,), ((2, 1),)),
        GriddedPerm((0,), ((2, 2),)),
        GriddedPerm((0, 1), ((0, 0), (2, 1))),
        GriddedPerm((0, 1), ((0, 0), (2, 1))),
        GriddedPerm((0, 1), ((0, 0), (2, 2))),
        GriddedPerm((0, 1), ((0, 0), (2, 2))),
        GriddedPerm((1, 0), ((0, 0), (0, 0))),
        GriddedPerm((1, 0), ((2, 2), (2, 1))),
        GriddedPerm((0, 2, 1), ((0, 0), (2, 2), (2, 1))),
        GriddedPerm((0, 2, 1), ((0, 0), (2, 2), (2, 1))),
        GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (2, 1))),
        GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (2, 2))),
        GriddedPerm((1, 0, 3, 2), ((0, 0), (0, 0), (2, 2), (2, 1))),
    ]


def test_remove_point(typicalob, simpleob, singlecellob):
    assert simpleob.remove_point(0) == GriddedPerm((0, 2, 1), [(0, 0), (2, 2), (2, 1)])
    assert simpleob.remove_point(1) == GriddedPerm((0, 2, 1), [(0, 0), (2, 2), (2, 1)])
    assert simpleob.remove_point(2) == GriddedPerm((1, 0, 2), [(0, 0), (0, 0), (2, 1)])
    assert simpleob.remove_point(3) == GriddedPerm((1, 0, 2), [(0, 0), (0, 0), (2, 2)])

    assert typicalob.remove_point(0) == GriddedPerm(
        (0, 1, 3, 2), [(0, 0), (1, 0), (1, 1), (1, 1)]
    )
    assert typicalob.remove_point(1) == GriddedPerm(
        (0, 1, 3, 2), [(0, 0), (1, 0), (1, 1), (1, 1)]
    )
    assert typicalob.remove_point(2) == GriddedPerm(
        (1, 0, 3, 2), [(0, 0), (0, 0), (1, 1), (1, 1)]
    )
    assert typicalob.remove_point(3) == GriddedPerm(
        (1, 0, 2, 3), [(0, 0), (0, 0), (1, 0), (1, 1)]
    )
    assert typicalob.remove_point(4) == GriddedPerm(
        (1, 0, 2, 3), [(0, 0), (0, 0), (1, 0), (1, 1)]
    )

    assert singlecellob.remove_point(0) == GriddedPerm(
        (0, 2, 1), [(2, 2), (2, 2), (2, 2)]
    )
    assert singlecellob.remove_point(1) == GriddedPerm(
        (0, 2, 1), [(2, 2), (2, 2), (2, 2)]
    )
    assert singlecellob.remove_point(2) == GriddedPerm(
        (1, 0, 2), [(2, 2), (2, 2), (2, 2)]
    )
    assert singlecellob.remove_point(3) == GriddedPerm(
        (1, 0, 2), [(2, 2), (2, 2), (2, 2)]
    )


def test_apply_map(typicalob, simpleob):
    def cell_mapping(x):
        return (x[0] + 1, x[1] + 2)

    assert typicalob.apply_map(cell_mapping) == GriddedPerm(
        (1, 0, 2, 4, 3), ((1, 2), (1, 2), (2, 2), (2, 3), (2, 3))
    )
    assert simpleob.apply_map(cell_mapping) == GriddedPerm(
        (1, 0, 3, 2), ((1, 2), (1, 2), (3, 4), (3, 3))
    )


def test_compression(simpleob, singlecellob, everycellob, typicalob, isolatedob):
    assert simpleob == GriddedPerm.decompress(simpleob.compress())
    assert singlecellob == GriddedPerm.decompress(singlecellob.compress())
    assert everycellob == GriddedPerm.decompress(everycellob.compress())
    assert typicalob == GriddedPerm.decompress(typicalob.compress())
    assert isolatedob == GriddedPerm.decompress(isolatedob.compress())


def test_plot_helper():
    gp = GriddedPerm(
        Perm((0, 3, 6, 1, 4, 7, 2, 5, 8)),
        ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)),
    )
    pos, dim = gp._get_plot_pos()
    assert dim == (3, 3)
    assert pos[0] == (0.25, 0.25)
    assert pos[3] == (0.5, 1.25)
    assert pos[6] == (0.75, 2.25)
    assert pos[1] == (1.25, 0.5)
    assert pos[4] == (1.5, 1.5)
    assert pos[7] == (1.75, 2.5)
    assert pos[2] == (2.25, 0.75)
    assert pos[5] == (2.5, 1.75)
    assert pos[8] == (2.75, 2.75)


def test_permute_columns():
    gp1 = GriddedPerm(
        (5, 1, 4, 2, 7, 3, 6, 0),
        ((0, 1), (0, 0), (1, 1), (1, 0), (1, 2), (2, 1), (3, 2), (3, 0)),
    )
    perm1 = (3, 2, 0, 1)
    expected1 = GriddedPerm(
        (6, 0, 3, 5, 1, 4, 2, 7),
        ((0, 2), (0, 0), (1, 1), (2, 1), (2, 0), (3, 1), (3, 0), (3, 2)),
    )

    gp2 = GriddedPerm(
        (0,),
        ((0, 0),),
    )
    perm2 = (1, 2, 0)
    expected2 = GriddedPerm(
        (0,),
        ((2, 0),),
    )

    assert gp1.permute_columns(perm1) == expected1
    assert gp2.permute_columns(perm2) == expected2


def test_column_reverse():
    assert GriddedPerm(
        (4, 1, 3, 0, 5, 2), ((0, 1), (0, 0), (1, 1), (1, 0), (1, 2), (2, 1))
    ).column_reverse(1) == GriddedPerm(
        (4, 1, 5, 0, 3, 2), ((0, 1), (0, 0), (1, 2), (1, 0), (1, 1), (2, 1))
    )


def test_row_complement():
    assert GriddedPerm(
        (2, 0, 4, 5, 8, 1, 7, 6, 3),
        ((0, 1), (0, 0), (0, 1), (0, 1), (0, 2), (1, 0), (1, 2), (1, 1), (1, 1)),
    ).row_complement(1) == GriddedPerm(
        (6, 0, 4, 3, 8, 1, 7, 2, 5),
        ((0, 1), (0, 0), (0, 1), (0, 1), (0, 2), (1, 0), (1, 2), (1, 1), (1, 1)),
    )

    for gp in (
        GriddedPerm((1, 0), ((2, 2), (2, 1))),
        GriddedPerm(
            (5, 1, 4, 2, 7, 3, 6, 0),
            ((0, 1), (0, 0), (1, 1), (1, 0), (1, 2), (2, 1), (3, 2), (3, 0)),
        ),
    ):
        for i in range(3):
            assert gp.rotate90(lambda z: (z[1], 3 - z[0] - 1)).column_reverse(
                i
            ).rotate270(lambda z: (3 - z[1] - 1, z[0])) == gp.row_complement(i)


def test_permute_rows():
    assert GriddedPerm(
        Perm((0, 2, 1, 4, 3)), ((0, 0), (0, 1), (0, 0), (1, 2), (2, 1))
    ).permute_rows((2, 0, 1)) == GriddedPerm(
        Perm((1, 3, 2, 0, 4)), ((0, 1), (0, 2), (0, 1), (1, 0), (2, 2))
    )

    assert GriddedPerm((0,), ((0, 0),),).permute_rows((1, 2, 0)) == GriddedPerm(
        (0,),
        ((0, 2),),
    )


def test_to_jsonable():
    assert GriddedPerm(
        (5, 1, 4, 2, 7, 3, 6, 0),
        ((0, 1), (0, 0), (1, 1), (1, 0), (1, 2), (2, 1), (3, 2), (3, 0)),
    ).to_jsonable() == {
        "patt": Perm((5, 1, 4, 2, 7, 3, 6, 0)),
        "pos": ((0, 1), (0, 0), (1, 1), (1, 0), (1, 2), (2, 1), (3, 2), (3, 0)),
    }
    assert GriddedPerm((), ()).to_jsonable() == {"patt": Perm(()), "pos": ()}


def test_apply_perm_map_to_cell():
    def do_nothing_for_empty_perm(perm):
        assert perm == ()
        return perm

    gp = GriddedPerm((1, 0, 2, 4, 3), ((1, 2), (1, 2), (2, 2), (2, 3), (2, 3)))
    assert gp.apply_perm_map_to_cell(do_nothing_for_empty_perm, (0, 0)) == gp

    assert (
        GriddedPerm().apply_perm_map_to_cell(do_nothing_for_empty_perm, (0, 0))
        == GriddedPerm()
    )

    pos = [(0, 0), (0, 1), (0, 0), (0, 1), (0, 1), (0, 2), (1, 1)]
    gp = GriddedPerm((0, 4, 1, 2, 3, 6, 5), pos)

    assert gp.apply_perm_map_to_cell(lambda p: p.complement(), (0, 1)) == GriddedPerm(
        (0, 2, 1, 4, 3, 6, 5), pos
    )
    assert gp.apply_perm_map_to_cell(lambda p: p.inverse(), (0, 1)) == GriddedPerm(
        (0, 3, 1, 4, 2, 6, 5), pos
    )
    assert gp.apply_perm_map_to_cell(lambda p: p.reverse(), (0, 1)) == GriddedPerm(
        (0, 3, 1, 2, 4, 6, 5), pos
    )


def test_is_interleaving():
    assert GriddedPerm(
        (5, 1, 4, 2, 7, 3, 6, 0),
        ((0, 1), (0, 0), (1, 1), (1, 0), (1, 2), (2, 1), (3, 2), (3, 0)),
    ).is_interleaving()
    assert not GriddedPerm(
        Perm((0, 1, 2, 3, 4, 5)), ((i, i) for i in range(6))
    ).is_interleaving()
    assert not GriddedPerm().is_interleaving()
    assert not GriddedPerm((0,), ((0, 0),)).is_interleaving()
    assert GriddedPerm(
        Perm((0, 6, 1, 2, 3, 4, 5)),
        [(0, 0), (0, 20), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)],
    ).is_interleaving()
    assert GriddedPerm(
        Perm((0, 2, 3, 4, 5, 6, 1)),
        [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 0)],
    ).is_interleaving()


def test_extend():
    gp = GriddedPerm((1, 0), ((0, 1), (1, 0)))
    assert set(gp.extend(2, 2)) == {
        GriddedPerm((2, 1, 0), ((0, 1), (0, 1), (1, 0))),
        GriddedPerm((1, 2, 0), ((0, 1), (0, 1), (1, 0))),
        GriddedPerm((1, 2, 0), ((0, 1), (1, 1), (1, 0))),
        GriddedPerm((1, 0, 2), ((0, 1), (1, 0), (1, 1))),
    }

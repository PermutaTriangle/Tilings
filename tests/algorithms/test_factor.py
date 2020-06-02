from itertools import combinations, product

import pytest

from permuta import Perm
from permuta.misc.union_find import UnionFind
from tilings import GriddedPerm, Tiling
from tilings.algorithms import (
    Factor,
    FactorWithInterleaving,
    FactorWithMonotoneInterleaving,
)

# ------------------------------------------------
#      Fixture and utility
# ------------------------------------------------


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
def not_fact_tiling():
    not_fact_tiling = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
        ]
    )
    return not_fact_tiling


@pytest.fixture
def factor1(tiling1):
    return Factor(tiling1)


@pytest.fixture
def factor2(tiling2):
    return Factor(tiling2)


@pytest.fixture
def factor1_with_int(tiling1):
    return FactorWithInterleaving(tiling1)


@pytest.fixture
def factor2_with_int(tiling2):
    return FactorWithInterleaving(tiling2)


@pytest.fixture
def factor1_with_mon_int(tiling1):
    return FactorWithMonotoneInterleaving(tiling1)


@pytest.fixture
def factor2_with_mon_int(tiling2):
    return FactorWithMonotoneInterleaving(tiling2)


# ------------------------------------------------
#       Test for the class Factor
# ------------------------------------------------


def test_init(tiling1):
    f = Factor(tiling1)
    assert f._tiling == tiling1
    assert f._active_cells == frozenset([(0, 0), (1, 1), (2, 2), (1, 2), (3, 0)])
    assert isinstance(f._cell_unionfind, UnionFind)


def test_cell_to_int(factor1):
    for c in product(range(4), range(3)):
        assert factor1._int_to_cell(factor1._cell_to_int(c)) == c
    assert set(range(12)) == set(
        factor1._cell_to_int(c) for c in product(range(4), range(3))
    )


def test_int_to_cell(factor1):
    for i in range(12):
        assert factor1._cell_to_int(factor1._int_to_cell(i)) == i


def test_get_cell_representative(factor1):
    all_rep = set(
        factor1._get_cell_representative(c) for c in product(range(4), range(3))
    )
    assert len(all_rep) == 12


def test_unite_two_cells(factor1):
    cells = [(0, 0), (1, 1)]
    factor1._unite_cells(cells)
    assert factor1._get_cell_representative(
        cells[0]
    ) == factor1._get_cell_representative(cells[1])
    all_rep = set(
        factor1._get_cell_representative(c) for c in product(range(4), range(3))
    )
    assert len(all_rep) == 11


def test_unite_single_cell(factor1):
    cells = [(0, 0)]
    factor1._unite_cells(cells)
    all_rep = set(
        factor1._get_cell_representative(c) for c in product(range(4), range(3))
    )
    assert len(all_rep) == 12


def test_unite_multiple_cells(factor1):
    cells = [(0, 0), (1, 1), (2, 2), (3, 2)]
    factor1._unite_cells(cells)
    for c1, c2 in combinations(cells, r=2):
        assert factor1._get_cell_representative(c1) == factor1._get_cell_representative(
            c2
        )
    all_rep = set(
        factor1._get_cell_representative(c) for c in product(range(4), range(3))
    )
    assert len(all_rep) == 9


def test_unite_no_cell(factor1):
    cells = []
    with pytest.raises(StopIteration):
        factor1._unite_cells(cells)
    all_rep = set(
        factor1._get_cell_representative(c) for c in product(range(4), range(3))
    )
    assert len(all_rep) == 12


def test_unite_obstruction(factor1, factor2):
    comp1 = [(1, 1), (2, 2)]
    factor1._unite_obstructions()
    assert factor1._get_cell_representative(
        comp1[0]
    ) == factor1._get_cell_representative(comp1[1])
    all_rep = set(
        factor1._get_cell_representative(c) for c in product(range(4), range(3))
    )
    assert len(all_rep) == 11

    comp1 = [(0, 0), (0, 1), (1, 0), (1, 1)]
    comp2 = [(2, 2), (3, 2), (4, 2)]
    factor2._unite_obstructions()
    for c1, c2 in combinations(comp1, r=2):
        print(c1, c2)
        assert factor2._get_cell_representative(c1) == factor2._get_cell_representative(
            c2
        )
    for c1, c2 in combinations(comp2, r=2):
        print(c1, c2)
        assert factor2._get_cell_representative(c1) == factor2._get_cell_representative(
            c2
        )
    all_rep = set(
        factor2._get_cell_representative(c) for c in product(range(5), range(4))
    )
    assert len(all_rep) == 15


def test_unite_requirements(factor2):
    comp1 = [(0, 0), (0, 1)]
    comp2 = [(2, 3), (3, 3), (4, 3)]
    factor2._unite_requirements()
    for c1, c2 in combinations(comp1, r=2):
        print(c1, c2)
        assert factor2._get_cell_representative(c1) == factor2._get_cell_representative(
            c2
        )
    for c1, c2 in combinations(comp2, r=2):
        print(c1, c2)
        assert factor2._get_cell_representative(c1) == factor2._get_cell_representative(
            c2
        )
    all_rep = set(
        factor2._get_cell_representative(c) for c in product(range(5), range(4))
    )
    assert len(all_rep) == 17


def test_same_row_or_col(factor1):
    assert factor1._same_row_or_col((0, 0), (2, 0))
    assert not factor1._same_row_or_col((0, 3), (2, 0))
    assert factor1._same_row_or_col((2, 0), (2, 0))
    assert factor1._same_row_or_col((2, 0), (2, 2))


def test_unite_rows_and_cols(factor1, factor2):
    factor1._unite_rows_and_cols()
    comp1 = [(1, 1), (1, 2), (2, 2)]
    for c1, c2 in combinations(comp1, r=2):
        print(c1, c2)
        assert factor1._get_cell_representative(c1) == factor1._get_cell_representative(
            c2
        )
    assert factor1._get_cell_representative((0, 0)) == factor1._get_cell_representative(
        (3, 0)
    )
    all_rep = set(
        factor1._get_cell_representative(c) for c in product(range(4), range(3))
    )
    assert len(all_rep) == 9

    factor2._unite_rows_and_cols()
    comp1 = [(0, 0), (0, 1), (1, 0), (1, 1)]
    comp2 = [(2, 2), (3, 2), (4, 2), (2, 3), (3, 3), (4, 3)]
    all_rep = set(
        factor2._get_cell_representative(c) for c in product(range(5), range(4))
    )
    assert len(all_rep) == 12
    for c1, c2 in combinations(comp1, r=2):
        print(c1, c2)
        assert factor2._get_cell_representative(c1) == factor2._get_cell_representative(
            c2
        )
    for c1, c2 in combinations(comp2, r=2):
        print(c1, c2)
        assert factor2._get_cell_representative(c1) == factor2._get_cell_representative(
            c2
        )


def test_unite_all(factor1, factor2):
    factor1._unite_all()
    comp1 = [(1, 1), (1, 2), (2, 2)]
    all_rep = set(
        factor1._get_cell_representative(c) for c in product(range(4), range(3))
    )
    assert len(all_rep) == 9
    for c1, c2 in combinations(comp1, r=2):
        print(c1, c2)
        assert factor1._get_cell_representative(c1) == factor1._get_cell_representative(
            c2
        )
    assert factor1._get_cell_representative((0, 0)) == factor1._get_cell_representative(
        (3, 0)
    )

    factor2._unite_all()
    comp1 = [(0, 0), (0, 1), (1, 0), (1, 1)]
    comp2 = [(2, 2), (3, 2), (4, 2), (2, 3), (3, 3), (4, 3)]
    all_rep = set(
        factor2._get_cell_representative(c) for c in product(range(5), range(4))
    )
    assert len(all_rep) == 12
    for c1, c2 in combinations(comp1, r=2):
        print(c1, c2)
        assert factor2._get_cell_representative(c1) == factor2._get_cell_representative(
            c2
        )
    for c1, c2 in combinations(comp2, r=2):
        print(c1, c2)
        assert factor2._get_cell_representative(c1) == factor2._get_cell_representative(
            c2
        )


def test_get_components(factor1, factor2):
    comp1 = {(1, 1), (1, 2), (2, 2)}
    comp2 = {(0, 0), (3, 0)}
    assert comp1 in factor1.get_components()
    assert comp2 in factor1.get_components()
    assert len(factor1.get_components()) == 2

    comp1 = {(0, 0), (0, 1), (1, 0), (1, 1)}
    comp2 = {(2, 2), (3, 2), (4, 2), (2, 3), (3, 3), (4, 3)}
    assert comp1 in factor2.get_components()
    assert comp2 in factor2.get_components()
    assert len(factor1.get_components()) == 2

    empty_tiling = Tiling()
    assert Factor(empty_tiling).get_components() == tuple()

    point_tiling = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0))),
        ],
        requirements=[[GriddedPerm(Perm((0,)), ((0, 0),))]],
    )
    assert Factor(point_tiling).get_components() == ({(0, 0)},)


def test_get_factor_obs_and_reqs(factor1, factor2):
    obs1 = tuple(
        sorted(
            [
                GriddedPerm(Perm((2, 1, 0)), ((0, 0),) * 3),
                GriddedPerm(Perm((2, 0, 1)), ((3, 0),) * 3),
            ]
        )
    )
    obs2 = tuple(
        sorted(
            [
                GriddedPerm(Perm((0, 1, 2)), ((1, 2),) * 3),
                GriddedPerm(Perm((1, 0)), ((1, 1),) * 2),
                GriddedPerm(Perm((1, 0)), ((2, 2),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 1), (2, 2))),
            ]
        )
    )
    f1_obs_and_reqs = factor1._get_factors_obs_and_reqs()
    assert len(f1_obs_and_reqs) == 2
    assert (obs1, tuple(), tuple()) in f1_obs_and_reqs
    assert (obs2, tuple(), tuple()) in f1_obs_and_reqs

    obs1 = tuple(
        sorted(
            [
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
                GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 1))),
                GriddedPerm(Perm((0, 1)), ((0, 1), (1, 1))),
            ]
        )
    )
    obs2 = tuple(
        sorted(
            [
                GriddedPerm(Perm((0, 1)), ((3, 3),) * 2),
                GriddedPerm(Perm((0, 1)), ((4, 3),) * 2),
                GriddedPerm(Perm((0, 1, 2)), ((2, 3),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((2, 2),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((3, 2),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((4, 2),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((2, 2), (3, 2), (4, 2))),
            ]
        )
    )
    reqs1 = ((GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1))),),)
    reqs2 = (
        (
            GriddedPerm(Perm((0, 1)), ((2, 3), (3, 3))),
            GriddedPerm(Perm((0, 1)), ((3, 3), (4, 3))),
        ),
    )
    f2_obs_and_reqs = factor2._get_factors_obs_and_reqs()
    assert len(f2_obs_and_reqs) == 2
    assert (obs1, reqs1, tuple()) in f2_obs_and_reqs
    assert (obs2, reqs2, tuple()) in f2_obs_and_reqs


def test_factorable(factor1, factor2, not_fact_tiling):
    assert factor1.factorable()
    assert factor2.factorable()

    empty_tiling = Tiling()
    assert not Factor(empty_tiling).factorable()

    point_tiling = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0))),
        ],
        requirements=[[GriddedPerm(Perm((0,)), ((0, 0),))]],
    )
    assert not Factor(point_tiling).factorable()

    assert not Factor(not_fact_tiling).factorable()


def test_factor(factor1, factor2):
    f1 = Tiling(
        obstructions=[
            GriddedPerm(Perm((2, 1, 0)), ((0, 0),) * 3),
            GriddedPerm(Perm((2, 0, 1)), ((1, 0),) * 3),
        ]
    )
    f2 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
            GriddedPerm(Perm((1, 0)), ((0, 0),) * 2),
            GriddedPerm(Perm((1, 0)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1))),
        ]
    )
    assert len(factor1.factors()) == 2
    assert f1 in factor1.factors()
    assert f2 in factor1.factors()

    f1 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (1, 1))),
        ],
        requirements=[[GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1)))]],
    )
    f2 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((2, 1),) * 2),
            GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 0))),
        ],
        requirements=[
            [
                GriddedPerm(Perm((0, 1)), ((0, 1), (1, 1))),
                GriddedPerm(Perm((0, 1)), ((1, 1), (2, 1))),
            ],
        ],
    )
    assert len(factor2.factors()) == 2
    assert f1 in factor2.factors()
    assert f2 in factor2.factors()


def test_reducible_factorisations():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((2, 2),) * 2),
        ]
    )
    fo = Factor(t)
    f1 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
        ]
    )
    f2 = Tiling(obstructions=[GriddedPerm(Perm((0, 1)), ((0, 0),) * 2)])
    assert set([f1, f2]) in map(set, fo.reducible_factorisations())
    assert [f2, f2, f2] not in fo.reducible_factorisations()


# ------------------------------------------------------------
#       Test for the class FactorWithMonotoneInterleaving
# ------------------------------------------------------------


def test_unite_rows_and_cols_monotone_interleaving(
    factor1_with_mon_int, factor2_with_mon_int
):
    factor1_with_mon_int._unite_rows_and_cols()
    all_rep = set(
        factor1_with_mon_int._get_cell_representative(c)
        for c in product(range(4), range(3))
    )
    assert len(all_rep) == 11
    assert factor1_with_mon_int._get_cell_representative(
        (0, 0)
    ) == factor1_with_mon_int._get_cell_representative((3, 0))

    factor2_with_mon_int._unite_rows_and_cols()
    comp1 = [(2, 2), (3, 2), (4, 2), (2, 3)]
    all_rep = set(
        factor2_with_mon_int._get_cell_representative(c)
        for c in product(range(5), range(4))
    )
    assert len(all_rep) == 17
    for c1, c2 in combinations(comp1, r=2):
        assert factor2_with_mon_int._get_cell_representative(
            c1
        ) == factor2_with_mon_int._get_cell_representative(c2)


def test_mon_int_factor(factor1_with_mon_int, factor2_with_mon_int):
    f1 = Tiling(
        obstructions=[
            GriddedPerm(Perm((2, 1, 0)), ((0, 0),) * 3),
            GriddedPerm(Perm((2, 0, 1)), ((1, 0),) * 3),
        ]
    )
    f2 = Tiling(
        obstructions=[
            GriddedPerm(Perm((1, 0)), ((0, 0),) * 2),
            GriddedPerm(Perm((1, 0)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1))),
        ]
    )
    f3 = Tiling(obstructions=[GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3)])
    assert len(factor1_with_mon_int.factors()) == 3
    assert f1 in factor1_with_mon_int.factors()
    assert f2 in factor1_with_mon_int.factors()
    assert f3 in factor1_with_mon_int.factors()

    f1 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (1, 1))),
        ],
        requirements=[[GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1)))]],
    )
    f2 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((2, 1),) * 2),
            GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 0))),
        ],
        requirements=[
            [
                GriddedPerm(Perm((0, 1)), ((0, 1), (1, 1))),
                GriddedPerm(Perm((0, 1)), ((1, 1), (2, 1))),
            ],
        ],
    )
    assert len(factor2_with_mon_int.factors()) == 2
    assert f1 in factor2_with_mon_int.factors()
    assert f2 in factor2_with_mon_int.factors()


# ------------------------------------------------------------
#       Test for the class FactorWithInterleaving
# ------------------------------------------------------------


def test_unite_rows_and_cols_interleaving(factor1_with_int, factor2_with_int):
    factor1_with_int._unite_rows_and_cols()
    all_rep = set(
        factor1_with_int._get_cell_representative(c)
        for c in product(range(4), range(3))
    )
    assert len(all_rep) == 12

    factor2_with_int._unite_rows_and_cols()
    all_rep = set(
        factor2_with_int._get_cell_representative(c)
        for c in product(range(5), range(4))
    )
    assert len(all_rep) == 20


def test_unite_all_interleaving(factor1_with_int):
    print(factor1_with_int._tiling)
    factor1_with_int._unite_all()
    assert factor1_with_int._get_cell_representative(
        (1, 1)
    ) == factor1_with_int._get_cell_representative((2, 2))
    all_rep = set(
        factor1_with_int._get_cell_representative(c)
        for c in product(range(4), range(3))
    )
    assert len(all_rep) == 11


def test_int_factor(factor1_with_int, factor2_with_int):
    f1 = Tiling(obstructions=[GriddedPerm(Perm((2, 1, 0)), ((0, 0),) * 3)])
    f2 = Tiling(obstructions=[GriddedPerm(Perm((2, 0, 1)), ((1, 0),) * 3)])
    f3 = Tiling(
        obstructions=[
            GriddedPerm(Perm((1, 0)), ((0, 0),) * 2),
            GriddedPerm(Perm((1, 0)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1))),
        ]
    )
    f4 = Tiling(obstructions=[GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3)])
    assert len(factor1_with_int.factors()) == 4
    assert f1 in factor1_with_int.factors()
    assert f2 in factor1_with_int.factors()
    assert f3 in factor1_with_int.factors()
    assert f4 in factor1_with_int.factors()

    f1 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (1, 1))),
        ],
        requirements=[[GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1)))]],
    )
    f2 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 0))),
        ]
    )
    f3 = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((2, 0),) * 2),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
        ],
        requirements=[
            [
                GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
                GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
            ],
        ],
    )
    assert len(factor2_with_int.factors()) == 3
    assert f1 in factor2_with_int.factors()
    assert f2 in factor2_with_int.factors()
    assert f3 in factor2_with_int.factors()

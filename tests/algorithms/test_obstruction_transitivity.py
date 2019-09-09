import pytest

from permuta import Perm
from tilings import Obstruction, Requirement, Tiling


@pytest.fixture
def simple_trans_row():
    return Tiling(obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
                                Obstruction(Perm((0, 1)), [(1, 0), (2, 0)])],
                  requirements=[[Requirement(Perm((0,)), [(1, 0)])]])


@pytest.fixture
def simple_trans_col():
    return Tiling(obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (0, 1)]),
                                Obstruction(Perm((0, 1)), [(0, 1), (0, 2)])],
                  requirements=[[Requirement(Perm((0,)), [(0, 1)])]])


@pytest.fixture
def simple_trans_row_len2():
    return Tiling(obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
                                Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
                                Obstruction(Perm((0, 1)), [(2, 0), (3, 0)])],
                  requirements=[[Requirement(Perm((0,)), [(1, 0)])],
                                [Requirement(Perm((0,)), [(2, 0)])]])


@pytest.fixture
def simple_trans_row_len3():
    return Tiling(obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
                                Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
                                Obstruction(Perm((0, 1)), [(2, 0), (3, 0)]),
                                Obstruction(Perm((0, 1)), [(3, 0), (4, 0)])],
                  requirements=[[Requirement(Perm((0,)), [(1, 0)])],
                                [Requirement(Perm((0,)), [(2, 0)])],
                                [Requirement(Perm((0,)), [(3, 0)])]])


@pytest.mark.xfail
def test_obstruction_transitivity(simple_trans_row,
                                  simple_trans_col,
                                  simple_trans_row_len2,
                                  simple_trans_row_len3):
    strat = obstruction_transitivity(simple_trans_row)
    assert strat.comb_classes[0] == Tiling(
        obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
                      Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
                      Obstruction(Perm((0, 1)), [(0, 0), (2, 0)])],
        requirements=[[Requirement(Perm((0,)), [(1, 0)])]])

    strat = obstruction_transitivity(simple_trans_col)
    assert strat.comb_classes[0] == Tiling(
        obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (0, 1)]),
                      Obstruction(Perm((0, 1)), [(0, 1), (0, 2)]),
                      Obstruction(Perm((0, 1)), [(0, 0), (0, 2)])],
        requirements=[[Requirement(Perm((0,)), [(0, 1)])]])

    strat = obstruction_transitivity(simple_trans_row_len2)
    assert strat.comb_classes[0] == Tiling(
        obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
                      Obstruction(Perm((0, 1)), [(0, 0), (2, 0)]),
                      Obstruction(Perm((0, 1)), [(0, 0), (3, 0)]),
                      Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
                      Obstruction(Perm((0, 1)), [(1, 0), (3, 0)]),
                      Obstruction(Perm((0, 1)), [(2, 0), (3, 0)])],
        requirements=[[Requirement(Perm((0,)), [(1, 0)])],
                      [Requirement(Perm((0,)), [(2, 0)])]])

    strat = obstruction_transitivity(simple_trans_row_len3)
    assert strat.comb_classes[0] == Tiling(
        obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
                      Obstruction(Perm((0, 1)), [(0, 0), (2, 0)]),
                      Obstruction(Perm((0, 1)), [(0, 0), (3, 0)]),
                      Obstruction(Perm((0, 1)), [(0, 0), (4, 0)]),
                      Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
                      Obstruction(Perm((0, 1)), [(1, 0), (3, 0)]),
                      Obstruction(Perm((0, 1)), [(1, 0), (4, 0)]),
                      Obstruction(Perm((0, 1)), [(2, 0), (3, 0)]),
                      Obstruction(Perm((0, 1)), [(2, 0), (4, 0)]),
                      Obstruction(Perm((0, 1)), [(3, 0), (4, 0)])],
        requirements=[[Requirement(Perm((0,)), [(1, 0)])],
                      [Requirement(Perm((0,)), [(2, 0)])],
                      [Requirement(Perm((0,)), [(3, 0)])]])

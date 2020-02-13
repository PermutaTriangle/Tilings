from permuta import Perm
from tilings import Obstruction, Requirement, Tiling
from tilings.strategies import FactorStrategy

pytest_plugins = [
    'tests.fixtures.simple_tiling',
    'tests.fixtures.diverse_tiling',
    'tests.fixtures.no_point_tiling',
]


def test_not_factorable(simple_tiling):
    assert len(list(FactorStrategy()(simple_tiling))) == 0
    assert (len(list(FactorStrategy(interleaving='monotone')(simple_tiling)))
            == 0)
    assert len(list(FactorStrategy(interleaving='all')(simple_tiling))) == 0


def test_with_union(diverse_tiling):
    strats = list(FactorStrategy(interleaving='all',
                                 union=True)(diverse_tiling))
    assert len(strats) == 14
    assert sum(1 for s in strats if 'unions' in s.formal_step) == 13
    assert sum(1 for s in strats if all(s.workable)) == 1
    assert sum(1 for s in strats if not any(s.workable)) == 13


def test_with_union_not_workable(diverse_tiling):
    strats = list(FactorStrategy(
        interleaving='all', union=True, workable=False,
                            )(diverse_tiling))
    assert sum(1 for s in strats if all(s.workable)) == 0
    assert sum(1 for s in strats if not any(s.workable)) == 14


def test_standard_factor(simple_tiling):
    tiling = Tiling(
        obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (0, 0)])],
        requirements=[[Requirement(Perm((0, 1)), [(1, 1), (1, 1)]),
                       Requirement(Perm((0, 1)), [(1, 1), (1, 2)])]])
    strats = [s.comb_classes for s in FactorStrategy()(tiling)]
    assert len(strats) == 1
    factors = strats[0]
    assert set(factors) == set([
        Tiling(requirements=[[Requirement(Perm((0, 1)), [(0, 0), (0, 0)]),
                              Requirement(Perm((0, 1)), [(0, 0), (0, 1)])]]),
        Tiling(obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (0, 0)])])])


def test_factor_all_interleaving(diverse_tiling):
    strats = [s.comb_classes
              for s in FactorStrategy(interleaving='all')(diverse_tiling)]
    assert len(strats) == 1
    factors = strats[0]
    assert len(factors) == 4
    print(diverse_tiling)
    assert set(factors) == set([
        Tiling(obstructions=[Obstruction(Perm((0, 2, 3, 1)),
                                         [(0, 0), (1, 1), (1, 1), (2, 0)])],
               requirements=[[Requirement(Perm((0,)), [(2, 0)])]]),
        Tiling(obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (0, 0)]),
                             Obstruction(Perm((1, 0)), [(0, 0), (0, 0)])],
               requirements=[[Requirement(Perm((0,)), [(0, 0)])]]),
        Tiling(obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (0, 0)]),
                             Obstruction(Perm((1, 0)), [(0, 0), (0, 0)])],
               requirements=[[Requirement(Perm((0,)), [(0, 0)])]]),
        Tiling(requirements=[[Requirement(Perm((1, 0)), [(0, 2), (0, 1)]),
                              Requirement(Perm((0, 2, 1)),
                                          [(0, 1), (0, 2), (1, 2)])]])])

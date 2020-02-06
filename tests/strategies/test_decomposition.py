from permuta import Perm
from tilings import Obstruction, Requirement, Tiling
from tilings.algorithms import (Factor, FactorWithInterleaving,
                                FactorWithMonotoneInterleaving)
from tilings.strategies.decomposition import (factor, factor_with_interleaving,
                                              general_factor)

pytest_plugins = [
    'tests.fixtures.simple_tiling',
    'tests.fixtures.diverse_tiling',
    'tests.fixtures.no_point_tiling',
]


def test_general_factor(simple_tiling, diverse_tiling):
    assert len(list(general_factor(simple_tiling, Factor))) == 0
    assert (len(list(general_factor(simple_tiling,
                                    FactorWithMonotoneInterleaving))) == 0)
    assert (len(list(general_factor(simple_tiling,
                                    FactorWithInterleaving))) == 0)
    assert (len(list(general_factor(diverse_tiling,
                                    FactorWithInterleaving))) == 1)
    # Test union param
    strats = list(general_factor(diverse_tiling,
                                 FactorWithInterleaving,
                                 union=True))
    assert len(strats) == 14
    assert sum(1 for s in strats if 'unions' in s.formal_step) == 13
    assert sum(1 for s in strats if all(s.workable)) == 1
    assert sum(1 for s in strats if not any(s.workable)) == 13
    # Test union param with workable to False
    strats = list(general_factor(diverse_tiling,
                                 FactorWithInterleaving,
                                 union=True,
                                 workable=False))
    assert sum(1 for s in strats if all(s.workable)) == 0
    assert sum(1 for s in strats if not any(s.workable)) == 14
    # Test union param with workable to True
    strats = list(general_factor(diverse_tiling,
                                 FactorWithInterleaving,
                                 union=True,
                                 workable=True))
    assert sum(1 for s in strats if all(s.workable)) == 1
    assert sum(1 for s in strats if not any(s.workable)) == 13


def test_factor_no_unions(simple_tiling,
                          diverse_tiling,
                          no_point_tiling):
    assert len(list(factor(simple_tiling))) == 0
    assert len(list(factor(diverse_tiling))) == 0
    tiling = Tiling(
        obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (0, 0)])],
        requirements=[[Requirement(Perm((0, 1)), [(1, 1), (1, 1)]),
                       Requirement(Perm((0, 1)), [(1, 1), (1, 2)])]])
    strats = [s.comb_classes for s in factor(tiling)]
    assert len(strats) == 1
    factors = strats[0]
    assert set(factors) == set([
        Tiling(requirements=[[Requirement(Perm((0, 1)), [(0, 0), (0, 0)]),
                              Requirement(Perm((0, 1)), [(0, 0), (0, 1)])]]),
        Tiling(obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (0, 0)])])])

    strats = [s.comb_classes
              for s in factor_with_interleaving(diverse_tiling)]
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

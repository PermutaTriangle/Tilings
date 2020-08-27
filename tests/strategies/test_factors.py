from itertools import chain

import pytest

from comb_spec_searcher import CartesianProduct
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.strategies import FactorFactory
from tilings.strategies.factor import FactorStrategy, Interleaving

pytest_plugins = [
    "tests.fixtures.simple_tiling",
    "tests.fixtures.diverse_tiling",
    "tests.fixtures.no_point_tiling",
]


@pytest.fixture
def tiling():
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
def factor_rules(tiling):
    return [s(tiling) for s in FactorFactory()(tiling)]


@pytest.fixture
def factor_with_int_rules(tiling):
    return [s(tiling) for s in FactorFactory(interleaving="all")(tiling)]


@pytest.fixture
def factor_with_mon_int_rules(tiling):
    return [s(tiling) for s in FactorFactory(interleaving="monotone")(tiling)]


def test_not_factorable(simple_tiling):
    assert len(list(FactorFactory()(simple_tiling))) == 0
    assert len(list(FactorFactory(interleaving="monotone")(simple_tiling))) == 0
    assert len(list(FactorFactory(interleaving="all")(simple_tiling))) == 0


def test_with_unions(diverse_tiling):
    strats = list(FactorFactory(interleaving="all", unions=True)(diverse_tiling))
    assert len(strats) == 14
    assert sum(1 for s in strats if s.workable) == 1
    assert sum(1 for s in strats if not s.workable) == 13


def test_with_unions_not_workable(diverse_tiling):
    strats = list(
        FactorFactory(interleaving="all", unions=True, workable=False)(diverse_tiling)
    )
    assert sum(1 for s in strats if s.workable) == 0
    assert sum(1 for s in strats if not s.workable) == 14


def test_standard_factor():
    tiling = Tiling(
        obstructions=[GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)])],
        requirements=[
            [
                GriddedPerm(Perm((0, 1)), [(1, 1), (1, 1)]),
                GriddedPerm(Perm((0, 1)), [(1, 1), (1, 2)]),
            ]
        ],
    )
    strats = [s(tiling).children for s in FactorFactory()(tiling)]
    assert len(strats) == 1
    factors = strats[0]
    assert set(factors) == set(
        [
            Tiling(
                requirements=[
                    [
                        GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)]),
                        GriddedPerm(Perm((0, 1)), [(0, 0), (0, 1)]),
                    ]
                ]
            ),
            Tiling(obstructions=[GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)])]),
        ]
    )


def test_factor_all_interleaving(diverse_tiling):
    strats = [
        s(diverse_tiling).children
        for s in FactorFactory(interleaving="all")(diverse_tiling)
    ]
    assert len(strats) == 1
    factors = strats[0]
    assert len(factors) == 4
    print(diverse_tiling)
    assert set(factors) == set(
        [
            Tiling(
                obstructions=[
                    GriddedPerm(Perm((0, 2, 3, 1)), [(0, 0), (1, 1), (1, 1), (2, 0)])
                ],
                requirements=[[GriddedPerm(Perm((0,)), [(2, 0)])]],
            ),
            Tiling(
                obstructions=[
                    GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)]),
                    GriddedPerm(Perm((1, 0)), [(0, 0), (0, 0)]),
                ],
                requirements=[[GriddedPerm(Perm((0,)), [(0, 0)])]],
            ),
            Tiling(
                obstructions=[
                    GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)]),
                    GriddedPerm(Perm((1, 0)), [(0, 0), (0, 0)]),
                ],
                requirements=[[GriddedPerm(Perm((0,)), [(0, 0)])]],
            ),
            Tiling(
                requirements=[
                    [
                        GriddedPerm(Perm((1, 0)), [(0, 2), (0, 1)]),
                        GriddedPerm(Perm((0, 2, 1)), [(0, 1), (0, 2), (1, 2)]),
                    ]
                ]
            ),
        ]
    )


def test_str():
    assert str(FactorFactory()) == "factor"
    assert (
        str(FactorFactory(interleaving="monotone"))
        == "factor with monotone interleaving"
    )
    assert str(FactorFactory(interleaving="all")) == "factor with interleaving"


# ------------------------------------------------------------
#       Test for all classes
# ------------------------------------------------------------


def test_formal_step(factor_rules, factor_with_int_rules, factor_with_mon_int_rules):
    all_rules = factor_rules + factor_with_int_rules + factor_with_mon_int_rules
    for rule in all_rules:
        assert (
            sum(1 for c in rule.formal_step if c == "/")
            == len(rule.strategy.partition) - 1
        )
        assert sum(1 for c in rule.formal_step if c == "{") == len(
            rule.strategy.partition
        )
        assert sum(1 for c in rule.formal_step if c == "}") == len(
            rule.strategy.partition
        )
        assert all(
            all(str(cell) in rule.formal_step for cell in p)
            for p in rule.strategy.partition
        )
        assert all("factor with partition " in rule.formal_step for rule in all_rules)
        assert " + " not in str(rule)
        assert " x " in str(rule) or " * " in str(rule)


def test_constructor(factor_rules, factor_with_int_rules, factor_with_mon_int_rules):
    assert all(rule.constructor.__class__ == CartesianProduct for rule in factor_rules)
    for rule in chain(factor_with_int_rules, factor_with_mon_int_rules):
        with pytest.raises(NotImplementedError):
            assert isinstance(rule.constructor, Interleaving)


def test_rule(
    factor_rules, factor_with_int_rules, factor_with_mon_int_rules, not_fact_tiling
):
    all_rules = factor_rules + factor_with_int_rules + factor_with_mon_int_rules
    assert all(not rule.inferrable for rule in factor_rules)
    assert all(rule.inferrable for rule in factor_with_mon_int_rules)
    assert all(rule.inferrable for rule in factor_with_int_rules)
    assert all(len(rule.strategy.partition) == len(rule.children) for rule in all_rules)
    assert all(rule.workable for rule in all_rules)
    assert all(not rule.possibly_empty for rule in all_rules)
    assert all(rule.ignore_parent for rule in all_rules)
    assert not list(FactorFactory(interleaving="all")(not_fact_tiling))


def test_all_union_rules():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((2, 2),) * 2),
        ]
    )
    fo = FactorFactory(unions=True)(t)
    f2 = Tiling(obstructions=[GriddedPerm(Perm((0, 1)), ((0, 0),) * 2)])
    # The full factorisation rule is not returned
    assert all(rule(t).children != [f2, f2, f2] for rule in fo)
    # The tiling are marked as not workable by default
    assert all(not rule(t).workable for rule in fo)
    # The workable can be turned on for union of factor
    assert all(rule(t).workable for rule in fo)


def test_interleaving_return_normal_factor():
    """
    In the case where there is no interleaving we make sure that an interleaving factory
    still return a plain cartesian product like factor strategy.
    """
    t = Tiling(
        obstructions=[
            GriddedPerm.single_cell(Perm((0, 1)), (0, 0)),
            GriddedPerm.single_cell(Perm((0, 1)), (1, 1)),
        ]
    )
    factor_strat = next(FactorFactory(interleaving="all")(t))
    assert factor_strat.formal_step() == "factor with partition {(0, 0)} / {(1, 1)}"
    assert factor_strat.__class__ == FactorStrategy
    rule = factor_strat(t)
    assert rule.constructor.__class__ == CartesianProduct

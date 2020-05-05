from permuta import Perm
from tilings import GriddedPerm, Requirement, Tiling
from tilings.strategies import FactorStrategy

pytest_plugins = [
    "tests.fixtures.simple_tiling",
    "tests.fixtures.diverse_tiling",
    "tests.fixtures.no_point_tiling",
]


def test_not_factorable(simple_tiling):
    assert len(list(FactorStrategy()(simple_tiling))) == 0
    assert len(list(FactorStrategy(interleaving="monotone")(simple_tiling))) == 0
    assert len(list(FactorStrategy(interleaving="all")(simple_tiling))) == 0


def test_with_union(diverse_tiling):
    strats = list(FactorStrategy(interleaving="all", union=True)(diverse_tiling))
    assert len(strats) == 14
    assert sum(1 for s in strats if "unions" in s.formal_step) == 13
    assert sum(1 for s in strats if all(s.workable)) == 1
    assert sum(1 for s in strats if not any(s.workable)) == 13


def test_with_union_not_workable(diverse_tiling):
    strats = list(
        FactorStrategy(interleaving="all", union=True, workable=False,)(diverse_tiling)
    )
    assert sum(1 for s in strats if all(s.workable)) == 0
    assert sum(1 for s in strats if not any(s.workable)) == 14


def test_standard_factor(simple_tiling):
    tiling = Tiling(
        obstructions=[GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)])],
        requirements=[
            [
                Requirement(Perm((0, 1)), [(1, 1), (1, 1)]),
                Requirement(Perm((0, 1)), [(1, 1), (1, 2)]),
            ]
        ],
    )
    strats = [s.comb_classes for s in FactorStrategy()(tiling)]
    assert len(strats) == 1
    factors = strats[0]
    assert set(factors) == set(
        [
            Tiling(
                requirements=[
                    [
                        Requirement(Perm((0, 1)), [(0, 0), (0, 0)]),
                        Requirement(Perm((0, 1)), [(0, 0), (0, 1)]),
                    ]
                ]
            ),
            Tiling(obstructions=[GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)])]),
        ]
    )


def test_factor_all_interleaving(diverse_tiling):
    strats = [
        s.comb_classes for s in FactorStrategy(interleaving="all")(diverse_tiling)
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
                requirements=[[Requirement(Perm((0,)), [(2, 0)])]],
            ),
            Tiling(
                obstructions=[
                    GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)]),
                    GriddedPerm(Perm((1, 0)), [(0, 0), (0, 0)]),
                ],
                requirements=[[Requirement(Perm((0,)), [(0, 0)])]],
            ),
            Tiling(
                obstructions=[
                    GriddedPerm(Perm((0, 1)), [(0, 0), (0, 0)]),
                    GriddedPerm(Perm((1, 0)), [(0, 0), (0, 0)]),
                ],
                requirements=[[Requirement(Perm((0,)), [(0, 0)])]],
            ),
            Tiling(
                requirements=[
                    [
                        Requirement(Perm((1, 0)), [(0, 2), (0, 1)]),
                        Requirement(Perm((0, 2, 1)), [(0, 1), (0, 2), (1, 2)]),
                    ]
                ]
            ),
        ]
    )


# ------------------------------------------------------------
#       Test for all classes
# ------------------------------------------------------------


def test_formal_step(factor1, factor1_with_mon_int, factor1_with_int):
    assert factor1.formal_step() == "The factors of the tiling."
    assert (
        factor1_with_int.formal_step() == "The factors with interleaving of the tiling."
    )
    assert (
        factor1_with_mon_int.formal_step()
        == "The factors with monotone interleaving of the tiling."
    )
    assert factor1.formal_step(union=True) == "The unions of factors of the tiling."
    assert (
        factor1_with_int.formal_step(union=True)
        == "The unions of factors with interleaving of the tiling."
    )
    assert (
        factor1_with_mon_int.formal_step(union=True)
        == "The unions of factors with monotone interleaving of the tiling."
    )


def test_constructor(factor1, factor1_with_mon_int, factor1_with_int):
    assert factor1.constructor == "cartesian"
    assert factor1_with_int.constructor == "other"
    assert factor1_with_mon_int.constructor == "other"


def test_rule(factor1, factor1_with_mon_int, factor1_with_int, not_fact_tiling):
    factor_objs = [factor1, factor1_with_mon_int, factor1_with_int]
    assert all(fo.rule().formal_step == fo.formal_step() for fo in factor_objs)
    assert all(not any(fo.rule().inferable) for fo in factor_objs)
    assert all(len(fo.rule().inferable) == len(fo.factors()) for fo in factor_objs)
    assert all(all(fo.rule().workable) for fo in factor_objs)
    assert all(len(fo.rule().inferable) == len(fo.factors()) for fo in factor_objs)
    assert all(not any(fo.rule(workable=False).workable) for fo in factor_objs)
    assert all(
        len(fo.rule(workable=False).workable) == len(fo.factors()) for fo in factor_objs
    )
    assert all(not any(fo.rule().possibly_empty) for fo in factor_objs)
    assert all(len(fo.rule().possibly_empty) == len(fo.factors()) for fo in factor_objs)
    assert all(fo.rule().ignore_parent for fo in factor_objs)
    assert not any(fo.rule(workable=False).ignore_parent for fo in factor_objs)
    assert all(fo.rule().constructor == fo.constructor for fo in factor_objs)

    assert Factor(not_fact_tiling).rule() is None


def test_all_union_rules():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            GriddedPerm(Perm((0, 1)), ((2, 2),) * 2),
        ]
    )
    fo = Factor(t)
    f2 = Tiling(obstructions=[GriddedPerm(Perm((0, 1)), ((0, 0),) * 2)])
    assert all("unions" in rule.formal_step for rule in fo.all_union_rules())
    # The full factorisation rule is not returned
    assert all(rule.comb_classes != [f2, f2, f2] for rule in fo.all_union_rules())
    # The tiling are marked as not workable by default
    assert all(rule.workable == [False, False] for rule in fo.all_union_rules())
    # The workable can be turned on for union of factor
    assert all(
        rule.workable == [True, True] for rule in fo.all_union_rules(workable=True)
    )

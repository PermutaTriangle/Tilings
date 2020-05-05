import pytest

from permuta import Perm
from tilings import Obstruction, Requirement, Tiling
from tilings.strategies import (
    ObstructionTransitivityStrategy,
    RowColumnSeparationStrategy,
)

pytest_plugins = ["tests.fixtures.simple_trans"]


# Obstruction transitivity test
def test_obstruction_transitivity(
    simple_trans_row, simple_trans_col, simple_trans_row_len2, simple_trans_row_len3
):
    strat = ObstructionTransitivityStrategy()(simple_trans_row)
    assert strat.comb_classes[0] == Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
            Obstruction(Perm((0, 1)), [(0, 0), (2, 0)]),
        ],
        requirements=[[Requirement(Perm((0,)), [(1, 0)])]],
    )

    strat = ObstructionTransitivityStrategy()(simple_trans_col)
    assert strat.comb_classes[0] == Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (0, 1)]),
            Obstruction(Perm((0, 1)), [(0, 1), (0, 2)]),
            Obstruction(Perm((0, 1)), [(0, 0), (0, 2)]),
        ],
        requirements=[[Requirement(Perm((0,)), [(0, 1)])]],
    )

    strat = ObstructionTransitivityStrategy()(simple_trans_row_len2)
    assert strat.comb_classes[0] == Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
            Obstruction(Perm((0, 1)), [(0, 0), (2, 0)]),
            Obstruction(Perm((0, 1)), [(0, 0), (3, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (3, 0)]),
            Obstruction(Perm((0, 1)), [(2, 0), (3, 0)]),
        ],
        requirements=[
            [Requirement(Perm((0,)), [(1, 0)])],
            [Requirement(Perm((0,)), [(2, 0)])],
        ],
    )

    strat = ObstructionTransitivityStrategy()(simple_trans_row_len3)
    assert strat.comb_classes[0] == Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
            Obstruction(Perm((0, 1)), [(0, 0), (2, 0)]),
            Obstruction(Perm((0, 1)), [(0, 0), (3, 0)]),
            Obstruction(Perm((0, 1)), [(0, 0), (4, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (3, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (4, 0)]),
            Obstruction(Perm((0, 1)), [(2, 0), (3, 0)]),
            Obstruction(Perm((0, 1)), [(2, 0), (4, 0)]),
            Obstruction(Perm((0, 1)), [(3, 0), (4, 0)]),
        ],
        requirements=[
            [Requirement(Perm((0,)), [(1, 0)])],
            [Requirement(Perm((0,)), [(2, 0)])],
            [Requirement(Perm((0,)), [(3, 0)])],
        ],
    )


def test_rule(simple_trans_col, no_trans_col):
    assert no_trans_col.rule() is None
    rule = simple_trans_col.rule()
    assert rule.formal_step == "Computing transitivity of inequalities."
    assert rule.comb_classes == [simple_trans_col.obstruction_transitivity()]
    assert rule.inferable == [True]
    assert rule.possibly_empty == [False]
    assert rule.workable == [True]
    assert rule.ignore_parent is True
    assert rule.constructor == "equiv"


def test_rule(obs_inf1, obs_not_inf):
    rule = obs_inf1.rule()
    assert isinstance(rule, Rule)
    assert rule.comb_classes == [obs_inf1.obstruction_inferral()]
    assert rule.ignore_parent
    assert rule.workable == [True]
    assert rule.constructor == "equiv"
    assert rule.possibly_empty == [False]
    assert obs_not_inf.rule() is None

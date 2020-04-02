import pytest

from comb_spec_searcher import Rule
from permuta import Perm
from tilings import Obstruction, Tiling
from tilings.strategies import ComponentFusionStrategy, FusionStrategy


@pytest.fixture
def tiling1():
    t = Tiling(
        obstructions=[
            Obstruction(Perm((1, 0)), ((0, 1), (1, 1))),
            Obstruction(Perm((1, 0)), ((0, 1), (0, 1))),
            Obstruction(Perm((1, 0)), ((0, 1), (1, 0))),
            Obstruction(Perm((1, 0)), ((0, 1), (0, 0))),
            Obstruction(Perm((1, 0)), ((0, 0), (0, 0))),
            Obstruction(Perm((1, 0)), ((0, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 1), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 1), (1, 1))),
        ]
    )
    return t


@pytest.fixture
def tiling2():
    t = Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
            Obstruction(Perm((0, 2, 1)), ((0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((0, 2, 1)), ((1, 0), (1, 0), (1, 0))),
            Obstruction(Perm((0, 2, 1, 3)), ((0, 0), (0, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 2, 1, 3)), ((0, 0), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 2, 1, 3)), ((1, 0), (1, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 2, 1, 3)), ((1, 0), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 2, 1, 3)), ((2, 0), (2, 0), (2, 0), (2, 0))),
        ]
    )
    return t


def test_component_fusion(tiling1, tiling2):
    assert len(list(ComponentFusionStrategy()(tiling1))) == 0
    assert len(list(ComponentFusionStrategy()(tiling2))) == 1


@pytest.fixture
def small_tiling():
    t = Tiling(
        obstructions=[
            Obstruction(Perm((1, 0)), ((0, 1), (1, 1))),
            Obstruction(Perm((1, 0)), ((0, 1), (0, 1))),
            Obstruction(Perm((1, 0)), ((0, 1), (1, 0))),
            Obstruction(Perm((1, 0)), ((0, 1), (0, 0))),
            Obstruction(Perm((1, 0)), ((0, 0), (0, 0))),
            Obstruction(Perm((1, 0)), ((0, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 1), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 1), (1, 1))),
        ]
    )
    return t


@pytest.fixture
def big_tiling():
    """ The original tiling from Jay's idea """
    t = Tiling(
        obstructions=(
            Obstruction(Perm((0,)), ((0, 1),)),
            Obstruction(Perm((0,)), ((0, 2),)),
            Obstruction(Perm((0,)), ((0, 3),)),
            Obstruction(Perm((0,)), ((1, 2),)),
            Obstruction(Perm((0,)), ((1, 3),)),
            Obstruction(Perm((1, 0)), ((0, 0), (0, 0))),
            Obstruction(Perm((1, 0)), ((0, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((0, 0), (2, 0))),
            Obstruction(Perm((1, 0)), ((1, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 0), (2, 0))),
            Obstruction(Perm((1, 0)), ((1, 1), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 1), (1, 1))),
            Obstruction(Perm((1, 0)), ((1, 1), (2, 0))),
            Obstruction(Perm((1, 0)), ((1, 1), (2, 1))),
            Obstruction(Perm((1, 0)), ((2, 0), (2, 0))),
            Obstruction(Perm((1, 0)), ((2, 1), (2, 0))),
            Obstruction(Perm((1, 0)), ((2, 1), (2, 1))),
            Obstruction(Perm((1, 0)), ((2, 2), (2, 0))),
            Obstruction(Perm((1, 0)), ((2, 2), (2, 1))),
            Obstruction(Perm((1, 0)), ((2, 2), (2, 2))),
            Obstruction(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 1))),
            Obstruction(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 2))),
            Obstruction(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 3))),
        ),
        requirements=(),
    )
    return t


def test_fusion(small_tiling, big_tiling):
    assert len(list(FusionStrategy()(big_tiling))) == 0
    small_tiling_rules = list(FusionStrategy()(small_tiling))
    assert len(small_tiling_rules) == 2
    assert all(isinstance(rule, Rule) for rule in small_tiling_rules)
    assert all(rule.constructor == "other" for rule in small_tiling_rules)
    t = Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
            Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
            Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
        ]
    )
    t_rules = list(FusionStrategy()(t))
    assert len(t_rules) == 1

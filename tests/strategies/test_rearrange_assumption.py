import pytest

from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.strategies.rearrange_assumption import RearrangeAssumptionStrategy


@pytest.fixture
def rule1():
    ass1 = TrackingAssumption([GriddedPerm((0,), ((0, 0),))])
    ass2 = TrackingAssumption(
        [GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))]
    )
    strat = RearrangeAssumptionStrategy(ass2, ass1)
    t1 = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0),) * 2),
            GriddedPerm((0, 1), ((1, 0),) * 2),
        ],
        assumptions=[ass1, ass2],
    )
    return strat(t1)


@pytest.fixture
def rule2():
    ass1 = TrackingAssumption([GriddedPerm((0,), ((0, 0),))])
    ass2 = TrackingAssumption(
        [GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))]
    )
    ass3 = TrackingAssumption([GriddedPerm((0,), ((1, 0),))])
    strat = RearrangeAssumptionStrategy(ass2, ass1)
    t1 = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0),) * 2),
            GriddedPerm((0, 1), ((1, 0),) * 2),
        ],
        assumptions=[ass1, ass2],
    )
    t2 = t1.add_assumption(ass3)
    return strat(t2)


def test_extra_param(rule1, rule2):
    print(rule2)
    assert rule1.strategy.extra_parameters(rule1.comb_class) == ({"k_0": "k_0"},)
    assert rule2.strategy.extra_parameters(rule2.comb_class) == (
        {"k_0": "k_0", "k_2": "k_1"},
    )


def test_param_map1(rule1):
    print(rule1)
    constructor = rule1.constructor
    pmap = constructor.param_map
    assert pmap((0, 0)) == (0, 0)
    assert pmap((0, 1)) == (0, 1)
    assert pmap((1, 0)) == (1, 1)
    assert pmap((1, 1)) == (1, 2)


def test_param_map2(rule2):
    print(rule2)
    constructor = rule2.constructor
    pmap = constructor.param_map
    assert pmap((0, 0)) == (0, 0, 0)
    assert pmap((0, 1)) == (0, 1, 1)
    assert pmap((1, 0)) == (1, 1, 0)
    assert pmap((1, 1)) == (1, 2, 1)


def test_rearrange1(rule1):
    print(rule1)
    for i in range(5):
        rule1.sanity_check(i)


def test_rearrange2(rule2):
    print(rule2)
    for i in range(5):
        rule2.sanity_check(i)

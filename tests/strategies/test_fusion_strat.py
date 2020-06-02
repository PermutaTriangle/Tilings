import pytest

from comb_spec_searcher.strategies import Rule
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Fusion
from tilings.strategies import ComponentFusionFactory, FusionFactory
from tilings.strategies.fusion import (
    ComponentFusionConstructor,
    ComponentFusionStrategy,
    FusionConstructor,
    FusionStrategy,
)


@pytest.fixture
def tiling1():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((1, 0)), ((0, 1), (1, 1))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (0, 1))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (0, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (1, 1))),
        ]
    )
    return t


@pytest.fixture
def tiling2():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((0, 2, 1)), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm(Perm((0, 2, 1)), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm(Perm((0, 2, 1, 3)), ((0, 0), (0, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((0, 2, 1, 3)), ((0, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((0, 2, 1, 3)), ((1, 0), (1, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((0, 2, 1, 3)), ((1, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm(Perm((0, 2, 1, 3)), ((2, 0), (2, 0), (2, 0), (2, 0))),
        ]
    )
    return t


def test_component_fusion(tiling1, tiling2):
    assert len(list(ComponentFusionFactory()(tiling1))) == 0
    assert len(list(ComponentFusionFactory()(tiling2))) == 1


@pytest.fixture
def small_tiling():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((1, 0)), ((0, 1), (1, 1))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (0, 1))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 1), (0, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (1, 1))),
        ]
    )
    return t


@pytest.fixture
def big_tiling():
    """ The original tiling from Jay's idea """
    t = Tiling(
        obstructions=(
            GriddedPerm(Perm((0,)), ((0, 1),)),
            GriddedPerm(Perm((0,)), ((0, 2),)),
            GriddedPerm(Perm((0,)), ((0, 3),)),
            GriddedPerm(Perm((0,)), ((1, 2),)),
            GriddedPerm(Perm((0,)), ((1, 3),)),
            GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((0, 0), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 0), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (1, 1))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (2, 1))),
            GriddedPerm(Perm((1, 0)), ((2, 0), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((2, 1), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((2, 1), (2, 1))),
            GriddedPerm(Perm((1, 0)), ((2, 2), (2, 0))),
            GriddedPerm(Perm((1, 0)), ((2, 2), (2, 1))),
            GriddedPerm(Perm((1, 0)), ((2, 2), (2, 2))),
            GriddedPerm(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 0))),
            GriddedPerm(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 1))),
            GriddedPerm(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 2))),
            GriddedPerm(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 3))),
        ),
        requirements=(),
    )
    return t


def test_fusion(small_tiling, big_tiling):
    assert len(list(FusionFactory()(big_tiling))) == 0
    small_tiling_rules = list(FusionFactory()(small_tiling))
    assert len(small_tiling_rules) == 2
    assert all(isinstance(rule, Rule) for rule in small_tiling_rules)
    assert all(
        isinstance(rule.constructor, FusionConstructor) for rule in small_tiling_rules
    )
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
        ]
    )
    t_rules = list(FusionFactory()(t))
    assert len(t_rules) == 1


@pytest.fixture
def row_fusion(small_tiling):
    return FusionStrategy(row_idx=0)(small_tiling)


@pytest.fixture
def col_fusion(small_tiling):
    return FusionStrategy(col_idx=0)(small_tiling)


def test_formal_step_fusion(row_fusion, col_fusion):
    assert row_fusion.formal_step == "fuse rows 0 and 1"
    assert col_fusion.formal_step == "fuse columns 0 and 1"


def test_rule(row_fusion):
    assert row_fusion.formal_step == "fuse rows 0 and 1"
    assert list(row_fusion.children) == [
        Fusion(row_fusion.comb_class, row_idx=0).fused_tiling()
    ]
    assert row_fusion.inferrable
    assert row_fusion.workable
    assert not row_fusion.possibly_empty
    assert isinstance(row_fusion.constructor, FusionConstructor)


@pytest.fixture
def row_tiling():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
            GriddedPerm(Perm((0, 1, 2)), ((0, 2),) * 3),
            GriddedPerm(Perm((0, 1)), ((1, 2),) * 2),
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 1), (0, 2))),
            GriddedPerm(Perm((2, 0, 1)), ((0, 2), (0, 0), (1, 2))),
            GriddedPerm(Perm((2, 0, 1)), ((0, 2), (0, 1), (1, 2))),
        ]
    )
    return t


@pytest.fixture
def col_tiling():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 2, 1)), ((0, 0),) * 3),
            GriddedPerm(Perm((0, 2, 1)), ((1, 0),) * 3),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
        ]
    )
    return t


@pytest.fixture
def component_row_fusion(row_tiling):
    return ComponentFusionStrategy(row_idx=0)(row_tiling)


@pytest.fixture
def component_col_fusion(col_tiling):
    return ComponentFusionStrategy(col_idx=0)(col_tiling)


def test_formal_step_component(component_col_fusion, component_row_fusion):
    assert component_col_fusion.formal_step == "component fuse columns 0 and 1"
    assert component_row_fusion.formal_step == "component fuse rows 0 and 1"
    assert len(component_col_fusion.children) == 1
    assert len(component_row_fusion.children) == 1
    assert component_row_fusion.inferrable
    assert component_row_fusion.workable
    assert not component_row_fusion.possibly_empty
    assert isinstance(component_row_fusion.constructor, ComponentFusionConstructor)
    assert component_col_fusion.inferrable
    assert component_col_fusion.workable
    assert not component_col_fusion.possibly_empty
    assert isinstance(component_col_fusion.constructor, ComponentFusionConstructor)

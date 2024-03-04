import pytest

from comb_spec_searcher import DisjointUnion
from comb_spec_searcher.exception import StrategyDoesNotApply
from tilings import GriddedPerm, Tiling
from tilings.strategies import (
    ObstructionInferralFactory,
    ObstructionTransitivityFactory,
    RowColumnSeparationStrategy,
)

pytest_plugins = ["tests.fixtures.simple_trans"]


@pytest.fixture
def tiling1():
    """
    A tiling that can be inferred.
    """
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
        ],
        requirements=[[GriddedPerm((1, 0), ((1, 0), (1, 0)))]],
    )
    return t


@pytest.fixture
def tiling_not_inf():
    """
    A tiling that cannot be inferred.
    """
    return Tiling.from_string("1234_2341")


# Obstruction transitivity test
def test_obstruction_transitivity(
    simple_trans_row, simple_trans_col, simple_trans_row_len2, simple_trans_row_len3
):
    strat = list(ObstructionTransitivityFactory()(simple_trans_row))
    assert len(strat) == 1
    rule = strat[0](simple_trans_row)
    assert len(rule.children) == 1
    assert rule.children[0] == Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((0, 1), [(1, 0), (2, 0)]),
            GriddedPerm((0, 1), [(0, 0), (2, 0)]),
        ],
        requirements=[[GriddedPerm((0,), [(1, 0)])]],
    )
    assert isinstance(rule.constructor, DisjointUnion)
    assert rule.formal_step == "added the obstructions {01: (0, 0), (2, 0)}"
    assert rule.inferrable
    assert not rule.possibly_empty
    assert rule.ignore_parent
    assert rule.workable

    strat = list(ObstructionTransitivityFactory()(simple_trans_col))
    assert len(strat) == 1
    rule = strat[0](simple_trans_col)
    assert len(rule.children) == 1
    assert rule.children[0] == Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (0, 1)]),
            GriddedPerm((0, 1), [(0, 1), (0, 2)]),
            GriddedPerm((0, 1), [(0, 0), (0, 2)]),
        ],
        requirements=[[GriddedPerm((0,), [(0, 1)])]],
    )
    assert isinstance(rule.constructor, DisjointUnion)
    assert rule.formal_step == "added the obstructions {01: (0, 0), (0, 2)}"
    assert rule.inferrable
    assert not rule.possibly_empty
    assert rule.ignore_parent
    assert rule.workable

    strat = list(ObstructionTransitivityFactory()(simple_trans_row_len2))
    assert len(strat) == 1
    rule = strat[0](simple_trans_row_len2)
    assert len(rule.children) == 1
    assert rule.children[0] == Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((0, 1), [(0, 0), (2, 0)]),
            GriddedPerm((0, 1), [(0, 0), (3, 0)]),
            GriddedPerm((0, 1), [(1, 0), (2, 0)]),
            GriddedPerm((0, 1), [(1, 0), (3, 0)]),
            GriddedPerm((0, 1), [(2, 0), (3, 0)]),
        ],
        requirements=[
            [GriddedPerm((0,), [(1, 0)])],
            [GriddedPerm((0,), [(2, 0)])],
        ],
    )
    assert isinstance(rule.constructor, DisjointUnion)
    assert (
        rule.formal_step
        == "added the obstructions {01: (0, 0), (2, 0), 01: (0, 0), (3, 0), "
        "01: (1, 0), (3, 0)}"
    )
    assert rule.inferrable
    assert not rule.possibly_empty
    assert rule.ignore_parent
    assert rule.workable

    strat = list(ObstructionTransitivityFactory()(simple_trans_row_len3))
    assert len(strat) == 1
    rule = strat[0](simple_trans_row_len3)
    assert len(rule.children) == 1
    assert rule.children[0] == Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((0, 1), [(0, 0), (2, 0)]),
            GriddedPerm((0, 1), [(0, 0), (3, 0)]),
            GriddedPerm((0, 1), [(0, 0), (4, 0)]),
            GriddedPerm((0, 1), [(1, 0), (2, 0)]),
            GriddedPerm((0, 1), [(1, 0), (3, 0)]),
            GriddedPerm((0, 1), [(1, 0), (4, 0)]),
            GriddedPerm((0, 1), [(2, 0), (3, 0)]),
            GriddedPerm((0, 1), [(2, 0), (4, 0)]),
            GriddedPerm((0, 1), [(3, 0), (4, 0)]),
        ],
        requirements=[
            [GriddedPerm((0,), [(1, 0)])],
            [GriddedPerm((0,), [(2, 0)])],
            [GriddedPerm((0,), [(3, 0)])],
        ],
    )
    assert isinstance(rule.constructor, DisjointUnion)
    assert (
        rule.formal_step == "added the obstructions {01: (0, 0), (2, 0), "
        "01: (0, 0), (3, 0), 01: (0, 0), (4, 0), 01: (1, 0), (3, 0), "
        "01: (1, 0), (4, 0), 01: (2, 0), (4, 0)}"
    )
    assert rule.inferrable
    assert not rule.possibly_empty
    assert rule.ignore_parent
    assert rule.workable


def test_obstruction_inferral(tiling1, tiling_not_inf):
    strat = list(ObstructionInferralFactory(maxlen=4)(tiling1))
    assert len(strat) == 1
    rule = strat[0](tiling1)
    assert len(rule.children) == 1
    assert rule.children[0] == Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((0, 0), (0, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
        ),
        requirements=((GriddedPerm((1, 0), ((1, 0), (1, 0))),),),
    )
    assert isinstance(rule.constructor, DisjointUnion)
    assert (
        rule.formal_step == "added the obstructions {01: (0, 0), (0, 0),"
        " 021: (0, 0), (0, 0), (1, 0), 120: (0, 0), (0, 0), (1, 0)}"
    )
    assert rule.inferrable
    assert not rule.possibly_empty
    assert rule.ignore_parent
    assert rule.workable

    strat = list(ObstructionInferralFactory(maxlen=4)(tiling_not_inf))
    assert len(strat) == 0


def test_row_col_sep(tiling1):
    with pytest.raises(StrategyDoesNotApply):
        print(RowColumnSeparationStrategy()(tiling1))
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
        ]
    )
    rule = RowColumnSeparationStrategy()(t)
    assert rule is not None
    print(rule)
    assert len(rule.children) == 1
    assert isinstance(rule.constructor, DisjointUnion)
    assert rule.formal_step == "row and column separation"
    assert rule.inferrable
    assert not rule.possibly_empty
    assert rule.ignore_parent
    assert rule.workable
    assert rule.children[0] == Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 1), (0, 1))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
        ]
    )

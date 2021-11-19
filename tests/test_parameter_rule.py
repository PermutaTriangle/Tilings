import pytest

from comb_spec_searcher.exception import StrategyDoesNotApply
from tilings import GriddedPerm, Tiling
from tilings.map import RowColMap
from tilings.parameter_counter import ParameterCounter, PreimageCounter
from tilings.strategies.fusion import FusionFactory, FusionStrategy
from tilings.strategies.parameter_strategies import RemoveReqFactory


def test_counting_fusion_rule():
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
        ),
        requirements=(),
        parameters=(
            ParameterCounter(
                (
                    PreimageCounter(
                        Tiling(
                            obstructions=(
                                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                                GriddedPerm((0, 1), ((0, 0), (1, 0))),
                                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                                GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                                GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                            ),
                            requirements=(),
                            parameters=(),
                        ),
                        RowColMap({0: 0}, {0: 0, 1: 1, 2: 1}),
                    ),
                )
            ),
        ),
    )
    strategy = FusionStrategy(col_idx=0, tracked=True)
    rule = strategy(t)
    for n in range(5):
        rule._sanity_check_count(n)


def test_fusion():
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
        ),
        requirements=(),
        parameters=(
            ParameterCounter(
                (
                    PreimageCounter(
                        Tiling(
                            obstructions=(
                                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                                GriddedPerm((0, 1), ((0, 0), (1, 0))),
                                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                                GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                                GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                            ),
                            requirements=(),
                            parameters=(),
                        ),
                        RowColMap({0: 0}, {0: 0, 1: 0, 2: 1}),
                    ),
                    PreimageCounter(
                        Tiling(
                            obstructions=(
                                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                            ),
                            requirements=(),
                            parameters=(),
                        ),
                        RowColMap({0: 0}, {0: 1, 1: 1}),
                    ),
                )
            ),
        ),
    )
    strategy = FusionStrategy(col_idx=0, tracked=True)
    with pytest.raises(StrategyDoesNotApply):
        strategy(t)


def test_positive_fusion():
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 1))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 1))),
        ),
        requirements=((GriddedPerm((0,), ((0, 0),)),),),
        parameters=(),
    )
    strategy = FusionStrategy(row_idx=0, tracked=True)
    rule = strategy(t)
    for n in range(5):
        rule._sanity_check_count(n)


def test_col_fuse_with_empty():
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 1))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 1))),
        ),
        requirements=((GriddedPerm((0,), ((0, 0),)),),),
        parameters=(),
    )
    strategy = FusionStrategy(col_idx=1, tracked=True)
    with pytest.raises(StrategyDoesNotApply):
        strategy(t)

    factory = FusionFactory()
    assert sum(1 for _ in factory(t)) == 1


def test_remove_req_identity():
    """
    Make sure that the remove req factory only return rule were there's actually an
    identity to remove.
    """
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 1), (0, 1))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 1), (2, 1), (2, 1))),
            GriddedPerm((0, 1, 2), ((1, 0), (2, 1), (2, 1))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 1), (2, 1))),
            GriddedPerm((0, 1, 2), ((2, 1), (2, 1), (2, 1))),
        ),
        requirements=(),
        parameters=(
            ParameterCounter(
                (
                    PreimageCounter(
                        Tiling(
                            obstructions=(
                                GriddedPerm((0, 1), ((0, 2), (0, 2))),
                                GriddedPerm((0, 1), ((1, 1), (1, 1))),
                                GriddedPerm((0, 1), ((2, 0), (2, 0))),
                                GriddedPerm((0, 1), ((2, 2), (2, 2))),
                            ),
                            requirements=((GriddedPerm((0,), ((1, 1),)),),),
                            parameters=(),
                        ),
                        RowColMap({0: 0, 1: 0, 2: 1}, {0: 0, 1: 1, 2: 2}),
                    ),
                    PreimageCounter(
                        Tiling(
                            obstructions=(
                                GriddedPerm((0, 1), ((0, 1), (0, 1))),
                                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                                GriddedPerm((0, 1, 2), ((0, 1), (1, 1), (1, 1))),
                                GriddedPerm((0, 1, 2), ((1, 0), (1, 1), (1, 1))),
                                GriddedPerm((0, 1, 2), ((1, 1), (1, 1), (1, 1))),
                            ),
                            requirements=(),
                            parameters=(),
                        ),
                        RowColMap({0: 0, 1: 1}, {0: 0, 1: 2}),
                    ),
                )
            ),
        ),
    )
    with pytest.raises(StopIteration):
        next(RemoveReqFactory()(t))

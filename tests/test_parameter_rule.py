import pytest

from tilings import GriddedPerm, Tiling
from tilings.map import RowColMap
from tilings.parameter_counter import ParameterCounter, PreimageCounter
from tilings.strategies.fusion import FusionStrategy
from comb_spec_searcher.exception import StrategyDoesNotApply


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

import itertools
import pickle

import pytest

from comb_spec_searcher.strategies.rule import EquivalencePathRule
from tilings import GriddedPerm, Tiling
from tilings.map import RowColMap
from tilings.parameter_counter import ParameterCounter, PreimageCounter
from tilings.strategies.factor import FactorStrategy
from tilings.strategies.obstruction_inferral import ObstructionInferralStrategy
from tilings.strategies.requirement_insertion import RequirementInsertionStrategy
from tilings.strategies.requirement_placement import RequirementPlacementStrategy

rules_to_check = [
    RequirementInsertionStrategy(
        gps=frozenset({GriddedPerm((0,), ((0, 0),))}), ignore_parent=True
    )(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((0, 0), (1, 0))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((1, 0), ((0, 0), (1, 0))),
                GriddedPerm((1, 0), ((1, 0), (1, 0))),
            ),
            requirements=((GriddedPerm((0,), ((1, 0),)),),),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                                    GriddedPerm((0, 1), ((0, 0), (1, 0))),
                                    GriddedPerm((0, 1), ((0, 0), (2, 0))),
                                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                                    GriddedPerm((0, 1), ((1, 0), (2, 0))),
                                    GriddedPerm((0, 1), ((2, 0), (2, 0))),
                                    GriddedPerm((1, 0), ((0, 0), (1, 0))),
                                    GriddedPerm((1, 0), ((0, 0), (2, 0))),
                                    GriddedPerm((1, 0), ((1, 0), (1, 0))),
                                    GriddedPerm((1, 0), ((1, 0), (2, 0))),
                                    GriddedPerm((1, 0), ((2, 0), (2, 0))),
                                ),
                                requirements=(
                                    (
                                        GriddedPerm((0,), ((1, 0),)),
                                        GriddedPerm((0,), ((2, 0),)),
                                    ),
                                ),
                                parameters=(),
                            ),
                            RowColMap({0: 0}, {0: 0, 1: 1, 2: 1}),
                        ),
                    )
                ),
            ),
        )
    ),
    RequirementInsertionStrategy(
        gps=frozenset({GriddedPerm((0,), ((2, 0),))}), ignore_parent=True
    )(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1), ((2, 0), (2, 0))),
                GriddedPerm((0, 1), ((2, 0), (3, 0))),
                GriddedPerm((0, 1), ((3, 0), (3, 0))),
                GriddedPerm((1, 0), ((0, 0), (2, 0))),
                GriddedPerm((1, 0), ((0, 0), (3, 0))),
                GriddedPerm((1, 0), ((2, 0), (2, 0))),
                GriddedPerm((1, 0), ((2, 0), (3, 0))),
                GriddedPerm((1, 0), ((3, 0), (3, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (3, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),
            ),
            requirements=(
                (GriddedPerm((0,), ((0, 0),)),),
                (GriddedPerm((0,), ((3, 0),)),),
            ),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                                    GriddedPerm((0, 1), ((2, 0), (2, 0))),
                                    GriddedPerm((0, 1), ((2, 0), (3, 0))),
                                    GriddedPerm((0, 1), ((2, 0), (4, 0))),
                                    GriddedPerm((0, 1), ((3, 0), (3, 0))),
                                    GriddedPerm((0, 1), ((3, 0), (4, 0))),
                                    GriddedPerm((0, 1), ((4, 0), (4, 0))),
                                    GriddedPerm((1, 0), ((0, 0), (2, 0))),
                                    GriddedPerm((1, 0), ((0, 0), (3, 0))),
                                    GriddedPerm((1, 0), ((0, 0), (4, 0))),
                                    GriddedPerm((1, 0), ((2, 0), (2, 0))),
                                    GriddedPerm((1, 0), ((2, 0), (3, 0))),
                                    GriddedPerm((1, 0), ((2, 0), (4, 0))),
                                    GriddedPerm((1, 0), ((3, 0), (3, 0))),
                                    GriddedPerm((1, 0), ((3, 0), (4, 0))),
                                    GriddedPerm((1, 0), ((4, 0), (4, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (3, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (4, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (3, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (4, 0))),
                                    GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
                                    GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),
                                ),
                                requirements=(
                                    (GriddedPerm((0,), ((0, 0),)),),
                                    (
                                        GriddedPerm((0,), ((3, 0),)),
                                        GriddedPerm((0,), ((4, 0),)),
                                    ),
                                ),
                                parameters=(),
                            ),
                            RowColMap({0: 0}, {0: 0, 1: 1, 2: 2, 3: 3, 4: 3}),
                        ),
                    )
                ),
            ),
        )
    ),
    # FusionStrategy(col_idx=1, tracked=True)(
    #     Tiling(
    #         obstructions=(
    #             GriddedPerm((0,), ((0, 0),)),
    #             GriddedPerm((0,), ((1, 0),)),
    #             GriddedPerm((0,), ((1, 1),)),
    #             GriddedPerm((0,), ((2, 0),)),
    #             GriddedPerm((0,), ((2, 1),)),
    #             GriddedPerm((0,), ((3, 1),)),
    #             GriddedPerm((0,), ((3, 2),)),
    #             GriddedPerm((0, 1), ((1, 2), (1, 2))),
    #             GriddedPerm((0, 1), ((1, 2), (2, 2))),
    #             GriddedPerm((0, 1), ((2, 2), (2, 2))),
    #             GriddedPerm((0, 1), ((3, 0), (3, 0))),
    #             GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 2))),
    #             GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (0, 2))),
    #             GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (1, 2))),
    #             GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (2, 2))),
    #             GriddedPerm((0, 2, 1), ((0, 1), (0, 1), (0, 1))),
    #             GriddedPerm((0, 2, 1), ((0, 1), (1, 2), (1, 2))),
    #             GriddedPerm((0, 2, 1), ((0, 1), (1, 2), (2, 2))),
    #             GriddedPerm((0, 2, 1), ((0, 1), (2, 2), (2, 2))),
    #             GriddedPerm((1, 0, 2), ((0, 2), (0, 1), (1, 2))),
    #             GriddedPerm((1, 0, 2), ((0, 2), (0, 1), (2, 2))),
    #             GriddedPerm((2, 0, 1), ((0, 1), (0, 1), (0, 1))),
    #             GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
    #             GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (0, 2), (1, 2))),
    #             GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (0, 2), (2, 2))),
    #             GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (1, 2), (1, 2))),
    #             GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (1, 2), (2, 2))),
    #             GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (2, 2), (2, 2))),
    #             GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 2), (0, 2), (0, 2))),
    #             GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 2), (0, 2), (1, 2))),
    #             GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 2), (0, 2), (2, 2))),
    #             GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
    #             GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (0, 2), (1, 2))),
    #             GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (0, 2), (2, 2))),
    #             GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (1, 2), (1, 2))),
    #             GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (1, 2), (2, 2))),
    #             GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (2, 2), (2, 2))),
    #             GriddedPerm((2, 0, 1, 3), ((0, 2), (0, 2), (0, 2), (0, 2))),
    #             GriddedPerm((2, 0, 1, 3), ((0, 2), (0, 2), (0, 2), (1, 2))),
    #             GriddedPerm((2, 0, 1, 3), ((0, 2), (0, 2), (0, 2), (2, 2))),
    #         ),
    #         requirements=(
    #             (GriddedPerm((0,), ((1, 2),)),),
    #             (GriddedPerm((0,), ((2, 2),)),),
    #             (GriddedPerm((0,), ((3, 0),)),),
    #         ),
    #         assumptions=(
    #             TrackingAssumption(
    #                 (
    #                     GriddedPerm((0,), ((2, 2),)),
    #                     GriddedPerm((0,), ((3, 0),)),
    #                 )
    #             ),
    #         ),
    #     )
    # ),
    RequirementInsertionStrategy(
        gps=frozenset({GriddedPerm((0,), ((0, 2),))}), ignore_parent=True
    )(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 1), (0, 1))),
                GriddedPerm((0, 1), ((0, 1), (0, 2))),
                GriddedPerm((0, 1), ((0, 2), (0, 2))),
                GriddedPerm((1, 0), ((0, 1), (0, 0))),
                GriddedPerm((1, 0), ((0, 1), (0, 1))),
                GriddedPerm((1, 0), ((0, 2), (0, 0))),
                GriddedPerm((1, 0), ((0, 2), (0, 1))),
                GriddedPerm((1, 0), ((0, 2), (0, 2))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 1))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 2))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
            ),
            requirements=((GriddedPerm((0,), ((0, 1),)),),),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                                    GriddedPerm((0, 1), ((0, 1), (0, 2))),
                                    GriddedPerm((0, 1), ((0, 1), (0, 3))),
                                    GriddedPerm((0, 1), ((0, 2), (0, 2))),
                                    GriddedPerm((0, 1), ((0, 2), (0, 3))),
                                    GriddedPerm((0, 1), ((0, 3), (0, 3))),
                                    GriddedPerm((1, 0), ((0, 1), (0, 0))),
                                    GriddedPerm((1, 0), ((0, 1), (0, 1))),
                                    GriddedPerm((1, 0), ((0, 2), (0, 0))),
                                    GriddedPerm((1, 0), ((0, 2), (0, 1))),
                                    GriddedPerm((1, 0), ((0, 2), (0, 2))),
                                    GriddedPerm((1, 0), ((0, 3), (0, 0))),
                                    GriddedPerm((1, 0), ((0, 3), (0, 1))),
                                    GriddedPerm((1, 0), ((0, 3), (0, 2))),
                                    GriddedPerm((1, 0), ((0, 3), (0, 3))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 1))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 2))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 3))),
                                    GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                                    GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
                                ),
                                requirements=(
                                    (
                                        GriddedPerm((0,), ((0, 1),)),
                                        GriddedPerm((0,), ((0, 2),)),
                                    ),
                                ),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 1, 2: 1, 3: 2}, {0: 0}),
                        ),
                    )
                ),
            ),
        )
    ),
    FactorStrategy([[(0, 0)], [(1, 1)]])(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
            ),
        )
    ),
    FactorStrategy([[(0, 0)], [(1, 1)], [(2, 2)]])(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
                GriddedPerm((0, 1), ((2, 2), (2, 2))),
                GriddedPerm((1, 0), ((2, 2), (2, 2))),
            ),
            requirements=(
                (GriddedPerm((0,), ((0, 0),)),),
                (GriddedPerm((0,), ((2, 2),)),),
            ),
        )
    ),
    FactorStrategy([[(0, 0)], [(1, 1)]])(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
            ),
            requirements=(),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                                    GriddedPerm((0, 1), ((0, 0), (0, 1))),
                                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                                    GriddedPerm((1, 0), ((1, 2), (1, 2))),
                                ),
                                requirements=(),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 0, 2: 1}, {0: 0, 1: 1}),
                        ),
                    )
                ),
            ),
        )
    ),
    FactorStrategy([[(0, 0)], [(1, 1)]])(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
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
                                    GriddedPerm((1, 0), ((2, 1), (2, 1))),
                                ),
                                requirements=(),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 1}, {0: 0, 1: 0, 2: 1}),
                        ),
                    )
                ),
            ),
        )
    ),
    FactorStrategy([[(0, 0)], [(1, 1)], [(2, 2)]])(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((2, 2), (2, 2))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
                GriddedPerm((1, 0), ((2, 2), (2, 2))),
            ),
            requirements=(
                (GriddedPerm((0,), ((0, 0),)),),
                (GriddedPerm((0,), ((2, 2),)),),
            ),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                                    GriddedPerm((0, 1), ((2, 2), (2, 2))),
                                    GriddedPerm((0, 1), ((2, 2), (2, 3))),
                                    GriddedPerm((0, 1), ((2, 3), (2, 3))),
                                    GriddedPerm((1, 0), ((1, 1), (1, 1))),
                                    GriddedPerm((1, 0), ((2, 2), (2, 2))),
                                    GriddedPerm((1, 0), ((2, 3), (2, 2))),
                                    GriddedPerm((1, 0), ((2, 3), (2, 3))),
                                ),
                                requirements=(
                                    (GriddedPerm((0,), ((0, 0),)),),
                                    (
                                        GriddedPerm((0,), ((2, 2),)),
                                        GriddedPerm((0,), ((2, 3),)),
                                    ),
                                ),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 1, 2: 2, 3: 2}, {0: 0, 1: 1, 2: 2}),
                        ),
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                                    GriddedPerm((0, 1), ((0, 0), (0, 1))),
                                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                                    GriddedPerm((0, 1), ((2, 3), (2, 3))),
                                    GriddedPerm((1, 0), ((1, 2), (1, 2))),
                                    GriddedPerm((1, 0), ((2, 3), (2, 3))),
                                ),
                                requirements=(
                                    (
                                        GriddedPerm((0,), ((0, 0),)),
                                        GriddedPerm((0,), ((0, 1),)),
                                    ),
                                    (GriddedPerm((0,), ((2, 3),)),),
                                ),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 0, 2: 1, 3: 2}, {0: 0, 1: 1, 2: 2}),
                        ),
                    )
                ),
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                                    GriddedPerm((0, 1), ((0, 0), (0, 1))),
                                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                                    GriddedPerm((0, 1), ((2, 3), (2, 3))),
                                    GriddedPerm((1, 0), ((1, 2), (1, 2))),
                                    GriddedPerm((1, 0), ((2, 3), (2, 3))),
                                ),
                                requirements=(
                                    (
                                        GriddedPerm((0,), ((0, 0),)),
                                        GriddedPerm((0,), ((0, 1),)),
                                    ),
                                    (GriddedPerm((0,), ((2, 3),)),),
                                ),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 0, 2: 1, 3: 2}, {0: 0, 1: 1, 2: 2}),
                        ),
                    )
                ),
            ),
        )
    ),
    FactorStrategy([[(0, 0)], [(1, 1)], [(2, 2)]])(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((2, 2), (2, 2))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
                GriddedPerm((1, 0), ((2, 2), (2, 2))),
            ),
            requirements=(
                (GriddedPerm((0,), ((0, 0),)),),
                (GriddedPerm((0,), ((2, 2),)),),
            ),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                                    GriddedPerm((0, 1), ((2, 2), (2, 2))),
                                    GriddedPerm((0, 1), ((2, 2), (3, 2))),
                                    GriddedPerm((0, 1), ((3, 2), (3, 2))),
                                    GriddedPerm((1, 0), ((1, 1), (1, 1))),
                                    GriddedPerm((1, 0), ((2, 2), (2, 2))),
                                    GriddedPerm((1, 0), ((2, 2), (3, 2))),
                                    GriddedPerm((1, 0), ((3, 2), (3, 2))),
                                ),
                                requirements=(
                                    (GriddedPerm((0,), ((0, 0),)),),
                                    (
                                        GriddedPerm((0,), ((2, 2),)),
                                        GriddedPerm((0,), ((3, 2),)),
                                    ),
                                ),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 1, 2: 2}, {0: 0, 1: 1, 2: 2, 3: 2}),
                        ),
                    )
                ),
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                                    GriddedPerm((0, 1), ((0, 0), (1, 0))),
                                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                                    GriddedPerm((0, 1), ((3, 2), (3, 2))),
                                    GriddedPerm((1, 0), ((2, 1), (2, 1))),
                                    GriddedPerm((1, 0), ((3, 2), (3, 2))),
                                ),
                                requirements=(
                                    (
                                        GriddedPerm((0,), ((0, 0),)),
                                        GriddedPerm((0,), ((1, 0),)),
                                    ),
                                    (GriddedPerm((0,), ((3, 2),)),),
                                ),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 1, 2: 2}, {0: 0, 1: 0, 2: 1, 3: 2}),
                        ),
                    )
                ),
            ),
        )
    ),
    # list(
    #     SlidingFactory(use_symmetries=True)(
    #         Tiling(
    #             obstructions=(
    #                 GriddedPerm((1, 0), ((2, 0), (2, 0))),
    #                 GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
    #                 GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
    #                 GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (3, 0))),
    #                 GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (3, 0))),
    #                 GriddedPerm((2, 1, 0), ((1, 0), (3, 0), (3, 0))),
    #                 GriddedPerm((2, 1, 0), ((2, 0), (3, 0), (3, 0))),
    #                 GriddedPerm((2, 1, 0), ((3, 0), (3, 0), (3, 0))),
    #                 GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
    #                 GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
    #                 GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
    #                 GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (3, 0))),
    #                 GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (1, 0))),
    #                 GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
    #                 GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (3, 0))),
    #                 GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (2, 0), (3, 0))),
    #                 GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (3, 0), (3, 0))),
    #             ),
    #             requirements=(),
    #             assumptions=(
    #                 TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),
    #                 TrackingAssumption(
    #                     (GriddedPerm((0,), ((2, 0),)), GriddedPerm((0,), ((3, 0),)))
    #                 ),
    #                 TrackingAssumption((GriddedPerm((0,), ((3, 0),)),)),
    #             ),
    #         )
    #     )
    # )[1],
    RequirementInsertionStrategy(
        gps=frozenset({GriddedPerm((0,), ((2, 0),))}), ignore_parent=True
    )(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1), ((2, 0), (2, 0))),
                GriddedPerm((0, 1), ((2, 0), (3, 0))),
                GriddedPerm((0, 1), ((3, 0), (3, 0))),
                GriddedPerm((1, 0), ((0, 0), (2, 0))),
                GriddedPerm((1, 0), ((0, 0), (3, 0))),
                GriddedPerm((1, 0), ((2, 0), (2, 0))),
                GriddedPerm((1, 0), ((2, 0), (3, 0))),
                GriddedPerm((1, 0), ((3, 0), (3, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (3, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),
            ),
            requirements=(
                (GriddedPerm((0,), ((0, 0),)),),
                (GriddedPerm((0,), ((3, 0),)),),
            ),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                                    GriddedPerm((0, 1), ((2, 0), (2, 0))),
                                    GriddedPerm((0, 1), ((2, 0), (3, 0))),
                                    GriddedPerm((0, 1), ((2, 0), (4, 0))),
                                    GriddedPerm((0, 1), ((3, 0), (3, 0))),
                                    GriddedPerm((0, 1), ((3, 0), (4, 0))),
                                    GriddedPerm((0, 1), ((4, 0), (4, 0))),
                                    GriddedPerm((1, 0), ((0, 0), (2, 0))),
                                    GriddedPerm((1, 0), ((0, 0), (3, 0))),
                                    GriddedPerm((1, 0), ((0, 0), (4, 0))),
                                    GriddedPerm((1, 0), ((2, 0), (2, 0))),
                                    GriddedPerm((1, 0), ((2, 0), (3, 0))),
                                    GriddedPerm((1, 0), ((2, 0), (4, 0))),
                                    GriddedPerm((1, 0), ((3, 0), (3, 0))),
                                    GriddedPerm((1, 0), ((3, 0), (4, 0))),
                                    GriddedPerm((1, 0), ((4, 0), (4, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (3, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (4, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (3, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (4, 0))),
                                    GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
                                    GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),
                                ),
                                requirements=(
                                    (GriddedPerm((0,), ((0, 0),)),),
                                    (
                                        GriddedPerm((0,), ((3, 0),)),
                                        GriddedPerm((0,), ((4, 0),)),
                                    ),
                                ),
                                parameters=(),
                            ),
                            RowColMap({0: 0}, {0: 0, 1: 1, 2: 2, 3: 3, 4: 3}),
                        ),
                    )
                ),
            ),
        )
    ),
    RequirementInsertionStrategy(
        gps=frozenset({GriddedPerm((0,), ((0, 2),))}), ignore_parent=True
    )(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 1), (0, 1))),
                GriddedPerm((0, 1), ((0, 1), (0, 2))),
                GriddedPerm((0, 1), ((0, 2), (0, 2))),
                GriddedPerm((1, 0), ((0, 1), (0, 0))),
                GriddedPerm((1, 0), ((0, 1), (0, 1))),
                GriddedPerm((1, 0), ((0, 2), (0, 0))),
                GriddedPerm((1, 0), ((0, 2), (0, 1))),
                GriddedPerm((1, 0), ((0, 2), (0, 2))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 1))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 2))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
            ),
            requirements=((GriddedPerm((0,), ((0, 1),)),),),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                                    GriddedPerm((0, 1), ((0, 1), (0, 2))),
                                    GriddedPerm((0, 1), ((0, 1), (0, 3))),
                                    GriddedPerm((0, 1), ((0, 2), (0, 2))),
                                    GriddedPerm((0, 1), ((0, 2), (0, 3))),
                                    GriddedPerm((0, 1), ((0, 3), (0, 3))),
                                    GriddedPerm((1, 0), ((0, 1), (0, 0))),
                                    GriddedPerm((1, 0), ((0, 1), (0, 1))),
                                    GriddedPerm((1, 0), ((0, 2), (0, 0))),
                                    GriddedPerm((1, 0), ((0, 2), (0, 1))),
                                    GriddedPerm((1, 0), ((0, 2), (0, 2))),
                                    GriddedPerm((1, 0), ((0, 3), (0, 0))),
                                    GriddedPerm((1, 0), ((0, 3), (0, 1))),
                                    GriddedPerm((1, 0), ((0, 3), (0, 2))),
                                    GriddedPerm((1, 0), ((0, 3), (0, 3))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 1))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 2))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 3))),
                                    GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                                    GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
                                ),
                                requirements=((GriddedPerm((0,), ((0, 1),)),),),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 1, 2: 2, 3: 2}, {0: 0}),
                        ),
                    )
                ),
            ),
        )
    ),
    # FusionStrategy(row_idx=2, tracked=True)(
    #     Tiling(
    #         obstructions=(
    #             GriddedPerm((0, 1), ((0, 2), (0, 2))),
    #             GriddedPerm((0, 1), ((0, 2), (0, 3))),
    #             GriddedPerm((0, 1), ((0, 3), (0, 3))),
    #             GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 1))),
    #             GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 2))),
    #             GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 3))),
    #             GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 0))),
    #             GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 1))),
    #             GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 2))),
    #             GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 3))),
    #             GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 1), (0, 1))),
    #             GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 1), (0, 2))),
    #             GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 1), (0, 3))),
    #         ),
    #         requirements=(),
    #         assumptions=(
    #             TrackingAssumption((GriddedPerm((0,), ((0, 1),)),)),
    #             TrackingAssumption(
    #                 (GriddedPerm((0,), ((0, 1),)), GriddedPerm((0,), ((0, 2),)))
    #             ),
    #             TrackingAssumption((GriddedPerm((0,), ((0, 3),)),)),
    #         ),
    #     )
    # ),
    # FusionStrategy(row_idx=3, tracked=True)(
    #     Tiling(
    #         obstructions=(
    #             GriddedPerm((0, 1), ((0, 2), (0, 2))),
    #             GriddedPerm((0, 1), ((1, 1), (1, 1))),
    #             GriddedPerm((0, 1), ((1, 3), (1, 3))),
    #             GriddedPerm((0, 1), ((1, 3), (1, 4))),
    #             GriddedPerm((0, 1), ((1, 4), (1, 4))),
    #             GriddedPerm((1, 0), ((0, 2), (0, 2))),
    #             GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
    #             GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 1))),
    #         ),
    #         requirements=((GriddedPerm((0,), ((0, 2),)),),),
    #         assumptions=(
    #             TrackingAssumption(
    #                 (GriddedPerm((0,), ((0, 2),)), GriddedPerm((0,), ((1, 1),)))
    #             ),
    #             TrackingAssumption(
    #                 (GriddedPerm((0,), ((1, 3),)), GriddedPerm((0,), ((1, 4),)))
    #             ),
    #             TrackingAssumption((GriddedPerm((0,), ((1, 4),)),)),
    #         ),
    #     )
    # ),
    # FusionStrategy(row_idx=1, tracked=True)(
    #     Tiling(
    #         obstructions=(
    #             GriddedPerm((0, 1), ((0, 0), (0, 0))),
    #             GriddedPerm((0, 1), ((0, 1), (0, 1))),
    #             GriddedPerm((0, 1), ((0, 1), (0, 2))),
    #             GriddedPerm((0, 1), ((0, 2), (0, 2))),
    #             GriddedPerm((0, 1), ((0, 4), (0, 4))),
    #             GriddedPerm((0, 1), ((1, 3), (1, 3))),
    #             GriddedPerm((1, 0), ((1, 3), (1, 3))),
    #         ),
    #         requirements=((GriddedPerm((0,), ((1, 3),)),),),
    #         assumptions=(
    #             TrackingAssumption((GriddedPerm((0,), ((0, 1),)),)),
    #             TrackingAssumption(
    #                 (GriddedPerm((0,), ((0, 1),)), GriddedPerm((0,), ((0, 2),)))
    #             ),
    #             TrackingAssumption((GriddedPerm((0,), ((0, 2),)),)),
    #             TrackingAssumption(
    #                 (GriddedPerm((0,), ((0, 4),)), GriddedPerm((0,), ((1, 3),)))
    #             ),
    #         ),
    #     )
    # ),
    # FusionStrategy(row_idx=1, col_idx=None, tracked=True)(
    #     Tiling(
    #         obstructions=(
    #             GriddedPerm((0, 1), ((0, 0), (0, 0))),
    #             GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 1))),
    #             GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (0, 2))),
    #             GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 2))),
    #             GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 1))),
    #             GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 2))),
    #             GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (0, 2))),
    #             GriddedPerm((0, 1, 2), ((0, 2), (0, 2), (0, 2))),
    #         ),
    #         assumptions=(
    #             TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),
    #             TrackingAssumption(
    #                 (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((0, 1),)))
    #             ),
    #             TrackingAssumption(
    #                 (
    #                     GriddedPerm((0,), ((0, 0),)),
    #                     GriddedPerm((0,), ((0, 1),)),
    #                     GriddedPerm((0,), ((0, 2),)),
    #                 )
    #             ),
    #             TrackingAssumption(
    #                 (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((0, 2),)))
    #             ),
    #             TrackingAssumption((GriddedPerm((0,), ((0, 2),)),)),
    #         ),
    #     )
    # ),
    # RearrangeAssumptionStrategy(
    #     assumption=TrackingAssumption(
    #         (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),)))
    #     ),
    #     sub_assumption=TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),
    # )(
    #     Tiling(
    #         obstructions=(
    #             GriddedPerm((0, 1), ((0, 0), (0, 0))),
    #             GriddedPerm((0, 1), ((1, 0), (1, 0))),
    #             GriddedPerm((0, 1), ((2, 0), (2, 0))),
    #         ),
    #         requirements=(),
    #         assumptions=(
    #             TrackingAssumption(
    #                 (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),)))
    #             ),
    #             TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),
    #         ),
    #     )
    # ),
    # AddAssumptionsStrategy(
    #     assumptions=(
    #         TrackingAssumption(
    #             (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),)))
    #         ),
    #     ),
    #     workable=False,
    # )(
    #     Tiling(
    #         obstructions=(
    #             GriddedPerm((0, 1), ((0, 0), (0, 0))),
    #             GriddedPerm((0, 1), ((1, 0), (1, 0))),
    #             GriddedPerm((0, 1), ((2, 0), (2, 0))),
    #         ),
    #         requirements=(),
    #         assumptions=(),
    #     )
    # ),
    RequirementPlacementStrategy(
        gps=(GriddedPerm((0,), ((0, 0),)),),
        indices=(0,),
        direction=3,
        own_col=True,
        own_row=True,
        ignore_parent=False,
        include_empty=True,
    )(
        Tiling(
            obstructions=(GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
                                    GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (1, 0))),
                                    GriddedPerm((1, 2, 0), ((0, 0), (1, 0), (1, 0))),
                                    GriddedPerm((1, 2, 0), ((1, 0), (1, 0), (1, 0))),
                                ),
                                requirements=(),
                                parameters=(),
                            ),
                            RowColMap({0: 0}, {0: 0, 1: 0}),
                        ),
                    )
                ),
            ),
        )
    ),
    RequirementInsertionStrategy(
        gps=frozenset({GriddedPerm((0,), ((1, 1),))}), ignore_parent=False
    )(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((1, 1), (1, 1))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 1))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 1))),
                GriddedPerm((0, 2, 1), ((0, 0), (1, 1), (1, 0))),
                GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (1, 1))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 3, 2), ((1, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 1, 3), ((0, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 1, 3), ((1, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 3, 1), ((0, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((1, 0, 2, 3), ((0, 0), (0, 0), (1, 0), (1, 0))),
                GriddedPerm((1, 0, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((1, 0, 2, 3), ((1, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((2, 0, 1, 3), ((0, 0), (0, 0), (1, 0), (1, 0))),
                GriddedPerm((2, 0, 1, 3), ((0, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((2, 0, 1, 3), ((1, 0), (1, 0), (1, 0), (1, 0))),
            ),
            requirements=((GriddedPerm((0,), ((0, 0),)),),),
        )
    ),
    RequirementPlacementStrategy(
        gps=(GriddedPerm((0,), ((0, 0),)),),
        indices=(0,),
        direction=1,
        own_col=True,
        own_row=True,
        ignore_parent=False,
        include_empty=True,
    )(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 2), (0, 2))),
                GriddedPerm((0, 1), ((1, 1), (1, 1))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
                GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((1, 2, 0), ((0, 0), (0, 2), (0, 0))),
            ),
            requirements=((GriddedPerm((0,), ((1, 1),)),),),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 3), (0, 3))),
                                    GriddedPerm((0, 1), ((1, 2), (1, 2))),
                                    GriddedPerm((1, 0), ((1, 2), (1, 2))),
                                    GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
                                    GriddedPerm((1, 2, 0), ((0, 0), (0, 1), (0, 0))),
                                    GriddedPerm((1, 2, 0), ((0, 0), (0, 3), (0, 0))),
                                    GriddedPerm((1, 2, 0), ((0, 1), (0, 1), (0, 0))),
                                    GriddedPerm((1, 2, 0), ((0, 1), (0, 1), (0, 1))),
                                    GriddedPerm((1, 2, 0), ((0, 1), (0, 3), (0, 0))),
                                    GriddedPerm((1, 2, 0), ((0, 1), (0, 3), (0, 1))),
                                ),
                                requirements=((GriddedPerm((0,), ((1, 2),)),),),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 0, 2: 1, 3: 2}, {0: 0, 1: 1}),
                        ),
                    )
                ),
            ),
        )
    ),
    RequirementPlacementStrategy(
        gps=(GriddedPerm((0,), ((0, 0),)),),
        indices=(0,),
        direction=3,
        own_col=True,
        own_row=True,
        ignore_parent=False,
        include_empty=True,
    )(
        Tiling(
            obstructions=(GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),),
            requirements=((GriddedPerm((0,), ((0, 0),)),),),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
                                    GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (1, 0))),
                                    GriddedPerm((1, 2, 0), ((0, 0), (1, 0), (1, 0))),
                                    GriddedPerm((1, 2, 0), ((1, 0), (1, 0), (1, 0))),
                                ),
                                requirements=(
                                    (
                                        GriddedPerm((0,), ((0, 0),)),
                                        GriddedPerm((0,), ((1, 0),)),
                                    ),
                                ),
                                parameters=(),
                            ),
                            RowColMap({0: 0}, {0: 0, 1: 0}),
                        ),
                    )
                ),
            ),
        )
    ),
    RequirementInsertionStrategy(gps=(GriddedPerm((0,), ((1, 0),)),),)(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((0, 0), (1, 0))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((1, 0), ((0, 0), (1, 0))),
            ),
            requirements=((GriddedPerm((0,), ((0, 0),)),),),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                                    GriddedPerm((0, 1), ((0, 0), (1, 0))),
                                    GriddedPerm((0, 1), ((0, 0), (2, 0))),
                                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                                    GriddedPerm((0, 1), ((1, 0), (2, 0))),
                                    GriddedPerm((0, 1), ((2, 0), (2, 0))),
                                    GriddedPerm((1, 0), ((0, 0), (1, 0))),
                                    GriddedPerm((1, 0), ((0, 0), (2, 0))),
                                ),
                                requirements=((GriddedPerm((0,), ((0, 0),)),),),
                                parameters=(),
                            ),
                            RowColMap({0: 0}, {0: 0, 1: 1, 2: 1}),
                        ),
                    )
                ),
            ),
        )
    ),
    RequirementInsertionStrategy(
        gps=frozenset({GriddedPerm((0,), ((1, 0),))}), ignore_parent=False
    )(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (1, 1))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 1))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 1), (0, 1))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 1), (1, 0))),
                GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((1, 0, 2), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((1, 0, 2), ((1, 0), (1, 0), (1, 1))),
                GriddedPerm((1, 0, 2), ((1, 1), (1, 0), (1, 1))),
                GriddedPerm((1, 0, 2), ((1, 1), (1, 1), (1, 1))),
                GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((2, 1, 0), ((1, 1), (1, 0), (1, 0))),
                GriddedPerm((2, 1, 0), ((1, 1), (1, 1), (1, 0))),
                GriddedPerm((2, 1, 0), ((1, 1), (1, 1), (1, 1))),
                GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 1, 3), ((0, 0), (0, 1), (0, 0), (0, 1))),
                GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 1), (0, 1), (0, 1))),
                GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 1), (0, 1), (1, 1))),
                GriddedPerm((0, 2, 1, 3), ((0, 1), (0, 1), (1, 1), (1, 1))),
                GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 1), (1, 1), (1, 1))),
                GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
                GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (1, 1))),
                GriddedPerm((0, 3, 2, 1), ((0, 1), (0, 1), (1, 1), (1, 1))),
            ),
            requirements=(
                (GriddedPerm((0,), ((1, 0),)), GriddedPerm((0,), ((1, 1),))),
            ),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (1, 1))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (0, 1), (2, 1))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 1))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 1))),
                                    GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 1))),
                                    GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                                    GriddedPerm((0, 2, 1), ((0, 0), (0, 1), (0, 1))),
                                    GriddedPerm((0, 2, 1), ((0, 0), (0, 1), (1, 0))),
                                    GriddedPerm((0, 2, 1), ((0, 0), (0, 1), (2, 0))),
                                    GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (1, 0))),
                                    GriddedPerm((0, 2, 1), ((0, 0), (1, 0), (2, 0))),
                                    GriddedPerm((0, 2, 1), ((0, 0), (2, 0), (2, 0))),
                                    GriddedPerm((1, 0, 2), ((1, 0), (1, 0), (1, 0))),
                                    GriddedPerm((1, 0, 2), ((1, 0), (1, 0), (1, 1))),
                                    GriddedPerm((1, 0, 2), ((1, 0), (1, 0), (2, 0))),
                                    GriddedPerm((1, 0, 2), ((1, 0), (1, 0), (2, 1))),
                                    GriddedPerm((1, 0, 2), ((1, 0), (2, 0), (2, 0))),
                                    GriddedPerm((1, 0, 2), ((1, 0), (2, 0), (2, 1))),
                                    GriddedPerm((1, 0, 2), ((1, 1), (1, 0), (1, 1))),
                                    GriddedPerm((1, 0, 2), ((1, 1), (1, 0), (2, 1))),
                                    GriddedPerm((1, 0, 2), ((1, 1), (1, 1), (1, 1))),
                                    GriddedPerm((1, 0, 2), ((1, 1), (1, 1), (2, 1))),
                                    GriddedPerm((1, 0, 2), ((1, 1), (2, 0), (2, 1))),
                                    GriddedPerm((1, 0, 2), ((1, 1), (2, 1), (2, 1))),
                                    GriddedPerm((1, 0, 2), ((2, 0), (2, 0), (2, 0))),
                                    GriddedPerm((1, 0, 2), ((2, 0), (2, 0), (2, 1))),
                                    GriddedPerm((1, 0, 2), ((2, 1), (2, 0), (2, 1))),
                                    GriddedPerm((1, 0, 2), ((2, 1), (2, 1), (2, 1))),
                                    GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
                                    GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
                                    GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
                                    GriddedPerm((2, 1, 0), ((1, 1), (1, 0), (1, 0))),
                                    GriddedPerm((2, 1, 0), ((1, 1), (1, 0), (2, 0))),
                                    GriddedPerm((2, 1, 0), ((1, 1), (1, 1), (1, 0))),
                                    GriddedPerm((2, 1, 0), ((1, 1), (1, 1), (1, 1))),
                                    GriddedPerm((2, 1, 0), ((1, 1), (1, 1), (2, 0))),
                                    GriddedPerm((2, 1, 0), ((1, 1), (1, 1), (2, 1))),
                                    GriddedPerm((2, 1, 0), ((1, 1), (2, 0), (2, 0))),
                                    GriddedPerm((2, 1, 0), ((1, 1), (2, 1), (2, 0))),
                                    GriddedPerm((2, 1, 0), ((1, 1), (2, 1), (2, 1))),
                                    GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
                                    GriddedPerm((2, 1, 0), ((2, 1), (2, 0), (2, 0))),
                                    GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (2, 0))),
                                    GriddedPerm((2, 1, 0), ((2, 1), (2, 1), (2, 1))),
                                    GriddedPerm(
                                        (0, 2, 1, 3), ((0, 0), (0, 0), (1, 0), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 1, 3), ((0, 0), (0, 0), (1, 0), (2, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 1, 3), ((0, 0), (0, 0), (2, 0), (2, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 1, 3), ((0, 0), (0, 1), (0, 0), (0, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 1, 3), ((0, 1), (0, 1), (0, 1), (0, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 1, 3), ((0, 1), (0, 1), (0, 1), (1, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 1, 3), ((0, 1), (0, 1), (0, 1), (2, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 1, 3), ((0, 1), (0, 1), (1, 1), (1, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 1, 3), ((0, 1), (0, 1), (1, 1), (2, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 1, 3), ((0, 1), (0, 1), (2, 1), (2, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 2, 1), ((0, 0), (0, 1), (1, 1), (1, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 2, 1), ((0, 0), (0, 1), (1, 1), (2, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 2, 1), ((0, 0), (0, 1), (2, 1), (2, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (0, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (1, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 2, 1), ((0, 1), (0, 1), (0, 1), (2, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 2, 1), ((0, 1), (0, 1), (1, 1), (1, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 2, 1), ((0, 1), (0, 1), (1, 1), (2, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 2, 1), ((0, 1), (0, 1), (2, 1), (2, 1))
                                    ),
                                ),
                                requirements=(
                                    (
                                        GriddedPerm((0,), ((1, 0),)),
                                        GriddedPerm((0,), ((1, 1),)),
                                        GriddedPerm((0,), ((2, 0),)),
                                        GriddedPerm((0,), ((2, 1),)),
                                    ),
                                ),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 1}, {0: 0, 1: 1, 2: 1}),
                        ),
                    )
                ),
            ),
        )
    ),
    FactorStrategy(
        partition=(((0, 1),), ((1, 0), (1, 2))), ignore_parent=True, workable=True
    )(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 1), (0, 1))),
                GriddedPerm((1, 0), ((0, 1), (0, 1))),
                GriddedPerm((1, 2, 0), ((1, 2), (1, 2), (1, 2))),
                GriddedPerm((2, 0, 1), ((1, 2), (1, 2), (1, 2))),
                GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 0), (1, 2), (1, 0))),
                GriddedPerm((0, 2, 3, 1), ((1, 0), (1, 2), (1, 2), (1, 0))),
                GriddedPerm((0, 3, 1, 2), ((1, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 3, 1, 2), ((1, 0), (1, 2), (1, 0), (1, 0))),
                GriddedPerm((0, 3, 1, 2), ((1, 0), (1, 2), (1, 0), (1, 2))),
            ),
            requirements=((GriddedPerm((0,), ((0, 1),)),),),
            parameters=(
                ParameterCounter(
                    (
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 2), (0, 2))),
                                    GriddedPerm((0, 1), ((1, 1), (1, 1))),
                                    GriddedPerm((1, 0), ((0, 2), (0, 2))),
                                    GriddedPerm((1, 0), ((1, 3), (1, 1))),
                                    GriddedPerm((1, 2, 0), ((1, 3), (1, 3), (1, 3))),
                                    GriddedPerm((2, 0, 1), ((1, 3), (1, 3), (1, 3))),
                                    GriddedPerm(
                                        (0, 2, 3, 1), ((1, 0), (1, 0), (1, 0), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 3, 1), ((1, 0), (1, 0), (1, 1), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 3, 1), ((1, 0), (1, 0), (1, 3), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 3, 1), ((1, 0), (1, 1), (1, 3), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 3, 1), ((1, 0), (1, 3), (1, 3), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 1, 2), ((1, 0), (1, 0), (1, 0), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 1, 2), ((1, 0), (1, 1), (1, 0), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 1, 2), ((1, 0), (1, 1), (1, 0), (1, 1))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 1, 2), ((1, 0), (1, 3), (1, 0), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 1, 2), ((1, 0), (1, 3), (1, 0), (1, 3))
                                    ),
                                ),
                                requirements=((GriddedPerm((0,), ((0, 2),)),),),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 0, 2: 1, 3: 2}, {0: 0, 1: 1}),
                        ),
                        PreimageCounter(
                            Tiling(
                                obstructions=(
                                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                                    GriddedPerm((1, 0), ((0, 1), (0, 1))),
                                    GriddedPerm((1, 2, 0), ((1, 2), (1, 2), (1, 2))),
                                    GriddedPerm((1, 2, 0), ((1, 2), (1, 3), (1, 2))),
                                    GriddedPerm((1, 2, 0), ((1, 3), (1, 3), (1, 2))),
                                    GriddedPerm((1, 2, 0), ((1, 3), (1, 3), (1, 3))),
                                    GriddedPerm((2, 0, 1), ((1, 2), (1, 2), (1, 2))),
                                    GriddedPerm((2, 0, 1), ((1, 3), (1, 2), (1, 2))),
                                    GriddedPerm((2, 0, 1), ((1, 3), (1, 2), (1, 3))),
                                    GriddedPerm((2, 0, 1), ((1, 3), (1, 3), (1, 3))),
                                    GriddedPerm(
                                        (0, 2, 3, 1), ((1, 0), (1, 0), (1, 0), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 3, 1), ((1, 0), (1, 0), (1, 2), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 3, 1), ((1, 0), (1, 0), (1, 3), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 3, 1), ((1, 0), (1, 2), (1, 2), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 3, 1), ((1, 0), (1, 2), (1, 3), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 2, 3, 1), ((1, 0), (1, 3), (1, 3), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 1, 2), ((1, 0), (1, 0), (1, 0), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 1, 2), ((1, 0), (1, 2), (1, 0), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 1, 2), ((1, 0), (1, 2), (1, 0), (1, 2))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 1, 2), ((1, 0), (1, 3), (1, 0), (1, 0))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 1, 2), ((1, 0), (1, 3), (1, 0), (1, 2))
                                    ),
                                    GriddedPerm(
                                        (0, 3, 1, 2), ((1, 0), (1, 3), (1, 0), (1, 3))
                                    ),
                                ),
                                requirements=((GriddedPerm((0,), ((0, 1),)),),),
                                parameters=(),
                            ),
                            RowColMap({0: 0, 1: 1, 2: 2, 3: 2}, {0: 0, 1: 1}),
                        ),
                    )
                ),
            ),
        )
    ),
]
equiv_rule_to_check = [r for r in rules_to_check if r.is_equivalence()]


@pytest.mark.parametrize("rule", rules_to_check)
def test_sanity_check_rules(rule):
    rules_to_check = [rule]
    if rule.is_two_way():
        rules_to_check.extend(
            rule.to_reverse_rule(i) for i in range(len(rule.children))
        )
    for rule, length in itertools.product(rules_to_check, range(6)):
        print(rule)
        assert rule.sanity_check(length)


@pytest.mark.parametrize("rule", equiv_rule_to_check)
def test_sanity_check_eqv(rule):
    new_rule = rule.to_equivalence_rule()
    for length in range(6):
        new_rule.sanity_check(length)


@pytest.mark.parametrize("rule", equiv_rule_to_check)
def test_sanity_check_eqv_then_reverse(rule):
    new_rule = rule.to_equivalence_rule().to_reverse_rule(0)
    for length in range(6):
        new_rule.sanity_check(length)


@pytest.mark.parametrize("rule", equiv_rule_to_check)
def test_sanity_check_reverse_then_equiv(rule):
    is_not_empty = [not c.is_empty() for c in rule.children]
    assert sum(is_not_empty) == 1
    non_empty_idx = is_not_empty.index(True)
    new_rule = rule.to_reverse_rule(non_empty_idx).to_equivalence_rule()
    for length in range(6):
        new_rule.sanity_check(length)


@pytest.mark.parametrize("rule", equiv_rule_to_check)
def test_sanity_check_eqv_then_path(rule):
    new_rule = EquivalencePathRule([rule.to_equivalence_rule()])
    for length in range(6):
        new_rule.sanity_check(length)


@pytest.mark.parametrize("rule", equiv_rule_to_check)
def test_sanity_check_eqv_then_reverse_then_path(rule):
    new_rule = EquivalencePathRule([rule.to_equivalence_rule().to_reverse_rule(0)])
    for length in range(6):
        new_rule.sanity_check(length)


@pytest.mark.parametrize("rule", equiv_rule_to_check)
def test_sanity_check_reverse_then_equiv_then_path(rule):
    is_not_empty = [not c.is_empty() for c in rule.children]
    assert sum(is_not_empty) == 1
    non_empty_idx = is_not_empty.index(True)
    new_rule = EquivalencePathRule(
        [rule.to_reverse_rule(non_empty_idx).to_equivalence_rule()]
    )
    for length in range(6):
        new_rule.sanity_check(length)


@pytest.mark.parametrize("rule", rules_to_check)
def test_pickle_rule(rule):
    print(rule)
    rule.constructor
    s = pickle.dumps(rule)
    new_rule = pickle.loads(s)
    assert rule == new_rule


def test_sanity_check_big_row_placement():
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0), (0, 0))),
            GriddedPerm((0, 1), ((0, 0), (3, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (3, 0))),
            GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (3, 0))),
            GriddedPerm((0, 1, 3, 2), ((1, 0), (2, 0), (2, 0), (3, 0))),
            GriddedPerm((0, 1, 3, 2), ((2, 0), (2, 0), (2, 0), (3, 0))),
            GriddedPerm((0, 2, 3, 1), ((1, 0), (2, 0), (2, 0), (3, 0))),
            GriddedPerm((0, 2, 3, 1), ((2, 0), (2, 0), (2, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 3, 4), ((1, 0), (2, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 3, 4), ((1, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 3, 4), ((2, 0), (2, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 3, 4), ((2, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 3, 4), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 4, 3), ((1, 0), (2, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 4, 3), ((1, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 4, 3), ((2, 0), (2, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 4, 3), ((2, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 4, 3), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 3, 4, 2), ((1, 0), (2, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 3, 4, 2), ((1, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 3, 4, 2), ((2, 0), (2, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 3, 4, 2), ((2, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 3, 4, 2), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 2, 3, 4, 1), ((1, 0), (2, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 2, 3, 4, 1), ((1, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 2, 3, 4, 1), ((2, 0), (2, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 2, 3, 4, 1), ((2, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 2, 3, 4, 1), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0))),
        ]
    )
    map_c0 = RowColMap({0: 0}, {0: 0, 1: 0, 2: 1, 3: 2, 4: 3})
    map_c1 = RowColMap({0: 0}, {0: 0, 1: 1, 2: 1, 3: 2, 4: 3})
    preimage_counter_c0 = PreimageCounter(map_c0.preimage_tiling(t), map_c0)
    preimage_counter_c1 = PreimageCounter(map_c1.preimage_tiling(t), map_c1)
    t = t.add_parameters(
        [
            ParameterCounter([preimage_counter_c0]),
            ParameterCounter([preimage_counter_c1]),
            ParameterCounter([preimage_counter_c0, preimage_counter_c1]),
        ]
    )
    strat = RequirementPlacementStrategy(
        gps=(
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((3, 0),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((2, 0),)),
        ),
        indices=(0, 0, 0, 0),
        direction=1,
        own_col=True,
        own_row=True,
        ignore_parent=False,
        include_empty=True,
    )
    rule = strat(t)
    rule.sanity_check(2)


def test_eqv_path_complement():
    strategy = ObstructionInferralStrategy(
        gps=(GriddedPerm((0,), ((0, 1),)), GriddedPerm((0,), ((0, 2),)))
    )
    tiling = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 1), (0, 2))),
            GriddedPerm((0, 1), ((0, 1), (0, 3))),
            GriddedPerm((0, 1), ((0, 2), (0, 3))),
            GriddedPerm((1, 0), ((0, 2), (0, 1))),
            GriddedPerm((1, 0), ((0, 3), (0, 1))),
            GriddedPerm((1, 0), ((0, 3), (0, 2))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 4), (0, 4))),
            GriddedPerm((0, 2, 1), ((0, 2), (0, 4), (0, 4))),
            GriddedPerm((0, 2, 1), ((0, 3), (0, 4), (0, 4))),
            GriddedPerm((2, 0, 1), ((0, 4), (0, 1), (0, 4))),
            GriddedPerm((2, 0, 1), ((0, 4), (0, 2), (0, 4))),
            GriddedPerm((2, 0, 1), ((0, 4), (0, 3), (0, 4))),
            GriddedPerm((2, 1, 0), ((0, 4), (0, 4), (0, 1))),
            GriddedPerm((2, 1, 0), ((0, 4), (0, 4), (0, 2))),
            GriddedPerm((2, 1, 0), ((0, 4), (0, 4), (0, 3))),
            GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 0, 3, 2), ((0, 1), (0, 1), (0, 4), (0, 1))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 2), (0, 2), (0, 4), (0, 2))),
            GriddedPerm((1, 0, 3, 2), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((1, 0, 3, 2), ((0, 3), (0, 3), (0, 4), (0, 3))),
            GriddedPerm((1, 0, 3, 2), ((0, 4), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((1, 3, 0, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 3, 0, 2), ((0, 1), (0, 4), (0, 1), (0, 1))),
            GriddedPerm((1, 3, 0, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 3, 0, 2), ((0, 2), (0, 4), (0, 2), (0, 2))),
            GriddedPerm((1, 3, 0, 2), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((1, 3, 0, 2), ((0, 3), (0, 4), (0, 3), (0, 3))),
            GriddedPerm((1, 3, 0, 2), ((0, 4), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((1, 3, 2, 0), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((1, 3, 2, 0), ((0, 1), (0, 4), (0, 1), (0, 1))),
            GriddedPerm((1, 3, 2, 0), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((1, 3, 2, 0), ((0, 2), (0, 4), (0, 2), (0, 2))),
            GriddedPerm((1, 3, 2, 0), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((1, 3, 2, 0), ((0, 3), (0, 4), (0, 3), (0, 3))),
            GriddedPerm((1, 3, 2, 0), ((0, 4), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 0), (0, 0), (0, 1), (0, 0))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 0), (0, 0), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 0), (0, 0), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 0), (0, 0), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 0), (0, 0), (0, 3), (0, 0))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 0), (0, 0), (0, 3), (0, 3))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 0), (0, 0), (0, 4), (0, 0))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 0), (0, 0), (0, 4), (0, 1))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 0), (0, 0), (0, 4), (0, 2))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 0), (0, 0), (0, 4), (0, 3))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 0), (0, 0), (0, 4), (0, 4))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 1), (0, 0), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 1), (0, 0), (0, 4), (0, 1))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 2), (0, 0), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 2), (0, 0), (0, 4), (0, 2))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 3), (0, 0), (0, 3), (0, 3))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 3), (0, 0), (0, 4), (0, 3))),
            GriddedPerm((0, 2, 1, 4, 3), ((0, 0), (0, 4), (0, 0), (0, 4), (0, 4))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 0), (0, 1), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 0), (0, 1), (0, 0), (0, 1))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 0), (0, 2), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 0), (0, 2), (0, 0), (0, 2))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 0), (0, 3), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 0), (0, 3), (0, 0), (0, 3))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 0), (0, 4), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 0), (0, 4), (0, 0), (0, 1))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 0), (0, 4), (0, 0), (0, 2))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 0), (0, 4), (0, 0), (0, 3))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 0), (0, 4), (0, 0), (0, 4))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 1), (0, 1), (0, 0), (0, 1))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 1), (0, 4), (0, 0), (0, 1))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 2), (0, 2), (0, 0), (0, 2))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 2), (0, 4), (0, 0), (0, 2))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 3), (0, 3), (0, 0), (0, 3))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 3), (0, 4), (0, 0), (0, 3))),
            GriddedPerm((0, 2, 4, 1, 3), ((0, 0), (0, 4), (0, 4), (0, 0), (0, 4))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 0), (0, 1), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 0), (0, 1), (0, 1), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 0), (0, 2), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 0), (0, 2), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 0), (0, 3), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 0), (0, 3), (0, 3), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 0), (0, 4), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 0), (0, 4), (0, 1), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 0), (0, 4), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 0), (0, 4), (0, 3), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 0), (0, 4), (0, 4), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 1), (0, 1), (0, 1), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 1), (0, 4), (0, 1), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 2), (0, 2), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 2), (0, 4), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 3), (0, 3), (0, 3), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 3), (0, 4), (0, 3), (0, 0))),
            GriddedPerm((0, 2, 4, 3, 1), ((0, 0), (0, 4), (0, 4), (0, 4), (0, 0))),
        ),
        requirements=((GriddedPerm((0,), ((0, 3),)),),),
        parameters=(
            ParameterCounter(
                (
                    PreimageCounter(
                        Tiling(
                            obstructions=(
                                GriddedPerm((0, 1), ((0, 1), (0, 2))),
                                GriddedPerm((0, 1), ((0, 1), (0, 3))),
                                GriddedPerm((0, 1), ((0, 1), (0, 4))),
                                GriddedPerm((0, 1), ((0, 2), (0, 3))),
                                GriddedPerm((0, 1), ((0, 2), (0, 4))),
                                GriddedPerm((1, 0), ((0, 2), (0, 1))),
                                GriddedPerm((1, 0), ((0, 3), (0, 1))),
                                GriddedPerm((1, 0), ((0, 3), (0, 2))),
                                GriddedPerm((1, 0), ((0, 4), (0, 1))),
                                GriddedPerm((1, 0), ((0, 4), (0, 2))),
                                GriddedPerm((0, 2, 1), ((0, 1), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 2), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 3), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 4), (0, 5), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 1), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 2), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 3), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 4), (0, 5))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 1))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 2))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 3))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 4))),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 5), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 5), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 4), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 5), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 5), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 3), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 3), (0, 5), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 4), (0, 5), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 5), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 5), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 4), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 4), (0, 3), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 5), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 5), (0, 3), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 4), (0, 3), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 5), (0, 3), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 5), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 5), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 5), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 4), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 4), (0, 4), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 5), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 5), (0, 4), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 4), (0, 4), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 5), (0, 4), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 5), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 1), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 2), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 3), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 1), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 5), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 2), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 5), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 3), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 4), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 4), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 5), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 5), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 4), (0, 0), (0, 4), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 4), (0, 0), (0, 5), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 5), (0, 0), (0, 5), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 1), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 5), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 2), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 5), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 3), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 4), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 4), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 5), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 5), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 4), (0, 4), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 4), (0, 5), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 5), (0, 5), (0, 0), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 1), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 2), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 3), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 5), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 1), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 5), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 2), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 5), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 3), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 4), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 4), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 5), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 5), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 4), (0, 4), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 4), (0, 5), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 5), (0, 5), (0, 5), (0, 0)),
                                ),
                            ),
                            requirements=(
                                (
                                    GriddedPerm((0,), ((0, 3),)),
                                    GriddedPerm((0,), ((0, 4),)),
                                ),
                            ),
                            parameters=(),
                        ),
                        RowColMap({0: 0, 1: 1, 2: 2, 3: 3, 4: 3, 5: 4}, {0: 0}),
                    ),
                    PreimageCounter(
                        Tiling(
                            obstructions=(
                                GriddedPerm((0, 1), ((0, 1), (0, 2))),
                                GriddedPerm((0, 1), ((0, 1), (0, 3))),
                                GriddedPerm((0, 1), ((0, 2), (0, 3))),
                                GriddedPerm((1, 0), ((0, 2), (0, 1))),
                                GriddedPerm((1, 0), ((0, 3), (0, 1))),
                                GriddedPerm((1, 0), ((0, 3), (0, 2))),
                                GriddedPerm((0, 2, 1), ((0, 1), (0, 4), (0, 4))),
                                GriddedPerm((0, 2, 1), ((0, 1), (0, 5), (0, 4))),
                                GriddedPerm((0, 2, 1), ((0, 1), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 2), (0, 4), (0, 4))),
                                GriddedPerm((0, 2, 1), ((0, 2), (0, 5), (0, 4))),
                                GriddedPerm((0, 2, 1), ((0, 2), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 3), (0, 4), (0, 4))),
                                GriddedPerm((0, 2, 1), ((0, 3), (0, 5), (0, 4))),
                                GriddedPerm((0, 2, 1), ((0, 3), (0, 5), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 4), (0, 1), (0, 4))),
                                GriddedPerm((2, 0, 1), ((0, 4), (0, 2), (0, 4))),
                                GriddedPerm((2, 0, 1), ((0, 4), (0, 3), (0, 4))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 1), (0, 4))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 1), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 2), (0, 4))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 2), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 3), (0, 4))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 3), (0, 5))),
                                GriddedPerm((2, 1, 0), ((0, 4), (0, 4), (0, 1))),
                                GriddedPerm((2, 1, 0), ((0, 4), (0, 4), (0, 2))),
                                GriddedPerm((2, 1, 0), ((0, 4), (0, 4), (0, 3))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 4), (0, 1))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 4), (0, 2))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 4), (0, 3))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 1))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 2))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 3))),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 4), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 5), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 4), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 5), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 4), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 5), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 4), (0, 5), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 4), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 5), (0, 4), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 4), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 5), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 4), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 5), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 4), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 5), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 5), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 5), (0, 4), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 5), (0, 5), (0, 4), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 4), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 5), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 4), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 5), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 4), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 5), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 5), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 5), (0, 5), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 5), (0, 5), (0, 5), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 1), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 2), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 3), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 1), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 4), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 5), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 2), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 4), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 5), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 3), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 4), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 5), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 4), (0, 0), (0, 4), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 4), (0, 0), (0, 5), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 4), (0, 0), (0, 5), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 5), (0, 0), (0, 5), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 1), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 4), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 5), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 2), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 4), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 5), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 3), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 4), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 5), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 4), (0, 4), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 4), (0, 5), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 4), (0, 5), (0, 0), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 5), (0, 5), (0, 0), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 1), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 2), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 3), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 5), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 1), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 4), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 5), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 2), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 4), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 5), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 3), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 4), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 5), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 4), (0, 4), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 4), (0, 5), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 4), (0, 5), (0, 5), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 5), (0, 5), (0, 5), (0, 0)),
                                ),
                            ),
                            requirements=((GriddedPerm((0,), ((0, 3),)),),),
                            parameters=(),
                        ),
                        RowColMap({0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 4}, {0: 0}),
                    ),
                )
            ),
            ParameterCounter(
                (
                    PreimageCounter(
                        Tiling(
                            obstructions=(
                                GriddedPerm((0, 1), ((0, 1), (0, 2))),
                                GriddedPerm((0, 1), ((0, 1), (0, 3))),
                                GriddedPerm((0, 1), ((0, 1), (0, 4))),
                                GriddedPerm((0, 1), ((0, 2), (0, 4))),
                                GriddedPerm((0, 1), ((0, 3), (0, 4))),
                                GriddedPerm((1, 0), ((0, 2), (0, 1))),
                                GriddedPerm((1, 0), ((0, 3), (0, 1))),
                                GriddedPerm((1, 0), ((0, 4), (0, 1))),
                                GriddedPerm((1, 0), ((0, 4), (0, 2))),
                                GriddedPerm((1, 0), ((0, 4), (0, 3))),
                                GriddedPerm((0, 2, 1), ((0, 1), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 2), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 3), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 4), (0, 5), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 1), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 2), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 3), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 4), (0, 5))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 1))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 2))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 3))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 4))),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 5), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 3), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 5), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 5), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 2), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 2), (0, 5), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 5), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 4), (0, 5), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 5), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 3), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 3), (0, 2), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 5), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 5), (0, 2), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 3), (0, 2), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 5), (0, 2), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 5), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 5), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 5), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 3), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 3), (0, 3), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 5), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 5), (0, 3), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 3), (0, 3), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 5), (0, 3), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 5), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 5), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 1), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 2), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 3), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 3), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 1), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 5), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 2), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 3), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 3), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 5), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 5), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 3), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 5), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 4), (0, 0), (0, 4), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 4), (0, 0), (0, 5), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 5), (0, 0), (0, 5), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 1), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 5), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 2), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 3), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 3), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 5), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 5), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 3), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 5), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 4), (0, 4), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 4), (0, 5), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 5), (0, 5), (0, 0), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 1), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 2), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 3), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 3), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 5), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 1), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 5), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 2), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 3), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 3), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 5), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 5), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 3), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 5), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 4), (0, 4), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 4), (0, 5), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 5), (0, 5), (0, 5), (0, 0)),
                                ),
                            ),
                            requirements=((GriddedPerm((0,), ((0, 4),)),),),
                            parameters=(),
                        ),
                        RowColMap({0: 0, 1: 1, 2: 2, 3: 2, 4: 3, 5: 4}, {0: 0}),
                    ),
                    PreimageCounter(
                        Tiling(
                            obstructions=(
                                GriddedPerm((0, 1), ((0, 1), (0, 3))),
                                GriddedPerm((0, 1), ((0, 1), (0, 4))),
                                GriddedPerm((0, 1), ((0, 2), (0, 3))),
                                GriddedPerm((0, 1), ((0, 2), (0, 4))),
                                GriddedPerm((0, 1), ((0, 3), (0, 4))),
                                GriddedPerm((1, 0), ((0, 3), (0, 1))),
                                GriddedPerm((1, 0), ((0, 3), (0, 2))),
                                GriddedPerm((1, 0), ((0, 4), (0, 1))),
                                GriddedPerm((1, 0), ((0, 4), (0, 2))),
                                GriddedPerm((1, 0), ((0, 4), (0, 3))),
                                GriddedPerm((0, 2, 1), ((0, 1), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 2), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 3), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 4), (0, 5), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 1), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 2), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 3), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 4), (0, 5))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 1))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 2))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 3))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 4))),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 2), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 5), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 5), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 1), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 1), (0, 5), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 5), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 5), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 4), (0, 5), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 2), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 2), (0, 1), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 5), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 5), (0, 1), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 2), (0, 1), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 5), (0, 1), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 5), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 5), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 5), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 2), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 2), (0, 2), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 5), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 5), (0, 2), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 2), (0, 2), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 5), (0, 2), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 5), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 5), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 5), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 1), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 2), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 2), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 3), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 1), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 2), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 2), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 5), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 5), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 2), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 5), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 3), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 5), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 4), (0, 0), (0, 4), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 4), (0, 0), (0, 5), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 5), (0, 0), (0, 5), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 1), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 2), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 2), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 5), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 5), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 2), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 5), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 3), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 5), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 4), (0, 4), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 4), (0, 5), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 5), (0, 5), (0, 0), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 1), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 2), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 2), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 3), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 5), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 1), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 2), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 2), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 5), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 5), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 2), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 5), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 3), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 5), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 4), (0, 4), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 4), (0, 5), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 5), (0, 5), (0, 5), (0, 0)),
                                ),
                            ),
                            requirements=((GriddedPerm((0,), ((0, 4),)),),),
                            parameters=(),
                        ),
                        RowColMap({0: 0, 1: 1, 2: 1, 3: 2, 4: 3, 5: 4}, {0: 0}),
                    ),
                )
            ),
            ParameterCounter(
                (
                    PreimageCounter(
                        Tiling(
                            obstructions=(
                                GriddedPerm((0, 1), ((0, 1), (0, 3))),
                                GriddedPerm((0, 1), ((0, 1), (0, 4))),
                                GriddedPerm((0, 1), ((0, 2), (0, 3))),
                                GriddedPerm((0, 1), ((0, 2), (0, 4))),
                                GriddedPerm((0, 1), ((0, 3), (0, 4))),
                                GriddedPerm((1, 0), ((0, 3), (0, 1))),
                                GriddedPerm((1, 0), ((0, 3), (0, 2))),
                                GriddedPerm((1, 0), ((0, 4), (0, 1))),
                                GriddedPerm((1, 0), ((0, 4), (0, 2))),
                                GriddedPerm((1, 0), ((0, 4), (0, 3))),
                                GriddedPerm((0, 2, 1), ((0, 1), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 2), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 3), (0, 5), (0, 5))),
                                GriddedPerm((0, 2, 1), ((0, 4), (0, 5), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 1), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 2), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 3), (0, 5))),
                                GriddedPerm((2, 0, 1), ((0, 5), (0, 4), (0, 5))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 1))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 2))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 3))),
                                GriddedPerm((2, 1, 0), ((0, 5), (0, 5), (0, 4))),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 2), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 5), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 1), (0, 1), (0, 5), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 1), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 1), (0, 5), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 2), (0, 2), (0, 5), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 3), (0, 3), (0, 5), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 4), (0, 4), (0, 5), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 0, 3, 2), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 2), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 2), (0, 1), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 5), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 1), (0, 5), (0, 1), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 2), (0, 1), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 5), (0, 1), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 2), (0, 5), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 3), (0, 5), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 4), (0, 5), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 0, 2), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 1), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 2), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 2), (0, 2), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 5), (0, 1), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 1), (0, 5), (0, 2), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 2), (0, 2), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 2), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 5), (0, 2), (0, 1))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 2), (0, 5), (0, 2), (0, 2))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 3), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 3), (0, 5), (0, 3), (0, 3))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 4), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 4), (0, 5), (0, 4), (0, 4))
                                ),
                                GriddedPerm(
                                    (1, 3, 2, 0), ((0, 5), (0, 5), (0, 5), (0, 5))
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 1), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 2), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 2), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 3), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 4), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 5), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 1), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 2), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 2), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 5), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 1), (0, 0), (0, 5), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 2), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 2), (0, 0), (0, 5), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 3), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 3), (0, 0), (0, 5), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 4), (0, 0), (0, 4), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 4), (0, 0), (0, 5), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 1, 4, 3),
                                    ((0, 0), (0, 5), (0, 0), (0, 5), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 1), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 2), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 2), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 5), (0, 0), (0, 1)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 1), (0, 5), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 2), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 2), (0, 5), (0, 0), (0, 2)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 3), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 3), (0, 5), (0, 0), (0, 3)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 4), (0, 4), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 4), (0, 5), (0, 0), (0, 4)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 1, 3),
                                    ((0, 0), (0, 5), (0, 5), (0, 0), (0, 5)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 1), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 1), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 2), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 2), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 2), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 3), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 3), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 4), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 0), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 0), (0, 5), (0, 5), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 1), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 2), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 2), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 5), (0, 1), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 1), (0, 5), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 2), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 2), (0, 5), (0, 2), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 3), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 3), (0, 5), (0, 3), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 4), (0, 4), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 4), (0, 5), (0, 4), (0, 0)),
                                ),
                                GriddedPerm(
                                    (0, 2, 4, 3, 1),
                                    ((0, 0), (0, 5), (0, 5), (0, 5), (0, 0)),
                                ),
                            ),
                            requirements=((GriddedPerm((0,), ((0, 4),)),),),
                            parameters=(),
                        ),
                        RowColMap({0: 0, 1: 1, 2: 1, 3: 2, 4: 3, 5: 4}, {0: 0}),
                    ),
                )
            ),
        ),
    )

    rule = EquivalencePathRule([strategy(tiling).to_reverse_rule(0)])
    for i in range(5):
        rule.sanity_check(i)

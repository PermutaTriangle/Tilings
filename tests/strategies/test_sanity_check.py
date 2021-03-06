import itertools

import pytest

from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.strategies.factor import FactorStrategy
from tilings.strategies.fusion import FusionStrategy
from tilings.strategies.requirement_insertion import RequirementInsertionStrategy
from tilings.strategies.requirement_placement import RequirementPlacementStrategy
from tilings.strategies.sliding import SlidingFactory

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
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
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
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((3, 0),)),)),),
        )
    ).to_equivalence_rule(),
    FusionStrategy(col_idx=1, tracked=True)(
        Tiling(
            obstructions=(
                GriddedPerm((0,), ((0, 0),)),
                GriddedPerm((0,), ((1, 0),)),
                GriddedPerm((0,), ((1, 1),)),
                GriddedPerm((0,), ((2, 0),)),
                GriddedPerm((0,), ((2, 1),)),
                GriddedPerm((0,), ((3, 1),)),
                GriddedPerm((0,), ((3, 2),)),
                GriddedPerm((0, 1), ((1, 2), (1, 2))),
                GriddedPerm((0, 1), ((1, 2), (2, 2))),
                GriddedPerm((0, 1), ((2, 2), (2, 2))),
                GriddedPerm((0, 1), ((3, 0), (3, 0))),
                GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 2))),
                GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (0, 2))),
                GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (1, 2))),
                GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (2, 2))),
                GriddedPerm((0, 2, 1), ((0, 1), (0, 1), (0, 1))),
                GriddedPerm((0, 2, 1), ((0, 1), (1, 2), (1, 2))),
                GriddedPerm((0, 2, 1), ((0, 1), (1, 2), (2, 2))),
                GriddedPerm((0, 2, 1), ((0, 1), (2, 2), (2, 2))),
                GriddedPerm((1, 0, 2), ((0, 2), (0, 1), (1, 2))),
                GriddedPerm((1, 0, 2), ((0, 2), (0, 1), (2, 2))),
                GriddedPerm((2, 0, 1), ((0, 1), (0, 1), (0, 1))),
                GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
                GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (0, 2), (1, 2))),
                GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (0, 2), (2, 2))),
                GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (1, 2), (1, 2))),
                GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (1, 2), (2, 2))),
                GriddedPerm((0, 1, 3, 2), ((0, 2), (0, 2), (2, 2), (2, 2))),
                GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 2), (0, 2), (0, 2))),
                GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 2), (0, 2), (1, 2))),
                GriddedPerm((0, 2, 1, 3), ((0, 2), (0, 2), (0, 2), (2, 2))),
                GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
                GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (0, 2), (1, 2))),
                GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (0, 2), (2, 2))),
                GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (1, 2), (1, 2))),
                GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (1, 2), (2, 2))),
                GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (2, 2), (2, 2))),
                GriddedPerm((2, 0, 1, 3), ((0, 2), (0, 2), (0, 2), (0, 2))),
                GriddedPerm((2, 0, 1, 3), ((0, 2), (0, 2), (0, 2), (1, 2))),
                GriddedPerm((2, 0, 1, 3), ((0, 2), (0, 2), (0, 2), (2, 2))),
            ),
            requirements=(
                (GriddedPerm((0,), ((1, 2),)),),
                (GriddedPerm((0,), ((2, 2),)),),
                (GriddedPerm((0,), ((3, 0),)),),
            ),
            assumptions=(
                TrackingAssumption(
                    (
                        GriddedPerm((0,), ((2, 2),)),
                        GriddedPerm((0,), ((3, 0),)),
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
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 2),)),)),),
        )
    ).to_equivalence_rule(),
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
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
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
            assumptions=(
                TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),
                TrackingAssumption(
                    (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((2, 2),))),
                ),
            ),
        ),
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
            assumptions=(
                TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),
                TrackingAssumption((GriddedPerm((0,), ((2, 2),)),)),
            ),
        ),
    ),
    list(
        SlidingFactory(use_symmetries=True)(
            Tiling(
                obstructions=(
                    GriddedPerm((1, 0), ((2, 0), (2, 0))),
                    GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
                    GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
                    GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (3, 0))),
                    GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (3, 0))),
                    GriddedPerm((2, 1, 0), ((1, 0), (3, 0), (3, 0))),
                    GriddedPerm((2, 1, 0), ((2, 0), (3, 0), (3, 0))),
                    GriddedPerm((2, 1, 0), ((3, 0), (3, 0), (3, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (0, 0), (3, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (1, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (1, 0), (3, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (2, 0), (3, 0))),
                    GriddedPerm((0, 3, 2, 1), ((0, 0), (0, 0), (3, 0), (3, 0))),
                ),
                requirements=(),
                assumptions=(
                    TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),
                    TrackingAssumption(
                        (GriddedPerm((0,), ((2, 0),)), GriddedPerm((0,), ((3, 0),)))
                    ),
                    TrackingAssumption((GriddedPerm((0,), ((3, 0),)),)),
                ),
            )
        )
    )[1],
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
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((3, 0),)),)),),
        )
    ).to_equivalence_rule(),
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
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 2),)),)),),
        )
    ).to_equivalence_rule(),
]


@pytest.mark.parametrize("rule", rules_to_check)
def test_sanity_check_rules(rule):
    rules_to_check = [rule]
    if rule.is_two_way():
        rules_to_check.extend(
            rule.to_reverse_rule(i) for i in range(len(rule.children))
        )
    for rule, length in itertools.product(rules_to_check, range(6)):
        assert rule.sanity_check(length)


def test_sanity_check_big_row_placement():
    rule = RequirementPlacementStrategy(
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
    )(
        Tiling(
            obstructions=(
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
            ),
            requirements=(),
            assumptions=(
                TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),
                TrackingAssumption(
                    (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),)))
                ),
                TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),
            ),
        )
    )
    rule.sanity_check(2)

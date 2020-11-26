import pytest

from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.strategies.fusion import FusionStrategy
from tilings.strategies.requirement_insertion import RequirementInsertionStrategy
from tilings.strategies.requirement_placement import RequirementPlacementStrategy
from tilings.strategies.sliding import SlidingFactory


@pytest.fixture
def rules_to_check():
    return [
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
        )
        .to_equivalence_rule()
        .to_reverse_rule(),
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
        )
        .to_equivalence_rule()
        .to_reverse_rule(),
    ]


def test_sanity_check_rules(rules_to_check):
    for rule in rules_to_check:
        print(rule)
        for n in range(6):
            assert rule.sanity_check(n)


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


def test_sanity_check_sliding():
    assert list(
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
    )[1].sanity_check(2)

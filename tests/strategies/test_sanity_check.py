import pytest

from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.strategies.fusion import FusionStrategy
from tilings.strategies.requirement_insertion import RequirementInsertionStrategy


@pytest.fixture
def rules_to_check():
    return [
        RequirementInsertionStrategy(
            gps=frozenset({GriddedPerm(Perm((0,)), ((0, 0),))}), ignore_parent=True
        )(
            Tiling(
                obstructions=(
                    GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
                    GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
                    GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
                    GriddedPerm(Perm((1, 0)), ((0, 0), (1, 0))),
                    GriddedPerm(Perm((1, 0)), ((1, 0), (1, 0))),
                ),
                requirements=((GriddedPerm(Perm((0,)), ((1, 0),)),),),
                assumptions=(
                    TrackingAssumption((GriddedPerm(Perm((0,)), ((0, 0),)),)),
                ),
            )
        ),
        RequirementInsertionStrategy(
            gps=frozenset({GriddedPerm(Perm((0,)), ((2, 0),))}), ignore_parent=True
        )(
            Tiling(
                obstructions=(
                    GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
                    GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
                    GriddedPerm(Perm((0, 1)), ((2, 0), (3, 0))),
                    GriddedPerm(Perm((0, 1)), ((3, 0), (3, 0))),
                    GriddedPerm(Perm((1, 0)), ((0, 0), (2, 0))),
                    GriddedPerm(Perm((1, 0)), ((0, 0), (3, 0))),
                    GriddedPerm(Perm((1, 0)), ((2, 0), (2, 0))),
                    GriddedPerm(Perm((1, 0)), ((2, 0), (3, 0))),
                    GriddedPerm(Perm((1, 0)), ((3, 0), (3, 0))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (1, 0))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (2, 0))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (3, 0))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 0))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (3, 0))),
                    GriddedPerm(Perm((0, 2, 1)), ((0, 0), (0, 0), (1, 0))),
                    GriddedPerm(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0))),
                ),
                requirements=(
                    (GriddedPerm(Perm((0,)), ((0, 0),)),),
                    (GriddedPerm(Perm((0,)), ((3, 0),)),),
                ),
                assumptions=(
                    TrackingAssumption((GriddedPerm(Perm((0,)), ((3, 0),)),)),
                ),
            )
        )
        .to_equivalence_rule()
        .to_reverse_rule(),
        FusionStrategy(col_idx=1, tracked=True)(
            Tiling(
                obstructions=(
                    GriddedPerm(Perm((0,)), ((0, 0),)),
                    GriddedPerm(Perm((0,)), ((1, 0),)),
                    GriddedPerm(Perm((0,)), ((1, 1),)),
                    GriddedPerm(Perm((0,)), ((2, 0),)),
                    GriddedPerm(Perm((0,)), ((2, 1),)),
                    GriddedPerm(Perm((0,)), ((3, 1),)),
                    GriddedPerm(Perm((0,)), ((3, 2),)),
                    GriddedPerm(Perm((0, 1)), ((1, 2), (1, 2))),
                    GriddedPerm(Perm((0, 1)), ((1, 2), (2, 2))),
                    GriddedPerm(Perm((0, 1)), ((2, 2), (2, 2))),
                    GriddedPerm(Perm((0, 1)), ((3, 0), (3, 0))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 1), (0, 1), (0, 2))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 1), (0, 2), (0, 2))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 1), (0, 2), (1, 2))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 1), (0, 2), (2, 2))),
                    GriddedPerm(Perm((0, 2, 1)), ((0, 1), (0, 1), (0, 1))),
                    GriddedPerm(Perm((0, 2, 1)), ((0, 1), (1, 2), (1, 2))),
                    GriddedPerm(Perm((0, 2, 1)), ((0, 1), (1, 2), (2, 2))),
                    GriddedPerm(Perm((0, 2, 1)), ((0, 1), (2, 2), (2, 2))),
                    GriddedPerm(Perm((1, 0, 2)), ((0, 2), (0, 1), (1, 2))),
                    GriddedPerm(Perm((1, 0, 2)), ((0, 2), (0, 1), (2, 2))),
                    GriddedPerm(Perm((2, 0, 1)), ((0, 1), (0, 1), (0, 1))),
                    GriddedPerm(Perm((0, 1, 3, 2)), ((0, 2), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm(Perm((0, 1, 3, 2)), ((0, 2), (0, 2), (0, 2), (1, 2))),
                    GriddedPerm(Perm((0, 1, 3, 2)), ((0, 2), (0, 2), (0, 2), (2, 2))),
                    GriddedPerm(Perm((0, 1, 3, 2)), ((0, 2), (0, 2), (1, 2), (1, 2))),
                    GriddedPerm(Perm((0, 1, 3, 2)), ((0, 2), (0, 2), (1, 2), (2, 2))),
                    GriddedPerm(Perm((0, 1, 3, 2)), ((0, 2), (0, 2), (2, 2), (2, 2))),
                    GriddedPerm(Perm((0, 2, 1, 3)), ((0, 2), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm(Perm((0, 2, 1, 3)), ((0, 2), (0, 2), (0, 2), (1, 2))),
                    GriddedPerm(Perm((0, 2, 1, 3)), ((0, 2), (0, 2), (0, 2), (2, 2))),
                    GriddedPerm(Perm((0, 2, 3, 1)), ((0, 2), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm(Perm((0, 2, 3, 1)), ((0, 2), (0, 2), (0, 2), (1, 2))),
                    GriddedPerm(Perm((0, 2, 3, 1)), ((0, 2), (0, 2), (0, 2), (2, 2))),
                    GriddedPerm(Perm((0, 2, 3, 1)), ((0, 2), (0, 2), (1, 2), (1, 2))),
                    GriddedPerm(Perm((0, 2, 3, 1)), ((0, 2), (0, 2), (1, 2), (2, 2))),
                    GriddedPerm(Perm((0, 2, 3, 1)), ((0, 2), (0, 2), (2, 2), (2, 2))),
                    GriddedPerm(Perm((2, 0, 1, 3)), ((0, 2), (0, 2), (0, 2), (0, 2))),
                    GriddedPerm(Perm((2, 0, 1, 3)), ((0, 2), (0, 2), (0, 2), (1, 2))),
                    GriddedPerm(Perm((2, 0, 1, 3)), ((0, 2), (0, 2), (0, 2), (2, 2))),
                ),
                requirements=(
                    (GriddedPerm(Perm((0,)), ((1, 2),)),),
                    (GriddedPerm(Perm((0,)), ((2, 2),)),),
                    (GriddedPerm(Perm((0,)), ((3, 0),)),),
                ),
                assumptions=(
                    TrackingAssumption(
                        (
                            GriddedPerm(Perm((0,)), ((2, 2),)),
                            GriddedPerm(Perm((0,)), ((3, 0),)),
                        )
                    ),
                ),
            )
        ),
        RequirementInsertionStrategy(
            gps=frozenset({GriddedPerm(Perm((0,)), ((0, 2),))}), ignore_parent=True
        )(
            Tiling(
                obstructions=(
                    GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
                    GriddedPerm(Perm((0, 1)), ((0, 1), (0, 2))),
                    GriddedPerm(Perm((0, 1)), ((0, 2), (0, 2))),
                    GriddedPerm(Perm((1, 0)), ((0, 1), (0, 0))),
                    GriddedPerm(Perm((1, 0)), ((0, 1), (0, 1))),
                    GriddedPerm(Perm((1, 0)), ((0, 2), (0, 0))),
                    GriddedPerm(Perm((1, 0)), ((0, 2), (0, 1))),
                    GriddedPerm(Perm((1, 0)), ((0, 2), (0, 2))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 1))),
                    GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 2))),
                    GriddedPerm(Perm((0, 2, 1)), ((0, 0), (0, 0), (0, 0))),
                    GriddedPerm(Perm((1, 2, 0)), ((0, 0), (0, 0), (0, 0))),
                ),
                requirements=((GriddedPerm(Perm((0,)), ((0, 1),)),),),
                assumptions=(
                    TrackingAssumption((GriddedPerm(Perm((0,)), ((0, 2),)),)),
                ),
            )
        )
        .to_equivalence_rule()
        .to_reverse_rule(),
    ]


def test_sanity_check_rules(rules_to_check):
    for rule in rules_to_check:
        print(rule)
        for n in range(6):
            for parameters in rule.comb_class.possible_parameters(n):
                assert rule.sanity_check(n, **parameters)

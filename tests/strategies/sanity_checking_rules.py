from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.strategies.requirement_insertion import RequirementInsertionStrategy
from tilings.assumptions import TrackingAssumption


@pytest.fixture
def single_variable():
    return []


@ptyest.fixture
def multi_variable():
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
        )
    ]


def test_single_variable(single_variable):
    for rule in single_variable:
        for i in range(6):
            rule.sanity_check(i)


@pytest.mark.xfail(reason="mutli variable sanity check not implemented")
def test_multi_variable(multi_variable):
    for rule in multi_variable:
        for i in range(6):
            rule.sanity_check(i)

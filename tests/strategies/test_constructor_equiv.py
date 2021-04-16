from tilings import GriddedPerm, Tiling, TrackingAssumption
from tilings.strategies.factor import FactorStrategy
from tilings.strategies.fusion import FusionStrategy
from tilings.strategies.requirement_placement import RequirementPlacementStrategy


def test_fusion_constructor_equiv():
    _tilings = [
        Tiling(
            obstructions=(
                GriddedPerm((1, 0), ((1, 0), (1, 0))),
                GriddedPerm((1, 0), ((1, 0), (2, 0))),
                GriddedPerm((1, 0), ((2, 0), (2, 0))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 2, 1), ((0, 0), (0, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),),
        ),
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
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
        ),
    ]
    constr1 = FusionStrategy(None, 1, True)(_tilings[0]).constructor
    constr2 = FusionStrategy(None, 0, True)(_tilings[1]).constructor

    are_equiv, reverse = constr1.equiv(constr2)
    assert are_equiv
    assert reverse
    are_equiv, reverse = constr1.equiv(constr1)
    assert are_equiv
    assert not reverse
    are_equiv, reverse = constr2.equiv(constr2)
    assert are_equiv
    assert not reverse

    _tilings = [
        Tiling(
            obstructions=(
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
        ),
        Tiling(
            obstructions=(
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (2, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (2, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),),
        ),
    ]
    constr1 = FusionStrategy(None, 0, True)(_tilings[0]).constructor
    constr2 = FusionStrategy(None, 1, True)(_tilings[1]).constructor

    are_equiv, reverse = constr1.equiv(constr2)
    assert are_equiv
    assert reverse
    are_equiv, reverse = constr1.equiv(constr1)
    assert are_equiv
    assert not reverse
    are_equiv, reverse = constr2.equiv(constr2)
    assert are_equiv
    assert not reverse

    _tilings = [
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((0, 0), (1, 0))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((2, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
            ),
            requirements=(),
            assumptions=(
                TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),
                TrackingAssumption(
                    (GriddedPerm((0,), ((1, 0),)), GriddedPerm((0,), ((2, 0),)))
                ),
            ),
        ),
        Tiling(
            obstructions=(
                GriddedPerm((1, 0), ((2, 0), (2, 0))),
                GriddedPerm((1, 0), ((2, 0), (3, 0))),
                GriddedPerm((1, 0), ((3, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (3, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (2, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (3, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (3, 0))),
            ),
            requirements=(),
            assumptions=(
                TrackingAssumption(
                    (GriddedPerm((0,), ((1, 0),)), GriddedPerm((0,), ((2, 0),)))
                ),
                TrackingAssumption((GriddedPerm((0,), ((3, 0),)),)),
            ),
        ),
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((2, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
            ),
            requirements=(),
            assumptions=(
                TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),
                TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),
            ),
        ),
        Tiling(
            obstructions=(
                GriddedPerm((1, 0), ((3, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (2, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (3, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (2, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (3, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (3, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (2, 0), (3, 0))),
            ),
            requirements=(),
            assumptions=(
                TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),
                TrackingAssumption((GriddedPerm((0,), ((3, 0),)),)),
            ),
        ),
    ]
    constr1 = FusionStrategy(None, 0, True)(_tilings[0]).constructor
    constr2 = FusionStrategy(None, 2, True)(_tilings[1]).constructor
    constr3 = FusionStrategy(None, 1, True)(_tilings[2]).constructor
    constr4 = FusionStrategy(None, 1, True)(_tilings[3]).constructor

    are_equiv, reverse = constr1.equiv(constr2)
    assert are_equiv
    assert reverse
    are_equiv, reverse = constr1.equiv(constr1)
    assert are_equiv
    assert not reverse
    are_equiv, reverse = constr2.equiv(constr2)
    assert are_equiv
    assert not reverse

    are_equiv, reverse = constr3.equiv(constr4)
    assert are_equiv
    assert reverse
    are_equiv, reverse = constr3.equiv(constr3)
    assert are_equiv
    assert not reverse
    are_equiv, reverse = constr4.equiv(constr4)
    assert are_equiv
    assert not reverse

    assert not constr1.equiv(constr3)[0]
    assert not constr1.equiv(constr4)[0]
    assert not constr2.equiv(constr3)[0]
    assert not constr2.equiv(constr3)[0]


def test_factor_equiv_with_assumptions():
    assert FactorStrategy((((0, 0), (2, 0), (3, 0)), ((1, 1),)))(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((1, 1), (1, 1))),
                GriddedPerm((1, 0), ((1, 1), (1, 1))),
                GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((2, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
            ),
            requirements=((GriddedPerm((0,), ((1, 1),)),),),
            assumptions=(
                TrackingAssumption(
                    (
                        GriddedPerm((0,), ((0, 0),)),
                        GriddedPerm((0,), ((1, 1),)),
                        GriddedPerm((0,), ((2, 0),)),
                    )
                ),
            ),
        )
    ).constructor.equiv(
        FactorStrategy((((0, 1), (1, 1), (3, 1)), ((2, 0),)))(
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((2, 0), (2, 0))),
                    GriddedPerm((1, 0), ((2, 0), (2, 0))),
                    GriddedPerm((1, 0), ((3, 1), (3, 1))),
                    GriddedPerm((0, 2, 1), ((1, 1), (1, 1), (1, 1))),
                    GriddedPerm((0, 2, 1), ((1, 1), (1, 1), (3, 1))),
                    GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
                    GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (1, 1))),
                    GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (3, 1))),
                    GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (1, 1), (1, 1))),
                    GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (1, 1), (3, 1))),
                ),
                requirements=((GriddedPerm((0,), ((2, 0),)),),),
                assumptions=(
                    TrackingAssumption(
                        (
                            GriddedPerm((0,), ((1, 1),)),
                            GriddedPerm((0,), ((2, 0),)),
                            GriddedPerm((0,), ((3, 1),)),
                        )
                    ),
                ),
            )
        ).constructor
    )[
        0
    ]
    assert not FactorStrategy((((0, 0), (1, 0), (3, 0)), ((2, 1),)))(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((2, 1), (2, 1))),
                GriddedPerm((1, 0), ((2, 1), (2, 1))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
            ),
            requirements=((GriddedPerm((0,), ((2, 1),)),),),
            assumptions=(TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),),
        )
    ).constructor.equiv(
        FactorStrategy((((0, 1), (1, 1), (3, 1)), ((2, 0),)))(
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((2, 0), (2, 0))),
                    GriddedPerm((1, 0), ((2, 0), (2, 0))),
                    GriddedPerm((1, 0), ((3, 1), (3, 1))),
                    GriddedPerm((0, 2, 1), ((1, 1), (1, 1), (1, 1))),
                    GriddedPerm((0, 2, 1), ((1, 1), (1, 1), (3, 1))),
                    GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
                    GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (1, 1))),
                    GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (0, 1), (3, 1))),
                    GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (1, 1), (1, 1))),
                    GriddedPerm((0, 1, 3, 2), ((0, 1), (0, 1), (1, 1), (3, 1))),
                ),
                requirements=((GriddedPerm((0,), ((2, 0),)),),),
                assumptions=(
                    TrackingAssumption(
                        (
                            GriddedPerm((0,), ((1, 1),)),
                            GriddedPerm((0,), ((2, 0),)),
                            GriddedPerm((0,), ((3, 1),)),
                        )
                    ),
                ),
            )
        ).constructor
    )[
        0
    ]


def test_req_placement_equiv_with_assumptions():
    constr = RequirementPlacementStrategy(
        (
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((2, 0),)),
            GriddedPerm((0,), ((1, 0),)),
        ),
        (0, 0, 0),
        1,
        include_empty=True,
    )(
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(
                TrackingAssumption((GriddedPerm((0,), ((0, 0),)),)),
                TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),
            ),
        )
    ).constructor
    assert constr.equiv(
        RequirementPlacementStrategy(
            (
                GriddedPerm((0,), ((0, 0),)),
                GriddedPerm((0,), ((2, 0),)),
                GriddedPerm((0,), ((1, 0),)),
            ),
            (0, 0, 0),
            3,
            include_empty=True,
        )(
            Tiling(
                obstructions=(
                    GriddedPerm((1, 0), ((2, 0), (2, 0))),
                    GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                    GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (2, 0))),
                    GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
                    GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (1, 0))),
                    GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (2, 0))),
                    GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (1, 0))),
                    GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (2, 0))),
                ),
                requirements=(),
                assumptions=(
                    TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),
                    TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),
                ),
            )
        ).constructor
    )[0]
    assert not constr.equiv(
        RequirementPlacementStrategy(
            (GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))),
            (0, 0),
            3,
            include_empty=True,
        )(
            Tiling(
                obstructions=(
                    GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                    GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
                    GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (1, 0))),
                    GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (1, 0))),
                ),
                requirements=(),
                assumptions=(TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),),
            )
        ).constructor
    )[0]
    assert not constr.equiv(
        RequirementPlacementStrategy(
            (
                GriddedPerm((0,), ((0, 0),)),
                GriddedPerm((0,), ((2, 0),)),
                GriddedPerm((0,), ((1, 0),)),
            ),
            (0, 0, 0),
            3,
            include_empty=True,
        )(
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                    GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
                    GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (1, 0))),
                    GriddedPerm((1, 2, 0), ((0, 0), (1, 0), (1, 0))),
                    GriddedPerm((1, 2, 0), ((1, 0), (2, 0), (2, 0))),
                    GriddedPerm((1, 2, 0), ((2, 0), (2, 0), (2, 0))),
                    GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 0), (2, 0))),
                    GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
                    GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (2, 0), (2, 0))),
                    GriddedPerm((0, 3, 1, 2), ((0, 0), (1, 0), (1, 0), (2, 0))),
                    GriddedPerm((0, 3, 1, 2), ((0, 0), (1, 0), (2, 0), (2, 0))),
                    GriddedPerm((0, 3, 1, 2), ((0, 0), (2, 0), (2, 0), (2, 0))),
                    GriddedPerm((0, 3, 1, 2), ((1, 0), (2, 0), (2, 0), (2, 0))),
                    GriddedPerm((2, 3, 1, 0), ((0, 0), (0, 0), (2, 0), (2, 0))),
                    GriddedPerm((2, 3, 1, 0), ((0, 0), (1, 0), (2, 0), (2, 0))),
                    GriddedPerm((2, 3, 1, 0), ((0, 0), (2, 0), (2, 0), (2, 0))),
                    GriddedPerm((3, 0, 2, 1), ((0, 0), (0, 0), (1, 0), (1, 0))),
                    GriddedPerm((3, 0, 2, 1), ((0, 0), (0, 0), (1, 0), (2, 0))),
                    GriddedPerm((3, 0, 2, 1), ((0, 0), (0, 0), (2, 0), (2, 0))),
                    GriddedPerm((3, 0, 2, 1), ((0, 0), (1, 0), (2, 0), (2, 0))),
                    GriddedPerm((3, 0, 2, 1), ((1, 0), (1, 0), (2, 0), (2, 0))),
                    GriddedPerm((3, 2, 0, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
                    GriddedPerm((3, 2, 0, 1), ((0, 0), (0, 0), (0, 0), (1, 0))),
                    GriddedPerm(
                        (1, 0, 4, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0))
                    ),
                    GriddedPerm(
                        (1, 0, 4, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 0), (1, 0))
                    ),
                    GriddedPerm(
                        (1, 0, 4, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (1, 0, 4, 2, 3), ((0, 0), (0, 0), (0, 0), (1, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (1, 0, 4, 2, 3), ((0, 0), (0, 0), (0, 0), (2, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (1, 0, 4, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (4, 1, 0, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0))
                    ),
                    GriddedPerm(
                        (4, 1, 0, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0), (1, 0))
                    ),
                    GriddedPerm(
                        (4, 1, 0, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (4, 1, 0, 3, 2), ((0, 0), (2, 0), (2, 0), (2, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (4, 1, 0, 3, 2), ((1, 0), (2, 0), (2, 0), (2, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (4, 1, 0, 3, 2), ((2, 0), (2, 0), (2, 0), (2, 0), (2, 0))
                    ),
                    GriddedPerm(
                        (4, 3, 1, 2, 0), ((0, 0), (0, 0), (0, 0), (2, 0), (2, 0))
                    ),
                ),
                requirements=(),
                assumptions=(TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),),
            )
        ).constructor
    )[0]

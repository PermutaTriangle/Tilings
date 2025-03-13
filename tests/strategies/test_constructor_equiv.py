import pytest

from comb_spec_searcher.strategies.rule import EquivalencePathRule
from tilings import GriddedPerm, Tiling, TrackingAssumption
from tilings.bijections import _TermCacher
from tilings.strategies.factor import FactorStrategy
from tilings.strategies.fusion import FusionStrategy
from tilings.strategies.obstruction_inferral import ObstructionInferralFactory
from tilings.strategies.requirement_placement import RequirementPlacementStrategy


def test_fusion_constructor_equiv():
    _term_cacher = _TermCacher()
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
    terms1 = _term_cacher.get_term_function_from_tiling(_tilings[0])
    terms2 = _term_cacher.get_term_function_from_tiling(_tilings[1])

    are_equiv, reverse = constr1.equiv(constr2, (terms1, terms2, 5))
    assert are_equiv
    assert len(reverse) == 1
    assert reverse[0]
    are_equiv, reverse = constr1.equiv(constr1, (terms1, terms1, 5))
    assert are_equiv
    assert len(reverse) == 1
    assert not reverse[0]
    are_equiv, reverse = constr2.equiv(constr2, (terms2, terms2, 5))
    assert are_equiv
    assert len(reverse) == 1
    assert not reverse[0]

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
    terms1 = _term_cacher.get_term_function_from_tiling(_tilings[0])
    terms2 = _term_cacher.get_term_function_from_tiling(_tilings[1])

    are_equiv, reverse = constr1.equiv(constr2, (terms1, terms2, 5))
    assert are_equiv
    assert len(reverse) == 1
    assert reverse[0]
    are_equiv, reverse = constr1.equiv(constr1, (terms1, terms1, 5))
    assert are_equiv
    assert len(reverse) == 1
    assert not reverse[0]
    are_equiv, reverse = constr2.equiv(constr2, (terms2, terms2, 5))
    assert are_equiv
    assert len(reverse) == 1
    assert not reverse[0]

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
    terms1 = _term_cacher.get_term_function_from_tiling(_tilings[0])
    terms2 = _term_cacher.get_term_function_from_tiling(_tilings[1])
    terms3 = _term_cacher.get_term_function_from_tiling(_tilings[2])
    terms4 = _term_cacher.get_term_function_from_tiling(_tilings[3])

    are_equiv, reverse = constr1.equiv(constr2, (terms1, terms2, 5))
    assert are_equiv
    assert len(reverse) == 1
    assert reverse[0]
    are_equiv, reverse = constr1.equiv(constr1, (terms1, terms1, 5))
    assert are_equiv
    assert len(reverse) == 1
    assert not reverse[0]
    are_equiv, reverse = constr2.equiv(constr2, (terms2, terms2, 5))
    assert are_equiv
    assert len(reverse) == 1
    assert not reverse[0]

    are_equiv, reverse = constr3.equiv(constr4, (terms3, terms4, 5))
    assert are_equiv
    assert len(reverse) == 1
    assert reverse[0]
    are_equiv, reverse = constr3.equiv(constr3, (terms3, terms3, 5))
    assert are_equiv
    assert len(reverse) == 1
    assert not reverse[0]
    are_equiv, reverse = constr4.equiv(constr4, (terms4, terms4, 5))
    assert are_equiv
    assert len(reverse) == 1
    assert not reverse[0]

    assert not constr1.equiv(constr3, (terms1, terms3, 5))[0]
    assert not constr1.equiv(constr4, (terms1, terms4, 5))[0]
    assert not constr2.equiv(constr3, (terms2, terms3, 5))[0]

    _tilings = [
        Tiling(
            obstructions=(
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (3, 0), (3, 0))),
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
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (2, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((2, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 2, 1), ((3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (2, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (3, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (1, 0), (3, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (2, 0), (3, 0))),
                GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (3, 0), (3, 0))),
            ),
            requirements=(),
            assumptions=(
                TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),
                TrackingAssumption((GriddedPerm((0,), ((3, 0),)),)),
            ),
        ),
    ]
    terms1 = _term_cacher.get_term_function_from_tiling(_tilings[0])
    terms2 = _term_cacher.get_term_function_from_tiling(_tilings[1])
    are_equiv, reverse = FusionStrategy(row_idx=None, col_idx=0, tracked=True)(
        _tilings[0]
    ).constructor.equiv(
        FusionStrategy(row_idx=None, col_idx=2, tracked=True)(_tilings[1]).constructor,
        (terms1, terms2, 5),
    )
    assert are_equiv
    assert len(reverse) == 2
    assert True in reverse and False in reverse

    _tilings = [
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
                TrackingAssumption((GriddedPerm((0,), ((1, 0),)),)),
                TrackingAssumption((GriddedPerm((0,), ((3, 0),)),)),
            ),
        ),
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
                TrackingAssumption((GriddedPerm((0,), ((2, 0),)),)),
            ),
        ),
    ]
    terms1 = _term_cacher.get_term_function_from_tiling(_tilings[0])
    terms2 = _term_cacher.get_term_function_from_tiling(_tilings[1])
    assert not FusionStrategy(row_idx=None, col_idx=1, tracked=True)(
        _tilings[0]
    ).constructor.equiv(
        FusionStrategy(row_idx=None, col_idx=0, tracked=True)(_tilings[1]).constructor,
        (terms1, terms2, 5),
    )[
        0
    ]


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


def test_complement_multiple_params():
    t = Tiling(
        [
            GriddedPerm.single_cell((0, 1, 2), (0, 0)),
            GriddedPerm.single_cell((0, 1, 2), (1, 0)),
            GriddedPerm((0, 1), ((0, 0), (1, 0))),
            GriddedPerm((1, 0), ((0, 0), (1, 0))),
        ],
        [[GriddedPerm.point_perm((0, 0))]],
        [
            TrackingAssumption.from_cells([(0, 0), (1, 0)]),
            TrackingAssumption.from_cells([(0, 0)]),
        ],
    )
    for strategy in ObstructionInferralFactory()(t):
        rule = strategy(t)
        print(rule)
        print(rule.to_reverse_rule(0))
        assert not rule.to_reverse_rule(0).is_equivalence()
        with pytest.raises(AssertionError):
            EquivalencePathRule([rule.to_reverse_rule(0)])

        for i in range(4):
            assert rule.sanity_check(i)
            assert rule.to_reverse_rule(0).sanity_check(i)

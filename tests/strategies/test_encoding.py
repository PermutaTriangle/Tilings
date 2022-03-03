import json
import os
from itertools import product

import pytest

from comb_spec_searcher import Strategy
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import GriddedPerm, TrackingAssumption
from tilings.strategies import (
    AllPlacementsFactory,
    BasicVerificationStrategy,
    CellInsertionFactory,
    CellReductionFactory,
    ComponentFusionFactory,
    DatabaseVerificationStrategy,
    DeflationFactory,
    ElementaryVerificationStrategy,
    EmptyCellInferralFactory,
    FactorFactory,
    FactorInsertionFactory,
    FusionFactory,
    LocallyFactorableVerificationStrategy,
    LocalVerificationStrategy,
    MonotoneTreeVerificationStrategy,
    ObstructionInferralFactory,
    ObstructionTransitivityFactory,
    OneByOneVerificationStrategy,
    PatternPlacementFactory,
    PointJumpingFactory,
    RearrangeAssumptionFactory,
    RequirementCorroborationFactory,
    RequirementExtensionFactory,
    RequirementInsertionFactory,
    RequirementPlacementFactory,
    RootInsertionFactory,
    RowAndColumnPlacementFactory,
    RowColumnSeparationStrategy,
    ShortObstructionVerificationStrategy,
    SlidingFactory,
    SplittingStrategy,
    SubclassVerificationFactory,
    SubobstructionInferralFactory,
    SymmetriesFactory,
)
from tilings.strategies.cell_reduction import CellReductionStrategy
from tilings.strategies.deflation import DeflationStrategy
from tilings.strategies.experimental_verification import SubclassVerificationStrategy
from tilings.strategies.factor import (
    FactorStrategy,
    FactorWithInterleavingStrategy,
    FactorWithMonotoneInterleavingStrategy,
)
from tilings.strategies.fusion import ComponentFusionStrategy, FusionStrategy
from tilings.strategies.obstruction_inferral import ObstructionInferralStrategy
from tilings.strategies.point_jumping import PointJumpingStrategy
from tilings.strategies.rearrange_assumption import RearrangeAssumptionStrategy
from tilings.strategies.requirement_insertion import RequirementInsertionStrategy
from tilings.strategies.requirement_placement import RequirementPlacementStrategy
from tilings.strategies.sliding import SlidingStrategy


def assert_same_strategy(s1, s2):
    """Check that two strategy object describe the same strategy."""
    __tracebackhide__ = True
    if s1.__class__ != s2.__class__:
        pytest.fail(
            "The two strategies have different class\n"
            "First one is: {}\n Second one is: {}\n".format(s1.__class__, s2.__class__)
        )
    assert s1.__dict__ == s2.__dict__, "The attributes of the strategies differ"


def json_encode_decode(s):
    """Take a strategy, encode it as json and build it back as a strategy."""
    __tracebackhide__ = True
    d = s.to_jsonable()
    if not isinstance(d, dict):
        pytest.fail("to_jsonable does not return a dict. \n" "Returned: {}".format(d))
    try:
        json_str = json.dumps(d)
    except TypeError as e:
        pytest.fail(
            "The to_jsonable method returns a dictionnary that can "
            "not be encoded as json string\n"
            "Got error: {}".format(e)
        )
    s_new = Strategy.from_dict(json.loads(json_str))
    return s_new


def repr_encode_decode(strategy):
    """Take a strategy, encode it as repr and build it back as a strategy."""
    __tracebackhide__ = True

    repr_str = repr(strategy)
    if not isinstance(repr_str, str):
        pytest.fail(f"repr does not return a string.\nReturned: {repr_str}")
    try:
        new_strategy = eval(repr_str)
    except Exception as e:
        pytest.fail(
            "The repr method returns a string that can not be loaded back\n"
            f"Got error: {e}\n"
            f"The repr is: {repr_str}\n"
            f"The class is: {strategy.__class__}"
        )
    return new_strategy


def maxreqlen_extrabasis_ignoreparent(strategy):
    return [
        strategy(
            maxreqlen=maxreqlen, extra_basis=extra_basis, ignore_parent=ignore_parent
        )
        for maxreqlen, extra_basis, ignore_parent in product(
            (1, 2, 3),
            (None, [Perm((0, 1))], [Perm((0, 2, 1)), Perm((0, 1, 2))]),
            (True, False),
        )
    ]


def maxreqlen_extrabasis_ignoreparent_maxnumreq(strategy):
    return [
        strategy(
            maxreqlen=maxreqlen,
            extra_basis=extra_basis,
            ignore_parent=ignore_parent,
            max_num_req=max_num_req,
        )
        for maxreqlen, extra_basis, ignore_parent, max_num_req in product(
            (1, 2, 3),
            (None, [Perm((0, 1))], [Perm((0, 2, 1)), Perm((0, 1, 2))]),
            (True, False),
            (1, 2, 3, None),
        )
    ]


def maxreqlen_extrabasis_ignoreparent_one_cell_only(strategy):
    return [
        strategy(
            maxreqlen=maxreqlen,
            extra_basis=extra_basis,
            ignore_parent=ignore_parent,
            one_cell_only=one_cell_only,
        )
        for (maxreqlen, extra_basis, ignore_parent, one_cell_only,) in product(
            (1, 2, 3),
            (None, [Perm((0, 1))], [Perm((0, 2, 1)), Perm((0, 1, 2))]),
            (True, False),
            (True, False),
        )
    ]


def ignoreparent(strategy):
    return [strategy(ignore_parent=True), strategy(ignore_parent=False)]


def interleaving_unions_ignoreparent_workable(strategy):
    return [
        strategy(
            interleaving=interleaving,
            unions=unions,
            ignore_parent=ignore_parent,
            workable=workable,
        )
        for interleaving, unions, ignore_parent, workable in product(
            (None, "all", "monotone"),
            (True, False),
            (True, False),
            (True, False),
        )
    ]


def maxlen(strategy):
    return [strategy(maxlen=maxlen) for maxlen in (1, 2, 3)]


def subreqs_partial_ignoreparent_dirs(strategy):
    return [
        strategy(
            subreqs=subreqs, partial=partial, ignore_parent=ignore_parent, dirs=dirs
        )
        for subreqs, partial, ignore_parent, dirs in product(
            (True, False),
            (True, False),
            (True, False),
            ([DIR_SOUTH], [DIR_EAST, DIR_WEST], [DIR_NORTH, DIR_SOUTH], DIRS),
        )
    ]


def pointonly_partial_ignoreparent_dirs(strategy):
    return [
        strategy(
            point_only=point_only,
            partial=partial,
            ignore_parent=ignore_parent,
            dirs=dirs,
        )
        for point_only, partial, ignore_parent, dirs in product(
            (True, False),
            (True, False),
            (True, False),
            ([DIR_SOUTH], [DIR_EAST, DIR_WEST], [DIR_NORTH, DIR_SOUTH], DIRS),
        )
    ]


def partition_ignoreparent_workable(strategy):
    return [
        strategy(partition=partition, ignore_parent=ignore_parent, workable=workable)
        for partition, ignore_parent, workable in product(
            (
                [[(2, 1), (0, 1)], [(1, 0)]],
                (((0, 0), (0, 2)), ((0, 1),), ((3, 3), (4, 3))),
            ),
            (True, False),
            (True, False),
        )
    ]


def gps_ignoreparent(strategy):
    return [
        strategy(gps=gps, ignore_parent=ignore_parent)
        for gps, ignore_parent in product(
            (
                (GriddedPerm((0,), ((0, 0),)),),
                (GriddedPerm.single_cell((0, 1, 2), (2, 1)),),
                (
                    GriddedPerm((0, 1), ((0, 1), (1, 1))),
                    GriddedPerm((1, 0), ((2, 2), (3, 1))),
                ),
            ),
            (True, False),
        )
    ]


def gps_ignoreparent_limited(factory):
    return [
        factory(
            extra_basis=list(basis),
            ignore_parent=ignore_parent,
            limited_insertion=limited_insertion,
        )
        for basis, ignore_parent, limited_insertion in product(
            ((Perm((0,)),), (Perm((0, 1, 2)),), (Perm((0, 1)), Perm((1, 0)))),
            (True, False),
            (True, False),
        )
    ]


def gps_indices_direction_owncol_ownrow_ignoreparent_includeempty(strategy):
    return [
        strategy(
            gps=gps,
            indices=indices,
            direction=direction,
            own_col=own_col,
            own_row=own_row,
            ignore_parent=ignore_parent,
            include_empty=include_empty,
        )
        for (
            gps,
            indices,
        ), direction, own_col, own_row, ignore_parent, include_empty in product(
            (
                ((GriddedPerm((0,), ((0, 0),)),), (0,)),
                ((GriddedPerm.single_cell((0, 1, 2), (2, 1)),), (1,)),
                (
                    (
                        GriddedPerm((0, 1), ((0, 1), (1, 1))),
                        GriddedPerm((1, 0), ((2, 2), (3, 1))),
                    ),
                    (1, 0),
                ),
            ),
            (DIR_EAST, DIR_WEST, DIR_NORTH, DIR_SOUTH),
            (True, False),
            (True, False),
            (True, False),
            (True, False),
        )
    ]


def row_col_partial_ignoreparent_direction(strategy):
    return [
        strategy(
            place_row=place_row,
            place_col=place_col,
            partial=partial,
            ignore_parent=ignore_parent,
            dirs=dirs,
        )
        for place_row, place_col, partial, ignore_parent, dirs in product(
            (True, False),
            (True, False),
            (True, False),
            (True, False),
            ([DIR_SOUTH], [DIR_EAST, DIR_WEST], [DIR_NORTH, DIR_SOUTH], DIRS),
        )
        if place_row or place_col
    ]


def use_symmetries(strategy):
    return [strategy(use_symmetries=False), strategy(use_symmetries=True)]


def sliding_strategy_arguments(strategy):
    lis = [
        strategy(av_12=av_12, av_123=av_123, symmetry_type=symmetry_type)
        for av_12, av_123, symmetry_type in product((0, 2, 4), (1, 3, 5), (0, 1, 2, 3))
    ]
    return lis


def short_length_arguments(strategy):
    return [
        strategy(basis=basis, short_length=short_length, ignore_parent=ignore_parent)
        for short_length in range(4)
        for ignore_parent in (True, False)
        for basis in (
            None,
            (Perm((0, 1, 2)),),
            (Perm((0, 1, 2, 3)), Perm((0, 1, 3, 2))),
        )
    ]


def indices_and_row(strategy):
    return [
        strategy(idx1, idx2, row)
        for idx1 in range(3)
        for idx2 in range(3)
        for row in (True, False)
    ]


strategy_objects = (
    maxreqlen_extrabasis_ignoreparent_one_cell_only(CellInsertionFactory)
    + ignoreparent(FactorInsertionFactory)
    + interleaving_unions_ignoreparent_workable(FactorFactory)
    + maxlen(ObstructionInferralFactory)
    + ignoreparent(AllPlacementsFactory)
    + maxreqlen_extrabasis_ignoreparent(RequirementExtensionFactory)
    + maxreqlen_extrabasis_ignoreparent(RequirementInsertionFactory)
    + subreqs_partial_ignoreparent_dirs(RequirementPlacementFactory)
    + [SymmetriesFactory(), BasicVerificationStrategy(), EmptyCellInferralFactory()]
    + partition_ignoreparent_workable(FactorStrategy)
    + partition_ignoreparent_workable(FactorWithInterleavingStrategy)
    + partition_ignoreparent_workable(FactorWithMonotoneInterleavingStrategy)
    + ignoreparent(DatabaseVerificationStrategy)
    + ignoreparent(LocallyFactorableVerificationStrategy)
    + ignoreparent(ElementaryVerificationStrategy)
    + ignoreparent(LocalVerificationStrategy)
    + ignoreparent(MonotoneTreeVerificationStrategy)
    + [ObstructionTransitivityFactory()]
    + [
        OneByOneVerificationStrategy(
            basis=[Perm((0, 1, 2)), Perm((2, 1, 0, 3))], ignore_parent=True
        ),
        OneByOneVerificationStrategy(
            basis=[Perm((2, 1, 0, 3))], ignore_parent=False, symmetry=True
        ),
        OneByOneVerificationStrategy(basis=[], ignore_parent=False, symmetry=False),
        OneByOneVerificationStrategy(basis=None, ignore_parent=False, symmetry=False),
    ]
    + [
        SubclassVerificationFactory(perms_to_check=[Perm((0, 1, 2)), Perm((1, 0))]),
        SubclassVerificationFactory(perms_to_check=list(Perm.up_to_length(3))),
        SubclassVerificationStrategy(
            subclass_basis=[Perm((0, 1, 2)), Perm((1, 0))], ignore_parent=True
        ),
        SubclassVerificationStrategy(
            subclass_basis=list(Perm.up_to_length(3)), ignore_parent=False
        ),
    ]
    + pointonly_partial_ignoreparent_dirs(PatternPlacementFactory)
    + ignoreparent(RequirementCorroborationFactory)
    + gps_ignoreparent(RequirementInsertionStrategy)
    + gps_ignoreparent_limited(RequirementInsertionFactory)
    + gps_indices_direction_owncol_ownrow_ignoreparent_includeempty(
        RequirementPlacementStrategy
    )
    + maxreqlen_extrabasis_ignoreparent_maxnumreq(RootInsertionFactory)
    + row_col_partial_ignoreparent_direction(RowAndColumnPlacementFactory)
    + use_symmetries(SlidingFactory)
    + sliding_strategy_arguments(SlidingStrategy)
    + short_length_arguments(ShortObstructionVerificationStrategy)
    + [RowColumnSeparationStrategy(), SubobstructionInferralFactory()]
    + [FusionStrategy(row_idx=1)]
    + [FusionStrategy(col_idx=3)]
    + [ComponentFusionStrategy(row_idx=1)]
    + [ComponentFusionStrategy(col_idx=3)]
    + [ComponentFusionStrategy(col_idx=3)]
    + [FusionFactory(tracked=True), FusionFactory(tracked=False)]
    + [DeflationFactory(tracked=True), DeflationFactory(tracked=False)]
    + [CellReductionFactory(tracked=True), DeflationFactory(tracked=False)]
    + [
        CellReductionStrategy((0, 0), True, True),
        CellReductionStrategy((2, 1), True, False),
        CellReductionStrategy((3, 3), False, True),
        CellReductionStrategy((4, 1), False, False),
    ]
    + [
        DeflationStrategy((0, 0), True, True),
        DeflationStrategy((2, 1), True, False),
        DeflationStrategy((3, 3), False, True),
        DeflationStrategy((4, 1), False, False),
    ]
    + [ComponentFusionFactory()]
    + [ObstructionInferralStrategy([GriddedPerm((0, 1, 2), ((0, 0), (1, 1), (1, 2)))])]
    + [
        SplittingStrategy(),
        SplittingStrategy("none"),
        SplittingStrategy("monotone"),
        SplittingStrategy("all"),
    ]
    + [RearrangeAssumptionFactory()]
    + [
        RearrangeAssumptionStrategy(
            TrackingAssumption(
                [GriddedPerm((0,), [(0, 0)]), GriddedPerm((0,), [(1, 0)])]
            ),
            TrackingAssumption([GriddedPerm((0,), [(0, 0)])]),
        )
    ]
    + [PointJumpingFactory()]
    + indices_and_row(PointJumpingStrategy)
)

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, "old_rule_json.jsonl")) as fp:
    strategy_dicts = list(map(json.loads, fp.readlines()))


@pytest.mark.parametrize("strategy", strategy_objects)
def test_json_encoding(strategy):
    strategy_new = json_encode_decode(strategy)
    print(strategy)
    assert_same_strategy(strategy, strategy_new)


@pytest.mark.parametrize("strategy", strategy_objects)
def test_repr_encoding(strategy):
    strategy_new = repr_encode_decode(strategy)
    print(strategy)
    print(repr(strategy))
    print(strategy.to_jsonable())
    assert_same_strategy(strategy, strategy_new)


@pytest.mark.parametrize("strat_dict", strategy_dicts)
def test_old_json_compatibility(strat_dict):
    Strategy.from_dict(strat_dict)

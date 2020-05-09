import json
from itertools import product

import pytest

from comb_spec_searcher import Strategy
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import GriddedPerm
from tilings.strategies import (
    AllCellInsertionStrategy,
    AllFactorInsertionStrategy,
    AllFactorStrategy,
    AllObstructionInferralStrategy,
    AllPlacementsStrategy,
    AllRequirementExtensionStrategy,
    AllRequirementInsertionStrategy,
    AllRequirementPlacementStrategy,
    AllSymmetriesStrategy,
    BasicVerificationStrategy,
    ComponentFusionStrategy,
    ComponentFusionStrategyGenerator,
    DatabaseVerificationStrategy,
    ElementaryVerificationStrategy,
    EmptyCellInferralStrategy,
    FactorStrategy,
    FactorWithInterleavingStrategy,
    FactorWithMonotoneInterleavingStrategy,
    FusionStrategy,
    FusionStrategyGenerator,
    LocallyFactorableVerificationStrategy,
    LocalVerificationStrategy,
    MonotoneTreeVerificationStrategy,
    ObstructionTransitivityStrategy,
    OneByOneVerificationStrategy,
    PatternPlacementStrategy,
    RequirementCorroborationStrategy,
    RequirementInsertionStrategy,
    RequirementPlacementStrategy,
    RootInsertionStrategy,
    RowAndColumnPlacementStrategy,
    RowColumnSeparationStrategy,
    SubobstructionInferralStrategy,
)


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
            (None, "all", "monotone"), (True, False), (True, False), (True, False),
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
                (GriddedPerm(Perm((0,)), ((0, 0),)),),
                (GriddedPerm.single_cell(Perm((0, 1, 2)), (2, 1)),),
                (
                    GriddedPerm(Perm((0, 1)), ((0, 1), (1, 1))),
                    GriddedPerm(Perm((1, 0)), ((2, 2), (3, 1))),
                ),
            ),
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
                ((GriddedPerm(Perm((0,)), ((0, 0),)),), (0,)),
                ((GriddedPerm.single_cell(Perm((0, 1, 2)), (2, 1)),), (1,)),
                (
                    (
                        GriddedPerm(Perm((0, 1)), ((0, 1), (1, 1))),
                        GriddedPerm(Perm((1, 0)), ((2, 2), (3, 1))),
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


strategy_objects = (
    maxreqlen_extrabasis_ignoreparent(AllCellInsertionStrategy)
    + ignoreparent(AllFactorInsertionStrategy)
    + interleaving_unions_ignoreparent_workable(AllFactorStrategy)
    + maxlen(AllObstructionInferralStrategy)
    + ignoreparent(AllPlacementsStrategy)
    + maxreqlen_extrabasis_ignoreparent(AllRequirementExtensionStrategy)
    + maxreqlen_extrabasis_ignoreparent(AllRequirementInsertionStrategy)
    + subreqs_partial_ignoreparent_dirs(AllRequirementPlacementStrategy)
    + [
        AllSymmetriesStrategy(),
        BasicVerificationStrategy(),
        EmptyCellInferralStrategy(),
    ]
    + partition_ignoreparent_workable(FactorStrategy)
    + partition_ignoreparent_workable(FactorWithInterleavingStrategy)
    + partition_ignoreparent_workable(FactorWithMonotoneInterleavingStrategy)
    + ignoreparent(DatabaseVerificationStrategy)
    + ignoreparent(LocallyFactorableVerificationStrategy)
    + ignoreparent(ElementaryVerificationStrategy)
    + ignoreparent(LocalVerificationStrategy)
    + ignoreparent(MonotoneTreeVerificationStrategy)
    + [ObstructionTransitivityStrategy()]
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
    + pointonly_partial_ignoreparent_dirs(PatternPlacementStrategy)
    + ignoreparent(RequirementCorroborationStrategy)
    + gps_ignoreparent(RequirementInsertionStrategy)
    + gps_indices_direction_owncol_ownrow_ignoreparent_includeempty(
        RequirementPlacementStrategy
    )
    + maxreqlen_extrabasis_ignoreparent_maxnumreq(RootInsertionStrategy)
    + row_col_partial_ignoreparent_direction(RowAndColumnPlacementStrategy)
    + [RowColumnSeparationStrategy(), SubobstructionInferralStrategy()]
)

# TODO add tests for: ComponentFusionStrategy, FusionStrategy


@pytest.mark.parametrize("strategy", strategy_objects)
def test_json_encoding(strategy):
    strategy_new = json_encode_decode(strategy)
    print(strategy)
    assert_same_strategy(strategy, strategy_new)

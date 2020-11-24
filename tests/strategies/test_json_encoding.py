import json
from itertools import product

import pytest

from comb_spec_searcher import Strategy
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Sliding
from tilings.strategies import (
    AllPlacementsFactory,
    BasicVerificationStrategy,
    CellInsertionFactory,
    ComponentFusionFactory,
    DatabaseVerificationStrategy,
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
from tilings.strategies.experimental_verification import SubclassVerificationStrategy
from tilings.strategies.factor import (
    FactorStrategy,
    FactorWithInterleavingStrategy,
    FactorWithMonotoneInterleavingStrategy,
)
from tilings.strategies.fusion import ComponentFusionStrategy, FusionStrategy
from tilings.strategies.obstruction_inferral import ObstructionInferralStrategy
from tilings.strategies.requirement_insertion import RequirementInsertionStrategy
from tilings.strategies.requirement_placement import RequirementPlacementStrategy
from tilings.strategies.sliding import SlidingStrategy, _AdditionalMaps


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
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
        ),
        requirements=(),
        assumptions=(),
    )
    lis = [
        strategy(
            av_12_column=av_12_column,
            av_123_column=av_123_column,
            sliding=sliding,
            maps=maps,
        )
        for av_12_column, av_123_column, sliding, maps in product(
            (1,), (0, 2), (Sliding(t),), (_AdditionalMaps(),)
        )
    ]
    return lis


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
    + [RowColumnSeparationStrategy(), SubobstructionInferralFactory()]
    + [FusionStrategy(row_idx=1)]
    + [FusionStrategy(col_idx=3)]
    + [ComponentFusionStrategy(row_idx=1)]
    + [ComponentFusionStrategy(col_idx=3)]
    + [ComponentFusionStrategy(col_idx=3)]
    + [FusionFactory()]
    + [ComponentFusionFactory()]
    + [ObstructionInferralStrategy([GriddedPerm((0, 1, 2), ((0, 0), (1, 1), (1, 2)))])]
    + [
        SplittingStrategy(),
        SplittingStrategy("none"),
        SplittingStrategy("monotone"),
        SplittingStrategy("all"),
    ]
    + [ShortObstructionVerificationStrategy()]
)

# TODO add tests for: ComponentFusionStrategy, FusionStrategy


@pytest.mark.parametrize("strategy", strategy_objects)
def test_json_encoding(strategy):
    strategy_new = json_encode_decode(strategy)
    print(strategy)
    assert_same_strategy(strategy, strategy_new)

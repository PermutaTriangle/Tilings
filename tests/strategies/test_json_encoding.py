import json

import pytest

from permuta import Perm
from comb_spec_searcher import Strategy
from tilings.strategies import (
    AllCellInsertionStrategy,
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
    DatabaseVerificationStrategy,
    ElementaryVerificationStrategy,
    EmptyCellInferralStrategy,
    LocallyFactorableVerificationStrategy,
    LocalVerificationStrategy,
    MonotoneTreeVerificationStrategy,
    ObstructionTransitivityStrategy,
    OneByOneVerificationStrategy,
    PatternPlacementStrategy,
    RequirementCorroborationStrategy,
    RequirementInsertionStrategy,
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
            "First one is: {}\n Second one is: {}\n".format(s1.__class__, s2.__class)
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


strategy_objects = [
    # Batch strategies
    AllCellInsertionStrategy(),
    AllCellInsertionStrategy(1, [Perm((0, 1, 2))], ignore_parent=True),
    AllFactorInsertionStrategy(),
    AllPlacementsStrategy(),
    AllRequirementExtensionStrategy(),
    AllRequirementExtensionStrategy(maxreqlen=4),
    AllRequirementInsertionStrategy(),
    RequirementCorroborationStrategy(),
    RootInsertionStrategy(),
    RootInsertionStrategy(max_num_req=3, maxreqlen=4),
    RowAndColumnPlacementStrategy(place_col=True, place_row=True),
    RowAndColumnPlacementStrategy(place_col=True, place_row=True, partial=False),
    RowAndColumnPlacementStrategy(place_col=False, place_row=True),
    # Inferral strategies
    EmptyCellInferralStrategy(),
    ObstructionTransitivityStrategy(),
    RowColumnSeparationStrategy(),
    SubobstructionInferralStrategy(),
    # Decomposition strategies
    AllFactorStrategy(),
    AllFactorStrategy(interleaving="all"),
    AllFactorStrategy(interleaving="monotone", unions=True),
    AllFactorStrategy(interleaving=None, unions=True, workable=False),
    # # Fusion strategies
    # FusionStrategy(),
    # ComponentFusionStrategy(),
    # Verification strategies
    BasicVerificationStrategy(),
    DatabaseVerificationStrategy(),
    ElementaryVerificationStrategy(),
    LocallyFactorableVerificationStrategy(),
    LocalVerificationStrategy(),
    MonotoneTreeVerificationStrategy(),
    OneByOneVerificationStrategy(),
    # Equivalent Strategy
    PatternPlacementStrategy(),
    PatternPlacementStrategy(ignore_parent=True),
    PatternPlacementStrategy(ignore_parent=False),
    PatternPlacementStrategy(point_only=True),
    PatternPlacementStrategy(point_only=False),
    PatternPlacementStrategy(partial=True),
    PatternPlacementStrategy(partial=False),
    PatternPlacementStrategy(dirs=[1, 3, 0]),
]


@pytest.mark.parametrize("strategy", strategy_objects)
def test_json_encoding(strategy):
    strategy_new = json_encode_decode(strategy)
    assert_same_strategy(strategy, strategy_new)

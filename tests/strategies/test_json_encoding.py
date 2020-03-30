import json

import pytest

from permuta import Perm
from tilings.strategies.abstract_strategy import Strategy
from tilings.strategies.batch import (AllCellInsertionStrategy,
                                      AllFactorInsertionStrategy,
                                      AllPlacementsStrategy,
                                      AllRequirementExtensionStrategy,
                                      AllRequirementInsertionStrategy,
                                      RequirementCorroborationStrategy,
                                      RootInsertionStrategy,
                                      RowAndColumnPlacementStrategy)
from tilings.strategies.decomposition import FactorStrategy
from tilings.strategies.equivalence import RequirementPlacementStrategy
from tilings.strategies.fusion import ComponentFusionStrategy, FusionStrategy
from tilings.strategies.inferral import (EmptyCellInferralStrategy,
                                         ObstructionTransitivityStrategy,
                                         RowColumnSeparationStrategy,
                                         SubobstructionInferralStrategy)
from tilings.strategies.verification import (
    BasicVerificationStrategy, DatabaseVerificationStrategy,
    ElementaryVerificationStrategy, LocallyFactorableVerificationStrategy,
    LocalVerificationStrategy, OneByOneVerificationStrategy)


def assert_same_strategy(s1, s2):
    """Check that two strategy object describe the same strategy."""
    __tracebackhide__ = True
    if s1.__class__ != s2.__class__:
        pytest.fail('The two strategies have different class\n'
                    'First one is: {}\n Second one is: {}\n'
                    .format(s1.__class__, s2.__class))
    assert (
        s1.__dict__ == s2.__dict__
    ), 'The attributes of the strategies differ'


def json_encode_decode(s):
    """Take a strategy, encode it as json and build it back as a strategy."""
    __tracebackhide__ = True
    d = s.to_jsonable()
    if not isinstance(d, dict):
        pytest.fail('to_jsonable does not return a dict. \n'
                    'Returned: {}'.format(d))
    try:
        json_str = json.dumps(d)
    except TypeError as e:
        pytest.fail('The to_jsonable method returns a dictionnary that can '
                    'not be encoded as json string\n'
                    'Got error: {}'.format(e))
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
    RowAndColumnPlacementStrategy(place_col=True, place_row=True,
                                  partial=False),
    RowAndColumnPlacementStrategy(place_col=False, place_row=True),

    # Inferral strategies
    EmptyCellInferralStrategy(),
    ObstructionTransitivityStrategy(),
    RowColumnSeparationStrategy(),
    SubobstructionInferralStrategy(),

    # Decomposition strategies
    FactorStrategy(),
    FactorStrategy(interleaving='all'),
    FactorStrategy(interleaving='monotone', union=True),
    FactorStrategy(interleaving=None, union=True, workable=False),

    # Fusion strategies
    FusionStrategy(),
    ComponentFusionStrategy(),

    # Verification strategies
    BasicVerificationStrategy(),
    DatabaseVerificationStrategy(),
    ElementaryVerificationStrategy(),
    LocallyFactorableVerificationStrategy(),
    LocalVerificationStrategy(),
    OneByOneVerificationStrategy(),

    # Equivalent Strategy
    RequirementPlacementStrategy(),
    RequirementPlacementStrategy(ignore_parent=True),
    RequirementPlacementStrategy(ignore_parent=False),
    RequirementPlacementStrategy(point_only=True),
    RequirementPlacementStrategy(point_only=False),
    RequirementPlacementStrategy(partial=True),
    RequirementPlacementStrategy(partial=False),
    RequirementPlacementStrategy(dirs=[1, 3, 0]),
]


@pytest.mark.parametrize("strategy", strategy_objects)
def test_json_encoding(strategy):
    strategy_new = json_encode_decode(strategy)
    assert_same_strategy(strategy, strategy_new)

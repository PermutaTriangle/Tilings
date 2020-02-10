from typing import Optional

from comb_spec_searcher import Rule
from tilings import Tiling
from tilings.algorithms import (EmptyCellInferral, ObstructionTransitivity,
                                RowColSeparation, SubobstructionInferral)
from tilings.strategies.abstract_strategy import Strategy


class ObstructionTransitivityStrategy(Strategy):
    """
    The obstruction transitivity strategy.

    The obstruction transitivity considers all length 2 obstructions with both
    points in the same row or some column. By considering these length 2
    obstructions in similar manner as the row and column separation, as
    inequality relations. When the obstructions use a positive cell,
    transitivity applies, i.e. if a < b < c and b is positive, then a < c.
    """
    def __call__(self, tiling: Tiling) -> Optional[Rule]:
        return ObstructionTransitivity(tiling).rule()

    def __str__(self) -> str:
        return 'obstruction transitivity'

    def to_json(self) -> dict:
        return {
            'class_module': 'tilings.algorithms.inferral',
            'strategy_class': 'ObstructionTransitivityStrategy',
        }

    @classmethod
    def from_json(cls, d: dict) -> 'ObstructionTransitivityStrategy':
        return cls()


class RowColumnSeparationStrategy(Strategy):
    """
    An inferral function that tries to separate cells in rows and columns.
    """
    def __call__(self, tiling: Tiling) -> Optional[Rule]:
        rcs = RowColSeparation(tiling)
        return rcs.rule()

    def __str__(self) -> str:
        return 'row and column separation'

    def to_json(self) -> dict:
        return {
            'class_module': 'tilings.algorithms.inferral',
            'strategy_class': 'RowColumnSeparationStrategy',
        }

    @classmethod
    def from_json(cls, d: dict) -> 'RowColumnSeparationStrategy':
        return cls()


class EmptyCellInferralStrategy(Strategy):
    """
    The empty cell inferral strategy.

    The strategy considers each active but non-positive cell and inserts a
    point requirement. If the resulting tiling is empty, then a point
    obstruction can be added into the cell, i.e. the cell is empty.
    """
    def __call__(self, tiling: Tiling) -> Optional[Rule]:
        return EmptyCellInferral(tiling).rule()

    def __str__(self) -> str:
        return 'empty cell inferral'

    def to_json(self) -> dict:
        return {
            'class_module': 'tilings.algorithms.inferral',
            'strategy_class': 'EmptyCellInferralStrategy',
        }

    @classmethod
    def from_json(cls, d: dict) -> 'EmptyCellInferralStrategy':
        return cls()


class SubobstructionInferralStrategy(Strategy):
    """
    Return tiling created by adding all subobstructions which can be
    added.
    """
    def __call__(self, tiling: Tiling) -> Optional[Rule]:
        return SubobstructionInferral(tiling).rule()

    def __str__(self) -> str:
        return 'subobstruction inferral'

    def to_json(self) -> dict:
        return {
            'class_module': 'tilings.algorithms.inferral',
            'strategy_class': 'SubobstructionInferralStrategy',
        }

    @classmethod
    def from_json(cls, d: dict) -> 'SubobstructionInferralStrategy':
        return cls()

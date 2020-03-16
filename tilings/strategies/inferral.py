from typing import Optional

from comb_spec_searcher import Rule
from tilings import Tiling
from tilings.algorithms import (AllObstructionInferral, EmptyCellInferral,
                                ObstructionTransitivity, RowColSeparation,
                                SubobstructionInferral)
from tilings.strategies.abstract_strategy import Strategy

__all__ = [
    'ObstructionTransitivityStrategy',
    'RowColumnSeparationStrategy',
    'EmptyCellInferralStrategy',
    'SubobstructionInferralStrategy',
    'ObstructionInferralStrategy',
]


class ObstructionTransitivityStrategy(Strategy):
    """
    The obstruction transitivity strategy.

    The obstruction transitivity considers all length 2 obstructions with both
    points in the same row or some column. By considering these length 2
    obstructions in similar manner as the row and column separation, as
    inequality relations. When the obstructions use a positive cell,
    transitivity applies, i.e. if a < b < c and b is positive, then a < c.
    """
    def __call__(self, tiling: Tiling, **kwargs) -> Optional[Rule]:
        return ObstructionTransitivity(tiling).rule()

    def __str__(self) -> str:
        return 'obstruction transitivity'

    def __repr__(self) -> str:
        return 'ObstructionTransitivityStrategy()'

    @classmethod
    def from_dict(cls, d: dict) -> 'ObstructionTransitivityStrategy':
        return cls()


class RowColumnSeparationStrategy(Strategy):
    """
    An inferral function that tries to separate cells in rows and columns.
    """
    def __call__(self, tiling: Tiling, **kwargs) -> Optional[Rule]:
        rcs = RowColSeparation(tiling)
        return rcs.rule()

    def __str__(self) -> str:
        return 'row and column separation'

    def __repr__(self) -> str:
        return 'RowColumnSeparationStrategy()'

    @classmethod
    def from_dict(cls, d: dict) -> 'RowColumnSeparationStrategy':
        return cls()


class EmptyCellInferralStrategy(Strategy):
    """
    The empty cell inferral strategy.

    The strategy considers each active but non-positive cell and inserts a
    point requirement. If the resulting tiling is empty, then a point
    obstruction can be added into the cell, i.e. the cell is empty.
    """
    def __call__(self, tiling: Tiling, **kwargs) -> Optional[Rule]:
        return EmptyCellInferral(tiling).rule()

    def __str__(self) -> str:
        return 'empty cell inferral'

    def __repr__(self) -> str:
        return 'EmptyCellInferralStrategy()'

    @classmethod
    def from_dict(cls, d: dict) -> 'EmptyCellInferralStrategy':
        return cls()


class SubobstructionInferralStrategy(Strategy):
    """
    Return tiling created by adding all subobstructions which can be
    added.
    """
    def __call__(self, tiling: Tiling, **kwargs) -> Optional[Rule]:
        return SubobstructionInferral(tiling).rule()

    def __str__(self) -> str:
        return 'subobstruction inferral'

    def __repr__(self) -> str:
        return 'SubobstructionInferralStrategy()'

    @classmethod
    def from_dict(cls, d: dict) -> 'SubobstructionInferralStrategy':
        return cls()


class ObstructionInferralStrategy(Strategy):
    """
    Return tiling created by adding all obstructions of length up to maxlen
    that can be added.
    """
    def __init__(self, maxlen: int = 3) -> None:
        self.maxlen = maxlen

    def __call__(self, tiling: Tiling, **kwargs) -> Optional[Rule]:
        return AllObstructionInferral(tiling, self.maxlen).rule()

    def __repr__(self) -> str:
        return 'ObstructionInferralStrategy(maxlen={})'.format(self.maxlen)

    def __str__(self) -> str:
        return 'length {} obstruction inferral'.format(self.maxlen)

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d['maxlen'] = self.maxlen
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'ObstructionInferralStrategy':
        return cls(maxlen=d['maxlen'])

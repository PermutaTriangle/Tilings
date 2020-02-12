from typing import Iterator, Optional

from comb_spec_searcher import Rule
from tilings import Tiling
from tilings.algorithms import (Factor, FactorWithInterleaving,
                                FactorWithMonotoneInterleaving)
from tilings.strategies.abstract_strategy import Strategy


class FactorStrategy(Strategy):

    factor_class = {
        None: Factor,
        'monotone': FactorWithMonotoneInterleaving,
        'all': FactorWithInterleaving,
    }

    def __init__(self, interleaving: Optional[str] = None,
                 union: bool = False, workable: bool = True) -> None:
        assert (
            interleaving in FactorStrategy.factor_class
        ), ('Invalid interleaving option. Must be in {}'
            .format(FactorStrategy.factor_class.keys()))
        self.interleaving = interleaving
        self.union = union
        self.workable = workable

    def __call__(self, tiling: Tiling) -> Iterator[Rule]:
        factor_algo = FactorStrategy.factor_class[self.interleaving](tiling)
        if factor_algo.factorable():
            yield factor_algo.rule(workable=self.workable)
            if self.union:
                yield from factor_algo.all_union_rules()

    def __str__(self) -> str:
        if self.interleaving is None:
            s = 'factor'
        elif self.interleaving == 'monotone':
            s = 'factor with monotone interleaving'
        elif self.interleaving == 'all':
            s = 'factor with interleaving'
        else:
            raise Exception('Invalid interleaving type')
        if self.union:
            s = 'unions of ' + s
        return s

    def __repr__(self) -> str:
        return ('FactorStrategy(interleaving={}, union={}, workable={})'
                .format(self.interleaving, self.union, self.workable))

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d['interleaving'] = self.interleaving
        d['union'] = self.union
        d['workable'] = self.workable
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'FactorStrategy':
        return cls(**d)

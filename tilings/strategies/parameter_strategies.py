from typing import Iterable, Iterator, List, Optional, Tuple

from comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import (
    AbstractStrategy,
    Constructor,
    DisjointUnion,
    DisjointUnionStrategy,
    Strategy,
    StrategyFactory,
)
from tilings import GriddedPerm, Tiling
from tilings.parameter_counter import ParameterCounter, PreimageCounter


class RemoveIdentityPreimage(Strategy[Tiling, GriddedPerm]):
    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        applied = False
        params: List[List[PreimageCounter]] = []
        for param in comb_class.parameters:
            params.append([])
            for preimg in param.counters:
                if (
                    preimg.map.is_identity()
                    and preimg.tiling == comb_class.remove_parameters()
                ):
                    applied = True
                else:
                    params[-1].append(preimg)
        if not applied:
            raise StrategyDoesNotApply
        t = comb_class.remove_parameters().add_parameters(map(ParameterCounter, params))
        return (t,)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Constructor:
        raise NotImplementedError

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        raise NotImplementedError

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        raise NotImplementedError

    def can_be_equivalent(self) -> bool:
        return False

    def formal_step(self) -> str:
        return "remove identity preimages"

    @classmethod
    def from_dict(cls, d: dict) -> "RemoveIdentityPreimage":
        raise NotImplementedError

    def is_reversible(self, comb_class: Tiling) -> bool:
        return True

    def is_two_way(self, comb_class: Tiling) -> bool:
        return True

    def shifts(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[int]:
        return (0,)


class DisjointParameterStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    def __init__(self, strategy: AbstractStrategy, param_idx: int, preimg_idx: int):
        self.strategy = strategy
        self.param_idx = param_idx
        self.preimg_idx = preimg_idx

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        if (
            len(comb_class.parameters) <= self.param_idx
            or len(comb_class.parameters[self.param_idx].counters) <= self.preimg_idx
        ):
            raise StrategyDoesNotApply
        params: List[List[PreimageCounter]] = []
        for param_idx, param in enumerate(comb_class.parameters):
            params.append([])
            for preimg_idx, preimg in enumerate(param.counters):
                if param_idx == self.param_idx and preimg_idx == self.preimg_idx:
                    t = preimg.tiling
                    rule = self.strategy(t)
                    if not isinstance(rule.constructor, DisjointUnion):
                        raise StrategyDoesNotApply
                    for child in rule.children:
                        params[-1].append(PreimageCounter(child, preimg.map))
                else:
                    params[-1].append(preimg)
        t = comb_class.remove_parameters().add_parameters(map(ParameterCounter, params))
        return (t,)

    # def backward_map(
    #     self,
    #     comb_class: Tiling,
    #     objs: Tuple[Optional[GriddedPerm], ...],
    #     children: Optional[Tuple[Tiling, ...]] = None,
    # ) -> Iterator[GriddedPerm]:
    #     return objs[0]

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        return (obj,)

    def formal_step(self) -> str:
        return f"applied '{self.strategy.formal_step()}' to primage {self.preimg_idx} in parameter {self.param_idx}"

    @classmethod
    def from_dict(cls, d: dict) -> "DisjointParameterStrategy":
        raise NotImplementedError


class DisjointUnionParameterFactory(StrategyFactory[Tiling]):
    def __init__(self, strategies: Iterable[AbstractStrategy], **kwargs):
        self.strategies = tuple(strategies)
        super().__init__(**kwargs)

    def __call__(self, comb_class: Tiling) -> Iterator[DisjointUnionStrategy]:
        for i, param in enumerate(comb_class.parameters):
            for j, preimage in enumerate(param.counters):
                for strategy in self.strategies:
                    for rule in CombinatorialSpecificationSearcher._rules_from_strategy(
                        preimage.tiling, strategy
                    ):
                        yield DisjointParameterStrategy(rule.strategy, i, j)

    def __str__(self) -> str:
        return f"applying '{self.strategies}' to parameters"

    def __repr__(self) -> str:
        return f"DisjointUnionParameterFactory({repr(self.strategies)})"

    def to_jsonable(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> "DisjointUnionParameterFactory":
        raise NotImplementedError

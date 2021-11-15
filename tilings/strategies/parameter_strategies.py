from typing import Iterable, Iterator, List, Optional, Tuple

from comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import (
    AbstractStrategy,
    Constructor,
    DisjointUnion,
    DisjointUnionStrategy,
    Rule,
    Strategy,
    StrategyFactory,
    StrategyPack,
    VerificationStrategy,
)
from comb_spec_searcher.typing import CSSstrategy
from tilings import GriddedPerm, Tiling
from tilings.parameter_counter import ParameterCounter, PreimageCounter


class RemoveIdentityPreimageStrategy(Strategy[Tiling, GriddedPerm]):
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
    def from_dict(cls, d: dict) -> "RemoveIdentityPreimageStrategy":
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
        super().__init__(ignore_parent=True)

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
                    assert isinstance(rule, Rule)
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
        return (
            f"applied '{self.strategy.formal_step()}' to primage "
            f"{self.preimg_idx} in parameter {self.param_idx}"
        )

    @classmethod
    def from_dict(cls, d: dict) -> "DisjointParameterStrategy":
        raise NotImplementedError


class DisjointUnionParameterFactory(StrategyFactory[Tiling]):
    def __init__(self, strategies: Iterable[CSSstrategy]):
        self.strategies = tuple(strategies)
        super().__init__()

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


class ParameterVerificationStrategy(VerificationStrategy[Tiling, GriddedPerm]):
    """
    A subclass for when a combinatorial class is equal to the empty set.
    """

    @staticmethod
    def random_sample_object_of_size(
        comb_class: Tiling, n: int, **parameters: int
    ) -> GriddedPerm:
        raise NotImplementedError

    @staticmethod
    def verified(comb_class: Tiling) -> bool:
        if (
            comb_class.dimensions != (1, 1)
            or len(comb_class.parameters) != 1
            or len(comb_class.parameters[0].counters) != 1
        ):
            return False
        preimage = comb_class.parameters[0].counters[0]
        extra_obs, extra_reqs = preimage.extra_obs_and_reqs(comb_class)
        # TODO: check if skew, sum, or point fusion.
        # TODO: Should child be without params?
        return not extra_reqs and all(len(ob) < 3 for ob in extra_obs)

    @staticmethod
    def formal_step() -> str:
        return "parameter verified"

    @staticmethod
    def pack(comb_class: Tiling) -> StrategyPack:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> "ParameterVerificationStrategy":
        assert not d
        return cls()

    def __str__(self) -> str:
        return "parameter verification"

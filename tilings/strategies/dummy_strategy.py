from typing import Dict, Iterator, Optional, Tuple

from comb_spec_searcher import Strategy
from tilings import GriddedPerm, Tiling

from .dummy_constructor import DummyConstructor


class DummyStrategy(Strategy[Tiling, GriddedPerm]):
    def can_be_equivalent(self) -> bool:
        pass

    def is_two_way(self, comb_class: Tiling) -> bool:
        pass

    def is_reversible(self, comb_class: Tiling) -> bool:
        pass

    def shifts(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]],
    ) -> Tuple[int, ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        pass

    def decomposition_function(
        self, comb_class: Tiling
    ) -> Optional[Tuple[Tiling, ...]]:
        pass

    def formal_step(self) -> str:
        return "dummy strategy"

    def constructor(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> DummyConstructor:
        if children is None:
            children = self.decomposition_function(comb_class)
        return DummyConstructor()

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> DummyConstructor:
        if children is None:
            children = self.decomposition_function(comb_class)
        return DummyConstructor()

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        if children is None:
            children = self.decomposition_function(comb_class)
        raise NotImplementedError

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        raise NotImplementedError

    def extra_parameters(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Dict[str, str], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> "DummyStrategy":
        return cls(**d)

from typing import Dict, Iterator, Optional, Tuple

from comb_spec_searcher import Strategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
from tilings import GriddedPerm, Tiling
from tilings.strategies.dummy_constructor import DummyConstructor


class RelaxAssumptionStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(self, child: Tiling, assumption_idx: int, **kwargs):
        self.child = child
        self.assumption_idx = assumption_idx
        super().__init__(**kwargs)

    def can_be_equivalent(self) -> bool:
        return False

    def is_two_way(self, comb_class: Tiling) -> bool:
        return False

    def is_reversible(self, comb_class: Tiling) -> bool:
        return False

    def shifts(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]],
    ) -> Tuple[int, ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        return (0,)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        try:
            assumption = self.child.assumptions[self.assumption_idx]
        except IndexError as e:
            raise StrategyDoesNotApply from e
        parent = self.child.add_obstructions(assumption.gps)
        if parent != comb_class:
            raise StrategyDoesNotApply
        return (self.child,)

    def formal_step(self) -> str:
        return f"the assumption at index {self.assumption_idx} is relaxed"

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

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["child"] = self.child.to_jsonable()
        d["assumption_idx"] = self.assumption_idx
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RelaxAssumptionStrategy":
        return cls(Tiling.from_dict(d.pop("child")), d.pop("assumption_idx"), **d)


class RelaxAssumptionFactory(StrategyFactory[Tiling]):
    def __call__(self, comb_class: Tiling) -> Iterator[Rule]:
        for idx, assumption in enumerate(comb_class.assumptions):
            parent = comb_class.add_obstructions(assumption.gps)
            yield RelaxAssumptionStrategy(comb_class, idx)(parent, (comb_class,))

    @classmethod
    def from_dict(cls, d: dict) -> "RelaxAssumptionFactory":
        return cls(**d)

    def __str__(self) -> str:
        return "Relax assumption"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

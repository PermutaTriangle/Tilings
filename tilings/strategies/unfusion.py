from itertools import chain
from typing import Dict, Iterator, Optional, Tuple

from comb_spec_searcher import Strategy
from comb_spec_searcher.strategies.strategy import StrategyFactory
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Fusion

from .dummy_constructor import DummyConstructor


class UnfusionColumnStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(
        self,
        ignore_parent: bool = False,
        inferrable: bool = True,
        possibly_empty: bool = True,
        workable: bool = True,
        cols: bool = True,
    ):
        self.cols = cols
        super().__init__(ignore_parent, inferrable, possibly_empty, workable)

    def can_be_equivalent(self) -> bool:
        return False

    def is_two_way(self, comb_class: Tiling) -> bool:
        return True

    def is_reversible(self, comb_class: Tiling) -> bool:
        return True

    def shifts(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]],
    ) -> Tuple[int, ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        print(self(comb_class))
        return tuple(0 for _ in range(self.width(comb_class)))

    def width(self, comb_class: Tiling) -> int:
        if self.cols:
            return comb_class.dimensions[0]
        return comb_class.dimensions[1]

    def decomposition_function(
        self, comb_class: Tiling
    ) -> Optional[Tuple[Tiling, ...]]:
        res = []
        for idx in range(self.width(comb_class)):
            if self.cols:
                algo = Fusion(comb_class, col_idx=idx)
            else:
                algo = Fusion(comb_class, row_idx=idx)
            obs = chain(
                *[algo.unfuse_gridded_perm(ob) for ob in comb_class.obstructions]
            )
            reqs = [
                [gp for req_gp in req_list for gp in algo.unfuse_gridded_perm(req_gp)]
                for req_list in comb_class.requirements
            ]
            ass = [
                ass.__class__(
                    [
                        gp
                        for ass_gp in ass.gps
                        for gp in algo.unfuse_gridded_perm(ass_gp)
                    ]
                )
                for ass in comb_class.assumptions
            ]
            res.append(Tiling(obs, reqs, ass))
        return tuple(res)

    def formal_step(self) -> str:
        if self.cols:
            return "unfuse columns strategy"
        return "unfuse rows strategy"

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
    def from_dict(cls, d: dict) -> "UnfusionColumnStrategy":
        return cls(**d)


class UnfusionRowStrategy(UnfusionColumnStrategy):
    def __init__(
        self,
        ignore_parent: bool = False,
        inferrable: bool = True,
        possibly_empty: bool = True,
        workable: bool = True,
        cols: bool = False,
    ):
        super().__init__(ignore_parent, inferrable, possibly_empty, workable, cols)


class UnfusionFactory(StrategyFactory[Tiling]):
    def __call__(self, comb_class: Tiling) -> Iterator[UnfusionColumnStrategy]:
        yield UnfusionColumnStrategy()
        yield UnfusionRowStrategy()

    def __str__(self) -> str:
        return "unfusion strategy"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d: dict) -> "UnfusionFactory":
        return cls()

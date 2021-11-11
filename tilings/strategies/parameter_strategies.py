from typing import Iterator, List, Optional, Tuple

from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Constructor, Strategy
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

from typing import Iterator, List, Optional, Tuple

from sympy import Eq, Function

from comb_spec_searcher import CombinatorialObject, Constructor, Strategy
from comb_spec_searcher.strategies.constructor import (
    RelianceProfile,
    SubGens,
    SubRecs,
    SubSamplers,
)
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Factor
from tilings.assumptions import TrackingAssumption


class Split(Constructor):
    def is_equivalence(self) -> bool:
        return False

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        raise NotImplementedError

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
        raise NotImplementedError

    def get_sub_objects(
        self, subgens: SubGens, n: int, **parameters: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        raise NotImplementedError

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int
    ):
        raise NotImplementedError

    @staticmethod
    def get_eq_symbol() -> str:
        return "↣"


class SplittingStrategy(Strategy[Tiling, GriddedPerm]):
    @staticmethod
    def decomposition_function(tiling: Tiling) -> Optional[Tuple[Tiling]]:
        if not tiling.assumptions:
            return None
        components = Factor(tiling.underlying_tiling()).get_components()
        if len(components) == 1:
            return None
        new_assumptions: List[TrackingAssumption] = []
        for ass in tiling.assumptions:
            assert isinstance(
                ass, TrackingAssumption
            ), "not implemented splitting assumption for given type"
            split_gps: List[List[GriddedPerm]] = [[] for _ in range(len(components))]
            for gp in ass.gps:
                for idx, component in enumerate(components):
                    if all(cell in component for cell in gp.pos):
                        split_gps[idx].append(gp)
                        # only add to one list
                        break
                else:
                    # gridded perms can't be partitioned
                    new_assumptions.extend([ass])
                    break
            else:
                new_assumptions.extend(
                    [TrackingAssumption(gps) for gps in split_gps if gps]
                )
        return (Tiling(tiling.obstructions, tiling.requirements, new_assumptions),)

    @staticmethod
    def constructor(
        comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Split:
        return Split()

    @staticmethod
    def formal_step() -> str:
        return "splitting the assumptions"

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> GriddedPerm:
        """
        The forward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)
        raise NotImplementedError

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> "SplittingStrategy":
        return cls(**d)


# TODO: iterate over all possible union of factors

# class SplittingFactory(StrategyFactory[Tiling]):

#     def __repr__(self):
#         return self.__class__.__name__ + "()"

#     def __str__(self):
#         return "splitting tracked variables"

#     @classmethod
#     def from_dict(cls, d: dict) -> "SplittingFactory":
#         assert not d, "no arguments needed for SplittingFactory"
#         return cls()

from typing import Dict, Iterator, Optional, Tuple

from comb_spec_searcher import (
    Constructor,
    Strategy,
)
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies.constructor import (
    RelianceProfile,
    SubGens,
    SubRecs,
    SubSamplers,
)
from sympy import Eq, Function
from tilings import GriddedPerm, Tiling, TrackingAssumption


class CountComponent(Constructor[Tiling, GriddedPerm]):
    """
    The constructor used to count when we see actual components.

    The components dictionary counts how many components are to be counted by
    each parameter, noting they will no longer be tracked in the child.

    The extra_parameters map the parent constructor to the child parameter. If
    a parent parameter became empty by removing a component, then it will not
    the parent parameter will not be a key in extra_parameters.
    """

    def __init__(self, components: Dict[str, int], extra_parameters: Dict[str, str]):
        self.components = components
        self.extra_parameters = extra_parameters

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        raise NotImplementedError

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
        raise NotImplementedError

    def get_sub_objects(
        self, subgens: SubGens, n: int, **parameters: int
    ) -> Iterator[Tuple[GriddedPerm, ...]]:
        raise NotImplementedError

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ):
        raise NotImplementedError

    @staticmethod
    def get_eq_symbol() -> str:
        return "↣"


class DetectComponentsStrategy(Strategy[Tiling, GriddedPerm]):
    @staticmethod
    def can_be_equivalent() -> bool:
        return False

    def decomposition_function(self, tiling: Tiling) -> Optional[Tuple[Tiling]]:
        if not tiling.assumptions:
            return None
        return (tiling.remove_components_from_assumptions(),)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None,
    ) -> CountComponent:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't split the tracking assumption")

        removed_components: Dict[str, int] = {}
        for ass in comb_class.assumptions:
            value = len(ass.get_components(comb_class))
            if value:
                k = comb_class.get_parameter(ass)
                removed_components[k] = value
        return CountComponent(removed_components, {})

    @staticmethod
    def formal_step() -> str:
        return "removing exact components"

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
    def from_dict(cls, d: dict) -> "DetectComponentsStrategy":
        return cls(**d)

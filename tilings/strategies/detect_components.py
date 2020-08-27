from functools import reduce
from operator import mul
from typing import Dict, Iterator, Optional, Tuple

from sympy import Eq, Function, var

from comb_spec_searcher import Constructor, Strategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies.constructor import (
    RelianceProfile,
    SubGens,
    SubRecs,
    SubSamplers,
)
from tilings import GriddedPerm, Tiling


class CountComponent(Constructor[Tiling, GriddedPerm]):
    """
    The constructor used to count when we see actual components.

    The components dictionary counts how many components are to be counted by
    each parameter, noting they will no longer be tracked in the child.

    The extra_parameters map the parent parameters to the child parameters. If
    a parent parameter became empty by removing a component the parent
    parameter will not be a key in extra_parameters.
    """

    def __init__(self, components: Dict[str, int], extra_parameters: Dict[str, str]):
        self.components = components
        self.extra_parameters = extra_parameters

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        rhs_func = rhs_funcs[0].subs(
            {b: a for a, b in self.extra_parameters.items()}, simultaneously=True
        )
        return Eq(
            lhs_func,
            rhs_func
            * reduce(mul, [var(k) ** val for k, val in self.components.items()], 1),
        )

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
        new_params: Dict[str, int] = {}
        for k, val in parameters.items():
            val -= self.components.get(k, 0)
            if val < 0:
                return 0
            mapped_k = self.extra_parameters[k]
            if mapped_k is not None:
                if mapped_k in new_params and new_params[mapped_k] != val:
                    return 0
                new_params[mapped_k] = val
        return subrecs[0](n, **new_params)

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

    @staticmethod
    def decomposition_function(tiling: Tiling) -> Optional[Tuple[Tiling]]:
        if not tiling.assumptions:
            return None
        return (tiling.remove_components_from_assumptions(),)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> CountComponent:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't detect components")

        removed_components: Dict[str, int] = {}
        for ass in comb_class.assumptions:
            value = len(ass.get_components(comb_class))
            if value:
                k = comb_class.get_parameter(ass)
                removed_components[k] = value
        return CountComponent(
            removed_components, self.extra_parameters(comb_class, children)[0]
        )

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str]]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        extra_parameters: Dict[str, str] = {}
        child = children[0]
        for assumption in comb_class.assumptions:
            mapped_assumption = assumption.remove_components(comb_class)
            if mapped_assumption.gps:
                extra_parameters[
                    comb_class.get_parameter(assumption)
                ] = child.get_parameter(mapped_assumption)
        return (extra_parameters,)

    @staticmethod
    def formal_step() -> str:
        return "removing exact components"

    @staticmethod
    def backward_map(
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> GriddedPerm:
        """
        The forward direction of the underlying bijection used for object
        generation and sampling.
        """
        assert isinstance(objs[0], GriddedPerm)
        return objs[0]

    @staticmethod
    def forward_map(
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        return (obj,)

    @classmethod
    def from_dict(cls, d: dict) -> "DetectComponentsStrategy":
        return cls(**d)

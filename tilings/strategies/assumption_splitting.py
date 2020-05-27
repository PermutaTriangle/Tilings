from itertools import product
from typing import Dict, Iterator, List, Optional, Tuple

from sympy import Eq, Function

from comb_spec_searcher import CombinatorialObject, Constructor, Strategy
from comb_spec_searcher.exception import StrategyDoesNotApply
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
    """
    The constructor used to cound when a variable is counted by some multiple
    disjoint subvariables.
    """

    def __init__(self, parameters: Dict[str, Tuple[str, ...]]):
        self.parameters = parameters

    def is_equivalence(self) -> bool:
        return False

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        raise NotImplementedError

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
        """
        The parameters tells you what each variable is split into,

        If there is k: (k_0, k_1) then we need to sum over all ways that
        k = k_0 + k_1.

        Side note: notice the similarity between this function and cartesian
        product - if we were to instead track the size of the root using a
        tracking assumption, then all of the complicated logic of the cartesian
        product could become local to the Split constructor, and the recurrence
        would just be a multiplication. This is because our Factor strategy,
        and cartesian product strategy is implicitly using the fact that we can
        always split the assumption covering the whole tiling with respect to
        the factors.

        # TODO: this should take into consideration the reliance profile.
        """
        rec = subrecs[0]
        res = 0
        for sub_params in self._valid_compositions(**parameters):
            res += rec(n, **sub_params)
        return res

    def _valid_compositions(self, **parameters: int) -> Iterator[Dict[str, int]]:
        """
        TODO: this should consider reliance profiles, and when variables are
        sub variable of other variables.
        """

        def compositions(value: int, parameters: Tuple[str, ...]):
            def _compositions(value: int, length: int) -> Iterator[Tuple[int, ...]]:
                if value < 0:
                    return
                if length == 0:
                    if value == 0:
                        yield tuple()
                    return
                for i in range(value + 1):
                    for comp in _compositions(value - i, length - 1):
                        yield (i,) + comp

            for comp in _compositions(value, len(parameters)):
                yield {k: val for k, val in zip(parameters, comp)}

        for sub_params in product(
            *[
                compositions(val, self.parameters[key])
                for key, val in parameters.items()
            ]
        ):
            new_params: Dict[str, int] = dict()
            for p in sub_params:
                new_params.update(p.items())
            yield new_params

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
    """
    A strategy which splits each TrackingAssumption into sub TrackingAssumptions,
    according to the factors of the underlying tiling.

    TODO: iterate over all possible union of factors
    """

    def decomposition_function(self, tiling: Tiling) -> Optional[Tuple[Tiling]]:
        if not tiling.assumptions:
            return None
        components = Factor(tiling.remove_assumptions()).get_components()
        if len(components) == 1:
            return None
        new_assumptions: List[TrackingAssumption] = []
        for ass in tiling.assumptions:
            new_assumptions.extend(self._split_assumption(ass, components))
        return (Tiling(tiling.obstructions, tiling.requirements, new_assumptions),)

    @staticmethod
    def _split_assumption(assumption, components):
        split_gps: List[List[GriddedPerm]] = [[] for _ in range(len(components))]
        for gp in assumption.gps:
            for idx, component in enumerate(components):
                if all(cell in component for cell in gp.pos):
                    split_gps[idx].append(gp)
                    # only add to one list
                    break
            else:
                # gridded perm can't be partitioned, so the partition can't be
                # partitioned
                return [assumption]
        return [TrackingAssumption(gps) for gps in split_gps if gps]

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Split:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't split the tracking assumption")
        child = children[0]
        parameters: Dict[str, Tuple[str, ...]] = {"n": ("n",)}
        components = Factor(comb_class.remove_assumptions()).get_components()
        for idx, assumption in enumerate(comb_class.assumptions):
            split_assumptions = self._split_assumption(assumption, components)
            child_vars = tuple(
                sorted(
                    "k_{}".format(child.assumptions.index(ass))
                    for ass in split_assumptions
                )
            )
            parameters["k_{}".format(idx)] = child_vars
        return Split(parameters)

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

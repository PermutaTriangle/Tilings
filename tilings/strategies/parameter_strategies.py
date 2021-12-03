from collections import Counter
from typing import Callable, Dict, Iterator, List, Optional, Tuple, Union, cast

import sympy

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
from comb_spec_searcher.typing import (
    CSSstrategy,
    Parameters,
    ParametersMap,
    RelianceProfile,
    SubObjects,
    SubRecs,
    SubSamplers,
    SubTerms,
    Terms,
)
from tilings import GriddedPerm, Tiling
from tilings.parameter_counter import ParameterCounter, PreimageCounter

from .requirement_insertion import (
    RemoveRequirementFactory,
    RequirementInsertionStrategy,
)


class RemoveIdentityPreimageConstructor(Constructor):
    def __init__(
        self,
        parent: Tiling,
        child: Tiling,
        extra_params: Dict[str, str],
        reduction: Dict[str, int],
    ):
        self.child_to_parent_map = self.remove_param_map(
            parent, child, extra_params, reduction
        )

    @staticmethod
    def remove_param_map(
        parent: Tiling,
        child: Tiling,
        extra_params: Dict[str, str],
        reduction: Dict[str, int],
    ) -> ParametersMap:
        """
        Returns a function that transform the parameters on the child to parameters on
        the parent of the rule.
        """
        map_data_partial: List[Optional[Tuple[int, int]]] = list(
            None for _ in parent.parameters
        )
        for parent_param_name, child_param_name in extra_params.items():
            child_param_idx = child.parameters.index(
                child.get_parameter(child_param_name)
            )
            parent_param_idx = parent.parameters.index(
                parent.get_parameter(parent_param_name)
            )
            map_data_partial[parent_param_idx] = (
                child_param_idx,
                reduction[parent_param_name],
            )
        assert all(x is not None for x in map_data_partial)
        map_data: Tuple[Tuple[int, int], ...] = tuple(
            cast(List[Tuple[int, int]], map_data_partial)
        )

        def param_map(param: Parameters) -> Parameters:
            return tuple(
                param[child_param_idx] + reduction
                for child_param_idx, reduction in map_data
            )

        return param_map

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        raise NotImplementedError

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        terms: Terms = Counter()
        for param, count in subterms[0](n).items():
            new_param = self.child_to_parent_map(param)
            terms[new_param] += count
        return terms

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[Tuple[Parameters, Tuple[List[Optional[GriddedPerm]], ...]]]:
        raise NotImplementedError

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        raise NotImplementedError

    def equiv(
        self, other: Constructor, data: Optional[object] = None
    ) -> Tuple[bool, Optional[object]]:
        raise NotImplementedError


class AddIdentityPreimageConstructor(Constructor):
    def __init__(
        self,
        parent: Tiling,
        child: Tiling,
        extra_params: Dict[str, str],
        reduction: Dict[str, int],
    ):
        self.child_to_parent_map = self.add_identity_param_map(
            parent, child, extra_params, reduction
        )

    @staticmethod
    def add_identity_param_map(
        parent: Tiling,
        child: Tiling,
        extra_params: Dict[str, str],
        reduction: Dict[str, int],
    ) -> ParametersMap:
        reverse_extra_params = {v: k for k, v in extra_params.items()}
        map_data_partial: List[Optional[Tuple[int, int]]] = list(
            None for _ in child.parameters
        )
        for child_param, parent_param in reverse_extra_params.items():
            child_param_idx = child.parameters.index(child.get_parameter(child_param))
            parent_param_idx = parent.parameters.index(
                parent.get_parameter(parent_param)
            )
            map_data_partial[child_param_idx] = (
                parent_param_idx,
                reduction[parent_param],
            )
        assert all(x is not None for x in map_data_partial)
        map_data: Tuple[Tuple[int, int], ...] = tuple(
            cast(List[Tuple[int, int]], map_data_partial)
        )

        def param_map(param: Parameters) -> Parameters:
            return tuple(
                param[parent_param_idx] - reduction
                for parent_param_idx, reduction in map_data
            )

        return param_map

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        raise NotImplementedError

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        terms: Terms = Counter()
        for param, count in subterms[0](n).items():
            new_param = self.child_to_parent_map(param)
            terms[new_param] += count
        return terms

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[Tuple[Parameters, Tuple[List[Optional[GriddedPerm]], ...]]]:
        raise NotImplementedError

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        raise NotImplementedError

    def equiv(
        self, other: Constructor, data: Optional[object] = None
    ) -> Tuple[bool, Optional[object]]:
        raise NotImplementedError


class RemoveIdentityPreimageStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(self) -> None:
        super().__init__(ignore_parent=True)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        applied = False
        params: List[ParameterCounter] = []
        for param in comb_class.parameters:
            new_param = self._map_param(comb_class, param)
            applied = applied or len(new_param.counters) < len(param.counters)
            params.append(new_param)
        if not applied:
            raise StrategyDoesNotApply
        t = comb_class.remove_parameters().add_parameters(params)
        return (t,)

    @staticmethod
    def _map_param(comb_class: Tiling, param: ParameterCounter) -> ParameterCounter:
        """
        Map a parameters of comb_class by removing the identity parameters.
        """
        preimgs = (
            preimg
            for preimg in param.counters
            if not preimg.always_counts_one(comb_class)
        )
        return ParameterCounter(preimgs)

    def extra_parameter(self, comb_class: Tiling, child: Tiling) -> Dict[str, str]:
        """
        Indicate to which parameter on the child each parameter on the parent is
        mapping.
        """
        return {
            comb_class.get_parameter_name(param): child.get_parameter_name(
                self._map_param(comb_class, param)
            )
            for param in comb_class.parameters
        }

    def _param_reduction(self, comb_class) -> Dict[str, int]:
        """
        For each of the param on comb_class, indicate how many identity preimages
        have been removed.
        """
        return {
            comb_class.get_parameter_name(param): len(param.counters)
            - len(self._map_param(comb_class, param).counters)
            for param in comb_class.parameters
        }

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Constructor:
        if children is None:
            children = self.decomposition_function(comb_class)
        child = children[0]
        return RemoveIdentityPreimageConstructor(
            comb_class,
            child,
            self.extra_parameter(comb_class, child),
            self._param_reduction(comb_class),
        )

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        assert idx == 0
        if children is None:
            children = self.decomposition_function(comb_class)
        child = children[0]
        return AddIdentityPreimageConstructor(
            comb_class,
            child,
            self.extra_parameter(comb_class, child),
            self._param_reduction(comb_class),
        )

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
        return cls()

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d.pop("ignore_parent")
        d.pop("inferrable")
        d.pop("possibly_empty")
        d.pop("workable")
        return d

    def is_reversible(self, comb_class: Tiling) -> bool:
        return True

    def is_two_way(self, comb_class: Tiling) -> bool:
        return True

    def shifts(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[int]:
        return (0,)


class DisjointParameterStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    def __init__(
        self,
        strategy: DisjointUnionStrategy[Tiling, GriddedPerm],
        param_idx: int,
        preimg_idx: int,
        ignore_parent: bool = True,
    ):
        assert isinstance(strategy, DisjointUnionStrategy)
        self.strategy = strategy
        self.param_idx = param_idx
        self.preimg_idx = preimg_idx
        super().__init__(ignore_parent=ignore_parent)

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

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        child = children[0]
        extra_params: Dict[str, str] = {}
        for i, param in enumerate(comb_class.parameters):
            if i == self.param_idx:
                continue
            extra_params[
                comb_class.get_parameter_name(param)
            ] = child.get_parameter_name(param)
        param = comb_class.parameters[self.param_idx]
        new_preimages = []
        for j, preimage in enumerate(param.counters):
            if j != self.preimg_idx:
                new_preimages.append(preimage)
                continue
            rule = self.strategy(preimage.tiling)
            for preimage_child in rule.children:
                new_preimages.append(
                    PreimageCounter(preimage_child, preimage.map)
                )  # TODO: did the preimage map change?
        new_parameter = ParameterCounter(new_preimages)
        extra_params[comb_class.get_parameter_name(param)] = child.get_parameter_name(
            new_parameter
        )
        return (extra_params,)

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
        return (obj,)

    def formal_step(self) -> str:
        return (
            f"applied '{self.strategy.formal_step()}' to preimage "
            f"{self.preimg_idx} in parameter {self.param_idx}"
        )

    @classmethod
    def from_dict(cls, d: dict) -> "DisjointParameterStrategy":
        strategy = AbstractStrategy.from_dict(d.pop("strategy"))
        assert isinstance(strategy, DisjointUnionStrategy)
        return cls(strategy, **d)

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["strategy"] = self.strategy.to_jsonable()
        d["param_idx"] = self.param_idx
        d["preimg_idx"] = self.preimg_idx
        return d


class DisjointUnionParameterFactory(StrategyFactory[Tiling]):
    def __init__(self, strategy: CSSstrategy):
        self.strategy = strategy
        super().__init__()

    def __call__(
        self, comb_class: Tiling
    ) -> Iterator[Union[DisjointUnionStrategy, Rule]]:
        for i, param in enumerate(comb_class.parameters):
            for j, preimage in enumerate(param.counters):
                for rule in CombinatorialSpecificationSearcher._rules_from_strategy(
                    preimage.tiling, self.strategy
                ):
                    assert isinstance(rule.strategy, DisjointUnionStrategy)
                    if rule.comb_class == preimage.tiling:
                        yield DisjointParameterStrategy(rule.strategy, i, j)
                    elif isinstance(self.strategy, RemoveRequirementFactory):
                        assert isinstance(rule.strategy, RequirementInsertionStrategy)
                        yield from self._special_case_remove_requirement_factory(
                            comb_class, rule.strategy, i, j
                        )

    @staticmethod
    def _special_case_remove_requirement_factory(
        comb_class: Tiling, strategy: RequirementInsertionStrategy, i: int, j: int
    ) -> Iterator[Rule]:
        """TODO: this is a major special case to reduce work done"""
        param = comb_class.parameters[i]
        preimage = param.counters[j]
        req = tuple(sorted(strategy.gps))
        req_idx = preimage.tiling.requirements.index(req)
        image_req = tuple(sorted(preimage.map.map_gps(req)))
        preimage_image_req = tuple(sorted(preimage.map.preimage_gps(image_req)))
        if image_req in comb_class.requirements and preimage_image_req == req:
            return
        new_tiling = Tiling(
            preimage.tiling.obstructions,
            preimage.tiling.requirements[:req_idx]
            + preimage.tiling.requirements[req_idx + 1 :]
            + ((preimage_image_req,) if preimage_image_req != req else tuple()),
        )
        new_preimage = PreimageCounter(new_tiling, preimage.map)
        new_param = ParameterCounter(
            comb_class.parameters[i].counters[:j]
            + comb_class.parameters[i].counters[j + 1 :]
            + (new_preimage,)
        )
        new_comb_class = comb_class.remove_parameter(param).add_parameter(new_param)
        if any(
            PreimageCounter(child, preimage.map).always_counts_one(comb_class)
            for child in strategy(new_tiling).children
        ):
            yield DisjointParameterStrategy(
                strategy,
                new_comb_class.parameters.index(new_param),
                new_param.counters.index(new_preimage),
                False,
            )(new_comb_class)

    def __str__(self) -> str:
        return f"applying '{self.strategy}' to parameters"

    def __repr__(self) -> str:
        return f"DisjointUnionParameterFactory({self.strategy!r})"

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["strategy"] = self.strategy.to_jsonable()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "DisjointUnionParameterFactory":
        strategy = AbstractStrategy.from_dict(d.pop("strategy"))
        assert not d
        return cls(strategy)


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
        if not sum(preimage.tiling.dimensions) == 3:
            return False
        extra_obs, extra_reqs = preimage.extra_obs_and_reqs(comb_class)
        # TODO: check if skew, sum, or point fusion.
        # TODO: Should child be without params?
        return not extra_reqs and (
            all(len(ob) < 3 and not ob.is_single_cell() for ob in extra_obs)
            or not extra_obs
        )

    def get_terms(self, comb_class: Tiling, n: int) -> Terms:
        return comb_class.get_terms(n)

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

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d.pop("ignore_parent")
        return d

    def __str__(self) -> str:
        return "parameter verification"

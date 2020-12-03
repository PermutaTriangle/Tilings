from collections import Counter
from itertools import chain, combinations, product
from random import randint
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Tuple

from sympy import Eq, Expr, Function, Number, Symbol, var

from comb_spec_searcher import Constructor, Strategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
from comb_spec_searcher.typing import (
    Objects,
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
from tilings.algorithms import FactorWithInterleaving
from tilings.assumptions import TrackingAssumption
from tilings.misc import partitions_iterator

from .factor import assumptions_to_add, interleaving_rows_and_cols

Cell = Tuple[int, int]


class DummyConstructor(Constructor):
    def __init__(
        self,
    ):
        pass

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        raise NotImplementedError

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        raise NotImplementedError

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
    ):
        raise NotImplementedError


class ReverseRearrangeConstructor(Constructor):
    def __init__(
        self,
        parent: Tiling,
        children: Tuple[Tiling],
        assumption: TrackingAssumption,
        sub_assumption: TrackingAssumption,
    ):
        self.variable_idx = parent.assumptions.index(assumption)
        self.sub_variable_idx = parent.assumptions.index(sub_assumption)

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        raise NotImplementedError

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        terms: Terms = Counter()
        for param, value in subterms[0](n).items():
            new_param = list(param)
            new_param[self.variable_idx] -= param[self.sub_variable_idx]
            terms[tuple(new_param)] += value
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
    ):
        raise NotImplementedError


class RearrangeConstructor(Constructor[Tiling, GriddedPerm]):
    def __init__(
        self,
        parent: Tiling,
        children: Tuple[Tiling],
        assumption: TrackingAssumption,
        sub_assumption: TrackingAssumption,
        extra_parameters: Dict[str, str],
    ):
        """extra_parameters maps parent to child."""
        new_ass = TrackingAssumption(set(assumption.gps) - set(sub_assumption.gps))
        child = children[0]
        self.new_ass_child_idx = child.extra_parameters.index(
            child.get_assumption_parameter(new_ass)
        )
        self.ass_parent_idx = parent.extra_parameters.index(
            parent.get_assumption_parameter(assumption)
        )
        self.subass_parent_idx = parent.extra_parameters.index(
            parent.get_assumption_parameter(sub_assumption)
        )
        self.subass_child_idx = child.extra_parameters.index(
            child.get_assumption_parameter(sub_assumption)
        )
        self.child_to_parent_param_map = self._build_child_param_map(
            parent,
            child,
            extra_parameters,
            assumption,
            sub_assumption,
        )
        self.parent_to_child_param_map = self._build_parent_param_map(
            parent,
            child,
            extra_parameters,
            assumption,
            sub_assumption,
        )
        self.parent_dict_to_param = self._build_map_dict_to_param(parent)
        self.child_param_to_dict = self._build_map_param_to_dict(child)

    def _build_child_param_map(
        self,
        parent: Tiling,
        child: Tiling,
        extra_parameters: Dict[str, str],
        assumptions: TrackingAssumption,
        sub_assumption: TrackingAssumption,
    ) -> ParametersMap:
        reversed_extra_param = {v: k for k, v in extra_parameters.items()}
        parent_param_to_pos = {
            param: pos for pos, param in enumerate(parent.extra_parameters)
        }
        child_pos_to_parent_pos: List[Tuple[int, ...]] = []
        for pos, param in enumerate(child.extra_parameters):
            to_add: List[int] = []
            if pos == self.subass_child_idx:
                to_add.append(self.ass_parent_idx)
            elif pos == self.new_ass_child_idx:
                to_add.append(self.ass_parent_idx)
            if param in reversed_extra_param:
                to_add.append(parent_param_to_pos[reversed_extra_param[param]])
            child_pos_to_parent_pos.append(tuple(to_add))
        return self._build_param_map(
            tuple(child_pos_to_parent_pos), len(parent.extra_parameters)
        )

    def _build_parent_param_map(
        self,
        parent: Tiling,
        child: Tiling,
        extra_parameters: Dict[str, str],
        assumptions: TrackingAssumption,
        sub_assumption: TrackingAssumption,
    ) -> ParametersMap:
        num_child_param = len(child.extra_parameters)
        # Each pair in the tuple indicate the parent param -> child param
        parent_pos_to_child_pos: Tuple[Tuple[int, int], ...] = tuple(
            (
                parent.extra_parameters.index(pparam),
                child.extra_parameters.index(cparam),
            )
            for pparam, cparam in extra_parameters.items()
        )

        def param_map(param: Parameters) -> Parameters:
            new_param = [-1 for _ in range(num_child_param)]
            for ppos, cpos in parent_pos_to_child_pos:
                new_param[cpos] = param[ppos]
            new_ass_value = param[self.ass_parent_idx] - param[self.subass_parent_idx]
            assert new_param[self.new_ass_child_idx] in (-1, new_ass_value)
            new_param[self.new_ass_child_idx] = new_ass_value
            assert all(v >= 0 for v in new_param)
            return tuple(new_param)

        return param_map

    def _build_map_dict_to_param(
        self,
        tiling: Tiling,
    ) -> Callable[[Dict[str, int]], Parameters]:
        """
        Returns a map the return the param tuple  from the param dictionary for
        the given tilings.
        Should probably live somewhere else.
        """

        tiling_params_order = tiling.extra_parameters
        return lambda d: tuple(d[p] for p in tiling_params_order)

    def _build_map_param_to_dict(
        self,
        tiling: Tiling,
    ) -> Callable[[Parameters], Dict[str, int]]:
        """
        Returns a map the return the param dictionary  from the param tuple for the
        given tilings.
        Should probably live somewhere else.
        """
        tiling_params_order = tiling.extra_parameters
        return lambda p: dict(zip(tiling_params_order, p))

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        raise NotImplementedError

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        terms: Terms = Counter()
        for param, value in subterms[0](n).items():
            new_param = self.child_to_parent_param_map(param)
            terms[new_param] += value
        return terms

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[Tuple[Parameters, Tuple[List[Optional[GriddedPerm]]]]]:
        assert len(subobjs) == 1
        for param, objs in subobjs[0](n).items():
            new_param = self.child_to_parent_param_map(param)
            for obj in objs:
                yield new_param, ([obj],)

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ) -> Tuple[GriddedPerm]:
        assert len(subsamplers) == 1
        parent_param_tuple = self.parent_dict_to_param(parameters)
        child_param_tuple = self.parent_to_child_param_map(parent_param_tuple)
        child_param_dict = self.child_param_to_dict(child_param_tuple)
        return (subsamplers[0](n, **child_param_dict),)


class RearrangeAssumptionStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(
        self, assumption: TrackingAssumption, sub_assumption: TrackingAssumption
    ):
        self.assumption = assumption
        self.sub_assumption = sub_assumption
        super().__init__()

    @staticmethod
    def can_be_equivalent() -> bool:
        return False

    def is_two_way(self, comb_class: Tiling) -> bool:
        return True

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't split the tracking assumption")
        return ReverseRearrangeConstructor(
            comb_class, children, self.assumption, self.sub_assumption
        )

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling]:
        tiling = tiling.remove_assumption(self.assumption)
        new_ass1 = TrackingAssumption(
            set(self.assumption.gps) - set(self.sub_assumption.gps)
        )
        return (tiling.add_assumption(new_ass1),)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> DummyConstructor:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't split the tracking assumption")
        return RearrangeConstructor(
            comb_class,
            children,
            self.assumption,
            self.sub_assumption,
            self.extra_parameters(comb_class, children)[0],
        )

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str]]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        res: Dict[str, str] = {}
        child = children[0]
        for parent_ass, parent_param in zip(
            comb_class.assumptions, comb_class.extra_parameters
        ):
            if parent_ass == self.assumption:
                continue
            child_param = child.extra_parameters[child.assumptions.index(parent_ass)]
            res[parent_param] = child_param
        return (res,)

    def formal_step(self) -> str:
        return f"rearranging the assumption"

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)
        assert len(objs) == 1 and objs[0] is not None
        yield objs[0]

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        """
        The forward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)
        return (obj,)

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d.pop("ignore_parent")
        d.pop("inferrable")
        d.pop("possibly_empty")
        d["assumptions"] = [ass.to_jsonable() for ass in self.assumptions]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RearrangeAssumptionStrategy":
        assumptions = [TrackingAssumption.from_dict(ass) for ass in d["assumptions"]]
        return cls(assumptions)

    @staticmethod
    def get_eq_symbol() -> str:
        return "↣"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(assumption={self.assumption!r}, "
            f"sub_assumption={self.assumption!r}, "
            f"workable={self.workable})"
        )


class RearrangeAssumptionFactory(StrategyFactory[Tiling]):
    def __call__(
        self, comb_class: Tiling, **kwargs
    ) -> Iterator[RearrangeAssumptionStrategy]:
        assumptions = comb_class.assumptions
        for ass1, ass2 in combinations(assumptions, 2):
            if set(ass1.gps).issubset(set(ass2.gps)):
                yield RearrangeAssumptionStrategy(ass2, ass1)
            if set(ass2.gps).issubset(set(ass1.gps)):
                yield RearrangeAssumptionStrategy(ass1, ass2)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    def __str__(self) -> str:
        return "rearrange assumptions"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RearrangeAssumptionFactory":
        return cls()

from collections import Counter
from functools import partial
from itertools import combinations
from typing import Callable, Dict, Iterator, List, Optional, Tuple

import sympy

from comb_spec_searcher import Constructor, Strategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.typing import (
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
from tilings.parameter_counter import ParameterCounter

Cell = Tuple[int, int]


class MultiSet(Counter):
    def subset_of(self, other: "MultiSet"):
        return all(val <= other[key] for key, val in self.items())

    def set_minus(self, other: "MultiSet") -> "MultiSet":
        minus = MultiSet()
        for key, val in self.items():
            new_val = val - other[key]
            if new_val > 0:
                minus[key] = new_val
        return minus

    def __iter__(self) -> Iterator:
        for key, val in self.items():
            for _ in range(val):
                yield key


class RearrangeConstructor(Constructor[Tiling, GriddedPerm]):
    def __init__(
        self,
        parent: Tiling,
        child: Tiling,
        parameter: ParameterCounter,
        sub_parameter: ParameterCounter,
        extra_parameters: Dict[str, str],
    ):
        """
        Constructor for the rearrange strategy.

        The extra_parameters should a dict mapping variable on the parent to the
        associated variable on the child. The variable for `parameter` should not
        appear in the dict since it does not match directly to a variable on the child.
        """
        new_param = ParameterCounter(MultiSet(parameter) - MultiSet(sub_parameter))
        self.new_param_child_idx = child.extra_parameters.index(
            child.get_parameter_name(new_param)
        )
        self.param_parent_idx = parent.extra_parameters.index(
            parent.get_parameter_name(parameter)
        )
        self.subparam_parent_idx = parent.extra_parameters.index(
            parent.get_parameter_name(sub_parameter)
        )
        self.subparam_child_idx = child.extra_parameters.index(
            child.get_parameter_name(sub_parameter)
        )
        self.child_to_parent_param_map = self._build_child_to_parent_param_map(
            parent,
            child,
            extra_parameters,
            parameter,
            sub_parameter,
        )
        self.parent_to_child_param_map = self._build_parent_to_child_param_map(
            parent,
            child,
            extra_parameters,
            parameter,
            sub_parameter,
        )
        self.parent_dict_to_param = self._build_map_dict_to_param(parent)
        self.child_param_to_dict = self._build_map_param_to_dict(child)
        self.eq_subs = self._build_eq_subs(parent, child, extra_parameters)

    def _build_child_to_parent_param_map(
        self,
        parent: Tiling,
        child: Tiling,
        extra_parameters: Dict[str, str],
        parameters: ParameterCounter,
        sub_parameter: ParameterCounter,
    ) -> ParametersMap:
        """
        Build a maps that maps parameters on the child to the corresponding parameters
        on the parent.
        """
        reversed_extra_param = {v: k for k, v in extra_parameters.items()}
        parent_param_to_pos = {
            param: pos for pos, param in enumerate(parent.extra_parameters)
        }
        child_pos_to_parent_pos: List[Tuple[int, ...]] = []
        for pos, param in enumerate(child.extra_parameters):
            to_add: List[int] = []
            if pos == self.subparam_child_idx:
                to_add.append(self.param_parent_idx)
            elif pos == self.new_param_child_idx:
                to_add.append(self.param_parent_idx)
            if param in reversed_extra_param:
                to_add.append(parent_param_to_pos[reversed_extra_param[param]])
            child_pos_to_parent_pos.append(tuple(to_add))
        return self.build_param_map(
            tuple(child_pos_to_parent_pos), len(parent.extra_parameters)
        )

    def param_map_for_rearrange(
        self,
        parent_pos_to_child_pos: Tuple[Tuple[int, int], ...],
        num_child_param: int,
        param: Parameters,
    ) -> Parameters:
        new_param = [-1 for _ in range(num_child_param)]
        for ppos, cpos in parent_pos_to_child_pos:
            new_param[cpos] = param[ppos]
        new_param_value = param[self.param_parent_idx] - param[self.subparam_parent_idx]
        assert new_param[self.new_param_child_idx] in (-1, new_param_value)
        new_param[self.new_param_child_idx] = new_param_value
        assert all(v >= 0 for v in new_param)
        return tuple(new_param)

    def _build_parent_to_child_param_map(
        self,
        parent: Tiling,
        child: Tiling,
        extra_parameters: Dict[str, str],
        parameters: ParameterCounter,
        sub_parameter: ParameterCounter,
    ) -> ParametersMap:
        """
        Build a maps that maps parameters on the parent to the corresponding parameters
        on the child.
        """
        num_child_param = len(child.extra_parameters)
        # Each pair in the tuple indicate the parent param -> child param
        parent_pos_to_child_pos: Tuple[Tuple[int, int], ...] = tuple(
            (
                parent.extra_parameters.index(pparam),
                child.extra_parameters.index(cparam),
            )
            for pparam, cparam in extra_parameters.items()
        )

        return partial(
            self.param_map_for_rearrange, parent_pos_to_child_pos, num_child_param
        )

    @staticmethod
    def _dict_to_param_helper(tiling_params_order, d):
        """
        this is required to be a standalone function to be pickleable
        """
        return tuple(d[p] for p in tiling_params_order)

    @staticmethod
    def _build_map_dict_to_param(
        tiling: Tiling,
    ) -> Callable[[Dict[str, int]], Parameters]:
        """
        Returns a map the return the param tuple  from the param dictionary for
        the given tilings.
        Should probably live somewhere else.
        """

        tiling_params_order = tiling.extra_parameters
        return partial(RearrangeConstructor._dict_to_param_helper, tiling_params_order)

    @staticmethod
    def _param_to_dict_helper(tiling_params_order, p):
        """
        this is required to be a standalone function to be pickleable
        """
        return dict(zip(tiling_params_order, p))

    @staticmethod
    def _build_map_param_to_dict(
        tiling: Tiling,
    ) -> Callable[[Parameters], Dict[str, int]]:
        """
        Returns a map the return the param dictionary  from the param tuple for the
        given tilings.
        Should probably live somewhere else.
        """
        tiling_params_order = tiling.extra_parameters
        return partial(RearrangeConstructor._param_to_dict_helper, tiling_params_order)

    def _build_eq_subs(
        self, parent: Tiling, child: Tiling, extra_parameters: Dict[str, str]
    ) -> dict:
        """
        Build the substitution dict needed to compute the equation.
        """
        subs = {
            sympy.var(child): sympy.var(parent)
            for parent, child in extra_parameters.items()
        }
        new_param_var_child = sympy.var(
            child.extra_parameters[self.new_param_child_idx]
        )
        param_var_parent = sympy.var(parent.extra_parameters[self.param_parent_idx])
        subparam_var_child = sympy.var(child.extra_parameters[self.subparam_child_idx])
        subs[new_param_var_child] = subs.get(new_param_var_child, 1) * param_var_parent
        subs[subparam_var_child] *= param_var_parent
        return subs

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        rhs = rhs_funcs[0].subs(self.eq_subs, simultaneous=True)
        return sympy.Eq(lhs_func, rhs)

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

    def equiv(
        self, other: "Constructor", data: Optional[object] = None
    ) -> Tuple[bool, Optional[object]]:
        return isinstance(other, type(self)), None


class ReverseRearrangeConstructor(RearrangeConstructor):
    def __init__(
        self,
        parent: Tiling,
        child: Tiling,
        parameter: ParameterCounter,
        sub_parameter: ParameterCounter,
        extra_parameters: Dict[str, str],
    ):
        super().__init__(parent, child, parameter, sub_parameter, extra_parameters)
        self.child_to_parent_param_map, self.parent_to_child_param_map = (
            self.parent_to_child_param_map,
            self.child_to_parent_param_map,
        )
        self.parent_dict_to_param = self._build_map_dict_to_param(child)
        self.child_param_to_dict = self._build_map_param_to_dict(parent)

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        return super().get_equation(rhs_funcs[0], (lhs_func,))


class RearrangeParameterStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(self, parameter: ParameterCounter, sub_parameter: ParameterCounter):
        self.parameter = parameter
        self.sub_parameter = sub_parameter
        super().__init__()

    @staticmethod
    def can_be_equivalent() -> bool:
        return False

    @staticmethod
    def is_two_way(comb_class: Tiling) -> bool:
        return True

    @staticmethod
    def is_reversible(comb_class: Tiling) -> bool:
        return True

    @staticmethod
    def shifts(
        comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[int, ...]:
        return (0,)

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> ReverseRearrangeConstructor:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't rearrange the parameter")
        return ReverseRearrangeConstructor(
            comb_class,
            children[0],
            self.parameter,
            self.sub_parameter,
            self.extra_parameters(comb_class, children)[0],
        )

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        tiling = comb_class.remove_parameter(self.parameter)
        new_param1 = ParameterCounter(
            MultiSet(self.parameter) - MultiSet(self.sub_parameter)
        )
        return (tiling.add_parameter(new_param1),)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> RearrangeConstructor:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't rearrange the parameter")
        return RearrangeConstructor(
            comb_class,
            children[0],
            self.parameter,
            self.sub_parameter,
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
        for parent_param, parent_param_name in zip(
            comb_class.parameters, comb_class.extra_parameters
        ):
            if parent_param == self.parameter:
                continue
            res[parent_param_name] = child.get_parameter_name(parent_param)
        return (res,)

    def formal_step(self) -> str:
        return f"rearranging the parameter {self.parameter} and {self.sub_parameter}"

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
        d.pop("workable")
        d["parameter"] = self.parameter.to_jsonable()
        d["sub_parameter"] = self.sub_parameter.to_jsonable()
        return d

    def __repr__(self) -> str:
        args = ", ".join(
            [
                f"parameter={self.parameter!r}",
                f"sub_parameter={self.sub_parameter!r}",
            ]
        )
        return f"{self.__class__.__name__}({args})"

    @classmethod
    def from_dict(cls, d: dict) -> "RearrangeParameterStrategy":
        parameter = ParameterCounter.from_dict(d.pop("parameter"))
        sub_parameter = ParameterCounter.from_dict(d.pop("sub_parameter"))
        assert not d
        return cls(parameter, sub_parameter)

    @staticmethod
    def get_eq_symbol() -> str:
        return "↣"


class RearrangeParameterFactory(StrategyFactory[Tiling]):
    def __call__(self, comb_class: Tiling) -> Iterator[RearrangeParameterStrategy]:
        parameters = comb_class.parameters
        for param1, param2 in combinations(parameters, 2):
            if MultiSet(param1).subset_of(MultiSet(param2)):
                yield RearrangeParameterStrategy(param2, param1)
            if MultiSet(param2).subset_of(MultiSet(param1)):
                yield RearrangeParameterStrategy(param1, param2)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    def __str__(self) -> str:
        return "rearrange parameters"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RearrangeParameterFactory":
        return cls()

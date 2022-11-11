from collections import Counter
from itertools import product
from random import randint
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Tuple

from sympy import Eq, Expr, Function, Number, Symbol, var

from comb_spec_searcher import Constructor, Strategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
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
from tilings.assumptions import ComponentAssumption, TrackingAssumption

Cell = Tuple[int, int]


class AddAssumptionsConstructor(Constructor):
    """
    The constructor used to count when a new variable is added.
    """

    def __init__(
        self,
        parent: Tiling,
        child: Tiling,
        new_parameters: Iterable[str],
        extra_parameters: Dict[str, str],
    ):
        #  parent parameter -> child parameter mapping
        self.extra_parameters = extra_parameters
        #  the paramater that was added, to count we must sum over all possible values
        self.new_parameters = tuple(new_parameters)
        self.child_param_map = self._build_child_param_map(parent, child)

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        rhs_func = rhs_funcs[0]
        subs: Dict[Symbol, Expr] = {
            var(child): var(parent) for parent, child in self.extra_parameters.items()
        }
        for k in self.new_parameters:
            subs[k] = Number(1)
        return Eq(lhs_func, rhs_func.subs(subs, simultaneous=True))

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        assert len(subterms) == 1
        return self._push_add_assumption(n, subterms[0], self.child_param_map)

    @staticmethod
    def _push_add_assumption(
        n: int,
        child_terms: Callable[[int], Terms],
        child_param_map: ParametersMap,
    ) -> Terms:
        new_terms: Terms = Counter()
        for param, value in child_terms(n).items():
            new_terms[child_param_map(param)] += value
        return new_terms

    def _build_child_param_map(self, parent: Tiling, child: Tiling) -> ParametersMap:
        parent_param_to_pos = {
            param: pos for pos, param in enumerate(parent.extra_parameters)
        }
        child_param_to_parent_param = {v: k for k, v in self.extra_parameters.items()}
        child_pos_to_parent_pos: Tuple[Tuple[int, ...], ...] = tuple(
            tuple()
            if param in self.new_parameters
            else (parent_param_to_pos[child_param_to_parent_param[param]],)
            for param in child.extra_parameters
        )
        return self.build_param_map(
            child_pos_to_parent_pos, len(parent.extra_parameters)
        )

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[Tuple[Parameters, Tuple[List[Optional[GriddedPerm]], ...]]]:
        for param, gps in subobjs[0](n).items():
            yield self.child_param_map(param), (gps,)

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ):
        subrec = subrecs[0]
        subsampler = subsamplers[0]
        random_choice = randint(1, parent_count)
        new_params = {self.extra_parameters[k]: val for k, val in parameters.items()}
        res = 0
        for values in product(*[range(n + 1) for _ in self.new_parameters]):
            for k, val in zip(self.new_parameters, values):
                new_params[k] = val
            res += subrec(n, **new_params)
            if random_choice <= res:
                return (subsampler(n, **new_params),)

    def equiv(
        self, other: "Constructor", data: Optional[object] = None
    ) -> Tuple[bool, Optional[object]]:
        return (
            isinstance(other, type(self))
            and len(other.new_parameters) == len(self.new_parameters)
            and AddAssumptionsConstructor.extra_params_equiv(
                (self.extra_parameters,), (other.extra_parameters,)
            ),
            None,
        )


class RemoveAssumptionsConstructor(Constructor):
    """
    The constructor used to count when a variable the same as n is removed.
    """

    def __init__(
        self,
        parent: Tiling,
        child: Tiling,
        parameter: str,
        extra_parameters: Dict[str, str],
    ):
        #  parent parameter -> child parameter mapping
        self.extra_parameters = extra_parameters
        #  the paramater that was added, to count we must sum over all possible values
        self.parameter = parameter
        self.parameter_idx = parent.extra_parameters.index(self.parameter)
        self.child_param_map = self._build_child_param_map(parent, child)

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        rhs_func = rhs_funcs[0]
        subs: Dict[Symbol, Expr] = {
            var(child): var(parent) for parent, child in self.extra_parameters.items()
        }
        subs[var("x")] = var("x") * var(self.parameter)
        return Eq(lhs_func, rhs_func.subs(subs, simultaneous=True))

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        assert len(subterms) == 1
        return self._push_add_assumption(n, subterms[0], self.child_param_map)

    def _push_add_assumption(
        self,
        n: int,
        child_terms: Callable[[int], Terms],
        child_param_map: ParametersMap,
    ) -> Terms:
        new_terms: Terms = Counter()
        for param, value in child_terms(n).items():
            new_param = list(child_param_map(param))
            new_param[self.parameter_idx] = n
            new_terms[tuple(new_param)] += value
        return new_terms

    def _build_child_param_map(self, parent: Tiling, child: Tiling) -> ParametersMap:
        parent_param_to_pos = {
            param: pos for pos, param in enumerate(parent.extra_parameters)
        }
        child_param_to_parent_param = {v: k for k, v in self.extra_parameters.items()}
        child_pos_to_parent_pos: Tuple[Tuple[int, ...], ...] = tuple(
            (parent_param_to_pos[child_param_to_parent_param[param]],)
            for param in child.extra_parameters
        )
        return self.build_param_map(
            child_pos_to_parent_pos, len(parent.extra_parameters)
        )

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

    def equiv(
        self, other: "Constructor", data: Optional[object] = None
    ) -> Tuple[bool, Optional[object]]:
        return (
            isinstance(other, type(self))
            and len(other.parameter) == len(self.parameter)
            and AddAssumptionsConstructor.extra_params_equiv(
                (self.extra_parameters,), (other.extra_parameters,)
            ),
            None,
        )


class AddAssumptionsStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(self, assumptions: Iterable[TrackingAssumption], workable=False):
        self.assumptions = tuple(set(assumptions))
        super().__init__(
            ignore_parent=False,
            inferrable=True,
            possibly_empty=False,
            workable=workable,
        )

    def can_be_equivalent(self) -> bool:
        return False

    def is_two_way(self, comb_class: Tiling):
        return False

    def is_reversible(self, comb_class: Tiling) -> bool:
        return all(
            not isinstance(assumption, ComponentAssumption)
            and frozenset(gp.pos[0] for gp in assumption.gps) == comb_class.active_cells
            for assumption in self.assumptions
        )

    def shifts(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[int, ...]:
        return (0,)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        if any(assumption in comb_class.assumptions for assumption in self.assumptions):
            raise StrategyDoesNotApply("The assumption is already on the tiling.")
        return (comb_class.add_assumptions(self.assumptions),)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> AddAssumptionsConstructor:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't split the tracking assumption")
        new_parameters = [
            children[0].get_assumption_parameter(ass) for ass in self.assumptions
        ]
        return AddAssumptionsConstructor(
            comb_class,
            children[0],
            new_parameters,
            self.extra_parameters(comb_class, children)[0],
        )

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        if children is None:
            children = self.decomposition_function(comb_class)
        assert idx == 0
        child = children[idx]
        assert len(self.assumptions) == 1
        assumption = self.assumptions[0]
        assert len(assumption.gps) == len(comb_class.active_cells)
        parameter = child.get_assumption_parameter(self.assumptions[0])
        extra_params = {
            child.get_assumption_parameter(ass): comb_class.get_assumption_parameter(
                ass
            )
            for ass in child.assumptions
            if ass != assumption
        }

        return RemoveAssumptionsConstructor(child, comb_class, parameter, extra_params)

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str]]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        child = children[0]
        return (
            {
                comb_class.get_assumption_parameter(
                    ass
                ): child.get_assumption_parameter(ass)
                for ass in comb_class.assumptions
            },
        )

    def formal_step(self) -> str:
        if len(self.assumptions) == 1:
            return f"adding the assumption '{self.assumptions[0]}'"
        assumptions = ", ".join([f"'{ass}'" for ass in self.assumptions])
        return f"adding the assumptions '{assumptions}'"

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
    def from_dict(cls, d: dict) -> "AddAssumptionsStrategy":
        assumptions = [TrackingAssumption.from_dict(ass) for ass in d["assumptions"]]
        return cls(assumptions)

    @staticmethod
    def get_eq_symbol() -> str:
        return "↣"

    def __repr__(self):
        return (
            self.__class__.__name__
            + f"(assumptions={repr(self.assumptions)}, workable={self.workable})"
        )


class AddAssumptionFactory(StrategyFactory[Tiling]):
    def __call__(self, comb_class: Tiling) -> Iterator[Rule]:
        for assumption in comb_class.assumptions:
            without = comb_class.remove_assumption(assumption)
            strategy = AddAssumptionsStrategy((assumption,))
            yield strategy(without)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    def __str__(self) -> str:
        return "add assumptions"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AddAssumptionFactory":
        return cls()

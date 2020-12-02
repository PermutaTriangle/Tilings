from collections import Counter
from itertools import chain, product, combinations
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


class RearrangeConstructor(Constructor):
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
            print(param, value)
            new_param = list(param)
            new_param[self.variable_idx] += param[self.sub_variable_idx]
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


class RearrangeAssumptionStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(
        self, assumption: TrackingAssumption, sub_assumption: TrackingAssumption
    ):
        self.assumption = assumption
        self.sub_assumption = sub_assumption
        super().__init__()

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

    @staticmethod
    def can_be_equivalent() -> bool:
        return True

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
            comb_class, children, self.assumption, self.sub_assumption
        )

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str]]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        raise NotImplementedError

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

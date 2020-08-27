from itertools import chain, product
from typing import Dict, Iterable, Iterator, Optional, Tuple

from sympy import Eq, Expr, Function, Number, Symbol, var

from comb_spec_searcher import (
    CombinatorialObject,
    Constructor,
    Strategy,
    StrategyFactory,
)
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
from comb_spec_searcher.strategies.constructor import (
    RelianceProfile,
    SubGens,
    SubRecs,
    SubSamplers,
)
from tilings import GriddedPerm, Tiling
from tilings.algorithms import FactorWithInterleaving
from tilings.assumptions import TrackingAssumption
from tilings.misc import partitions_iterator

from .factor import assumptions_to_add, interleaving_rows_and_cols

Cell = Tuple[int, int]


class AddAssumptionsConstructor(Constructor):
    """
    The constructor used to count when a new variable is added.
    """

    def __init__(self, new_parameters: Iterable[str], extra_parameters: Dict[str, str]):
        #  parent parameter -> child parameter mapping
        self.extra_parameters = extra_parameters
        #  the paramater that was added, to count we must sum over all possible values
        self.new_parameters = tuple(new_parameters)

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

    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
        subrec = subrecs[0]
        new_params = {self.extra_parameters[k]: val for k, val in parameters.items()}
        res = 0
        for values in product(*[range(n + 1) for _ in self.new_parameters]):
            for k, val in zip(self.new_parameters, values):
                new_params[k] = val
            res += subrec(n, **new_params)
        return res

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
        **parameters: int,
    ):
        raise NotImplementedError


class AddAssumptionsStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(self, assumptions: Iterable[TrackingAssumption], workable=False):
        self.assumptions = tuple(set(assumptions))
        super().__init__(
            ignore_parent=False,
            inferrable=True,
            possibly_empty=False,
            workable=workable,
        )

    @staticmethod
    def can_be_equivalent() -> bool:
        return False

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling]:
        if any(assumption in tiling.assumptions for assumption in self.assumptions):
            raise StrategyDoesNotApply("The assumption is already on the tiling.")
        return (tiling.add_assumptions(self.assumptions),)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> AddAssumptionsConstructor:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't split the tracking assumption")
        new_parameters = [children[0].get_parameter(ass) for ass in self.assumptions]
        return AddAssumptionsConstructor(
            new_parameters, self.extra_parameters(comb_class, children)[0]
        )

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
                comb_class.get_parameter(ass): child.get_parameter(ass)
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
    ) -> GriddedPerm:
        """
        The forward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)
        assert len(objs) == 1 and objs[0] is not None
        return objs[0]

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
    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[Rule]:
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


class AddInterleavingAssumptionFactory(StrategyFactory[Tiling]):
    def __init__(self, unions: bool = False):
        self.unions = unions

    @staticmethod
    def strategy_from_components(
        comb_class: Tiling, components: Tuple[Tuple[Cell, ...], ...]
    ) -> Iterator[Rule]:
        """
        Yield an AddAssumption strategy for the given component if needed.
        """
        cols, rows = interleaving_rows_and_cols(components)
        assumptions = set(
            ass
            for ass in chain.from_iterable(
                assumptions_to_add(cells, cols, rows) for cells in components
            )
            if ass not in comb_class.assumptions
        )
        if assumptions:
            strategy = AddAssumptionsStrategy(assumptions, workable=True)
            yield strategy(comb_class)

    # TODO: monotone?
    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[Rule]:
        factor_algo = FactorWithInterleaving(comb_class)
        if factor_algo.factorable():
            min_comp = tuple(tuple(part) for part in factor_algo.get_components())
            if self.unions:
                for partition in partitions_iterator(min_comp):
                    components = tuple(
                        tuple(chain.from_iterable(part)) for part in partition
                    )
                    yield from self.strategy_from_components(comb_class, components)
            yield from self.strategy_from_components(comb_class, min_comp)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    def __str__(self) -> str:
        return "add interleaving assumptions to factor"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["unions"] = self.unions
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AddInterleavingAssumptionFactory":
        return cls(**d)

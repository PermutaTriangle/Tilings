from typing import Iterable, Iterator, Optional, Tuple


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
from sympy import Eq, Function
from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption


class AddAssumptionConstructor(Constructor):
    """
    The constructor used to cound when a new variable is added.
    """

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


class AddAssumptionStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(self, gps: Iterable[GriddedPerm]):
        self.assumption = TrackingAssumption(gps)
        super().__init__(
            ignore_parent=False, inferrable=True, possibly_empty=False, workable=True
        )

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling]:
        return (tiling.add_assumption(self.assumption),)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None,
    ) -> AddAssumptionConstructor:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't split the tracking assumption")
        return AddAssumptionConstructor()

    def formal_step(self) -> str:
        return "adding the assumption '{}'".format(self.assumption)

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
    def from_dict(cls, d: dict) -> "AddAssumptionStrategy":
        return cls(**d)

    def __repr__(self):
        return self.__class__.__name__ + "(gps={})".format(
            repr(tuple(self.assumption.gps))
        )


class AddAssumptionFactory(StrategyFactory[Tiling]):
    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[Rule]:
        for assumption in comb_class.assumptions:
            without = comb_class.remove_assumption(assumption)
            strategy = AddAssumptionStrategy(assumption.gps)
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

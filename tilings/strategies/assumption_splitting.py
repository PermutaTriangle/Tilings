from collections import defaultdict
from functools import reduce
from itertools import product
from operator import mul
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple

from sympy import Eq, Function, var

from comb_spec_searcher import Constructor, Strategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.typing import (
    Parameters,
    RelianceProfile,
    SubObjects,
    SubRecs,
    SubSamplers,
    SubTerms,
    Terms,
)
from comb_spec_searcher.utils import compositions
from tilings import GriddedPerm, Tiling
from tilings.algorithms import factor
from tilings.assumptions import (
    SkewComponentAssumption,
    SumComponentAssumption,
    TrackingAssumption,
)

Cell = Tuple[int, int]


class Split(Constructor):
    """
    The constructor used to cound when a variable is counted by some multiple
    disjoint subvariables.
    """

    def __init__(self, split_parameters: Dict[str, Tuple[str, ...]]):
        self.split_parameters = split_parameters

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        rhs_func = rhs_funcs[0]
        subs: Dict[var, List[var]] = defaultdict(list)
        for parent, children in self.split_parameters.items():
            for child in children:
                subs[var(child)].append(var(parent))
        var_subs = {
            parent: reduce(mul, children, 1) for parent, children in subs.items()
        }
        return Eq(lhs_func, rhs_func.subs(var_subs, simultaneous=True))

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_terms(self, subterms: SubTerms, n: int) -> Terms:
        raise NotImplementedError

    def _valid_compositions(self, **parameters: int) -> Iterator[Dict[str, int]]:
        """
        For each parameter which splits according to split_parameters, it will
        take a composition of the value for parameter and assign it to the
        subparameters it is split into.

        TODO: this should consider reliance profiles, and when variables are
        sub variable of other variables.
        """

        def compositions_dict(value: int, parameters: Tuple[str, ...]):
            for comp in compositions(
                value,
                len(parameters),
                (0,) * len(parameters),
                (None,) * len(parameters),
            ):
                yield dict(zip(parameters, comp))

        def union_params(
            sub_params: Tuple[Dict[str, int], ...]
        ) -> Optional[Dict[str, int]]:
            new_params: Dict[str, int] = dict()
            for params in sub_params:
                for k, val in params.items():
                    if k in new_params:
                        if val != new_params[k]:
                            return None
                    else:
                        new_params[k] = val
            return new_params

        for sub_params in product(
            *[
                compositions_dict(val, self.split_parameters[key])
                for key, val in parameters.items()
            ]
        ):
            new_params = union_params(sub_params)
            if new_params is not None:
                yield new_params

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


class SplittingStrategy(Strategy[Tiling, GriddedPerm]):
    """
    A strategy which splits each TrackingAssumption into sub TrackingAssumptions,
    according to the factors of the underlying tiling.

    TODO: iterate over all possible union of factors
    """

    FACTOR_ALGO = {
        "none": factor.Factor,
        "monotone": factor.FactorWithMonotoneInterleaving,
        "all": factor.FactorWithInterleaving,
    }

    def __init__(
        self,
        interleaving: str = "none",
        ignore_parent: bool = False,
        inferrable: bool = True,
        possibly_empty: bool = True,
        workable: bool = True,
    ):
        try:
            self.factor_class = SplittingStrategy.FACTOR_ALGO[interleaving]
        except KeyError as e:
            raise ValueError(
                "interleaving argument must be in "
                f"{list(SplittingStrategy.FACTOR_ALGO)}"
            ) from e
        super().__init__(
            ignore_parent=ignore_parent,
            inferrable=inferrable,
            possibly_empty=possibly_empty,
            workable=workable,
        )

    @staticmethod
    def can_be_equivalent() -> bool:
        return False

    def decomposition_function(self, tiling: Tiling) -> Optional[Tuple[Tiling]]:
        if not tiling.assumptions:
            return None
        components = self.factor_class(tiling.remove_assumptions()).get_components()
        if len(components) == 1:
            return None
        new_assumptions: List[TrackingAssumption] = []
        for ass in tiling.assumptions:
            new_assumptions.extend(self._split_assumption(ass, components))
        return (Tiling(tiling.obstructions, tiling.requirements, new_assumptions),)

    def _split_assumption(
        self, assumption: TrackingAssumption, components: Tuple[Set[Cell], ...]
    ) -> List[TrackingAssumption]:
        if isinstance(assumption, SkewComponentAssumption):
            return self._split_skew_assumption(assumption)
        if isinstance(assumption, SumComponentAssumption):
            return self._split_sum_assumption(assumption)
        return self._split_tracking_assumption(assumption, components)

    @staticmethod
    def _split_tracking_assumption(
        assumption: TrackingAssumption, components: Tuple[Set[Cell], ...]
    ) -> List[TrackingAssumption]:
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
        return [assumption.__class__(gps) for gps in split_gps if gps]

    def _split_skew_assumption(
        self, assumption: SkewComponentAssumption
    ) -> List[TrackingAssumption]:
        decomposition = self.skew_decomposition(assumption.cells)
        return [
            SkewComponentAssumption(
                GriddedPerm.single_cell((0,), cell) for cell in cells
            )
            for cells in decomposition
        ]

    def _split_sum_assumption(
        self, assumption: SumComponentAssumption
    ) -> List[TrackingAssumption]:
        decomposition = self.sum_decomposition(assumption.cells)
        return [
            SumComponentAssumption(
                GriddedPerm.single_cell((0,), cell) for cell in cells
            )
            for cells in decomposition
        ]

    @staticmethod
    def sum_decomposition(
        cells: Iterable[Cell], skew: bool = False
    ) -> List[List[Cell]]:
        """
        Returns the sum decomposition of the cells.
        If skew is True then returns the skew decomposition instead.
        """
        cells = sorted(cells)
        decomposition: List[List[Cell]] = []
        while len(cells) > 0:
            x = cells[0][0]  # x boundary, maximum in both cases
            y = cells[0][1]  # y boundary, maximum in sum, minimum in skew
            change = True
            while change:
                change = False
                for c in cells:
                    if c[0] <= x:
                        if (skew and c[1] < y) or (not skew and c[1] > y):
                            y = c[1]
                            change = True
                    if (skew and c[1] >= y) or (not skew and c[1] <= y):
                        if c[0] > x:
                            x = c[0]
                            change = True
            decomposition.append([])
            new_cells = []
            for c in cells:
                if c[0] <= x:
                    decomposition[-1].append(c)
                else:
                    new_cells.append(c)
            cells = new_cells
        return decomposition

    def skew_decomposition(self, cells: Iterable[Cell]) -> List[List[Cell]]:
        """
        Returns the skew decomposition of the cells
        """
        return self.sum_decomposition(cells, skew=True)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Split:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't split the tracking assumption")
        child = children[0]
        split_parameters: Dict[str, Tuple[str, ...]] = {"n": ("n",)}
        components = self.factor_class(comb_class.remove_assumptions()).get_components()
        for idx, assumption in enumerate(comb_class.assumptions):
            split_assumptions = self._split_assumption(assumption, components)
            child_vars = tuple(
                sorted(
                    "k_{}".format(child.assumptions.index(ass))
                    for ass in split_assumptions
                )
            )
            split_parameters["k_{}".format(idx)] = child_vars
        return Split(split_parameters)

    @staticmethod
    def formal_step() -> str:
        return "splitting the assumptions"

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
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

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["interleaving"] = next(
            k
            for k, v in SplittingStrategy.FACTOR_ALGO.items()
            if v == self.factor_class
        )
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "SplittingStrategy":
        return cls(**d)

    @staticmethod
    def get_eq_symbol() -> str:
        return "↣"

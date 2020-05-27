from typing import Dict, Iterable, Iterator, Optional, Set, Tuple

from sympy import Eq, Function

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
from tilings.algorithms import ComponentFusion, Fusion
from tilings.assumptions import TrackingAssumption

__all__ = ["FusionStrategy", "ComponentFusionStrategy"]


class FusionConstructor(Constructor):
    """
    The fusion constructor. It will multiply by (fuse_paramater + 1), and
    otherwise pass on the variables.

    The parameters given should be a dictionary. Each child variable should
    point to some parent variable with the exception of the fuse variable which
    will not point if it was just added. If [ A | A ] fuses to [ A ] then we
    assume any one sided variable maps to the [ A ].
    """

    def __init__(
        self,
        fuse_parameter: str,
        extra_parameters: Dict[str, str],
        left_sided_parameters=Iterable[str],
        right_sided_parameters=Iterable[str],
    ):
        self.extra_parameters = extra_parameters
        self.fuse_parameter = fuse_parameter
        self.left_sided_parameters = frozenset(left_sided_parameters)
        self.right_sided_parameters = frozenset(right_sided_parameters)

    def is_equivalence(self) -> bool:
        return False

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        raise NotImplementedError

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
        """
        Let k be the fuse_parameter, then we should get
            (k + 1) * subrec(n, **parameters)
        where extra_parameters are updated according to extra_parameters.
        """
        subrec = subrecs[0]
        new_params = {
            child_var: parameters[parent_var]
            for child_var, parent_var in self.extra_parameters.items()
        }
        fuse_parameter = self.fuse_parameter
        if fuse_parameter in self.extra_parameters:
            # this is the number of points in the prefused region that is tracked
            # by  the fuse variable.
            number_points_in_fuse_region = parameters[
                self.extra_parameters[fuse_parameter]
            ]
            # pass on parameters and multiply by k + 1
            if not self.left_sided_parameters and not self.right_sided_parameters:
                return (number_points_in_fuse_region + 1) * subrec(n, **new_params)
            min_left_points = 0
            max_left_points = n
            if fuse_parameter in self.left_sided_parameters:
                min_left_points += number_points_in_fuse_region
            if fuse_parameter in self.right_sided_parameters:
                max_left_points -= number_points_in_fuse_region
            res = 0
            for number_of_left_points in range(min_left_points, max_left_points + 1):
                number_of_right_points = (
                    number_of_left_points - number_points_in_fuse_region
                )
                res += subrec(
                    n,
                    **{
                        k: (
                            val + number_of_left_points
                            if k in self.right_sided_parameters
                            else val + number_of_right_points
                            if k in self.left_sided_parameters
                            else val
                        )
                        for k, val in new_params.items()
                    },
                )
            return res
        else:
            # sum over all possible k
            # TODO: valid k_val should be computed in reliance profile before
            # asking subrec
            res = 0
            for k_val in range(n + 1):
                # add the fuse parameter to the new paramaters
                new_params[fuse_parameter] = k_val
                if not self.left_sided_parameters and not self.right_sided_parameters:
                    res += (k_val + 1) * subrec(n, **new_params)
                else:
                    for number_of_left_points in range(0, k_val + 1):
                        number_of_right_points = k_val - number_of_left_points
                        res += subrec(
                            n,
                            **{
                                k: (
                                    val + number_of_left_points
                                    if k in self.right_sided_parameters
                                    else val + number_of_right_points
                                    if k in self.left_sided_parameters
                                    else val
                                )
                                for k, val in new_params.items()
                            },
                        )
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
        **parameters: int
    ):
        raise NotImplementedError

    @staticmethod
    def get_eq_symbol() -> str:
        return "↣"


class FusionStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(self, row_idx=None, col_idx=None, tracked: bool = False):
        self.col_idx = col_idx
        self.row_idx = row_idx
        self.tracked = tracked
        if not sum(1 for x in (self.col_idx, self.row_idx) if x is not None) == 1:
            raise RuntimeError("Cannot specify a row and a columns")
        super().__init__(
            ignore_parent=False, inferrable=True, possibly_empty=False, workable=True
        )

    def fusion_algorithm(self, tiling: Tiling) -> Fusion:
        return Fusion(
            tiling, row_idx=self.row_idx, col_idx=self.col_idx, tracked=self.tracked
        )

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        algo = self.fusion_algorithm(comb_class)
        if algo.fusable():
            return (algo.fused_tiling(),)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None,
    ) -> FusionConstructor:
        if not self.tracked:
            # constructor only enumerates when tracked.
            return FusionConstructor("n", {})
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")

        extra_parameters, left_sided_params, right_sided_params = self.extra_parameters(
            comb_class, children
        )
        return FusionConstructor(
            self._fuse_parameter(comb_class),
            extra_parameters,
            left_sided_params,
            right_sided_params,
        )

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Dict[str, str], Set[str], Set[str]]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        algo = self.fusion_algorithm(comb_class)
        child = children[0]
        mapped_assumptions = [
            TrackingAssumption(gps) for gps in algo.assumptions_fuse_counters
        ]
        extra_parameters = {
            child.get_parameter(ass): k
            for k, ass in zip(comb_class.extra_parameters(), mapped_assumptions)
        }
        left_sided_params: Set[str] = set()
        right_sided_params: Set[str] = set()
        for assumption, mapped_assumption in zip(
            comb_class.assumptions, mapped_assumptions
        ):
            left_sided = algo.is_left_sided_assumption(assumption)
            right_sided = algo.is_right_sided_assumption(assumption)
            if left_sided and not right_sided:
                left_sided_params.add(child.get_parameter(mapped_assumption))
            elif right_sided and not left_sided:
                right_sided_params.add(child.get_parameter(mapped_assumption))
        return extra_parameters, left_sided_params, right_sided_params

    def _fuse_parameter(self, comb_class: Tiling) -> str:
        algo = self.fusion_algorithm(comb_class)
        child = algo.fused_tiling()
        fuse_assumption = algo.new_assumption()
        idx = child.assumptions.index(fuse_assumption)
        return "k_{}".format(idx)

    def formal_step(self) -> str:
        fusing = "rows" if self.row_idx is not None else "columns"
        idx = self.row_idx if self.row_idx is not None else self.col_idx
        return "fuse {} {} and {}".format(fusing, idx, idx + 1)

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

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d.pop("ignore_parent")
        d.pop("inferrable")
        d.pop("possibly_empty")
        d.pop("workable")
        d["row_idx"] = self.row_idx
        d["col_idx"] = self.col_idx
        d["tracked"] = self.tracked
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "FusionStrategy":
        return cls(**d)


class ComponentFusionConstructor(FusionConstructor):
    pass


class ComponentFusionStrategy(FusionStrategy):
    def __init__(self, row_idx=None, col_idx=None, tracked: bool = False):
        assert not tracked, "tracking not implemented for component fusion"
        super().__init__(row_idx=row_idx, col_idx=col_idx, tracked=False)

    def fusion_algorithm(self, tiling: Tiling) -> Fusion:
        return ComponentFusion(tiling, row_idx=self.row_idx, col_idx=self.col_idx)

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None,
    ) -> ComponentFusionConstructor:
        return ComponentFusionConstructor(self._fuse_parameter(comb_class), {"n": "n"})

    def formal_step(self) -> str:
        fusing = "rows" if self.row_idx is not None else "columns"
        idx = self.row_idx if self.row_idx is not None else self.col_idx
        return "component fuse {} {} and {}".format(fusing, idx, idx + 1)


class FusionFactory(StrategyFactory[Tiling]):
    def __init__(self, tracked: bool = False):
        self.tracked = tracked

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[Rule]:
        cols, rows = comb_class.dimensions
        for row_idx in range(rows - 1):
            algo = Fusion(comb_class, row_idx=row_idx, tracked=self.tracked)
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield FusionStrategy(row_idx=row_idx, tracked=self.tracked)(
                    comb_class, (fused_tiling,)
                )
        for col_idx in range(cols - 1):
            algo = Fusion(comb_class, col_idx=col_idx, tracked=self.tracked)
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield FusionStrategy(col_idx=col_idx, tracked=self.tracked)(
                    comb_class, (fused_tiling,)
                )

    def __str__(self) -> str:
        if self.tracked:
            return "tracked fusion"
        return "fusion"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "(tracked={})".format(self.tracked)

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["tracked"] = self.tracked
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "FusionFactory":
        assert (
            len(d) == 1 and "tracked" in d
        ), "FusionFactory takes only tracked argument"
        return cls(**d)


class ComponentFusionFactory(StrategyFactory[Tiling]):
    def __init__(self, tracked: bool = False):
        assert not tracked, "tracking not implemented for component fusion"
        self.tracked = tracked

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[Rule]:
        if comb_class.requirements:
            return
        cols, rows = comb_class.dimensions
        for row_idx in range(rows - 1):
            algo = ComponentFusion(comb_class, row_idx=row_idx)
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield ComponentFusionStrategy(row_idx=row_idx)(
                    comb_class, (fused_tiling,)
                )
        for col_idx in range(cols - 1):
            algo = ComponentFusion(comb_class, col_idx=col_idx)
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield ComponentFusionStrategy(col_idx=col_idx)(
                    comb_class, (fused_tiling,)
                )

    def __str__(self) -> str:
        return "component fusion"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["tracked"] = self.tracked
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ComponentFusionFactory":
        assert (
            len(d) == 1 and "tracked" in d
        ), "ComponentFusionFactory takes only tracked argument"
        return cls(**d)

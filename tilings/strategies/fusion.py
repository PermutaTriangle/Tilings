from collections import defaultdict
from itertools import product
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple

from sympy import Eq, Function

from comb_spec_searcher import Constructor, Strategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
from comb_spec_searcher.strategies.constructor import RelianceProfile, SubRecs
from tilings import GriddedPerm, Tiling
from tilings.algorithms import ComponentFusion, Fusion
from tilings.assumptions import TrackingAssumption

__all__ = ["FusionStrategy", "ComponentFusionStrategy"]

SubGens = Tuple[Callable[..., Iterator[GriddedPerm]], ...]
SubRec = Callable[..., int]
SubSamplers = Tuple[Callable[..., GriddedPerm], ...]


class FusionConstructor(Constructor[Tiling, GriddedPerm]):
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
        both_sided_parameters=Iterable[str],
    ):
        # parent -> child parameters
        self.extra_parameters = extra_parameters
        # the reverse of the above list, although different parent parameters could
        # point to the same child parameter as when an assumption in the fused region
        # is fused, we map it to the row or column if it uses at least one row
        # or column in the fusion region.
        #
        # FALSE: In particular, these lists can have size
        #           at most two, and one of the two variables
        #           is a subset of the other
        #
        # In particular, the lists can have size at most two (in which one of
        # the two variables is a subset of the other), unless, they are contained
        # entirely within the fused region, in which case it can have up
        # to 3: left, right and both.
        self.reversed_extra_parameters: Dict[str, List[str]] = defaultdict(list)
        # the child parameter that determine 'where the line is drawn'.
        self.fuse_parameter = fuse_parameter
        # sets to tell if parent assumption is one sided, or both
        self.left_sided_parameters = frozenset(left_sided_parameters)
        self.right_sided_parameters = frozenset(right_sided_parameters)
        self.both_sided_parameters = frozenset(both_sided_parameters)
        # The following assertions check that if two parent assumptions map to the
        # sameassumption, then one of them is one sided, and the other covers both
        # sides, OR that they are all contained fully in fuse region.
        assert all(
            len(val) <= 2
            or (
                len(val) == 3
                and all(
                    self.extra_parameters[parent_var] == self.fuse_parameter
                    for parent_var in val
                )
            )
            for val in self.reversed_extra_parameters.values()
        )
        for parent_var, child_var in self.extra_parameters.items():
            self.reversed_extra_parameters[child_var].append(parent_var)
        assert all(
            (
                any(
                    parent_var in self.left_sided_parameters
                    or parent_var in self.right_sided_parameters
                    for parent_var in parent_vars
                )
                and any(
                    parent_var in self.both_sided_parameters
                    for parent_var in parent_vars
                )
            )
            or all(
                self.extra_parameters[parent_var] == self.fuse_parameter
                for parent_var in parent_vars
            )
            for parent_vars in self.reversed_extra_parameters.values()
            if len(parent_vars) == 2
        )
        # if any two parents map to the same child, then these determine the
        # number of left and right points
        self.predeterminable_left_right_points = [
            parent_vars
            for parent_vars in self.reversed_extra_parameters.values()
            if len(parent_vars) == 2
        ]
        # we now determine which fusion recurrence we want to use
        if not self.left_sided_parameters and not self.right_sided_parameters:
            # no parent variable maps to the fusion region
            self.rec_function = self._new_fusion_no_interaction_get_recurrence
        elif self.fuse_parameter in extra_parameters.values():
            # some parent variable(s) map to the fusion region
            if self.predeterminable_left_right_points:
                self.rec_function = (
                    self._predetermined_fusing_parent_parameter_get_recurrence
                )
            else:
                self.rec_function = self._fusing_parent_parameter_get_recurrence
                self.parent_fusion_parameter = self.reversed_extra_parameters[
                    self.fuse_parameter
                ][0]
                self.fusion_type = (
                    "left"
                    if self.parent_fusion_parameter in self.left_sided_parameters
                    else "right"
                    if self.parent_fusion_parameter in self.right_sided_parameters
                    else "both"
                )
        else:
            # no parent variable maps to the fusion region, so need to add new
            # parameter to each call.
            if self.predeterminable_left_right_points:
                self.rec_function = (
                    self._predetermined_new_fusion_parameter_get_recurrence
                )
            else:
                self.rec_function = self._new_fusion_parameter_get_recurrence

    @staticmethod
    def is_equivalence() -> bool:
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
        return self.rec_function(subrec, n, **parameters)

    def _fusing_parent_parameter_get_recurrence(
        self, subrec: SubRec, n: int, **parameters: int
    ) -> int:
        """
        In this case, a region of the parent was mapped to the fused region, and
        there are no two regions mapped to the same region from parent to child.

        In this case, the fusion_type is set as follows:
            - left: the parent region was only the left of the unfused region
            - right: the parent region was only the right of the unfused region
            - both: the parent region was all of the unfused region.

        With this we need to consider the number of left points there can be,
        and update other parameters if they only use one half of the unfused region.
        """
        number_points_parent_fuse_parameter = parameters[self.parent_fusion_parameter]
        # TODO: compute number_of_left_points using reliance profile
        min_left_points = (
            number_points_parent_fuse_parameter
            if self.fusion_type in ("left", "both")
            else 0
        )
        # TODO: determine n using reliance profile
        max_left_points = (
            n - number_points_parent_fuse_parameter
            if self.fusion_type in ("right", "both")
            else n
        )
        res = 0
        for number_of_left_points in range(min_left_points, max_left_points + 1):
            new_params = self._update_subparams_unique_parent(
                number_of_left_points, number_points_parent_fuse_parameter, **parameters
            )
            res += subrec(n, **new_params)
        return res

    def _predetermined_fusing_parent_parameter_get_recurrence(
        self, subrec: SubRec, n: int, **parameters: int
    ) -> int:
        """
        Not implemented yet...
        """
        return 0

    def _new_fusion_parameter_get_recurrence(
        self, subrec: SubRec, n: int, **parameters: int
    ) -> int:
        """
        In this case, a new fusion parameter was added but at least one other parent
        regions was mapped to overlap the fusion region. However, there are no two
        regions mapped to the same region from parent to child.

        We therefore need to consider every possible value for the number of points
        in the fused region, and for each consider how many left and right points
        there are in order to update the regions which overlap the fused region.
        """
        # TODO: get k_val from the reliance profile
        res = 0
        for k_val in range(n + 1):
            for number_of_left_points in range(k_val + 1):
                # TODO: move this to a subfunction
                new_params = self._update_subparams_unique_parent(
                    number_of_left_points, k_val, **parameters
                )
                res += subrec(n, **new_params, **{self.fuse_parameter: k_val})
        return res

    def _update_subparams_unique_parent(
        self, number_of_left_points: int, total_points_in_region: int, **parameters: int
    ) -> Dict[str, int]:
        """
        Return the updates dictionary of parameters, such that each parameter points
        to the child parameter. This mapping should be unique.

        Also, number_of_left_points is added to the parameter if it is unnfused
        to include only the right side of the fused region, and number of right
        points is added to the region is it is unfused to include only the left
        side.
        """
        return {
            self.extra_parameters[parameter]: (
                value + number_of_left_points
                if parameter in self.right_sided_parameters
                else value
                # + number of right points
                + (total_points_in_region - number_of_left_points)
                if parameter in self.left_sided_parameters
                else value
            )
            for parameter, value in parameters.items()
        }

    def _update_subparams_non_unique_parent(
        self, number_of_left_points: int, number_of_right_points: int, **parameters: int
    ) -> Optional[Dict[str, int]]:
        """
        Return the updates dictionary of parameters, such that each parameter points
        to the child parameter.

        The extra parameters mapping may not be unique, so if
        two updated parameters have a different value, then the function returns None
        to tell the calling function that the value of the subrec call should be 0.

        Also, number_of_left_points is added to the parameter if it is unnfused
        to include only the right side of the fused region, and number of right
        points is added to the region is it is unfused to include only the left
        side.
        """
        res: Dict[str, int] = dict()
        for parameter, value in parameters.items():
            updated_value = (
                value + number_of_left_points
                if parameter in self.right_sided_parameters
                else value + number_of_right_points
                if parameter in self.left_sided_parameters
                else value
            )
            child_parameter = self.extra_parameters[parameter]
            if child_parameter in res:
                if updated_value != res[child_parameter]:
                    return None
            else:
                res[child_parameter] = updated_value
        return res

    def _predetermined_new_fusion_parameter_get_recurrence(
        self, subrec: SubRec, n: int, **parameters: int
    ) -> int:
        """
        In this case, a new fused region was added and no other parameter uses
        the fused region. However, there are two parent assumptions that map to
        the same assumption overlapping the fused region. These determine the
        unique value that can be assigned to the fusion region.
        """
        values = self._determine_number_of_points_in_fuse_region(**parameters)
        if any(k < 0 for k in values if k is not None):
            return 0

        # TODO: moven next 20 lines of logic to the
        # _determine_number_of_points_in_fuse_region function
        number_of_left_points, number_of_right_points = values
        # TODO: get the values from reliance profile function, e.g. n
        if number_of_left_points is None:
            assert number_of_right_points is not None
            number_of_left_points_range = range(n - number_of_right_points + 1)
        else:
            number_of_left_points_range = range(
                number_of_left_points, number_of_left_points + 1
            )

        if number_of_right_points is None:
            assert number_of_right_points is not None
            number_of_right_points_range = range(n - number_of_left_points + 1)
        else:
            number_of_right_points_range = range(
                number_of_right_points, number_of_right_points + 1
            )
        res = 0
        for number_of_left_points, number_of_right_points in product(
            number_of_left_points_range, number_of_right_points_range
        ):
            new_params = self._update_subparams_non_unique_parent(
                number_of_left_points, number_of_right_points, **parameters
            )
            if new_params is None:
                continue
            assert self.fuse_parameter not in new_params
            new_params[self.fuse_parameter] = (
                number_of_left_points + number_of_right_points
            )
            res += subrec(n, **new_params)
        return res

    def _determine_number_of_points_in_fuse_region(
        self, **parameters: int
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Return the number of points that are in the fused region as determined
        by the overlapping parameters.

        Precisely, it returns the number of points on the left, and the number
        of points on the right. If it can't determine one, then None is returned
        for that value.

        If there is a contradiction, (-1, -1) is returned.
        """
        assert self.predeterminable_left_right_points
        assert all(
            len(overlapping_parameters) >= 2
            for overlapping_parameters in self.predeterminable_left_right_points
        ), "not a valid amount of overlapping factors."

        def helper(
            overlapping_parameters: List[str],
        ) -> Tuple[Optional[int], Optional[int]]:
            """
            Any two overlappping parameters determine the number of points in the
            region. If there are three, then we can assess if it is a valid value.
            """
            p1 = overlapping_parameters[0]
            p2 = overlapping_parameters[1]
            p1_left = p1 in self.left_sided_parameters
            p1_right = p1 in self.right_sided_parameters
            p2_left = p2 in self.left_sided_parameters
            p2_right = p2 in self.right_sided_parameters
            if p1_left and p2_right:
                assert (
                    self.extra_parameters[p1] == self.fuse_parameter
                    and self.extra_parameters[p2] == self.fuse_parameter
                )
                return parameters[p1], parameters[p2]
            if p1_right and p2_left:
                assert (
                    self.extra_parameters[p1] == self.fuse_parameter
                    and self.extra_parameters[p2] == self.fuse_parameter
                )
                return parameters[p1], parameters[p2]
            if p1_left:
                assert p2 in self.both_sided_parameters
                return None, parameters[p2] - parameters[p1]
            if p1_right:
                assert p2 in self.both_sided_parameters
                return parameters[p2] - parameters[p1], None
            if p2_left:
                assert p1 in self.both_sided_parameters
                return None, parameters[p1] - parameters[p2]
            if p2_right:
                assert p1 in self.both_sided_parameters
                return parameters[p1] - parameters[p2], None
            raise ValueError("Overlapping parameters overlap same region")

        left: Optional[int] = None
        right: Optional[int] = None
        for overlapping_parameters in self.predeterminable_left_right_points:
            new_left, new_right = helper(overlapping_parameters)
            if left is None:
                left = new_left
            elif left != new_left:
                return -1, -1
            if right is None:
                right = new_right
            elif right != new_right:
                return -1, -1
        return left, right

    def _new_fusion_no_interaction_get_recurrence(
        self, subrec: SubRec, n: int, **parameters: int
    ) -> int:
        """
        In this case, a new fused region was added and no other parameter uses
        the fused region. Therefore, we just need to consider all of the possible
        values for the fused region, say k_val and multiply by k_val + 1. The
        other parameters are passed on directly.
        """
        # TODO: get k_val from reliance profile
        # TODO: get {self.fuse_parameter: k_val} from a parameters dictionary function
        new_params = {
            self.extra_parameters[parameter]: value
            for parameter, value in parameters.items()
        }
        return sum(
            (k_val + 1) * subrec(n, **new_params, **{self.fuse_parameter: k_val})
            for k_val in range(n + 1)
        )

        # subrec = subrecs[0]
        # new_params = {
        #     child_var: parameters[parent_var]
        #     for parent_var, child_var in self.extra_parameters.items()
        # }
        # fuse_parameter = self.fuse_parameter
        # if fuse_parameter in self.extra_parameters.values():
        #     # this is the number of points in the prefused region that is tracked
        #     # by  the fuse variable.
        #     parent_fuse_parameter: Optional[str] = None
        #     for parent_var, child_var in self.extra_parameters.items():
        #         if child_var == fuse_parameter:
        #             assert (
        #                 parent_fuse_parameter is None
        #             ), "multiple parent fuse parameters"
        #             parent_fuse_parameter = parent_var
        #     assert parent_fuse_parameter is not None
        #     number_points_in_fuse_region = new_params[parent_fuse_parameter]
        #     # pass on parameters and multiply by k + 1
        #     if not self.left_sided_parameters and not self.right_sided_parameters:
        #         return (number_points_in_fuse_region + 1) * subrec(n, **new_params)
        #     min_left_points = 0
        #     max_left_points = n
        #     if parent_fuse_parameter in self.left_sided_parameters:
        #         min_left_points += number_points_in_fuse_region
        #     if parent_fuse_parameter in self.right_sided_parameters:
        #         max_left_points -= number_points_in_fuse_region
        #     res = 0
        #     for number_of_left_points in range(min_left_points, max_left_points + 1):
        #         number_of_right_points = (
        #             number_of_left_points - number_points_in_fuse_region
        #         )
        #         res += subrec(
        #             n,
        #             **{
        #                 k: (
        #                     val + number_of_left_points
        #                     if k in self.right_sided_parameters
        #                     else val + number_of_right_points
        #                     if k in self.left_sided_parameters
        #                     else val
        #                 )
        #                 for k, val in new_params.items()
        #             },
        #         )
        #     return res
        # else:
        #     # sum over all possible k
        #     # TODO: valid k_val should be computed in reliance profile before
        #     # asking subrec
        #     res = 0
        #     for k_val in range(n + 1):
        #         # add the fuse parameter to the new paramaters
        #         new_params[fuse_parameter] = k_val
        #         if not self.left_sided_parameters and not self.right_sided_parameters:
        #             res += (k_val + 1) * subrec(n, **new_params)
        #         else:
        #             for number_of_left_points in range(0, k_val + 1):
        #                 number_of_right_points = k_val - number_of_left_points
        #                 res += subrec(
        #                     n,
        #                     **{
        #                         k: (
        #                             val + number_of_left_points
        #                             if k in self.right_sided_parameters
        #                             else val + number_of_right_points
        #                             if k in self.left_sided_parameters
        #                             else val
        #                         )
        #                         for k, val in new_params.items()
        #                     },
        #                 )
        #     return res

    def get_sub_objects(
        self, subgens: SubGens, n: int, **parameters: int
    ) -> Iterator[Tuple[GriddedPerm, ...]]:
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
        return FusionConstructor(
            self._fuse_parameter(comb_class),
            *self.extra_parameters(comb_class, children),
        )

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Dict[str, str], Set[str], Set[str], Set[str]]:
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
            k: child.get_parameter(ass)
            for k, ass in zip(comb_class.extra_parameters(), mapped_assumptions)
        }
        left_sided_params: Set[str] = set()
        right_sided_params: Set[str] = set()
        both_sided_params: Set[str] = set()
        for assumption in comb_class.assumptions:
            parent_var = comb_class.get_parameter(assumption)
            left_sided = algo.is_left_sided_assumption(assumption)
            right_sided = algo.is_right_sided_assumption(assumption)
            if left_sided and not right_sided:
                left_sided_params.add(parent_var)
            elif right_sided and not left_sided:
                right_sided_params.add(parent_var)
            else:
                both_sided_params.add(parent_var)
        return (
            extra_parameters,
            left_sided_params,
            right_sided_params,
            both_sided_params,
        )

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

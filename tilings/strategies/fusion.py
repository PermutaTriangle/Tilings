"""
The fusion strategy. The goal of the fusion strategy is to find a pair of
adjacent rows, or adjacent columns such that they can be viewed as a single
column, with a line drawn between them. When this fusion happens, an assumption
that we can count the number of points in the fused row or column is added.

When we map an assumption from the parent tiling to the fused tiling, if it
uses either of the rows or columns being fused, then it is mapped to cover the
entire fused region. With this in mind, we assume that a tiling cannot fuse if
it has an assumption that intersects only partially with one of the adjacent
rows or columns.

We will assume we are always fusing two adjacent columns, and discuss the left
and right hand sides accordingly.
"""
from collections import Counter, defaultdict
from functools import reduce
from operator import mul
from random import randint
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple, cast

from sympy import Eq, Expr, Function, Number, var

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
from tilings.algorithms import ComponentFusion, Fusion

__all__ = ["FusionStrategy", "ComponentFusionStrategy"]


class FusionConstructor(Constructor[Tiling, GriddedPerm]):
    """
    The fusion constructor. It will multiply by (fuse_paramater + 1), and
    otherwise pass on the variables.

    - fuse_parameter:           parameter corresponding to the region of the
                                tiling of the child where a line must be drawn.
    - extra_parameters:         a dictionary where the keys are each of the
                                parent parameters pointing to the child
                                parameter it was mapped to. Note, if [ A | A ]
                                fuses to [ A ] then we assume any one sided
                                variable maps to the [ A ] on the child.
    - left_sided_parameters:    all of the parent parameters which overlap
                                fully the left side of the region that is
                                being fused.
    - right_sided_parameters:   all of the parent parameters which overlap
                                fully the right side of the region that is
                                being fused.
    - both_sided_parameters:    all of the parent parameters which overlap
                                fully the entire region that is being fused
    """

    # pylint: disable=too-many-instance-attributes
    # This pylint warning is ignored due to adding in a new algorithm for
    # computing terms that does not apply to sampling. Therefore, this class
    # has two fundamentally different approaches to counting and we would
    # need to refactor the old one to pass this test.
    def __init__(
        self,
        parent: Tiling,
        child: Tiling,
        fuse_parameter: str,
        extra_parameters: Dict[str, str],
        left_sided_parameters: Iterable[str],
        right_sided_parameters: Iterable[str],
        both_sided_parameters: Iterable[str],
        min_left: int,
        min_right: int,
    ):
        # parent -> child parameters
        self.extra_parameters = extra_parameters
        # the reverse of the above list, although different parent parameters could
        # point to the same child parameter as when an assumption in the fused region
        # is fused, we map it to the row or column if it uses at least one row
        # or column in the fusion region.
        self.reversed_extra_parameters: Dict[str, List[str]] = defaultdict(list)
        for parent_var, child_var in self.extra_parameters.items():
            self.reversed_extra_parameters[child_var].append(parent_var)
        # the child parameter that determine 'where the line is drawn'.
        self.fuse_parameter = fuse_parameter
        # sets to tell if parent assumption is one sided, or both
        self.left_sided_parameters = frozenset(left_sided_parameters)
        self.right_sided_parameters = frozenset(right_sided_parameters)
        self.both_sided_parameters = frozenset(both_sided_parameters)

        self._init_checked()

        self.parent_fusion_parameters = self.reversed_extra_parameters[
            self.fuse_parameter
        ]
        self.fusion_types = [
            (
                "left"
                if parent_fusion_parameter in self.left_sided_parameters
                else "right"
                if parent_fusion_parameter in self.right_sided_parameters
                else "both"
            )
            for parent_fusion_parameter in self.parent_fusion_parameters
        ]
        self.predeterminable_left_right_points = [
            parent_vars
            for child_var, parent_vars in self.reversed_extra_parameters.items()
            if child_var != self.fuse_parameter and len(parent_vars) >= 2
        ]
        self.min_points = min_left, min_right

        index_mapping = {
            child.extra_parameters.index(child_param): tuple(
                map(parent.extra_parameters.index, parent_params)
            )
            for child_param, parent_params in self.reversed_extra_parameters.items()
        }
        self.left_parameter_indices = tuple(
            i
            for i, k in enumerate(parent.extra_parameters)
            if k in self.left_sided_parameters
        )
        self.right_parameter_indices = tuple(
            i
            for i, k in enumerate(parent.extra_parameters)
            if k in self.right_sided_parameters
        )
        self.fuse_parameter_index = child.extra_parameters.index(self.fuse_parameter)
        child_pos_to_parent_pos = tuple(
            index_mapping[idx] for idx in range(len(child.extra_parameters))
        )
        self.children_param_map = self._build_param_map(
            child_pos_to_parent_pos, len(parent.extra_parameters)
        )

    def _init_checked(self):
        """
        The lists in reversed_extra_parameters can have size at most two (in
        which case one of the two variables is a subset of the other), unless,
        they are contained entirely within the fused region, in which case it
        can have up to 3, namely left, right and both. This is checked in the
        first assertion.

        Moreover, if two parent assumptions map to the same assumption, then one
        of them is one sided, and the other covers both sides, OR they are all
        contained fully in fuse region. This is checked in the second assertion.
        """
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

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        if max(self.min_points) > 1:
            raise NotImplementedError(
                "not implemented equation in the case of "
                "left or right containing more than one point"
            )
        rhs_func = rhs_funcs[0]
        subs: Dict[str, Expr] = {
            child: reduce(mul, [var(k) for k in parent_vars], 1)
            for child, parent_vars in self.reversed_extra_parameters.items()
        }
        left_vars = reduce(
            mul,
            [
                var(k)
                for k in self.left_sided_parameters
                if k not in self.parent_fusion_parameters
            ],
            1,
        )
        right_vars = reduce(
            mul,
            [
                var(k)
                for k in self.right_sided_parameters
                if k not in self.parent_fusion_parameters
            ],
            1,
        )
        p, q = Number(1), Number(1)
        for parent_fuse_parameter, fuse_type in zip(
            self.parent_fusion_parameters, self.fusion_types
        ):
            if fuse_type in ("left", "both"):
                p *= var(parent_fuse_parameter)
            if fuse_type in ("right", "both"):
                q *= var(parent_fuse_parameter)
        if left_vars == 1 and right_vars == 1 and p == q:
            raise NotImplementedError(
                "Not handled case with no left and right vars, and new fuse "
                "parameter, or only parent fusion parameter covered entire region"
            )
        subs1 = {**subs}
        subs1[self.fuse_parameter] = q / left_vars
        subs2 = {**subs}
        subs2[self.fuse_parameter] = p / right_vars

        left_right_empty = (
            rhs_func.subs(subs2, simultaneous=True),
            rhs_func.subs(subs1, simultaneous=True),
        )
        to_subtract = 0
        if self.min_points[0] == 1:
            # left side is positive, so the right can't be empty
            to_subtract += left_right_empty[1]
        if self.min_points[1] == 1:
            # right side is positive, so thr left can't be empty
            to_subtract += left_right_empty[0]

        return Eq(
            lhs_func,
            (
                (q * right_vars * rhs_func.subs(subs1, simultaneous=True))
                - (p * left_vars * rhs_func.subs(subs2, simultaneous=True))
            )
            / (q * right_vars - p * left_vars)
            - to_subtract,
        )

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_terms(self, subterms: SubTerms, n: int) -> Terms:
        """
        Uses the `subterms` functions to and the `children_param_maps` to compute
        the terms of size `n`.
        """
        new_terms: Terms = Counter()

        min_left, min_right = self.min_points

        def add_new_term(
            params: List[int], value: int, left_points: int, fuse_region_points: int
        ) -> None:
            """Update new terms if there is enough points on the left and right."""
            if (
                min_left <= left_points
                and min_right <= fuse_region_points - left_points
            ):
                new_terms[tuple(params)] += value

        for param, value in subterms[0](n).items():
            fuse_region_points = param[self.fuse_parameter_index]
            new_params = list(self.children_param_map(param))
            for idx in self.left_parameter_indices:
                new_params[idx] -= fuse_region_points
            add_new_term(new_params, value, 0, fuse_region_points)
            for left_points in range(1, fuse_region_points + 1):
                for idx in self.left_parameter_indices:
                    new_params[idx] += 1
                for idx in self.right_parameter_indices:
                    new_params[idx] -= 1

                add_new_term(new_params, value, left_points, fuse_region_points)
        return new_terms

    @staticmethod
    def _build_param_map(
        child_pos_to_parent_pos: Tuple[Tuple[int, ...], ...], num_parent_params: int
    ) -> ParametersMap:
        """
        Build the ParametersMap that will map according to the given child pos to parent
        pos map given.
        """

        def param_map(param: Parameters) -> Parameters:
            new_params: List[Optional[int]] = [None for _ in range(num_parent_params)]
            for pos, value in enumerate(param):
                for parent_pos in child_pos_to_parent_pos[pos]:
                    assert new_params[parent_pos] is None
                    new_params[parent_pos] = value
            assert all(x is not None for x in new_params)
            return tuple(cast(List[int], new_params))

        return param_map

    def determine_number_of_points_in_fuse_region(
        self, n: int, **parameters: int
    ) -> Iterator[Tuple[int, int]]:
        """
        There are two cases we use to determine the number of left and right points.

        # Case 1:
        There was an assumption A on the parent which maps precisely to the fused
        region. It must be either on the left, right, or covering both columns,
        crucially fully contained within the region to be fused.

        In this case we can determine:
        - if A is left sided, then we know the number of points on the left must be the
        number of points in A
        - if A is right sided, then we know the number of points on the right must be
        be the number of points in A.
        - if A is both sided, then this tells as the sum of the number of left points
        and right points must be equal to the number of points in A. In particular,
        the number of points in A gives us an upper bound for the number of points
        on the left or the right.

        # Case 2:
        We're not in case 1, however there are two assumptions A and B which are mapped
        to the same region on the fused tiling. This means that one of A or B must use
        just the left or right column. Due to the nature of these regions always
        remaining rectangles, this tells us that the other must use both columns.
        W.l.o.g, we will assume the B is the assumption covering both columns

        In this case we can determine:
        - if A uses the left column, then number of points on the right is the number
        of points in B substract the number of points in A
        - if A uses the right column, then the number of points on the left is the
        number of points in B substract the number of points in A
        - the number of points in the entire region is upper bounded by the number of
        points in B.


        In this case, the fusion_type for each fusion parameter is set as follows:
            - left: the parent region was only the left of the unfused region
            - right: the parent region was only the right of the unfused region
            - both: the parent region was all of the unfused region.
        """
        (
            min_left_points,
            max_left_points,
            min_right_points,
            max_right_points,
            min_both_points,
            max_both_points,
        ) = self._min_max_points_by_fuse_parameters(n, **parameters)

        if (
            min_left_points > max_left_points
            or min_right_points > max_right_points
            or min_both_points > max_both_points
        ):
            return

        for overlapping_parameters in self.predeterminable_left_right_points:
            (
                new_left,
                new_right,
            ) = self._determine_number_of_points_by_overlapping_parameter(
                overlapping_parameters, **parameters
            )
            if new_left is not None:
                min_left_points = max(min_left_points, new_left)
                max_left_points = min(min_left_points, new_left)
            if new_right is not None:
                min_right_points = max(min_right_points, new_right)
                max_right_points = min(max_right_points, new_right)
            if min_left_points > max_left_points or min_right_points > max_right_points:
                return

        min_both_points = max(min_both_points, min_left_points + min_right_points)
        max_both_points = min(max_both_points, max_right_points + max_left_points)
        for number_left_points in range(min_left_points, max_left_points + 1):
            for number_right_points in range(min_right_points, max_right_points + 1):
                both = number_left_points + number_right_points
                if both < min_both_points:
                    continue
                if both > max_both_points:
                    break
                yield number_left_points, number_right_points

    def _min_max_points_by_fuse_parameters(
        self, n: int, **parameters: int
    ) -> Tuple[int, int, int, int, int, int]:
        """
        # Case 1:
        There was an assumption A on the parent which maps precisely to the fused
        region. It must be either on the left, right, or covering both columns,
        crucially fully contained within the region to be fused.

        In this case we can determine:
        - if A is left sided, then we know the number of points on the left must be the
        number of points in A
        - if A is right sided, then we know the number of points on the right must be
        be the number of points in A.
        - if A is both sided, then this tells as the sum of the number of left points
        and right points must be equal to the number of points in A. In particular,
        the number of points in A gives us an upper bound for the number of points
        on the left or the right.
        """
        min_left_points, max_left_points = self.min_points[0], n - self.min_points[1]
        min_right_points, max_right_points = self.min_points[1], n - self.min_points[0]
        min_both_points, max_both_points = sum(self.min_points), n
        for parent_fusion_parameter, fusion_type in zip(
            self.parent_fusion_parameters, self.fusion_types
        ):
            number_points_parent_fuse_parameter = parameters[parent_fusion_parameter]
            if fusion_type == "left":
                min_left_points = max(
                    min_left_points, number_points_parent_fuse_parameter
                )
                max_left_points = min(
                    max_left_points, number_points_parent_fuse_parameter
                )
            elif fusion_type == "right":
                min_right_points = max(
                    min_right_points, number_points_parent_fuse_parameter
                )
                max_right_points = min(
                    max_right_points, number_points_parent_fuse_parameter
                )
            else:
                assert fusion_type == "both"
                # TODO: is this the right way?
                max_left_points = min(
                    max_left_points, number_points_parent_fuse_parameter
                )
                max_right_points = min(
                    max_right_points, number_points_parent_fuse_parameter
                )
                min_both_points = max(
                    min_both_points, number_points_parent_fuse_parameter
                )
                max_both_points = min(
                    max_both_points, number_points_parent_fuse_parameter
                )
            if (
                min_left_points > max_left_points
                or min_right_points > max_right_points
                or min_both_points > max_both_points
            ):
                break

        return (
            min_left_points,
            max_left_points,
            min_right_points,
            max_right_points,
            min_both_points,
            max_both_points,
        )

    def _determine_number_of_points_by_overlapping_parameter(
        self, overlapping_parameters: List[str], **parameters: int
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        # Case 2:
        There are two assumptions A and B which are mapped to the same region
        on the fused tiling (which is not the fused region, else we'd be in case
        1). This means that one of A or B must use just the left or right column.
        Due to the nature of these regions always remaining rectangles, this tells
        us that the other must use both columns.
        W.l.o.g, we will assume the B is the assumption covering both columns

        In this case we can determine:
        - if A uses the left column, then number of points on the right is the number
        of points in B substract the number of points in A
        - if A uses the right column, then the number of points on the left is the
        number of points in B substract the number of points in A
        - the number of points in the entire region is upper bounded by the number of
        points in B.
        """
        p1 = overlapping_parameters[0]
        p2 = overlapping_parameters[1]
        p1_left = p1 in self.left_sided_parameters
        p1_right = p1 in self.right_sided_parameters
        p2_left = p2 in self.left_sided_parameters
        p2_right = p2 in self.right_sided_parameters
        # TODO: tidy up this function, and update doc string
        assert not (p1_left and p2_right) and not (p1_right and p2_left)
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

    def update_subparams(
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
        res = {self.fuse_parameter: number_of_left_points + number_of_right_points}
        for parameter, value in parameters.items():
            if parameter not in self.extra_parameters and value != 0:
                return None
            if (
                parameter in self.left_sided_parameters
                and number_of_left_points > value
            ) or (
                parameter in self.right_sided_parameters
                and number_of_right_points > value
            ):
                return None
            updated_value = (
                value + number_of_left_points
                if parameter in self.right_sided_parameters
                else value + number_of_right_points
                if parameter in self.left_sided_parameters
                else value
            )
            child_parameter = self.extra_parameters[parameter]
            if child_parameter not in res:
                res[child_parameter] = updated_value
            elif updated_value != res[child_parameter]:
                return None
        return res

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[Tuple[Parameters, Tuple[List[Optional[GriddedPerm]], ...]]]:
        raise NotImplementedError(
            "This is implemented on the FusionRule class directly"
        )

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ):
        raise NotImplementedError(
            "This is implemented on the FusionRule class directly"
        )


class FusionRule(Rule[Tiling, GriddedPerm]):
    """Overwritten the generate objects of size method, as this relies on
    knowing the number of left and right points of the parent tiling."""

    @property
    def strategy(self) -> "FusionStrategy":
        return cast(
            FusionStrategy,
            super().strategy,
        )

    @property
    def constructor(self) -> FusionConstructor:
        return cast(FusionConstructor, super().constructor)

    def _ensure_level_objects(self, n: int) -> None:

        if self.subobjects is None:
            raise RuntimeError("set_subrecs must be set first")
        while n >= len(self.objects_cache):
            res: Objects = defaultdict(list)
            min_left, min_right = self.constructor.min_points

            def add_new_gp(
                params: List[int],
                left_points: int,
                fuse_region_points: int,
                unfused_gps: Iterator[GriddedPerm],
            ) -> None:
                """Update new terms if there is enough points on the left and right."""
                gp = next(unfused_gps)
                if (
                    min_left <= left_points
                    and min_right <= fuse_region_points - left_points
                ):
                    res[tuple(params)].append(gp)

            for param, objects in self.subobjects[0](len(self.objects_cache)).items():
                fuse_region_points = param[self.constructor.fuse_parameter_index]
                for gp in objects:
                    new_params = list(self.constructor.children_param_map(param))
                    unfused_gps = self.strategy.backward_map(
                        self.comb_class, (gp,), self.children
                    )  # iterates over unfused gridded perms in order
                    # with 0, 1, .., and finally fuse_region_points on the left
                    for idx in self.constructor.left_parameter_indices:
                        new_params[idx] -= fuse_region_points
                    add_new_gp(new_params, 0, fuse_region_points, unfused_gps)
                    for left_points in range(1, fuse_region_points + 1):
                        for idx in self.constructor.left_parameter_indices:
                            new_params[idx] += 1
                        for idx in self.constructor.right_parameter_indices:
                            new_params[idx] -= 1
                        add_new_gp(
                            new_params, left_points, fuse_region_points, unfused_gps
                        )

            self.objects_cache.append(res)

    def random_sample_object_of_size(self, n: int, **parameters: int) -> GriddedPerm:
        """Return a random objects of the give size."""
        assert (
            self.subrecs is not None and self.subsamplers is not None
        ), "you must call the set_subrecs function first"
        subrec = self.subrecs[0]
        subsampler = self.subsamplers[0]
        parent_count = self.count_objects_of_size(n, **parameters)
        random_choice = randint(1, parent_count)
        total = 0
        left_right_points = self.constructor.determine_number_of_points_in_fuse_region(
            n, **parameters
        )
        for left_points, right_points in left_right_points:
            new_params = self.constructor.update_subparams(
                left_points, right_points, **parameters
            )
            if new_params is not None:
                assert (
                    new_params[self.constructor.fuse_parameter]
                    == left_points + right_points
                )
                total += subrec(n, **new_params)
                if random_choice <= total:
                    gp = subsampler(n, **new_params)
                    try:
                        return next(
                            self.strategy.backward_map(
                                self.comb_class, (gp,), self.children, left_points
                            )
                        )
                    except StopIteration:
                        assert 0, "something went wrong"


class FusionStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(self, row_idx=None, col_idx=None, tracked: bool = False):
        self.col_idx = col_idx
        self.row_idx = row_idx
        self.tracked = tracked
        if not sum(1 for x in (self.col_idx, self.row_idx) if x is not None) == 1:
            raise RuntimeError("Cannot specify a row and a column")
        super().__init__(
            ignore_parent=False, inferrable=True, possibly_empty=False, workable=True
        )

    def __call__(
        self,
        comb_class: Tiling,
        children: Tuple[Tiling, ...] = None,
        **kwargs,
    ) -> FusionRule:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        return FusionRule(self, comb_class, children=children)

    def fusion_algorithm(self, tiling: Tiling) -> Fusion:
        return Fusion(
            tiling, row_idx=self.row_idx, col_idx=self.col_idx, tracked=self.tracked
        )

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        algo = self.fusion_algorithm(comb_class)
        if algo.fusable():
            return (algo.fused_tiling(),)

    @staticmethod
    def can_be_equivalent() -> bool:
        return False

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> FusionConstructor:
        if not self.tracked:
            # constructor only enumerates when tracked.
            raise NotImplementedError("The fusion strategy was not tracked.")
        # Need to recompute some info to count, so ignoring passed in children
        algo = self.fusion_algorithm(comb_class)
        if not algo.fusable():
            raise StrategyDoesNotApply("Strategy does not apply")
        child = algo.fused_tiling()
        assert children is None or children == (child,)
        min_left, min_right = algo.min_left_right_points()
        return FusionConstructor(
            comb_class,
            child,
            self._fuse_parameter(comb_class),
            self.extra_parameters(comb_class, children)[0],
            *self.left_right_both_sided_parameters(comb_class),
            min_left,
            min_right,
        )

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str]]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        algo = self.fusion_algorithm(comb_class)
        child = children[0]
        mapped_assumptions = [
            child.forward_map_assumption(ass.__class__(gps))
            for ass, gps in zip(comb_class.assumptions, algo.assumptions_fuse_counters)
        ]
        return (
            {
                k: child.get_assumption_parameter(ass)
                for k, ass in zip(comb_class.extra_parameters, mapped_assumptions)
                if ass.gps
            },
        )

    def left_right_both_sided_parameters(
        self, comb_class: Tiling
    ) -> Tuple[Set[str], Set[str], Set[str]]:
        left_sided_params: Set[str] = set()
        right_sided_params: Set[str] = set()
        both_sided_params: Set[str] = set()
        algo = self.fusion_algorithm(comb_class)
        for assumption in comb_class.assumptions:
            parent_var = comb_class.get_assumption_parameter(assumption)
            left_sided = algo.is_left_sided_assumption(assumption)
            right_sided = algo.is_right_sided_assumption(assumption)
            if left_sided and not right_sided:
                left_sided_params.add(parent_var)
            elif right_sided and not left_sided:
                right_sided_params.add(parent_var)
            elif not left_sided and not right_sided:
                both_sided_params.add(parent_var)
        return (
            left_sided_params,
            right_sided_params,
            both_sided_params,
        )

    def _fuse_parameter(self, comb_class: Tiling) -> str:
        algo = self.fusion_algorithm(comb_class)
        child = algo.fused_tiling()
        ass = algo.new_assumption()
        fuse_assumption = ass.__class__(child.forward_map(gp) for gp in ass.gps)
        return child.get_assumption_parameter(fuse_assumption)

    def formal_step(self) -> str:
        fusing = "rows" if self.row_idx is not None else "columns"
        idx = self.row_idx if self.row_idx is not None else self.col_idx
        return "fuse {} {} and {}".format(fusing, idx, idx + 1)

    def backward_map(
        self,
        comb_class: Tiling,
        gps: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
        left_points: int = None,
    ) -> Iterator[GriddedPerm]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)
        gp = gps[0]
        assert gp is not None
        gp = children[0].backward_map(gp)
        yield from self.fusion_algorithm(comb_class).unfuse_gridded_perm(
            gp, left_points
        )

    def forward_map(
        self,
        comb_class: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        """
        The forward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)
        fused_gp = self.fusion_algorithm(comb_class).fuse_gridded_perm(gp)
        return (children[0].forward_map(fused_gp),)

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

    @staticmethod
    def get_op_symbol() -> str:
        return "⚮"

    @staticmethod
    def get_eq_symbol() -> str:
        return "↣"

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + f"(row_idx={self.row_idx}, col_idx={self.col_idx}, "
            f"tracked={self.tracked})"
        )


class ComponentFusionStrategy(FusionStrategy):
    def fusion_algorithm(self, tiling: Tiling) -> Fusion:
        return ComponentFusion(
            tiling, row_idx=self.row_idx, col_idx=self.col_idx, tracked=self.tracked
        )

    def formal_step(self) -> str:
        fusing = "rows" if self.row_idx is not None else "columns"
        idx = self.row_idx if self.row_idx is not None else self.col_idx
        return "component fuse {} {} and {}".format(fusing, idx, idx + 1)

    def backward_map(
        self,
        comb_class: Tiling,
        gps: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
        left_points: Optional[int] = None,
    ) -> Iterator[GriddedPerm]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        raise NotImplementedError


class FusionFactory(StrategyFactory[Tiling]):
    def __init__(self, tracked: bool = True, isolation_level: Optional[str] = None):
        self.tracked = tracked
        self.isolation_level = isolation_level

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[Rule]:
        cols, rows = comb_class.dimensions
        for row_idx in range(rows - 1):
            algo = Fusion(
                comb_class,
                row_idx=row_idx,
                tracked=self.tracked,
                isolation_level=self.isolation_level,
            )
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield FusionStrategy(row_idx=row_idx, tracked=self.tracked)(
                    comb_class, (fused_tiling,)
                )
        for col_idx in range(cols - 1):
            algo = Fusion(
                comb_class,
                col_idx=col_idx,
                tracked=self.tracked,
                isolation_level=self.isolation_level,
            )
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
        return cls(**d)


class ComponentFusionFactory(StrategyFactory[Tiling]):
    def __init__(self, tracked: bool = False, isolation_level: Optional[str] = None):
        self.tracked = tracked
        self.isolation_level = isolation_level

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[Rule]:
        if comb_class.requirements:
            return
        cols, rows = comb_class.dimensions
        for row_idx in range(rows - 1):
            algo = ComponentFusion(
                comb_class,
                row_idx=row_idx,
                tracked=self.tracked,
                isolation_level=self.isolation_level,
            )
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield ComponentFusionStrategy(row_idx=row_idx, tracked=self.tracked)(
                    comb_class, (fused_tiling,)
                )
        for col_idx in range(cols - 1):
            algo = ComponentFusion(
                comb_class,
                col_idx=col_idx,
                tracked=self.tracked,
                isolation_level=self.isolation_level,
            )
            if algo.fusable():
                fused_tiling = algo.fused_tiling()
                yield ComponentFusionStrategy(col_idx=col_idx, tracked=self.tracked)(
                    comb_class, (fused_tiling,)
                )

    def __str__(self) -> str:
        return f"{'tracked ' if self.tracked else ''}component fusion"

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + f"(tracked={self.tracked}, isolation_level={self.isolation_level})"
        )

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["tracked"] = self.tracked
        d["isolation_level"] = self.isolation_level
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ComponentFusionFactory":
        return cls(**d)

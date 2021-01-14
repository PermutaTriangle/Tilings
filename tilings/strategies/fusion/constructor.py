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
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Tuple

import sympy

from comb_spec_searcher import Constructor
from comb_spec_searcher.typing import (
    Parameters,
    RelianceProfile,
    SubObjects,
    SubRecs,
    SubSamplers,
    SubTerms,
    Terms,
)
from tilings import GriddedPerm, Tiling

__all__ = ["FusionConstructor"]


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
        self.children_param_map = self.build_param_map(
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

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        if max(self.min_points) > 1:
            raise NotImplementedError(
                "not implemented equation in the case of "
                "left or right containing more than one point"
            )
        rhs_func = rhs_funcs[0]
        subs: Dict[str, sympy.Expr] = {
            child: reduce(mul, [sympy.var(k) for k in parent_vars], 1)
            for child, parent_vars in self.reversed_extra_parameters.items()
        }
        left_vars = reduce(
            mul,
            [
                sympy.var(k)
                for k in self.left_sided_parameters
                if k not in self.parent_fusion_parameters
            ],
            1,
        )
        right_vars = reduce(
            mul,
            [
                sympy.var(k)
                for k in self.right_sided_parameters
                if k not in self.parent_fusion_parameters
            ],
            1,
        )
        p, q = sympy.Number(1), sympy.Number(1)
        for parent_fuse_parameter, fuse_type in zip(
            self.parent_fusion_parameters, self.fusion_types
        ):
            if fuse_type in ("left", "both"):
                p *= sympy.var(parent_fuse_parameter)
            if fuse_type in ("right", "both"):
                q *= sympy.var(parent_fuse_parameter)
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

        return sympy.Eq(
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

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
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


class ReverseFusionConstructor(Constructor[Tiling, GriddedPerm]):
    def __init__(
        self,
        parent: Tiling,
        child: Tiling,
        fuse_parameter: str,
        extra_parameters: Dict[str, str],
        left_sided_parameters: Tuple[str],
        right_sided_parameters: Tuple[str],
    ):
        self.left_idx = tuple(map(parent.extra_parameters.index, left_sided_parameters))
        self.right_idx = tuple(
            map(parent.extra_parameters.index, right_sided_parameters)
        )
        try:
            self.left_fuse_index = self.get_left_fuse_index(
                left_sided_parameters, fuse_parameter, extra_parameters, parent
            )
        except RuntimeError:
            self.left_idx, self.right_idx = self.right_idx, self.left_idx
            self.left_fuse_index = self.get_left_fuse_index(
                right_sided_parameters, fuse_parameter, extra_parameters, parent
            )
        self.child_pos_to_parent_pos: Tuple[int, ...] = tuple(
            y
            for _, y in sorted(
                (
                    parent.extra_parameters.index(parent_param),
                    child.extra_parameters.index(child_param),
                )
                for parent_param, child_param in extra_parameters.items()
            )
        )
        self.right_mapped_idx = tuple(
            self.child_pos_to_parent_pos[idx] for idx in self.right_idx
        )

    def get_left_fuse_index(
        self,
        left_sided_parameters: Tuple[str],
        fuse_parameter: str,
        extra_parameters: Dict[str, str],
        parent: Tiling,
    ) -> int:
        for parent_param, child_param in extra_parameters.items():
            if child_param == fuse_parameter and parent_param in left_sided_parameters:
                return parent.extra_parameters.index(parent_param)
        raise RuntimeError("FAIL")

    def forward_map(self, param: Parameters) -> Parameters:
        """
        Maps a set of parameters on the fuse tiling to a set of parameters on
        the unfused tiling.
        """
        new_param = [0 for _ in range(max(self.child_pos_to_parent_pos) + 1)]
        for parent_idx, child_idx in enumerate(self.child_pos_to_parent_pos):
            new_param[child_idx] += param[parent_idx]
        return tuple(new_param)

    def a_map(self, param: Parameters) -> Parameters:
        new_param = list(param)
        for idx in self.left_idx:
            new_param[idx] += 1
        for idx in self.right_idx:
            new_param[idx] -= 1
        return tuple(new_param)

    def b_map(self, param: Parameters) -> Parameters:
        new_param = list(self.forward_map(param))
        for idx in self.right_mapped_idx:
            new_param[idx] += param[self.left_fuse_index]
        return tuple(new_param)

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        terms: Terms = Counter()
        child_terms = subterms[0](n)
        for param, value in child_terms.items():
            new_param = self.b_map(param)
            new_value = value - child_terms[self.a_map(param)]
            assert new_param not in terms
            terms[new_param] = new_value
        return terms

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        raise NotImplementedError

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
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

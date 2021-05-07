from collections import defaultdict
from itertools import islice
from random import randint
from typing import Dict, Iterator, List, Optional, Set, Tuple, cast

from comb_spec_searcher import Constructor, Strategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
from comb_spec_searcher.typing import Objects
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Fusion

from .constructor import FusionConstructor, ReverseFusionConstructor


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

    @staticmethod
    def is_equivalence() -> bool:
        return False

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

    def _forward_order(
        self,
        obj: GriddedPerm,
        image: Tuple[Optional[GriddedPerm], ...],
        data: Optional[object] = None,
    ) -> int:
        return next(i for i, gp in enumerate(self.backward_map(image)) if gp == obj)

    def _backward_order_item(
        self,
        idx: int,
        objs: Tuple[Optional[GriddedPerm], ...],
        data: Optional[object] = None,
    ) -> GriddedPerm:
        if data:
            return tuple(self.backward_map(objs))[-idx - 1]
        return next(islice(self.backward_map(objs), idx))


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

    @staticmethod
    def is_two_way(comb_class: Tiling):
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

    def reverse_constructor(  # pylint: disable=no-self-use
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        if not self.tracked:
            # constructor only enumerates when tracked.
            raise NotImplementedError("The fusion strategy was not tracked.")
        # Need to recompute some info to count, so ignoring passed in children
        algo = self.fusion_algorithm(comb_class)
        if not algo.fusable():
            raise StrategyDoesNotApply("Strategy does not apply")
        if algo.min_left_right_points() != (0, 0):
            raise NotImplementedError(
                "Reverse positive fusion counting not implemented"
            )
        child = algo.fused_tiling()
        assert children is None or children == (child,)
        (
            left_sided_params,
            right_sided_params,
            _,
        ) = self.left_right_both_sided_parameters(comb_class)
        return ReverseFusionConstructor(
            comb_class,
            child,
            self._fuse_parameter(comb_class),
            self.extra_parameters(comb_class, children)[0],
            tuple(left_sided_params),
            tuple(right_sided_params),
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

    # pylint: disable=arguments-differ
    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
        left_points: int = None,
    ) -> Iterator[GriddedPerm]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)
        gp = objs[0]
        assert gp is not None
        gp = children[0].backward_map(gp)
        yield from self.fusion_algorithm(comb_class).unfuse_gridded_perm(
            gp, left_points
        )

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
        fused_gp = self.fusion_algorithm(comb_class).fuse_gridded_perm(obj)
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


class FusionFactory(StrategyFactory[Tiling]):
    def __init__(self, tracked: bool = True, isolation_level: Optional[str] = None):
        self.tracked = tracked
        self.isolation_level = isolation_level

    def make_tracked(self) -> "FusionFactory":
        """Return a new version of the strategy that is tracked."""
        if self.tracked:
            raise ValueError("FusionFactory already tracked")
        return self.__class__(tracked=True, isolation_level=self.isolation_level)

    def __call__(self, comb_class: Tiling) -> Iterator[Rule]:
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

from itertools import chain
from typing import FrozenSet, Iterator, Optional, Set, Tuple, Union

from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies.constructor.base import Constructor
from tilings import GriddedPerm, Tiling
from tilings.assumptions import Assumption, Cell, TrackingAssumption
from tilings.strategies.fusion.constructor import ReverseFusionConstructor
from tilings.strategies.fusion.fusion import FusionRule, FusionStrategy
from tilings.strategies.pointing import DivideByK


class UnfusionRule(FusionRule):
    def _ensure_level_objects(self, n: int) -> None:
        raise NotImplementedError

    def random_sample_object_of_size(self, n: int, **parameters: int) -> GriddedPerm:
        raise NotImplementedError

    def _forward_order(
        self,
        obj: GriddedPerm,
        image: Tuple[Optional[GriddedPerm], ...],
        data: Optional[object] = None,
    ) -> int:
        raise NotImplementedError

    def _backward_order_item(
        self,
        idx: int,
        objs: Tuple[Optional[GriddedPerm], ...],
        data: Optional[object] = None,
    ) -> GriddedPerm:
        raise NotImplementedError


class UnfusionStrategy(FusionStrategy):
    def __init__(
        self,
        row_idx=None,
        col_idx=None,
        tracked: bool = False,
        left: bool = False,
        right: bool = False,
        both: bool = False,
    ):
        super().__init__(row_idx, col_idx, tracked)
        self.left = left
        self.right = right
        self.both = both
        assert left or right or both or not self.tracked

    def __call__(
        self,
        comb_class: Tiling,
        children: Tuple[Tiling, ...] = None,
    ) -> UnfusionRule:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        return UnfusionRule(self, comb_class, children=children)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        fused_region = self.fused_region(comb_class)

        def valid_fusion_assumptions():

            if (
                TrackingAssumption.from_cells(fused_region)
                not in comb_class.assumptions
            ):
                return False
            for assumption in comb_class.tracking_assumptions:
                intersected = fused_region.intersection(assumption.cells)
                if intersected and intersected != fused_region:
                    # strategy does not apply
                    return False
            return True

        if valid_fusion_assumptions():
            return (self.unfused_tiling(comb_class),)

    def unfused_tiling(self, tiling: Tiling) -> Tiling:
        algo = self.fusion_algorithm(tiling)
        obs = chain(*[algo.unfuse_gridded_perm(ob) for ob in tiling.obstructions])
        reqs = [
            [gp for req_gp in req_list for gp in algo.unfuse_gridded_perm(req_gp)]
            for req_list in tiling.requirements
        ]
        ass = set(
            ass.__class__(
                [gp for ass_gp in ass.gps for gp in algo.unfuse_gridded_perm(ass_gp)]
            )
            for ass in tiling.assumptions
        )
        if self.tracked:

            def add_or_remove(
                assumptions: Set[Assumption], assumption: TrackingAssumption, add: bool
            ) -> Set[Assumption]:
                if add:
                    assumptions.add(assumption)
                else:
                    assumptions.discard(assumption)

            add_or_remove(ass, self.left_tracking_assumption(tiling), self.left)
            add_or_remove(ass, self.right_tracking_assumption(tiling), self.right)
            add_or_remove(ass, self.both_tracking_assumption(tiling), self.both)
        return Tiling(obs, reqs, ass)

    def fused_region(self, tiling: Tiling) -> FrozenSet[Cell]:
        if self.row_idx is not None:
            return tiling.cells_in_row(self.row_idx)
        return tiling.cells_in_col(self.col_idx)

    def left_unfused_region(self, tiling: Tiling) -> FrozenSet[Cell]:
        return self.fused_region(tiling)

    def right_unfused_region(self, tiling: Tiling) -> FrozenSet[Cell]:
        if self.row_idx is not None:
            return frozenset((x, y + 1) for (x, y) in self.fused_region(tiling))
        return frozenset((x + 1, y) for (x, y) in self.fused_region(tiling))

    def unfused_region(self, tiling: Tiling) -> FrozenSet[Cell]:
        return self.left_unfused_region(tiling).union(self.right_unfused_region(tiling))

    def left_tracking_assumption(self, tiling: Tiling) -> TrackingAssumption:
        return TrackingAssumption.from_cells(self.left_unfused_region(tiling))

    def right_tracking_assumption(self, tiling: Tiling) -> TrackingAssumption:
        return TrackingAssumption.from_cells(self.right_unfused_region(tiling))

    def both_tracking_assumption(self, tiling: Tiling) -> TrackingAssumption:
        return TrackingAssumption.from_cells(self.unfused_region(tiling))

    def is_reversible(self, comb_class: Tiling) -> bool:
        return False

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Union[DivideByK, ReverseFusionConstructor]:
        if not self.tracked:
            # constructor only enumerates when tracked.
            raise NotImplementedError("The fusion strategy was not tracked.")
        if children is None:
            children = self.decomposition_function(comb_class)
        assert children is not None
        fused_tiling, unfused_tiling = comb_class, children[0]
        # Need to recompute some info to count, so ignoring passed in children
        algo = self.fusion_algorithm(unfused_tiling)
        # if not algo.fusable():
        #     raise StrategyDoesNotApply("Strategy does not apply")
        if algo.min_left_right_points() != (0, 0):
            raise NotImplementedError(
                "Reverse positive fusion counting not implemented"
            )
        (
            left_sided_params,
            right_sided_params,
            _,
        ) = self.left_right_both_sided_parameters(unfused_tiling)
        if not self.left and not self.right:
            assert self.both
            unfused_assumption = self.both_tracking_assumption(comb_class)
            assert unfused_assumption in unfused_tiling.assumptions
            return DivideByK(
                fused_tiling,
                (unfused_tiling,),
                1,
                unfused_tiling.get_assumption_parameter(unfused_assumption),
                self.extra_parameters(unfused_tiling, (fused_tiling,)),
            )
        return ReverseFusionConstructor(
            unfused_tiling,
            comb_class,
            self._fuse_parameter(fused_tiling),
            self.extra_parameters(unfused_tiling, (fused_tiling,))[0],
            tuple(left_sided_params),
            tuple(right_sided_params),
        )

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        raise NotImplementedError

    def _fuse_parameter(self, comb_class: Tiling) -> str:
        return comb_class.get_assumption_parameter(
            TrackingAssumption.from_cells(self.fused_region(comb_class))
        )

    def formal_step(self) -> str:
        fusing = "rows" if self.row_idx is not None else "columns"
        idx = self.row_idx if self.row_idx is not None else self.col_idx
        return f"unfuse {fusing} {idx}"

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
        left_points: int = None,
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        raise NotImplementedError


# if __name__ == "__main__":
#     from tilings.assumptions import OddCountAssumption, OppositeParityAssumption
#     from tilings.strategies import FusionFactory

#     t = Tiling(
#         obstructions=[
#             GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
#             GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
#             GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
#             GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
#         ],
#         assumptions=[
#             TrackingAssumption.from_cells([(0, 0)]),
#             OddCountAssumption.from_cells([(0, 0)]),
#             OddCountAssumption.from_cells([(1, 0)]),
#             OppositeParityAssumption.from_cells([(0, 0)]),
#             OppositeParityAssumption.from_cells([(1, 0)]),
#         ],
#     )

#     for rule in FusionFactory()(t):
#         print(rule)
#     print(t)
#     for left in (True, False):
#         for right in (True, False):
#             for both in (True, False):
#                 if left or right or both:
#                     strat = UnfusionStrategy(
#                         0, None, True, left=left, right=right, both=both
#                     )
#                     rule = strat(t)
#                     for i in range(6):
#                         print(i, rule.sanity_check(i))
#                         # rule.sanity_check(i)

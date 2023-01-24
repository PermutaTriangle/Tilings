from itertools import chain
from typing import Dict, Iterator, List, Optional, Tuple

from comb_spec_searcher import DisjointUnionStrategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Fusion


class GeneralizedSlidingStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    """
    A strategy that slides column idx and idx + 1.
    """

    def __init__(self, idx: int, rotate: bool = False):
        super().__init__()
        self.idx = idx
        self.rotate = rotate

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        if self.can_slide(comb_class):
            return (self.slide_tiling(comb_class),)
        raise StrategyDoesNotApply(f"Sliding idx {self.idx} does not apply")

    def can_slide(self, comb_class: Tiling) -> bool:
        return MonotoneSlidingFactory.can_slide_col(
            self.idx, comb_class.rotate270() if self.rotate else comb_class
        )

    def slide_tiling(self, comb_class: Tiling) -> Tiling:
        if self.rotate:
            comb_class = comb_class.rotate270()
        child = Tiling(
            self.slide_gps(comb_class.obstructions),
            map(self.slide_gps, comb_class.requirements),
            [ass.__class__(self.slide_gps(ass.gps)) for ass in comb_class.assumptions],
        )
        if self.rotate:
            child = child.rotate90()
        return child

    def formal_step(self) -> str:
        return f"Sliding index {self.idx}"

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], Optional[GriddedPerm]]:
        raise NotImplementedError

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if not comb_class.extra_parameters:
            return super().extra_parameters(comb_class, children)
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        if self.rotate:
            raise NotImplementedError("Not implemented counting for columns")
        child = children[0]
        return (
            {
                comb_class.get_assumption_parameter(
                    ass
                ): child.get_assumption_parameter(
                    ass.__class__(self.slide_gps(ass.gps))
                )
                for ass in comb_class.assumptions
            },
        )

    def slide_gp(self, gp: GriddedPerm) -> GriddedPerm:
        pos = sorted(
            x if x < self.idx or x > self.idx + 1 else x + 1 if x == self.idx else x - 1
            for x, _ in gp.pos
        )
        return GriddedPerm(gp.patt, ((x, 0) for x in pos))

    def slide_gps(self, gps: Tuple[GriddedPerm, ...]) -> Tuple[GriddedPerm, ...]:
        return tuple(map(self.slide_gp, gps))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(idx={self.idx}, rotate={self.rotate})"

    def __str__(self) -> str:
        return f"slide column {self.idx} and {self.idx + 1}"

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["idx"] = self.idx
        d["rotate"] = self.rotate
        return d

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["idx"], d["rotate"])


class MonotoneSlidingFactory(StrategyFactory[Tiling]):
    """
    A factory that creates rules that swaps neighbouring cells if they
    are 'monotone' fusable, i.e., they are a generalized fusion with
    a monotone local extra obstruction.

    This is only looks at n x 1 and 1 x n tilings.
    """

    def __call__(self, comb_class: Tiling) -> Iterator[Rule]:
        parent = comb_class
        rotate = False
        if (
            not comb_class.dimensions[1] == 1
            and comb_class.dimensions[0] == 1
            and not comb_class.requirements
        ):
            comb_class = comb_class.rotate270()
            rotate = True

        if comb_class.dimensions[1] == 1 and not comb_class.requirements:
            # TODO: allow requirements outside of sliding region
            for col in range(comb_class.dimensions[0] - 1):
                if self.can_slide_col(col, comb_class):
                    strategy = GeneralizedSlidingStrategy(col, rotate)
                    child = strategy.slide_tiling(parent)
                    yield strategy(parent, (child,))

    @staticmethod
    def can_slide_col(col: int, comb_class: Tiling) -> bool:
        """
        Return True if the column can be slid.
        """
        local_cells = (
            comb_class.cell_basis()[(col, 0)][0],
            comb_class.cell_basis()[(col + 1, 0)][0],
        )
        if MonotoneSlidingFactory.valid_monotone_sliding_region(
            col, local_cells, comb_class
        ):
            # Check the fusability condition
            shortest = (
                col if len(local_cells[0][0]) <= len(local_cells[1][0]) else col + 1
            )
            algo = Fusion(comb_class, col_idx=col)
            fused_obs = tuple(
                algo.fuse_gridded_perm(gp)
                for gp in comb_class.obstructions
                if not all(x == shortest for x, _ in gp.pos)
            )
            unfused_obs = tuple(
                chain.from_iterable(algo.unfuse_gridded_perm(gp) for gp in fused_obs)
            )
            return comb_class == comb_class.add_obstructions(unfused_obs)
        return False

    @staticmethod
    def valid_monotone_sliding_region(
        col: int, local_cells: Tuple[List[Perm], List[Perm]], comb_class: Tiling
    ) -> bool:
        """
        Return True if the region is a possible valid monotone sliding region.

        That is:
            - neighbouring cells are both increasing or decreasing.
            - the values of non-local obstructions in sliding region are
            monotone and consecutive in value.
        """

        def consecutive_value(col: int, tiling: Tiling, incr: bool = True) -> bool:
            """
            Return True if the values in the column are consecutive,
            and increasing or decreasing if incr is True or False.
            """
            for gp in tiling.obstructions:
                if any(x not in (col, col + 1) for x, _ in gp.pos):
                    points = chain(gp.get_points_col(col), gp.get_points_col(col + 1))
                    values = [y for _, y in points]
                    if incr and not all(x + 1 == y for x, y in zip(values, values[1:])):
                        return False
                    if not incr and not all(
                        x - 1 == y for x, y in zip(values, values[1:])
                    ):
                        return False
            return True

        return (len(local_cells[0]) == 1 and len(local_cells[1]) == 1) and (
            (  # both cells are increasing, and consecutive values are increasing
                local_cells[0][0].is_increasing()
                and local_cells[1][0].is_increasing()
                and consecutive_value(col, comb_class)
            )
            or (  # both cells are decreasing, and consecutive values are decreasing
                (
                    local_cells[0][0].is_decreasing()
                    and local_cells[1][0].is_decreasing()
                    and consecutive_value(col, comb_class, False)
                )
            )
        )

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __str__(self):
        return "monotone sliding"

    @classmethod
    def from_dict(cls, d: dict):
        return cls()

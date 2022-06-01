from typing import Iterator, Optional, Tuple

from comb_spec_searcher import Constructor, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule, Strategy
from tilings import GriddedPerm, Tiling
from tilings.algorithms.fusion import FiniteFusion


class RemoveGapVectorStrategy(Strategy[Tiling, GriddedPerm]):
    """
    A strategy that restricts the set of gap vector for which you have permutation on
    the tiling.

    The ouptut of the strategy is expected to be fusable with regular fusion.
    """

    def __init__(self, row_idx=None, col_idx=None, tracked: bool = False):
        super().__init__(possibly_empty=False)
        self.row_idx = row_idx
        self.col_idx = col_idx
        self.tracked = tracked

    def to_jsonable(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> "RemoveGapVectorStrategy":
        raise NotImplementedError

    def __call__(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Rule:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        return Rule(self, comb_class, children=children)

    def can_be_equivalent(self) -> bool:
        return False

    def is_two_way(self, comb_class: Tiling) -> bool:
        return False

    def is_reversible(self, comb_class: Tiling) -> bool:
        return False

    def shifts(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[int, ...]:
        return (0,)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        algo = self.fusion_algorithm(comb_class)
        if algo.fusable() and algo.get_valid_gap_vectors():
            obs, req = algo.unfused_fused_obs_reqs()
            ass = comb_class.assumptions
            return (Tiling(obs, req, ass),)
        raise StrategyDoesNotApply("Can't remove gap vectors")

    def fusion_algorithm(self, tiling: Tiling) -> FiniteFusion:
        return FiniteFusion(
            tiling, row_idx=self.row_idx, col_idx=self.col_idx, tracked=self.tracked
        )

    def formal_step(self) -> str:
        orientation = "rows" if self.row_idx is not None else "columns"
        idx = self.row_idx if self.row_idx is not None else self.col_idx
        return f"Removing gap vectors on {orientation} {idx} and {idx+1}"

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        raise NotImplementedError

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
        left_points: Optional[int] = None,
    ) -> Iterator[GriddedPerm]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        raise NotImplementedError

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ):
        raise NotImplementedError

    def reverse_constructor(  # pylint: disable=no-self-use
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        raise NotImplementedError


class RemoveGapVectorFactory(StrategyFactory[Tiling]):
    def __init__(self, tracked: bool = False):
        self.tracked = tracked

    def __call__(self, comb_class: Tiling) -> Iterator[RemoveGapVectorStrategy]:
        if comb_class.requirements:
            return
        cols, rows = comb_class.dimensions
        for row_idx in range(rows - 1):
            yield RemoveGapVectorStrategy(
                row_idx=row_idx,
                tracked=self.tracked,
            )
        for col_idx in range(cols - 1):
            yield RemoveGapVectorStrategy(
                col_idx=col_idx,
                tracked=self.tracked,
            )

    def __str__(self) -> str:
        return f"{'tracked ' if self.tracked else ''} removed gap vectors"

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"(tracked={self.tracked})"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["tracked"] = self.tracked
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RemoveGapVectorFactory":
        return cls(**d)

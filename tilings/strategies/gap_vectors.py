import itertools
from typing import Iterator, Optional, Tuple

from comb_spec_searcher import Constructor, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule, Strategy
from tilings import GriddedPerm, Tiling
from tilings.algorithms.fusion import FiniteFusion
from tilings.strategies.assumption_insertion import AddAssumptionsStrategy


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
        algo = FiniteFusion(
            comb_class, row_idx=self.row_idx, col_idx=self.col_idx, tracked=self.tracked
        )
        gvs = set(algo.get_valid_gap_vectors())
        needed_ass = set(
            itertools.chain.from_iterable(
                algo.assumption_for_gap_vector(gv) for gv in gvs
            )
        )
        has_right_ass = all(ass in comb_class.assumptions for ass in needed_ass)
        if has_right_ass and algo.fusable() and algo.get_valid_gap_vectors():
            obs, req = algo.unfused_fused_obs_reqs()
            ass = comb_class.assumptions
            return (Tiling(obs, req, ass),)
        raise StrategyDoesNotApply("Can't remove gap vectors")

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


class RelaxGapVectorStrategy(Strategy[Tiling, GriddedPerm]):
    """
    A strategy that relaxes the set of gap vector for which you have permutation on
    the tiling.
    """

    def __init__(
        self,
        child: Tiling,
        gv: Tuple[int, int],
        *,
        row_idx=None,
        col_idx=None,
        tracked: bool = False,
    ):
        super().__init__(possibly_empty=False)
        self.row_idx = row_idx
        self.col_idx = col_idx
        self.tracked = tracked
        self.gv = gv
        algo = FiniteFusion(child, row_idx=row_idx, col_idx=col_idx)
        self.child = child
        if tracked:
            self.child.add_assumptions(algo.assumption_for_gap_vector(gv))
        self.parent = child.add_obstructions(algo.get_sk_from_gap_vector(gv))

    def to_jsonable(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> "RemoveGapVectorStrategy":
        raise NotImplementedError

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
        if comb_class != self.parent:
            raise StrategyDoesNotApply("Can't remove gap vectors")
        return (self.child,)

    def formal_step(self) -> str:
        orientation = "rows" if self.row_idx is not None else "columns"
        idx = self.row_idx if self.row_idx is not None else self.col_idx
        return f"Relaxing gap vectors on {orientation} {idx} and {idx+1} from {self.gv}"

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


class RelaxGapVectorFactory(StrategyFactory[Tiling]):
    def __init__(self, tracked: bool = False):
        self.tracked = tracked

    def __call__(self, comb_class: Tiling) -> Iterator[Rule]:
        if comb_class.requirements:
            return
        cols, rows = comb_class.dimensions
        for row_idx in range(rows - 1):
            algo = FiniteFusion(comb_class, row_idx=row_idx)
            gap_vectors = algo.get_valid_gap_vectors()
            smaller_gap_vectors = set(
                itertools.chain.from_iterable(
                    self.smaller_gap_vector(gv) for gv in gap_vectors
                )
            )
            for gv in smaller_gap_vectors:
                sk = algo.get_sk_from_gap_vector(gv)
                parent = comb_class.add_obstructions(sk)
                strategy = RelaxGapVectorStrategy(
                    comb_class, gv, row_idx=row_idx, tracked=self.tracked
                )
                if self.tracked:
                    new_ass = [
                        ass
                        for ass in algo.assumption_for_gap_vector(gv)
                        if ass not in comb_class.assumptions
                    ]
                    if new_ass:
                        yield AddAssumptionsStrategy(new_ass)(comb_class)
                yield strategy(parent)
        for col_idx in range(cols - 1):
            algo = FiniteFusion(comb_class, col_idx=col_idx)
            gap_vectors = algo.get_valid_gap_vectors()
            smaller_gap_vectors = set(
                itertools.chain.from_iterable(
                    self.smaller_gap_vector(gv) for gv in gap_vectors
                )
            )
            for gv in smaller_gap_vectors:
                sk = algo.get_sk_from_gap_vector(gv)
                parent = comb_class.add_obstructions(sk)
                strategy = RelaxGapVectorStrategy(
                    comb_class, gv, col_idx=col_idx, tracked=self.tracked
                )
                if self.tracked:
                    new_ass = [
                        ass
                        for ass in algo.assumption_for_gap_vector(gv)
                        if ass not in comb_class.assumptions
                    ]
                    if new_ass:
                        yield AddAssumptionsStrategy(new_ass)(comb_class)
                yield strategy(parent)

    def smaller_gap_vector(self, gv: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
        left = range(0, gv[0] + 1)
        right = range(0, gv[1] + 1)
        return filter((0, 0).__ne__, filter(gv.__ne__, itertools.product(left, right)))

    def __str__(self) -> str:
        return "relaxing gap vectos"

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"(tracked={self.tracked})"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["tracked"] = self.tracked
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RelaxGapVectorFactory":
        return cls(**d)

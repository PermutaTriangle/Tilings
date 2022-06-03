import abc
from itertools import chain
from typing import Dict, Iterator, Optional, Tuple

from comb_spec_searcher import Constructor
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import (
    DisjointUnionStrategy,
    Strategy,
    StrategyFactory,
)
from tilings import GriddedPerm, Tiling, TrackingAssumption
from tilings.algorithms import Fusion

Cell = Tuple[int, int]


class AssumptionOrPointJumpingStrategy(Strategy[Tiling, GriddedPerm]):
    """
    An abstract strategy class which moves requirements or assumptions from a
    column (or row) to its neighbouring column (or row) if the two columns
    are fusable.
    """

    def __init__(self, idx1: int, idx2: int, row: bool):
        self.idx1 = idx1
        self.idx2 = idx2
        self.row = row
        super().__init__()

    @abc.abstractmethod
    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        pass

    def swapped_requirements(
        self, tiling: Tiling
    ) -> Tuple[Tuple[GriddedPerm, ...], ...]:
        return tuple(tuple(map(self._swapped_gp, req)) for req in tiling.requirements)

    def swapped_assumptions(self, tiling: Tiling) -> Tuple[TrackingAssumption, ...]:
        return tuple(
            ass.__class__(map(self._swapped_gp, ass.gps)) for ass in tiling.assumptions
        )

    def _swapped_gp(self, gp: GriddedPerm) -> GriddedPerm:
        if self._in_both_columns(gp):
            return gp
        return GriddedPerm(gp.patt, map(self._swap_cell, gp.pos))

    def _in_both_columns(self, gp: GriddedPerm) -> bool:
        if self.row:
            return any(y == self.idx1 for _, y in gp.pos) and any(
                y == self.idx2 for _, y in gp.pos
            )
        return any(x == self.idx1 for x, _ in gp.pos) and any(
            x == self.idx2 for x, _ in gp.pos
        )

    def _swap_cell(self, cell: Cell) -> Cell:
        x, y = cell
        if self.row:
            if y == self.idx1:
                y = self.idx2
            elif y == self.idx2:
                y = self.idx1
        else:
            if x == self.idx1:
                x = self.idx2
            elif x == self.idx2:
                x = self.idx1
        return x, y

    def _swap_assumption(self, assumption: TrackingAssumption) -> TrackingAssumption:
        return TrackingAssumption(self._swapped_gp(gp) for gp in assumption.gps)

    @abc.abstractmethod
    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        pass

    @abc.abstractmethod
    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm]]:
        pass

    @abc.abstractmethod
    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        pass

    @abc.abstractmethod
    def formal_step(self) -> str:
        pass

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d.pop("ignore_parent")
        d["idx1"] = self.idx1
        d["idx2"] = self.idx2
        d["row"] = self.row
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AssumptionOrPointJumpingStrategy":
        return cls(d.pop("idx1"), d.pop("idx2"), d.pop("row"))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.idx1}, {self.idx2}, {self.row})"


class AssumptionAndPointJumpingStrategy(
    AssumptionOrPointJumpingStrategy,
    DisjointUnionStrategy[Tiling, GriddedPerm],
):
    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        return (
            Tiling(
                comb_class.obstructions,
                self.swapped_requirements(comb_class),
                self.swapped_assumptions(comb_class),
                simplify=False,
                derive_empty=False,
                remove_empty_rows_and_cols=False,
            ),
        )

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError("not implemented map for assumption or point jumping")

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm]]:
        raise NotImplementedError("not implemented map for assumption or point jumping")

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if not comb_class.extra_parameters:
            return super().extra_parameters(comb_class, children)
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        child = children[0]
        return (
            {
                comb_class.get_assumption_parameter(
                    ass
                ): child.get_assumption_parameter(self._swap_assumption(ass))
                for ass in comb_class.assumptions
            },
        )

    def formal_step(self) -> str:
        row_or_col = "rows" if self.row else "cols"
        return (
            f"swapping reqs and assumptions in {row_or_col} {self.idx1} and {self.idx2}"
        )


class AssumptionJumpingStrategy(AssumptionOrPointJumpingStrategy):
    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        return (
            Tiling(
                comb_class.obstructions,
                comb_class.requirements,
                self.swapped_assumptions(comb_class),
                simplify=False,
                derive_empty=False,
                remove_empty_rows_and_cols=False,
            ),
        )

    @staticmethod
    def can_be_equivalent() -> bool:
        return False

    @staticmethod
    def is_two_way(comb_class: Tiling) -> bool:
        return True

    @staticmethod
    def is_reversible(comb_class: Tiling) -> bool:
        return True

    @staticmethod
    def shifts(
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]],
    ) -> Tuple[int, ...]:
        return (0,)

    def constructor(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        raise NotImplementedError

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        raise NotImplementedError

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError("not implemented map for assumption or point jumping")

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm]]:
        raise NotImplementedError("not implemented map for assumption or point jumping")

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if not comb_class.extra_parameters:
            return super().extra_parameters(comb_class, children)
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        raise NotImplementedError

    def formal_step(self) -> str:
        row_or_col = "rows" if self.row else "cols"
        return f"swapping assumptions in {row_or_col} {self.idx1} and {self.idx2}"


class PointJumpingStrategy(AssumptionOrPointJumpingStrategy):
    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        return (
            Tiling(
                comb_class.obstructions,
                self.swapped_requirements(comb_class),
                comb_class.assumptions,
                simplify=False,
                derive_empty=False,
                remove_empty_rows_and_cols=False,
            ),
        )

    @staticmethod
    def can_be_equivalent() -> bool:
        return False

    @staticmethod
    def is_two_way(comb_class: Tiling) -> bool:
        return True

    @staticmethod
    def is_reversible(comb_class: Tiling) -> bool:
        return True

    @staticmethod
    def shifts(
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]],
    ) -> Tuple[int, ...]:
        return (0,)

    def constructor(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        raise NotImplementedError

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        raise NotImplementedError

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError("not implemented map for assumption or point jumping")

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm]]:
        raise NotImplementedError("not implemented map for assumption or point jumping")

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if not comb_class.extra_parameters:
            return super().extra_parameters(comb_class, children)
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        raise NotImplementedError

    def formal_step(self) -> str:
        row_or_col = "rows" if self.row else "cols"
        return f"swapping requirements in {row_or_col} {self.idx1} and {self.idx2}"


class AssumptionAndPointJumpingFactory(StrategyFactory[Tiling]):
    """
    A factory returning the strategies that moves requirements and/or assumptions
    across the boundary of two fusable columns (or rows).
    """

    def __call__(
        self, comb_class: Tiling
    ) -> Iterator[AssumptionOrPointJumpingStrategy]:
        cols, rows = comb_class.dimensions
        gps_to_be_swapped = chain(
            *comb_class.requirements, *[ass.gps for ass in comb_class.assumptions]
        )
        for col in range(cols - 1):
            if any(x in (col, col + 1) for gp in gps_to_be_swapped for x, _ in gp.pos):
                algo = Fusion(comb_class, col_idx=col)
                if algo.fusable():
                    yield AssumptionAndPointJumpingStrategy(col, col + 1, False)
                    yield AssumptionJumpingStrategy(col, col + 1, False)
                    yield PointJumpingStrategy(col, col + 1, False)
        for row in range(rows - 1):
            if any(y in (row, row + 1) for gp in gps_to_be_swapped for y, _ in gp.pos):
                algo = Fusion(comb_class, row_idx=row)
                if algo.fusable():
                    yield AssumptionAndPointJumpingStrategy(row, row + 1, True)
                    yield AssumptionJumpingStrategy(row, row + 1, True)
                    yield PointJumpingStrategy(row, row + 1, True)

    def __str__(self) -> str:
        return "assumption and point jumping"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __eq__(self, other: object) -> bool:
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash(self.__class__)

    @classmethod
    def from_dict(cls, d: dict) -> "AssumptionAndPointJumpingFactory":
        assert not d
        return cls()

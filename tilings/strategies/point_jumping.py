from itertools import chain
from typing import Iterator, Tuple

from comb_spec_searcher.strategies import DisjointUnionStrategy, StrategyFactory
from permuta import Perm
from tilings import GriddedPerm, Tiling, TrackingAssumption
from tilings.algorithms import Fusion

Cell = Tuple[int, int]


class PointJumpingStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    """
    A strategy which moves requirements and assumptions from a column (or row)
    to its neighbouring column (or row) if the two columns are fusable.
    """

    def __init__(self, idx1: int, idx2: int, row: bool):
        self.idx1 = idx1
        self.idx2 = idx2
        self.row = row
        super().__init__()

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling]:
        return (
            Tiling(
                tiling.obstructions,
                self.swapped_requirements(tiling),
                self.swapped_assumptions(tiling),
            ),
        )

    def swapped_requirements(
        self, tiling: Tiling
    ) -> Tuple[Tuple[GriddedPerm, ...], ...]:
        return tuple(tuple(map(self._swapped_gp, req)) for req in tiling.requirements)

    def swapped_assumptions(self, tiling: Tiling) -> Tuple[TrackingAssumption, ...]:
        return tuple(
            TrackingAssumption(map(self._swapped_gp, ass.gps))
            for ass in tiling.assumptions
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

    def backward_map(self, objs: Tuple[GriddedPerm, ...]) -> GriddedPerm:
        return objs[0]

    def forward_map(self, obj: GriddedPerm):
        return (obj,)

    def formal_step(self) -> str:
        row_or_col = "row" if self.row else "col"
        return f"swapping reqs in {row_or_col} {self.idx1} and {self.idx2}"

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d.pop("ignore_parent")
        d["idx1"] = self.idx1
        d["idx2"] = self.idx2
        d["row"] = self.row
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "PointJumpingStrategy":
        return cls(d.pop("idx1"), d.pop("idx2"), d.pop("row"))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.idx1}, {self.idx2}, {self.row})"


class PointJumpingFactory(StrategyFactory[Tiling]):
    """
    A factory returning the disjoint union strategies that moves requirements
    across the boundary of two fusable columns (or rows).
    """

    def __call__(self, comb_class: Tiling) -> Iterator[DisjointUnionStrategy]:
        cols, rows = comb_class.dimensions
        gps_to_be_swapped = chain(
            *comb_class.requirements, *[ass.gps for ass in comb_class.assumptions]
        )
        for col in range(cols - 1):
            if any(
                x == col or x == col + 1 for gp in gps_to_be_swapped for x, _ in gp.pos
            ):
                algo = Fusion(comb_class, col_idx=col)
                if algo.fusable():
                    yield PointJumpingStrategy(col, col + 1, False)
        for row in range(rows - 1):
            if any(
                y == row or y == row + 1 for gp in gps_to_be_swapped for y, _ in gp.pos
            ):
                algo = Fusion(comb_class, row_idx=row)
                if algo.fusable():
                    yield PointJumpingStrategy(row, row + 1, True)

    def __str__(self) -> str:
        return "point jumping"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __eq__(self, other: object) -> bool:
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash(self.__class__)

    @classmethod
    def from_dict(cls, d: dict) -> "PointJumpingFactory":
        assert not d
        return PointJumpingFactory()

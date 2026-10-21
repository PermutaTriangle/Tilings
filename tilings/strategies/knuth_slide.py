"""
The Knuth slide strategy: an equivalence between a tiling and the tiling with a block
of adjacent columns, or of adjacent rows, reversed. See tilings.algorithms.knuth_slide
for when a block slides and why the slide is a bijection.
"""

from typing import Dict, Iterator, Optional, Tuple

from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
from comb_spec_searcher.strategies.strategy import (
    DisjointUnionStrategy,
    StrategyFactory,
)
from tilings import GriddedPerm, Tiling
from tilings.algorithms.knuth_slide import KnuthSlide, mirror_gp

__all__ = ["KnuthSlideFactory", "KnuthSlideStrategy"]


def _flip(cell: Tuple[int, int]) -> Tuple[int, int]:
    return (cell[1], cell[0])


class KnuthSlideStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    """
    The Knuth slide of the block of width columns starting at column col, or with
    transpose, of the block of width rows starting at row col (the slide of the
    inverse tiling's columns).
    """

    def __init__(self, col: int, width: int, transpose: bool = False) -> None:
        super().__init__(possibly_empty=False)
        self.col = col
        self.width = width
        self.transpose = transpose

    def _frame(self, tiling: Tiling) -> Tiling:
        return tiling.inverse() if self.transpose else tiling

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        slide = KnuthSlide(self._frame(comb_class))
        reason = slide.why_not(self.col, self.width)
        if reason is not None:
            raise StrategyDoesNotApply(f"no Knuth slide: {reason}")
        return (self._frame(slide.slide(self.col, self.width)),)

    def _map(self, gridded_perm: GriddedPerm) -> GriddedPerm:
        if self.transpose:
            image = KnuthSlide.slide_gp(
                gridded_perm.inverse(_flip), self.col, self.width
            )
            return image.inverse(_flip)
        return KnuthSlide.slide_gp(gridded_perm, self.col, self.width)

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm]:
        return (self._map(obj),)

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        # the slide is an involution
        yield from (
            self._map(gridded_perm) for gridded_perm in objs if gridded_perm is not None
        )

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if not comb_class.extra_parameters:
            return super().extra_parameters(comb_class, children)
        if children is None:
            children = self.decomposition_function(comb_class)
        child = children[0]
        mapped = {}
        for assumption in comb_class.assumptions:
            gridded_perms = (
                (gridded_perm.inverse(_flip) for gridded_perm in assumption.gps)
                if self.transpose
                else assumption.gps
            )
            image = (
                mirror_gp(gridded_perm, self.col, self.width)
                for gridded_perm in gridded_perms
            )
            if self.transpose:
                image = (gridded_perm.inverse(_flip) for gridded_perm in image)
            mapped[comb_class.get_assumption_parameter(assumption)] = (
                child.get_assumption_parameter(assumption.__class__(image))
            )
        return (mapped,)

    def formal_step(self) -> str:
        kind = "rows" if self.transpose else "columns"
        return f"Knuth slide of the {self.width} {kind} from {kind[:-1]} {self.col}"

    def to_jsonable(self) -> dict:
        return {
            "class_module": "tilings.strategies.knuth_slide",
            "strategy_class": "KnuthSlideStrategy",
            "col": self.col,
            "width": self.width,
            "transpose": self.transpose,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "KnuthSlideStrategy":
        return cls(d["col"], d["width"], d["transpose"])

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(col={self.col}, width={self.width}, "
            f"transpose={self.transpose})"
        )

    def __str__(self) -> str:
        return self.formal_step()


class KnuthSlideFactory(StrategyFactory[Tiling]):
    """
    Every Knuth slide of a tiling that changes it: of blocks of 2 to max_width adjacent
    columns, and with transpose, of rows. With rows False, only blocks within one row
    (or, with transpose, one column); with rows True also the Ferrers version, of
    blocks spanning several rows.
    """

    def __init__(
        self, max_width: int = 3, rows: bool = True, transpose: bool = True
    ) -> None:
        super().__init__()
        self.max_width = max_width
        self.rows = rows
        self.transpose = transpose

    def __call__(self, comb_class: Tiling) -> Iterator[Rule]:
        for transpose in (False, True) if self.transpose else (False,):
            if not KnuthSlide.has_blocks(comb_class, transpose, self.rows):
                continue
            frame = comb_class.inverse() if transpose else comb_class
            slide = KnuthSlide(frame)
            for column, width in slide.blocks(self.max_width, self.rows):
                if slide.why_not(column, width) is not None or slide.is_identity(
                    column, width
                ):
                    continue
                child = slide.slide(column, width)
                if transpose:
                    child = child.inverse()
                if child == comb_class:
                    continue
                yield KnuthSlideStrategy(column, width, transpose)(comb_class, (child,))

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(max_width={self.max_width}, "
            f"rows={self.rows}, transpose={self.transpose})"
        )

    def __str__(self) -> str:
        what = "columns or rows" if self.transpose else "columns"
        where = "" if self.rows else ", in one row of cells"
        return f"Knuth slides of up to {self.max_width} {what}{where}"

    def to_jsonable(self) -> dict:
        jsonable: dict = super().to_jsonable()
        jsonable["max_width"] = self.max_width
        jsonable["rows"] = self.rows
        jsonable["transpose"] = self.transpose
        return jsonable

    @classmethod
    def from_dict(cls, d: dict) -> "KnuthSlideFactory":
        return cls(**d)

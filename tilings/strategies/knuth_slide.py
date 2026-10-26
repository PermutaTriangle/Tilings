"""
The Knuth slide strategy: an equivalence between a tiling and the tiling with a block
of adjacent columns, or of adjacent rows, reversed. See tilings.algorithms.knuth_slide
for when a block slides and why the slide is a bijection.
"""

from typing import Dict, Iterator, Optional, Tuple, cast

from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
from comb_spec_searcher.strategies.strategy import (
    DisjointUnionStrategy,
    StrategyFactory,
)
from tilings import GriddedPerm, Tiling
from tilings.algorithms.knuth_slide import KnuthSlide
from tilings.strategies.symmetry import TilingInverse

__all__ = ["KnuthSlideFactory", "KnuthSlideStrategy"]

# the inverse's maps of gridded permutations, for the slides of blocks of rows
_INVERSE = TilingInverse()


class KnuthSlideStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    """
    The Knuth slide of the block of width columns starting at column start, or with
    transpose, of the block of width rows starting at row start (the slide of the
    inverse tiling's columns).
    """

    def __init__(self, start: int, width: int, transpose: bool = False) -> None:
        super().__init__(possibly_empty=False)
        self.start = start
        self.width = width
        self.transpose = transpose

    def _inverse_if_transposed(self, tiling: Tiling) -> Tiling:
        """The tiling, or with transpose its inverse: the one whose columns slide."""
        return tiling.inverse() if self.transpose else tiling

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        slide = KnuthSlide(self._inverse_if_transposed(comb_class))
        reason = slide.why_not(self.start, self.width)
        if reason is not None:
            raise StrategyDoesNotApply(f"no Knuth slide: {reason}")
        return (self._inverse_if_transposed(slide.slide(self.start, self.width)),)

    def _map(self, comb_class: Tiling, gridded_perm: GriddedPerm) -> GriddedPerm:
        if not self.transpose:
            return KnuthSlide.slide_gridded_perm(gridded_perm, self.start, self.width)
        image = KnuthSlide.slide_gridded_perm(
            _INVERSE.gp_transform(comb_class, gridded_perm), self.start, self.width
        )
        return _INVERSE.inverse_gp_transform(comb_class, image)

    def _mirror(self, comb_class: Tiling, gridded_perm: GriddedPerm) -> GriddedPerm:
        """A requirement's or an assumption's point with the block mirrored."""
        mirror = KnuthSlide.mirror(self.start, self.width)
        if not self.transpose:
            return gridded_perm.apply_map(mirror)
        image = _INVERSE.gp_transform(comb_class, gridded_perm).apply_map(mirror)
        return _INVERSE.inverse_gp_transform(comb_class, image)

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm]:
        return (self._map(comb_class, obj),)

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        # the slide is an involution
        gridded_perm = objs[self.backward_map_index(objs)]
        yield self._map(comb_class, cast(GriddedPerm, gridded_perm))

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
            mirrored = assumption.__class__(
                self._mirror(comb_class, gridded_perm)
                for gridded_perm in assumption.gps
            )
            mapped[comb_class.get_assumption_parameter(assumption)] = (
                child.get_assumption_parameter(mirrored)
            )
        return (mapped,)

    def formal_step(self) -> str:
        kind = "rows" if self.transpose else "columns"
        return f"Knuth slide of the {self.width} {kind} from {kind[:-1]} {self.start}"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d.pop("ignore_parent")
        d.pop("inferrable")
        d.pop("possibly_empty")
        d.pop("workable")
        d["start"] = self.start
        d["width"] = self.width
        d["transpose"] = self.transpose
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "KnuthSlideStrategy":
        return cls(d["start"], d["width"], d["transpose"])

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(start={self.start}, width={self.width}, "
            f"transpose={self.transpose})"
        )


class KnuthSlideFactory(StrategyFactory[Tiling]):
    """
    Every Knuth slide of a tiling that changes it: of blocks of 2 to max_width adjacent
    columns, and with slide_rows, of blocks of 2 to max_width adjacent rows too. A
    block of columns may span several rows of cells, and a block of rows several
    columns of cells; with one_line_only, a block of columns lies in one row of cells,
    and a block of rows in one column of cells.
    """

    def __init__(
        self, max_width: int = 3, one_line_only: bool = False, slide_rows: bool = True
    ) -> None:
        super().__init__()
        self.max_width = max_width
        self.one_line_only = one_line_only
        self.slide_rows = slide_rows

    def __call__(self, comb_class: Tiling) -> Iterator[Rule]:
        for transpose in (False, True) if self.slide_rows else (False,):
            if not KnuthSlide.has_blocks(comb_class, transpose, self.one_line_only):
                continue
            frame = comb_class.inverse() if transpose else comb_class
            slide = KnuthSlide(frame)
            for column, width in slide.blocks(self.max_width, self.one_line_only):
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
            f"one_line_only={self.one_line_only}, slide_rows={self.slide_rows})"
        )

    def __str__(self) -> str:
        what = "columns or rows" if self.slide_rows else "columns"
        where = ", in one line of cells" if self.one_line_only else ""
        return f"Knuth slides of up to {self.max_width} {what}{where}"

    def to_jsonable(self) -> dict:
        jsonable: dict = super().to_jsonable()
        jsonable["max_width"] = self.max_width
        jsonable["one_line_only"] = self.one_line_only
        jsonable["slide_rows"] = self.slide_rows
        return jsonable

    @classmethod
    def from_dict(cls, d: dict) -> "KnuthSlideFactory":
        return cls(**d)

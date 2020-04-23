"""
The row and column separation strategy. The details of the algorithm can be
found in the algorithms folder.
"""
from typing import Tuple, Optional

from comb_spec_searcher import DisjointUnionStrategy
from tilings import GriddedPerm, Tiling
from tilings.algorithms import RowColSeparation


__all__ = ["RowColumnSeparationStrategy"]


class RowColumnSeparationStrategy(DisjointUnionStrategy):
    """
    An inferral strategy that tries to separate cells in rows and columns.
    """

    def __init__(self):
        super().__init__(
            ignore_parent=True, inferrable=True, possibly_empty=False, workable=True,
        )

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, ...]:
        """Return the separated tiling if it separates, otherwise None."""
        rcs = self.row_col_sep_algorithm(tiling)
        if rcs.separable():
            return (rcs.separated_tiling(),)

    def row_col_sep_algorithm(self, tiling: Tiling):
        """Return the algorithm class using tiling."""
        return RowColSeparation(tiling)

    def formal_step(self) -> str:
        """Return formal step."""
        return "row and column separation"

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[GriddedPerm, ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> GriddedPerm:
        """This method will enable us to generate objects, and sample. """
        if children is None:
            children = self.decomposition_function(tiling)
        raise NotImplementedError

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm, ...]:
        """This function will enable us to have a quick membership test."""
        if children is None:
            children = self.decomposition_function(tiling)
        raise NotImplementedError

    def __str__(self) -> str:
        return "row and column separation"

    def __repr__(self) -> str:
        return "RowColumnSeparationStrategy()"
"""
The row and column separation strategy. The details of the algorithm can be
found in the algorithms folder.
"""
from typing import Dict, Iterator, Optional, Tuple

from comb_spec_searcher import DisjointUnionStrategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from tilings import GriddedPerm, Tiling
from tilings.algorithms import RowColSeparation
from tilings.map import CellMap

__all__ = ["RowColumnSeparationStrategy"]


Cell = Tuple[int, int]


class RowColumnSeparationStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    """
    An inferral strategy that tries to separate cells in rows and columns.
    """

    _cell_maps: Dict[Tiling, Tuple[CellMap, CellMap]] = {}

    def __init__(self):
        super().__init__(
            ignore_parent=True, inferrable=True, possibly_empty=False, workable=True
        )

    def forward_cell_map(self, tiling: Tiling) -> CellMap:
        return self._get_cell_maps(tiling)[0]

    def backward_cell_map(self, tiling: Tiling) -> CellMap:
        return self._get_cell_maps(tiling)[1]

    def _get_cell_maps(self, tiling: Tiling) -> Tuple[CellMap, CellMap]:
        res = self._cell_maps.get(tiling)
        if res is None:
            forward_cell_map = self.row_col_sep_algorithm(tiling).get_cell_map()
            backward_cell_map = forward_cell_map.inverse()
            self._cell_maps[tiling] = forward_cell_map, backward_cell_map
        else:
            forward_cell_map, backward_cell_map = res
        return forward_cell_map, backward_cell_map

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        """Return the separated tiling if it separates, otherwise None."""
        rcs = self.row_col_sep_algorithm(comb_class)
        if rcs.separable():
            return (rcs.separated_tiling(),)

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
        algo = self.row_col_sep_algorithm(comb_class)
        mapped_params = tuple(map(algo.map_param, comb_class.parameters))
        return (
            {
                comb_class.get_parameter_name(param): child.get_parameter_name(
                    mapped_param
                )
                for param, mapped_param in zip(comb_class.parameters, mapped_params)
                # TODO: previsously checked that the tracked assumption had some gps
                # here. What is the equivalence in our case.
            },
        )

    @staticmethod
    def row_col_sep_algorithm(tiling: Tiling) -> RowColSeparation:
        """Return the algorithm class using tiling."""
        return RowColSeparation(tiling)

    @staticmethod
    def formal_step() -> str:
        """Return formal step."""
        return "row and column separation"

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        """This method will enable us to generate objects, and sample."""
        if children is None:
            children = self.decomposition_function(comb_class)
        gp = objs[0]
        assert gp is not None
        yield self.backward_cell_map(comb_class).map_gp(gp)

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm]:
        """This function will enable us to have a quick membership test."""
        if children is None:
            children = self.decomposition_function(comb_class)
        return (self.forward_cell_map(comb_class).map_gp(obj),)

    def __str__(self) -> str:
        return "row and column separation"

    def __repr__(self) -> str:
        return "RowColumnSeparationStrategy()"

    @classmethod
    def from_dict(cls, d) -> "RowColumnSeparationStrategy":
        return cls()

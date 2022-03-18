"""The cell reduction strategy."""
from itertools import chain
from typing import Callable, Dict, Iterator, List, Optional, Set, Tuple, cast

import sympy

from comb_spec_searcher import Constructor, Strategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.typing import (
    Parameters,
    RelianceProfile,
    SubObjects,
    SubRecs,
    SubSamplers,
    SubTerms,
    Terms,
)
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption

Cell = Tuple[int, int]


class CellReductionConstructor(Constructor):
    def __init__(self, parameter: str):
        self.parameter = parameter

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        raise NotImplementedError

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        raise NotImplementedError

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[Tuple[Parameters, Tuple[List[Optional[GriddedPerm]]]]]:
        raise NotImplementedError

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ) -> Tuple[GriddedPerm]:
        raise NotImplementedError

    def equiv(
        self, other: "Constructor", data: Optional[object] = None
    ) -> Tuple[bool, Optional[object]]:
        raise NotImplementedError


class CellReductionStrategy(Strategy[Tiling, GriddedPerm]):
    """A strategy that replaces the cell with an increasing or decreasing cell."""

    def __init__(
        self,
        cell: Cell,
        increasing: bool,
        tracked: bool = True,
    ):
        self.cell = cell
        self.tracked = tracked
        self.increasing = increasing
        super().__init__()

    @staticmethod
    def can_be_equivalent() -> bool:
        return False

    @staticmethod
    def is_two_way(comb_class: Tiling) -> bool:
        return False

    @staticmethod
    def is_reversible(comb_class: Tiling) -> bool:
        return False

    @staticmethod
    def shifts(
        comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[int, ...]:
        return (0, 0)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, Tiling]:
        if self.increasing:
            extra = Perm((1, 0))
        else:
            extra = Perm((0, 1))
        reduced_obs = sorted(
            [
                ob
                for ob in comb_class.obstructions
                if not ob.pos[0] == self.cell or not ob.is_single_cell()
            ]
            + [GriddedPerm.single_cell(extra, self.cell)]
        )
        reduced_tiling = Tiling(
            reduced_obs,
            comb_class.requirements,
            comb_class.assumptions,
            remove_empty_rows_and_cols=False,
            derive_empty=False,
            simplify=False,
            sorted_input=True,
        )
        local_basis = comb_class.sub_tiling([self.cell])
        if self.tracked:
            return (
                reduced_tiling.add_assumption(
                    TrackingAssumption.from_cells([self.cell])
                ),
                local_basis,
            )
        return reduced_tiling, local_basis

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> CellReductionConstructor:
        if not self.tracked:
            raise NotImplementedError("The reduction strategy was not tracked")
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't reduce the cell")
        ass = TrackingAssumption.from_cells([self.cell])
        child_param = children[0].get_assumption_parameter(ass)
        gp = GriddedPerm.point_perm(self.cell)
        if any(gp in assumption.gps for assumption in comb_class.assumptions):
            raise NotImplementedError
        return CellReductionConstructor(child_param)

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't reduce the cell")
        raise NotImplementedError

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str]]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        raise NotImplementedError

    def formal_step(self) -> str:
        return f"reducing cell {self.cell}"

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        if children is None:
            children = self.decomposition_function(comb_class)
        raise NotImplementedError

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        raise NotImplementedError

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d.pop("ignore_parent")
        d.pop("inferrable")
        d.pop("possibly_empty")
        d.pop("workable")
        d["cell"] = self.cell
        d["tracked"] = self.tracked
        d["increasing"] = self.increasing
        return d

    def __repr__(self) -> str:
        args = ", ".join(
            [
                f"cell={self.cell!r}",
                f"increasing={self.increasing!r}",
                f"tracked={self.tracked!r}",
            ]
        )
        return f"{self.__class__.__name__}({args})"

    @classmethod
    def from_dict(cls, d: dict) -> "CellReductionStrategy":
        cell = cast(Tuple[int, int], tuple(d.pop("cell")))
        tracked = d.pop("tracked")
        increasing = d.pop("increasing")
        assert not d
        return cls(cell, increasing, tracked)

    @staticmethod
    def get_eq_symbol() -> str:
        return "↣"


class CellReductionFactory(StrategyFactory[Tiling]):
    def __init__(self, tracked: bool):
        self.tracked = tracked
        super().__init__()

    def __call__(self, comb_class: Tiling) -> Iterator[CellReductionStrategy]:
        cell_bases = comb_class.cell_basis()
        for cell in self.reducible_cells(comb_class):
            if not (  # a finite cell
                any(patt.is_increasing() for patt in cell_bases[cell][0])
                and any(patt.is_decreasing() for patt in cell_bases[cell][0])
            ):
                yield CellReductionStrategy(cell, True, self.tracked)
                yield CellReductionStrategy(cell, False, self.tracked)

    @staticmethod
    def reducible_cells(tiling: Tiling) -> Set[Cell]:
        """Return the set of cells with at most one point in a crossing
        gridded permutation touching them"""

        def gp_in_row_and_col(gp: GriddedPerm, cell: Cell) -> bool:
            """Return True if there are points touching a cell in the row and col of
            cell that isn't cell itself."""
            x, y = cell
            return (
                len(set(gp.pos[idx][1] for idx, _ in gp.get_points_col(x))) > 1
                and len(set(gp.pos[idx][0] for idx, _ in gp.get_points_row(y))) > 1
            )

        gps: Iterator[GriddedPerm] = chain(tiling.obstructions, *tiling.requirements)
        cells = set(tiling.active_cells) - set(tiling.point_cells)
        for gp in gps:
            if not cells:
                break
            if not gp.is_localized():
                seen = set()
                for cell in gp.pos:
                    if cell in seen or gp_in_row_and_col(gp, cell):
                        cells.discard(cell)
                    seen.add(cell)
        return cells

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.tracked})"

    def __str__(self) -> str:
        return ("tracked " if self.tracked else "") + "cell reduction factory"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["tracked"] = self.tracked
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "CellReductionFactory":
        return cls(d["tracked"])

"""The deflation strategy."""
from typing import Callable, Dict, Iterator, List, Optional, Tuple, cast

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


class DeflationConstructor(Constructor):
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


class DeflationStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(
        self,
        cell: Cell,
        sum_deflate: bool,
        tracked: bool = True,
    ):
        self.cell = cell
        self.tracked = tracked
        self.sum_deflate = sum_deflate
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
        if self.sum_deflate:
            extra = Perm((1, 0))
        else:
            extra = Perm((0, 1))
        deflated_tiling = comb_class.add_obstruction(extra, (self.cell, self.cell))
        local_basis = comb_class.sub_tiling([self.cell])
        if self.tracked:
            return (
                deflated_tiling.add_assumption(
                    TrackingAssumption.from_cells([self.cell])
                ),
                local_basis,
            )
        return deflated_tiling, local_basis

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> DeflationConstructor:
        if not self.tracked:
            raise NotImplementedError("The deflation strategy was not tracked")
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't deflate the cell")
        ass = TrackingAssumption.from_cells([self.cell])
        child_param = children[0].get_assumption_parameter(ass)
        gp = GriddedPerm.point_perm(self.cell)
        if any(gp in assumption.gps for assumption in comb_class.assumptions):
            raise NotImplementedError
        return DeflationConstructor(child_param)

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Can't deflate the cell")
        raise NotImplementedError

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str]]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        raise NotImplementedError

    def cell_maps(
        self, tiling: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[Cell, List[Cell]], ...]:
        if children is None:
            children = self.decomposition_function(tiling)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        return ({cell: [cell] for cell in tiling.active_cells}, {self.cell: [(0, 0)]})

    def formal_step(self) -> str:
        return f"deflating cell {self.cell}"

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
        d["sum_deflate"] = self.sum_deflate
        return d

    def __repr__(self) -> str:
        args = ", ".join(
            [
                f"cell={self.cell!r}",
                f"sum_deflate={self.sum_deflate!r}",
                f"tracked={self.tracked!r}",
            ]
        )
        return f"{self.__class__.__name__}({args})"

    @classmethod
    def from_dict(cls, d: dict) -> "DeflationStrategy":
        cell = d.pop("cell")
        tracked = d.pop("tracked")
        assert not d
        return cls(cell, tracked)

    @staticmethod
    def get_eq_symbol() -> str:
        return "↣"


class DeflationFactory(StrategyFactory[Tiling]):
    def __init__(self, tracked: bool):
        self.tracked = tracked
        super().__init__()

    def __call__(self, comb_class: Tiling) -> Iterator[DeflationStrategy]:
        if comb_class.requirements:
            # TODO: this is obviously too strong
            return
        for cell in comb_class.active_cells:
            if self.can_deflate(comb_class, cell, True):
                yield DeflationStrategy(cell, True, self.tracked)
            if self.can_deflate(comb_class, cell, False):
                yield DeflationStrategy(cell, False, self.tracked)

    @staticmethod
    def can_deflate(tiling: Tiling, cell: Cell, sum_deflate: bool) -> bool:
        alone_in_row = tiling.only_cell_in_row(cell)
        alone_in_col = tiling.only_cell_in_col(cell)

        if alone_in_row and alone_in_col:
            return False

        deflate_patt = GriddedPerm.single_cell(
            Perm((1, 0)) if sum_deflate else Perm((0, 1)), cell
        )

        # we must be sure that no cell in a row or column can interleave
        # with any reinflated components, so collect cells that do not.
        cells_not_interleaving = set([cell])

        for ob in tiling.obstructions:
            if ob == deflate_patt:
                break  # False
            if ob.is_single_cell() or not ob.occupies(cell):
                continue
            number_points_in_cell = sum(1 for c in ob.pos if c == cell)
            if number_points_in_cell == 1:
                if len(ob) == 2:
                    # not interleaving with cell as separating if
                    # in same row or column
                    other_cell = [c for c in ob.pos if c != cell][0]
                    cells_not_interleaving.add(other_cell)
            elif number_points_in_cell == 2:
                if len(ob) != 3:
                    break  # False
                patt_in_cell = ob.get_gridded_perm_in_cells((cell,))
                if patt_in_cell != deflate_patt:
                    # you can interleave with components
                    break  # False
                # we need the other cell to be in between the intended deflate
                # patt in either the row or column
                other_cell = [c for c in ob.pos if c != cell][0]
                if DeflationFactory.point_in_between(
                    ob, True, cell, other_cell
                ) or DeflationFactory.point_in_between(ob, False, cell, other_cell):
                    # this cell does not interleave with inflated components
                    cells_not_interleaving.add(other_cell)
                    continue
                break  # False
            elif number_points_in_cell >= 3:
                # you can interleave with components
                break  # False
        else:
            # check that do not interleave with any cells in row or column.
            return cells_not_interleaving >= tiling.cells_in_row(
                cell[1]
            ) and cells_not_interleaving >= tiling.cells_in_col(cell[0])
        return False

    @staticmethod
    def point_in_between(
        ob: GriddedPerm, row: bool, cell: Cell, other_cell: Cell
    ) -> bool:
        """Return true if point in other cell is in between point in cell.
        Assumes a length 3 pattern, and to be told if row or column."""
        patt = cast(Tuple[int, int, int], ob.patt)
        if row:
            left = other_cell[0] < cell[0]
            if left:
                return bool(patt[0] == 1)
            return bool(patt[2] == 1)
        below = other_cell[1] < cell[1]
        if below:
            return bool(patt[1] == 0)
        return bool(patt[1] == 2)

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.tracked})"

    def __str__(self) -> str:
        return ("tracked " if self.tracked else "") + "deflation factory"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["tracked"] = self.tracked
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "DeflationFactory":
        return cls(d["tracked"])

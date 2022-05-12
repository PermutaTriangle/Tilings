"""
The directionless point placement strategy that is counted
by the 'pointing' constructor.
"""
from collections import Counter
from itertools import product
from typing import (
    Callable,
    Dict,
    FrozenSet,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
    cast,
)

from comb_spec_searcher import Strategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies.constructor.disjoint import DisjointUnion
from comb_spec_searcher.strategies.rule import Rule
from comb_spec_searcher.strategies.strategy import StrategyFactory
from comb_spec_searcher.typing import CombinatorialClassType, SubTerms, Terms
from permuta.misc import DIR_NONE
from tilings import GriddedPerm, Tiling
from tilings.algorithms import RequirementPlacement
from tilings.assumptions import ComponentAssumption, TrackingAssumption
from tilings.strategies.assumption_insertion import AddAssumptionsStrategy
from tilings.strategies.obstruction_inferral import ObstructionInferralStrategy
from tilings.tiling import Cell

from .unfusion import DivideByN, ReverseDivideByN


class PointingStrategy(Strategy[Tiling, GriddedPerm]):
    def can_be_equivalent(self) -> bool:
        return False

    def is_two_way(self, comb_class: Tiling) -> bool:
        return True

    def is_reversible(self, comb_class: Tiling) -> bool:
        return True

    def shifts(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]],
    ) -> Tuple[int, ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        assert children is not None
        return tuple(0 for _ in children)

    @staticmethod
    def already_placed_cells(comb_class: Tiling) -> FrozenSet[Cell]:
        return frozenset(
            cell
            for cell in comb_class.point_cells
            if comb_class.only_cell_in_row_and_col(cell)
        )

    def cells_to_place(self, comb_class: Tiling) -> FrozenSet[Cell]:
        return comb_class.active_cells - self.already_placed_cells(comb_class)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        cells = self.cells_to_place(comb_class)
        if cells:
            return tuple(
                comb_class.place_point_in_cell(cell, DIR_NONE) for cell in sorted(cells)
            )
        raise StrategyDoesNotApply("The tiling is just point cells!")

    def formal_step(self) -> str:
        return "directionless point placement"

    def constructor(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> DivideByN:
        if children is None:
            children = self.decomposition_function(comb_class)
        return DivideByN(
            comb_class,
            children,
            -len(self.already_placed_cells(comb_class)),
            self.extra_parameters(comb_class, children),
        )

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> ReverseDivideByN:
        if children is None:
            children = self.decomposition_function(comb_class)
        return ReverseDivideByN(
            comb_class,
            children,
            idx,
            -len(self.already_placed_cells(comb_class)),
            self.extra_parameters(comb_class, children),
        )

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

    def extra_parameters(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Dict[str, str], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        cells = self.cells_to_place(comb_class)
        algo = RequirementPlacement(comb_class, True, True)
        res = []
        for child, cell in zip(children, sorted(cells)):
            params: Dict[str, str] = {}
            mapped_assumptions = [
                child.forward_map.map_assumption(ass).avoiding(child.obstructions)
                for ass in algo.stretched_assumptions(cell)
            ]
            for ass, mapped_ass in zip(comb_class.assumptions, mapped_assumptions):
                if mapped_ass.gps:
                    params[
                        comb_class.get_assumption_parameter(ass)
                    ] = child.get_assumption_parameter(mapped_ass)
            res.append(params)
        return tuple(res)

    @classmethod
    def from_dict(cls, d: dict) -> "PointingStrategy":
        return cls(**d)


class DivideByK(DivideByN):
    """
    A constructor that works as disjoint union
    but divides the values by k + shift.
    """

    def __init__(
        self,
        parent: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...],
        shift: int,
        parameter: str,
        extra_parameters: Optional[Tuple[Dict[str, str], ...]] = None,
    ):
        self.parameter = parameter
        self.division_index = parent.extra_parameters.index(parameter)
        super().__init__(parent, children, shift, extra_parameters)

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        if n + self.shift <= 0:
            return self.initial_conditions[n]
        terms = DisjointUnion.get_terms(self, parent_terms, subterms, n)
        return Counter(
            {
                key: value // (key[self.division_index] + self.shift)
                if (key[self.division_index] + self.shift) != 0
                else value
                for key, value in terms.items()
            }
        )

    def __str__(self):
        return f"divide by {self.parameter}"


class ReverseDivideByK(ReverseDivideByN):
    """
    The complement version of DivideByK.
    It works as Complement, but multiplies by k + shift the original left hand side.
    """

    def __init__(
        self,
        parent: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...],
        idx: int,
        shift: int,
        parameter: str,
        extra_parameters: Optional[Tuple[Dict[str, str], ...]] = None,
    ):
        self.parameter = parameter
        self.division_index = parent.extra_parameters.index(parameter)
        super().__init__(parent, children, idx, shift, extra_parameters)

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        if n + self.shift <= 0:
            return self.initial_conditions[n]
        parent_terms_mapped: Terms = Counter()
        for param, value in subterms[0](n).items():
            if value:
                # This is the only change from complement
                K = param[self.division_index] + self.shift
                assert K >= 0
                if K == 0:
                    parent_terms_mapped[self._parent_param_map(param)] += value
                else:
                    parent_terms_mapped[self._parent_param_map(param)] += value * K
        children_terms = subterms[1:]
        for child_terms, param_map in zip(children_terms, self._children_param_maps):
            # we subtract from total
            for param, value in child_terms(n).items():
                mapped_param = self._parent_param_map(param_map(param))
                parent_terms_mapped[mapped_param] -= value
                assert parent_terms_mapped[mapped_param] >= 0
                if parent_terms_mapped[mapped_param] == 0:
                    parent_terms_mapped.pop(mapped_param)

        return parent_terms_mapped

    def __str__(self):
        return f"reverse divide by {self.parameter}"


class AssumptionPointingStrategy(PointingStrategy):
    def __init__(
        self,
        assumption: TrackingAssumption,
        ignore_parent: bool = False,
        inferrable: bool = True,
        possibly_empty: bool = True,
        workable: bool = True,
    ):
        self.assumption = assumption
        assert not isinstance(assumption, ComponentAssumption)
        self.cells = frozenset(gp.pos[0] for gp in assumption.gps)
        super().__init__(ignore_parent, inferrable, possibly_empty, workable)

    def cells_to_place(self, comb_class: Tiling) -> FrozenSet[Cell]:
        return super().cells_to_place(comb_class).intersection(self.cells)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        if self.assumption not in comb_class.assumptions:
            raise StrategyDoesNotApply("The assumption is not on tiling")
        cells = self.cells_to_place(comb_class)
        if cells:
            return (
                comb_class.add_obstructions(
                    [GriddedPerm.point_perm(cell) for cell in cells]
                ),
            ) + tuple(
                comb_class.place_point_in_cell(cell, DIR_NONE) for cell in sorted(cells)
            )
        raise StrategyDoesNotApply("The assumption is just point cells!")

    def formal_step(self) -> str:
        return super().formal_step() + f" in cells {set(self.cells)}"

    def constructor(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> DivideByN:
        if children is None:
            children = self.decomposition_function(comb_class)
        return DivideByK(
            comb_class,
            children,
            -len(self.cells.intersection(self.already_placed_cells(comb_class))),
            comb_class.get_assumption_parameter(self.assumption),
            self.extra_parameters(comb_class, children),
        )

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> ReverseDivideByN:
        if children is None:
            children = self.decomposition_function(comb_class)
        return ReverseDivideByK(
            comb_class,
            children,
            idx,
            -len(self.cells.intersection(self.already_placed_cells(comb_class))),
            comb_class.get_assumption_parameter(self.assumption),
            self.extra_parameters(comb_class, children),
        )

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        empty_params = ObstructionInferralStrategy(
            [GriddedPerm.point_perm(cell) for cell in self.cells_to_place(comb_class)]
        ).extra_parameters(comb_class)
        return empty_params + super().extra_parameters(comb_class, children[1:])

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["assumption"] = self.assumption.to_jsonable()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AssumptionPointingStrategy":
        assumption = TrackingAssumption.from_dict(d.pop("assumption"))
        return cls(assumption=assumption, **d)

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + f"({repr(self.assumption)}, {self.ignore_parent}, "
            f"{self.inferrable}, {self.possibly_empty}, {self.workable})"
        )


class AssumptionPointingFactory(StrategyFactory[Tiling]):
    def __call__(self, comb_class: Tiling) -> Iterator[AssumptionPointingStrategy]:
        for assumption in comb_class.assumptions:
            if not isinstance(assumption, ComponentAssumption):
                yield AssumptionPointingStrategy(assumption)

    def __str__(self) -> str:
        return "assumption pointing strategy"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d: dict) -> "AssumptionPointingFactory":
        return cls()


class RequirementPointingStrategy(PointingStrategy):
    def __init__(
        self,
        gps: Tuple[GriddedPerm, ...],
        indices: Tuple[int, ...],
        ignore_parent: bool = False,
        inferrable: bool = True,
        possibly_empty: bool = True,
        workable: bool = True,
    ):
        assert len(gps) == len(indices)
        self.gps = gps
        self.indices = indices
        super().__init__(ignore_parent, inferrable, possibly_empty, workable)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        cells = self.cells_to_place(comb_class)
        algo = RequirementPlacement(comb_class)
        if cells:
            return algo.place_point_of_req(
                self.gps, self.indices, DIR_NONE, include_not=True, cells=cells
            )
        raise StrategyDoesNotApply("The assumption is just point cells!")

    def formal_step(self) -> str:
        return super().formal_step() + f" in {self.gps} at indices {self.indices}"

    def extra_parameters(
        self: Union[
            "RequirementPointingStrategy", "RequirementAssumptionPointingStrategy"
        ],
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Dict[str, str], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        even_index = tuple(child for idx, child in enumerate(children) if idx % 2 == 0)
        odd_index = tuple(child for idx, child in enumerate(children) if idx % 2 == 1)
        res: List[Optional[Dict[str, str]]] = [None for _ in children]
        for idx, param in enumerate(
            PointingStrategy.extra_parameters(self, comb_class, even_index)
        ):
            res[2 * idx] = param
        for idx, param in enumerate(
            PointingStrategy.extra_parameters(self, comb_class, odd_index)
        ):
            res[2 * idx + 1] = param
        cast(List[Dict[str, str]], res)
        return tuple(cast(List[Dict[str, str]], res))

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["gps"] = [gp.to_jsonable() for gp in self.gps]
        d["indices"] = self.indices
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementPointingStrategy":
        return cls(
            tuple(GriddedPerm.from_dict(gp) for gp in d.pop("gps")),
            tuple(d.pop("indices")),
            **d,
        )

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + f"({self.gps}, {self.indices}, {self.ignore_parent}, "
            f"{self.inferrable}, {self.possibly_empty}, {self.workable})"
        )


class RequirementAssumptionPointingStrategy(AssumptionPointingStrategy):
    def __init__(
        self,
        gps: Tuple[GriddedPerm, ...],
        indices: Tuple[int, ...],
        ignore_parent: bool = False,
        inferrable: bool = True,
        possibly_empty: bool = True,
        workable: bool = True,
    ):
        assert len(gps) == len(indices)
        self.gps = gps
        self.indices = indices
        self.cells = frozenset(gp.pos[idx] for gp, idx in zip(gps, indices))
        self.assumption = TrackingAssumption.from_cells(self.cells)

        super().__init__(
            self.assumption, ignore_parent, inferrable, possibly_empty, workable
        )

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        if self.assumption not in comb_class.assumptions:
            raise StrategyDoesNotApply("The assumption is not on tiling")
        cells = self.cells_to_place(comb_class)
        algo = RequirementPlacement(comb_class)
        if cells:
            return (
                comb_class.add_obstructions(
                    [GriddedPerm.point_perm(cell) for cell in cells]
                ),
            ) + algo.place_point_of_req(
                self.gps, self.indices, DIR_NONE, include_not=True
            )
        raise StrategyDoesNotApply("The assumption is just point cells!")

    def formal_step(self) -> str:
        return super().formal_step() + f" in {self.gps} at indices {self.indices}"

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        empty_params = ObstructionInferralStrategy(
            [GriddedPerm.point_perm(cell) for cell in self.cells_to_place(comb_class)]
        ).extra_parameters(comb_class)
        rest = RequirementPointingStrategy.extra_parameters(
            self, comb_class, children[1:]
        )
        return empty_params + tuple(rest)

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["gps"] = [gp.to_jsonable() for gp in self.gps]
        d["indices"] = self.indices
        d.pop("assumption")
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementAssumptionPointingStrategy":
        return cls(
            tuple(GriddedPerm.from_dict(gp) for gp in d.pop("gps")),
            tuple(d.pop("indices")),
            **d,
        )

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + f"({self.gps}, {self.indices}, {self.ignore_parent}, "
            f"{self.inferrable}, {self.possibly_empty}, {self.workable})"
        )


class RequirementPointingFactory(StrategyFactory[Tiling]):
    def __call__(self, comb_class: Tiling) -> Iterator[Rule]:
        for gp, indices in product(
            Tiling(comb_class.obstructions).gridded_perms_of_length(2), [(0,), (1,)]
        ):
            gps = (gp,)
            untracked_strategy = RequirementPointingStrategy(gps, indices)
            yield untracked_strategy(comb_class)
            strategy = RequirementAssumptionPointingStrategy(gps, indices)
            if untracked_strategy.cells_to_place(comb_class) != strategy.cells_to_place(
                comb_class
            ):
                parent = comb_class
                if strategy.assumption not in comb_class.assumptions:
                    rule = AddAssumptionsStrategy([strategy.assumption])(comb_class)
                    yield rule
                    parent = rule.children[0]
                yield strategy(parent)

        # for gps in comb_class.requirements:
        #     for indices in product(*[range(len(gp)) for gp in gps]):
        #         untracked_strategy = RequirementPointingStrategy(gps, indices)
        #         yield untracked_strategy(comb_class)
        #         strategy = RequirementAssumptionPointingStrategy(gps, indices)
        #         if untracked_strategy.cells_to_place(
        #             comb_class
        #         ) != strategy.cells_to_place(comb_class):
        #             parent = comb_class
        #             if strategy.assumption not in comb_class.assumptions:
        #                 rule = AddAssumptionsStrategy([strategy.assumption])(
        #                     comb_class
        #                 )
        #                 yield rule
        #                 parent = rule.children[0]
        #             yield strategy(parent)

    def __str__(self) -> str:
        return "requirement pointing strategy"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementPointingFactory":
        return cls()

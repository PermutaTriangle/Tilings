from itertools import chain, product
from typing import Dict, Iterator, Optional, Tuple

from comb_spec_searcher import DisjointUnionStrategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from tilings import GriddedPerm, Tiling


class RefinePredicatesStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    def __init__(
        self,
        ignore_parent: bool = True,
        inferrable: bool = False,
        possibly_empty: bool = True,
        workable: bool = True,
    ):
        super().__init__(ignore_parent, inferrable, possibly_empty, workable)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        if comb_class.predicate_assumptions:
            without_predicates = comb_class.remove_assumptions().add_assumptions(
                comb_class.tracking_assumptions
            )
            children = []
            for assumptions in product(
                *[ass.refinements() for ass in comb_class.predicate_assumptions]
            ):
                children.append(without_predicates.add_assumptions(chain(*assumptions)))
            return tuple(children)
        raise StrategyDoesNotApply

    def formal_step(self) -> str:
        return "predicate refinement"

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
        return tuple(
            {
                comb_class.get_assumption_parameter(
                    ass
                ): child.get_assumption_parameter(child.forward_map.map_assumption(ass))
                for ass in comb_class.tracking_assumptions
                if child.forward_map.map_assumption(ass).gps
            }
            for child in children
        )

    @classmethod
    def from_dict(cls, d: dict) -> "RefinePredicatesStrategy":
        return cls(**d)

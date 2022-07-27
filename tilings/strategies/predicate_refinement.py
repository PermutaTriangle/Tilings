from itertools import chain, product
from typing import Dict, Iterator, List, Optional, Tuple, cast

from comb_spec_searcher import DisjointUnionStrategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from tilings import GriddedPerm, Tiling
from tilings.assumptions import EvenCountAssumption, OddCountAssumption


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
        try:
            assumption_to_refine = next(
                ass for ass in comb_class.predicate_assumptions if ass.can_be_refined()
            )
            without_predicate = comb_class.remove_assumption(assumption_to_refine)
            children = []
            for assumptions in assumption_to_refine.refinements():
                children.append(without_predicate.add_assumptions(assumptions))
            return tuple(children)
        except StopIteration:
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
        idx = DisjointUnionStrategy.backward_map_index(objs)
        yield children[idx].backward_map.map_gp(cast(GriddedPerm, objs[idx]))

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
        res: List[Optional[GriddedPerm]] = []
        for child in children:
            if child.forward_map.is_mappable_gp(obj):
                gp = child.forward_map.map_gp(obj)
                if all(ass.satisfies(gp) for ass in child.predicate_assumptions):
                    res.append(gp)
                    continue
            res.append(None)
        return tuple(res)

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

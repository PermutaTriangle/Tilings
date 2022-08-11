from collections import Counter
from itertools import chain
from typing import Callable, Dict, Iterator, List, Optional, Tuple

import sympy

from comb_spec_searcher import Strategy
from comb_spec_searcher.strategies import Constructor
from comb_spec_searcher.strategies.constructor import Complement, DisjointUnion
from comb_spec_searcher.strategies.strategy import StrategyFactory
from comb_spec_searcher.typing import (
    CombinatorialClassType,
    CombinatorialObjectType,
    Parameters,
    SubObjects,
    SubRecs,
    SubSamplers,
    SubTerms,
    Terms,
)
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Fusion


class DivideByN(DisjointUnion[CombinatorialClassType, CombinatorialObjectType]):
    """
    A constructor that works as disjoint union
    but divides the values by n + shift.
    """

    def __init__(
        self,
        parent: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...],
        shift: int,
        extra_parameters: Optional[Tuple[Dict[str, str], ...]] = None,
    ):
        self.shift = shift
        self.initial_conditions = {
            n: parent.get_terms(n) for n in range(1 - self.shift)
        }
        super().__init__(parent, children, extra_parameters)

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        # TODO: d/dx [ x**shift * lhsfun ] / x**(shift - 1) = A + B + ...
        raise NotImplementedError

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        if n + self.shift <= 0:
            return self.initial_conditions[n]
        terms = super().get_terms(parent_terms, subterms, n)
        return Counter({key: value // (n + self.shift) for key, value in terms.items()})

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[
        Tuple[Parameters, Tuple[List[Optional[CombinatorialObjectType]], ...]]
    ]:
        raise NotImplementedError

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        raise NotImplementedError

    @staticmethod
    def get_eq_symbol() -> str:
        return "?"

    def __str__(self):
        return "divide by n"

    def equiv(
        self, other: Constructor, data: Optional[object] = None
    ) -> Tuple[bool, Optional[object]]:
        raise NotImplementedError


class ReverseDivideByN(Complement[CombinatorialClassType, CombinatorialObjectType]):
    """
    The complement version of DivideByN.
    It works as Complement, but multiplies by n + shift the original left hand side.
    """

    def __init__(
        self,
        parent: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...],
        idx: int,
        shift: int,
        extra_parameters: Optional[Tuple[Dict[str, str], ...]] = None,
    ):
        self.shift = shift
        self.initial_conditions = {
            n: children[idx].get_terms(n) for n in range(1 - self.shift)
        }
        super().__init__(parent, children, idx, extra_parameters)

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        # TODO: rhs_funcs[0] should be a derivative etc, see DivideByN.get_equation.
        raise NotImplementedError

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        if n + self.shift <= 0:
            return self.initial_conditions[n]
        parent_terms_mapped: Terms = Counter()
        for param, value in subterms[0](n).items():
            if value:
                # This is the only change from complement
                N = n + self.shift
                assert N > 0
                parent_terms_mapped[self._parent_param_map(param)] += value * N
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
        return "reverse divide by n"


class UnfusionColumnStrategy(Strategy[Tiling, GriddedPerm]):
    def __init__(
        self,
        ignore_parent: bool = False,
        inferrable: bool = True,
        possibly_empty: bool = True,
        workable: bool = True,
        cols: bool = True,
    ):
        self.cols = cols
        super().__init__(ignore_parent, inferrable, possibly_empty, workable)

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
        return tuple(0 for _ in range(self.width(comb_class)))

    def width(self, comb_class: Tiling) -> int:
        if self.cols:
            return comb_class.dimensions[0]
        return comb_class.dimensions[1]

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        res = []
        for idx in range(self.width(comb_class)):
            if self.cols:
                algo = Fusion(comb_class, col_idx=idx)
            else:
                algo = Fusion(comb_class, row_idx=idx)
            obs = chain(
                *[algo.unfuse_gridded_perm(ob) for ob in comb_class.obstructions]
            )
            reqs = [
                [gp for req_gp in req_list for gp in algo.unfuse_gridded_perm(req_gp)]
                for req_list in comb_class.requirements
            ]
            ass = [
                ass.__class__(
                    [
                        gp
                        for ass_gp in ass.gps
                        for gp in algo.unfuse_gridded_perm(ass_gp)
                    ]
                )
                for ass in comb_class.assumptions
            ]
            res.append(Tiling(obs, reqs, ass))
        return tuple(res)

    def formal_step(self) -> str:
        if self.cols:
            return "unfuse columns strategy"
        return "unfuse rows strategy"

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
            len(children),
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
            len(children),
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
        res = []
        for idx in range(self.width(comb_class)):
            if self.cols:
                algo = Fusion(comb_class, col_idx=idx)
            else:
                algo = Fusion(comb_class, row_idx=idx)
            params: Dict[str, str] = {}
            for ass in comb_class.tracking_assumptions:
                mapped_ass = ass.__class__(
                    [
                        children[idx].forward_map.map_gp(gp)
                        for ass_gp in ass.gps
                        for gp in algo.unfuse_gridded_perm(ass_gp)
                    ]
                )
                params[comb_class.get_assumption_parameter(ass)] = children[
                    idx
                ].get_assumption_parameter(mapped_ass)
            res.append(params)
        return tuple(res)

    @classmethod
    def from_dict(cls, d: dict) -> "UnfusionColumnStrategy":
        return cls(**d)


class UnfusionRowStrategy(UnfusionColumnStrategy):
    def __init__(
        self,
        ignore_parent: bool = False,
        inferrable: bool = True,
        possibly_empty: bool = True,
        workable: bool = True,
        cols: bool = False,
    ):
        super().__init__(ignore_parent, inferrable, possibly_empty, workable, cols)


class UnfusionRowColumnFactory(StrategyFactory[Tiling]):
    def __init__(self, max_width: int = 4, max_height: int = 4) -> None:
        self.max_height = max_height
        self.max_width = max_width
        super().__init__()

    def __call__(self, comb_class: Tiling) -> Iterator[UnfusionColumnStrategy]:
        width, height = comb_class.dimensions
        if width <= self.max_width:
            yield UnfusionColumnStrategy()
        if height <= self.max_height:
            yield UnfusionRowStrategy()

    def __str__(self) -> str:
        return "unfusion strategy"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d: dict) -> "UnfusionRowColumnFactory":
        return cls()

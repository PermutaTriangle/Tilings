import logging
from typing import Dict, Optional, Tuple

from logzero import logger

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
)
from comb_spec_searcher.strategies.constructor import CartesianProduct, DisjointUnion
from comb_spec_searcher.strategies.rule import Rule, VerificationRule
from comb_spec_searcher.strategies.strategy import VerificationStrategy
from comb_spec_searcher.typing import CSSstrategy
from permuta import Av, Basis, Perm
from tilings import GriddedPerm, Tiling

__all__ = ["shift_from_spec"]


class TmpLoggingLevel:
    def __init__(self, level):
        self.tmp_level = level
        self.curent_level = logger.level

    def __enter__(self):
        logger.setLevel(self.tmp_level)

    def __exit__(self, exc_type, exc_value, traceback):
        logger.setLevel(self.curent_level)


class NoBasisVerification(VerificationStrategy[Tiling, GriddedPerm]):
    def __init__(self, basis: Tuple[Perm, ...]) -> None:
        self.basis = Basis(*basis)
        super().__init__()

    def formal_step(self) -> str:
        return f"No cell is {Av(self.basis)}"

    def verified(self, comb_class: Tiling) -> bool:
        cell_bases = (Basis(*obs) for obs, _ in comb_class.cell_basis().values())
        return self.basis not in cell_bases

    @classmethod
    def from_dict(cls, d: dict) -> CSSstrategy:
        raise NotImplementedError

    def to_jsonable(self) -> dict:
        raise NotImplementedError


def expanded_spec(
    tiling: Tiling, strat: VerificationStrategy, basis: Tuple[Perm, ...]
) -> CombinatorialSpecification:
    """
    Return a spec where any tiling that does not have the basis in one cell is
    verified.
    """
    pack = strat.pack(tiling).add_verification(
        NoBasisVerification(basis), apply_first=True
    )
    with TmpLoggingLevel(logging.WARN):
        css = CombinatorialSpecificationSearcher(tiling, pack)
        spec = css.auto_search()
    return spec


def shift_from_spec(
    tiling: Tiling, strat: VerificationStrategy, basis: Tuple[Perm, ...]
) -> Optional[int]:
    assert basis
    traverse_cache: Dict[Tiling, Optional[int]] = {}
    spec = expanded_spec(tiling, strat, basis)

    def traverse(t: Tiling) -> Optional[int]:
        rule = spec.rules_dict[t]
        if t in traverse_cache:
            return traverse_cache[t]
        res: Optional[int]
        if isinstance(rule.strategy, NoBasisVerification):
            res = None
        elif t.dimensions == (1, 1):
            res = 0
        elif isinstance(rule, VerificationRule):
            res = shift_from_spec(tiling, rule.strategy, basis)
        elif isinstance(rule, Rule) and isinstance(rule.constructor, DisjointUnion):
            children_reliance = [traverse(c) for c in rule.children]
            res = min([r for r in children_reliance if r is not None], default=None)
        elif isinstance(rule, Rule) and isinstance(rule.constructor, CartesianProduct):
            min_points = [len(next(c.minimal_gridded_perms())) for c in rule.children]
            point_sum = sum(min_points)
            shifts = [point_sum - mpoint for mpoint in min_points]
            children_reliance = [traverse(c) for c in rule.children]
            res = min(
                [r + s for r, s in zip(children_reliance, shifts) if r is not None],
                default=None,
            )
        else:
            raise NotImplementedError(rule)
        traverse_cache[t] = res
        return res

    return traverse(tiling)

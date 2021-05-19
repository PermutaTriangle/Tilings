import logging
from typing import Dict, FrozenSet, Optional

from logzero import logger

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
)
from comb_spec_searcher.strategies.constructor import CartesianProduct, DisjointUnion
from comb_spec_searcher.strategies.rule import Rule, VerificationRule
from comb_spec_searcher.strategies.strategy import VerificationStrategy
from comb_spec_searcher.typing import CSSstrategy
from permuta import Perm
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
    def __init__(self, symmetries: FrozenSet[FrozenSet[Perm]]) -> None:
        self.symmetries = symmetries
        super().__init__()

    def formal_step(self) -> str:
        return "No cell is the basis"

    def verified(self, comb_class: Tiling) -> bool:
        cell_bases = (frozenset(obs) for obs, _ in comb_class.cell_basis().values())
        return not bool(self.symmetries.intersection(cell_bases))

    @classmethod
    def from_dict(cls, d: dict) -> CSSstrategy:
        raise NotImplementedError

    def to_jsonable(self) -> dict:
        raise NotImplementedError


def expanded_spec(
    tiling: Tiling, strat: VerificationStrategy, symmetries: FrozenSet[FrozenSet[Perm]]
) -> CombinatorialSpecification:
    """
    Return a spec where any tiling that does not have the basis in one cell is
    verified.
    """
    print(symmetries)
    print(tiling)
    print(repr(strat))
    print(strat.__dict__)
    pack = strat.pack(tiling).add_verification(
        NoBasisVerification(symmetries), apply_first=True
    )
    with TmpLoggingLevel(logging.WARN):
        css = CombinatorialSpecificationSearcher(tiling, pack)
        spec = css.auto_search()
    return spec


def shift_from_spec(
    tiling: Tiling,
    strat: VerificationStrategy,
    symmetries: FrozenSet[FrozenSet[Perm]],
) -> Optional[int]:
    assert all(symmetries)
    traverse_cache: Dict[Tiling, Optional[int]] = {}
    spec = expanded_spec(tiling, strat, symmetries)

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
            res = shift_from_spec(tiling, rule.strategy, symmetries)
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

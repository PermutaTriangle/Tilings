import logging
from typing import Dict, FrozenSet, Optional

from logzero import logger

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
)
from comb_spec_searcher.strategies.constructor import DisjointUnion
from comb_spec_searcher.strategies.rule import Rule, VerificationRule
from comb_spec_searcher.strategies.strategy import VerificationStrategy
from comb_spec_searcher.strategies.strategy_pack import StrategyPack
from comb_spec_searcher.typing import CSSstrategy
from permuta import Av, Perm
from tilings import GriddedPerm, Tiling
from tilings.strategies.detect_components import CountComponent
from tilings.strategies.factor import FactorStrategy

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
        cls = Av(min(self.symmetries))
        if len(self.symmetries) == 1:
            return f"No cell is {cls}"
        return f"No cell is a symmetry of {cls}"

    def verified(self, comb_class: Tiling) -> bool:
        cell_bases = (frozenset(obs) for obs, _ in comb_class.cell_basis().values())
        return not bool(self.symmetries.intersection(cell_bases))

    @classmethod
    def from_dict(cls, d: dict) -> CSSstrategy:
        raise NotImplementedError

    def to_jsonable(self) -> dict:
        raise NotImplementedError


def expanded_spec(
    tiling: Tiling, pack: StrategyPack, symmetries: FrozenSet[FrozenSet[Perm]]
) -> CombinatorialSpecification:
    """
    Return a spec where any tiling that does not have the basis in one cell is
    verified.

    A locally factorable tiling can always result in a spec where the
    verified leaves are one by one if we remove the local verification
    and monotone tree verification strategies and instead use the
    interleaving factors. As we only care about the shift, we can
    tailor our packs to find this.
    """
    # pylint: disable=import-outside-toplevel
    from tilings.strategies.verification import (
        LocalVerificationStrategy,
        MonotoneTreeVerificationStrategy,
    )
    from tilings.tilescope import TileScopePack

    pack = TileScopePack(
        initial_strats=pack.initial_strats,
        inferral_strats=pack.inferral_strats,
        expansion_strats=pack.expansion_strats,
        ver_strats=pack.ver_strats,
        name=pack.name,
    )
    pack = pack.remove_strategy(MonotoneTreeVerificationStrategy()).make_interleaving(
        tracked=False, unions=False
    )
    pack = pack.remove_strategy(LocalVerificationStrategy())
    pack = pack.add_verification(NoBasisVerification(symmetries), apply_first=True)
    with TmpLoggingLevel(logging.WARN):
        css = CombinatorialSpecificationSearcher(tiling, pack)
        spec = css.auto_search()
    return spec


def shift_from_spec(
    tiling: Tiling,
    pack: StrategyPack,
    symmetries: FrozenSet[FrozenSet[Perm]],
) -> Optional[int]:
    assert all(symmetries)
    traverse_cache: Dict[Tiling, Optional[int]] = {}
    spec = expanded_spec(tiling, pack, symmetries)

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
            raise ValueError(
                "this should be unreachable, looks like JP, HU "
                "and CB misunderstood the code."
            )
        elif isinstance(rule, Rule) and isinstance(rule.strategy, FactorStrategy):
            min_points = [len(next(c.minimal_gridded_perms())) for c in rule.children]
            point_sum = sum(min_points)
            shifts = [point_sum - mpoint for mpoint in min_points]
            children_reliance = [traverse(c) for c in rule.children]
            res = min(
                (r + s for r, s in zip(children_reliance, shifts) if r is not None),
                default=None,
            )
        elif isinstance(rule, Rule) and isinstance(
            rule.constructor, (DisjointUnion, CountComponent)
        ):
            children_reliance = [traverse(c) for c in rule.children]
            res = min((r for r in children_reliance if r is not None), default=None)

        else:
            raise NotImplementedError(rule)
        traverse_cache[t] = res
        return res

    return traverse(tiling)

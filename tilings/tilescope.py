from collections import defaultdict
from typing import Iterable, Optional, Tuple, Union

import requests
from logzero import logger

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
)
from comb_spec_searcher.rule_db import RuleDB
from comb_spec_searcher.strategies import StrategyFactory
from comb_spec_searcher.typing import CombinatorialClassType, CSSstrategy
from permuta import Basis, Perm
from tilings import GriddedPerm, Tiling
from tilings.strategy_pack import TileScopePack

__all__ = ("TileScope", "TileScopePack", "LimitedAssumptionTileScope", "GuidedSearcher")


class TileScope(CombinatorialSpecificationSearcher):
    """
    An instance of TileScope is used to build up knowledge about tilings with
    respect to the given basis.
    """

    def __init__(
        self,
        start_class: Union[str, Iterable[Perm], Tiling],
        strategy_pack: TileScopePack,
        ruledb: Optional[Union[str, RuleDB]] = None,
        expand_verified: bool = False,
        debug: bool = False,
    ) -> None:

        """Initialise TileScope."""
        if isinstance(start_class, str):
            basis = Basis.from_string(start_class)
        elif isinstance(start_class, Tiling):
            if start_class.dimensions == (1, 1):
                basis = Basis(*[o.patt for o in start_class.obstructions])
            start_tiling = start_class
        else:
            try:
                basis = Basis(*start_class)
            except TypeError as e:
                raise ValueError(
                    "start class must be a string, an iterable of Perm or a tiling"
                ) from e

        if not isinstance(start_class, Tiling):
            start_tiling = Tiling(
                obstructions=[GriddedPerm.single_cell(patt, (0, 0)) for patt in basis]
            )

        if start_tiling.dimensions == (1, 1):
            logger.debug("Fixing basis in basis aware verification strategies.")
            strategy_pack = strategy_pack.add_basis(basis)
        strategy_pack = strategy_pack.setup_subclass_verification(start_tiling)

        super().__init__(start_tiling, strategy_pack, ruledb, expand_verified, debug)


class LimitedAssumptionTileScope(TileScope):
    """
    A subclass of Tilescope that allows a limit to be set on the maximum number of
    assumptions that appear on any tiling in the universe.
    """

    def __init__(
        self,
        start_class: Union[str, Iterable[Perm], Tiling],
        strategy_pack: TileScopePack,
        max_assumptions: int,
        **kwargs
    ) -> None:
        super().__init__(start_class, strategy_pack, **kwargs)
        self.max_assumptions = max_assumptions

    def _expand(
        self,
        comb_class: CombinatorialClassType,
        label: int,
        strategies: Tuple[CSSstrategy, ...],
        inferral: bool,
    ) -> None:
        """
        Will expand the combinatorial class with given label using the given
        strategies, but only add rules whose children all satisfy the max_assumptions
        requirement.
        """
        if inferral:
            self._inferral_expand(comb_class, label, strategies)
        else:
            for strategy_generator in strategies:
                for start_label, end_labels, rule in self._expand_class_with_strategy(
                    comb_class, strategy_generator, label
                ):
                    if all(
                        len(child.assumptions) <= self.max_assumptions
                        for child in rule.children
                    ):
                        self._add_rule(start_label, end_labels, rule)


class GuidedSearcher(TileScope):
    def __init__(
        self,
        tilings: Iterable[Tiling],
        basis: Tiling,
        pack: TileScopePack,
        *args,
        **kwargs
    ):
        self.tilings = frozenset(t.remove_assumptions() for t in tilings)
        super().__init__(basis, pack, *args, **kwargs)
        for t in self.tilings:
            class_label = self.classdb.get_label(t)
            is_empty = self.classdb.is_empty(t, class_label)
            if not is_empty:
                self.classqueue.add(class_label)

    def _expand(
        self,
        comb_class: Tiling,
        label: int,
        strategies: Tuple[CSSstrategy, ...],
        inferral: bool,
    ) -> None:
        if comb_class.remove_assumptions() not in self.tilings:
            return
        return super()._expand(comb_class, label, strategies, inferral)

    @classmethod
    def from_spec(
        cls, specification: CombinatorialSpecification, pack: TileScopePack
    ) -> "GuidedSearcher":
        tilings = specification.comb_classes()
        root = specification.root
        return cls(tilings, root, pack)

    @classmethod
    def from_uri(cls, URI: str) -> "GuidedSearcher":
        response = requests.get(URI)
        spec = CombinatorialSpecification.from_dict(response.json()["specification"])
        pack = TileScopePack.from_dict(response.json()["pack"]).make_tracked()
        return cls.from_spec(spec, pack)

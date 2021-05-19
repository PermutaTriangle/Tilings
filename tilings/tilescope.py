from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import requests
from logzero import logger

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
)
from comb_spec_searcher.rule_db.abstract import RuleDBAbstract
from comb_spec_searcher.strategies import AbstractStrategy
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.typing import CombinatorialClassType, CSSstrategy
from comb_spec_searcher.utils import cssmethodtimer
from permuta import Basis, Perm
from tilings import GriddedPerm, Tiling
from tilings.strategies import AddAssumptionFactory, RearrangeAssumptionFactory
from tilings.strategies.assumption_insertion import AddAssumptionsStrategy
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
        ruledb: Optional[RuleDBAbstract] = None,
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

        super().__init__(
            start_class=start_tiling,
            strategy_pack=strategy_pack,
            ruledb=ruledb,
            expand_verified=expand_verified,
            debug=debug,
        )


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
                        self.add_rule(start_label, end_labels, rule)


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


class TrackedSearcher(LimitedAssumptionTileScope):
    """
    A TileScope that keeps track of the strategies that apply to Tilings without
    assumptions and applies these to any tiling with assumptions.
    """

    def __init__(self, *args, **kwargs):
        self.assumptionless_strategies: Dict[int, List[AbstractStrategy]] = dict()
        self.expanded = set()
        super().__init__(*args, **kwargs)

    # @cssmethodtimer("add rule") # called recursively so shouldn't time it.
    def add_rule(
        self, start_label: int, end_labels: Tuple[int, ...], rule: AbstractRule
    ) -> None:
        if not rule.comb_class.assumptions:
            if start_label not in self.assumptionless_strategies:
                self.assumptionless_strategies[start_label] = [
                    rule.strategy,
                ]
            else:
                self.assumptionless_strategies[start_label].append(rule.strategy)
        for comb_class, child_label in zip(rule.children, end_labels):
            if self.symmetries and child_label not in self.symmetry_expanded:
                self._symmetry_expand(
                    comb_class, child_label
                )  # TODO: mark symmetries as empty where appropriate
            if comb_class.assumptions:
                if self.expand_sooner(comb_class, child_label):
                    # print("SKIPPING")
                    # print(comb_class)
                    # input()
                    continue
                # print("ADDING")
                # print(comb_class)
                # input()
            if rule.workable:
                # assert child_label >= self.classdb.get_label(
                #     comb_class.remove_assumptions()
                # )
                self.classqueue.add(child_label)
            if not rule.inferrable:
                self.classqueue.set_not_inferrable(child_label)
            if not rule.possibly_empty:
                self.classdb.set_empty(child_label, empty=False)
            self.try_verify(comb_class, child_label)
        if rule.ignore_parent:
            self.classqueue.set_stop_yielding(start_label)
        self.ruledb.add(start_label, end_labels, rule)

    def expand_sooner(self, comb_class: Tiling, label: int) -> bool:
        """
        Return True if all strategies have been tried, i.e., the underlying tiling
        has been fully expanded.
        """
        if label in self.expanded:
            return True
        self.expanded.add(label)
        underlying_label = self.classdb.get_label(comb_class.remove_assumptions())
        if underlying_label in self.assumptionless_strategies:
            for strategy in [
                AddAssumptionFactory(),
                RearrangeAssumptionFactory(),
            ] + self.assumptionless_strategies[underlying_label]:
                if isinstance(strategy, AddAssumptionsStrategy):
                    continue
                for start_label, end_labels, rule in self._expand_class_with_strategy(
                    comb_class, strategy, label
                ):
                    if all(
                        len(child.assumptions) <= self.max_assumptions
                        for child in rule.children
                    ):
                        self.add_rule(start_label, end_labels, rule)
            return underlying_label in self.classqueue.ignore
        return False

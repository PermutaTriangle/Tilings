from collections import defaultdict
from itertools import chain
from typing import DefaultDict, Iterable, Iterator, List, Optional, Set, Tuple, Union

import requests
from logzero import logger

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
)
from comb_spec_searcher.rule_db import RuleDBForgetStrategy
from comb_spec_searcher.rule_db.abstract import RuleDBAbstract
from comb_spec_searcher.strategies import AbstractStrategy
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.typing import CombinatorialClassType, CSSstrategy
from permuta import Basis, Perm
from tilings import GriddedPerm, Tiling
from tilings.strategies import AddAssumptionFactory, RearrangeAssumptionFactory
from tilings.strategies.assumption_insertion import AddAssumptionsStrategy
from tilings.strategies.rearrange_assumption import RearrangeAssumptionStrategy
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
    A TileScope that only adds underlying tilings to the queue, but expands all
    assumption tilings with the strategies that apply to the underlying tiling
    immediately.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tilings_from_underlying: DefaultDict[int, Set[int]] = defaultdict(set)
        self.tracking_strategies = [
            AddAssumptionFactory(),
            RearrangeAssumptionFactory(),
        ]
        self.tracked_expanded: Set[int] = set()
        self.retroactively_expanded: Set[int] = set()
        # TODO: keep self._strats on the ruledb, and avoid storing strats twice.
        self._strats: DefaultDict[int, List[AbstractStrategy]] = defaultdict(list)

    def store_strategy(self, label: int, strategy: AbstractStrategy) -> None:
        self._strats[label].append(strategy)

    def get_old_strategies(self, label: int) -> Tuple[CSSstrategy, ...]:
        return tuple(self._strats[label])

    def add_rule(
        self, start_label: int, end_labels: Tuple[int, ...], rule: AbstractRule
    ) -> None:
        """
        Add the rule to the searcher

        - try to verify children combinatorial classes
        - set workability of combinatorial classes
        - symmetry expand combinatorial classes
        - add underlying class to classqueue, and do the expansion for any assumption
        tilings with same underlying tiling
        """
        for comb_class, child_label in zip(rule.children, end_labels):
            underlying_label = (
                self.classdb.get_label(comb_class.remove_assumptions())
                if comb_class.assumptions
                else child_label
            )
            if underlying_label != child_label:
                self.tilings_from_underlying[underlying_label].add(child_label)
            if self.symmetries and child_label not in self.symmetry_expanded:
                self._symmetry_expand(comb_class, child_label)
            if rule.workable:
                # add the underlying label to the queue
                self.classqueue.add(underlying_label)
            if (
                underlying_label != child_label
                and child_label not in self.retroactively_expanded
            ):
                self.retroactively_expanded.add(child_label)
                # apply all rules in ruledb to child_label
                old_strategies = self.get_old_strategies(underlying_label)
                self._expand(comb_class, child_label, old_strategies, False)
            # apply tracking strategies
            if comb_class.assumptions and child_label not in self.tracked_expanded:
                self.tracked_expanded.add(child_label)
                self._expand(comb_class, child_label, self.tracking_strategies, False)
            if not rule.inferrable:
                self.classqueue.set_not_inferrable(underlying_label)
            if not rule.possibly_empty:
                # this is shortcutting some empty checks by ruledb,
                # so should be done to both underlying and child labels
                self.classdb.set_empty(child_label, empty=False)
                if underlying_label != child_label:
                    self.classdb.set_empty(underlying_label, empty=False)
            underlying_tiling = (
                comb_class.remove_assumptions()
                if comb_class.assumptions
                else comb_class
            )
            # calls add rule recursively, so will add verification
            # rules for all with underlying tiling
            self.try_verify(underlying_tiling, underlying_label)
        if rule.ignore_parent:
            self.classqueue.set_stop_yielding(start_label)

        # update all with same underlying label
        self.ruledb.add(start_label, end_labels, rule)
        if not isinstance(
            rule.strategy,
            (RearrangeAssumptionStrategy, AddAssumptionsStrategy),
        ):
            self.store_strategy(start_label, rule.strategy)
            for label in list(self.tilings_from_underlying[start_label]):
                assumption_tiling = self.classdb.get_class(label)
                self._expand(assumption_tiling, label, (rule.strategy,), False)


class ForgetTrackedSearcher(TrackedSearcher):
    def __init__(
        self,
        start_class: Union[str, Iterable[Perm], Tiling],
        strategy_pack: TileScopePack,
        **kwargs
    ):
        self.strategies: List[CSSstrategy] = list(
            chain(
                strategy_pack.ver_strats,
                strategy_pack.initial_strats,
                strategy_pack.inferral_strats,
                *strategy_pack.expansion_strats,
            )
        )
        self._strat_indices: DefaultDict[int, int] = defaultdict(int)
        kwargs["ruledb"] = kwargs.get("ruledb", RuleDBForgetStrategy())
        super().__init__(start_class, strategy_pack, **kwargs)

    def store_strategy(self, label: int, strategy: AbstractStrategy) -> None:
        """We do nothing as instead we track in the _expand method."""

    def get_old_strategies(self, label: int) -> Tuple[CSSstrategy, ...]:
        return tuple(
            self.strategies[idx]
            for idx, bit in enumerate(bin(self._strat_indices[label])[-1:1:-1])
            if bit == "1"
        )

    def _expand_class_with_strategy(
        self,
        comb_class: CombinatorialClassType,
        strategy_generator: CSSstrategy,
        label: Optional[int] = None,
        initial: bool = False,
    ) -> Iterator[Tuple[int, Tuple[int, ...], AbstractRule]]:
        if not isinstance(
            strategy_generator, (AddAssumptionFactory, RearrangeAssumptionFactory)
        ):
            try:
                idx = self.strategies.index(strategy_generator)
                assert isinstance(label, int)
                self._strat_indices[label] |= 1 << idx

            except ValueError:
                pass
        yield from super()._expand_class_with_strategy(
            comb_class, strategy_generator, label, initial
        )

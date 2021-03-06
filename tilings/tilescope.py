from collections import defaultdict
from typing import Iterable, Optional, Tuple, Union

import requests
from logzero import logger

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
)
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
        logger_kwargs: Optional[dict] = None,
        **kwargs
    ) -> None:

        """Initialise TileScope."""
        if isinstance(start_class, str):
            basis = Basis.from_string(start_class)
        elif isinstance(start_class, Tiling):
            if start_class.dimensions == (1, 1):
                basis = Basis(*[o.patt for o in start_class.obstructions])
            start_tiling = start_class
        # elif isinstance(start_class, collections.abc.Iterable):
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
            procname = kwargs.get("logger_kwargs", {"processname": "runner"})
            logger.debug("Fixing basis in OneByOneVerificationStrategy", extra=procname)
            strategy_pack = strategy_pack.fix_one_by_one(basis)
        strategy_pack = strategy_pack.setup_subclass_verification(start_tiling)

        super().__init__(
            start_tiling, strategy_pack, logger_kwargs=logger_kwargs, **kwargs
        )

    @staticmethod
    def _strat_dict_to_jsonable(dict_):
        keys = []
        values = []
        for k, v in dict_.items():
            if k == "is empty":
                keys.append(k)
            else:
                keys.append(k.to_jsonable())
            values.append(v)
        return {"keys": keys, "values": values}

    @staticmethod
    def _strat_dict_from_jsonable(dict_):
        keys = dict_["keys"]
        values = dict_["values"]
        d = {}
        for k, v in zip(keys, values):
            if k == "is empty":
                d[k] = v
            else:
                d[StrategyFactory.from_dict(k)] = v
            values.append(v)
        return defaultdict(int, d)


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
        logger_kwargs: Optional[dict] = None,
        **kwargs
    ) -> None:
        super().__init__(start_class, strategy_pack, logger_kwargs, **kwargs)
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
        self.tilings = frozenset(tilings)
        super().__init__(basis, pack, *args, **kwargs)
        for t in self.tilings:
            class_label = self.classdb.get_label(t)
            is_empty = self.classdb.is_empty(t, class_label)
            if not is_empty:
                self._add_to_queue(class_label)

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

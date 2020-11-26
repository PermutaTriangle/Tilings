from collections import defaultdict
from typing import Iterable, Optional, Union

from logzero import logger

from comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.strategies import StrategyFactory
from permuta import Basis, Perm
from tilings import GriddedPerm, Tiling
from tilings.strategy_pack import TileScopePack

__all__ = ("TileScope", "TileScopePack")


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

import collections
from collections import defaultdict
from typing import Iterable, Optional, Union

from logzero import logger

from comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.strategies import StrategyFactory
from comb_spec_searcher.utils import cssmethodtimer
from permuta import Perm
from permuta.descriptors import Basis
from tilings import GriddedPerm, Tiling
from tilings.algorithms import GriddedPermReduction
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
            basis = Basis(
                [Perm.to_standard([int(c) for c in p]) for p in start_class.split("_")]
            )
        elif isinstance(start_class, Tiling):
            start_tiling = start_class
            if start_class.dimensions == (1, 1):
                basis = Basis([o.patt for o in start_class.obstructions])
        elif isinstance(start_class, collections.abc.Iterable):
            basis = Basis(start_class)
            assert all(
                isinstance(p, Perm) for p in basis
            ), "Basis must contains Perm only"
        else:
            raise ValueError(
                "start class must be a string, an iterable of Perm or a tiling"
            )

        if not isinstance(start_class, Tiling):
            start_tiling = Tiling(
                obstructions=[GriddedPerm.single_cell(patt, (0, 0)) for patt in basis]
            )

        if start_tiling.dimensions == (1, 1):
            procname = kwargs.get("logger_kwargs", {"processname": "runner"})
            logger.debug("Fixing basis in OneByOneVerificationStrategy", extra=procname)
            strategy_pack = strategy_pack.fix_one_by_one(basis)

        super().__init__(
            start_tiling, strategy_pack, logger_kwargs=logger_kwargs, **kwargs,
        )

    @cssmethodtimer("tilescope status")
    def status(self, elaborate: bool) -> str:
        """
        Return a string of the current status of the TileScope.
        Calls the status function of the parent CombSpecSearcher.

        "elaborate" status updates are those that provide information that
        may be slow to compute
        """
        status = super().status(elaborate)
        total = sum(self.func_times.values())

        status += "Tilescope Status:\n"
        for explanation in GriddedPermReduction.func_calls:
            count = GriddedPermReduction.func_calls[explanation]
            time_spent = GriddedPermReduction.func_times[explanation]
            percentage = int((time_spent * 100) / total)
            status += (
                f"\tApplied {explanation} {count} times."
                f" Time spent is {round(time_spent, 2)} seconds (~{percentage}%).\n"
            )
        return status

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

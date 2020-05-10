from collections import defaultdict
from typing import List, Optional, Union

from logzero import logger

from comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.strategies import StrategyGenerator
from permuta import Perm
from permuta.descriptors import Basis
from tilings import GriddedPerm, Tiling
from tilings.strategy_pack import TileScopePack


class TileScope(CombinatorialSpecificationSearcher):
    """
    An instance of TileScope is used to build up knowledge about tilings with
    respect to the given basis.
    """

    def __init__(
        self,
        start_class: Union[str, List[Perm], Tiling],
        strategy_pack: TileScopePack,
        logger_kwargs: Optional[dict] = None,
        **kwargs
    ) -> None:
        """Initialise TileScope."""
        if isinstance(start_class, str):
            basis = Basis(
                [Perm.to_standard([int(c) for c in p]) for p in start_class.split("_")]
            )
        elif isinstance(start_class, list):
            basis = Basis(start_class)
        elif isinstance(start_class, Tiling):
            start_tiling = start_class
            if start_class.dimensions == (1, 1):
                basis = Basis([o.patt for o in start_class.obstructions])

        if not isinstance(start_class, Tiling):
            start_tiling = Tiling(
                obstructions=[GriddedPerm.single_cell(patt, (0, 0)) for patt in basis]
            )

        if start_tiling.dimensions == (1, 1):
            logger.info("Fixing basis in OneByOneVerificationStrategy")
            strategy_pack = strategy_pack.fix_one_by_one(basis)

        function_kwargs = {"basis": basis}
        super().__init__(
            start_tiling,
            strategy_pack,
            function_kwargs=function_kwargs,
            logger_kwargs=logger_kwargs,
            **kwargs,
        )

    def build_zdict(self) -> List[str]:
        """
        Return a list of common strings that may appear in the JSON of the
        strategies to be compressed.
        """
        strings: List[str] = []
        strings.append("[0, 0]")

        return strings + super().build_zdict()

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
                d[StrategyGenerator.from_dict(k)] = v
            values.append(v)
        return defaultdict(int, d)

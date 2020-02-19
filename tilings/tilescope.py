from typing import Callable, List, Optional, Union

from comb_spec_searcher import CombinatorialSpecificationSearcher
from permuta import Perm
from permuta.descriptors import Basis
from tilings import Obstruction, Tiling
from tilings.strategy_pack import TileScopePack


class TileScope(CombinatorialSpecificationSearcher):
    """
    An instance of TileScope is used to build up knowledge about tilings with
    respect to the given basis.
    """
    def __init__(self,
                 start_class: Union[str, List[Perm], Tiling],
                 strategy_pack: TileScopePack,
                 forward_equivalence: bool = False,
                 logger_kwargs: Optional[dict] = None,
                 **kwargs) -> None:
        """Initialise TileScope."""
        if isinstance(start_class, str):
            basis = Basis([Perm.to_standard([int(c) for c in p])
                           for p in start_class.split('_')])
        elif isinstance(start_class, list):
            basis = Basis(start_class)
        elif isinstance(start_class, Tiling):
            start_tiling = start_class
            if start_class.dimensions == (1, 1):
                basis = Basis([o.patt for o in start_class.obstructions])
            else:
                basis = []
        if not isinstance(start_class, Tiling):
            start_tiling = Tiling(
                obstructions=[Obstruction.single_cell(patt, (0, 0))
                              for patt in basis])
        function_kwargs = {"basis": basis}
        super().__init__(
            start_tiling,
            strategy_pack,
            forward_equivalence=forward_equivalence,
            function_kwargs=function_kwargs,
            logger_kwargs=logger_kwargs,
            **kwargs)

    def update_status(self, strategy: Callable, time_taken: int):
        """Update that it took 'time_taken' to expand a combinatorial class
        with strategy"""
        # pylint: disable=comparison-with-callable
        if strategy == self.is_empty:
            self.strategy_times['is empty'] += time_taken
            self.strategy_expansions['is empty'] += 1
        else:
            self.strategy_times[strategy] += time_taken
            self.strategy_expansions[strategy] += 1

from base64 import b64decode, b64encode
from collections import defaultdict
from typing import Callable, List, Optional, Union

from comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.class_queue import ClassQueue
from comb_spec_searcher.equiv_db import EquivalenceDB
from comb_spec_searcher.rule_db import RuleDB
from permuta import Perm
from permuta.descriptors import Basis
from tilings import Obstruction, Tiling
from tilings.strategies.abstract_strategy import Strategy
from tilings.strategy_pack import TileScopePack


class TileScope(CombinatorialSpecificationSearcher):
    """
    An instance of TileScope is used to build up knowledge about tilings with
    respect to the given basis.
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self,
                 start_class: Union[str, List[Perm], Tiling],
                 strategy_pack: TileScopePack,
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

    @staticmethod
    def _strat_dict_to_jsonable(dict_):
        keys = []
        values = []
        for k, v in dict_.items():
            if k == 'is empty':
                keys.append(k)
            else:
                keys.append(k.to_jsonable())
            values.append(v)
        return {"keys": keys, "values": values}

    @staticmethod
    def _strat_dict_from_jsonable(dict_):
        keys = dict_['keys']
        values = dict_['values']
        d = {}
        for k, v in zip(keys, values):
            if k == 'is empty':
                d[k] = v
            else:
                d[Strategy.from_dict(k)] = v
            values.append(v)
        return defaultdict(int, d)

    def to_dict(self) -> dict:
        return {
            'start_class': b64encode(self.start_class.compress()).decode(),
            'debug': self.debug,
            'kwargs': self.kwargs,
            'logger_kwargs': self.logger_kwargs,
            'strategy_pack': self.strategy_pack.to_jsonable(),
            'classdb': self.classdb.to_dict(),
            'equivdb': self.equivdb.to_dict(),
            'classqueue': self.classqueue.to_dict(),
            'ruledb': self.ruledb.to_dict(),
            'start_label': self.start_label,
            '_has_proof_tree': self._has_proof_tree,
            'strategy_times':
                self._strat_dict_to_jsonable(self.strategy_times),
            'strategy_expansions':
                self._strat_dict_to_jsonable(self.strategy_expansions),
            'symmetry_time': self.symmetry_time,
            'tree_search_time': self.tree_search_time,
            'prep_for_tree_search_time': self.prep_for_tree_search_time,
            'queue_time': self.queue_time,
            '_time_taken': self._time_taken,
        }

    # pylint: disable=arguments-differ
    @classmethod
    def from_dict(cls, dict_, combinatorial_class=Tiling):
        # pylint: disable=protected-access
        strategy_pack = TileScopePack.from_dict(dict_['strategy_pack'])
        init_kwargs = {
            'debug': dict_['debug'],
            'logger_kwargs': dict_['logger_kwargs'],
        }
        b = b64decode(dict_['start_class'].encode())
        c = Tiling.decompress(b)
        css = cls(c, strategy_pack, **init_kwargs)
        css.classdb = ClassDB.from_dict(dict_['classdb'], combinatorial_class)
        css.equivdb = EquivalenceDB.from_dict(dict_['equivdb'])
        css.classqueue = ClassQueue.from_dict(dict_['classqueue'])
        css.ruledb = RuleDB.from_dict(dict_['ruledb'])
        css.start_label = dict_['start_label']
        css._has_proof_tree = dict_['_has_proof_tree']
        css.strategy_times = cls._strat_dict_from_jsonable(
            dict_['strategy_times'])
        css.strategy_expansions = cls._strat_dict_from_jsonable(
            dict_['strategy_expansions'])
        css.symmetry_time = dict_['symmetry_time']
        css.tree_search_time = dict_['tree_search_time']
        css.prep_for_tree_search_time = dict_['prep_for_tree_search_time']
        css.queue_time = dict_['queue_time']
        css._time_taken = dict_['_time_taken']
        return css

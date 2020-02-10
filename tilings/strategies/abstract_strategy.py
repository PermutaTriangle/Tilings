import abc
from importlib import import_module
from typing import Iterator, Optional, Union

from comb_spec_searcher import Rule
from tilings import Tiling

STRATEGY_OUTPUT = Union[Optional[Rule], Iterator[Rule]]


class Strategy(abc.ABC):
    @abc.abstractmethod
    def __call__(self, tiling: Tiling) -> STRATEGY_OUTPUT:
        """Returns the results of the strategy on a tiling."""

    @abc.abstractmethod
    def __str__(self) -> str:
        """Return the name of the strategy."""

    @abc.abstractmethod
    def to_jsonable(self) -> dict:
        """Return a dictionary form of the strategy."""

    @abc.abstractclassmethod
    def from_dict(cls, d: dict) -> 'Strategy':
        """Return the strategy from the json representation."""
        module = import_module(d['class_module'])
        StrategyClass = getattr(module, d['strategy_class'])
        assert isinstance(StrategyClass, Strategy), 'Not a valid strategy'
        return StrategyClass.from_dict(d)

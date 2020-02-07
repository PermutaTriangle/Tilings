import abc
from importlib import import_module

from tilings import Tiling

class Strategy(abc.ABC):
    @abc.abstractmethod
    def __call__(self, tiling: Tiling):
        """Returns the results of the strategy on a tiling."""

    @abc.abstractmethod
    def __str__(self):
        """Return the name of the strategy."""

    @abc.abstractmethod
    def to_json(self) -> dict:
        """Return a dictionary form of the strategy."""

    @abc.abstractclassmethod
    def from_json(d: dict) -> Strategy:
        """Return the strategy from the json representation."""
        module = import_module(d['class_module'])
        StrategyClass = getattr(module, d['strategy_class'])
        assert isinstance(StrategyClass, Strategy), 'Not a valid strategy'
        return StrategyClass.to_json(d)

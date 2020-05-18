import abc
from importlib import import_module

from typing import TYPE_CHECKING, Iterable, Type

from .griddedperm import GriddedPerm

if TYPE_CHECKING:
    from .tiling import Tiling


class AbstractAssumption(abc.ABC):
    @abc.abstractmethod
    def contradictory(self, tiling: "Tiling") -> bool:
        """
        Return True if the assumption contradicts the tiling. That is,
        return True if all gridded perms on the tiling can not satisfy the
        assumption.
        """

    def to_jsonable(self) -> dict:
        return {
            "class_module": self.__class__.__module__,
            "assumption_class": self.__class__.__name__,
        }

    @classmethod
    @abc.abstractmethod
    def from_dict(self, d: dict) -> "AbstractAssumption":
        module = import_module(d.pop("class_module"))
        AssumptionClass: Type["AbstractAssumption"] = getattr(
            module, d.pop("assumption_class")
        )
        return AssumptionClass.from_dict(d)

    @abc.abstractmethod
    def __hash__(self) -> int:
        pass

    def __eq__(self, other) -> bool:
        return isinstance(self, other.__class__) and self.__dict__ == other.__dict__

    @abc.abstractmethod
    def __lt__(self, other) -> bool:
        return bool(self.__class__.__name__ < other.__class__.__name__)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    def __str__(self) -> str:
        return self.__class__.__name__


class TrackingAssumption(AbstractAssumption):
    def __init__(self, gps: Iterable[GriddedPerm]):
        self.gps = tuple(sorted(set(gps)))

    def avoiding(self, obstructions: Iterable[GriddedPerm]) -> "TrackingAssumption":
        obstructions = tuple(obstructions)
        return self.__class__(tuple(gp for gp in self.gps if gp.avoids(*obstructions)))

    @staticmethod
    def contradictory(tiling: "Tiling") -> bool:
        return False

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["gps"] = [gp.to_jsonable() for gp in self.gps]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "TrackingAssumption":
        gps = [GriddedPerm.from_dict(gp) for gp in d["gps"]]
        return cls(gps)

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.gps < other.gps
        return super().__lt__(other)

    def __hash__(self) -> int:
        return hash(self.gps)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "({})".format(self.gps)

    def __str__(self):
        return "can count occurences of\n{}".format(
            "\n".join(str(gp) for gp in self.gps)
        )

from typing import Iterable

from .griddedperm import GriddedPerm


class TrackingAssumption:
    """
    An assumption used to keep track of the occurrences of a set of gridded
    permutations.
    """

    def __init__(self, gps: Iterable[GriddedPerm]):
        self.gps = tuple(sorted(set(gps)))

    def avoiding(self, obstructions: Iterable[GriddedPerm]) -> "TrackingAssumption":
        """
        Return the tracking absumption where all of the gridded perms avoiding
        the obstructions are removed.
        """
        obstructions = tuple(obstructions)
        return self.__class__(tuple(gp for gp in self.gps if gp.avoids(*obstructions)))

    def to_jsonable(self) -> dict:
        return {"gps": [gp.to_jsonable() for gp in self.gps]}

    @classmethod
    def from_dict(cls, d: dict) -> "TrackingAssumption":
        gps = [GriddedPerm.from_dict(gp) for gp in d["gps"]]
        return cls(gps)

    def __eq__(self, other) -> bool:
        if isinstance(other, TrackingAssumption):
            return bool(self.gps == other.gps)
        return NotImplemented

    def __lt__(self, other) -> bool:
        if isinstance(other, TrackingAssumption):
            return bool(self.gps < other.gps)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.gps)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "({})".format(self.gps)

    def __str__(self):
        return "can count occurences of\n{}".format(
            "\n".join(str(gp) for gp in self.gps)
        )

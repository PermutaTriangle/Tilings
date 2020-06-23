import abc
from importlib import import_module
from itertools import chain
from typing import Iterable, List, Optional, Tuple, Type

from permuta import Perm

from .griddedperm import GriddedPerm

Cell = Tuple[int, int]


class TrackingAssumption:
    """
    An assumption used to keep track of the occurrences of a set of gridded
    permutations.
    """

    def __init__(self, gps: Iterable[GriddedPerm]):
        self.gps = tuple(sorted(set(gps)))

    def avoiding(
        self,
        obstructions: Iterable[GriddedPerm],
        active_cells: Optional[Iterable[Cell]] = None,
    ) -> "TrackingAssumption":
        """
        Return the tracking absumption where all of the gridded perms avoiding
        the obstructions are removed. If active_cells is not None, then any
        assumptions involving a cell not in active_cells will be removed.
        """
        obstructions = tuple(obstructions)
        if active_cells is not None:
            return self.__class__(
                tuple(
                    gp
                    for gp in self.gps
                    if all(cell in active_cells for cell in gp.pos)
                    and gp.avoids(*obstructions)
                )
            )
        return self.__class__(tuple(gp for gp in self.gps if gp.avoids(*obstructions)))

    def get_value(self, gp: GriddedPerm) -> int:
        """
        Return the number of occurrences of each of the gridded perms being track in
        the gridded perm gp.
        """
        return len(list(chain.from_iterable(p.occurrences_in(gp) for p in self.gps)))

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the assumption."""
        c = self.__class__
        return {
            "class_module": c.__module__,
            "assumption": c.__name__,
            "gps": [gp.to_jsonable() for gp in self.gps],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TrackingAssumption":
        """Return the assumption from the json dict representation."""
        module = import_module(d["class_module"])
        AssClass: Type["TrackingAssumption"] = getattr(module, d["assumption"])
        assert issubclass(
            AssClass, TrackingAssumption
        ), "Not a valid TrackingAssumption"
        gps = [GriddedPerm.from_dict(gp) for gp in d["gps"]]
        return AssClass(gps)

    def __eq__(self, other) -> bool:
        if other.__class__ == TrackingAssumption:
            return bool(self.gps == other.gps)
        return NotImplemented

    def __lt__(self, other) -> bool:
        if isinstance(other, TrackingAssumption):
            return bool(
                self.__class__.__name__ < other.__class__.__name__
                and self.gps < other.gps
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.gps)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "({})".format(self.gps)

    def __str__(self):
        return "can count occurrences of\n{}".format(
            "\n".join(str(gp) for gp in self.gps)
        )


class ComponentAssumption(TrackingAssumption):
    """
    An assumption used to keep track of the number of components in a
    region of a tiling.

    In order to inherit from TrackingAssumption, the set of cells should be
    given as a set of length 1 gridded perms using each cell. This ensures
    most strategies work without change.
    """

    def __init__(self, gps: Iterable[GriddedPerm]):
        super().__init__(gps)
        assert all(len(gp) == 1 for gp in self.gps)
        self.cells = frozenset(gp.pos[0] for gp in self.gps)

    @abc.abstractmethod
    def decomposition(self, perm: Perm) -> List[Perm]:
        """Count the number of component in a permutation."""

    def get_value(self, gp: GriddedPerm) -> int:
        """
        Return the number of components in the tracked region of the gridded perm.
        """
        subgp = gp.get_gridded_perm_in_cells(self.cells)
        return len(self.decomposition(subgp.patt))

    def __eq__(self, other) -> bool:
        if isinstance(other, ComponentAssumption) and self.__class__ == other.__class__:
            return bool(self.gps == other.gps)
        return NotImplemented

    def __repr__(self) -> str:
        return self.__class__.__name__ + "({})".format(self.gps)

    def __str__(self):
        return f"can count components in cells {self.cells}"

    def __hash__(self) -> int:
        return hash(self.gps)


class SumComponentAssumption(ComponentAssumption):
    @staticmethod
    def sum_decomposition(perm: Perm) -> List[Perm]:
        """
        Return the sum decomposition of the permutation.
        TODO: this method should be on permuta.
        """
        res: List[Perm] = []
        max_val = -1
        curr_block_start_idx = 0
        for idx, val in enumerate(perm):
            max_val = max(max_val, val)
            if idx == max_val:
                res.append(Perm.to_standard(perm[curr_block_start_idx : idx + 1]))
                curr_block_start_idx = idx + 1
        return res

    decomposition = Perm.sum_decomposition

    def __str__(self):
        return f"can count sum components in cells {self.cells}"

    def __hash__(self) -> int:
        return hash(self.gps)


class SkewComponentAssumption(ComponentAssumption):
    @staticmethod
    def skew_decomposition(perm: Perm) -> List[Perm]:
        """
        Return the skew decomposition of the permutation.
        TODO: this method should be on permuta.
        """
        res: List[Perm] = []
        min_val = len(perm) + 1
        curr_block_start_idx = 0
        for idx, val in enumerate(perm):
            min_val = min(min_val, val)
            if len(perm) - idx - 1 == min_val:
                res.append(Perm.to_standard(perm[curr_block_start_idx : idx + 1]))
                curr_block_start_idx = idx + 1
        return res

    decomposition = Perm.skew_decomposition

    def __str__(self):
        return f"can count skew components in cells {self.cells}"

    def __hash__(self) -> int:
        return hash(self.gps)

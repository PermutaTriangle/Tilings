"""
This file contains "experimental" verification packs, which are those that verify
tilings for which we are not certain we can independently calculate their counting
sequence or generating function.
"""

from typing import Iterable, Optional

from comb_spec_searcher import VerificationStrategy
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import SubclassVerificationAlgorithm

__all__ = [
    "SubclassVerificationStrategy",
]


TileScopeVerificationStrategy = VerificationStrategy[Tiling, GriddedPerm]


class SubclassVerificationStrategy(TileScopeVerificationStrategy):
    """
    Verify a tiling if its underlying ungridded permutations are contained in a subclass
    of the search class.
    """

    def __init__(
        self,
        perms_to_check: Optional[Iterable[Perm]] = None,
        ignore_parent: bool = True,
    ):
        if perms_to_check is None:
            self.perms_to_check = None
        else:
            self.perms_to_check = set(perms_to_check)
        super().__init__(ignore_parent=ignore_parent)

    def verified(self, tiling: Tiling) -> bool:
        assert self.perms_to_check is not None, "perms_to_check was never set"
        algo = SubclassVerificationAlgorithm(tiling, self.perms_to_check)
        return algo.verified()

    @staticmethod
    def formal_step() -> str:
        return "tiling is a subclass"

    def __str__(self) -> str:
        return "subclass verification"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["perms_to_check"] = (
            frozenset(self.perms_to_check) if self.perms_to_check is not None else None
        )
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "SubclassVerificationStrategy":
        perms_to_check = d.pop("perms_to_check")
        return cls(perms_to_check=perms_to_check, **d)

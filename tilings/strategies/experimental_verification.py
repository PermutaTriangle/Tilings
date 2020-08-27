"""
This file contains "experimental" verification strategies, which are those that verify
tilings for which we are not certain we can independently calculate their counting
sequence or generating function.
"""

from typing import Iterable, Iterator, Optional

from comb_spec_searcher import StrategyFactory, VerificationStrategy
from comb_spec_searcher.strategies import VerificationRule
from permuta import Av, Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Factor, SubclassVerificationAlgorithm

__all__ = [
    "ShortObstructionVerificationStrategy",
    "SubclassVerificationFactory",
]

TileScopeVerificationStrategy = VerificationStrategy[Tiling, GriddedPerm]


class ShortObstructionVerificationStrategy(TileScopeVerificationStrategy):
    """
    A strategy to mark as verified any tiling whose crossing obstructions all have
    size at most 3. Tilings with dimensions 1x1 are ignored.
    """

    @staticmethod
    def verified(tiling: Tiling):
        return tiling.dimensions != (1, 1) and all(
            ob.is_single_cell() or len(ob) <= 3 for ob in tiling.obstructions
        )

    @staticmethod
    def formal_step() -> str:
        return "tiling has short crossing obstructions"

    def __str__(self) -> str:
        return "short crossing obstruction verification"

    @classmethod
    def from_dict(cls, d: dict) -> "ShortObstructionVerificationStrategy":
        return cls(**d)


class SubclassVerificationStrategy(TileScopeVerificationStrategy):
    """
    A strategy object for holding the results of SubclassVerification
    """

    def __init__(self, subclass_basis=Iterable[Perm], ignore_parent: bool = True):
        self.subclass_basis = tuple(sorted(subclass_basis))
        super().__init__(ignore_parent=ignore_parent)

    def verified(self, tiling: Tiling) -> bool:
        algo = SubclassVerificationAlgorithm(tiling, set(self.subclass_basis))
        return algo.subclasses == self.subclass_basis

    def formal_step(self) -> str:
        return "tiling is contained in the subclass {}".format(Av(self.subclass_basis))

    def __str__(self) -> str:
        return "subclass verification strategy"

    def __repr__(self):
        return self.__class__.__name__ + "(subclass_basis={})".format(
            self.subclass_basis
        )

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["subclass_basis"] = self.subclass_basis
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "SubclassVerificationStrategy":
        subclass_basis = [Perm(p) for p in d.pop("subclass_basis")]
        return cls(subclass_basis=subclass_basis, **d)


class SubclassVerificationFactory(StrategyFactory[Tiling]):
    """
    A factory that verifies a tiling if its underlying ungridded permutations are
    contained in a subclass of the search class, and if so creates the appropriate
    strategy.

    Note: it isn't really a generator.
    """

    def __init__(self, perms_to_check: Optional[Iterable[Perm]] = None):
        if perms_to_check is None:
            self.perms_to_check = None
        else:
            self.perms_to_check = set(perms_to_check)
        super().__init__()

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[VerificationRule]:
        assert self.perms_to_check is not None, "perms_to_check was never set"

        # It is a waste of time to check a factorable tiling, since we will check its
        # children eventually.
        if Factor(comb_class).factorable():
            return

        algo = SubclassVerificationAlgorithm(comb_class, self.perms_to_check)
        if algo.subclasses:
            yield SubclassVerificationStrategy(algo.subclasses)(comb_class, tuple())

    def change_perms(
        self, perms_to_check: Iterable[Perm]
    ) -> "SubclassVerificationFactory":
        """
        Return a new version of the verfication strategy with the given perms to check
        instead of the current one.
        """
        perms_to_check = set(perms_to_check)
        return self.__class__(perms_to_check=perms_to_check)

    def __str__(self):
        return "subclass verification factory"

    def __repr__(self):
        return self.__class__.__name__ + "(perms_to_check={})".format(
            self.perms_to_check
        )

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["perms_to_check"] = (
            tuple(sorted(self.perms_to_check))
            if self.perms_to_check is not None
            else None
        )
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "SubclassVerificationFactory":
        if d["perms_to_check"] is not None:
            perms_to_check: Optional[Iterable[Perm]] = [
                Perm(p) for p in d.pop("perms_to_check")
            ]
        else:
            perms_to_check = d.pop("perms_to_check")
        assert len(d) == 0
        return cls(perms_to_check=perms_to_check)

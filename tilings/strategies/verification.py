from itertools import chain
from typing import Iterable

from sympy import Expr, var

from comb_spec_searcher import (
    AtomStrategy,
    StrategyPack,
    VerificationStrategy,
)
from permuta import Perm
from permuta.permutils.symmetry import all_symmetry_sets
from tilings import Tiling
from tilings.algorithms.enumeration import (
    DatabaseEnumeration,
    LocalEnumeration,
    MonotoneTreeEnumeration,
)
from tilings.strategies import (
    AllFactorStrategy,
    AllFactorInsertionStrategy,
    RequirementCorroborationStrategy,
)
from tilings.exception import InvalidOperationError

# TileScopeVerificationStrategyType = TypeVar(
#     "TileScopeVerificationStrategyType", bound="TileScopeVerificationStrategy"
# )

x = var("x")

__all__ = [
    "BasicVerificationStrategy",
    "OneByOneVerificationStrategy",
    "DatabaseVerificationStrategy",
    "LocallyFactorableVerificationStrategy",
    "ElementaryVerificationStrategy",
    "LocalVerificationStrategy",
    "MonotoneTreeVerificationStrategy",
]


BasicVerificationStrategy = AtomStrategy


class OneByOneVerificationStrategy(VerificationStrategy[Tiling]):
    def __init__(
        self, basis: Iterable[Perm] = None, symmetry: bool = False,
    ):
        if basis is not None:
            assert all(
                isinstance(p, Perm) for p in basis
            ), "Element of the basis must be Perm"
            if symmetry:
                self.symmetries = set(frozenset(b) for b in all_symmetry_sets(basis))
            else:
                self.symmetries = set([frozenset(basis)])
        else:
            self.symmetries = set()
        super().__init__()

    def add_basis(self, basis: Iterable[Perm], symmetry: bool = False):
        if symmetry:
            self.symmetries.update(frozenset(b) for b in all_symmetry_sets(basis))
        else:
            self.symmetries.add(frozenset(basis))

    def pack(self) -> StrategyPack:
        raise InvalidOperationError(
            "Cannot get a specification for one by one verification"
        )

    def get_genf(self, tiling: Tiling):
        if not self.verified(tiling):
            raise InvalidOperationError("tiling not one by one verified")
        return LocalEnumeration(tiling).get_genf()

    def verified(self, tiling: Tiling):
        return (
            tiling.dimensions == (1, 1)
            and frozenset(ob.patt for ob in tiling.obstructions) not in self.symmetries
        )

    def formal_step(self) -> str:
        return "tiling is a subclass of the original tiling"

    def __repr__(self) -> str:
        if self.symmetries:
            basis = list(self.symmetries)[0]
            return self.__class__.__name__ + "(basis={}, symmetry={})".format(
                basis, True
            )
        else:
            return self.__class__.__name__ + "()"

    def __str__(self) -> str:
        return "one by one verification"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["basis"] = list(list(self.symmetries)[0]) if self.symmetries else None
        d["symmetry"] = bool(self.symmetries)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "OneByOneVerificationStrategy":
        basis = [Perm(p) for p in d["basis"]] if d["basis"] is not None else None
        return cls(basis=basis, symmetry=d["symmetry"])


class DatabaseVerificationStrategy(VerificationStrategy[Tiling]):
    """
    Enumeration strategy for a tilings that are in the database.

    There is not always a specification for a tiling in the database but you
    can always find the generating function by looking up the database.
    """

    def pack(self) -> StrategyPack:
        # TODO: check database for tiling
        raise InvalidOperationError(
            "Cannot get a specification for a tiling in the database"
        )

    def get_genf(self, tiling: Tiling):
        return DatabaseEnumeration(tiling).get_genf()

    def verified(self, tiling: Tiling):
        return DatabaseEnumeration(tiling).verified()

    def formal_step(self) -> str:
        return "tiling is in the database"

    def __str__(self) -> str:
        return "database verification"

    @classmethod
    def from_dict(cls, d: dict) -> "DatabaseVerificationStrategy":
        return cls()


class LocallyFactorableVerificationStrategy(VerificationStrategy[Tiling]):
    """
    Verification strategy for a locally factorable tiling.

    A tiling is locally factorable if all its obstructions and requirements are
    locally factorable, i.e. each obstruction or requirement use at most one
    cell on each row and column. To be locally factorable, a tiling
    should not be equivalent to a 1x1 tiling.

    A locally factorable tiling can be describe with a specification with only subset
    verified tiling.
    """

    def pack(self) -> StrategyPack:
        return StrategyPack(
            name="LocallyFactorable",
            initial_strats=[AllFactorStrategy(), RequirementCorroborationStrategy()],
            inferral_strats=[],
            expansion_strats=[[AllFactorInsertionStrategy()]],
            ver_strats=[
                BasicVerificationStrategy(),
                OneByOneVerificationStrategy(),
                MonotoneTreeVerificationStrategy(),  # no factors
                LocalVerificationStrategy(),  # no factors
            ],
        )

    def _locally_factorable_obstructions(self, tiling: Tiling):
        """
        Check if all the obstructions of the tiling are locally factorable.
        """
        return all(not ob.is_interleaving() for ob in tiling.obstructions)

    def _locally_factorable_requirements(self, tiling: Tiling):
        """
        Check if all the requirements of the tiling are locally factorable.
        """
        reqs = chain.from_iterable(tiling.requirements)
        return all(not r.is_interleaving() for r in reqs)

    def verified(self, tiling: Tiling):
        return (
            not tiling.dimensions == (1, 1)
            and self._locally_factorable_obstructions(tiling)
            and self._locally_factorable_requirements(tiling)
        )

    def formal_step(self) -> str:
        return "tiling is locally factorable"

    @classmethod
    def from_dict(cls, d: dict) -> "LocallyFactorableVerificationStrategy":
        return cls()

    def __str__(self) -> str:
        return "locally factorable verification"


class ElementaryVerificationStrategy(LocallyFactorableVerificationStrategy):
    """
    Verification strategy for elementary tilings.

    A tiling is elementary if each active cell is on its own row and column.
    To be elementary, a tiling should not be equivalent to a 1x1
    tiling.

    By definition an elementary tiling is locally factorable.

    A elementary tiling can be describe with a specification with only one by one
    verified tiling.
    """

    def verified(self, tiling: Tiling):
        return tiling.fully_isolated() and not tiling.dimensions == (1, 1)

    def formal_step(self) -> str:
        return "tiling is elementary verified"

    @classmethod
    def from_dict(cls, d: dict) -> "ElementaryVerificationStrategy":
        return cls()

    def __str__(self) -> str:
        return "elementary verification"


class LocalVerificationStrategy(VerificationStrategy[Tiling]):
    """
    The local verified strategy.

    A tiling is local verified if every obstruction and every requirement is
    localized, i.e. in a single cell and the tiling is not 1x1.
    """

    def pack(self) -> StrategyPack:
        # TODO: check database for tiling
        raise InvalidOperationError(
            "Cannot get a specification for a tiling in the database"
        )

    def get_genf(self, tiling: Tiling):
        return LocalEnumeration(tiling).get_genf()

    def verified(self, tiling: Tiling):
        return tiling.dimensions != (1, 1) and LocalEnumeration(tiling).verified()

    def formal_step(self) -> str:
        return "tiling is locally enumerable"

    @classmethod
    def from_dict(cls, d: dict) -> "LocalVerificationStrategy":
        return cls()

    def __str__(self) -> str:
        return "local verification"


class MonotoneTreeVerificationStrategy(VerificationStrategy[Tiling]):
    """
    Verify all tiling that is a monotone tree.
    """

    def pack(self) -> StrategyPack:
        # TODO: check database for tiling
        raise InvalidOperationError(
            "Cannot get a specification for a tiling in the database"
        )

    def verified(self, tiling: Tiling):
        return MonotoneTreeEnumeration(tiling).verified()

    def formal_step(self) -> str:
        return "tiling is a monotone tree"

    @classmethod
    def from_dict(cls, d: dict) -> "MonotoneTreeVerificationStrategy":
        return cls()

    def get_genf(self, tiling: Tiling) -> Expr:
        return MonotoneTreeEnumeration(tiling).get_genf()

    def __str__(self) -> str:
        return "monotone tree verification"

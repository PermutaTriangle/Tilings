from itertools import chain
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from sympy import Expr, Function, var

from comb_spec_searcher import AtomStrategy, StrategyPack, VerificationStrategy
from comb_spec_searcher.exception import InvalidOperationError, StrategyDoesNotApply
from permuta import Perm
from permuta.permutils.symmetry import all_symmetry_sets
from tilings import GriddedPerm, Tiling
from tilings.algorithms.enumeration import (
    DatabaseEnumeration,
    LocalEnumeration,
    MonotoneTreeEnumeration,
)
from tilings.strategies import (
    FactorFactory,
    FactorInsertionFactory,
    RequirementCorroborationFactory,
)

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
TileScopeVerificationStrategy = VerificationStrategy[Tiling, GriddedPerm]


class OneByOneVerificationStrategy(TileScopeVerificationStrategy):
    def __init__(
        self,
        basis: Optional[Iterable[Perm]] = None,
        symmetry: bool = False,
        ignore_parent: bool = True,
    ):
        self._basis = tuple(basis) if basis is not None else tuple()
        self._symmetry = symmetry
        assert all(
            isinstance(p, Perm) for p in self._basis
        ), "Element of the basis must be Perm"
        if symmetry:
            self.symmetries = set(frozenset(b) for b in all_symmetry_sets(self._basis))
        else:
            self.symmetries = set([frozenset(self._basis)])
        super().__init__(ignore_parent=ignore_parent)

    def change_basis(
        self, basis: Iterable[Perm], symmetry: bool = False
    ) -> "OneByOneVerificationStrategy":
        """
        Return a new version of the verfication strategy with the given basis instead of
        the current one.
        """
        basis = tuple(basis)
        return self.__class__(basis, self._symmetry, self.ignore_parent)

    @property
    def basis(self) -> Tuple[Perm, ...]:
        return self._basis

    @staticmethod
    def pack() -> StrategyPack:
        raise InvalidOperationError(
            "Cannot get a specification for one by one verification"
        )

    def verified(self, tiling: Tiling) -> bool:
        return (
            tiling.dimensions == (1, 1)
            and frozenset(ob.patt for ob in tiling.obstructions) not in self.symmetries
        )

    @staticmethod
    def formal_step() -> str:
        return "tiling is a subclass of the original tiling"

    def get_genf(self, tiling: Tiling, funcs: Optional[Dict[Tiling, Function]] = None):
        if not self.verified(tiling):
            raise StrategyDoesNotApply("tiling not one by one verified")
        return LocalEnumeration(tiling).get_genf()

    def count_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> int:
        raise NotImplementedError(
            "Not implemented method to count objects for monotone tree "
            "verified tilings"
        )

    def generate_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError(
            "Not implemented method to generate objects for monotone tree "
            "verified tilings"
        )

    def random_sample_object_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> GriddedPerm:
        raise NotImplementedError(
            "Not implemented random sample for monotone tree verified tilings"
        )

    def __repr__(self) -> str:
        if self.symmetries:
            return self.__class__.__name__ + (
                "(basis={}, symmetry={}, " "ignore_parent={})"
            ).format(list(self._basis), True, self.ignore_parent)
        return self.__class__.__name__ + "()"

    def __str__(self) -> str:
        return "one by one verification"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["basis"] = self._basis
        d["symmetry"] = self._symmetry
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "OneByOneVerificationStrategy":
        if d["basis"] is not None:
            basis: Optional[List[Perm]] = [Perm(p) for p in d.pop("basis")]
        else:
            basis = d.pop("basis")
        return cls(basis=basis, **d)


class DatabaseVerificationStrategy(TileScopeVerificationStrategy):
    """
    Enumeration strategy for a tilings that are in the database.

    There is not always a specification for a tiling in the database but you
    can always find the generating function by looking up the database.
    """

    @staticmethod
    def pack() -> StrategyPack:
        # TODO: check database for tiling
        raise InvalidOperationError(
            "Cannot get a specification for a tiling in the database"
        )

    @staticmethod
    def verified(tiling: Tiling):
        return DatabaseEnumeration(tiling).verified()

    @staticmethod
    def formal_step() -> str:
        return "tiling is in the database"

    def get_genf(self, tiling: Tiling, funcs: Optional[Dict[Tiling, Function]] = None):
        if not self.verified(tiling):
            raise StrategyDoesNotApply("tiling is not in the database")
        return DatabaseEnumeration(tiling).get_genf()

    def count_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> int:
        raise NotImplementedError(
            "Not implemented method to count objects for monotone tree "
            "verified tilings"
        )

    def generate_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError(
            "Not implemented method to generate objects for monotone tree "
            "verified tilings"
        )

    def random_sample_object_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> GriddedPerm:
        raise NotImplementedError(
            "Not implemented random sample for monotone tree verified tilings"
        )

    def __str__(self) -> str:
        return "database verification"

    @classmethod
    def from_dict(cls, d: dict) -> "DatabaseVerificationStrategy":
        return cls(**d)


class LocallyFactorableVerificationStrategy(TileScopeVerificationStrategy):
    """
    Verification strategy for a locally factorable tiling.

    A tiling is locally factorable if all its obstructions and requirements are
    locally factorable, i.e. each obstruction or requirement use at most one
    cell on each row and column. To be locally factorable, a tiling
    should not be equivalent to a 1x1 tiling.

    A locally factorable tiling can be describe with a specification with only subset
    verified tiling.
    """

    @staticmethod
    def pack() -> StrategyPack:
        return StrategyPack(
            name="LocallyFactorable",
            initial_strats=[FactorFactory(), RequirementCorroborationFactory()],
            inferral_strats=[],
            expansion_strats=[[FactorInsertionFactory()]],
            ver_strats=[
                BasicVerificationStrategy(),
                OneByOneVerificationStrategy(),
                MonotoneTreeVerificationStrategy(),  # no factors
                LocalVerificationStrategy(),  # no factors
            ],
        )

    @staticmethod
    def _locally_factorable_obstructions(tiling: Tiling):
        """
        Check if all the obstructions of the tiling are locally factorable.
        """
        return all(not ob.is_interleaving() for ob in tiling.obstructions)

    @staticmethod
    def _locally_factorable_requirements(tiling: Tiling):
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

    @staticmethod
    def formal_step() -> str:
        return "tiling is locally factorable"

    @classmethod
    def from_dict(cls, d: dict) -> "LocallyFactorableVerificationStrategy":
        return cls(**d)

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

    @staticmethod
    def verified(tiling: Tiling):
        return tiling.fully_isolated() and not tiling.dimensions == (1, 1)

    @staticmethod
    def formal_step() -> str:
        return "tiling is elementary verified"

    @classmethod
    def from_dict(cls, d: dict) -> "ElementaryVerificationStrategy":
        return cls(**d)

    def __str__(self) -> str:
        return "elementary verification"


class LocalVerificationStrategy(TileScopeVerificationStrategy):
    """
    The local verified strategy.

    A tiling is local verified if every obstruction and every requirement is
    localized, i.e. in a single cell and the tiling is not 1x1.
    """

    @staticmethod
    def pack() -> StrategyPack:
        # TODO: check database for tiling
        raise InvalidOperationError(
            "Cannot get a specification for a tiling in the database"
        )

    @staticmethod
    def verified(tiling: Tiling):
        return tiling.dimensions != (1, 1) and LocalEnumeration(tiling).verified()

    @staticmethod
    def formal_step() -> str:
        return "tiling is locally enumerable"

    @classmethod
    def from_dict(cls, d: dict) -> "LocalVerificationStrategy":
        return cls(**d)

    def get_genf(self, tiling: Tiling, funcs: Optional[Dict[Tiling, Function]] = None):
        if not self.verified(tiling):
            raise StrategyDoesNotApply("tiling not locally verified")
        return LocalEnumeration(tiling).get_genf()

    def count_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> int:
        raise NotImplementedError(
            "Not implemented method to count objects for monotone tree "
            "verified tilings"
        )

    def generate_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError(
            "Not implemented method to generate objects for monotone tree "
            "verified tilings"
        )

    def random_sample_object_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> GriddedPerm:
        raise NotImplementedError(
            "Not implemented random sample for monotone tree verified tilings"
        )

    def __str__(self) -> str:
        return "local verification"


class MonotoneTreeVerificationStrategy(TileScopeVerificationStrategy):
    """
    Verify all tiling that is a monotone tree.
    """

    @staticmethod
    def pack() -> StrategyPack:
        # TODO: check database for tiling
        raise InvalidOperationError(
            "Cannot get a specification for a tiling in the database"
        )

    @staticmethod
    def verified(tiling: Tiling):
        return MonotoneTreeEnumeration(tiling).verified()

    @staticmethod
    def formal_step() -> str:
        return "tiling is a monotone tree"

    @classmethod
    def from_dict(cls, d: dict) -> "MonotoneTreeVerificationStrategy":
        return cls(**d)

    def get_genf(
        self, tiling: Tiling, funcs: Optional[Dict[Tiling, Function]] = None
    ) -> Expr:
        if not self.verified(tiling):
            raise StrategyDoesNotApply("tiling is not monotone tree verified")
        return MonotoneTreeEnumeration(tiling).get_genf()

    def count_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> int:
        raise NotImplementedError(
            "Not implemented method to count objects for monotone tree "
            "verified tilings"
        )

    def generate_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError(
            "Not implemented method to generate objects for monotone tree "
            "verified tilings"
        )

    def random_sample_object_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> GriddedPerm:
        raise NotImplementedError(
            "Not implemented random sample for monotone tree verified tilings"
        )

    def __str__(self) -> str:
        return "monotone tree verification"

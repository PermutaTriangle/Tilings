from typing import Iterable, Iterator, List, Tuple, Type, TypeVar

from sympy import Expr, var

from comb_spec_searcher import (
    CombinatorialSpecification,
    StrategyGenerator,
    StrategyPack,
    VerificationStrategy,
)
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms.enumeration import (
    DatabaseEnumeration,
    ElementaryEnumeration,
    Enumeration,
    LocalEnumeration,
    LocallyFactorableEnumeration,
    MonotoneTreeEnumeration,
    OneByOneEnumeration,
)
from tilings.exception import InvalidOperationError

TileScopeVerificationStrategyType = TypeVar(
    "TileScopeVerificationStrategyType", bound="TileScopeVerificationStrategy"
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


class BasicVerificationStrategy(VerificationStrategy[Tiling]):
    def __init__(self):
        super().__init__()

    def verified(self, tiling: Tiling) -> bool:
        return tiling.is_epsilon() or tiling.is_point_tiling()

    def pack(self) -> StrategyPack:
        raise InvalidOperationError("Cannot get a tree for a basic " "verification")

    def get_specfication(self, tiling: Tiling, **kwargs) -> CombinatorialSpecification:
        raise InvalidOperationError("Cannot get a tree for a basic " "verification")

    def get_genf(self, tiling: Tiling) -> Expr:
        if tiling.is_epsilon():
            return 1
        if tiling.is_point_tiling():
            return x
        raise InvalidOperationError("Not an atom")

    def count_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> int:
        """Verification strategies must contain a method to count the objects."""
        if (n == 0 and comb_class.is_epsilon()) or (
            n == 1 and comb_class.is_point_tiling()
        ):
            return 1
        return 0

    def generate_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> Iterator[GriddedPerm]:
        """Verification strategies must contain a method to generate the objects."""
        if n == 0 and comb_class.is_epsilon():
            yield GriddedPerm.empty_perm()
        if n == 1 and comb_class.is_point_tiling():
            yield GriddedPerm(Perm((0,)), ((0, 0),))

    def random_sample_object_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> GriddedPerm:
        """
        A method to sample uniformly at random from a verified combinatorial class.
        Raises an InvalidOperationError if the combinatorial class is not verified.
        """
        if n == 0 and comb_class.is_epsilon():
            return GriddedPerm.empty_perm()
        if n == 1 and comb_class.is_point_tiling():
            return GriddedPerm(Perm((0,)), ((0, 0),))

    def formal_step(self) -> str:
        return "tiling is an atom"

    def __repr__(self) -> str:
        return "{}(ignore_parent={})".format(
            self.__class__.__name__, self.ignore_parent
        )

    def __str__(self) -> str:
        return "verify atoms"

    @classmethod
    def from_dict(cls, d: dict) -> "BasicVerificationStrategy":
        return cls()


class TileScopeVerificationStrategy(VerificationStrategy[Tiling]):
    """
    Abstract verification strategy class the group the shared logic of
    verification strategy. Subclass need to have the class attribute
    `VERIFICATION_CLASS`.
    """

    VERIFICATION_CLASS: Type[Enumeration] = NotImplemented

    def __init__(self, ignore_parent: bool = True):
        super().__init__(ignore_parent=ignore_parent)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.VERIFICATION_CLASS is NotImplemented:
            raise NotImplementedError(
                "Need to define {}.VERIFICATION_CLASS".format(cls.__name__)
            )

    def pack(self) -> StrategyPack:
        return self.VERIFICATION_CLASS.pack

    def verified(self, tiling: Tiling) -> bool:
        return self.VERIFICATION_CLASS(tiling).verified()

    def formal_step(self) -> str:
        return self.VERIFICATION_CLASS.formal_step

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(
        cls: Type[TileScopeVerificationStrategyType], d: dict
    ) -> TileScopeVerificationStrategyType:
        return cls(ignore_parent=d["ignore_parent"])


class _OneByOneVerificationStrategy(TileScopeVerificationStrategy):
    def __init__(
        self, basis: Iterable[Perm], symmetry: bool = False, ignore_parent: bool = True,
    ):
        self.basis = tuple(basis)
        self.symmetry = symmetry
        super().__init__(ignore_parent=ignore_parent)

    VERIFICATION_CLASS = OneByOneEnumeration

    def pack(self) -> StrategyPack:
        raise InvalidOperationError(
            "Cannot get a specification for one by one verification"
        )

    def get_specification(self, tiling: Tiling) -> CombinatorialSpecification:
        raise InvalidOperationError(
            "Cannot get a specification for one by one verification"
        )

    def get_genf(self, tiling: Tiling):
        if not self.verified(tiling):
            raise InvalidOperationError("tiling not one by one verified")
        raise NotImplementedError("not implemented one by one verification")

    def verified(self, tiling: Tiling):
        return (
            tiling.dimensions == (1, 1)
            and self.VERIFICATION_CLASS(tiling, self.basis, self.symmetry).verified()
        )

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + "(basis={}, symmetry={}, ignore_parent={})".format(
                self.basis, self.symmetry, self.ignore_parent
            )
        )

    def __str__(self) -> str:
        return "one by one verification"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["basis"] = self.basis
        d["symmetry"] = self.symmetry
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "_OneByOneVerificationStrategy":
        basis = [Perm(p) for p in d["basis"]]
        return cls(
            basis=basis, symmetry=d["symmetry"], ignore_parent=d["ignore_parent"],
        )


class OneByOneVerificationStrategy(StrategyGenerator[Tiling]):
    """Return a verification rule if one-by-one verified."""

    def __init__(self, ignore_parent: bool = True):
        self.ignore_parent = ignore_parent

    def __call__(
        self, comb_class: Tiling, **kwargs
    ) -> Iterator[_OneByOneVerificationStrategy]:
        if "basis" not in kwargs:
            raise TypeError("Missing basis argument")
        basis: Iterable[Perm] = kwargs["basis"]
        symmetry = kwargs.get("symmetry", False)
        yield _OneByOneVerificationStrategy(
            basis=basis, symmetry=symmetry, ignore_parent=self.ignore_parent
        )

    def __str__(self) -> str:
        return "one by one verification"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["ignore_parent"] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d) -> "OneByOneVerificationStrategy":
        return cls(ignore_parent=d["ignore_parent"])


class DatabaseVerificationStrategy(TileScopeVerificationStrategy):
    """Verify a tiling that is in the database"""

    VERIFICATION_CLASS = DatabaseEnumeration

    def pack(self) -> StrategyPack:
        raise InvalidOperationError(
            "Cannot get a specification for database verification"
        )

    def get_specification(self, tiling: Tiling) -> CombinatorialSpecification:
        raise InvalidOperationError(
            "Cannot get a specification for database verification"
        )

    def get_genf(self, tiling: Tiling) -> Expr:
        return self.VERIFICATION_CLASS(tiling).get_genf()

    def __str__(self) -> str:
        return "database verification"


class LocallyFactorableVerificationStrategy(TileScopeVerificationStrategy):
    """
    The locally factorable verified strategy.

    A tiling is locally factorable if every requirement and obstruction is
    non-interleaving, i.e. use a single cell in each row and column.
    """

    VERIFICATION_CLASS = LocallyFactorableEnumeration

    def pack(self) -> StrategyPack:
        raise NotImplementedError(
            "No pack for locally factorable verification strategy."
        )

    def __str__(self) -> str:
        return "locally factorable verification"


class ElementaryVerificationStrategy(TileScopeVerificationStrategy):
    """
    A tiling is elementary verified if it is locally factorable
    and has no interleaving cells.
    """

    VERIFICATION_CLASS = ElementaryEnumeration

    def pack(self) -> StrategyPack:
        raise InvalidOperationError("No pack for elementary verification strategy")

    def __str__(self) -> str:
        return "elementary verification"


class LocalVerificationStrategy(TileScopeVerificationStrategy):
    """
    The local verified strategy.

    A tiling is local verified if every obstruction and every requirement is
    localized, i.e. in a single cell and the tiling is not 1x1.
    """

    VERIFICATION_CLASS = LocalEnumeration

    def pack(self) -> StrategyPack:
        raise InvalidOperationError("Cannot get a specification for local verification")

    def get_specification(self, tiling: Tiling) -> CombinatorialSpecification:
        raise InvalidOperationError("Cannot get a specification for local verification")

    def __str__(self) -> str:
        return "local verification"


class MonotoneTreeVerificationStrategy(TileScopeVerificationStrategy):
    """
    Verify all tiling that is a monotone tree.
    """

    VERIFICATION_CLASS = MonotoneTreeEnumeration

    def pack(self) -> StrategyPack:
        raise InvalidOperationError(
            "Cannot get a specification for monotone tree verification"
        )

    def get_specification(self, tiling: Tiling) -> CombinatorialSpecification:
        raise InvalidOperationError(
            "Cannot get a specification for monotone tree verification"
        )

    def get_genf(self, tiling: Tiling) -> Expr:
        return self.VERIFICATION_CLASS(tiling).get_genf()

    def __str__(self) -> str:
        return "monotone tree verification"

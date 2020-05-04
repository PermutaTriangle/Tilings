from typing import Iterable, Iterator, Optional, Tuple, Type

from sympy import var

from comb_spec_searcher import (
    CombinatorialSpecification,
    Constructor,
    StrategyGenerator,
    VerificationStrategy,
)
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.exception import InvalidOperationError
from tilings.algorithms.enumeration import (
    DatabaseEnumeration,
    ElementaryEnumeration,
    Enumeration,
    LocalEnumeration,
    LocallyFactorableEnumeration,
    MonotoneTreeEnumeration,
    OneByOneEnumeration,
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


class BasicVerificationStrategy(VerificationStrategy):
    def verified(self, tiling: Tiling) -> bool:
        return tiling.is_epsilon() or tiling.is_point_tiling()

    @property
    def pack(self):
        raise InvalidOperationError("Cannot get a tree for a basic " "verification")

    def get_specfication(self, tiling: Tiling, **kwargs) -> CombinatorialSpecification:
        raise InvalidOperationError("Cannot get a tree for a basic " "verification")

    def get_genf(self, tiling: Tiling, **kwargs):
        if tiling.is_epsilon():
            return 1
        if tiling.is_point_tiling():
            return x
        raise InvalidOperationError("Not an atom")

    def count_objects_of_size(self, tiling: Tiling, **parameters):
        """Verification strategies must contain a method to count the objects."""
        if (parameters["n"] == 0 and tiling.is_epsilon()) or (
            parameters["n"] == 1 and tiling.is_point_tiling()
        ):
            return 1
        return 0

    def generate_objects_of_size(
        self, tiling: Tiling, **parameters
    ) -> Iterator[GriddedPerm]:
        """Verification strategies must contain a method to generate the objects."""
        if parameters["n"] == 0 and tiling.is_epsilon():
            yield GriddedPerm.empty_perm()
        elif parameters["n"] == 1 and tiling.is_point_tiling():
            yield GriddedPerm(Perm((0,)), ((0, 0),))

    def formal_step(self) -> str:
        return "tiling is an atom"

    def __repr__(self) -> str:
        return "{}(ignore_parent={})".format(
            self.__class__.__name__, self.ignore_parent
        )

    def __str__(self) -> str:
        return "verify atoms"

    @classmethod
    def from_dict(cls, d):
        return cls()


class TileScopeVerificationStrategy(VerificationStrategy):
    """
    Abstract verification strategy class the group the shared logic of
    verification strategy. Subclass need to have the class attribute
    `VERIFICATION_CLASS`.
    """

    # pylint: disable=E1102
    VERIFICATION_CLASS = NotImplemented  # type: Type[Enumeration]

    def __init__(self, ignore_parent: bool = True):
        super().__init__(ignore_parent=ignore_parent)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.VERIFICATION_CLASS is NotImplemented:
            raise NotImplementedError(
                "Need to define {}.VERIFICATION_CLASS".format(cls.__name__)
            )

    @property
    def pack(self, tiling: Tiling):
        return self.VERIFICATION_CLASS(tiling).pack

    def verified(self, tiling: Tiling):
        return self.VERIFICATION_CLASS(tiling).verified()

    def formal_step(self):
        return self.VERIFICATION_CLASS.formal_step

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d: dict) -> "TileScopeVerificationStrategy":
        return cls(ignore_parent=d["ignore_parent"])


class _OneByOneVerificationStrategy(TileScopeVerificationStrategy):
    def __init__(
        self,
        basis: Optional[Iterable[Perm]] = None,
        symmetry: bool = False,
        ignore_parent: bool = True,
    ):
        self.basis = tuple(basis)
        self.symmetry = symmetry
        super().__init__(ignore_parent=ignore_parent)

    VERIFICATION_CLASS = OneByOneEnumeration

    @property
    def pack(self):
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
        d = super().to_jsonable()
        d["basis"] = self.basis
        d["symmetry"] = self.symmetry
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AllCellInsertionStrategy":
        if d["basis"] is None:
            basis = None
        else:
            basis = [Perm(p) for p in d["basis"]]
        return cls(
            basis=basis, symmetry=d["symmetry"], ignore_parent=d["ignore_parent"],
        )


class OneByOneVerificationStrategy(StrategyGenerator):
    """Return a verification rule if one-by-one verified."""

    def __init__(self, ignore_parent: bool = True):
        self.ignore_parent = ignore_parent

    def __call__(
        self, tiling: Tiling, children: Tuple[Tiling, ...] = None, **kwargs
    ) -> "SpecificRule":
        if "basis" not in kwargs:
            raise TypeError("Missing basis argument")
        basis = kwargs["basis"]  # type: Iterable[Perm]
        symmetry = kwargs.get("symmetry", False)
        return [
            _OneByOneVerificationStrategy(
                basis=basis, symmetry=symmetry, ignore_parent=self.ignore_parent
            )
        ]

    def __str__(self):
        return "one by one verification"

    def __repr__(self):
        return self.__class__.__name__ + "()"

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["ignore_parent"] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(ignore_parent=d["ignore_parent"])


class DatabaseVerificationStrategy(TileScopeVerificationStrategy):
    """Verify a tiling that is in the database"""

    VERIFICATION_CLASS = DatabaseEnumeration

    @property
    def pack(self):
        raise InvalidOperationError(
            "Cannot get a specification for database verification"
        )

    def get_specification(self, tiling: Tiling) -> CombinatorialSpecification:
        raise InvalidOperationError(
            "Cannot get a specification for database verification"
        )

    def get_genf(self, tiling: Tiling):
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

    @property
    def pack(self):
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

    @property
    def pack(self):
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

    @property
    def pack(self):
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

    @property
    def pack(self):
        raise InvalidOperationError(
            "Cannot get a specification for monotone tree verification"
        )

    def get_specification(self, tiling: Tiling) -> CombinatorialSpecification:
        raise InvalidOperationError(
            "Cannot get a specification for monotone tree verification"
        )

    def get_genf(self, tiling: Tiling):
        return self.VERIFICATION_CLASS(tiling).get_genf()

    def __str__(self) -> str:
        return "monotone tree verification"

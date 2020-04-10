from typing import Iterable, Optional, Type

from comb_spec_searcher import Rule, VerificationRule
from permuta import Perm
from tilings import Tiling
from tilings.algorithms.enumeration import (
    BasicEnumeration,
    DatabaseEnumeration,
    ElementaryEnumeration,
    Enumeration,
    LocalEnumeration,
    LocallyFactorableEnumeration,
    MonotoneTreeEnumeration,
    OneByOneEnumeration,
)
from tilings.strategies.abstract_strategy import Strategy

__all__ = [
    "BasicVerificationStrategy",
    "OneByOneVerificationStrategy",
    "DatabaseVerificationStrategy",
    "LocallyFactorableVerificationStrategy",
    "ElementaryVerificationStrategy",
    "LocalVerificationStrategy",
    "MonotoneTreeVerificationStrategy",
    "FakeVerificationStrategy",
]


class _VerificationStrategy(Strategy):
    """
    Abstract verification strategy class the group the shared logic of
    verification strategy. Subclass need to have the class attribute
    `VERIFICATION_CLASS`.
    """

    # pylint: disable=E1102
    VERIFICATION_CLASS = NotImplemented  # type: Type[Enumeration]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.VERIFICATION_CLASS is NotImplemented:
            raise NotImplementedError(
                "Need to define {}.VERIFICATION_CLASS".format(cls.__name__)
            )

    def __call__(self, tiling: Tiling, **kwargs) -> Optional[Rule]:
        return self.VERIFICATION_CLASS(tiling).verification_rule()

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d: dict) -> "_VerificationStrategy":
        return cls()


class BasicVerificationStrategy(_VerificationStrategy):
    """Verify the most basics tilings."""

    VERIFICATION_CLASS = BasicEnumeration

    def __str__(self) -> str:
        return "basic verification"


class OneByOneVerificationStrategy(_VerificationStrategy):
    """Return a verification if one-by-one verified."""

    VERIFICATION_CLASS = OneByOneEnumeration

    def __call__(self, tiling: Tiling, **kwargs):
        if "basis" not in kwargs:
            raise TypeError("Missing basis argument")
        basis = kwargs["basis"]  # type: Iterable[Perm]
        return self.VERIFICATION_CLASS(tiling, basis).verification_rule()

    def __str__(self) -> str:
        return "one by one verification"


class DatabaseVerificationStrategy(_VerificationStrategy):
    """Verify a tiling that is in the database"""

    VERIFICATION_CLASS = DatabaseEnumeration

    def __str__(self) -> str:
        return "database verification"


class LocallyFactorableVerificationStrategy(_VerificationStrategy):
    """
    The locally factorable verified strategy.

    A tiling is locally factorable if every requirement and obstruction is
    non-interleaving, i.e. use a single cell in each row and column.
    """

    VERIFICATION_CLASS = LocallyFactorableEnumeration

    def __str__(self) -> str:
        return "locally factorable verification"


class ElementaryVerificationStrategy(_VerificationStrategy):
    """
    A tiling is elementary verified if it is locally factorable
    and has no interleaving cells.
    """

    VERIFICATION_CLASS = ElementaryEnumeration

    def __str__(self) -> str:
        return "elementary verification"


class LocalVerificationStrategy(_VerificationStrategy):
    """
    The local verified strategy.

    A tiling is local verified if every obstruction and every requirement is
    localized, i.e. in a single cell and the tiling is not 1x1.
    """

    VERIFICATION_CLASS = LocalEnumeration

    def __str__(self) -> str:
        return "local verification"


class MonotoneTreeVerificationStrategy(_VerificationStrategy):
    """
    Verify all tiling that is a monotone tree.
    """

    VERIFICATION_CLASS = MonotoneTreeEnumeration

    def __str__(self) -> str:
        return "monotone tree verification"


class FakeVerificationStrategy(Strategy):
    """
    Automatically verify all the tilings that are given
    """

    def __init__(self, tilings: Iterable[Tiling]):
        self.tilings = frozenset(tilings)

    def __call__(self, tiling: Tiling, **kwargs) -> Optional[Rule]:
        if tiling in self.tilings:
            print(tiling)
            return VerificationRule("fake verify")
        return None

    def __repr__(self) -> str:
        return "FakeVerify({})".format(self.tilings)

    def __str__(self) -> str:
        return "fake verification of {} tilings".format(len(self.tilings))

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["tilings"] = list(t.to_jsonable() for t in self.tilings)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "FakeVerificationStrategy":
        tilings = [Tiling.from_dict(t) for t in d["tilings"]]
        return cls(tilings)

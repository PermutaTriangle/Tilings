from typing import Iterable, List, Optional, Tuple, Type, TypeVar

from comb_spec_searcher import VerificationStrategy
from permuta import Perm
from permuta.permutils.symmetry import all_symmetry_sets
from tilings import GriddedPerm, Tiling

__all__ = [
    "BasisAwareVerificationStrategy",
]


BasisAwareVerificationStrategyType = TypeVar(
    "BasisAwareVerificationStrategyType", bound="BasisAwareVerificationStrategy"
)


class BasisAwareVerificationStrategy(VerificationStrategy[Tiling, GriddedPerm]):
    """
    A base class for a verification strategy that needs to know the basis the
    Tilescope is currently running.
    """

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
            self.symmetries = frozenset(
                frozenset(b) for b in all_symmetry_sets(self._basis)
            )
        else:
            self.symmetries = frozenset([frozenset(self._basis)])
        super().__init__(ignore_parent=ignore_parent)

    def change_basis(
        self: BasisAwareVerificationStrategyType, basis: Iterable[Perm], symmetry: bool
    ) -> BasisAwareVerificationStrategyType:
        """
        Return a new version of the verification strategy with the given basis instead
        of the current one.
        """
        basis = tuple(basis)
        return self.__class__(basis, symmetry, self.ignore_parent)

    @property
    def basis(self) -> Tuple[Perm, ...]:
        return self._basis

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["basis"] = self._basis
        d["symmetry"] = self._symmetry
        return d

    @classmethod
    def from_dict(
        cls: Type[BasisAwareVerificationStrategyType], d: dict
    ) -> BasisAwareVerificationStrategyType:
        if "basis" in d and d["basis"] is not None:
            basis: Optional[List[Perm]] = [Perm(p) for p in d.pop("basis")]
        else:
            basis = d.pop("basis", None)
        return cls(basis=basis, **d)

    def __repr__(self) -> str:
        args = ", ".join(
            [
                f"basis={self._basis}",
                f"symmetry={self._symmetry}",
                f"ignore_parent={self.ignore_parent}",
            ]
        )
        return f"{self.__class__.__name__}({args})"

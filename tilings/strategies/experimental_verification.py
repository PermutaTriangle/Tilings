"""
This file contains "experimental" verification strategies, which are those that verify
tilings for which we are not certain we can independently calculate their counting
sequence or generating function.
"""

from typing import Iterable, Iterator, Optional, Tuple

from comb_spec_searcher import StrategyFactory, VerificationStrategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import VerificationRule
from permuta import Av, Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Factor, SubclassVerificationAlgorithm

from .abstract import BasisAwareVerificationStrategy

__all__ = [
    "NonemptyCellVerificationStrategy",
    "NoRootCellVerificationStrategy",
    "ShortObstructionVerificationStrategy",
    "SubclassVerificationFactory",
]

TileScopeVerificationStrategy = VerificationStrategy[Tiling, GriddedPerm]


class NoRootCellVerificationStrategy(BasisAwareVerificationStrategy):
    """
    A strategy to mark as verified any tiling that does not contain the root
    basis localized in a cell. Tilings with dimensions 1x1 are ignored.
    """

    def verified(self, comb_class: Tiling):
        return comb_class.dimensions != (1, 1) and all(
            frozenset(obs) not in self.symmetries
            for obs, _ in comb_class.cell_basis().values()
        )

    def formal_step(self) -> str:
        basis = ", ".join(str(p) for p in self.basis)
        return f"tiling has no Av({basis}) cell"

    def __str__(self) -> str:
        basis = ", ".join(str(p) for p in self.basis)
        return f"no Av({basis}) cell verification"


class NonemptyCellVerificationStrategy(BasisAwareVerificationStrategy):
    """
    A strategy to mark as verified any tiling with fewer than a preset
    number of nonempty cell. Possibly useful when search for a spec for a
    non-1x1 tiling.
    """

    def __init__(
        self,
        allowed_nonempty_cells: int,
        symmetry: bool = False,
        ignore_parent: bool = True,
    ):
        self.allowed_nonempty_cells = allowed_nonempty_cells
        super().__init__(symmetry=symmetry, ignore_parent=ignore_parent)

    def verified(self, comb_class: Tiling):
        """
        verifies any tiling with at most [allowed_nonempty_cells] nonempty cells.
        """
        return len(comb_class.active_cells) <= self.allowed_nonempty_cells

    def formal_step(self) -> str:
        return f"tiling has at most {self.allowed_nonempty_cells} nonempty cells"

    def __str__(self) -> str:
        return f"at most {self.allowed_nonempty_cells} nonempty cells verification"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(allowed_nonempty_cells="
            f"{self.allowed_nonempty_cells})"
        )

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["allowed_nonempty_cells"] = self.allowed_nonempty_cells
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ShortObstructionVerificationStrategy":
        allowed_nonempty_cells: int = d.pop("allowed_nonempty_cells")
        return cls(allowed_nonempty_cells=allowed_nonempty_cells, **d)


class ShortObstructionVerificationStrategy(BasisAwareVerificationStrategy):
    """
    A strategy to mark as verified any tiling whose crossing obstructions all have
    size at most 3. Tilings with dimensions 1x1 are ignored.
    """

    def __init__(
        self,
        short_length: int = 3,
        basis: Optional[Iterable[Perm]] = None,
        symmetry: bool = False,
        ignore_parent: bool = True,
    ):
        self.short_length = short_length
        super().__init__(basis=basis, symmetry=symmetry, ignore_parent=ignore_parent)

    def verified(self, comb_class: Tiling):
        return comb_class.dimensions != (1, 1) and all(
            ob.is_single_cell() or len(ob) <= self.short_length
            for ob in comb_class.obstructions
        )

    def change_basis(
        self, basis: Iterable[Perm], symmetry: bool
    ) -> "ShortObstructionVerificationStrategy":
        """
        Return a new version of the verification strategy with the given basis instead
        of the current one.
        """
        basis = tuple(basis)
        return ShortObstructionVerificationStrategy(
            self.short_length, basis, symmetry, self.ignore_parent
        )

    def formal_step(self) -> str:
        return f"tiling has short (length <= {self.short_length}) crossing obstructions"

    def decomposition_function(
        self, comb_class: Tiling
    ) -> Optional[Tuple[Tiling, ...]]:
        """
        The rule as the root as children if one of the cell of the tiling is the root.
        """
        if self.verified(comb_class):
            if not self.basis:
                return ()
            for obs, _ in comb_class.cell_basis().values():
                if frozenset(obs) in self.symmetries:
                    return (Tiling.from_perms(self.basis),)
            return ()
        return None

    def shifts(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[int, ...]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply
        if children:
            return (0,)
        return ()

    def __str__(self) -> str:
        return (
            f"short (length <= {self.short_length}) crossing obstruction verification"
        )

    def __repr__(self) -> str:
        args = ", ".join(
            [
                f"basis={self._basis}",
                f"short_length={self.short_length}",
                f"ignore_parent={self.ignore_parent}",
            ]
        )
        return f"{self.__class__.__name__}({args})"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["short_length"] = self.short_length
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ShortObstructionVerificationStrategy":
        if "basis" in d and d["basis"] is not None:
            basis: Optional[Tuple[Perm, ...]] = tuple(Perm(p) for p in d.pop("basis"))
        else:
            basis = d.pop("basis", None)
        return cls(basis=basis, **d)


class SubclassVerificationStrategy(TileScopeVerificationStrategy):
    """
    A strategy object for holding the results of SubclassVerification
    """

    def __init__(self, subclass_basis=Iterable[Perm], ignore_parent: bool = True):
        self.subclass_basis = tuple(sorted(subclass_basis))
        super().__init__(ignore_parent=ignore_parent)

    def verified(self, comb_class: Tiling) -> bool:
        algo = SubclassVerificationAlgorithm(comb_class, set(self.subclass_basis))
        return algo.subclasses == self.subclass_basis

    def formal_step(self) -> str:
        return f"tiling is contained in the subclass {Av(self.subclass_basis)}"

    def __str__(self) -> str:
        return "subclass verification strategy"

    def __repr__(self):
        args = ", ".join(
            [
                f"subclass_basis={self.subclass_basis}",
                f"ignore_parent={self.ignore_parent}",
            ]
        )
        return f"{self.__class__.__name__}({args})"

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

    def __call__(self, comb_class: Tiling) -> Iterator[VerificationRule]:
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
        return f"{self.__class__.__name__}(perms_to_check={self.perms_to_check})"

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

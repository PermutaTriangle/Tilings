from collections import Counter, defaultdict
from functools import reduce
from itertools import chain
from operator import mul
from typing import Dict, Iterable, Iterator, List, Optional, Tuple, cast

from sympy import Expr, Function, var

from comb_spec_searcher import (
    AtomStrategy,
    CombinatorialClass,
    StrategyPack,
    VerificationStrategy,
)
from comb_spec_searcher.exception import InvalidOperationError, StrategyDoesNotApply
from comb_spec_searcher.typing import Objects, Terms
from permuta import Perm
from permuta.permutils import (
    is_insertion_encodable_maximum,
    is_insertion_encodable_rightmost,
)
from permuta.permutils.symmetry import all_symmetry_sets
from tilings import GriddedPerm, Tiling
from tilings.algorithms.enumeration import (
    DatabaseEnumeration,
    LocalEnumeration,
    MonotoneTreeEnumeration,
)
from tilings.assumptions import ComponentAssumption
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


TileScopeVerificationStrategy = VerificationStrategy[Tiling, GriddedPerm]


class BasicVerificationStrategy(AtomStrategy):
    """
    TODO: can this be moved to the CSS atom strategy?
    """

    @staticmethod
    def get_terms(comb_class: CombinatorialClass, n: int) -> Terms:
        if not isinstance(comb_class, Tiling):
            raise NotImplementedError
        gp = next(comb_class.minimal_gridded_perms())
        if n == len(gp):
            parameters = tuple(
                assumption.get_value(gp) for assumption in comb_class.assumptions
            )
            return Counter([parameters])
        return Counter()

    @staticmethod
    def get_objects(comb_class: CombinatorialClass, n: int) -> Objects:
        if not isinstance(comb_class, Tiling):
            raise NotImplementedError
        res: Objects = defaultdict(list)
        gp = next(comb_class.minimal_gridded_perms())
        if n == len(gp):
            parameters = tuple(
                assumption.get_value(gp) for assumption in comb_class.assumptions
            )
            res[parameters].append(gp)
        return res

    @staticmethod
    def generate_objects_of_size(
        comb_class: CombinatorialClass, n: int, **parameters: int
    ) -> Iterator[GriddedPerm]:
        """
        Verification strategies must contain a method to generate the objects.
        """
        yield from comb_class.objects_of_size(n, **parameters)

    @staticmethod
    def random_sample_object_of_size(
        comb_class: CombinatorialClass, n: int, **parameters: int
    ) -> GriddedPerm:
        """
        Verification strategies must contain a method to sample the objects.
        """
        key = tuple(y for _, y in sorted(parameters.items()))
        if BasicVerificationStrategy.get_terms(comb_class, n).get(key):
            return cast(GriddedPerm, next(comb_class.objects_of_size(n, **parameters)))

    def get_genf(
        self,
        comb_class: CombinatorialClass,
        funcs: Optional[Dict[CombinatorialClass, Function]] = None,
    ) -> Expr:
        if not self.verified(comb_class):
            raise StrategyDoesNotApply("Can't find generating functon for non-atom.")
        if not isinstance(comb_class, Tiling):
            raise NotImplementedError
        cast(Tiling, comb_class)
        gp = next(comb_class.minimal_gridded_perms())
        expected = {"x": len(gp)}
        for assumption in comb_class.assumptions:
            expected[
                comb_class.get_assumption_parameter(assumption)
            ] = assumption.get_value(gp)
        return reduce(mul, [var(k) ** n for k, n in expected.items()], 1)


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
        self, basis: Iterable[Perm], symmetry: bool
    ) -> "OneByOneVerificationStrategy":
        """
        Return a new version of the verfication strategy with the given basis instead of
        the current one.
        """
        basis = tuple(basis)
        return self.__class__(basis, symmetry, self.ignore_parent)

    @property
    def basis(self) -> Tuple[Perm, ...]:
        return self._basis

    @staticmethod
    def pack(tiling: Tiling) -> StrategyPack:
        if any(isinstance(ass, ComponentAssumption) for ass in tiling.assumptions):
            raise InvalidOperationError(
                "Can't find generating function with component assumption."
            )
        # pylint: disable=import-outside-toplevel
        from tilings.tilescope import TileScopePack

        assert tiling.dimensions == (1, 1)
        basis, _ = tiling.cell_basis()[(0, 0)]
        if any(
            any(p.contains(patt) for patt in basis)
            for p in [
                Perm((0, 2, 1)),
                Perm((1, 2, 0)),
                Perm((1, 0, 2)),
                Perm((2, 0, 1)),
            ]
        ):
            # subclass of Av(231) or a symmetry, use point placements!
            return TileScopePack.point_and_row_and_col_placements().add_verification(
                BasicVerificationStrategy(), replace=True
            )
        if is_insertion_encodable_maximum(basis):
            return TileScopePack.regular_insertion_encoding(3)
        if is_insertion_encodable_rightmost(basis):
            return TileScopePack.regular_insertion_encoding(2)
        # if it is the class or positive class
        if not tiling.requirements or (
            len(tiling.requirements) == 1
            and len(tiling.requirements[0]) == 1
            and len(tiling.requirements[0][0]) <= 2
        ):
            if basis in ([Perm((0, 1, 2))], [Perm((2, 1, 0))]):
                # Av(123) or Av(321) - use fusion!
                return (
                    TileScopePack.row_and_col_placements(row_only=True)
                    .make_fusion(tracked=True)
                    .fix_one_by_one(basis)
                )
            if (Perm((0, 1, 2)) in basis or Perm((2, 1, 0)) in basis) and all(
                len(p) <= 4 for p in basis
            ):
                # is a subclass of Av(123) avoiding patterns of length <= 4
                # experimentally showed that such clsses always terminates
                return TileScopePack.row_and_col_placements().fix_one_by_one(basis)
        raise InvalidOperationError(
            "Cannot get a specification for one by one verification for "
            f"subclass Av({basis})"
        )

    def verified(self, tiling: Tiling) -> bool:
        return tiling.dimensions == (1, 1) and (
            frozenset(ob.patt for ob in tiling.obstructions) not in self.symmetries
            or any(isinstance(ass, ComponentAssumption) for ass in tiling.assumptions)
        )

    def get_genf(
        self, tiling: Tiling, funcs: Optional[Dict[Tiling, Function]] = None
    ) -> Expr:
        if not self.verified(tiling):
            raise StrategyDoesNotApply("tiling not 1x1 verified")
        if len(tiling.obstructions) == 1 and tiling.obstructions[0] in (
            GriddedPerm.single_cell((0, 1, 2), (0, 0)),
            GriddedPerm.single_cell((2, 1, 0), (0, 0)),
        ):
            return LocalEnumeration(tiling).get_genf(funcs=funcs)
        try:
            return super().get_genf(tiling, funcs)
        except InvalidOperationError:
            return LocalEnumeration(tiling).get_genf(funcs=funcs)

    @staticmethod
    def formal_step() -> str:
        return "tiling is a subclass of the original tiling"

    @staticmethod
    def get_terms(comb_class: Tiling, n: int) -> Terms:
        raise NotImplementedError(
            "Not implemented method to count objects for one by one verified tilings"
        )

    def generate_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError(
            "Not implemented method to generate objects for one by one "
            "verified tilings"
        )

    def random_sample_object_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> GriddedPerm:
        raise NotImplementedError(
            "Not implemented random sample for one by one verified tilings"
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
    def pack(tiling: Tiling) -> StrategyPack:
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

    def get_genf(
        self, tiling: Tiling, funcs: Optional[Dict[Tiling, Function]] = None
    ) -> Expr:
        if not self.verified(tiling):
            raise StrategyDoesNotApply("tiling is not in the database")
        return DatabaseEnumeration(tiling).get_genf()

    @staticmethod
    def get_terms(comb_class: Tiling, n: int) -> Terms:
        raise NotImplementedError(
            "Not implemented method to count objects for database verified tilings"
        )

    def generate_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError(
            "Not implemented method to generate objects for database verified tilings"
        )

    def random_sample_object_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> GriddedPerm:
        raise NotImplementedError(
            "Not implemented random sample for database verified tilings"
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
    def pack(tiling: Tiling) -> StrategyPack:
        if any(isinstance(ass, ComponentAssumption) for ass in tiling.assumptions):
            raise InvalidOperationError(
                "Can't find generating function with component assumption."
            )
        return StrategyPack(
            name="LocallyFactorable",
            initial_strats=[FactorFactory(), RequirementCorroborationFactory()],
            inferral_strats=[],
            expansion_strats=[[FactorInsertionFactory()]],
            ver_strats=[
                BasicVerificationStrategy(),
                OneByOneVerificationStrategy(),
                InsertionEncodingVerificationStrategy(),
                MonotoneTreeVerificationStrategy(no_factors=True),
                LocalVerificationStrategy(no_factors=True),
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

    def __init__(self, ignore_parent: bool = True, no_factors: bool = False):
        self.no_factors = no_factors
        super().__init__(ignore_parent=ignore_parent)

    def pack(self, tiling: Tiling) -> StrategyPack:
        try:
            return InsertionEncodingVerificationStrategy().pack(tiling)
        except StrategyDoesNotApply:
            pass
        if self.no_factors:
            raise InvalidOperationError("Cannot get a simpler specification")
        if (
            any(isinstance(ass, ComponentAssumption) for ass in tiling.assumptions)
            and len(tiling.find_factors()) == 1
        ):
            raise InvalidOperationError(
                "Can't find generating function with component assumption."
            )
        return StrategyPack(
            initial_strats=[FactorFactory()],
            inferral_strats=[],
            expansion_strats=[],
            ver_strats=[
                BasicVerificationStrategy(),
                OneByOneVerificationStrategy(),
                InsertionEncodingVerificationStrategy(),
                MonotoneTreeVerificationStrategy(no_factors=True),
                LocalVerificationStrategy(no_factors=True),
            ],
            name="factor pack",
        )

    def verified(self, tiling: Tiling) -> bool:
        return (
            tiling.dimensions != (1, 1)
            and (not self.no_factors or len(tiling.find_factors()) == 1)
            and LocalEnumeration(tiling).verified()
        )

    @staticmethod
    def formal_step() -> str:
        return "tiling is locally enumerable"

    @classmethod
    def from_dict(cls, d: dict) -> "LocalVerificationStrategy":
        return cls(**d)

    def get_genf(
        self, tiling: Tiling, funcs: Optional[Dict[Tiling, Function]] = None
    ) -> Expr:
        if not self.verified(tiling):
            raise StrategyDoesNotApply("tiling not locally verified")
        if len(tiling.obstructions) == 1 and tiling.obstructions[0] in (
            GriddedPerm.single_cell((0, 1, 2), (0, 0)),
            GriddedPerm.single_cell((2, 1, 0), (0, 0)),
        ):
            return LocalEnumeration(tiling).get_genf(funcs=funcs)
        try:
            return super().get_genf(tiling, funcs)
        except InvalidOperationError:
            return LocalEnumeration(tiling).get_genf(funcs=funcs)

    @staticmethod
    def get_terms(comb_class: Tiling, n: int) -> Terms:
        raise NotImplementedError(
            "Not implemented method to count objects for locally verified tilings"
        )

    def generate_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError(
            "Not implemented method to generate objects for locally verified tilings"
        )

    def random_sample_object_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> GriddedPerm:
        raise NotImplementedError(
            "Not implemented random sample for locally verified tilings"
        )

    def __str__(self) -> str:
        return "local verification"


class InsertionEncodingVerificationStrategy(TileScopeVerificationStrategy):
    """
    Verify all n x 1 and 1 x n tilings that have a regular insertion encoding.
    """

    def __init__(self, ignore_parent: bool = True):
        super().__init__(ignore_parent=ignore_parent)

    def pack(self, tiling: Tiling) -> StrategyPack:
        if any(isinstance(ass, ComponentAssumption) for ass in tiling.assumptions):
            raise InvalidOperationError(
                "Can't find generating function with component assumption."
            )
        # pylint: disable=import-outside-toplevel
        from tilings.strategy_pack import TileScopePack

        if self.has_rightmost_insertion_encoding(tiling):
            return TileScopePack.regular_insertion_encoding(2)
        if self.has_topmost_insertion_encoding(tiling):
            return TileScopePack.regular_insertion_encoding(3)
        raise StrategyDoesNotApply("tiling does not has a regular insertion encoding")

    @staticmethod
    def has_rightmost_insertion_encoding(tiling: Tiling) -> bool:
        return tiling.dimensions[0] == 1 and all(
            is_insertion_encodable_rightmost(basis)
            for basis, _ in tiling.cell_basis().values()
        )

    @staticmethod
    def has_topmost_insertion_encoding(tiling: Tiling) -> bool:
        return tiling.dimensions[1] == 1 and all(
            is_insertion_encodable_maximum(basis)
            for basis, _ in tiling.cell_basis().values()
        )

    def verified(self, tiling: Tiling) -> bool:
        return self.has_rightmost_insertion_encoding(
            tiling
        ) or self.has_topmost_insertion_encoding(tiling)

    @staticmethod
    def formal_step() -> str:
        return "tiling has a regular insertion encoding"

    @classmethod
    def from_dict(cls, d: dict) -> "InsertionEncodingVerificationStrategy":
        return cls(**d)

    @staticmethod
    def get_terms(comb_class: Tiling, n: int) -> Terms:
        raise NotImplementedError(
            "Not implemented method to count objects for insertion encoding "
            "verified tilings"
        )

    def generate_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError(
            "Not implemented method to generate objects for insertion encoding "
            "verified tilings"
        )

    def random_sample_object_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> GriddedPerm:
        raise NotImplementedError(
            "Not implemented random sample for insertion encoding verified tilings"
        )

    def __str__(self) -> str:
        return "insertion encoding verified"


class MonotoneTreeVerificationStrategy(TileScopeVerificationStrategy):
    """
    Verify all tiling that is a monotone tree.
    """

    def __init__(self, ignore_parent: bool = True, no_factors: bool = True):
        self.no_factors = no_factors
        super().__init__(ignore_parent=ignore_parent)

    def pack(self, tiling: Tiling) -> StrategyPack:
        if any(isinstance(ass, ComponentAssumption) for ass in tiling.assumptions):
            raise InvalidOperationError(
                "Can't find generating function with component assumption."
            )
        try:
            return InsertionEncodingVerificationStrategy().pack(tiling)
        except StrategyDoesNotApply:
            pass
        if self.no_factors:
            raise InvalidOperationError(
                "Cannot get a specification for a tiling in the database"
            )
        return StrategyPack(
            initial_strats=[FactorFactory()],
            inferral_strats=[],
            expansion_strats=[],
            ver_strats=[
                BasicVerificationStrategy(),
                OneByOneVerificationStrategy(),
                InsertionEncodingVerificationStrategy(),
                MonotoneTreeVerificationStrategy(no_factors=True),
            ],
            name="factor pack",
        )

    def verified(self, tiling: Tiling) -> bool:
        return (
            not self.no_factors or len(tiling.find_factors()) == 1
        ) and MonotoneTreeEnumeration(tiling).verified()

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
            raise StrategyDoesNotApply("tiling not locally verified")
        try:
            return super().get_genf(tiling, funcs)
        except InvalidOperationError:
            return MonotoneTreeEnumeration(tiling).get_genf(funcs=funcs)

    @staticmethod
    def get_terms(comb_class: Tiling, n: int) -> Terms:
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

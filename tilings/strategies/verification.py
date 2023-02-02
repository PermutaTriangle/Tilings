from collections import Counter, defaultdict
from functools import reduce
from itertools import chain
from operator import mul
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Tuple, cast

import requests
from sympy import Eq, Expr, Function, Symbol, collect, degree, solve, sympify, var

from comb_spec_searcher import (
    AtomStrategy,
    CombinatorialClass,
    CombinatorialSpecification,
    StrategyPack,
    VerificationStrategy,
)
from comb_spec_searcher.exception import InvalidOperationError, StrategyDoesNotApply
from comb_spec_searcher.strategies import VerificationRule
from comb_spec_searcher.typing import Objects, Terms
from permuta import Av, Perm
from permuta.permutils import (
    is_insertion_encodable_maximum,
    is_insertion_encodable_rightmost,
    lex_min,
)
from tilings import GriddedPerm, Tiling
from tilings.algorithms import locally_factorable_shift
from tilings.algorithms.enumeration import (
    DatabaseEnumeration,
    LocalEnumeration,
    MonotoneTreeEnumeration,
)
from tilings.assumptions import ComponentAssumption, TrackingAssumption
from tilings.strategies import (
    DetectComponentsStrategy,
    FactorFactory,
    FactorInsertionFactory,
    RemoveRequirementFactory,
    RequirementCorroborationFactory,
    SymmetriesFactory,
)

from .abstract import BasisAwareVerificationStrategy

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

    def get_terms(self, comb_class: CombinatorialClass, n: int) -> Terms:
        if not isinstance(comb_class, Tiling):
            raise NotImplementedError
        gp = next(comb_class.minimal_gridded_perms())
        if n == len(gp):
            parameters = tuple(
                assumption.get_value(gp) for assumption in comb_class.assumptions
            )
            return Counter([parameters])
        return Counter()

    def get_objects(self, comb_class: CombinatorialClass, n: int) -> Objects:
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

    def random_sample_object_of_size(
        self, comb_class: CombinatorialClass, n: int, **parameters: int
    ) -> GriddedPerm:
        """
        Verification strategies must contain a method to sample the objects.
        """
        key = tuple(y for _, y in sorted(parameters.items()))
        if BasicVerificationStrategy().get_terms(comb_class, n).get(key):
            return cast(GriddedPerm, next(comb_class.objects_of_size(n, **parameters)))
        raise (
            NotImplementedError(
                "Verification strategy did not contain a method to sample the objects"
            )
        )

    def get_genf(
        self,
        comb_class: CombinatorialClass,
        funcs: Optional[Dict[CombinatorialClass, Function]] = None,
    ) -> Any:
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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class OneByOneVerificationRule(VerificationRule[Tiling, GriddedPerm]):
    def get_equation(
        self,
        get_function: Callable[[Tiling], Function],
        funcs: Optional[Dict[Tiling, Function]] = None,
    ) -> Eq:
        # Find the minimal polynomial for the underlying class
        basis = [ob.patt for ob in self.comb_class.obstructions]
        basis_str = "_".join(map(str, lex_min(basis)))
        uri = f"https://permpal.com/perms/raw_data_json/basis/{basis_str}"
        request = requests.get(uri, timeout=10)
        if request.status_code == 404:
            return super().get_equation(get_function, funcs)
        data = request.json()
        min_poly = data["min_poly_maple"]
        if min_poly is None:
            return Eq(
                get_function(self.comb_class),
                self.tiling_to_symbol_eq(self.comb_class),
            )
        min_poly = min_poly.replace("^", "**").replace("F(x)", "F")
        lhs, _ = min_poly.split("=")
        # We now need to worry about the requirements. The min poly we got is
        # for the class with requirements.
        eq = Eq(self.without_req_genf(self.comb_class), get_function(self.comb_class))
        subs = solve([eq], var("F"), dict=True)[0]
        if self.comb_class.assumptions:
            subs["x"] = var("x") * var("k_0")
        res, _ = sympify(lhs).subs(subs, simultaneous=True).as_numer_denom()
        # Pick the unique factor that contains F
        for factor in res.as_ordered_factors():
            if factor.atoms(Function):
                res = factor
        # currently we have 0 = rhs,
        lhs = get_function(self.comb_class)
        if degree(res, lhs) == 1:
            # solve for rational gf
            rhs = solve([Eq(res, 0)], lhs, dict=True)[0][lhs]
        else:
            # or add F to both sides
            rhs = collect(res + lhs, lhs)
        return Eq(lhs, rhs)

    def tiling_to_symbol_eq(self, tiling: Tiling) -> Any:
        """
        Find the equation for the tiling in terms of F_C's, where C are
        permutation classes.
        """
        if tiling.requirements:
            reqs = tiling.requirements[0]
            avoided = tiling.__class__(
                tiling.obstructions + reqs,
                tiling.requirements[1:],
                tiling.assumptions,
            )
            without = tiling.__class__(
                tiling.obstructions,
                tiling.requirements[1:],
                tiling.assumptions,
            )
            return self.tiling_to_symbol_eq(without) - self.tiling_to_symbol_eq(avoided)
        params = self.comb_class.extra_parameters
        x_var = "x"
        if params:
            assert len(params) == 1
            x_var += "*" + params[0]
        basis = [ob.patt for ob in tiling.obstructions]
        return Symbol(f"F_{Av(basis)}({x_var})")

    @property
    def no_req_tiling(self) -> Tiling:
        return self.comb_class.__class__(
            self.comb_class.obstructions, tuple(), self.comb_class.assumptions
        )

    def without_req_genf(self, tiling: Tiling):
        """
        Find the equation for the tiling in terms of F, the generating
        function where the reqs are reomoved from tiling.
        """
        if tiling == self.no_req_tiling:
            return var("F")
        if tiling.requirements:
            reqs = tiling.requirements[0]
            avoided = tiling.__class__(
                tiling.obstructions + reqs,
                tiling.requirements[1:],
                tiling.assumptions,
            )
            without = tiling.__class__(
                tiling.obstructions,
                tiling.requirements[1:],
                tiling.assumptions,
            )
            avgf = self.without_req_genf(avoided)
            wogf = self.without_req_genf(without)
            return wogf - avgf
        return LocalEnumeration(tiling).get_genf()


class OneByOneVerificationStrategy(BasisAwareVerificationStrategy):
    def __init__(
        self,
        basis: Optional[Iterable[Perm]] = None,
        symmetry: bool = False,
        ignore_parent: bool = False,
    ):
        super().__init__(basis, symmetry, ignore_parent)
        self._spec: Dict[Tiling, CombinatorialSpecification] = {}

    @staticmethod
    def _spec_from_permpal(tiling: Tiling) -> CombinatorialSpecification:
        basis = [ob.patt for ob in tiling.obstructions]
        basis_str = "_".join(map(str, lex_min(basis)))
        uri = f"https://permpal.com/perms/raw_data_json/basis/{basis_str}"
        request = requests.get(uri, timeout=10)
        if request.status_code == 404:
            raise InvalidOperationError("Can't find spec for one by one verified rule.")
        data = request.json()
        spec_json = data["specs_and_eqs"][0]["spec_json"]
        spec = cast(
            CombinatorialSpecification, CombinatorialSpecification.from_dict(spec_json)
        )
        actual_class = Tiling(tiling.obstructions)
        if spec.root != actual_class:
            for strategy in SymmetriesFactory()(actual_class):
                rule = strategy(actual_class)
                if rule.children[0] == spec.root:
                    break
            else:
                raise InvalidOperationError("Error fixing sym in 1x1")
            rules = [rule] + list(spec.rules_dict.values())
            spec = CombinatorialSpecification(rule.comb_class, rules)
        assert spec.root == Tiling(tiling.obstructions)
        return spec

    def get_specification(
        self, comb_class: Tiling
    ) -> CombinatorialSpecification[Tiling, GriddedPerm]:
        if comb_class not in self._spec:
            try:
                self._spec[comb_class] = super().get_specification(comb_class)
            except InvalidOperationError as e:
                if len(comb_class.requirements) > 1 or comb_class.dimensions != (1, 1):
                    raise e
                self._spec[comb_class] = self._spec_from_permpal(comb_class)
        return self._spec[comb_class]

    def get_complement_spec(self, tiling: Tiling) -> CombinatorialSpecification:
        assert len(tiling.requirements) == 1
        complement = tiling.remove_requirement(tiling.requirements[0]).add_obstructions(
            tiling.requirements[0]
        )
        return self.get_specification(complement)

    def pack(self, comb_class: Tiling) -> StrategyPack:
        if any(isinstance(ass, ComponentAssumption) for ass in comb_class.assumptions):
            return ComponentVerificationStrategy().pack(comb_class)
        # pylint: disable=import-outside-toplevel
        from tilings.tilescope import TileScopePack

        assert comb_class.dimensions == (1, 1)
        basis, _ = comb_class.cell_basis()[(0, 0)]
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
        if not comb_class.requirements or (
            len(comb_class.requirements) == 1
            and len(comb_class.requirements[0]) == 1
            and len(comb_class.requirements[0][0]) <= 2
        ):
            if (
                (Perm((0, 1, 2)) in basis or Perm((2, 1, 0)) in basis)
                and all(len(p) <= 4 for p in basis)
                and len(basis) > 1
            ):
                # is a subclass of Av(123) avoiding patterns of length <= 4
                # experimentally showed that such clsses always terminates
                return TileScopePack.row_and_col_placements().add_basis(basis)
        raise InvalidOperationError(
            "Cannot get a specification for one by one verification for "
            f"subclass Av({basis})"
        )

    def __call__(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> OneByOneVerificationRule:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("The combinatorial class is not verified")
        return OneByOneVerificationRule(self, comb_class, children)

    def verified(self, comb_class: Tiling) -> bool:
        if not comb_class.dimensions == (1, 1):
            return False
        if not self.basis:
            return True
        tiling_class = Av([ob.patt for ob in comb_class.obstructions])
        sym_classes = (Av(sym) for sym in self.symmetries)
        is_strict_subclass = any(
            tiling_class.is_subclass(cls) and cls != tiling_class for cls in sym_classes
        )
        return is_strict_subclass

    def get_genf(
        self, comb_class: Tiling, funcs: Optional[Dict[Tiling, Function]] = None
    ) -> Any:
        if not self.verified(comb_class):
            raise StrategyDoesNotApply("tiling not 1x1 verified")
        if len(comb_class.obstructions) == 1 and comb_class.obstructions[0] in (
            GriddedPerm.single_cell((0, 1, 2), (0, 0)),
            GriddedPerm.single_cell((2, 1, 0), (0, 0)),
        ):
            return LocalEnumeration(comb_class).get_genf(funcs=funcs)
        try:
            return super().get_genf(comb_class, funcs)
        except InvalidOperationError:
            return LocalEnumeration(comb_class).get_genf(funcs=funcs)

    def formal_step(self) -> str:
        return "tiling is a subclass of the original tiling"

    def get_terms(self, comb_class: Tiling, n: int) -> Terms:
        terms = super().get_terms(comb_class.remove_assumptions(), n)
        if (
            comb_class.requirements
            and self.get_specification(comb_class).root != comb_class
        ):
            if len(comb_class.requirements) == 1:
                comp_spec = self.get_complement_spec(comb_class.remove_assumptions())
            else:
                raise NotImplementedError(
                    "Not implemented counting for one by one with two or more reqs"
                )
            comp_terms = comp_spec.get_terms(n)
            terms = Counter({tuple(): terms[tuple()] - comp_terms[tuple()]})
        if comb_class.assumptions:
            assert comb_class.assumptions == (TrackingAssumption.from_cells([(0, 0)]),)
            terms = Counter({(n,): terms[tuple()]})
        return terms

    def get_objects(self, comb_class: Tiling, n: int) -> Objects:
        objects = super().get_objects(comb_class, n)
        if comb_class.requirements:
            if len(comb_class.requirements) == 1:
                comp_spec = self.get_complement_spec(comb_class.remove_assumptions())
            else:
                raise NotImplementedError(
                    "Not implemented objects for one by one with two or more reqs"
                )
            comp_objects = comp_spec.get_objects(n)
            objects = defaultdict(
                list,
                {
                    a: list(set(b).difference(comp_objects[a]))
                    for a, b in objects.items()
                },
            )

        if comb_class.assumptions:
            assert comb_class.assumptions == (TrackingAssumption.from_cells([(0, 0)]),)
            objects = defaultdict(list, {(n,): objects[tuple()]})
        return objects

    def random_sample_object_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> GriddedPerm:
        if comb_class.assumptions:
            assert (
                len(comb_class.assumptions) == 1
                and parameters[
                    comb_class.get_assumption_parameter(comb_class.assumptions[0])
                ]
                == n
            )
        while True:
            # Rejection sampling
            gp = super().random_sample_object_of_size(
                Tiling(comb_class.obstructions), n
            )
            if gp in comb_class:
                return gp

    def __str__(self) -> str:
        if not self.basis:
            return "one by one verification"
        return f"One by one subclass of {Av(self.basis)}"


class ComponentVerificationStrategy(TileScopeVerificationStrategy):
    """Enumeration strategy for verifying 1x1s with component assumptions."""

    def pack(self, comb_class: Tiling) -> StrategyPack:
        raise InvalidOperationError("No pack for removing component assumption")

    def verified(self, comb_class: Tiling) -> bool:
        return comb_class.dimensions == (1, 1) and any(
            isinstance(ass, ComponentAssumption) for ass in comb_class.assumptions
        )

    def decomposition_function(
        self, comb_class: Tiling
    ) -> Optional[Tuple[Tiling, ...]]:
        """
        The rule as the root as children if one of the cell of the tiling is the root.
        """
        if self.verified(comb_class):
            return (comb_class.remove_assumptions(),)
        return None

    def shifts(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[int, ...]:
        return (0,)

    def formal_step(self) -> str:
        return "component verified"

    def get_genf(
        self, comb_class: Tiling, funcs: Optional[Dict[Tiling, Function]] = None
    ) -> Expr:
        raise NotImplementedError(
            "Not implemented method to count objects for component verified"
        )

    def get_terms(self, comb_class: Tiling, n: int) -> Terms:
        raise NotImplementedError(
            "Not implemented method to count objects for component verified"
        )

    def generate_objects_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> Iterator[GriddedPerm]:
        raise NotImplementedError(
            "Not implemented method to generate objects for component verified tilings"
        )

    def random_sample_object_of_size(
        self, comb_class: Tiling, n: int, **parameters: int
    ) -> GriddedPerm:
        raise NotImplementedError(
            "Not implemented random sample for component verified tilings"
        )

    def __str__(self) -> str:
        return "component verification"

    @classmethod
    def from_dict(cls, d: dict) -> "ComponentVerificationStrategy":
        return cls(**d)


class DatabaseVerificationStrategy(TileScopeVerificationStrategy):
    """
    Enumeration strategy for a tilings that are in the database.

    There is not always a specification for a tiling in the database but you
    can always find the generating function by looking up the database.
    """

    def pack(self, comb_class: Tiling) -> StrategyPack:
        # TODO: check database for tiling
        raise InvalidOperationError(
            "Cannot get a specification for a tiling in the database"
        )

    def verified(self, comb_class: Tiling):
        return DatabaseEnumeration(comb_class).verified()

    def formal_step(self) -> str:
        return "tiling is in the database"

    def get_genf(
        self, comb_class: Tiling, funcs: Optional[Dict[Tiling, Function]] = None
    ) -> Any:
        if not self.verified(comb_class):
            raise StrategyDoesNotApply("tiling is not in the database")
        return DatabaseEnumeration(comb_class).get_genf()

    def get_terms(self, comb_class: Tiling, n: int) -> Terms:
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


class LocallyFactorableVerificationStrategy(BasisAwareVerificationStrategy):
    """
    Verification strategy for a locally factorable tiling.

    A tiling is locally factorable if all its obstructions and requirements are
    locally factorable, i.e. each obstruction or requirement use at most one
    cell on each row and column. To be locally factorable, a tiling
    should not be equivalent to a 1x1 tiling.

    A locally factorable tiling can be describe with a specification with only subset
    verified tiling.
    """

    def pack(self, comb_class: Tiling) -> StrategyPack:
        return StrategyPack(
            name="LocallyFactorable",
            initial_strats=[
                FactorFactory(),
                RequirementCorroborationFactory(),
                DetectComponentsStrategy(),
            ],
            inferral_strats=[],
            expansion_strats=[[FactorInsertionFactory()], [RemoveRequirementFactory()]],
            ver_strats=[
                BasicVerificationStrategy(),
                OneByOneVerificationStrategy(
                    basis=self._basis, symmetry=self._symmetry
                ),
                ComponentVerificationStrategy(),
                InsertionEncodingVerificationStrategy(),
                MonotoneTreeVerificationStrategy(no_factors=True),
                LocalVerificationStrategy(no_factors=True),
            ],
        )

    @staticmethod
    def _pack_for_shift(comb_class: Tiling) -> StrategyPack:
        return StrategyPack(
            name="LocallyFactorable",
            initial_strats=[
                FactorFactory(),
                RequirementCorroborationFactory(),
                DetectComponentsStrategy(),
            ],
            inferral_strats=[],
            expansion_strats=[[FactorInsertionFactory()]],
            ver_strats=[
                BasicVerificationStrategy(),
                OneByOneVerificationStrategy(),
                ComponentVerificationStrategy(),
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

    def verified(self, comb_class: Tiling):
        return (
            not comb_class.dimensions == (1, 1)
            and self._locally_factorable_obstructions(comb_class)
            and self._locally_factorable_requirements(comb_class)
            and all(
                not isinstance(ass, ComponentAssumption)
                or (
                    len(ass.gps) == 1
                    and comb_class.only_cell_in_row_and_col(list(ass.cells)[0])
                )
                for ass in comb_class.assumptions
            )
        )

    def decomposition_function(
        self, comb_class: Tiling
    ) -> Optional[Tuple[Tiling, ...]]:
        """
        The rule as the root as children if one of the cell of the tiling is the root.
        """
        if self.verified(comb_class):
            if not self.basis:
                return ()
            pack = self._pack_for_shift(comb_class)
            sfs = locally_factorable_shift.shift_from_spec(
                comb_class, pack, self.symmetries
            )
            if sfs is not None:
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
        if not children:
            return ()
        pack = self._pack_for_shift(comb_class)
        shift = locally_factorable_shift.shift_from_spec(
            comb_class, pack, self.symmetries
        )
        assert shift is not None
        return (shift,)

    def formal_step(self) -> str:
        return "tiling is locally factorable"

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

    def verified(self, comb_class: Tiling):
        return (
            comb_class.fully_isolated()
            and not comb_class.dimensions == (1, 1)
            and all(
                len(ass.gps) == 1
                for ass in comb_class.assumptions
                if isinstance(ass, ComponentAssumption)
            )
        )

    def formal_step(self) -> str:
        return "tiling is elementary verified"

    @classmethod
    def from_dict(cls, d: dict) -> "ElementaryVerificationStrategy":
        return cls(**d)

    def __str__(self) -> str:
        return "elementary verification"


class LocalVerificationStrategy(BasisAwareVerificationStrategy):
    """
    The local verified strategy.

    A tiling is local verified if every obstruction and every requirement is
    localized, i.e. in a single cell and the tiling is not 1x1.
    """

    def __init__(
        self,
        basis: Optional[Iterable[Perm]] = None,
        symmetry: bool = False,
        ignore_parent: bool = False,
        no_factors: bool = False,
    ):
        self.no_factors = no_factors
        super().__init__(basis, symmetry, ignore_parent)

    def pack(self, comb_class: Tiling) -> StrategyPack:
        try:
            return InsertionEncodingVerificationStrategy().pack(comb_class)
        except StrategyDoesNotApply:
            pass
        if self.no_factors:
            raise InvalidOperationError(
                f"Cannot get a simpler specification for\n{comb_class}"
            )
        return StrategyPack(
            initial_strats=[FactorFactory(), DetectComponentsStrategy()],
            inferral_strats=[],
            expansion_strats=[],
            ver_strats=[
                BasicVerificationStrategy(),
                OneByOneVerificationStrategy(self.basis, self._symmetry),
                ComponentVerificationStrategy(),
                InsertionEncodingVerificationStrategy(),
                MonotoneTreeVerificationStrategy(no_factors=True),
                LocalVerificationStrategy(self.basis, self._symmetry, no_factors=True),
            ],
            name="factor pack",
        )

    def verified(self, comb_class: Tiling) -> bool:
        return (
            comb_class.dimensions != (1, 1)
            and (not self.no_factors or len(comb_class.find_factors()) == 1)
            and LocalEnumeration(comb_class).verified()
            and all(
                not isinstance(ass, ComponentAssumption)
                or (
                    len(ass.gps) == 1
                    and comb_class.only_cell_in_row_and_col(list(ass.cells)[0])
                )
                for ass in comb_class.assumptions
            )
        )

    def formal_step(self) -> str:
        return "tiling is locally enumerable"

    @classmethod
    def from_dict(cls, d: dict) -> "LocalVerificationStrategy":
        return cls(**d)

    def get_genf(
        self, comb_class: Tiling, funcs: Optional[Dict[Tiling, Function]] = None
    ) -> Any:
        if not self.verified(comb_class):
            raise StrategyDoesNotApply("tiling not locally verified")
        if len(comb_class.obstructions) == 1 and comb_class.obstructions[0] in (
            GriddedPerm.single_cell((0, 1, 2), (0, 0)),
            GriddedPerm.single_cell((2, 1, 0), (0, 0)),
        ):
            return LocalEnumeration(comb_class).get_genf(funcs=funcs)
        try:
            return super().get_genf(comb_class, funcs)
        except InvalidOperationError:
            return LocalEnumeration(comb_class).get_genf(funcs=funcs)

    def get_terms(self, comb_class: Tiling, n: int) -> Terms:
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

    def __init__(self, ignore_parent: bool = False):
        super().__init__(ignore_parent=ignore_parent)

    def pack(self, comb_class: Tiling) -> StrategyPack:
        # pylint: disable=import-outside-toplevel
        from tilings.strategy_pack import TileScopePack

        if self.has_rightmost_insertion_encoding(comb_class):
            pack = TileScopePack.regular_insertion_encoding(2)
        elif self.has_topmost_insertion_encoding(comb_class):
            pack = TileScopePack.regular_insertion_encoding(3)
        else:
            raise StrategyDoesNotApply(
                "tiling does not has a regular insertion encoding"
            )
        return pack.add_initial(DetectComponentsStrategy())

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

    def verified(self, comb_class: Tiling) -> bool:
        return self.has_rightmost_insertion_encoding(
            comb_class
        ) or self.has_topmost_insertion_encoding(comb_class)

    def formal_step(self) -> str:
        return "tiling has a regular insertion encoding"

    @classmethod
    def from_dict(cls, d: dict) -> "InsertionEncodingVerificationStrategy":
        return cls(**d)

    def get_terms(self, comb_class: Tiling, n: int) -> Terms:
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

    def __init__(self, ignore_parent: bool = False, no_factors: bool = True):
        self.no_factors = no_factors
        super().__init__(ignore_parent=ignore_parent)

    def pack(self, comb_class: Tiling) -> StrategyPack:
        try:
            return InsertionEncodingVerificationStrategy().pack(comb_class)
        except StrategyDoesNotApply:
            pass
        if self.no_factors:
            raise InvalidOperationError("Cannot get a simpler specification")
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

    def verified(self, comb_class: Tiling) -> bool:
        return (
            not self.no_factors or len(comb_class.find_factors()) == 1
        ) and MonotoneTreeEnumeration(comb_class).verified()

    def formal_step(self) -> str:
        return "tiling is a monotone tree"

    @classmethod
    def from_dict(cls, d: dict) -> "MonotoneTreeVerificationStrategy":
        return cls(**d)

    def get_genf(
        self, comb_class: Tiling, funcs: Optional[Dict[Tiling, Function]] = None
    ) -> Any:
        if not self.verified(comb_class):
            raise StrategyDoesNotApply("tiling not locally verified")
        try:
            return super().get_genf(comb_class, funcs)
        except InvalidOperationError:
            return MonotoneTreeEnumeration(comb_class).get_genf(funcs=funcs)

    def get_terms(self, comb_class: Tiling, n: int) -> Terms:
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

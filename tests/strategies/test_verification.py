import abc

import pytest
import sympy

from comb_spec_searcher import CombinatorialSpecification, StrategyPack
from comb_spec_searcher.exception import InvalidOperationError, StrategyDoesNotApply
from comb_spec_searcher.strategies import VerificationRule
from comb_spec_searcher.utils import taylor_expand
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.strategies import (
    BasicVerificationStrategy,
    DatabaseVerificationStrategy,
    ElementaryVerificationStrategy,
    LocallyFactorableVerificationStrategy,
    LocalVerificationStrategy,
    MonotoneTreeVerificationStrategy,
    OneByOneVerificationStrategy,
)


class CommonTest(abc.ABC):
    @abc.abstractmethod
    @pytest.fixture
    def strategy(self):
        raise NotImplementedError

    @abc.abstractmethod
    @pytest.fixture
    def formal_step(self):
        pass

    @abc.abstractmethod
    @pytest.fixture
    def enum_verified(self):
        raise NotImplementedError

    @abc.abstractmethod
    @pytest.fixture
    def enum_not_verified(self):
        raise NotImplementedError

    def test_verified(self, strategy, enum_verified, enum_not_verified):
        for tiling in enum_verified:
            print(tiling)
            assert strategy.verified(tiling)
        for tiling in enum_not_verified:
            print(tiling)
            assert not strategy.verified(tiling)

    def test_formal_step(self, strategy, formal_step, enum_verified):
        for tiling in enum_verified:
            assert strategy(tiling).formal_step == formal_step

    def test_verification_rule(self, strategy, enum_verified, enum_not_verified):
        for tiling in enum_not_verified:
            with pytest.raises(StrategyDoesNotApply):
                strategy(tiling).children
        for tiling in enum_verified:
            rule = strategy(tiling)
            assert rule.children == tuple()
            assert isinstance(rule, VerificationRule)
            assert rule.formal_step == strategy.formal_step()

    def test_pack(self, strategy):
        with pytest.raises(InvalidOperationError):
            strategy.pack()

    def test_get_specification(self, strategy, enum_verified):
        for tiling in enum_verified:
            with pytest.raises(InvalidOperationError):
                strategy.get_specification(tiling)

    @abc.abstractmethod
    def test_get_genf(self, strategy, enum_verified):
        raise NotImplementedError

    def test_get_genf_not_verified(self, strategy, enum_not_verified):
        for tiling in enum_not_verified:
            with pytest.raises(StrategyDoesNotApply):
                strategy.get_genf(tiling)

    def test_get_spec_not_verified(self, strategy, enum_not_verified):
        for tiling in enum_not_verified:
            with pytest.raises(StrategyDoesNotApply):
                strategy.get_specification(tiling)


class TestBasicVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return BasicVerificationStrategy()

    @pytest.fixture
    def formal_step(self):
        return "is atom"

    @pytest.fixture
    def empty_enum(self):
        return Tiling.from_string("1")

    @pytest.fixture
    def point_enum(self):
        t = Tiling.from_string("12_21")
        return t.insert_cell((0, 0))

    @pytest.fixture
    def enum_verified(self, empty_enum, point_enum):
        return [empty_enum, point_enum]

    @pytest.fixture
    def enum_not_verified(self):
        return [Tiling.from_string("123")]

    def test_get_genf(self, strategy, enum_verified):
        assert strategy.get_genf(enum_verified[0]) == sympy.sympify("1")
        assert strategy.get_genf(enum_verified[1]) == sympy.sympify("x")


class TestLocallyFactorableVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return LocallyFactorableVerificationStrategy()

    @pytest.fixture
    def formal_step(self):
        return "tiling is locally factorable"

    @pytest.fixture
    def onebyone_enum(self):
        return Tiling.from_string("123")

    @pytest.fixture
    def enum_not_verified(self, onebyone_enum):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1))),
                GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
                GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
            ]
        )
        return [t, onebyone_enum]

    @pytest.fixture
    def enum_verified(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1))),
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            ]
        )
        return [t]

    def test_pack(self, strategy):
        pack = strategy.pack()
        assert isinstance(pack, StrategyPack)
        assert pack.name == "LocallyFactorable"

    def test_get_specification(self, strategy, enum_verified):
        for tiling in enum_verified:
            spec = strategy.get_specification(tiling)
            assert isinstance(spec, CombinatorialSpecification)

    def test_get_genf(self, strategy, enum_verified):
        x = sympy.var("x")
        assert strategy.get_genf(enum_verified[0]) == 1 / (2 * x ** 2 - 3 * x + 1)

    def test_locally_factorable_requirements(
        self, strategy, enum_verified, enum_not_verified
    ):
        assert strategy._locally_factorable_requirements(enum_not_verified[0])
        assert strategy._locally_factorable_requirements(enum_verified[0])
        t1 = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            ],
            requirements=[
                [GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0)))],
                [GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0)))],
            ],
        )
        assert not (strategy._locally_factorable_requirements(t1))
        t2 = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            ],
            requirements=[
                [GriddedPerm(Perm((1, 0)), ((1, 0), (1, 0)))],
                [GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0)))],
            ],
        )
        assert strategy._locally_factorable_requirements(t2)

    def test_locally_factorable_obstructions(
        self, strategy, enum_not_verified, enum_verified
    ):
        assert not strategy._locally_factorable_obstructions(enum_not_verified[0])
        assert strategy._locally_factorable_obstructions(enum_verified[0])

    @pytest.fixture
    def enum_with_tautology(self):
        return Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 1),) * 3),
                GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1))),
            ]
        )

    @pytest.mark.xfail(reason="Cannot think of a tautology")
    def test_possible_tautology(self, strategy, enum_verified, enum_with_tautology):
        for tiling in enum_verified:
            assert not strategy._possible_tautology(tiling)
        assert strategy._possible_tautology(enum_with_tautology)


class TestLocalVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return LocalVerificationStrategy()

    @pytest.fixture
    def formal_step(self):
        return "tiling is locally enumerable"

    @pytest.fixture
    def enum_verified(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
                GriddedPerm(Perm((0, 2, 1)), ((1, 0),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
                GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            ],
            requirements=[
                [
                    GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                    GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                ]
            ],
        )
        return [t]

    @pytest.fixture
    def onebyone_enum(self):
        return Tiling.from_string("123")

    @pytest.fixture
    def enum_not_verified(self, onebyone_enum):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
                GriddedPerm(Perm((0, 2, 1)), ((1, 0),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
                GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1))),
            ],
            requirements=[
                [
                    GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                    GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                ]
            ],
        )
        return [t, onebyone_enum]

    def test_get_genf(self, strategy, enum_verified):
        for tiling in enum_verified:
            with pytest.raises(NotImplementedError):
                strategy.get_genf(tiling)

    @pytest.fixture
    def enum_no_req(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
                GriddedPerm(Perm((0, 2, 1)), ((1, 0),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
                GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            ],
            requirements=[
                [
                    GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                    GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                ]
            ],
        )
        return t

    @pytest.mark.xfail(reason="the no req flag was removed")
    def test_no_req_option(self, enum_no_req):
        assert LocalVerificationStrategy().verified(enum_no_req)


class TestMonotoneTreeVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return MonotoneTreeVerificationStrategy()

    @pytest.fixture
    def formal_step(self):
        return "tiling is a monotone tree"

    @pytest.fixture
    def enum_verified(self):
        t1 = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 2),) * 2),
                GriddedPerm(Perm((0, 1)), ((2, 0),) * 2),
                GriddedPerm(Perm((0, 1, 2)), ((1, 1),) * 3),
            ]
        )
        t2 = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            ]
        )
        return [t1, t2]

    @pytest.fixture
    def enum_with_crossing(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 2),) * 2),
                GriddedPerm(Perm((0, 1)), ((2, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1))),
                GriddedPerm(Perm((0, 1, 2)), ((1, 1),) * 3),
            ]
        )
        return t

    @pytest.fixture
    def enum_with_list_req(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
                GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            ],
            requirements=[
                [
                    GriddedPerm(Perm((0,)), ((0, 0),)),
                    GriddedPerm(Perm((0,)), ((1, 0),)),
                ]
            ],
        )
        return t

    @pytest.fixture
    def onebyone_enum(self):
        return Tiling.from_string("123")

    @pytest.fixture
    def enum_not_verified(self, enum_with_crossing, enum_with_list_req, onebyone_enum):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 2),) * 2),
                GriddedPerm(Perm((0, 1)), ((2, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((2, 2),) * 2),
                GriddedPerm(Perm((0, 1, 2)), ((1, 1),) * 3),
            ]
        )
        forest_tiling = Tiling(
            obstructions=[
                GriddedPerm(Perm((0,)), ((0, 0),)),
                GriddedPerm(Perm((0,)), ((1, 1),)),
                GriddedPerm(Perm((0,)), ((2, 1),)),
                GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
                GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
                GriddedPerm(Perm((0, 1, 2)), ((0, 1), (0, 1), (0, 1))),
            ],
            requirements=[[GriddedPerm(Perm((0,)), ((0, 1),))]],
        )
        return [t, enum_with_crossing, enum_with_list_req, onebyone_enum, forest_tiling]

    @pytest.mark.xfail(reason="combopal database not setup")
    def test_get_genf(self, strategy, enum_verified):
        x = sympy.Symbol("x")
        expected_gf = -(
            sympy.sqrt(
                -(4 * x ** 3 - 14 * x ** 2 + 8 * x - 1) / (2 * x ** 2 - 4 * x + 1)
            )
            - 1
        ) / (2 * x * (x ** 2 - 3 * x + 1))
        assert sympy.simplify(strategy.get_genf(enum_verified[0]) - expected_gf) == 0

        expected_gf = -1 / ((x - 1) * (x / (x - 1) + 1))
        assert sympy.simplify(strategy.get_genf(enum_verified[1]) - expected_gf) == 0

    def test_get_genf_simple(self, strategy):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((1, 0)), ((1, 0),) * 2),
            ]
        )

        print(t)
        assert strategy.verified(t)
        assert sympy.simplify(strategy.get_genf(t) - sympy.sympify("1/(1-2*x)")) == 0

    def test_with_finite_monotone_cell(self, strategy):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((1, 0)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                GriddedPerm(Perm((1, 0)), ((1, 0),) * 2),
            ]
        )
        print(t)
        assert strategy.verified(t)
        assert sympy.simplify(strategy.get_genf(t) - sympy.sympify("1+2*x+2*x**2")) == 0

    def test_with_finite_monotone_cell2(self, strategy):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((1, 0)), ((0, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
                GriddedPerm(Perm((1, 0)), ((1, 1),) * 2),
            ]
        )
        print(t)
        assert strategy.verified(t)
        assert (
            sympy.sympify("x/(1-x)**4 + 1/(1-x)**2") - strategy.get_genf(t)
        ).simplify() == 0

    def test_genf_with_req(self, strategy):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            ],
            requirements=[
                [GriddedPerm(Perm((1, 0)), ((0, 0),) * 2)],
                [GriddedPerm(Perm((0,)), ((1, 0),))],
            ],
        )
        print(t)
        assert strategy.verified(t)
        genf = strategy.get_genf(t).expand()
        terms = [0, 0, 0, 3, 10, 25, 56, 119, 246, 501, 1012]
        assert taylor_expand(genf) == terms

    @pytest.mark.xfail(reason="combopal database not setup")
    def test_genf_with_big_finite_cell(self, strategy):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                GriddedPerm(Perm((3, 2, 1, 0)), ((0, 0),) * 4),
                GriddedPerm(Perm((3, 2, 1, 0)), ((1, 0),) * 4),
            ]
        )
        print(t)
        assert strategy.verified(t)
        genf = strategy.get_genf(t).expand()
        x = sympy.var("x")
        assert (
            genf
            == 1
            + 2 * x
            + 4 * x ** 2
            + 8 * x ** 3
            + 14 * x ** 4
            + 20 * x ** 5
            + 20 * x ** 6
        )

    def test_with_two_reqs(self, strategy):
        t = Tiling(
            obstructions=(
                GriddedPerm(Perm((0,)), ((1, 1),)),
                GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
                GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
                GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
                GriddedPerm(Perm((1, 0)), ((0, 1), (0, 1))),
            ),
            requirements=(
                (GriddedPerm(Perm((0,)), ((0, 0),)),),
                (GriddedPerm(Perm((0,)), ((0, 1),)),),
            ),
        )
        expected_enum = [0, 0, 2, 7, 19, 47, 111, 255, 575, 1279, 2815]
        assert strategy.verified(t)
        assert (
            sympy.simplify(
                strategy.get_genf(t)
                - sympy.sympify("x**2*(3*x - 2)/(4*x**3 - 8*x**2 + 5*x - 1)")
            )
            == 0
        )
        assert taylor_expand(strategy.get_genf(t)) == expected_enum

    def test_corner(self, strategy):
        t = Tiling(
            obstructions=(
                GriddedPerm(Perm((0,)), ((1, 1),)),
                GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
                GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
                GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            ),
            requirements=((GriddedPerm(Perm((0,)), ((0, 0),)),),),
        )
        expected_enum = [0, 1, 5, 17, 50, 138, 370, 979, 2575, 6755, 17700]
        assert strategy.verified(t)
        assert taylor_expand(strategy.get_genf(t)) == expected_enum


class TestElementaryVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return ElementaryVerificationStrategy()

    @pytest.fixture
    def formal_step(self):
        return "tiling is elementary verified"

    @pytest.fixture
    def enum_with_req(self):
        return Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 2),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
                GriddedPerm(Perm((1, 2, 0)), ((0, 1), (1, 2), (2, 0))),
            ],
            requirements=[
                [GriddedPerm(Perm((0,)), ((0, 1),))],
                [GriddedPerm(Perm((0, 1)), ((0, 1), (1, 2)))],
            ],
        )

    @pytest.fixture
    def enum_verified(self, enum_with_req):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 2),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
                GriddedPerm(Perm((1, 2, 0)), ((0, 1), (1, 2), (2, 0))),
            ]
        )
        return [t, enum_with_req]

    @pytest.fixture
    def enum_onebyone(self):
        return Tiling.from_string("123")

    @pytest.fixture
    def enum_with_interleaving(self):
        return Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 2),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            ]
        )

    @pytest.fixture
    def enum_not_verified(self, enum_onebyone, enum_with_interleaving):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 2),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
                GriddedPerm(Perm((1, 2, 0)), ((0, 1), (1, 2), (1, 0))),
            ]
        )
        return [t, enum_onebyone, enum_with_interleaving]

    def test_pack(self, strategy):
        pack = strategy.pack()
        assert isinstance(pack, StrategyPack)
        assert pack.name == "LocallyFactorable"

    def test_get_specification(self, strategy, enum_verified):
        for tiling in enum_verified:
            spec = strategy.get_specification(tiling)
            assert isinstance(spec, CombinatorialSpecification)

    @pytest.mark.xfail(reason="Av(123) not in combopal database")
    def test_get_genf(self, strategy, enum_verified):
        for tiling in enum_verified:
            with pytest.raises(NotImplementedError):
                strategy.get_genf(tiling)


class TestDatabaseVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return DatabaseVerificationStrategy()

    @pytest.fixture
    def formal_step(self):
        return "tiling is in the database"

    @pytest.fixture
    def enum_verified(self):
        return [Tiling.from_string("123_132_231")]

    @pytest.fixture
    def enum_not_verified(self):
        return [Tiling.from_string("1324")]

    def test_get_genf(self, strategy, enum_verified):
        assert strategy.get_genf(enum_verified[0]) == sympy.sympify(
            "(x**2 - x + 1)/(x**2 - 2*x + 1)"
        )


class TestOneByOneVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return OneByOneVerificationStrategy([Perm((2, 1, 0))])

    @pytest.fixture
    def formal_step(self):
        return "tiling is a subclass of the original tiling"

    @pytest.fixture
    def enum_verified(self):
        return [Tiling.from_string("1324_321")]

    @pytest.fixture
    def enum_not_verified(self):
        return [Tiling.from_string("321")]

    def test_change_basis(self, strategy):
        new_s = strategy.change_basis([Perm((0, 1, 2))])
        assert strategy.basis == (Perm((2, 1, 0)),)
        assert new_s.basis == (Perm((0, 1, 2)),)

    def test_get_genf(self, strategy, enum_verified):
        for tiling in enum_verified:
            with pytest.raises(NotImplementedError):
                strategy.get_genf(tiling)

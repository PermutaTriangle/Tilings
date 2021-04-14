import abc

import pytest
import sympy

from comb_spec_searcher import CombinatorialSpecification, StrategyPack
from comb_spec_searcher.exception import InvalidOperationError, StrategyDoesNotApply
from comb_spec_searcher.strategies import VerificationRule
from comb_spec_searcher.utils import taylor_expand
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.assumptions import TrackingAssumption
from tilings.strategies import (
    BasicVerificationStrategy,
    DatabaseVerificationStrategy,
    ElementaryVerificationStrategy,
    InsertionEncodingVerificationStrategy,
    LocallyFactorableVerificationStrategy,
    LocalVerificationStrategy,
    MonotoneTreeVerificationStrategy,
    OneByOneVerificationStrategy,
    ShortObstructionVerificationStrategy,
)
from tilings.strategies.experimental_verification import SubclassVerificationStrategy
from tilings.tilescope import TileScopePack


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

    def test_pack(self, strategy, enum_verified):
        for tiling in enum_verified:
            with pytest.raises(InvalidOperationError):
                strategy.pack(tiling)

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
        # atoms
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
                GriddedPerm((0, 1), ((0, 0), (0, 1))),
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((0, 1), (0, 1))),
            ]
        )
        return [t, onebyone_enum]

    @pytest.fixture
    def enum_verified(self):
        t1 = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0), (1, 1))),
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((0, 1),) * 2),
                GriddedPerm((0, 1), ((1, 1),) * 2),
            ]
        )
        t2 = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 1),) * 2),
                GriddedPerm((1, 0), ((0, 1),) * 2),
                GriddedPerm((0, 1), ((1, 0),) * 2),
                GriddedPerm((0, 1), ((2, 0),) * 2),
            ],
            requirements=[[GriddedPerm((0,), ((0, 1),))]],
            assumptions=[
                TrackingAssumption(
                    [GriddedPerm((0,), ((0, 1),)), GriddedPerm((0,), ((1, 0),))]
                ),
                TrackingAssumption([GriddedPerm((0,), ((1, 0),))]),
            ],
        )
        return [t1, t2]

    def test_pack(self, strategy, enum_verified):
        for tiling in enum_verified:
            pack = strategy.pack(tiling)
            assert isinstance(pack, StrategyPack)
            assert pack.name == "LocallyFactorable"

    @pytest.mark.timeout(5)
    def test_get_specification(self, strategy, enum_verified):
        for tiling in enum_verified:
            spec = strategy.get_specification(tiling)
            assert isinstance(spec, CombinatorialSpecification)

    def test_get_genf(self, strategy, enum_verified):
        x = sympy.var("x")
        assert (
            sympy.simplify(
                strategy.get_genf(enum_verified[0]) - 1 / (2 * x ** 2 - 3 * x + 1)
            )
            == 0
        )

    def test_locally_factorable_requirements(
        self, strategy, enum_verified, enum_not_verified
    ):
        assert strategy._locally_factorable_requirements(enum_not_verified[0])
        assert strategy._locally_factorable_requirements(enum_verified[0])
        t1 = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((1, 0),) * 2),
            ],
            requirements=[
                [GriddedPerm((0, 1), ((0, 0), (1, 0)))],
                [GriddedPerm((1, 0), ((0, 0), (0, 0)))],
            ],
        )
        assert not (strategy._locally_factorable_requirements(t1))
        t2 = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((1, 0),) * 2),
            ],
            requirements=[
                [GriddedPerm((1, 0), ((1, 0), (1, 0)))],
                [GriddedPerm((1, 0), ((0, 0), (0, 0)))],
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
                GriddedPerm((0, 1, 2), ((0, 0),) * 3),
                GriddedPerm((0, 1, 2), ((1, 1),) * 3),
                GriddedPerm((0, 1), ((0, 0), (1, 1))),
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
                GriddedPerm((0, 1, 2), ((0, 0),) * 3),
                GriddedPerm((1, 0, 2), ((0, 0),) * 3),
                GriddedPerm((2, 0, 1), ((0, 0),) * 3),
                GriddedPerm((0, 2, 1), ((1, 0),) * 3),
                GriddedPerm((0, 1, 2), ((1, 0),) * 3),
                GriddedPerm((1, 0, 2), ((1, 0),) * 3),
                GriddedPerm((2, 0, 1), ((1, 0),) * 3),
            ],
            requirements=[
                [GriddedPerm((0,), ((0, 0),))],
                [GriddedPerm((0,), ((1, 0),))],
            ],
        )
        t1 = Tiling(
            obstructions=[
                GriddedPerm((0, 1), [(0, 0), (0, 0)]),
                GriddedPerm((0, 1), [(1, 1), (1, 1)]),
                GriddedPerm((0, 1), [(2, 0), (2, 0)]),
                GriddedPerm((1, 0), [(1, 1), (1, 1)]),
            ],
            requirements=[
                [GriddedPerm((1, 0), ((0, 0), (0, 0)))],
                [GriddedPerm.point_perm((1, 1))],
                [GriddedPerm.point_perm((2, 0))],
            ],
            assumptions=[
                TrackingAssumption([GriddedPerm.point_perm((0, 0))]),
                TrackingAssumption([GriddedPerm.point_perm((1, 1))]),
                TrackingAssumption([GriddedPerm.point_perm((2, 0))]),
                TrackingAssumption(
                    [GriddedPerm.point_perm((0, 0)), GriddedPerm.point_perm((2, 0))]
                ),
            ],
        )
        t2 = Tiling(
            obstructions=(
                GriddedPerm((0,), ((0, 0),)),
                GriddedPerm((0,), ((1, 1),)),
                GriddedPerm((0,), ((2, 0),)),
                GriddedPerm((0, 1), ((0, 1), (0, 1))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1), ((2, 1), (2, 1))),
                GriddedPerm((1, 0), ((1, 0), (1, 0))),
            ),
            requirements=(
                (GriddedPerm((0,), ((1, 0),)),),
                (GriddedPerm((1, 0), ((2, 1), (2, 1))),),
            ),
            assumptions=(
                TrackingAssumption(
                    (GriddedPerm((0,), ((0, 1),)), GriddedPerm((0,), ((1, 0),)))
                ),
                TrackingAssumption(
                    (
                        GriddedPerm((0,), ((0, 1),)),
                        GriddedPerm((0,), ((1, 0),)),
                        GriddedPerm((0,), ((2, 1),)),
                    )
                ),
                TrackingAssumption((GriddedPerm((0,), ((2, 1),)),)),
            ),
        )
        return [t, t1, t2]

    @pytest.fixture
    def onebyone_enum(self):
        return Tiling.from_string("123")

    @pytest.fixture
    def enum_not_verified(self, onebyone_enum):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1, 2), ((0, 0),) * 3),
                GriddedPerm((0, 2, 1), ((1, 0),) * 3),
                GriddedPerm((0, 1, 2), ((1, 0),) * 3),
                GriddedPerm((0, 1), ((1, 1),) * 2),
                GriddedPerm((0, 1), ((0, 0), (1, 1))),
            ],
            requirements=[
                [
                    GriddedPerm((0, 1), ((0, 0),) * 2),
                    GriddedPerm((0, 1), ((1, 0),) * 2),
                ]
            ],
        )
        return [t, onebyone_enum]

    def test_pack(self, strategy, enum_verified):
        assert strategy.pack(
            enum_verified[0]
        ) == TileScopePack.regular_insertion_encoding(3)
        assert strategy.pack(enum_verified[1]).name == "factor pack"
        assert strategy.pack(enum_verified[2]).name == "factor pack"

    @pytest.mark.timeout(10)
    def test_get_specification(self, strategy, enum_verified):
        for tiling in enum_verified:
            spec = strategy.get_specification(tiling)
            assert isinstance(spec, CombinatorialSpecification)

    @pytest.mark.timeout(60)
    def test_get_genf(self, strategy, enum_verified):
        assert (
            sympy.simplify(
                strategy.get_genf(enum_verified[0])
                - sympy.simplify("2*x**2*(x**2 + x - 1)/((x - 1)**3*(2*x - 1)**2)")
            )
            == 0
        )
        # can't the other tilings due to assumptions.

    @pytest.fixture
    def enum_crossing_req(self):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1, 2), ((0, 0),) * 3),
                GriddedPerm((0, 2, 1), ((1, 0),) * 3),
                GriddedPerm((0, 1, 2), ((1, 0),) * 3),
                GriddedPerm((0, 1), ((1, 1),) * 2),
            ],
            requirements=[
                [
                    GriddedPerm((0, 1), ((0, 0),) * 2),
                    GriddedPerm((0, 1), ((1, 0),) * 2),
                ]
            ],
        )
        return t

    def test_no_crossing_req_option(self, enum_crossing_req):
        assert not LocalVerificationStrategy(no_factors=True).verified(
            enum_crossing_req
        )


class TestInsertionEncodingVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return InsertionEncodingVerificationStrategy()

    @pytest.fixture
    def formal_step(self):
        return "tiling has a regular insertion encoding"

    @pytest.fixture
    def enum_verified(self):
        return [
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                    GriddedPerm((0, 1), ((0, 0), (1, 0))),
                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                    GriddedPerm((0, 1), ((2, 0), (2, 0))),
                ),
                requirements=(),
                assumptions=(),
            )
        ]

    @pytest.fixture
    def enum_not_verified(self):
        return [
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                    GriddedPerm((0, 1), ((0, 0), (1, 0))),
                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                    GriddedPerm((0, 1), ((2, 0), (2, 0))),
                    GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (3, 0))),
                ),
                requirements=(),
                assumptions=(),
            )
        ]

    def test_pack(self, strategy, enum_verified):
        for tiling in enum_verified:
            strategy.pack(tiling) == TileScopePack.regular_insertion_encoding(3)

    @pytest.mark.timeout(60)
    def test_get_specification(self, strategy, enum_verified):
        for tiling in enum_verified:
            assert isinstance(
                strategy.get_specification(tiling), CombinatorialSpecification
            )

    def test_get_genf(self, strategy, enum_verified):
        x = sympy.Symbol("x")
        expected_gf = (1 - x) / (4 * x ** 2 - 4 * x + 1)
        assert sympy.simplify(strategy.get_genf(enum_verified[0]) - expected_gf) == 0


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
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((0, 1),) * 2),
                GriddedPerm((0, 1), ((0, 2),) * 2),
                GriddedPerm((0, 1), ((2, 0),) * 2),
                GriddedPerm((0, 1, 2), ((1, 1),) * 3),
            ]
        )
        t2 = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((1, 0),) * 2),
            ]
        )
        return [t1, t2]

    @pytest.fixture
    def enum_with_crossing(self):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((0, 1),) * 2),
                GriddedPerm((0, 1), ((0, 2),) * 2),
                GriddedPerm((0, 1), ((2, 0),) * 2),
                GriddedPerm((0, 1), ((0, 0), (0, 1))),
                GriddedPerm((0, 1, 2), ((1, 1),) * 3),
            ]
        )
        return t

    @pytest.fixture
    def enum_with_list_req(self):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
            ],
            requirements=[[GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))]],
        )
        return t

    @pytest.fixture
    def onebyone_enum(self):
        return Tiling.from_string("123")

    @pytest.fixture
    def enum_not_verified(self, enum_with_crossing, enum_with_list_req, onebyone_enum):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((0, 1),) * 2),
                GriddedPerm((0, 1), ((0, 2),) * 2),
                GriddedPerm((0, 1), ((2, 0),) * 2),
                GriddedPerm((0, 1), ((2, 2),) * 2),
                GriddedPerm((0, 1, 2), ((1, 1),) * 3),
            ]
        )
        forest_tiling = Tiling(
            obstructions=[
                GriddedPerm((0,), ((0, 0),)),
                GriddedPerm((0,), ((1, 1),)),
                GriddedPerm((0,), ((2, 1),)),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1), ((2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 1), (0, 1), (0, 1))),
            ],
            requirements=[[GriddedPerm((0,), ((0, 1),))]],
        )
        return [t, enum_with_crossing, enum_with_list_req, onebyone_enum, forest_tiling]

    def test_pack(self, strategy, enum_verified):
        with pytest.raises(InvalidOperationError):
            strategy.pack(enum_verified[0])
        assert strategy.pack(
            enum_verified[1]
        ) == TileScopePack.regular_insertion_encoding(3)

    @pytest.mark.timeout(30)
    def test_get_specification(self, strategy, enum_verified):
        with pytest.raises(InvalidOperationError):
            isinstance(
                strategy.get_specification(enum_verified[0]), CombinatorialSpecification
            )
        assert isinstance(
            strategy.get_specification(enum_verified[1]), CombinatorialSpecification
        )

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
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((1, 0), ((1, 0),) * 2),
            ]
        )

        print(t)
        assert strategy.verified(t)
        assert sympy.simplify(strategy.get_genf(t) - sympy.sympify("1/(1-2*x)")) == 0

    def test_with_finite_monotone_cell(self, strategy):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((1, 0), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((1, 0),) * 2),
                GriddedPerm((1, 0), ((1, 0),) * 2),
            ]
        )
        print(t)
        assert strategy.verified(t)
        assert sympy.simplify(strategy.get_genf(t) - sympy.sympify("1+2*x+2*x**2")) == 0

    def test_with_finite_monotone_cell2(self, strategy):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((1, 0), ((0, 1),) * 2),
                GriddedPerm((0, 1), ((0, 1),) * 2),
                GriddedPerm((1, 0), ((1, 1),) * 2),
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
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((1, 0),) * 2),
            ],
            requirements=[
                [GriddedPerm((1, 0), ((0, 0),) * 2)],
                [GriddedPerm((0,), ((1, 0),))],
            ],
        )
        print(t)
        assert strategy.verified(t)
        genf = strategy.get_genf(t).expand()
        terms = [0, 0, 0, 3, 10, 25, 56, 119, 246, 501, 1012]
        assert taylor_expand(genf) == terms

    def test_genf_with_big_finite_cell(self, strategy):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((0, 0),) * 2),
                GriddedPerm((0, 1), ((1, 0),) * 2),
                GriddedPerm((3, 2, 1, 0), ((0, 0),) * 4),
                GriddedPerm((3, 2, 1, 0), ((1, 0),) * 4),
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
                GriddedPerm((0,), ((1, 1),)),
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((0, 1), (0, 1))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((1, 0), ((0, 1), (0, 1))),
            ),
            requirements=(
                (GriddedPerm((0,), ((0, 0),)),),
                (GriddedPerm((0,), ((0, 1),)),),
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
                GriddedPerm((0,), ((1, 1),)),
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((0, 1), (0, 1))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
            ),
            requirements=((GriddedPerm((0,), ((0, 0),)),),),
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
                GriddedPerm((0, 2, 1), ((0, 1),) * 3),
                GriddedPerm((0, 2, 1), ((1, 2),) * 3),
                GriddedPerm((0, 2, 1), ((2, 0),) * 3),
                GriddedPerm((1, 2, 0), ((0, 1), (1, 2), (2, 0))),
            ],
            requirements=[
                [GriddedPerm((0,), ((0, 1),))],
                [GriddedPerm((0, 1), ((0, 1), (1, 2)))],
            ],
        )

    @pytest.fixture
    def enum_verified(self, enum_with_req):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 2, 1), ((0, 1),) * 3),
                GriddedPerm((0, 2, 1), ((1, 2),) * 3),
                GriddedPerm((0, 2, 1), ((2, 0),) * 3),
                GriddedPerm((1, 2, 0), ((0, 1), (1, 2), (2, 0))),
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
                GriddedPerm((0, 1, 2), ((0, 1),) * 3),
                GriddedPerm((0, 1, 2), ((1, 2),) * 3),
                GriddedPerm((0, 1, 2), ((1, 0),) * 3),
            ]
        )

    @pytest.fixture
    def enum_not_verified(self, enum_onebyone, enum_with_interleaving):
        t = Tiling(
            obstructions=[
                GriddedPerm((0, 1, 2), ((0, 1),) * 3),
                GriddedPerm((0, 1, 2), ((1, 2),) * 3),
                GriddedPerm((0, 1, 2), ((1, 0),) * 3),
                GriddedPerm((1, 2, 0), ((0, 1), (1, 2), (1, 0))),
            ]
        )
        return [t, enum_onebyone, enum_with_interleaving]

    def test_pack(self, strategy, enum_verified):
        for tiling in enum_verified:
            pack = strategy.pack(tiling)
            assert isinstance(pack, StrategyPack)
            assert pack.name == "LocallyFactorable"

    def test_get_specification(self, strategy, enum_verified):
        for tiling in enum_verified:
            spec = strategy.get_specification(tiling)
            assert isinstance(spec, CombinatorialSpecification)

    def test_get_genf(self, strategy, enum_verified):
        assert (
            sympy.simplify(
                strategy.get_genf(enum_verified[0])
                - sympy.sympify(
                    "(2*x**2 + 3*x*sqrt(1 - 4*x) - 9*x - 3*sqrt(1 - 4*x) + 3)/(2*x**2)"
                )
            )
            == 0
        )
        assert (
            sympy.simplify(
                strategy.get_genf(enum_verified[1])
                - sympy.sympify(
                    "sqrt(1 - 4*x)*(2*x - 1)/(2*x**2) + (2*x**2 - 4*x + 1)/(2*x**2)"
                )
            )
            == 0
        )


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
        return [
            # any 231 subclass
            Tiling.from_string("132_4321"),
            # any with regular insertion encoding, regardless of reqs
            Tiling.from_string("012_1032"),
            Tiling.from_string("012_1302").add_list_requirement(
                [
                    GriddedPerm.single_cell((1, 0), (0, 0)),
                    GriddedPerm.single_cell((0, 1), (0, 0)),
                ]
            ),
            Tiling.from_string("0231_2103"),
            # subclass of Av(123) avoiding patterns of length <= 4, positive or not
            Tiling.from_string("012_2301").add_requirement(Perm((0,)), [(0, 0)]),
            # uses fusion
            Tiling.from_string("123").insert_cell((0, 0)),
            # no pack yet
            Tiling.from_string("1324"),
        ]

    @pytest.fixture
    def enum_not_verified(self):
        return [Tiling.from_string("321")]

    def test_change_basis(self, strategy):
        new_s = strategy.change_basis([Perm((0, 1, 2))], False)
        assert strategy.basis == (Perm((2, 1, 0)),)
        assert new_s.basis == (Perm((0, 1, 2)),)

    def test_pack(self, strategy, enum_verified):
        assert strategy.pack(
            enum_verified[0]
        ) == TileScopePack.point_and_row_and_col_placements().add_verification(
            BasicVerificationStrategy(), replace=True
        )
        assert strategy.pack(enum_verified[1]) in (
            TileScopePack.regular_insertion_encoding(2),
            TileScopePack.regular_insertion_encoding(3),
        )

        assert strategy.pack(
            enum_verified[2]
        ) == TileScopePack.regular_insertion_encoding(3)

        assert strategy.pack(
            enum_verified[3]
        ) == TileScopePack.regular_insertion_encoding(2)
        assert strategy.pack(
            enum_verified[4]
        ) == TileScopePack.row_and_col_placements().inject_basis(
            [Perm((0, 1, 2)), Perm((2, 3, 0, 1))]
        )

        assert strategy.pack(enum_verified[5]) == TileScopePack.row_and_col_placements(
            row_only=True
        ).make_fusion(tracked=True).inject_basis([Perm((0, 1, 2))])
        with pytest.raises(InvalidOperationError):
            strategy.pack(enum_verified[6])

    @pytest.mark.timeout(120)
    def test_get_specification(self, strategy, enum_verified):
        for tiling in enum_verified[:-1]:
            spec = strategy.get_specification(tiling)
            assert isinstance(spec, CombinatorialSpecification)
        with pytest.raises(InvalidOperationError):
            spec = strategy.get_specification(enum_verified[-1])
            assert isinstance(spec, CombinatorialSpecification)

    @pytest.mark.timeout(300)
    def test_get_genf(self, strategy, enum_verified):
        # any 231 subclass
        assert (
            sympy.simplify(
                strategy.get_genf(enum_verified[0])
                - sympy.sympify("-(3*x**4 - 5*x**3 + 7*x**2 - 4*x + 1)/(x - 1)**5")
            )
            == 0
        )
        # any with regular insertion encoding
        assert (
            sympy.simplify(
                strategy.get_genf(enum_verified[1])
                - sympy.sympify("-(2*x - 1)/(x**2 - 3*x + 1)")
            )
            == 0
        )
        assert (
            sympy.simplify(
                strategy.get_genf(enum_verified[2])
                - sympy.sympify("-x**2*(x - 2)/(x**2 - 3*x + 1)")
            )
            == 0
        )
        # This test takes too long!
        # assert (
        #     sympy.simplify(
        #         strategy.get_genf(enum_verified[3])
        #         - sympy.sympify(
        #             "-(x - 1)*(3*x - 1)*(x**2 - 3*x + 1)/(2*x**5 -"
        #             " 10*x**4 + 25*x**3 - 22*x**2 + 8*x - 1)"
        #         )
        #     )
        #     == 0
        # )
        # subclass of Av(123) avoiding patterns of length <= 4
        assert (
            sympy.simplify(
                strategy.get_genf(enum_verified[4])
                - sympy.sympify(
                    "-x*(2*x**4 - 5*x**3 + 7*x**2 - 4*x + 1)/((x - 1)**4*(2*x - 1))"
                )
            )
            == 0
        )

        # uses fusion, gives error because not implemented,
        #  so can't test enum_verified[5]

        # no method for Av(1324) yet
        with pytest.raises(InvalidOperationError):
            strategy.pack(enum_verified[6])

    def test_132_with_two_points(self, strategy):
        t = Tiling(
            obstructions=[GriddedPerm((0, 2, 1), ((0, 0),) * 3)],
            requirements=[
                [
                    GriddedPerm((0, 1), ((0, 0),) * 2),
                    GriddedPerm((1, 0), ((0, 0),) * 2),
                ]
            ],
        )
        assert strategy.verified(t)
        assert strategy.get_specification(t) is not None
        assert (
            sympy.simplify(
                strategy.get_genf(t) - sympy.sympify("(1 - sqrt(1 - 4*x)) / (2*x)")
            )
            == -sympy.var("x") - 1
        )

    def test_with_assumptions(self, strategy):
        ass = TrackingAssumption([GriddedPerm.point_perm((0, 0))])
        t = Tiling.from_string("01").add_assumption(ass)
        assert strategy.verified(t)
        assert strategy.get_genf(t) == sympy.sympify("-1/(k_0*x - 1)")

    def test_with_123_subclass_12req(self, strategy):
        t2 = Tiling(
            obstructions=[
                GriddedPerm((2, 1, 0), ((0, 0),) * 3),
                GriddedPerm((1, 0, 3, 2), ((0, 0),) * 4),
            ],
            requirements=[[GriddedPerm((1, 0), ((0, 0),) * 2)]],
        )
        assert strategy.verified(t2)
        genf = strategy.get_genf(t2)
        assert taylor_expand(genf, 16) == [
            0,
            0,
            1,
            4,
            12,
            32,
            79,
            184,
            410,
            884,
            1861,
            3852,
            7880,
            15992,
            32283,
            64944,
            130358,
        ]


class TestShortObstructionVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return ShortObstructionVerificationStrategy()

    @pytest.fixture
    def formal_step(self):
        return "tiling has short (length <= 3) crossing obstructions"

    @pytest.fixture
    def enum_verified(self):
        # +-+-+-+-+
        # |2| | | |
        # +-+-+-+-+
        # | | |●| |
        # +-+-+-+-+
        # |\| | | |
        # +-+-+-+-+
        # | |●| | |
        # +-+-+-+-+
        # |1| | |3|
        # +-+-+-+-+
        # 1: Av+(120, 0132)
        # 2: Av(012)
        # 3: Av(0132, 0231, 1203)
        # \: Av(01)
        # ●: point
        # Crossing obstructions:
        # 01: (0, 0), (3, 0)
        # 012: (0, 0), (0, 0), (0, 2)
        # 012: (0, 0), (0, 0), (0, 4)
        # 012: (0, 0), (0, 2), (0, 4)
        # 012: (0, 0), (0, 4), (0, 4)
        # 012: (0, 2), (0, 4), (0, 4)
        # 120: (0, 0), (0, 2), (0, 0)
        # Requirement 0:
        # 0: (0, 0)
        # Requirement 1:
        # 0: (1, 1)
        # Requirement 2:
        # 0: (2, 3)
        return [
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((0, 0), (3, 0))),
                    GriddedPerm((0, 1), ((0, 2), (0, 2))),
                    GriddedPerm((0, 1), ((1, 1), (1, 1))),
                    GriddedPerm((0, 1), ((2, 3), (2, 3))),
                    GriddedPerm((1, 0), ((1, 1), (1, 1))),
                    GriddedPerm((1, 0), ((2, 3), (2, 3))),
                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 2))),
                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 4))),
                    GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 4))),
                    GriddedPerm((0, 1, 2), ((0, 0), (0, 4), (0, 4))),
                    GriddedPerm((0, 1, 2), ((0, 2), (0, 4), (0, 4))),
                    GriddedPerm((0, 1, 2), ((0, 4), (0, 4), (0, 4))),
                    GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
                    GriddedPerm((1, 2, 0), ((0, 0), (0, 2), (0, 0))),
                    GriddedPerm((0, 1, 3, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
                    GriddedPerm((0, 1, 3, 2), ((3, 0), (3, 0), (3, 0), (3, 0))),
                    GriddedPerm((0, 2, 3, 1), ((3, 0), (3, 0), (3, 0), (3, 0))),
                    GriddedPerm((1, 2, 0, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
                ),
                requirements=(
                    (GriddedPerm((0,), ((0, 0),)),),
                    (GriddedPerm((0,), ((1, 1),)),),
                    (GriddedPerm((0,), ((2, 3),)),),
                ),
                assumptions=(),
            )
        ]

    @pytest.fixture
    def enum_not_verified(self):
        return [
            Tiling.from_string("12"),
            Tiling.from_string("123"),
            Tiling.from_string("1234"),
        ]

    def test_get_genf(self, strategy, enum_verified):
        pass


class TestSubclassVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return SubclassVerificationStrategy([Perm((0, 1, 2))])

    @pytest.fixture
    def formal_step(self):
        return "tiling is contained in the subclass Av(012)"

    @pytest.fixture
    def enum_verified(self):
        # +-+-+-+
        # | |\| |
        # +-+-+-+
        # |\| |\|
        # +-+-+-+
        # | |\|1|
        # +-+-+-+
        # 1: Av(012)
        # \: Av(01)
        # Crossing obstructions:
        # 012: (1, 0), (2, 0), (2, 0)
        # 012: (1, 0), (2, 0), (2, 1)
        # 012: (2, 0), (2, 0), (2, 1)
        return [
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((0, 1), (0, 1))),
                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                    GriddedPerm((0, 1), ((1, 2), (1, 2))),
                    GriddedPerm((0, 1), ((2, 1), (2, 1))),
                    GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                    GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 1))),
                    GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                    GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 1))),
                ),
                requirements=(),
                assumptions=(),
            ),
            Tiling.from_string("123"),
        ]

    @pytest.fixture
    def enum_not_verified(self):
        return [
            Tiling.from_string("1234"),
        ]

    def test_get_genf(self, strategy, enum_verified):
        pass

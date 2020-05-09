import abc

import pytest
import sympy

from comb_spec_searcher import CombinatorialSpecification, Rule, StrategyPack
from comb_spec_searcher.exception import InvalidOperationError, StrategyDoesNotApply
from comb_spec_searcher.strategies.rule import VerificationRule
from comb_spec_searcher.utils import taylor_expand
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.strategies import (
    BasicVerificationStrategy,
    DatabaseVerificationStrategy,
    ElementaryVerificationStrategy,
    LocalVerificationStrategy,
    LocallyFactorableVerificationStrategy,
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
            assert isinstance(rule, Rule)
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
            with pytest.raises(InvalidOperationError):
                strategy.get_genf(tiling)

    def test_get_spec_not_verified(self, strategy, enum_not_verified):
        for tiling in enum_not_verified:
            with pytest.raises(InvalidOperationError):
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
        for tiling in enum_verified:
            with pytest.raises(NotImplementedError):
                strategy.get_genf(tiling)

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
        return "tiling is locally factorable"

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
        return LocalVerificationStrategy(t)

    @pytest.fixture
    def enum_not_verified(self):
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
        return LocalVerificationStrategy(t)

    @pytest.fixture
    def onebyone_enum(self):
        return LocalVerificationStrategy(Tiling.from_string("123"))

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
        return LocalVerificationStrategy(t, no_req=True)

    def test_pack(self, enum_verified):
        assert enum_verified.pack is None

    def test_verified(self, enum_verified, enum_not_verified):
        assert enum_verified.verified()
        assert not enum_not_verified.verified()

    def test_formal_step(self, enum_verified):
        assert enum_verified.formal_step == "Tiling is locally enumerable"

    def test_get_specification(self, enum_verified):
        with pytest.raises(NotImplementedError):
            enum_verified.get_specification()

    def test_get_genf(self, enum_verified):
        with pytest.raises(NotImplementedError):
            enum_verified.get_genf()

    def test_get_genf_not_verified(self, enum_not_verified):
        with pytest.raises(InvalidOperationError):
            enum_not_verified.get_genf()

    def test_1x1_verified(self, onebyone_enum):
        assert not onebyone_enum.verified()

    def test_no_req_option(self, enum_no_req):
        assert not enum_no_req.verified()


class TestMonotoneTreeVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return MonotoneTreeVerificationStrategy()

    @pytest.fixture
    def formal_step(self):
        return "tiling is locally factorable"

    @pytest.fixture
    def enum_verified(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 2),) * 2),
                GriddedPerm(Perm((0, 1)), ((2, 0),) * 2),
                GriddedPerm(Perm((0, 1, 2)), ((1, 1),) * 3),
            ]
        )
        return MonotoneTreeVerificationStrategy(t)

    @pytest.fixture
    def enum_not_verified(self):
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
        return MonotoneTreeVerificationStrategy(t)

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
        return MonotoneTreeVerificationStrategy(t)

    @pytest.fixture
    def onebyone_enum(self):
        return LocalVerificationStrategy(Tiling.from_string("123"))

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
        return MonotoneTreeVerificationStrategy(t)

    def test_formal_step(self, enum_verified):
        assert enum_verified.formal_step == "Tiling is a monotone tree"

    def test_visited_cells_aligned(self, enum_verified):
        visited = {(1, 1), (0, 1)}
        assert sorted(enum_verified._visted_cells_aligned((0, 2), visited)) == [(0, 1)]

    def test_cell_tree_traversal(self, enum_verified):
        order = list(enum_verified._cell_tree_traversal((1, 1)))
        assert len(order) == 4
        assert (1, 1) not in order
        assert order[0] == (0, 1)
        assert order[3] == (2, 0)
        assert set(order[1:3]) == {(0, 0), (0, 2)}

    def test_not_verified(self, enum_with_list_req, onebyone_enum, enum_with_crossing):
        assert not enum_with_crossing.verified()
        assert not enum_with_list_req.verified()
        assert not onebyone_enum.verified()
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
        assert not MonotoneTreeVerificationStrategy(forest_tiling).verified()

    @pytest.mark.xfail(reason="No database setup")
    def test_get_genf(self, enum_verified):
        x = sympy.Symbol("x")
        expected_gf = -(
            sympy.sqrt(
                -(4 * x ** 3 - 14 * x ** 2 + 8 * x - 1) / (2 * x ** 2 - 4 * x + 1)
            )
            - 1
        ) / (2 * x * (x ** 2 - 3 * x + 1))
        assert sympy.simplify(enum_verified.get_genf() - expected_gf) == 0
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            ]
        )
        enum_no_start = MonotoneTreeVerificationStrategy(t)
        expected_gf = -1 / ((x - 1) * (x / (x - 1) + 1))
        assert sympy.simplify(enum_no_start.get_genf() - expected_gf) == 0

    @pytest.mark.xfail(reason="pack does not exist")
    def test_get_specification(self, enum_verified):
        raise NotImplementedError

    @pytest.mark.xfail
    def test_pack(self, enum_verified):
        pack = enum_verified.pack
        assert isinstance(pack, StrategyPack)
        assert pack.name == "MonotoneTree"

    def test_get_genf_simple(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((1, 0)), ((1, 0),) * 2),
            ]
        )
        enum = MonotoneTreeVerificationStrategy(t)
        print(t)
        assert enum.verified()
        assert sympy.simplify(enum.get_genf() - sympy.sympify("1/(1-2*x)")) == 0

    def test_with_finite_monotone_cell(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((1, 0)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                GriddedPerm(Perm((1, 0)), ((1, 0),) * 2),
            ]
        )
        enum = MonotoneTreeVerificationStrategy(t)
        print(t)
        assert enum.verified()
        assert enum.get_genf().expand() == sympy.sympify("1+2*x+2*x**2")

    def test_with_finite_monotone_cell2(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((1, 0)), ((0, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
                GriddedPerm(Perm((1, 0)), ((1, 1),) * 2),
            ]
        )
        enum = MonotoneTreeVerificationStrategy(t)
        print(t)
        assert enum.verified()
        assert (
            sympy.sympify("x/(1-x)**4 + 1/(1-x)**2") - enum.get_genf()
        ).simplify() == 0

    def test_interleave_fixed_length(self, enum_verified):
        track_var = MonotoneTreeVerificationStrategy._tracking_var
        cell_var = enum_verified._cell_variable((1, 0))
        dummy_var = enum_verified._cell_variable((0, 0))
        x = sympy.var("x")
        F = x ** 8 * track_var ** 3 * dummy_var ** 3
        assert (
            enum_verified._interleave_fixed_length(F, (1, 0), 1)
            == 4 * x ** 9 * dummy_var ** 3 * cell_var ** 1
        )
        assert (
            enum_verified._interleave_fixed_length(F, (1, 0), 3)
            == 20 * x ** 11 * dummy_var ** 3 * cell_var ** 3
        )
        assert (
            enum_verified._interleave_fixed_length(F, (1, 0), 0)
            == x ** 8 * dummy_var ** 3
        )

    def test_interleave_fixed_lengths(self, enum_verified):
        track_var = MonotoneTreeVerificationStrategy._tracking_var
        cell_var = enum_verified._cell_variable((1, 0))
        dummy_var = enum_verified._cell_variable((0, 0))
        x = sympy.var("x")
        F = x ** 8 * track_var ** 3 * dummy_var ** 3
        assert (
            enum_verified._interleave_fixed_lengths(F, (1, 0), 1, 1)
            == 4 * x ** 9 * dummy_var ** 3 * cell_var ** 1
        )
        assert (
            enum_verified._interleave_fixed_lengths(F, (1, 0), 3, 3)
            == 20 * x ** 11 * dummy_var ** 3 * cell_var ** 3
        )
        assert (
            enum_verified._interleave_fixed_lengths(F, (1, 0), 0, 0)
            == x ** 8 * dummy_var ** 3
        )
        assert (
            enum_verified._interleave_fixed_lengths(F, (1, 0), 0, 2)
            == x ** 8 * dummy_var ** 3
            + 4 * x ** 9 * dummy_var ** 3 * cell_var ** 1
            + 10 * x ** 10 * dummy_var ** 3 * cell_var ** 2
        )
        assert (
            enum_verified._interleave_fixed_lengths(F, (1, 0), 1, 3)
            == 4 * x ** 9 * dummy_var ** 3 * cell_var ** 1
            + 10 * x ** 10 * dummy_var ** 3 * cell_var ** 2
            + 20 * x ** 11 * dummy_var ** 3 * cell_var ** 3
        )

    def test_genf_with_req(self):
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
        enum = MonotoneTreeVerificationStrategy(t)
        print(t)
        assert enum.verified()
        genf = enum.get_genf().expand()
        terms = [0, 0, 0, 3, 10, 25, 56, 119, 246, 501, 1012]
        assert taylor_expand(genf) == terms

    def test_genf_with_big_finite_cell(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                GriddedPerm(Perm((3, 2, 1, 0)), ((0, 0),) * 4),
                GriddedPerm(Perm((3, 2, 1, 0)), ((1, 0),) * 4),
            ]
        )
        enum = MonotoneTreeVerificationStrategy(t)
        print(t)
        assert enum.verified()
        genf = enum.get_genf().expand()
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

    def test_with_two_reqs(self):
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
        enum = MonotoneTreeVerificationStrategy(t)
        expected_enum = [0, 0, 2, 7, 19, 47, 111, 255, 575, 1279, 2815]
        assert enum.verified()
        assert taylor_expand(enum.get_genf()) == expected_enum

    def test_corner(self):
        t = Tiling(
            obstructions=(
                GriddedPerm(Perm((0,)), ((1, 1),)),
                GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
                GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
                GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            ),
            requirements=((GriddedPerm(Perm((0,)), ((0, 0),)),),),
        )
        enum = MonotoneTreeVerificationStrategy(t)
        expected_enum = [0, 1, 5, 17, 50, 138, 370, 979, 2575, 6755, 17700]
        assert enum.verified()
        assert taylor_expand(enum.get_genf()) == expected_enum


class TestElementaryVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return ElementaryVerificationStrategy()

    @pytest.fixture
    def formal_step(self):
        return "tiling is locally factorable"

    @pytest.fixture
    def enum_verified(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 2),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((2, 0),) * 3),
                GriddedPerm(Perm((1, 2, 0)), ((0, 1), (1, 2), (2, 0))),
            ]
        )
        return ElementaryVerificationStrategy(t)

    @pytest.fixture
    def enum_not_verified(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 2),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
                GriddedPerm(Perm((1, 2, 0)), ((0, 1), (1, 2), (1, 0))),
            ]
        )
        return ElementaryVerificationStrategy(t)

    @pytest.fixture
    def enum_onebyone(self):
        t = Tiling.from_string("123")
        return ElementaryVerificationStrategy(t)

    @pytest.fixture
    def enum_with_interleaving(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 1),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 2),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
            ]
        )
        return ElementaryVerificationStrategy(t)

    @pytest.fixture
    def enum_with_req(self):
        t = Tiling(
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
        return ElementaryVerificationStrategy(t)

    @pytest.mark.xfail
    def test_pack(self, enum_verified):
        pack = enum_verified.pack
        assert isinstance(pack, StrategyPack)
        assert pack.name == "LocallyFactorable"

    def test_formal_step(self, enum_verified):
        assert enum_verified.formal_step == "Tiling is elementary"

    @pytest.mark.xfail
    def test_get_specification(self, enum_verified):
        raise NotImplementedError

    @pytest.mark.xfail
    def test_get_genf(self, enum_verified):
        raise NotImplementedError

    def test_more_verified(
        self, enum_onebyone, enum_with_interleaving, enum_with_req,
    ):
        assert not enum_onebyone.verified()
        assert not enum_with_interleaving.verified()
        assert enum_with_req.verified()


class TestDatabaseVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return DatabaseVerificationStrategy()

    @pytest.fixture
    def formal_step(self):
        return "tiling is locally factorable"

    @pytest.fixture
    def enum_verified(self):
        t = Tiling.from_string("123_132_231")
        return DatabaseVerificationStrategy(t)

    @pytest.fixture
    def enum_not_verified(self):
        t = Tiling.from_string("1324")
        return DatabaseVerificationStrategy(t)

    def test_formal_step(self, enum_verified):
        assert enum_verified.formal_step == "Tiling is in the database"

    def test_get_genf(self, enum_verified):
        assert enum_verified.get_genf() == sympy.sympify(
            "(x**2 - x + 1)/(x**2 - 2*x + 1)"
        )

    def test_get_specification(self, enum_verified):
        with pytest.raises(NotImplementedError):
            enum_verified.get_specification()

    def test_pack(self, enum_verified):
        with pytest.raises(NotImplementedError):
            enum_verified.pack

    @pytest.mark.slow
    def test_load_verified_tilings(self):
        assert not DatabaseVerificationStrategy.all_verified_tilings
        DatabaseVerificationStrategy.load_verified_tiling()
        assert DatabaseVerificationStrategy.all_verified_tilings
        sample = next(iter(DatabaseVerificationStrategy.all_verified_tilings))
        Tiling.decompress(sample)

    def test_verification_with_cache(self):
        t = Tiling.from_string("123_132_231")
        DatabaseVerificationStrategy.all_verified_tilings = frozenset()
        assert DatabaseVerificationStrategy(t).verified()
        DatabaseVerificationStrategy.all_verified_tilings = frozenset([1, 2, 3, 4])
        assert not DatabaseVerificationStrategy(t).verified()
        DatabaseVerificationStrategy.all_verified_tilings = frozenset([t.compress()])
        assert DatabaseVerificationStrategy(t).verified()


class TestOneByOneVerificationStrategy(CommonTest):
    @pytest.fixture
    def strategy(self):
        return OneByOneVerificationStrategy()

    @pytest.fixture
    def formal_step(self):
        return "tiling is locally factorable"

    @pytest.fixture
    def enum_verified(self):
        t = Tiling.from_string("1324_321")
        return OneByOneVerificationStrategy(t, [Perm((2, 1, 0))])

    @pytest.fixture
    def enum_not_verified(self):
        t = Tiling.from_string("321")
        return OneByOneVerificationStrategy(t, [Perm((2, 1, 0))])

    @pytest.mark.xfail
    def test_pack(self, enum_verified):
        pack = enum_verified.pack
        assert isinstance(pack, StrategyPack)
        assert pack.name == "LocallyFactorable"

    def test_formal_step(self, enum_verified):
        assert (
            enum_verified.formal_step
            == "This tiling is a subclass of the original tiling."
        )

    @pytest.mark.xfail
    def test_get_specification(self, enum_verified):
        raise NotImplementedError

    @pytest.mark.xfail
    def test_get_genf(self, enum_verified):
        raise NotImplementedError

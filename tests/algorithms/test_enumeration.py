import abc
from unittest.mock import Mock, PropertyMock, patch

import pytest
import sympy

from comb_spec_searcher import StrategyPack
from comb_spec_searcher.strategies.rule import VerificationRule
from permuta import Perm
from tilings import Obstruction, Requirement, Tiling
from tilings.algorithms import (BasicEnumeration, LocalEnumeration,
                                LocallyFactorableEnumeration,
                                MonotoneTreeEnumeration)
from tilings.algorithms.enumeration import Enumeration
from tilings.exception import InvalidOperationError


class CommonTest(abc.ABC):
    @abc.abstractmethod
    @pytest.fixture
    def enum_verified(self):
        raise NotImplementedError

    @pytest.fixture
    def enum_not_verified(self):
        raise NotImplementedError

    @abc.abstractmethod
    def test_pack(self, enum_verified):
        raise NotImplementedError

    def test_verified(self, enum_verified, enum_not_verified):
        assert enum_verified.verified()
        assert not enum_not_verified.verified()

    @abc.abstractmethod
    def test_formal_step(self, enum_verified):
        raise NotImplementedError

    def test_verification_rule(self, enum_verified, enum_not_verified):
        assert isinstance(enum_verified.verification_rule(), VerificationRule)
        assert (enum_verified.verification_rule().formal_step ==
                enum_verified.formal_step)
        assert enum_not_verified.verification_rule() is None

    @abc.abstractmethod
    def test_get_tree(self, enum_verified):
        raise NotImplementedError

    @abc.abstractmethod
    def test_get_genf(self, enum_verified):
        raise NotImplementedError

    def test_get_genf_not_verified(self, enum_not_verified):
        with pytest.raises(InvalidOperationError):
            enum_not_verified.get_genf()

    def test_get_tree_not_verified(self, enum_not_verified):
        with pytest.raises(InvalidOperationError):
            enum_not_verified.get_tree()


class TestBasicEnumeration(CommonTest):

    @pytest.fixture
    def empty_enum(self):
        t = Tiling.from_string('1')
        return BasicEnumeration(t)

    @pytest.fixture
    def enum_not_verified(self):
        t = Tiling.from_string('123')
        return BasicEnumeration(t)

    enum_verified = empty_enum

    @pytest.fixture
    def point_enum(self):
        t = Tiling.from_string('12_21')
        t = t.insert_cell((0, 0))
        return BasicEnumeration(t)

    def test_point_is_verified(self, point_enum):
        assert point_enum.verified()

    def test_formal_step(self, enum_verified):
        assert enum_verified.formal_step == 'Base cases'

    def test_pack(self, enum_verified):
        with pytest.raises(InvalidOperationError):
            enum_verified.pack

    def test_get_tree(self, enum_verified):
        with pytest.raises(InvalidOperationError):
            enum_verified.get_tree()

    def test_get_genf(self, empty_enum, point_enum):
        assert empty_enum.get_genf() == sympy.sympify('1')
        assert point_enum.get_genf() == sympy.sympify('x')


class TestLocallyFactorableEnumeration(CommonTest):
    @pytest.fixture
    def enum_not_verified(self):
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0), (0, 1))),
            Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
            Obstruction(Perm((0, 1)), ((0, 1), (0, 1))),
        ])
        return LocallyFactorableEnumeration(t)

    @pytest.fixture
    def enum_verified(self):
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0), (1, 1))),
            Obstruction(Perm((0, 1)), ((0, 0),)*2),
            Obstruction(Perm((0, 1)), ((0, 1),)*2),
            Obstruction(Perm((0, 1)), ((1, 1),)*2),
        ])
        return LocallyFactorableEnumeration(t)
        pass

    @pytest.fixture
    def enum_with_tautology(self):
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1, 2)), ((0, 0),)*3),
            Obstruction(Perm((0, 1, 2)), ((1, 1),)*3),
            Obstruction(Perm((0, 1)), ((0, 0), (1, 1))),
        ])
        print(t)
        return LocallyFactorableEnumeration(t)

    @pytest.fixture
    def onebyone_enum(self):
        return LocallyFactorableEnumeration(Tiling.from_string('123'))

    @pytest.mark.xfail
    def test_pack(self, enum_verified):
        pack = enum_verified.pack
        assert isinstance(pack, StrategyPack)
        assert pack.name == 'LocallyFactorable'

    def test_formal_step(self, enum_verified):
        assert enum_verified.formal_step == "Tiling is locally factorable"

    @pytest.mark.xfail
    def test_get_tree(self, enum_verified):
        raise NotImplementedError

    @pytest.mark.xfail
    def test_get_genf(self, enum_verified):
        raise NotImplementedError

    def test_locally_factorable_requirements(self, enum_verified,
                                             enum_not_verified):
        assert enum_not_verified._locally_factorable_requirements()
        assert enum_verified._locally_factorable_requirements()
        t1 = Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0),)*2),
            Obstruction(Perm((0, 1)), ((1, 0),)*2),
        ], requirements=[
            [Requirement(Perm((0, 1)), ((0, 0), (1, 0)))],
            [Requirement(Perm((1, 0)), ((0, 0), (0, 0)))]
        ])
        enum_with_not_loc_fact_reqs = LocallyFactorableEnumeration(t1)
        assert not (enum_with_not_loc_fact_reqs.
                    _locally_factorable_requirements())
        t2 = Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0),)*2),
            Obstruction(Perm((0, 1)), ((1, 0),)*2),
        ], requirements=[
            [Requirement(Perm((1, 0)), ((1, 0), (1, 0)))],
            [Requirement(Perm((1, 0)), ((0, 0), (0, 0)))]
        ])
        enum_with_loc_fact_reqs = LocallyFactorableEnumeration(t2)
        assert enum_with_loc_fact_reqs._locally_factorable_requirements()

    def test_locally_factorable_obstructions(self, enum_not_verified,
                                             enum_verified):
        assert not enum_not_verified._locally_factorable_obstructions()
        assert enum_verified._locally_factorable_obstructions()

    @pytest.mark.xfail(reason='Cannot think of a tautology')
    def test_possible_tautology(self, enum_verified, enum_with_tautology):
        assert not enum_verified._possible_tautology()
        assert enum_with_tautology._possible_tautology()

    def test_1x1_verified(self, onebyone_enum):
        assert not onebyone_enum.verified()


class TestLocalEnumeration(CommonTest):
    @pytest.fixture
    def enum_verified(self):
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1, 2)), ((0, 0),)*3),
            Obstruction(Perm((0, 2, 1)), ((1, 0),)*3),
            Obstruction(Perm((0, 1, 2)), ((1, 0),)*3),
            Obstruction(Perm((0, 1)), ((1, 1),)*2),
        ], requirements=[[
            Requirement(Perm((0, 1)), ((0, 0),)*2),
            Requirement(Perm((0, 1)), ((1, 0),)*2),
        ]])
        return LocalEnumeration(t)

    @pytest.fixture
    def enum_not_verified(self):
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1, 2)), ((0, 0),)*3),
            Obstruction(Perm((0, 2, 1)), ((1, 0),)*3),
            Obstruction(Perm((0, 1, 2)), ((1, 0),)*3),
            Obstruction(Perm((0, 1)), ((1, 1),)*2),
            Obstruction(Perm((0, 1)), ((0, 0), (1, 1))),
        ], requirements=[[
            Requirement(Perm((0, 1)), ((0, 0),)*2),
            Requirement(Perm((0, 1)), ((1, 0),)*2),
        ]])
        return LocalEnumeration(t)

    @pytest.fixture
    def onebyone_enum(self):
        return LocalEnumeration(Tiling.from_string('123'))

    def test_pack(self, enum_verified):
        assert enum_verified.pack is None

    def test_verified(self, enum_verified, enum_not_verified):
        assert enum_verified.verified()
        assert not enum_not_verified.verified()

    def test_formal_step(self, enum_verified):
        assert (enum_verified.formal_step == "Tiling is locally enumerable")

    def test_get_tree(self, enum_verified):
        with pytest.raises(NotImplementedError):
            enum_verified.get_tree()

    def test_get_genf(self, enum_verified):
        with pytest.raises(NotImplementedError):
            enum_verified.get_genf()

    def test_get_genf_not_verified(self, enum_not_verified):
        with pytest.raises(InvalidOperationError):
            enum_not_verified.get_genf()

    def test_1x1_verified(self, onebyone_enum):
        assert not onebyone_enum.verified()


class TestMonotoneTreeEnumeration(CommonTest):

    @pytest.fixture
    def enum_verified(self):
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0),)*2),
            Obstruction(Perm((0, 1)), ((0, 1),)*2),
            Obstruction(Perm((0, 1)), ((0, 2),)*2),
            Obstruction(Perm((0, 1)), ((2, 0),)*2),
            Obstruction(Perm((0, 1, 2)), ((1, 1),)*3),
        ])
        return MonotoneTreeEnumeration(t)

    @pytest.fixture
    def enum_not_verified(self):
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0),)*2),
            Obstruction(Perm((0, 1)), ((0, 1),)*2),
            Obstruction(Perm((0, 1)), ((0, 2),)*2),
            Obstruction(Perm((0, 1)), ((2, 0),)*2),
            Obstruction(Perm((0, 1)), ((2, 2),)*2),
            Obstruction(Perm((0, 1, 2)), ((1, 1),)*3),
        ])
        return MonotoneTreeEnumeration(t)

    @pytest.fixture
    def enum_with_req(self):
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0),)*2),
            Obstruction(Perm((0, 1)), ((0, 1),)*2),
            Obstruction(Perm((0, 1)), ((0, 2),)*2),
            Obstruction(Perm((0, 1)), ((2, 0),)*2),
            Obstruction(Perm((0, 1, 2)), ((1, 1),)*3),
        ], requirements=[
            [Requirement(Perm((2, 0, 1)), ((2, 0),)*3)],
            [Requirement(Perm((0,)), ((0, 1),))]
        ])
        return MonotoneTreeEnumeration(t)

    @pytest.fixture
    def onebyone_enum(self):
        return LocalEnumeration(Tiling.from_string('123'))

    @pytest.fixture
    def enum_with_crossing(self):
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0),)*2),
            Obstruction(Perm((0, 1)), ((0, 1),)*2),
            Obstruction(Perm((0, 1)), ((0, 2),)*2),
            Obstruction(Perm((0, 1)), ((2, 0),)*2),
            Obstruction(Perm((0, 1)), ((0, 0), (0, 1))),
            Obstruction(Perm((0, 1, 2)), ((1, 1),)*3),
        ])
        return MonotoneTreeEnumeration(t)

    def test_formal_step(self, enum_verified):
        assert enum_verified.formal_step == "Tiling is a monotone tree"

    def test_visited_cells_aligned(self, enum_verified):
        visited = {(1, 1), (0, 1)}
        assert (sorted(enum_verified._visted_cells_aligned((0, 2), visited)) ==
                [(0, 1)])

    def test_cell_tree_traversal(self, enum_verified):
        order = list(enum_verified._cell_tree_traversal((1, 1)))
        assert len(order) == 4
        assert (1, 1) not in order
        assert order[0] == (0, 1)
        assert order[3] == (2, 0)
        assert set(order[1:3]) == {(0, 0), (0, 2)}

    def test_not_verified(self, enum_with_req, onebyone_enum,
                          enum_with_crossing):
        assert not enum_with_crossing.verified()
        assert not enum_with_req.verified()
        assert not onebyone_enum.verified()

    def test_get_genf(self, enum_verified):
        x = sympy.Symbol('x')
        expected_gf = -(sympy.sqrt(-(4*x**3 - 14*x**2 + 8*x - 1) /
                                   (2*x**2 - 4*x + 1)) - 1)/(2*x*(x**2 - 3*x +
                                                                  1))
        assert sympy.simplify(enum_verified.get_genf() - expected_gf) == 0

    @pytest.mark.xfail(reason='pack does not exist')
    def test_get_tree(self, enum_verified):
        raise NotImplementedError

    @pytest.mark.xfail
    def test_pack(self, enum_verified):
        pack = enum_verified.pack
        assert isinstance(pack, StrategyPack)
        assert pack.name == 'MonotoneTree'

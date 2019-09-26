import abc

import pytest
import sympy
from unittest.mock import Mock, patch, PropertyMock

from comb_spec_searcher import StrategyPack
from comb_spec_searcher.strategies.rule import VerificationRule
from tilescopethree.strategy_packs_v2 import point_placements
from tilings import Obstruction, Requirement, Tiling
from tilings.exception import InvalidOperationError
from tilings.algorithms.enumeration import Enumeration
from tilings.algorithms import BasicEnumeration, LocallyFactorableEnumeration


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
            Obstruction(Perm((0, 1)), ((1, 0), (1, 1))),
            Obstruction(Perm((0, 1)), ((1, 1), (1, 1))),
            Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
            Obstruction(Perm((0, 1)), ((0, 1), (0, 1))),
            Obstruction(Perm((0, 1)), ((0, 0), (1, 1))),
            Obstruction(Perm((1, 0)), ((0, 1), (1, 0))),
        ])
        return LocallyFactorableEnumeration(t)
        pass

    def test_pack(self, enum_verified):
        raise NotImplementedError

    def test_formal_step(self, enum_verified):
        raise NotImplementedError

    def test_get_tree(self, enum_verified):
        raise NotImplementedError

    def test_get_genf(self, enum_verified):
        raise NotImplementedError

import abc
from unittest.mock import MagicMock, patch

import pytest

from comb_spec_searcher import Rule
from permuta import Perm
from tilings import Obstruction, Requirement, Tiling
from tilings.algorithms import EmptyCellInferral, SubobstructionInferral
from tilings.algorithms.obstruction_inferral import ObstructionInferral


class CommonTest(abc.ABC):
    @pytest.fixture
    def tiling1(self):
        """
        A tiling that can be inferred.
        """
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((0, 0), (0, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (1, 0))),
            Obstruction(Perm((2, 1, 0)), ((0, 0), (1, 0), (1, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (1, 0)))
        ], requirements=[[
            Requirement(Perm((1, 0)), ((1, 0), (1, 0)))
        ]])
        return t

    @pytest.fixture
    def tiling2(self):
        """
        A tiling that can be inferred.
        """
        t2 = Tiling(obstructions=[
            Obstruction(Perm((0, 2, 1)), ((0, 0), (1, 0), (1, 0))),
            Obstruction(Perm((0, 2, 1)), ((0, 0), (1, 0), (2, 0))),
            Obstruction(Perm((0, 2, 1)), ((0, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 2, 1)), ((1, 0), (2, 0), (2, 0))),
            Obstruction(Perm((1, 0, 2)), ((0, 0), (0, 0), (1, 0))),
            Obstruction(Perm((1, 0, 2)), ((0, 0), (0, 0), (2, 0))),
            Obstruction(Perm((1, 0, 2)), ((0, 0), (1, 0), (2, 0))),
            Obstruction(Perm((1, 0, 2)), ((1, 0), (1, 0), (2, 0))),
            Obstruction(Perm((0, 3, 2, 1)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((0, 3, 2, 1)), ((0, 0), (0, 0), (0, 0), (1, 0))),
            Obstruction(Perm((0, 3, 2, 1)), ((0, 0), (0, 0), (0, 0), (2, 0))),
            Obstruction(Perm((0, 3, 2, 1)), ((1, 0), (1, 0), (1, 0), (1, 0))),
            Obstruction(Perm((0, 3, 2, 1)), ((1, 0), (1, 0), (1, 0), (2, 0))),
            Obstruction(Perm((0, 3, 2, 1)), ((2, 0), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((1, 0, 3, 2)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((1, 0, 3, 2)), ((1, 0), (1, 0), (1, 0), (1, 0))),
            Obstruction(Perm((1, 0, 3, 2)), ((2, 0), (2, 0), (2, 0), (2, 0)))
        ], requirements=[[
            Requirement(Perm((1, 0)), ((1, 0), (1, 0)))
        ]])
        return t2

    @pytest.fixture
    def tiling_not_inf(self):
        """
        A tiling that cannot be inferred.
        """
        return Tiling.from_string('1234_2341')

    @abc.abstractmethod
    @pytest.fixture
    def obs_inf1(self, tiling1):
        pass

    @abc.abstractmethod
    @pytest.fixture
    def obs_not_inf(self, obs_not_inf):
        pass

    def test_formal_step(self, obs_inf1):
        assert (obs_inf1.formal_step() ==
                "Added the obstructions [Obstruction(Perm((0, 1)), "
                "((0, 0), (0, 0)))].")

    def test_rule(self, obs_inf1, obs_not_inf):
        rule = obs_inf1.rule()
        assert isinstance(rule, Rule)
        assert rule.comb_classes == [obs_inf1.obstruction_inferral()]
        assert rule.ignore_parent
        assert rule.workable == [True]
        assert rule.constructor == 'equiv'
        assert rule.possibly_empty == [False]
        assert obs_not_inf.rule() is None


class TestObstructionInferral(CommonTest):

    @pytest.fixture
    @patch.multiple(ObstructionInferral, __abstractmethods__=set())
    def obs_inf1(self, tiling1):
        obs_trans = ObstructionInferral(tiling1)
        obs_trans.potential_new_obs = MagicMock(return_value=[
            Obstruction(Perm((0, 1)), [(0, 0), (0, 0)]),
            Obstruction(Perm((1, 0)), [(0, 0), (1, 0)]),
        ])
        return obs_trans

    @pytest.fixture
    @patch.multiple(ObstructionInferral, __abstractmethods__=set())
    def obs_not_inf(self, tiling_not_inf):
        """
        An obstruction inferral object where no new obstructions can be
        added.
        """
        obs_trans = ObstructionInferral(tiling_not_inf)
        obs_trans.potential_new_obs = MagicMock(return_value=[])
        return obs_trans

    def test_init(self, tiling1):
        with pytest.raises(TypeError):
            ObstructionInferral(tiling1)

    def test_new_obs(self, obs_inf1, obs_not_inf):
        assert obs_inf1.new_obs() == [
            Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
        ]
        assert obs_not_inf.new_obs() == []

    def test_obstruction_inferral(self, obs_inf1, tiling1, obs_not_inf,
                                  tiling_not_inf):
        assert obs_not_inf.obstruction_inferral() == tiling_not_inf
        inf_tiling = tiling1.add_single_cell_obstruction(Perm((0, 1)), (0, 0))
        assert obs_inf1.obstruction_inferral() == inf_tiling

    def test_can_add_obstruction(self, obs_inf1, tiling1):
        ob1 = Obstruction(Perm((0, 1)), [(0, 0), (0, 0)])
        ob2 = Obstruction(Perm((1, 0)), [(0, 0), (1, 0)])
        assert obs_inf1.can_add_obstruction(ob1, tiling1)
        assert not obs_inf1.can_add_obstruction(ob2, tiling1)


class TestSubobstructionInferral(CommonTest):
    @pytest.fixture
    def obs_inf1(self, tiling1):
        obs_inf = SubobstructionInferral(tiling1)
        return obs_inf

    @pytest.fixture
    def obs_inf2(self, tiling2):
        obs_inf = SubobstructionInferral(tiling2)
        return obs_inf

    @pytest.fixture
    def obs_not_inf(self, tiling_not_inf):
        """
        An obstruction inferral object where no new obstructions can be
        added.
        """
        obs_trans = SubobstructionInferral(tiling_not_inf)
        return obs_trans

    def test_init(self, tiling1):
        sub_obs_inf = SubobstructionInferral(tiling1)
        assert sub_obs_inf._tiling == tiling1

    def test_potential_new_obs(self, obs_inf1):
        print(obs_inf1._tiling)
        assert obs_inf1.potential_new_obs() == set([
            Obstruction(Perm((0,)), ((0, 0),)),
            Obstruction(Perm((0,)), ((1, 0),)),
            Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
            Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((0, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 0), (1, 0))),
        ])

    def test_new_obs(self, obs_not_inf, obs_inf1, obs_inf2):
        assert obs_inf1.new_obs() == [
            Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
        ]
        assert obs_not_inf.new_obs() == []
        assert obs_inf2.new_obs() == [
            Obstruction(Perm((0, 1)), ((0, 0), (2, 0))),
            Obstruction(Perm((0, 2, 1)), ((0, 0), (0, 0), (2, 0))),
        ]

    def test_obstruction_inferral(self, obs_inf2):
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0), (2, 0))),
            Obstruction(Perm((0, 2, 1)), ((0, 0), (1, 0), (1, 0))),
            Obstruction(Perm((0, 2, 1)), ((1, 0), (2, 0), (2, 0))),
            Obstruction(Perm((1, 0, 2)), ((0, 0), (0, 0), (1, 0))),
            Obstruction(Perm((1, 0, 2)), ((1, 0), (1, 0), (2, 0))),
            Obstruction(Perm((0, 3, 2, 1)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((0, 3, 2, 1)), ((0, 0), (0, 0), (0, 0), (1, 0))),
            Obstruction(Perm((0, 3, 2, 1)), ((1, 0), (1, 0), (1, 0), (1, 0))),
            Obstruction(Perm((0, 3, 2, 1)), ((1, 0), (1, 0), (1, 0), (2, 0))),
            Obstruction(Perm((0, 3, 2, 1)), ((2, 0), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((1, 0, 3, 2)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((1, 0, 3, 2)), ((1, 0), (1, 0), (1, 0), (1, 0))),
            Obstruction(Perm((1, 0, 3, 2)), ((2, 0), (2, 0), (2, 0), (2, 0)))
        ], requirements=[[
            Requirement(Perm((1, 0)), ((1, 0), (1, 0)))
        ]])
        assert obs_inf2.obstruction_inferral() == t


class TestEmptyCellInferral(CommonTest):
    @pytest.fixture
    def tiling1(self):
        t = Tiling(obstructions=[
            Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((0, 0), (1, 0))),
        ], requirements=[[
            Requirement(Perm((0,)), ((0, 0),)),
        ]])
        return t

    @pytest.fixture
    def obs_inf1(self, tiling1):
        obs_inf = EmptyCellInferral(tiling1)
        return obs_inf

    @pytest.fixture
    def obs_inf2(self, tiling2):
        obs_inf = EmptyCellInferral(tiling2)
        return obs_inf

    @pytest.fixture
    def obs_not_inf(self, tiling_not_inf):
        obs_trans = SubobstructionInferral(tiling_not_inf)
        return obs_trans

    def test_init(self, tiling1):
        empty_inf = EmptyCellInferral(tiling1)
        assert empty_inf._tiling == tiling1

    def test_potential_new_obs(self, obs_inf1, obs_inf2):
        assert obs_inf1.potential_new_obs() == set([
            Obstruction(Perm((0,)), ((1, 0), )),
        ])
        assert obs_inf2.potential_new_obs() == set([
            Obstruction(Perm((0,)), ((0, 0), )),
            Obstruction(Perm((0,)), ((2, 0), )),
        ])

    def test_formal_step(self, obs_inf1):
        assert "The cells (1, 0) are empty."

import pytest

from permuta import Perm
from tilings import Obstruction, Requirement, Tiling


@pytest.fixture
def simple_tiling():
    return Tiling(
        obstructions=[Obstruction(Perm((1, 0)), [(0, 1), (1, 0)])],
        requirements=[[Requirement(Perm((0, 1)), [(0, 0), (1, 0)]),
                       Requirement(Perm((0, 1)), [(0, 0), (1, 1)])]])

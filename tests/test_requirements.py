import pytest

from grids_three import Obstruction, Requirement
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_WEST


@pytest.fixture
def simple_req():
    return Requirement(Perm((0, 2, 1)), [(0, 1), (1, 1), (1, 1)])


def test_place_forced_point(simple_req):
    reqs, obs = simple_req.place_forced_point(1, DIR_WEST)
    assert reqs == [Requirement(Perm((0, 1)), [(0, 1), (3, 1)])]
    assert sorted(obs) == [
        Obstruction(Perm((0, 1)), ((0, 1), (1, 3))),
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 1), (1, 1))),
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 1), (3, 1))),
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 3), (1, 1))),
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 3), (1, 3))),
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 3), (3, 1))),
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 3), (3, 3))),
        Obstruction(Perm((0, 2, 1)), ((0, 3), (1, 3), (1, 3))),
        Obstruction(Perm((0, 2, 1)), ((0, 3), (1, 3), (3, 3)))]

    reqs, obs = simple_req.place_forced_point(1, DIR_EAST)
    assert reqs == [Requirement(Perm((0, 1)), [(0, 1), (3, 1)])]
    assert sorted(obs) == [
        Obstruction(Perm((0, 2, 1)), ((0, 1), (3, 1), (3, 1))),
        Obstruction(Perm((0, 2, 1)), ((0, 1), (3, 3), (3, 1))),
        Obstruction(Perm((0, 2, 1)), ((0, 1), (3, 3), (3, 3))),
        Obstruction(Perm((0, 2, 1)), ((0, 3), (3, 3), (3, 3)))]

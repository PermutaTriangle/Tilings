import pytest

from grids_three import Obstruction, Requirement
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST


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


def test_partial_place_forced_point(simple_req):
    reqs, obs = simple_req.partial_place_forced_point(1, DIR_WEST)
    assert reqs == [Requirement(Perm((0, 2, 1)), ((0, 1), (2, 1), (3, 1)))]
    assert sorted(obs) == [
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 1), (1, 1))),
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 1), (2, 1))),
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 1), (3, 1)))
    ]
    reqs, obs = simple_req.partial_place_forced_point(1, DIR_EAST)
    assert reqs == [Requirement(Perm((0, 2, 1)), ((0, 1), (2, 1), (3, 1)))]
    assert sorted(obs) == [
        Obstruction(Perm((0, 2, 1)), ((0, 1), (3, 1), (3, 1)))
    ]

    reqs, obs = simple_req.partial_place_forced_point(1, DIR_NORTH)
    assert reqs == [Requirement(Perm((0, 2, 1)), ((0, 1), (1, 2), (1, 1)))]
    assert sorted(obs) == [
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 3), (1, 1))),
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 3), (1, 2))),
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 3), (1, 3))),
        Obstruction(Perm((0, 2, 1)), ((0, 3), (1, 3), (1, 3)))
    ]

    reqs, obs = simple_req.partial_place_forced_point(1, DIR_SOUTH)
    assert reqs == [Requirement(Perm((0, 2, 1)), ((0, 1), (1, 2), (1, 1)))]
    assert sorted(obs) == [
        Obstruction(Perm((0, 2, 1)), ((0, 1), (1, 1), (1, 1)))
    ]

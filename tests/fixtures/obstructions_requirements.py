import pytest

from permuta import Perm
from tilings import Obstruction, Requirement


@pytest.fixture
def typical_redundant_obstructions():
    """Returns a very typical list of obstructions clustered together in a
    corner of a tiling.  """
    return [
        Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (3, 0))),
        Obstruction(Perm((0, 1)), ((2, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((2, 0), (3, 0))),
        Obstruction(Perm((0, 1)), ((3, 1), (3, 1))),
        Obstruction(Perm((1, 0)), ((3, 0), (3, 0))),
        Obstruction(Perm((1, 0)), ((3, 1), (3, 0))),
        Obstruction(Perm((1, 0)), ((3, 1), (3, 1))),
        Obstruction(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 0))),
        Obstruction(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 1))),
        Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (1, 0))),
        Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (2, 0))),
        Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (3, 0))),
        Obstruction(Perm((2, 1, 0)), ((1, 0), (2, 0), (2, 0))),
        Obstruction(Perm((2, 1, 0)), ((1, 0), (2, 0), (3, 0))),
        Obstruction(Perm((2, 1, 0)), ((2, 0), (2, 0), (2, 0))),
        Obstruction(Perm((2, 1, 0)), ((2, 0), (2, 0), (3, 0))),
        Obstruction(Perm((3, 2, 1, 0)), ((1, 1), (2, 0), (2, 0), (2, 0))),
        Obstruction(Perm((3, 2, 1, 0)), ((2, 1), (2, 1), (3, 0), (3, 0)))
    ]


@pytest.fixture
def typical_redundant_requirements():
    """Returns a very typical list of requirements of a tiling.  """
    return [
        [Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 3))),
         Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 4))),
         Requirement(Perm((1, 0, 2)), ((0, 0), (1, 0), (2, 3))),
         Requirement(Perm((1, 0, 2)), ((0, 1), (1, 0), (2, 3)))],
        [Requirement(Perm((0, 1, 2)), ((2, 3), (2, 3), (2, 3))),
         Requirement(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0))),
         Requirement(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 0)))],
        [Requirement(Perm((0, 1)), ((1, 0), (3, 0))),
         Requirement(Perm((0, 1)), ((2, 0), (2, 0))),
         Requirement(Perm((0, 1)), ((2, 0), (3, 0))),
         Requirement(Perm((0, 1)), ((2, 0), (3, 1)))],
        [Requirement(Perm((1, 0)), ((3, 3), (3, 1))),
         Requirement(Perm((1, 0)), ((3, 1), (3, 1))),
         Requirement(Perm((1, 0)), ((3, 1), (3, 0)))]]


@pytest.fixture
def typical_obstructions_with_local():
    return [
        Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (3, 0))),
        Obstruction(Perm((0, 1)), ((2, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((2, 0), (3, 0))),
        Obstruction(Perm((0, 1)), ((3, 1), (3, 1))),
        Obstruction(Perm((0, 2, 1)), ((3, 0), (3, 0), (3, 0))),
        Obstruction(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 1))),
        Obstruction(Perm((1, 2, 0)), ((1, 0), (1, 0), (1, 0))),

        Obstruction(Perm((3, 2, 1, 0)), ((1, 1), (2, 0), (2, 0), (2, 0))),
        Obstruction(Perm((3, 2, 1, 0)), ((2, 1), (2, 1), (3, 0), (3, 0)))
    ]


@pytest.fixture
def typical_requirements_with_local():
    """Return a very typical list of requirements of a tiling, including some
    local length 1 requirements."""
    return [
        [Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 3))),
         Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 4))),
         Requirement(Perm((1, 0, 2)), ((0, 0), (1, 0), (2, 3))),
         Requirement(Perm((1, 0, 2)), ((0, 1), (1, 0), (2, 3)))],
        [Requirement(Perm((0, 1)), ((1, 0), (3, 0))),
         Requirement(Perm((0, 1)), ((2, 0), (2, 0))),
         Requirement(Perm((0, 1)), ((2, 0), (3, 0))),
         Requirement(Perm((0, 1)), ((2, 0), (3, 1)))],
        [Requirement(Perm((0, )), ((3, 0),))],
        [Requirement(Perm((1, 0)), ((2, 0), (2, 0)))],
        [Requirement(Perm((0, 2, 1)), ((0, 0), (2, 3), (2, 3)))]]

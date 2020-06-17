import pytest

from permuta import Perm
from tilings import GriddedPerm


@pytest.fixture
def typical_redundant_obstructions():
    """Returns a very typical list of obstructions clustered together in a
    corner of a tiling.  """
    return [
        GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
        GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
        GriddedPerm(Perm((0, 1)), ((1, 0), (3, 0))),
        GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
        GriddedPerm(Perm((0, 1)), ((2, 0), (3, 0))),
        GriddedPerm(Perm((0, 1)), ((3, 1), (3, 1))),
        GriddedPerm(Perm((1, 0)), ((3, 0), (3, 0))),
        GriddedPerm(Perm((1, 0)), ((3, 1), (3, 0))),
        GriddedPerm(Perm((1, 0)), ((3, 1), (3, 1))),
        GriddedPerm(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 0))),
        GriddedPerm(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 1))),
        GriddedPerm(Perm((2, 1, 0)), ((1, 0), (1, 0), (1, 0))),
        GriddedPerm(Perm((2, 1, 0)), ((1, 0), (1, 0), (2, 0))),
        GriddedPerm(Perm((2, 1, 0)), ((1, 0), (1, 0), (3, 0))),
        GriddedPerm(Perm((2, 1, 0)), ((1, 0), (2, 0), (2, 0))),
        GriddedPerm(Perm((2, 1, 0)), ((1, 0), (2, 0), (3, 0))),
        GriddedPerm(Perm((2, 1, 0)), ((2, 0), (2, 0), (2, 0))),
        GriddedPerm(Perm((2, 1, 0)), ((2, 0), (2, 0), (3, 0))),
        GriddedPerm(Perm((3, 2, 1, 0)), ((1, 1), (2, 0), (2, 0), (2, 0))),
        GriddedPerm(Perm((3, 2, 1, 0)), ((2, 1), (2, 1), (3, 0), (3, 0))),
    ]


@pytest.fixture
def typical_redundant_requirements():
    """Returns a very typical list of requirements of a tiling.  """
    return [
        [
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 3))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 4))),
            GriddedPerm(Perm((1, 0, 2)), ((0, 0), (1, 0), (2, 3))),
            GriddedPerm(Perm((1, 0, 2)), ((0, 1), (1, 0), (2, 3))),
        ],
        [
            GriddedPerm(Perm((0, 1, 2)), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 0))),
        ],
        [
            GriddedPerm(Perm((0, 1)), ((1, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (3, 1))),
        ],
        [
            GriddedPerm(Perm((1, 0)), ((3, 3), (3, 1))),
            GriddedPerm(Perm((1, 0)), ((3, 1), (3, 1))),
            GriddedPerm(Perm((1, 0)), ((3, 1), (3, 0))),
        ],
    ]


@pytest.fixture
def typical_obstructions_with_local():
    return [
        GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
        GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))),
        GriddedPerm(Perm((0, 1)), ((1, 0), (3, 0))),
        GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
        GriddedPerm(Perm((0, 1)), ((2, 0), (3, 0))),
        GriddedPerm(Perm((0, 1)), ((3, 1), (3, 1))),
        GriddedPerm(Perm((0, 2, 1)), ((3, 0), (3, 0), (3, 0))),
        GriddedPerm(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 1))),
        GriddedPerm(Perm((1, 2, 0)), ((1, 0), (1, 0), (1, 0))),
        GriddedPerm(Perm((3, 2, 1, 0)), ((1, 1), (2, 0), (2, 0), (2, 0))),
        GriddedPerm(Perm((3, 2, 1, 0)), ((2, 1), (2, 1), (3, 0), (3, 0))),
    ]


@pytest.fixture
def typical_requirements_with_local():
    """Return a very typical list of requirements of a tiling, including some
    local length 1 requirements."""
    return [
        [
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 3))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 4))),
            GriddedPerm(Perm((1, 0, 2)), ((0, 0), (1, 0), (2, 3))),
            GriddedPerm(Perm((1, 0, 2)), ((0, 1), (1, 0), (2, 3))),
        ],
        [
            GriddedPerm(Perm((0, 1)), ((1, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (3, 0))),
            GriddedPerm(Perm((0, 1)), ((2, 0), (3, 1))),
        ],
        [GriddedPerm(Perm((0,)), ((3, 0),))],
        [GriddedPerm(Perm((1, 0)), ((2, 0), (2, 0)))],
        [GriddedPerm(Perm((0, 2, 1)), ((0, 0), (2, 3), (2, 3)))],
    ]

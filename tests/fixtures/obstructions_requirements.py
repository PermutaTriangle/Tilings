import pytest

from tilings import GriddedPerm


@pytest.fixture
def typical_redundant_obstructions():
    """Returns a very typical list of obstructions clustered together in a
    corner of a tiling."""
    return [
        GriddedPerm((0, 1), ((1, 0), (1, 0))),
        GriddedPerm((0, 1), ((1, 0), (2, 0))),
        GriddedPerm((0, 1), ((1, 0), (3, 0))),
        GriddedPerm((0, 1), ((2, 0), (2, 0))),
        GriddedPerm((0, 1), ((2, 0), (3, 0))),
        GriddedPerm((0, 1), ((3, 1), (3, 1))),
        GriddedPerm((1, 0), ((3, 0), (3, 0))),
        GriddedPerm((1, 0), ((3, 1), (3, 0))),
        GriddedPerm((1, 0), ((3, 1), (3, 1))),
        GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (3, 1))),
        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (1, 0))),
        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (2, 0))),
        GriddedPerm((2, 1, 0), ((1, 0), (1, 0), (3, 0))),
        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (2, 0))),
        GriddedPerm((2, 1, 0), ((1, 0), (2, 0), (3, 0))),
        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (2, 0))),
        GriddedPerm((2, 1, 0), ((2, 0), (2, 0), (3, 0))),
        GriddedPerm((3, 2, 1, 0), ((1, 1), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((3, 2, 1, 0), ((2, 1), (2, 1), (3, 0), (3, 0))),
    ]


@pytest.fixture
def typical_redundant_requirements():
    """Returns a very typical list of requirements of a tiling."""
    return [
        [
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 3))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 4))),
            GriddedPerm((1, 0, 2), ((0, 0), (1, 0), (2, 3))),
            GriddedPerm((1, 0, 2), ((0, 1), (1, 0), (2, 3))),
        ],
        [
            GriddedPerm((0, 1, 2), ((2, 3), (2, 3), (2, 3))),
            GriddedPerm((1, 0, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
        ],
        [
            GriddedPerm((0, 1), ((1, 0), (3, 0))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((0, 1), ((2, 0), (3, 0))),
            GriddedPerm((0, 1), ((2, 0), (3, 1))),
        ],
        [
            GriddedPerm((1, 0), ((3, 3), (3, 1))),
            GriddedPerm((1, 0), ((3, 1), (3, 1))),
            GriddedPerm((1, 0), ((3, 1), (3, 0))),
        ],
    ]


@pytest.fixture
def typical_obstructions_with_local():
    return [
        GriddedPerm((0, 1), ((1, 0), (1, 0))),
        GriddedPerm((0, 1), ((1, 0), (2, 0))),
        GriddedPerm((0, 1), ((1, 0), (3, 0))),
        GriddedPerm((0, 1), ((2, 0), (2, 0))),
        GriddedPerm((0, 1), ((2, 0), (3, 0))),
        GriddedPerm((0, 1), ((3, 1), (3, 1))),
        GriddedPerm((0, 2, 1), ((3, 0), (3, 0), (3, 0))),
        GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (3, 1))),
        GriddedPerm((1, 2, 0), ((1, 0), (1, 0), (1, 0))),
        GriddedPerm((3, 2, 1, 0), ((1, 1), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((3, 2, 1, 0), ((2, 1), (2, 1), (3, 0), (3, 0))),
    ]


@pytest.fixture
def typical_requirements_with_local():
    """Return a very typical list of requirements of a tiling, including some
    local length 1 requirements."""
    return [
        [
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 3))),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 4))),
            GriddedPerm((1, 0, 2), ((0, 0), (1, 0), (2, 3))),
            GriddedPerm((1, 0, 2), ((0, 1), (1, 0), (2, 3))),
        ],
        [
            GriddedPerm((0, 1), ((1, 0), (3, 0))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
            GriddedPerm((0, 1), ((2, 0), (3, 0))),
            GriddedPerm((0, 1), ((2, 0), (3, 1))),
        ],
        [GriddedPerm((0,), ((3, 0),))],
        [GriddedPerm((1, 0), ((2, 0), (2, 0)))],
        [GriddedPerm((0, 2, 1), ((0, 0), (2, 3), (2, 3)))],
    ]

from itertools import chain

import pytest

from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST
from tilings import GriddedPerm, Tiling
from tilings.algorithms import RequirementPlacement

# ------------------------------------------------
#      Fixture and utility
# ------------------------------------------------


@pytest.fixture
def tiling1():
    t = Tiling(
        obstructions=(
            GriddedPerm((2, 1, 0), ((0, 0),) * 3),
            GriddedPerm((0, 1, 2), ((1, 2),) * 3),
            GriddedPerm((2, 0, 1), ((3, 0),) * 3),
            GriddedPerm((1, 0), ((1, 1),) * 2),
            GriddedPerm((1, 0), ((2, 2),) * 2),
            GriddedPerm((0, 1), ((1, 1), (2, 2))),
        )
    )
    return t


@pytest.fixture
def tiling2():
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), ((0, 0),) * 2),
            GriddedPerm((0, 1), ((0, 1),) * 2),
            GriddedPerm((0, 1), ((1, 0),) * 2),
            GriddedPerm((0, 1), ((1, 1),) * 2),
            GriddedPerm((0, 1), ((3, 3),) * 2),
            GriddedPerm((0, 1), ((4, 3),) * 2),
            GriddedPerm((0, 1), ((4, 3),) * 2),
            GriddedPerm((0, 1, 2), ((2, 3),) * 3),
            GriddedPerm((0, 1, 2), ((2, 2),) * 3),
            GriddedPerm((0, 1, 2), ((3, 2),) * 3),
            GriddedPerm((0, 1, 2), ((4, 2),) * 3),
            GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 1))),
            GriddedPerm((0, 1, 2), ((2, 2), (3, 2), (4, 2))),
            GriddedPerm((0, 1), ((0, 1), (1, 1))),
        ],
        requirements=[
            [GriddedPerm((0, 1), ((0, 0), (0, 1)))],
            [
                GriddedPerm((0, 1), ((2, 3), (3, 3))),
                GriddedPerm((0, 1), ((3, 3), (4, 3))),
            ],
        ],
    )
    return t


@pytest.fixture
def placement1(tiling1):
    return RequirementPlacement(tiling1)


@pytest.fixture
def placement1ownrow(tiling1):
    return RequirementPlacement(tiling1, own_row=True, own_col=False)


@pytest.fixture
def placement1owncol(tiling1):
    return RequirementPlacement(tiling1, own_row=False, own_col=True)


@pytest.fixture
def placement2(tiling2):
    return RequirementPlacement(tiling2)


@pytest.fixture
def placement2ownrow(tiling2):
    return RequirementPlacement(tiling2, own_row=True, own_col=False)


@pytest.fixture
def placement2owncol(tiling2):
    return RequirementPlacement(tiling2, own_row=False, own_col=True)


@pytest.fixture
def placement_only_west():
    t = Tiling(
        obstructions=[GriddedPerm((0, 1, 2), ((0, 0),) * 3)],
        requirements=[[GriddedPerm((0,), ((0, 0),))]],
    )
    return RequirementPlacement(t, dirs=[DIR_WEST])


@pytest.fixture
def gp1():
    return GriddedPerm((3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (1, 0), (1, 1)))


# ------------------------------------------------------------
#       Tests for RequirementPlacement Class
# ------------------------------------------------------------


def test_col_placement(placement1):
    print(placement1._tiling)
    tilings = placement1.col_placement(1, DIR_WEST)
    assert len(tilings) == 2
    assert all(isinstance(t, Tiling) for t in tilings)


def test_row_placement(placement1):
    print(placement1._tiling)
    tilings = placement1.row_placement(1, DIR_NORTH)
    assert len(tilings) == 1
    assert all(isinstance(t, Tiling) for t in tilings)


def test_empty_row(placement1):
    t = Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((2, 0),)),
            GriddedPerm((0,), ((3, 1),)),
            GriddedPerm((1, 0), ((2, 1), (2, 1))),
            GriddedPerm((0, 1, 2), ((1, 1), (1, 1), (1, 1))),
            GriddedPerm((2, 0, 1), ((3, 0), (3, 0), (3, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),
        ),
    )
    assert placement1.empty_row(1) == t


def test_empty_col(placement1):
    t = Tiling(
        obstructions=(
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((0, 2),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((1, 1),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0,), ((2, 2),)),
            GriddedPerm((1, 0), ((1, 2), (1, 2))),
            GriddedPerm((2, 0, 1), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),
        ),
        requirements=(),
    )
    print(t)
    print(placement1._tiling)
    assert placement1.empty_col(1) == t


def test_point_translation(gp1, placement1, placement1owncol, placement1ownrow):
    assert placement1._point_translation(gp1, 2, (0, 3)) == (3, 1)
    assert placement1._point_translation(gp1, 2, (1, 2)) == (3, 3)
    assert placement1._point_translation(gp1, 2, (2, 2)) == (3, 3)
    assert placement1._point_translation(gp1, 2, (3, 0)) == (1, 3)
    assert placement1._point_translation(gp1, 2, (4, 4)) == (1, 1)

    assert placement1owncol._point_translation(gp1, 2, (0, 3)) == (3, 1)
    assert placement1owncol._point_translation(gp1, 2, (1, 2)) == (3, 1)
    assert placement1owncol._point_translation(gp1, 2, (2, 2)) == (3, 1)
    assert placement1owncol._point_translation(gp1, 2, (3, 0)) == (1, 1)
    assert placement1owncol._point_translation(gp1, 2, (4, 4)) == (1, 1)

    assert placement1ownrow._point_translation(gp1, 2, (0, 3)) == (1, 1)
    assert placement1ownrow._point_translation(gp1, 2, (1, 2)) == (1, 3)
    assert placement1ownrow._point_translation(gp1, 2, (2, 2)) == (1, 3)
    assert placement1ownrow._point_translation(gp1, 2, (3, 0)) == (1, 3)
    assert placement1ownrow._point_translation(gp1, 2, (4, 4)) == (1, 1)


def test_gridded_perm_translation(gp1, placement1, placement1owncol, placement1ownrow):
    assert placement1._gridded_perm_translation(gp1, (0, 3)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((2, 3), (2, 0), (3, 1), (3, 0), (3, 3))
    )
    assert placement1._gridded_perm_translation(gp1, (1, 1)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (2, 2), (3, 3), (3, 0), (3, 3))
    )
    assert placement1._gridded_perm_translation(gp1, (2, 2)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (0, 0), (3, 3), (3, 0), (3, 3))
    )
    assert placement1._gridded_perm_translation(gp1, (3, 0)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (0, 2), (1, 3), (3, 2), (3, 3))
    )
    assert placement1._gridded_perm_translation(gp1, (4, 4)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (1, 0), (3, 3))
    )
    assert placement1owncol._gridded_perm_translation(gp1, (0, 3)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((2, 1), (2, 0), (3, 1), (3, 0), (3, 1))
    )
    assert placement1owncol._gridded_perm_translation(gp1, (1, 1)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 1), (2, 0), (3, 1), (3, 0), (3, 1))
    )
    assert placement1owncol._gridded_perm_translation(gp1, (2, 2)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 1), (0, 0), (3, 1), (3, 0), (3, 1))
    )
    assert placement1owncol._gridded_perm_translation(gp1, (3, 0)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (3, 0), (3, 1))
    )
    assert placement1owncol._gridded_perm_translation(gp1, (4, 4)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (1, 0), (3, 1))
    )
    assert placement1ownrow._gridded_perm_translation(gp1, (0, 3)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (0, 0), (1, 1), (1, 0), (1, 3))
    )
    assert placement1ownrow._gridded_perm_translation(gp1, (1, 1)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (0, 2), (1, 3), (1, 0), (1, 3))
    )
    assert placement1ownrow._gridded_perm_translation(gp1, (2, 2)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (0, 0), (1, 3), (1, 0), (1, 3))
    )
    assert placement1ownrow._gridded_perm_translation(gp1, (3, 0)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (0, 2), (1, 3), (1, 2), (1, 3))
    )
    assert placement1ownrow._gridded_perm_translation(gp1, (4, 4)) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (1, 0), (1, 3))
    )


def test_gridded_perm_translation_with_point(
    gp1, placement1, placement1owncol, placement1ownrow
):
    assert placement1._gridded_perm_translation_with_point(gp1, 0) == GriddedPerm(
        (3, 1, 2, 0, 4), ((1, 2), (2, 0), (3, 1), (3, 0), (3, 3))
    )
    assert placement1._gridded_perm_translation_with_point(gp1, 1) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (1, 1), (3, 3), (3, 0), (3, 3))
    )
    assert placement1._gridded_perm_translation_with_point(gp1, 2) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (0, 0), (2, 2), (3, 0), (3, 3))
    )
    assert placement1._gridded_perm_translation_with_point(gp1, 3) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (0, 2), (1, 3), (2, 1), (3, 3))
    )
    assert placement1._gridded_perm_translation_with_point(gp1, 4) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (1, 0), (2, 2))
    )
    assert placement1ownrow._gridded_perm_translation_with_point(gp1, 0) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 2), (0, 0), (1, 1), (1, 0), (1, 3))
    )
    assert placement1ownrow._gridded_perm_translation_with_point(gp1, 1) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (0, 1), (1, 3), (1, 0), (1, 3))
    )
    assert placement1ownrow._gridded_perm_translation_with_point(gp1, 2) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (0, 0), (1, 2), (1, 0), (1, 3))
    )
    assert placement1ownrow._gridded_perm_translation_with_point(gp1, 3) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 3), (0, 2), (1, 3), (1, 1), (1, 3))
    )
    assert placement1ownrow._gridded_perm_translation_with_point(gp1, 4) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (1, 0), (1, 2))
    )
    assert placement1owncol._gridded_perm_translation_with_point(gp1, 0) == GriddedPerm(
        (3, 1, 2, 0, 4), ((1, 1), (2, 0), (3, 1), (3, 0), (3, 1))
    )
    assert placement1owncol._gridded_perm_translation_with_point(gp1, 1) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 1), (1, 0), (3, 1), (3, 0), (3, 1))
    )
    assert placement1owncol._gridded_perm_translation_with_point(gp1, 2) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 1), (0, 0), (2, 1), (3, 0), (3, 1))
    )
    assert placement1owncol._gridded_perm_translation_with_point(gp1, 3) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (2, 0), (3, 1))
    )
    assert placement1owncol._gridded_perm_translation_with_point(gp1, 4) == GriddedPerm(
        (3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (1, 0), (2, 1))
    )


def test_placed_cell(placement1, placement1owncol, placement1ownrow):
    assert placement1._placed_cell((0, 0)) == (1, 1)
    assert placement1._placed_cell((3, 2)) == (4, 3)
    assert placement1owncol._placed_cell((9, 7)) == (10, 7)
    assert placement1owncol._placed_cell((2, 1)) == (3, 1)
    assert placement1ownrow._placed_cell((0, 4)) == (0, 5)
    assert placement1ownrow._placed_cell((4, 2)) == (4, 3)


def test_point_obstructions(placement1, placement1owncol, placement1ownrow):
    assert placement1._point_obstructions((0, 0)) == [
        GriddedPerm((0, 1), ((1, 1), (1, 1))),
        GriddedPerm((1, 0), ((1, 1), (1, 1))),
    ]
    assert placement1owncol._point_obstructions((0, 0)) == [
        GriddedPerm((0, 1), ((1, 0), (1, 0))),
        GriddedPerm((1, 0), ((1, 0), (1, 0))),
    ]
    assert placement1ownrow._point_obstructions((0, 0)) == [
        GriddedPerm((0, 1), ((0, 1), (0, 1))),
        GriddedPerm((1, 0), ((0, 1), (0, 1))),
    ]


def test_point_requirements(placement1, placement1owncol, placement1ownrow):
    assert placement1._point_requirements((2, 3)) == [[GriddedPerm((0,), ((3, 4),))]]
    assert placement1ownrow._point_requirements((2, 3)) == [
        [GriddedPerm((0,), ((2, 4),))]
    ]
    assert placement1owncol._point_requirements((2, 3)) == [
        [GriddedPerm((0,), ((3, 3),))]
    ]


def test_stretch_gridded_perm(gp1, placement1, placement1owncol, placement1ownrow):
    assert set(placement1._stretch_gridded_perm(gp1, (0, 0))) == set(
        [
            GriddedPerm((3, 1, 2, 0, 4), ((2, 3), (2, 2), (3, 3), (3, 2), (3, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((2, 3), (2, 2), (3, 3), (3, 0), (3, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((2, 3), (2, 0), (3, 3), (3, 0), (3, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (2, 2), (3, 3), (3, 2), (3, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (2, 2), (3, 3), (3, 0), (3, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (2, 0), (3, 3), (3, 0), (3, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 2), (3, 3), (3, 2), (3, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 2), (3, 3), (3, 0), (3, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 0), (3, 3), (3, 0), (3, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (1, 1), (3, 3), (3, 0), (3, 3))),
        ]
    )
    assert set(placement1owncol._stretch_gridded_perm(gp1, (1, 0))) == set(
        [
            GriddedPerm((3, 1, 2, 0, 4), ((0, 1), (0, 0), (3, 1), (3, 0), (3, 1))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (3, 0), (3, 1))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (1, 0), (3, 1))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (2, 0), (3, 1))),
        ]
    )
    assert set(placement1ownrow._stretch_gridded_perm(gp1, (1, 1))) == set(
        [
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 0), (1, 3), (1, 0), (1, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 0), (1, 1), (1, 0), (1, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (1, 0), (1, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (1, 0), (1, 1))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 0), (1, 2), (1, 0), (1, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 1), (0, 0), (1, 1), (1, 0), (1, 2))),
        ]
    )


def test_stretch_gridded_perms(placement1, placement1owncol, placement1ownrow):
    gps = [
        GriddedPerm((0, 1), [(0, 0), (1, 1)]),
        GriddedPerm((0, 1), [(1, 1), (2, 2)]),
    ]
    for p in (placement1, placement1ownrow, placement1owncol):
        assert set(p._stretch_gridded_perms(gps, (1, 1))) == set(
            chain.from_iterable(p._stretch_gridded_perm(gp, (1, 1)) for gp in gps)
        )


def test_stretched_obstructions(placement1, placement1owncol, placement1ownrow):
    orig_obs = placement1._tiling.obstructions
    assert sorted(placement1.stretched_obstructions((1, 1))) == sorted(
        placement1._stretch_gridded_perms(orig_obs, (1, 1))
    )
    assert sorted(placement1owncol.stretched_obstructions((1, 1))) == sorted(
        placement1owncol._stretch_gridded_perms(orig_obs, (1, 1))
    )
    assert sorted(placement1ownrow.stretched_obstructions((1, 1))) == sorted(
        placement1ownrow._stretch_gridded_perms(orig_obs, (1, 1))
    )


def test_stretched_requirements(placement1, placement1owncol, placement1ownrow):
    orig_reqs = placement1._tiling.requirements
    assert sorted(placement1.stretched_requirements((1, 1))) == sorted(
        placement1._stretch_gridded_perms(orig_reqs, (1, 1))
    )
    orig_reqs = placement1owncol._tiling.requirements
    assert sorted(placement1owncol.stretched_requirements((1, 1))) == sorted(
        placement1owncol._stretch_gridded_perms(orig_reqs, (1, 1))
    )
    orig_reqs = placement1ownrow._tiling.requirements
    assert sorted(placement1ownrow.stretched_requirements((1, 1))) == sorted(
        placement1ownrow._stretch_gridded_perms(orig_reqs, (1, 1))
    )


def test_stretched_obstructions_and_assumptions(
    placement1, placement1owncol, placement1ownrow
):
    obs, reqs, _ = placement1._stretched_obstructions_requirements_and_assumptions(
        (1, 1)
    )
    assert set(obs) == set(
        placement1.stretched_obstructions((1, 1))
        + [
            GriddedPerm.single_cell((0, 1), (2, 2)),
            GriddedPerm.single_cell((1, 0), (2, 2)),
        ]
    )
    assert sorted(reqs) == sorted(
        placement1.stretched_requirements((1, 1)) + [[GriddedPerm((0,), ((2, 2),))]]
    )
    (
        obs,
        reqs,
        _,
    ) = placement1ownrow._stretched_obstructions_requirements_and_assumptions((1, 1))
    assert set(obs) == set(
        placement1ownrow.stretched_obstructions((1, 1))
        + [
            GriddedPerm.single_cell((0, 1), (1, 2)),
            GriddedPerm.single_cell((1, 0), (1, 2)),
        ]
    )
    assert sorted(reqs) == sorted(
        placement1ownrow.stretched_requirements((1, 1))
        + [[GriddedPerm((0,), ((1, 2),))]]
    )
    (
        obs,
        reqs,
        _,
    ) = placement1owncol._stretched_obstructions_requirements_and_assumptions((1, 1))
    assert set(obs) == set(
        placement1owncol.stretched_obstructions((1, 1))
        + [
            GriddedPerm.single_cell((0, 1), (2, 1)),
            GriddedPerm.single_cell((1, 0), (2, 1)),
        ]
    )
    assert sorted(reqs) == sorted(
        placement1owncol.stretched_requirements((1, 1))
        + [[GriddedPerm((0,), ((2, 1),))]]
    )


def farther(placement1):
    assert placement1._farther((0, 0), (2, 0), DIR_EAST) is False
    assert placement1._farther((0, 0), (2, 0), DIR_NORTH) is False
    assert placement1._farther((0, 0), (2, 0), DIR_WEST) is True
    assert placement1._farther((0, 0), (2, 0), DIR_SOUTH) is False

    assert placement1._farther((2, 3), (2, 0), DIR_EAST) is False
    assert placement1._farther((2, 3), (2, 0), DIR_NORTH) is True
    assert placement1._farther((2, 3), (2, 0), DIR_WEST) is False
    assert placement1._farther((2, 3), (2, 0), DIR_SOUTH) is False

    assert placement1._farther((1, 1), (3, 4), DIR_EAST) is False
    assert placement1._farther((1, 1), (3, 4), DIR_NORTH) is False
    assert placement1._farther((1, 1), (3, 4), DIR_WEST) is True
    assert placement1._farther((1, 1), (3, 4), DIR_SOUTH) is True

    assert placement1._farther((1, 5), (3, 4), DIR_EAST) is False
    assert placement1._farther((1, 5), (3, 4), DIR_NORTH) is True
    assert placement1._farther((1, 5), (3, 4), DIR_WEST) is True
    assert placement1._farther((1, 5), (3, 4), DIR_SOUTH) is False

    assert placement1._farther((2, 2), (1, 1), DIR_EAST) is True
    assert placement1._farther((2, 2), (1, 1), DIR_NORTH) is True
    assert placement1._farther((2, 2), (1, 1), DIR_WEST) is False
    assert placement1._farther((2, 2), (1, 1), DIR_SOUTH) is False


def test_forced_obstructions_from_patt(
    gp1, placement1, placement1owncol, placement1ownrow
):
    assert set(
        placement1.forced_obstructions_from_requirement(
            (gp1,), (2,), gp1.pos[2], DIR_NORTH
        )
    ) == set(
        [
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 0), (3, 3), (3, 0), (3, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 0), (1, 3), (3, 0), (3, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 0), (1, 3), (1, 0), (3, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 0), (1, 3), (1, 0), (1, 3))),
        ]
    )

    assert set(
        placement1owncol.forced_obstructions_from_requirement(
            (gp1,), (1,), gp1.pos[1], DIR_EAST
        )
    ) == set(
        [
            GriddedPerm((3, 1, 2, 0, 4), ((2, 1), (2, 0), (3, 1), (3, 0), (3, 1))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 1), (2, 0), (3, 1), (3, 0), (3, 1))),
        ]
    )

    assert set(
        placement1ownrow.forced_obstructions_from_requirement(
            (gp1,), (3,), gp1.pos[3], DIR_SOUTH
        )
    ) == set(
        [
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 2), (1, 3), (1, 0), (1, 3))),
            GriddedPerm((3, 1, 2, 0, 4), ((0, 3), (0, 0), (1, 3), (1, 0), (1, 3))),
        ]
    )


def test_forced_obstructions_from_list(
    gp1, placement1, placement1owncol, placement1ownrow
):
    req_list_row = [
        GriddedPerm((0,), ((0, 0),)),
        GriddedPerm((0,), ((1, 0),)),
    ]
    assert set(
        placement1.forced_obstructions_from_requirement(
            req_list_row, (0, 0), (0, 0), DIR_NORTH
        )
    ) == set(
        [
            GriddedPerm((0,), ((0, 2),)),
            GriddedPerm((0,), ((2, 2),)),
            GriddedPerm((0,), ((3, 2),)),
        ]
    )
    assert set(
        placement1.forced_obstructions_from_requirement(
            req_list_row, (0, 0), (0, 0), DIR_SOUTH
        )
    ) == set(
        [
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((2, 0),)),
            GriddedPerm((0,), ((3, 0),)),
        ]
    )
    assert set(
        placement1.forced_obstructions_from_requirement(
            req_list_row, (0, 0), (1, 0), DIR_NORTH
        )
    ) == set(
        [
            GriddedPerm((0,), ((0, 2),)),
            GriddedPerm((0,), ((1, 2),)),
            GriddedPerm((0,), ((3, 2),)),
        ]
    )
    assert set(
        placement1.forced_obstructions_from_requirement(
            req_list_row, (0, 0), (1, 0), DIR_SOUTH
        )
    ) == set(
        [
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((1, 0),)),
            GriddedPerm((0,), ((3, 0),)),
        ]
    )
    assert set(
        placement1ownrow.forced_obstructions_from_requirement(
            req_list_row, (0, 0), (0, 0), DIR_NORTH
        )
    ) == set([GriddedPerm((0,), ((0, 2),)), GriddedPerm((0,), ((1, 2),))])
    assert set(
        placement1ownrow.forced_obstructions_from_requirement(
            req_list_row, (0, 0), (0, 0), DIR_SOUTH
        )
    ) == set([GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))])
    assert set(
        placement1ownrow.forced_obstructions_from_requirement(
            req_list_row, (0, 0), (1, 0), DIR_NORTH
        )
    ) == set([GriddedPerm((0,), ((0, 2),)), GriddedPerm((0,), ((1, 2),))])
    assert set(
        placement1ownrow.forced_obstructions_from_requirement(
            req_list_row, (0, 0), (1, 0), DIR_SOUTH
        )
    ) == set([GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((1, 0),))])

    req_list_col = [
        GriddedPerm((0,), ((0, 0),)),
        GriddedPerm((0,), ((0, 1),)),
    ]
    assert set(
        placement1.forced_obstructions_from_requirement(
            req_list_col, (0, 0), (0, 0), DIR_EAST
        )
    ) == set(
        [
            GriddedPerm((0,), ((2, 0),)),
            GriddedPerm((0,), ((2, 2),)),
            GriddedPerm((0,), ((2, 3),)),
        ]
    )
    assert set(
        placement1.forced_obstructions_from_requirement(
            req_list_col, (0, 0), (0, 0), DIR_WEST
        )
    ) == set(
        [
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((0, 2),)),
            GriddedPerm((0,), ((0, 3),)),
        ]
    )
    assert set(
        placement1.forced_obstructions_from_requirement(
            req_list_col, (0, 0), (0, 1), DIR_EAST
        )
    ) == set(
        [
            GriddedPerm((0,), ((2, 0),)),
            GriddedPerm((0,), ((2, 1),)),
            GriddedPerm((0,), ((2, 3),)),
        ]
    )
    assert set(
        placement1.forced_obstructions_from_requirement(
            req_list_col, (0, 0), (0, 1), DIR_WEST
        )
    ) == set(
        [
            GriddedPerm((0,), ((0, 0),)),
            GriddedPerm((0,), ((0, 1),)),
            GriddedPerm((0,), ((0, 3),)),
        ]
    )
    assert set(
        placement1owncol.forced_obstructions_from_requirement(
            req_list_col, (0, 0), (0, 0), DIR_EAST
        )
    ) == set([GriddedPerm((0,), ((2, 0),)), GriddedPerm((0,), ((2, 1),))])
    assert set(
        placement1owncol.forced_obstructions_from_requirement(
            req_list_col, (0, 0), (0, 0), DIR_WEST
        )
    ) == set([GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((0, 1),))])
    assert set(
        placement1owncol.forced_obstructions_from_requirement(
            req_list_col, (0, 0), (0, 1), DIR_EAST
        )
    ) == set([GriddedPerm((0,), ((2, 0),)), GriddedPerm((0,), ((2, 1),))])
    assert set(
        placement1owncol.forced_obstructions_from_requirement(
            req_list_col, (0, 0), (0, 1), DIR_WEST
        )
    ) == set([GriddedPerm((0,), ((0, 0),)), GriddedPerm((0,), ((0, 1),))])

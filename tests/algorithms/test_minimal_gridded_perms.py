import pytest

from permuta import Perm
from tilings import GriddedPerm, Obstruction, Requirement, Tiling
from tilings.algorithms import MinimalGriddedPerms


@pytest.fixture
def t1():
    """Testing glueing indep cells"""
    return Tiling(
        obstructions=(
            Obstruction(Perm((0,)), ((0, 1),)),
            Obstruction(Perm((0,)), ((1, 0),)),
            Obstruction(Perm((0,)), ((1, 2),)),
            Obstruction(Perm((0, 1)), ((1, 1), (1, 1))),
            Obstruction(Perm((1, 0)), ((1, 1), (1, 1))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 2))),
            Obstruction(Perm((0, 2, 1)), ((0, 2), (0, 2), (0, 2))),
            Obstruction(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 2))),
            Obstruction(Perm((1, 2, 0)), ((0, 0), (0, 2), (0, 0))),
            Obstruction(Perm((1, 2, 0)), ((0, 2), (0, 2), (0, 0))),
            Obstruction(Perm((0, 1, 3, 2)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((1, 0, 3, 2)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((1, 3, 0, 2)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((1, 3, 2, 0)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((2, 3, 0, 1)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((2, 3, 0, 1)), ((0, 2), (0, 2), (0, 2), (0, 2))),
        ),
        requirements=(
            (Requirement(Perm((0,)), ((1, 1),)),),
            (
                Requirement(Perm((1, 0)), ((0, 2), (0, 2))),
                Requirement(Perm((2, 1, 0)), ((0, 0), (0, 0), (0, 0))),
                Requirement(Perm((2, 1, 0)), ((0, 2), (0, 0), (0, 0))),
            ),
        ),
    )


@pytest.fixture
def mg1():
    return frozenset(
        [
            GriddedPerm(Perm((2, 1, 0)), ((0, 2), (0, 2), (1, 1))),
            GriddedPerm(Perm((2, 1, 0, 3)), ((0, 0), (0, 0), (0, 0), (1, 1))),
            GriddedPerm(Perm((3, 1, 0, 2)), ((0, 2), (0, 0), (0, 0), (1, 1))),
        ]
    )


@pytest.fixture
def t2():
    """Make sure you generate all minimal gridded perms"""
    return Tiling(
        obstructions=(
            Obstruction(Perm((0,)), ((0, 0),)),
            Obstruction(Perm((0,)), ((0, 2),)),
            Obstruction(Perm((0,)), ((1, 0),)),
            Obstruction(Perm((0,)), ((1, 1),)),
            Obstruction(Perm((0,)), ((1, 3),)),
            Obstruction(Perm((0,)), ((2, 0),)),
            Obstruction(Perm((0,)), ((2, 1),)),
            Obstruction(Perm((0,)), ((2, 2),)),
            Obstruction(Perm((0,)), ((3, 1),)),
            Obstruction(Perm((0,)), ((3, 2),)),
            Obstruction(Perm((0,)), ((3, 3),)),
            Obstruction(Perm((0, 1)), ((1, 2), (1, 2))),
            Obstruction(Perm((0, 1)), ((2, 3), (2, 3))),
            Obstruction(Perm((0, 1)), ((3, 0), (3, 0))),
            Obstruction(Perm((1, 0)), ((1, 2), (1, 2))),
            Obstruction(Perm((0, 1, 2)), ((0, 1), (0, 1), (0, 3))),
            Obstruction(Perm((0, 1, 2)), ((0, 1), (0, 3), (0, 3))),
            Obstruction(Perm((0, 1, 2)), ((0, 1), (0, 3), (2, 3))),
            Obstruction(Perm((0, 2, 1)), ((0, 1), (0, 1), (0, 1))),
            Obstruction(Perm((0, 2, 1)), ((0, 1), (0, 3), (0, 3))),
            Obstruction(Perm((0, 2, 1)), ((0, 1), (2, 3), (2, 3))),
            Obstruction(Perm((1, 0, 2)), ((0, 3), (0, 1), (0, 3))),
            Obstruction(Perm((1, 2, 0)), ((0, 3), (2, 3), (2, 3))),
            Obstruction(Perm((2, 0, 1)), ((0, 1), (0, 1), (0, 1))),
            Obstruction(Perm((2, 0, 1)), ((0, 3), (0, 1), (0, 3))),
            Obstruction(Perm((2, 1, 0)), ((0, 3), (2, 3), (2, 3))),
            Obstruction(Perm((2, 1, 0)), ((2, 3), (2, 3), (2, 3))),
            Obstruction(Perm((0, 1, 3, 2)), ((0, 3), (0, 3), (0, 3), (0, 3))),
            Obstruction(Perm((0, 1, 3, 2)), ((0, 3), (0, 3), (0, 3), (2, 3))),
            Obstruction(Perm((0, 1, 3, 2)), ((0, 3), (0, 3), (2, 3), (2, 3))),
            Obstruction(Perm((0, 2, 1, 3)), ((0, 3), (0, 3), (0, 3), (0, 3))),
            Obstruction(Perm((0, 2, 1, 3)), ((0, 3), (0, 3), (0, 3), (2, 3))),
            Obstruction(Perm((0, 2, 3, 1)), ((0, 3), (0, 3), (0, 3), (0, 3))),
            Obstruction(Perm((0, 2, 3, 1)), ((0, 3), (0, 3), (0, 3), (2, 3))),
            Obstruction(Perm((0, 3, 2, 1)), ((0, 3), (0, 3), (0, 3), (0, 3))),
            Obstruction(Perm((0, 3, 2, 1)), ((0, 3), (0, 3), (0, 3), (2, 3))),
            Obstruction(Perm((2, 0, 3, 1)), ((0, 3), (0, 3), (0, 3), (0, 3))),
            Obstruction(Perm((2, 0, 3, 1)), ((0, 3), (0, 3), (0, 3), (2, 3))),
            Obstruction(Perm((3, 0, 2, 1)), ((0, 3), (0, 3), (0, 3), (0, 3))),
            Obstruction(Perm((3, 0, 2, 1)), ((0, 3), (0, 3), (0, 3), (2, 3))),
        ),
        requirements=(
            (Requirement(Perm((0,)), ((1, 2),)),),
            (Requirement(Perm((0,)), ((2, 3),)),),
            (
                Requirement(Perm((1, 0)), ((0, 3), (0, 1))),
                Requirement(Perm((1, 0)), ((0, 3), (2, 3))),
                Requirement(Perm((2, 0, 1)), ((0, 3), (0, 3), (0, 3))),
            ),
        ),
    )


@pytest.fixture
def mg2():
    return frozenset(
        [
            GriddedPerm(Perm((2, 0, 1)), ((0, 3), (1, 2), (2, 3))),
            GriddedPerm(Perm((2, 0, 1, 3)), ((0, 3), (0, 1), (1, 2), (2, 3))),
            GriddedPerm(
                Perm((3, 1, 2, 0, 4)), ((0, 3), (0, 3), (0, 3), (1, 2), (2, 3))
            ),
        ]
    )


@pytest.fixture
def t3():
    """Avoid duplicate work"""
    return Tiling(
        obstructions=(
            Obstruction(Perm((0,)), ((0, 1),)),
            Obstruction(Perm((0,)), ((1, 0),)),
            Obstruction(Perm((0,)), ((2, 1),)),
            Obstruction(Perm((0, 1)), ((1, 1), (1, 1))),
            Obstruction(Perm((1, 0)), ((1, 1), (1, 1))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (2, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 2, 1)), ((0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((0, 2, 1)), ((0, 0), (0, 0), (2, 0))),
            Obstruction(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((1, 2, 0)), ((0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((1, 2, 0)), ((0, 0), (0, 0), (2, 0))),
            Obstruction(Perm((0, 1, 2, 3)), ((2, 0), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 1, 3, 2)), ((2, 0), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 2, 1, 3)), ((2, 0), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 2, 3, 1)), ((2, 0), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 3, 1, 2)), ((2, 0), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((1, 0, 2, 3)), ((2, 0), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((1, 2, 0, 3)), ((2, 0), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((1, 2, 3, 0)), ((2, 0), (2, 0), (2, 0), (2, 0))),
        ),
        requirements=(
            (Requirement(Perm((0,)), ((1, 1),)),),
            (Requirement(Perm((0,)), ((2, 0),)),),
            (Requirement(Perm((2, 1, 0)), ((0, 0), (0, 0), (0, 0))),),
        ),
    )


@pytest.fixture
def mg3():
    return frozenset(
        [
            GriddedPerm(
                Perm((2, 1, 0, 4, 3)), ((0, 0), (0, 0), (0, 0), (1, 1), (2, 0))
            ),
            GriddedPerm(
                Perm((3, 1, 0, 4, 2)), ((0, 0), (0, 0), (0, 0), (1, 1), (2, 0))
            ),
            GriddedPerm(
                Perm((3, 2, 0, 4, 1)), ((0, 0), (0, 0), (0, 0), (1, 1), (2, 0))
            ),
            GriddedPerm(
                Perm((3, 2, 1, 4, 0)), ((0, 0), (0, 0), (0, 0), (1, 1), (2, 0))
            ),
        ]
    )


@pytest.fixture
def t4():
    """Skips a level"""
    return Tiling(
        obstructions=(
            Obstruction(Perm((0,)), ((0, 0),)),
            Obstruction(Perm((0,)), ((0, 2),)),
            Obstruction(Perm((0,)), ((1, 0),)),
            Obstruction(Perm((0,)), ((1, 1),)),
            Obstruction(Perm((0,)), ((1, 3),)),
            Obstruction(Perm((0,)), ((2, 0),)),
            Obstruction(Perm((0,)), ((2, 1),)),
            Obstruction(Perm((0,)), ((2, 2),)),
            Obstruction(Perm((0,)), ((3, 1),)),
            Obstruction(Perm((0,)), ((3, 2),)),
            Obstruction(Perm((0,)), ((3, 3),)),
            Obstruction(Perm((0, 1)), ((0, 3), (0, 3))),
            Obstruction(Perm((0, 1)), ((1, 2), (1, 2))),
            Obstruction(Perm((0, 1)), ((2, 3), (2, 3))),
            Obstruction(Perm((0, 1)), ((3, 0), (3, 0))),
            Obstruction(Perm((1, 0)), ((1, 2), (1, 2))),
            Obstruction(Perm((0, 1, 2)), ((0, 1), (0, 3), (2, 3))),
            Obstruction(Perm((0, 2, 1)), ((0, 1), (0, 1), (0, 1))),
            Obstruction(Perm((0, 2, 1)), ((0, 3), (2, 3), (2, 3))),
            Obstruction(Perm((1, 0, 2)), ((0, 1), (0, 1), (0, 3))),
            Obstruction(Perm((1, 2, 0)), ((0, 3), (2, 3), (2, 3))),
            Obstruction(Perm((2, 0, 1)), ((0, 3), (0, 1), (0, 3))),
            Obstruction(Perm((2, 1, 0)), ((0, 3), (2, 3), (2, 3))),
            Obstruction(Perm((1, 0, 3, 2)), ((0, 1), (0, 1), (2, 3), (2, 3))),
        ),
        requirements=(
            (Requirement(Perm((0,)), ((1, 2),)),),
            (Requirement(Perm((0,)), ((2, 3),)),),
            (
                Requirement(Perm((0,)), ((3, 0),)),
                Requirement(Perm((1, 2, 0)), ((0, 1), (0, 1), (0, 1))),
                Requirement(Perm((1, 2, 0)), ((0, 1), (0, 3), (0, 1))),
            ),
        ),
    )


@pytest.fixture
def mg4():
    return frozenset(
        [
            GriddedPerm(Perm((1, 2, 0)), ((1, 2), (2, 3), (3, 0))),
            GriddedPerm(
                Perm((1, 2, 0, 3, 4)), ((0, 1), (0, 1), (0, 1), (1, 2), (2, 3))
            ),
            GriddedPerm(
                Perm((1, 4, 0, 2, 3)), ((0, 1), (0, 3), (0, 1), (1, 2), (2, 3))
            ),
        ]
    )


@pytest.fixture
def t5():
    """careful about skipping undone work!"""
    return Tiling(
        obstructions=(
            Obstruction(Perm((0,)), ((0, 1),)),
            Obstruction(Perm((0,)), ((1, 0),)),
            Obstruction(Perm((0,)), ((1, 2),)),
            Obstruction(Perm((0,)), ((2, 1),)),
            Obstruction(Perm((0,)), ((2, 2),)),
            Obstruction(Perm((0,)), ((3, 0),)),
            Obstruction(Perm((0,)), ((3, 1),)),
            Obstruction(Perm((0, 1)), ((1, 1), (1, 1))),
            Obstruction(Perm((1, 0)), ((1, 1), (1, 1))),
            Obstruction(Perm((1, 0)), ((2, 0), (2, 0))),
            Obstruction(Perm((1, 0)), ((3, 2), (3, 2))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 2))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (2, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (3, 2))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 2), (0, 2))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 2), (3, 2))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (2, 0), (3, 2))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (3, 2), (3, 2))),
            Obstruction(Perm((0, 1, 2)), ((0, 2), (0, 2), (3, 2))),
            Obstruction(Perm((0, 1, 2)), ((3, 2), (3, 2), (3, 2))),
            Obstruction(Perm((0, 2, 1)), ((0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((0, 2, 1)), ((0, 0), (0, 0), (2, 0))),
            Obstruction(Perm((0, 2, 1)), ((0, 0), (0, 2), (0, 0))),
            Obstruction(Perm((0, 2, 1)), ((0, 0), (0, 2), (3, 2))),
            Obstruction(Perm((1, 0, 2)), ((0, 0), (2, 0), (3, 2))),
            Obstruction(Perm((1, 2, 0)), ((0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((2, 0, 1)), ((0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((0, 1, 2, 3)), ((0, 2), (0, 2), (0, 2), (0, 2))),
            Obstruction(Perm((0, 1, 2, 3)), ((2, 0), (2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((0, 1, 2, 3)), ((2, 0), (2, 0), (2, 0), (3, 2))),
            Obstruction(Perm((0, 1, 2, 3)), ((2, 0), (2, 0), (3, 2), (3, 2))),
            Obstruction(Perm((0, 1, 3, 2)), ((0, 2), (0, 2), (0, 2), (0, 2))),
            Obstruction(Perm((0, 2, 1, 3)), ((0, 2), (0, 2), (0, 2), (0, 2))),
            Obstruction(Perm((0, 2, 3, 1)), ((0, 2), (0, 2), (0, 2), (0, 2))),
            Obstruction(Perm((0, 2, 3, 1)), ((0, 2), (0, 2), (0, 2), (3, 2))),
            Obstruction(Perm((0, 3, 1, 2)), ((0, 2), (0, 2), (0, 2), (0, 2))),
            Obstruction(Perm((0, 3, 1, 2)), ((0, 2), (0, 2), (3, 2), (3, 2))),
            Obstruction(Perm((1, 2, 0, 3)), ((0, 2), (0, 2), (0, 0), (0, 2))),
            Obstruction(Perm((1, 2, 0, 3)), ((0, 2), (0, 2), (0, 2), (0, 2))),
        ),
        requirements=(
            (Requirement(Perm((0,)), ((1, 1),)),),
            (Requirement(Perm((0,)), ((2, 0),)),),
            (
                Requirement(Perm((0, 1)), ((2, 0), (2, 0))),
                Requirement(Perm((1, 0)), ((0, 2), (0, 0))),
                Requirement(Perm((1, 0)), ((0, 2), (3, 2))),
                Requirement(Perm((2, 0, 1)), ((0, 0), (0, 0), (2, 0))),
                Requirement(Perm((2, 0, 1)), ((0, 2), (0, 2), (0, 2))),
            ),
        ),
    )


@pytest.fixture
def mg5():
    return frozenset(
        [
            GriddedPerm(Perm((2, 0, 1)), ((1, 1), (2, 0), (2, 0))),
            GriddedPerm(Perm((2, 0, 3, 1)), ((0, 0), (0, 0), (1, 1), (2, 0))),
            GriddedPerm(Perm((3, 0, 2, 1)), ((0, 2), (0, 0), (1, 1), (2, 0))),
            GriddedPerm(Perm((3, 1, 0, 2)), ((0, 2), (1, 1), (2, 0), (3, 2))),
            GriddedPerm(Perm((3, 1, 2, 0)), ((0, 2), (0, 0), (1, 1), (2, 0))),
            GriddedPerm(
                Perm((4, 2, 3, 1, 0)), ((0, 2), (0, 2), (0, 2), (1, 1), (2, 0))
            ),
        ]
    )


@pytest.fixture
def t6():
    """Yield GriddedPerm, not Requirement"""
    return Tiling(
        obstructions=(
            Obstruction(Perm((0,)), ((0, 0),)),
            Obstruction(Perm((0,)), ((1, 1),)),
            Obstruction(Perm((0,)), ((1, 2),)),
            Obstruction(Perm((0, 1)), ((0, 1), (0, 1))),
            Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((0, 1), (0, 1))),
            Obstruction(Perm((1, 0)), ((0, 2), (0, 2))),
            Obstruction(Perm((0, 1, 2)), ((0, 1), (0, 2), (0, 2))),
            Obstruction(Perm((0, 1, 2)), ((0, 2), (0, 2), (0, 2))),
        ),
        requirements=((Requirement(Perm((1, 0)), ((0, 2), (0, 1))),),),
    )


@pytest.fixture
def mg6():
    return frozenset([GriddedPerm(Perm((1, 0)), ((0, 2), (0, 1)))])


def test_minimal_gridded_perms(t1, t2, t3, t4, t5, t6, mg1, mg2, mg3, mg4, mg5, mg6):
    for t, mg in zip([t1, t2, t3, t4, t5, t6], [mg1, mg2, mg3, mg4, mg5, mg6]):
        mgps = []
        for gp in MinimalGriddedPerms(t).minimal_gridded_perms():
            assert gp not in mgps
            for old in mgps:
                assert gp not in old
                assert old not in gp
            mgps.append(gp)
        assert frozenset(mgps) == mg
        assert len(mgps) == len(mg)

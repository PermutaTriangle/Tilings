# pylint: disable=no-name-in-module
import pytest

from tilings import GriddedPerm, Tiling
from tilings.algorithms import Sliding


def generate_all_slided_tilings(tiling):
    sliding = Sliding(tiling)
    for av_12, av_123 in sliding.slidable_pairs():
        yield sliding.slide_column(av_12, av_123)


t_cases = [
    (
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
    ),
    (
        Tiling(
            obstructions=(
                GriddedPerm((0, 1, 2, 3, 4), ((1, 0),) * 5),
                GriddedPerm((0, 1), ((3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3, 4), ((1, 0),) * 4 + ((3, 0),)),
                GriddedPerm((4, 3, 2, 1), ((0, 0),) * 4),
                GriddedPerm((2, 3, 1, 0), ((2, 0),) * 4),
                GriddedPerm((0, 2, 1), ((4, 0),) * 3),
                GriddedPerm((1, 2, 0), ((1, 0), (2, 0), (4, 0))),
                GriddedPerm((2, 1, 0), ((2, 0), (3, 0), (4, 0))),
                GriddedPerm((4, 1, 2, 3, 0), ((0, 0), (0, 0), (1, 0), (1, 0), (4, 0))),
                GriddedPerm((4, 1, 2, 3, 0), ((0, 0), (0, 0), (1, 0), (3, 0), (4, 0))),
            )
        ),
        Tiling(
            obstructions=(
                GriddedPerm((0, 1, 2, 3, 4), ((3, 0),) * 5),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2, 3, 4), ((1, 0),) + ((3, 0),) * 4),
                GriddedPerm((4, 3, 2, 1), ((0, 0),) * 4),
                GriddedPerm((2, 3, 1, 0), ((2, 0),) * 4),
                GriddedPerm((0, 2, 1), ((4, 0),) * 3),
                GriddedPerm((1, 2, 0), ((1, 0), (2, 0), (4, 0))),
                GriddedPerm((2, 1, 0), ((2, 0), (3, 0), (4, 0))),
                GriddedPerm((4, 1, 2, 3, 0), ((0, 0), (0, 0), (3, 0), (3, 0), (4, 0))),
                GriddedPerm((4, 1, 2, 3, 0), ((0, 0), (0, 0), (1, 0), (3, 0), (4, 0))),
            )
        ),
    ),
    (
        Tiling(
            obstructions=(
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((1, 2, 3, 0), ((0, 0), (0, 0), (2, 0), (2, 0))),
                GriddedPerm((1, 2, 3, 0), ((0, 0), (1, 0), (2, 0), (2, 0))),
            ),
            requirements=(((GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),),)),
        ),
        Tiling(
            obstructions=(
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((1, 2, 3, 0), ((1, 0), (1, 0), (2, 0), (2, 0))),
                GriddedPerm((1, 2, 3, 0), ((0, 0), (1, 0), (2, 0), (2, 0))),
            ),
            requirements=(((GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),),)),
        ),
    ),
    (
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
                GriddedPerm((1, 3, 0, 2), ((0, 0), (1, 0), (1, 0), (2, 0))),
                GriddedPerm((3, 0, 1, 2), ((1, 0), (1, 0), (2, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (2, 0))),
                GriddedPerm((1, 3, 0, 2), ((0, 0), (1, 0), (1, 0), (2, 0))),
                GriddedPerm((1, 2, 3, 0), ((0, 0), (0, 0), (1, 0), (1, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
    ),
    (
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (1, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
    ),
    (
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (3, 0), (3, 0), (3, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((0, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((1, 0), (3, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2, 3), ((2, 0), (2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2, 3), ((3, 0), (3, 0), (3, 0), (3, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
    ),
    (
        Tiling(
            obstructions=(
                GriddedPerm((0,), ((0, 0),)),
                GriddedPerm((0,), ((0, 2),)),
                GriddedPerm((0,), ((1, 1),)),
                GriddedPerm((0, 1), ((0, 1), (0, 1))),
                GriddedPerm((1, 0), ((0, 1), (0, 1))),
                GriddedPerm((1, 0), ((1, 0), (1, 0))),
                GriddedPerm((0, 2, 1), ((1, 0), (1, 2), (1, 2))),
                GriddedPerm((2, 1, 0), ((1, 2), (1, 2), (1, 2))),
                GriddedPerm((1, 0, 3, 2), ((1, 2), (1, 2), (1, 2), (1, 2))),
            ),
            requirements=(
                (GriddedPerm((0,), ((0, 1),)),),
                (GriddedPerm((0,), ((1, 0),)),),
            ),
        ),
        None,
    ),
    (
        Tiling(
            obstructions=[
                GriddedPerm((0, 1), ((1, 0), (3, 0))),
                GriddedPerm((0, 1), ((2, 0), (2, 0))),
                GriddedPerm((0, 1), ((2, 0), (3, 0))),
                GriddedPerm((0, 1), ((3, 0), (3, 0))),
                GriddedPerm((1, 0), ((1, 0), (1, 0))),
                GriddedPerm((1, 0), ((1, 0), (2, 0))),
                GriddedPerm((1, 0), ((1, 0), (3, 0))),
                GriddedPerm((1, 0), ((2, 0), (2, 0))),
                GriddedPerm((1, 0), ((2, 0), (3, 0))),
                GriddedPerm((1, 0), ((3, 0), (3, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (3, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
                GriddedPerm((3, 2, 1, 0), ((0, 0), (0, 0), (0, 0), (0, 0))),
                GriddedPerm((3, 2, 1, 0), ((0, 0), (0, 0), (0, 0), (1, 0))),
                GriddedPerm((3, 2, 1, 0), ((0, 0), (0, 0), (0, 0), (2, 0))),
                GriddedPerm((3, 2, 1, 0), ((0, 0), (0, 0), (0, 0), (3, 0))),
            ],
            requirements=[[GriddedPerm((0, 1), ((1, 0), (2, 0)))]],
        ),
        None,
    ),
    (
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
        None,
    ),
    (
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1), ((1, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
        None,
    ),
    (
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1), ((0, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
        None,
    ),
    (
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
        None,
    ),
    (
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
        None,
    ),
]


def test_algorithms_sliding():
    for tc, (t1, t2) in enumerate(t_cases):
        l1 = list(generate_all_slided_tilings(t1))
        if t2 is None:
            assert l1 == []
            continue
        l2 = list(generate_all_slided_tilings(t2))
        assert len(l1) == 1
        assert l1[0] == t2
        if tc > 0:
            assert len(l2) == 1
            assert l2[0] == t1
        else:
            assert len(l2) == 2
            assert set(l2) == {
                t1,
                Tiling(
                    obstructions=(
                        GriddedPerm((0, 1), ((0, 0), (0, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                        GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                    ),
                    requirements=(),
                    assumptions=(),
                ),
            }

    lis = [
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1), ((3, 0), (3, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (3, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (3, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((1, 0), (1, 0))),
                GriddedPerm((0, 1), ((2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (3, 0), (3, 0))),
                GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (3, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
        Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((0, 1), ((3, 0), (3, 0))),
                GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (3, 0))),
            ),
            requirements=(),
            assumptions=(),
        ),
    ]

    s = {lis[0]}
    while True:
        len_before = len(s)
        ss = set()
        for tt in s:
            ss.update(generate_all_slided_tilings(tt))
        s.update(ss)
        if len(s) == len_before:
            break
    assert s == set(lis)


@pytest.mark.slow
def test_slide():
    tcases = [
        (
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((2, 0), (2, 0))),
                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
                    GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                    GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                    GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                    GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
                ),
                requirements=(),
                assumptions=(),
            ),
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
                    GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (2, 0))),
                    GriddedPerm((0, 1, 2), ((0, 0), (2, 0), (2, 0))),
                    GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
                    GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
                ),
                requirements=(),
                assumptions=(),
            ),
            (1, 2),
            7,
        ),
        (
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1, 2, 3, 4), ((1, 0),) * 5),
                    GriddedPerm((0, 1), ((3, 0), (3, 0))),
                    GriddedPerm((0, 1, 2, 3, 4), ((1, 0),) * 4 + ((3, 0),)),
                    GriddedPerm((4, 3, 2, 1), ((0, 0),) * 4),
                    GriddedPerm((2, 3, 1, 0), ((2, 0),) * 4),
                    GriddedPerm((0, 2, 1), ((4, 0),) * 3),
                    GriddedPerm((1, 2, 0), ((1, 0), (2, 0), (4, 0))),
                    GriddedPerm((2, 1, 0), ((2, 0), (3, 0), (4, 0))),
                    GriddedPerm(
                        (4, 1, 2, 3, 0), ((0, 0), (0, 0), (1, 0), (1, 0), (4, 0))
                    ),
                    GriddedPerm(
                        (4, 1, 2, 3, 0), ((0, 0), (0, 0), (1, 0), (3, 0), (4, 0))
                    ),
                )
            ),
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1, 2, 3, 4), ((3, 0),) * 5),
                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                    GriddedPerm((0, 1, 2, 3, 4), ((1, 0),) + ((3, 0),) * 4),
                    GriddedPerm((4, 3, 2, 1), ((0, 0),) * 4),
                    GriddedPerm((2, 3, 1, 0), ((2, 0),) * 4),
                    GriddedPerm((0, 2, 1), ((4, 0),) * 3),
                    GriddedPerm((1, 2, 0), ((1, 0), (2, 0), (4, 0))),
                    GriddedPerm((2, 1, 0), ((2, 0), (3, 0), (4, 0))),
                    GriddedPerm(
                        (4, 1, 2, 3, 0), ((0, 0), (0, 0), (3, 0), (3, 0), (4, 0))
                    ),
                    GriddedPerm(
                        (4, 1, 2, 3, 0), ((0, 0), (0, 0), (1, 0), (3, 0), (4, 0))
                    ),
                )
            ),
            (1, 3),
            6,
        ),
        (
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
                    GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
                    GriddedPerm((0, 1), ((1, 0), (1, 0))),
                    GriddedPerm((1, 2, 3, 0), ((0, 0), (0, 0), (2, 0), (2, 0))),
                    GriddedPerm((1, 2, 3, 0), ((0, 0), (1, 0), (2, 0), (2, 0))),
                ),
                requirements=(((GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),),)),
            ),
            Tiling(
                obstructions=(
                    GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
                    GriddedPerm((0, 1, 2), ((0, 0), (1, 0), (1, 0))),
                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                    GriddedPerm((1, 2, 3, 0), ((1, 0), (1, 0), (2, 0), (2, 0))),
                    GriddedPerm((1, 2, 3, 0), ((0, 0), (1, 0), (2, 0), (2, 0))),
                ),
                requirements=(((GriddedPerm((0, 2, 1), ((2, 0), (2, 0), (2, 0))),),)),
            ),
            (),  # default
            7,
        ),
    ]

    for t1, t2, cols, up_to in tcases:
        visited = set()
        expected = set(t2.gridded_perms(up_to))
        for gp in t1.gridded_perms(up_to):
            sl = Sliding.slide_gp(gp, *cols)
            assert sl not in visited
            visited.add(sl)
            assert sl in expected
            expected.remove(sl)
        assert len(expected) == 0

        visited = set()
        expected = set(t1.gridded_perms(up_to))
        for gp in t2.gridded_perms(up_to):
            sl = Sliding.slide_gp_inverse(gp, *cols)
            assert sl not in visited
            visited.add(sl)
            assert sl in expected
            expected.remove(sl)
        assert len(expected) == 0

import json
import random
from collections import defaultdict

import pytest

from comb_spec_searcher import CombinatorialSpecification, Strategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from permuta import Av, Perm
from permuta.misc import DIR_NORTH, DIR_SOUTH
from tilings import GriddedPerm, Tiling
from tilings import strategies as strat
from tilings.algorithms.reduction import (
    is_reducible,
    is_rigid,
    monotone_obstructions,
    reduction_children,
    reduction_plan,
)
from tilings.assumptions import TrackingAssumption
from tilings.strategies.cell_reduction import (
    CellReductionFactory,
    CellReductionStrategy,
)
from tilings.strategies.reduction import ReductionFactory, ReductionStrategy
from tilings.strategies.requirement_placement import RequirementPlacementStrategy
from tilings.strategy_pack import TileScopePack
from tilings.tilescope import TileScope


def tiling_from(cell_bases, crossing_obstructions, empty_cells, tracked_cells=()):
    obstructions = [
        GriddedPerm.single_cell(patt, cell)
        for cell, patts in cell_bases.items()
        for patt in patts
    ]
    obstructions.extend(
        GriddedPerm(patt, cells) for patt, cells in crossing_obstructions
    )
    obstructions.extend(GriddedPerm.point_perm(cell) for cell in empty_cells)
    return Tiling(
        obstructions,
        assumptions=[TrackingAssumption.from_cells([cell]) for cell in tracked_cells],
    )


@pytest.fixture
def two_rows():
    """Av(1234, 1342, 2413) with its minimum and the first point to the right of
    the minimum placed, the points factored away: the class beside a decreasing
    cell above, and Av(123, 2413) beside Av(123, 231) below."""
    return tiling_from(
        {
            (0, 1): [Perm((0, 1, 2, 3)), Perm((0, 2, 3, 1)), Perm((1, 3, 0, 2))],
            (1, 0): [Perm((0, 1, 2)), Perm((1, 3, 0, 2))],
            (2, 0): [Perm((0, 1, 2)), Perm((1, 2, 0))],
            (3, 1): [Perm((0, 1))],
        },
        [
            (Perm((0, 1, 2)), ((1, 0), (1, 0), (3, 1))),
            (Perm((0, 1, 2)), ((2, 0), (2, 0), (3, 1))),
            (Perm((0, 2, 1)), ((0, 1), (0, 1), (3, 1))),
            (Perm((0, 2, 1)), ((1, 0), (1, 0), (2, 0))),
            (Perm((1, 0, 2)), ((1, 0), (2, 0), (2, 0))),
            (Perm((0, 1, 2, 3)), ((0, 1), (0, 1), (0, 1), (3, 1))),
            (Perm((0, 1, 2, 3)), ((1, 0), (1, 0), (2, 0), (2, 0))),
        ],
        [(0, 0), (1, 1), (2, 1), (3, 0)],
    )


@pytest.fixture
def apart():
    """Two cells sharing no row or column, tied by a 123 with two points in the
    lower one, beside a tracked increasing cell (from Av(1234, 2431))."""
    return tiling_from(
        {
            (0, 1): [Perm((1, 0))],
            (1, 0): [Perm((0, 1, 2)), Perm((1, 3, 2, 0))],
            (2, 2): [Perm((1, 0))],
        },
        [
            (Perm((1, 0)), ((0, 1), (1, 0))),
            (Perm((0, 1, 2)), ((1, 0), (1, 0), (2, 2))),
        ],
        [(0, 0), (0, 2), (1, 1), (1, 2), (2, 0), (2, 1)],
        tracked_cells=[(0, 1), (2, 2)],
    )


@pytest.fixture
def row_and_column():
    """A tiling from Av(1243, 1324, 2431) whose first column and bottom row are
    both reducible."""
    return tiling_from(
        {
            (0, 0): [Perm((0, 1))],
            (0, 1): [Perm((0, 2, 1))],
            (1, 0): [Perm((0, 2, 1))],
            (2, 0): [Perm((0, 1, 3, 2)), Perm((0, 2, 1, 3)), Perm((1, 3, 2, 0))],
        },
        [
            (Perm((1, 0)), ((0, 0), (2, 0))),
            (Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 0))),
            (Perm((0, 1, 2)), ((1, 0), (1, 0), (2, 0))),
            (Perm((0, 2, 1)), ((0, 0), (0, 1), (0, 1))),
            (Perm((0, 2, 1)), ((0, 0), (1, 0), (1, 0))),
            (Perm((1, 2, 0)), ((0, 0), (1, 0), (1, 0))),
            (Perm((1, 2, 0)), ((1, 0), (2, 0), (2, 0))),
            (Perm((0, 1, 3, 2)), ((0, 0), (2, 0), (2, 0), (2, 0))),
            (Perm((0, 1, 3, 2)), ((1, 0), (2, 0), (2, 0), (2, 0))),
            (Perm((0, 2, 1, 3)), ((0, 0), (2, 0), (2, 0), (2, 0))),
            (Perm((0, 2, 1, 3)), ((1, 0), (2, 0), (2, 0), (2, 0))),
        ],
        [(1, 1), (2, 1)],
    )


@pytest.fixture
def one_cell():
    """A cell that the cell reduction reduces: the obstruction it shares with the
    cell to its right has one point in it."""
    return tiling_from(
        {(0, 0): [Perm((0, 2, 1))], (1, 0): [Perm((1, 0))]},
        [(Perm((0, 1)), ((0, 0), (1, 0)))],
        [],
    )


@pytest.fixture
def threshold():
    """Av(2143) with its topmost point placed, a 21 inserted into the cell left of
    the point and the 2 of the 21 placed bottommost: that is the lowest top of an
    inversion of the left cell. Its points below it are in two increasing cells,
    left and right of it, every point of the left one below those of the right
    one, in the row of the cell right of the topmost point, which sees them only
    through the 2143 with one point in them."""
    with_point = Tiling.from_string("2143").add_single_cell_requirement(
        Perm((0,)), (0, 0)
    )
    placed = RequirementPlacementStrategy(
        [GriddedPerm(Perm((0,)), ((0, 0),))], [0], DIR_NORTH
    )(with_point).children[0]
    with_inversion = placed.add_single_cell_requirement(Perm((1, 0)), (0, 0))
    return RequirementPlacementStrategy(
        [GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0)))], [0], DIR_SOUTH
    )(with_inversion).children[0]


THRESHOLD_CELLS = [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)]


def beside_a_row_cell(both_above):
    """Two cells of the set in a row, A = (0, 0) before B = (1, 0), every point of A
    below those of B, beside a cell C = (2, 0) of the rest in the same row. Every
    point of A lies above those of C; so does every point of B if both_above, and
    then C sees A and B alike."""
    crossing = [
        (Perm((1, 0)), ((0, 0), (1, 0))),
        (Perm((0, 1)), ((0, 0), (2, 0))),
    ]
    if both_above:
        crossing.append((Perm((0, 1)), ((1, 0), (2, 0))))
    return tiling_from(
        {
            (0, 0): [Perm((0, 2, 1))],
            (1, 0): [Perm((0, 2, 1))],
            (2, 0): [Perm((1, 0))],
        },
        crossing,
        [],
    )


@pytest.fixture
def alike_row():
    return beside_a_row_cell(True)


@pytest.fixture
def unlike_row():
    return beside_a_row_cell(False)


@pytest.fixture
def with_requirement_list():
    """alike_row with a point required in A or in C."""
    tiling = beside_a_row_cell(True)
    return Tiling(
        tiling.obstructions,
        [[GriddedPerm.point_perm((0, 0)), GriddedPerm.point_perm((2, 0))]],
    )


@pytest.fixture
def touched_only():
    """A cell A = (0, 0) of the set below a cell B = (0, 1) of it, in a column and
    rows with no cell outside the set, and a cell C = (1, 2) of the rest: the rest
    sees A only through the 132s with a point in A and two in C, and B not at
    all."""
    return tiling_from(
        {
            (0, 0): [Perm((0, 2, 1))],
            (0, 1): [Perm((1, 0))],
            (1, 2): [Perm((0, 1, 2))],
        },
        [(Perm((0, 2, 1)), ((0, 0), (1, 2), (1, 2)))],
        [(0, 2), (1, 0), (1, 1)],
    )


def offered_sets(tiling, region):
    return sorted(
        {strategy.cells for strategy in ReductionFactory(True, region)(tiling)}
    )


def test_reducible(two_rows, apart):
    assert is_reducible(two_rows, [(1, 0), (2, 0), (3, 1)])
    assert is_reducible(two_rows, [(0, 1), (3, 1)])
    # a 123 with two points in (1, 0) and one in (3, 1) crosses the set
    assert not is_reducible(two_rows, [(1, 0), (2, 0)])
    assert not is_reducible(two_rows, [(1, 0)])
    assert is_reducible(apart, [(1, 0), (2, 2)])
    assert not is_reducible(apart, [(1, 0)])


def test_rigid(two_rows):
    assert is_rigid(two_rows, [(3, 1)])
    assert not is_rigid(two_rows, [(0, 1), (3, 1)])
    row = tiling_from({(0, 0): [Perm((1, 0))], (1, 0): [Perm((1, 0))]}, [], [])
    assert not is_rigid(row, [(0, 0), (1, 0)])
    increasing_row = tiling_from(
        {(0, 0): [Perm((1, 0))], (1, 0): [Perm((1, 0))]},
        [(Perm((1, 0)), ((0, 0), (1, 0)))],
        [],
    )
    assert is_rigid(increasing_row, [(0, 0), (1, 0)])


def test_regions(two_rows, apart, row_and_column, one_cell):
    assert offered_sets(two_rows, "cell") == []
    assert offered_sets(two_rows, "row") == [((0, 1), (3, 1))]
    assert offered_sets(two_rows, "column") == []
    assert offered_sets(two_rows, "line") == [((0, 1), (3, 1))]
    assert offered_sets(two_rows, "any") == [
        ((0, 1), (3, 1)),
        ((1, 0), (2, 0), (3, 1)),
    ]
    assert offered_sets(apart, "line") == []
    assert offered_sets(apart, "any") == [((1, 0), (2, 2))]
    assert offered_sets(row_and_column, "row") == [((0, 0), (1, 0), (2, 0))]
    assert offered_sets(row_and_column, "column") == [((0, 0), (0, 1))]
    assert offered_sets(row_and_column, "line") == [
        ((0, 0), (0, 1)),
        ((0, 0), (1, 0), (2, 0)),
    ]
    assert offered_sets(one_cell, "cell") == [((0, 0),)]
    assert offered_sets(one_cell, "any") == [((0, 0),)]
    assert offered_sets(two_rows, "any") == sorted(
        {
            strategy.cells
            for strategy in ReductionFactory(True, "any", max_cells=3)(two_rows)
        }
    )
    assert offered_sets(two_rows, "any")[:1] == sorted(
        {
            strategy.cells
            for strategy in ReductionFactory(True, "any", max_cells=2)(two_rows)
        }
    )
    with pytest.raises(ValueError):
        ReductionFactory(True, "diagonal")


def cut_sets(tiling):
    """The active cells on each side of each line between adjacent columns or rows."""
    width, height = tiling.dimensions
    cells = tiling.active_cells
    sides = []
    for column in range(1, width):
        sides.append({cell for cell in cells if cell[0] < column})
        sides.append({cell for cell in cells if cell[0] >= column})
    for row in range(1, height):
        sides.append({cell for cell in cells if cell[1] < row})
        sides.append({cell for cell in cells if cell[1] >= row})
    return sides


def test_cut_region(two_rows, apart, row_and_column, one_cell, threshold):
    # the threshold reduction's set, the cells left of the topmost point, is a cut
    assert tuple(THRESHOLD_CELLS) in offered_sets(threshold, "cut")
    for tiling in (two_rows, apart, row_and_column, one_cell, threshold):
        offered = offered_sets(tiling, "cut")
        # each set offered is one side of a line, and "any" offers it too
        assert all(set(cells) in cut_sets(tiling) for cells in offered)
        assert set(offered) <= set(offered_sets(tiling, "any"))
    # both of two_rows' reductions are cuts: above its middle line, and right of
    # its first column
    assert offered_sets(two_rows, "cut") == [
        ((0, 1), (3, 1)),
        ((1, 0), (2, 0), (3, 1)),
    ]
    assert offered_sets(one_cell, "cut") == [((0, 0),)]
    # max_cells bounds the sets of a cut as it bounds those of "any"
    assert tuple(THRESHOLD_CELLS) not in {
        strategy.cells for strategy in ReductionFactory(True, "cut", 4)(threshold)
    }
    assert str(ReductionFactory(True, "cut")) == (
        "tracked reduction factory of the cells on one side of a line"
    )
    assert str(ReductionFactory(False, "cut", 4)) == (
        "reduction factory of the cells on one side of a line of at most 4 cells"
    )
    for strategy in ReductionFactory(True, "cut")(threshold):
        rule = strategy(threshold)
        assert all(rule.sanity_check(n) for n in range(5))


def test_children(two_rows):
    cells = [(1, 0), (2, 0), (3, 1)]
    # no cell outside the set shares a row or a column with (1, 0) or (2, 0), and
    # no obstruction with points outside the set has a point in them
    assert reduction_plan(two_rows, cells) == ((((3, 1),),), ((1, 0), (2, 0)))
    reduced_tiling, own_tiling = reduction_children(two_rows, cells, False)
    # the reduced tiling keeps (3, 1) beside (0, 1), decreasing and tracked
    assert reduced_tiling.dimensions == (2, 1)
    assert GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))) in reduced_tiling.obstructions
    assert reduced_tiling.assumptions == (TrackingAssumption.from_cells([(1, 0)]),)
    # the own tiling keeps the 123s with the decreasing cell, in three columns and
    # two rows, and tracks (3, 1) only
    assert own_tiling.dimensions == (3, 2)
    assert GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (2, 1))) in (
        own_tiling.obstructions
    )
    assert own_tiling.assumptions == (TrackingAssumption.from_cells([(2, 1)]),)


@pytest.mark.parametrize(
    "fixture, cells",
    [
        ("two_rows", [(1, 0), (2, 0), (3, 1)]),
        ("two_rows", [(0, 1), (3, 1)]),
        ("apart", [(1, 0), (2, 2)]),
        ("row_and_column", [(0, 0), (0, 1)]),
        ("row_and_column", [(0, 0), (1, 0), (2, 0)]),
        ("one_cell", [(0, 0)]),
    ],
)
@pytest.mark.parametrize("increasing", [True, False])
def test_sanity_check(request, fixture, cells, increasing):
    """The counts, objects and random samples of the rule against its tilings."""
    tiling = request.getfixturevalue(fixture)
    rule = ReductionStrategy(cells, increasing)(tiling)
    for n in range(6):
        assert rule.sanity_check(n)


@pytest.mark.parametrize(
    "fixture, cells, increasing",
    [
        (fixture, cells, increasing)
        for fixture, cells in (
            ("two_rows", [(1, 0), (2, 0), (3, 1)]),
            ("apart", [(1, 0), (2, 2)]),
            ("row_and_column", [(0, 0), (1, 0), (2, 0)]),
            ("touched_only", [(0, 0), (0, 1)]),
        )
        for increasing in (True, False)
    ]
    + [
        ("alike_row", [(0, 0), (1, 0)], True),
        ("unlike_row", [(0, 0), (1, 0)], True),
        ("with_requirement_list", [(0, 0), (1, 0)], True),
        ("threshold", THRESHOLD_CELLS, True),
    ],
)
def test_maps(request, fixture, cells, increasing):
    """The forward map is a bijection onto the pairs with as many points in each
    group, whose sizes add up to the parent's with the groups' points counted once,
    and the backward map is its inverse."""
    tiling = request.getfixturevalue(fixture)
    strategy = ReductionStrategy(cells, increasing)
    reduced_tiling, own_tiling = strategy.decomposition_function(tiling)
    groups, _ = strategy.plan(tiling)

    def reduced_group_sizes(reduced_gridded_perm):
        parent_gridded_perm = reduced_tiling.backward_map.map_gp(reduced_gridded_perm)
        return tuple(
            sum(1 for other in parent_gridded_perm.pos if other == group[0])
            for group in groups
        )

    def own_group_sizes(own_gridded_perm):
        own_cells = own_tiling.backward_map.map_gp(own_gridded_perm).pos
        return tuple(
            sum(1 for other in own_cells if other in group) for group in groups
        )

    own_by_sizes = defaultdict(list)
    for n in range(6):
        for own_gridded_perm in own_tiling.objects_of_size(n):
            own_by_sizes[own_group_sizes(own_gridded_perm)].append(own_gridded_perm)
    for n in range(6):
        images = set()
        for gridded_perm in tiling.objects_of_size(n):
            reduced_gridded_perm, own_gridded_perm = strategy.forward_map(
                tiling, gridded_perm
            )
            assert (
                reduced_gridded_perm in reduced_tiling
                and own_gridded_perm in own_tiling
            )
            assert (
                next(
                    strategy.backward_map(
                        tiling, (reduced_gridded_perm, own_gridded_perm)
                    )
                )
                == gridded_perm
            )
            images.add((reduced_gridded_perm, own_gridded_perm))
        pairs = {
            (reduced_gridded_perm, own_gridded_perm)
            for reduced_size in range(n + 1)
            for reduced_gridded_perm in reduced_tiling.objects_of_size(reduced_size)
            for own_gridded_perm in own_by_sizes[
                reduced_group_sizes(reduced_gridded_perm)
            ]
            if reduced_size
            + len(own_gridded_perm)
            - sum(reduced_group_sizes(reduced_gridded_perm))
            == n
        }
        assert images == pairs


def test_monotone_obstructions():
    """In each cell, and between the two cells of each row and of each column, in
    the order of the direction: the lower (left) cell's points left of (below) the
    other's when increasing, right of (above) them when decreasing."""
    cells = [(0, 0), (1, 0), (0, 1)]
    increasing_obstructions = [
        GriddedPerm(Perm((1, 0)), positions)
        for positions in (
            ((0, 0), (0, 0)),
            ((0, 0), (1, 0)),
            ((0, 1), (0, 0)),
            ((0, 1), (0, 1)),
            ((1, 0), (1, 0)),
        )
    ]
    decreasing_obstructions = [
        GriddedPerm(Perm((0, 1)), positions)
        for positions in (
            ((0, 0), (0, 0)),
            ((0, 0), (0, 1)),
            ((0, 0), (1, 0)),
            ((0, 1), (0, 1)),
            ((1, 0), (1, 0)),
        )
    ]
    assert sorted(monotone_obstructions(cells, True)) == sorted(increasing_obstructions)
    assert sorted(monotone_obstructions(cells, False)) == sorted(
        decreasing_obstructions
    )


def test_groups_along_a_row(alike_row, unlike_row):
    """Two cells of a row that the rest sees alike are one group, kept in the
    first; two cells it does not see alike are two groups."""
    cells = [(0, 0), (1, 0)]
    assert reduction_plan(alike_row, cells) == ((((0, 0), (1, 0)),), ())
    assert reduction_plan(unlike_row, cells) == ((((0, 0),), ((1, 0),)), ())
    for tiling in (alike_row, unlike_row):
        assert is_reducible(tiling, cells, True)
        assert not is_reducible(tiling, cells, False)
        rule = ReductionStrategy(cells, True)(tiling)
        assert all(rule.sanity_check(n) for n in range(6))
    reduced_tiling, own_tiling = reduction_children(alike_row, cells, True)
    assert reduced_tiling.dimensions == (2, 1)
    assert own_tiling.dimensions == (2, 1)


def test_left_out_beside_kept(touched_only):
    """A cell the rest sees only through an obstruction with a point in it is
    kept, and the cell beside it, which the rest does not see, is left out."""
    cells = [(0, 0), (0, 1)]
    assert reduction_plan(touched_only, cells) == ((((0, 0),),), ((0, 1),))
    for increasing in (True, False):
        rule = ReductionStrategy(cells, increasing)(touched_only)
        assert all(rule.sanity_check(n) for n in range(6))


def test_requirement_list(with_requirement_list):
    """A requirement list with a point in the set and a point outside it."""
    cells = [(0, 0), (1, 0)]
    assert is_reducible(with_requirement_list, cells, True)
    rule = ReductionStrategy(cells, True)(with_requirement_list)
    assert all(rule.sanity_check(n) for n in range(6))


def test_direction_not_reducible(threshold):
    """A strategy applied in a direction its set is not reducible in."""
    with pytest.raises(StrategyDoesNotApply):
        ReductionStrategy(THRESHOLD_CELLS, False)(threshold)


def random_gridded_perm(rng, cells, size):
    """A gridded permutation with points in random cells, read left to right by
    column and bottom to top by row."""
    positions = sorted(rng.choice(cells) for _ in range(size))
    by_value = sorted(
        range(size), key=lambda index: (positions[index][1], rng.random())
    )
    values = [0] * size
    for value, index in enumerate(by_value):
        values[index] = value
    return GriddedPerm(Perm(values), tuple(positions))


def random_tiling(rng):
    width, height = rng.randint(1, 3), rng.randint(1, 3)
    cells = [(column, row) for column in range(width) for row in range(height)]
    active = rng.sample(cells, rng.randint(1, min(len(cells), 4)))
    patterns = [
        Perm(pattern)
        for pattern in ((0, 1), (1, 0), (0, 2, 1), (1, 0, 2), (1, 2, 0), (0, 1, 2))
    ]
    obstructions = [
        GriddedPerm.point_perm(cell) for cell in cells if cell not in active
    ]
    for cell in active:
        for pattern in rng.sample(patterns, rng.randint(1, 2)):
            obstructions.append(GriddedPerm.single_cell(pattern, cell))
    for _ in range(rng.randint(1, 4)):
        obstructions.append(random_gridded_perm(rng, active, rng.randint(2, 3)))
    requirements = (
        [[GriddedPerm.point_perm(rng.choice(active))]] if rng.random() < 0.3 else []
    )
    return Tiling(obstructions, requirements)


@pytest.mark.timeout(300)
def test_random_tilings():
    """Every reduction the factory offers on 30 random tilings, seeded, passes its
    sanity check (counts, objects and random samples) to size 4."""
    rng = random.Random(2026)
    tilings = []
    while len(tilings) < 30:
        tiling = random_tiling(rng)
        if not tiling.is_empty() and len(tiling.active_cells) >= 2:
            tilings.append(tiling)
    reductions = 0
    for tiling in tilings:
        for strategy in ReductionFactory(True, "any", max_cells=3)(tiling):
            rule = strategy(tiling)
            assert all(rule.sanity_check(n) for n in range(5)), rule
            reductions += 1
    assert reductions >= 30


def test_ordered_line(threshold):
    """An obstruction with one point in the set may see it along a row the set has
    other cells in, when the set's own obstructions put those cells in the order of
    the reduction: here the two low cells, the left one below the right one, so
    increasing only."""
    assert is_reducible(threshold, THRESHOLD_CELLS, True)
    assert not is_reducible(threshold, THRESHOLD_CELLS, False)
    assert [
        strategy.increasing
        for strategy in ReductionFactory(True, "any")(threshold)
        if strategy.cells == tuple(THRESHOLD_CELLS)
    ] == [True]


@pytest.mark.timeout(120)
def test_threshold(threshold):
    """The reduction of the left cell's five cells: the two low cells are seen as
    one, the point and the high cells are left out, and each child tracks one
    group."""
    strategy = ReductionStrategy(THRESHOLD_CELLS, True)
    assert strategy.plan(threshold) == (
        (((0, 0), (2, 0)),),
        ((0, 2), (1, 1), (2, 2)),
    )
    reduced_tiling, own_tiling = strategy.decomposition_function(threshold)
    assert reduced_tiling.dimensions == (3, 2)
    assert len(reduced_tiling.assumptions) == 1
    assert len(own_tiling.assumptions) == 1
    assert [len(list(threshold.objects_of_size(n))) for n in range(7)] == [
        0,
        0,
        0,
        1,
        7,
        40,
        225,
    ]
    rule = strategy(threshold)
    for n in range(7):
        assert rule.sanity_check(n)


@pytest.mark.timeout(120)
def test_threshold_inverse(threshold):
    """The inverse of the threshold tiling: the two low cells are in one column,
    which the cell below the topmost point's cell shares, and are seen as one."""
    tiling = threshold.inverse()
    cells = [(row, column) for column, row in THRESHOLD_CELLS]
    assert is_reducible(tiling, cells, True)
    assert not is_reducible(tiling, cells, False)
    strategy = ReductionStrategy(cells, True)
    groups, left_out = strategy.plan(tiling)
    assert groups == (((0, 0), (0, 2)),)
    assert len(left_out) == 3
    rule = strategy(tiling)
    for n in range(7):
        assert rule.sanity_check(n)


def test_parent_assumptions(apart):
    """The parent's tracked cells keep their counts."""
    rule = ReductionStrategy([(1, 0), (2, 2)], True)(apart)
    for n in range(6):
        assert rule.sanity_check(n)
    assert len(rule.children[0].extra_parameters) == 3


def test_unrestricted_cell():
    """A cell with no obstruction of its own is not reduced: its own tiling would be
    Tiling(), with only the empty permutation."""
    tiling = tiling_from(
        {(1, 0): [Perm((1, 0))]}, [(Perm((0, 1)), ((0, 0), (1, 0)))], []
    )
    assert not is_reducible(tiling, [(0, 0)])
    assert list(ReductionFactory(True, "any")(tiling)) == []
    assert list(CellReductionFactory(True)(tiling)) == []


def test_tracked_pattern():
    """A tracking assumption on a gridded permutation of two or more points counts
    occurrences of a pattern, which the sorting does not keep: a set with a cell of
    one is not reduced (the review of the pull request, round 1, finding 1)."""
    tiling = Tiling(
        [
            GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
            GriddedPerm(Perm((1, 0)), ((0, 1),) * 2),
            GriddedPerm(Perm((0, 2, 1)), ((1, 1),) * 3),
            GriddedPerm(Perm((1, 0, 2)), ((1, 0),) * 3),
        ],
        assumptions=[TrackingAssumption([GriddedPerm(Perm((0, 1)), ((1, 0),) * 2)])],
    )
    assert not is_reducible(tiling, [(1, 0)])
    for increasing in (True, False):
        with pytest.raises(StrategyDoesNotApply):
            ReductionStrategy([(1, 0)], increasing)(tiling)
    offered = offered_sets(tiling, "any")
    assert offered and all((1, 0) not in cells for cells in offered)
    for strategy in ReductionFactory(True, "any")(tiling):
        rule = strategy(tiling)
        assert all(rule.sanity_check(n) for n in range(5))


def test_not_tracked(two_rows):
    strategy = ReductionStrategy([(1, 0), (2, 0), (3, 1)], True, tracked=False)
    reduced_tiling, _ = strategy.decomposition_function(two_rows)
    assert not reduced_tiling.assumptions
    with pytest.raises(NotImplementedError):
        strategy.constructor(two_rows)


def test_cell_reduction(one_cell, two_rows):
    """The cell reduction is the reduction of single cells."""
    for tiling in (one_cell, two_rows):
        cell_strategies = list(CellReductionFactory(True)(tiling))
        assert all(
            isinstance(strategy, CellReductionStrategy) for strategy in cell_strategies
        )
        assert sorted(
            (strategy.cells, strategy.increasing) for strategy in cell_strategies
        ) == sorted(
            (strategy.cells, strategy.increasing)
            for strategy in ReductionFactory(True, "cell")(tiling)
        )
    rule = CellReductionStrategy((0, 0), True)(one_cell)
    for n in range(6):
        assert rule.sanity_check(n)
    assert str(CellReductionFactory(True)) == "tracked cell reduction factory"


def test_encoding():
    for strategy in (
        ReductionStrategy([(0, 0), (1, 0)], True, True),
        CellReductionStrategy((2, 1), False, False),
        ReductionFactory(True, "line"),
        ReductionFactory(True, "cut", 6),
        ReductionFactory(False, "any", 3),
        CellReductionFactory(True),
    ):
        decoded = Strategy.from_dict(json.loads(json.dumps(strategy.to_jsonable())))
        assert decoded.__class__ == strategy.__class__
        assert decoded.__dict__ == strategy.__dict__
    assert CellReductionStrategy((2, 1), False).to_jsonable()["cell"] == (2, 1)
    assert "region" not in CellReductionFactory(True).to_jsonable()


@pytest.mark.timeout(120)
def test_specification():
    """A specification of Av(1234, 1342, 2413) that reduces a set of three cells."""
    pack = TileScopePack.row_and_col_placements(row_only=False)
    counting_verification = (
        strat.BasicVerificationStrategy,
        strat.OneByOneVerificationStrategy,
    )
    pack = TileScopePack(
        initial_strats=pack.initial_strats,
        ver_strats=[
            strategy
            for strategy in pack.ver_strats
            if isinstance(strategy, counting_verification)
        ],
        inferral_strats=pack.inferral_strats,
        expansion_strats=pack.expansion_strats,
        name=pack.name,
    )
    pack = pack.make_fusion(tracked=True).add_initial(
        ReductionFactory(True, "any", max_cells=3)
    )
    spec = TileScope("1234_1342_2413", pack).auto_search()
    assert isinstance(spec, CombinatorialSpecification)
    assert any(
        isinstance(rule.strategy, ReductionStrategy) and len(rule.strategy.cells) > 1
        for rule in spec.rules_dict.values()
    )
    basis = [Perm((0, 1, 2, 3)), Perm((0, 2, 3, 1)), Perm((1, 3, 0, 2))]
    assert [spec.count_objects_of_size(n) for n in range(9)] == [
        len(list(Av(basis).of_length(n))) for n in range(9)
    ]

import json
from collections import defaultdict

import pytest

from comb_spec_searcher import CombinatorialSpecification, Strategy
from permuta import Av, Perm
from tilings import GriddedPerm, Tiling
from tilings import strategies as strat
from tilings.assumptions import TrackingAssumption
from tilings.strategies.cell_reduction import (
    CellReductionFactory,
    CellReductionStrategy,
)
from tilings.strategies.reduction import (
    ReductionFactory,
    ReductionStrategy,
    compression,
    is_reducible,
    is_rigid,
    reduction_children,
)
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


def test_children(two_rows):
    cells = [(1, 0), (2, 0), (3, 1)]
    reduced_tiling, own_tiling = reduction_children(two_rows, cells, False)
    # the bottom row is one decreasing sequence, the cells tracked
    assert GriddedPerm(Perm((0, 1)), ((1, 0), (2, 0))) in reduced_tiling.obstructions
    for cell in cells:
        assert GriddedPerm(Perm((0, 1)), (cell, cell)) in reduced_tiling.obstructions
        assert TrackingAssumption.from_cells([cell]) in reduced_tiling.assumptions
    assert reduced_tiling.dimensions == two_rows.dimensions
    # the own tiling keeps the 123s with the decreasing cell, in three columns and
    # two rows
    assert own_tiling.dimensions == (3, 2)
    assert GriddedPerm(Perm((0, 1, 2)), ((0, 0), (0, 0), (2, 1))) in (
        own_tiling.obstructions
    )
    assert len(own_tiling.assumptions) == 3


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
    "fixture, cells",
    [
        ("two_rows", [(1, 0), (2, 0), (3, 1)]),
        ("apart", [(1, 0), (2, 2)]),
        ("row_and_column", [(0, 0), (1, 0), (2, 0)]),
    ],
)
@pytest.mark.parametrize("increasing", [True, False])
def test_maps(request, fixture, cells, increasing):
    """The forward map is a bijection onto the pairs with as many points in each
    cell, and the backward map is its inverse."""
    tiling = request.getfixturevalue(fixture)
    strategy = ReductionStrategy(cells, increasing)
    reduced_tiling, own_tiling = strategy.decomposition_function(tiling)
    _, own_to_parent = compression(strategy.cells)

    def reduced_cell_sizes(reduced_gp):
        parent_gp = reduced_tiling.backward_map.map_gp(reduced_gp)
        return tuple(
            sum(1 for other in parent_gp.pos if other == cell)
            for cell in strategy.cells
        )

    def own_cell_sizes(own_gp):
        own_cells = [own_to_parent[cell] for cell in own_gp.pos]
        return tuple(
            sum(1 for other in own_cells if other == cell) for cell in strategy.cells
        )

    own_by_sizes = defaultdict(list)
    for n in range(6):
        for own_gp in own_tiling.objects_of_size(n):
            own_by_sizes[own_cell_sizes(own_gp)].append(own_gp)
    for n in range(6):
        images = set()
        for gp in tiling.objects_of_size(n):
            reduced_gp, own_gp = strategy.forward_map(tiling, gp)
            assert reduced_gp in reduced_tiling and own_gp in own_tiling
            assert next(strategy.backward_map(tiling, (reduced_gp, own_gp))) == gp
            images.add((reduced_gp, own_gp))
        pairs = {
            (reduced_gp, own_gp)
            for reduced_gp in reduced_tiling.objects_of_size(n)
            for own_gp in own_by_sizes[reduced_cell_sizes(reduced_gp)]
        }
        assert images == pairs


def test_parent_assumptions(apart):
    """The parent's tracked cells keep their counts."""
    rule = ReductionStrategy([(1, 0), (2, 2)], True)(apart)
    for n in range(6):
        assert rule.sanity_check(n)
    assert len(rule.children[0].extra_parameters) == 3


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
        assert all(isinstance(s, CellReductionStrategy) for s in cell_strategies)
        assert sorted((s.cells, s.increasing) for s in cell_strategies) == sorted(
            (s.cells, s.increasing) for s in ReductionFactory(True, "cell")(tiling)
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

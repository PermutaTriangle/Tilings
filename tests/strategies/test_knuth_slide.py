import json
import os
from itertools import combinations_with_replacement, permutations, product

import pytest

from comb_spec_searcher import CombinatorialSpecification
from comb_spec_searcher.rule_db import RuleDBForest
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms.knuth_slide import KnuthSlide, rsk
from tilings.assumptions import SumComponentAssumption, TrackingAssumption
from tilings.strategies import KnuthSlideFactory
from tilings.strategies.knuth_slide import KnuthSlideStrategy
from tilings.strategies.monotone_sliding import MonotoneSlidingFactory
from tilings.strategies.sliding import SlidingFactory
from tilings.strategy_pack import TileScopePack
from tilings.tilescope import GuidedSearcher, TrackedSearcher

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, "knuth_slide_15432.json")) as blocks_file:
    AV_15432_BLOCKS = {
        name: (Tiling.from_dict(entry["tiling"]), entry["col"], entry["width"])
        for name, entry in json.load(blocks_file).items()
    }


def cell(cell_, *patterns):
    return [
        GriddedPerm(Perm.to_standard(pattern), [cell_] * len(pattern))
        for pattern in patterns
    ]


def griddings_of(pattern, *cells):
    return [GriddedPerm(Perm.to_standard(pattern), cells)]


def griddings(pattern, cells):
    """Every valid gridding of patt over the cells."""
    pattern = Perm.to_standard(pattern)
    for positions in product(cells, repeat=len(pattern)):
        if any(positions[i][0] > positions[i + 1][0] for i in range(len(pattern) - 1)):
            continue
        if any(
            pattern[i] < pattern[j] and positions[i][1] > positions[j][1]
            for i in range(len(pattern))
            for j in range(len(pattern))
        ):
            continue
        yield GriddedPerm(pattern, positions)


def assert_bijection(parent, child, strategy, length):
    """The forward map takes the parent's gridded permutations of each size onto the
    child's, and the backward map takes them back."""
    for size in range(length + 1):
        parent_gridded_perms = set(parent.objects_of_size(size))
        images = {
            strategy.forward_map(parent, gridded_perm)[0]
            for gridded_perm in parent_gridded_perms
        }
        assert images == set(child.objects_of_size(size))
        assert {
            next(strategy.backward_map(parent, (gridded_perm,)))
            for gridded_perm in images
        } == (parent_gridded_perms)


def sanity_check(rule, length):
    for size in range(length + 1):
        assert rule.sanity_check(size)


def slides(tiling, **kwargs):
    return list(KnuthSlideFactory(**kwargs)(tiling))


def naive_one_row_slide(tiling, column, width):
    """The child the slide would have if every obstruction inside one cell were the
    cell's own and every other one a window constraint: the cells' obstructions
    mirrored, the others regridded over the block."""
    cells = [(column + i, 0) for i in range(width)]
    mirror = {cell_: cells[width - 1 - i] for i, cell_ in enumerate(cells)}
    obstructions = set()
    for obstruction in tiling.obstructions:
        indices = [i for i, cell_ in enumerate(obstruction.pos) if cell_ in cells]
        if not indices:
            obstructions.add(obstruction)
        elif (
            len(indices) == len(obstruction)
            and len({obstruction.pos[i] for i in indices}) == 1
        ):
            obstructions.add(
                GriddedPerm(
                    obstruction.patt, [mirror[cell_] for cell_ in obstruction.pos]
                )
            )
        else:
            for choice in combinations_with_replacement(cells, len(indices)):
                positions = list(obstruction.pos)
                for i, cell_ in zip(indices, choice):
                    positions[i] = cell_
                obstructions.add(GriddedPerm(obstruction.patt, positions))
    requirements = [
        [
            GriddedPerm(
                gridded_perm.patt,
                [mirror.get(cell_, cell_) for cell_ in gridded_perm.pos],
            )
            for gridded_perm in requirement
        ]
        for requirement in tiling.requirements
    ]
    return Tiling(obstructions, requirements)


ROW_PLACEMENTS = TileScopePack.row_and_col_placements(row_only=True).make_fusion(
    tracked=False
)
COL_PLACEMENTS = TileScopePack.row_and_col_placements(col_only=True).make_fusion(
    tracked=False
)


def counts(tiling, length):
    return [sum(1 for _ in tiling.objects_of_size(size)) for size in range(length + 1)]


# Babson and West's pair: an increasing cell next to a 321-avoiding one, jointly
# 321-avoiding (the Catalan numbers either way round).
LEFT, RIGHT = (0, 0), (1, 0)
babson_west = Tiling(
    cell(LEFT, "21")
    + cell(RIGHT, "321")
    + [GriddedPerm(Perm((2, 1, 0)), (LEFT, RIGHT, RIGHT))]
)


def test_babson_west_pair():
    (rule,) = slides(babson_west)
    child = rule.children[0]
    assert child == Tiling(
        cell(RIGHT, "21")
        + cell(LEFT, "321")
        + [GriddedPerm(Perm((2, 1, 0)), (LEFT, LEFT, RIGHT))]
    )
    assert (
        counts(babson_west, 7) == counts(child, 7) == [1, 2, 5, 14, 42, 132, 429, 1430]
    )
    assert_bijection(babson_west, child, rule.strategy, 6)
    sanity_check(rule, 6)


@pytest.mark.parametrize("name", sorted(AV_15432_BLOCKS))
def test_three_column_slides_of_av_15432(name):
    """The three blocks of three cells that Av(15432)'s specification reverses."""
    tiling, column, width = AV_15432_BLOCKS[name]
    rules = [
        rule
        for rule in slides(tiling)
        if rule.strategy.col == column and rule.strategy.width == width
    ]
    assert len(rules) == 1
    assert_bijection(tiling, rules[0].children[0], rules[0].strategy, 5)
    sanity_check(rules[0], 5)


def test_three_distinct_cells_do_not_slide_two_at_a_time():
    """[Av(15432) | Av(4321) | Av(321) | inc]: the last two cells avoid 321 together,
    and all three avoid 4321, so only the pair (Av(321), inc) slides; the naive slide
    of the others changes the counts."""
    tiling, _, _ = AV_15432_BLOCKS["04321|3210|210|10"]
    knuth_slide = KnuthSlide(tiling)
    assert knuth_slide.why_not(1, 3) is None
    assert knuth_slide.why_not(2, 2) is None
    for column in (0, 1):
        assert knuth_slide.why_not(column, 2) is not None
        assert counts(tiling, 5) != counts(naive_one_row_slide(tiling, column, 2), 5)


def test_slides_agree_with_tilings_sliding():
    """On the tilings Tilings' sliding was made for, the Knuth slide gives the same
    children."""
    av_1432 = ROW_PLACEMENTS.add_initial(SlidingFactory(use_symmetries=True))
    searcher = TrackedSearcher(
        Tiling.from_string("1432"), av_1432, max_assumptions=0, ruledb=RuleDBForest()
    )
    searcher.auto_search(status_update=None)
    tested = 0
    for label in range(len(searcher.classdb.label_to_tilings)):
        tiling = searcher.classdb.get_class(label)
        for rule in SlidingFactory(use_symmetries=True)(tiling):
            children = {slide_rule.children[0] for slide_rule in slides(tiling)}
            assert rule.children[0] in children
            tested += 1
    assert tested > 0


def test_slides_agree_with_tilings_monotone_sliding():
    """Every rule of Tilings' monotone sliding, on the tilings of an untracked search
    and of the tracked search it guides, is a Knuth slide of two columns, assumptions
    included. The Knuth slide gives it the maps it lacks."""
    pack = ROW_PLACEMENTS.add_initial(MonotoneSlidingFactory())
    untracked = TrackedSearcher(
        Tiling.from_string("1432"), pack, max_assumptions=0, ruledb=RuleDBForest()
    )
    spec = untracked.auto_search(status_update=None)
    tracked = GuidedSearcher(
        spec.comb_classes(), spec.root, pack.make_tracked(), ruledb=RuleDBForest()
    )
    tracked.auto_search(status_update=None)
    tested = with_assumptions = 0
    for searcher in (untracked, tracked):
        for label in range(len(searcher.classdb.label_to_tilings)):
            tiling = searcher.classdb.get_class(label)
            for rule in MonotoneSlidingFactory()(tiling):
                if rule.children[0] == tiling:
                    continue
                children = {
                    slide_rule.children[0] for slide_rule in slides(tiling, max_width=2)
                }
                assert rule.children[0] in children
                tested += 1
                with_assumptions += bool(tiling.assumptions)
    assert tested > 0 and with_assumptions > 0


def two_rows(strip_column, short_columns):
    """Babson and West's picture as a tiling: the pair, columns 1 and 2, has cells in
    both rows; the short columns have a cell in one row. Everything avoids 321, and
    the strip column, as a whole, avoids 21."""
    cells = [(1, 0), (1, 1), (2, 0), (2, 1)] + short_columns
    width = max(x for x, _ in cells) + 1
    empty = [
        GriddedPerm((0,), ((x, y),))
        for x in range(width)
        for y in range(2)
        if (x, y) not in cells
    ]
    strip = [cell_ for cell_ in cells if cell_[0] == strip_column]
    return Tiling(list(griddings("321", cells)) + list(griddings("21", strip)) + empty)


@pytest.mark.parametrize(
    "short_columns", [[(0, 0)], [(0, 0), (3, 1)]], ids=["left", "both sides"]
)
def test_the_ferrers_version(short_columns):
    parent = two_rows(1, short_columns)
    (rule,) = [
        slide_rule for slide_rule in slides(parent) if not slide_rule.strategy.transpose
    ]
    assert rule.children[0] == two_rows(2, short_columns)
    assert_bijection(parent, rule.children[0], rule.strategy, 5)
    sanity_check(rule, 5)


def test_the_ferrers_version_needs_whole_columns():
    """With the 21 on the strip's top cell only, the naive slide changes the counts."""
    cells = [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1)]
    base = list(griddings("321", cells)) + [GriddedPerm((0,), ((0, 1),))]
    top_of_1 = Tiling(base + cell((1, 1), "21"))
    top_of_2 = Tiling(base + cell((2, 1), "21"))
    assert KnuthSlide(top_of_1).why_not(1, 2) is not None
    assert counts(top_of_1, 6) != counts(top_of_2, 6)


def point_and_pair(x_basis, y_basis, window):
    """A point, and to its right the pair; above the point, the pair's word avoids
    the window's patterns."""
    point, x_cell, y_cell = (0, 0), (1, 0), (2, 0)
    obstructions = (
        cell(point, "12", "21") + cell(x_cell, *x_basis) + cell(y_cell, *y_basis)
    )
    for pattern in window:
        lifted = (0,) + tuple(value + 1 for value in Perm.to_standard(pattern))
        for choice in combinations_with_replacement([x_cell, y_cell], len(pattern)):
            obstructions.append(GriddedPerm(Perm(lifted), (point,) + choice))
    return Tiling(obstructions, [[GriddedPerm((0,), (point,))]])


def shape_31():
    """The nine permutations of RSK shape (3, 1): a class determined by the shape,
    whose basis is not monotone."""
    return [
        Perm(perm)
        for perm in permutations(range(4))
        if tuple(len(row) for row in rsk(perm)[0]) == (3, 1)
    ]


@pytest.mark.parametrize(
    "tiling",
    [
        point_and_pair(["123"], ["21"], ["132", "312"]),
        point_and_pair(shape_31(), ["12"], ["1243", "1423", "4123"]),
    ],
    ids=["Knuth-closed window", "shape-closed cell, Knuth class window"],
)
def test_general_slides(tiling):
    """Windows closed under Knuth moves, and cells determined by the shape, that are
    not monotone."""
    (rule,) = slides(tiling)
    assert_bijection(tiling, rule.children[0], rule.strategy, 6)
    sanity_check(rule, 5)


@pytest.mark.parametrize(
    "tiling, column",
    [
        (
            Tiling(
                cell(LEFT, "132")
                + cell(RIGHT, "21")
                + list(griddings("1234", [LEFT, RIGHT]))
            ),
            0,
        ),
        (point_and_pair(["21"], ["321"], ["132"]), 1),
        (
            Tiling(
                cell(LEFT, "21")
                + cell(RIGHT, "12")
                + [GriddedPerm(Perm((1, 0)), (LEFT, RIGHT))]
            ),
            0,
        ),
    ],
    ids=["cell not shape-closed", "window not Knuth-closed", "split-dependent"],
)
def test_each_condition_is_needed(tiling, column):
    """Each tiling breaks one condition: the slide refuses it, and the naive slide
    changes the counts."""
    assert KnuthSlide(tiling).why_not(column, 2) is not None
    assert not [
        slide_rule for slide_rule in slides(tiling) if slide_rule.strategy.col == column
    ]
    assert counts(tiling, 6) != counts(naive_one_row_slide(tiling, column, 2), 6)


def test_requirements_and_assumptions_follow_the_cells():
    tiling = Tiling(
        babson_west.obstructions,
        [[GriddedPerm((0,), (LEFT,))]],
        [TrackingAssumption([GriddedPerm((0,), (LEFT,))])],
    )
    (rule,) = slides(tiling)
    child = rule.children[0]
    assert child.requirements == ((GriddedPerm((0,), (RIGHT,)),),)
    assert child.assumptions == (TrackingAssumption([GriddedPerm((0,), (RIGHT,))]),)
    sanity_check(rule, 6)


def decreasing_square(requirements=(), assumptions=()):
    """A block of two columns and two rows avoiding 12 in every gridding."""
    cells = [(0, 0), (0, 1), (1, 0), (1, 1)]
    return Tiling(list(griddings("12", cells)), requirements, assumptions)


def test_a_requirement_on_part_of_a_column_stops_the_ferrers_slide():
    """A point requirement in one of a column's two cells: the slide refuses it, and
    the naive child, with the requirement mirrored, has other counts."""
    tiling = decreasing_square([[GriddedPerm((0,), ((0, 1),))]])
    assert (
        KnuthSlide(tiling).why_not(0, 2)
        == "a requirement is on part of a column of the block"
    )
    naive = decreasing_square([[GriddedPerm((0,), ((1, 1),))]])
    assert counts(tiling, 5) != counts(naive, 5)
    parent = two_rows(1, [(0, 0)])
    whole_column = Tiling(
        parent.obstructions,
        [[GriddedPerm((0,), ((1, 0),)), GriddedPerm((0,), ((1, 1),))]],
    )
    (rule,) = [
        slide_rule
        for slide_rule in slides(whole_column)
        if not slide_rule.strategy.transpose
    ]
    sanity_check(rule, 5)


def test_an_assumption_on_part_of_the_block_stops_the_slide():
    """An assumption on one cell of a block spanning two rows: the slide refuses it,
    and the naive child, with the assumption mirrored, has other parameters."""
    tiling = decreasing_square(
        assumptions=[TrackingAssumption([GriddedPerm((0,), ((0, 1),))])]
    )
    assert (
        KnuthSlide(tiling).why_not(0, 2)
        == "an assumption covers part of the block's columns and rows"
    )
    naive = decreasing_square(
        assumptions=[TrackingAssumption([GriddedPerm((0,), ((1, 1),))])]
    )
    assert tiling.get_terms(3) != naive.get_terms(3)


@pytest.mark.parametrize(
    "assumption",
    [
        TrackingAssumption([GriddedPerm((0, 1), (LEFT, RIGHT))]),
        SumComponentAssumption(
            [GriddedPerm((0,), (LEFT,)), GriddedPerm((0,), (RIGHT,))]
        ),
    ],
    ids=["on more than a point", "counting components"],
)
def test_assumptions_that_do_not_count_points_stop_the_slide(assumption):
    tiling = Tiling(babson_west.obstructions, [], [assumption])
    assert KnuthSlide(tiling).why_not(0, 2) is not None
    assert not slides(tiling)


def test_an_assumption_from_outside_the_block_stops_the_slide():
    """An assumption on two points, the first outside the block: not a point
    assumption on the block either."""
    other, x, y = (0, 0), (1, 0), (2, 0)
    tiling = Tiling(
        cell(other, "21")
        + cell(x, "21")
        + cell(y, "321")
        + griddings_of("321", x, y, y),
        [],
        [TrackingAssumption([GriddedPerm((0, 1), (other, y))])],
    )
    assert not slides(tiling)


def test_a_tiling_with_an_empty_column_does_not_slide():
    """The child would lose the empty column, and the map would not fit it."""
    tiling = Tiling(
        babson_west.obstructions
        + (GriddedPerm((0,), ((2, 0),)), GriddedPerm((0, 1), ((3, 0), (3, 0)))),
        remove_empty_rows_and_cols=False,
    )
    assert tiling.dimensions == (4, 1)
    assert KnuthSlide(tiling).why_not(0, 2) == "the tiling has an empty row or column"
    assert not slides(tiling)


def test_transposed_slides():
    """The slide of a block of rows: Babson and West's pair stacked in a column."""
    tiling = babson_west.inverse()
    (rule,) = slides(tiling)
    assert rule.strategy.transpose
    assert rule.children[0] == slides(babson_west)[0].children[0].inverse()
    assert_bijection(tiling, rule.children[0], rule.strategy, 6)
    sanity_check(rule, 6)


def test_transposed_slides_with_assumptions():
    """A block of rows with an assumption: its parameter goes through the inverse."""
    tiling = Tiling(
        babson_west.obstructions, [], [TrackingAssumption([GriddedPerm((0,), (LEFT,))])]
    ).inverse()
    (rule,) = slides(tiling)
    assert rule.strategy.transpose
    assert rule.children[0] == slides(tiling.inverse())[0].children[0].inverse()
    assert_bijection(tiling, rule.children[0], rule.strategy, 5)
    sanity_check(rule, 6)


def test_identical_columns_give_no_rule():
    twins = Tiling(
        cell(LEFT, "21") + cell(RIGHT, "21") + list(griddings("21", [LEFT, RIGHT]))
    )
    assert KnuthSlide(twins).why_not(0, 2) is None
    assert KnuthSlide(twins).is_identity(0, 2)
    assert not slides(twins)


def test_factory_options():
    tiling, _, _ = AV_15432_BLOCKS["04321|3210|10|210|3210"]
    widths = {rule.strategy.width for rule in slides(tiling)}
    assert 3 in widths
    assert {rule.strategy.width for rule in slides(tiling, max_width=2)} <= {2}
    assert not [
        slide_rule
        for slide_rule in slides(two_rows(1, [(0, 0)]), rows=False)
        if not slide_rule.strategy.transpose
    ]
    assert slides(babson_west.inverse())
    assert not slides(babson_west.inverse(), transpose=False)
    assert str(KnuthSlideFactory()) == "Knuth slides of up to 3 columns or rows"
    assert (
        str(KnuthSlideFactory(max_width=2, rows=False, transpose=False))
        == "Knuth slides of up to 2 columns, in one row of cells"
    )


def test_the_strategy_refuses_a_block_that_does_not_slide():
    from comb_spec_searcher.exception import StrategyDoesNotApply

    with pytest.raises(StrategyDoesNotApply):
        KnuthSlideStrategy(0, 2)(
            Tiling(
                cell(LEFT, "21")
                + cell(RIGHT, "12")
                + [GriddedPerm(Perm((1, 0)), (LEFT, RIGHT))]
            )
        )


def untracked_then_guided(basis, pack, max_width):
    pack = pack.add_initial(KnuthSlideFactory(max_width=max_width))
    untracked = TrackedSearcher(
        Tiling.from_string(basis),
        pack,
        max_assumptions=0,
        ruledb=RuleDBForest(),
        expand_verified=True,
    ).auto_search(status_update=None)
    return GuidedSearcher(
        untracked.comb_classes(),
        untracked.root,
        pack.make_tracked(),
        ruledb=RuleDBForest(),
        expand_verified=True,
    ).auto_search(status_update=None)


def test_av_1432_with_two_column_slides():
    spec = untracked_then_guided("1432", ROW_PLACEMENTS, 2)
    assert [spec.count_objects_of_size(size) for size in range(9)] == [
        1,
        1,
        2,
        6,
        23,
        103,
        513,
        2761,
        15767,
    ]
    spec.sanity_check(5)


@pytest.mark.slow
def test_av_15432_with_three_column_slides():
    """Av(15432), which Tilings' sliding does not reach, with its Wilf-equivalent
    Av(12345)'s counts."""
    spec = untracked_then_guided("15432", ROW_PLACEMENTS, 3)
    assert [spec.count_objects_of_size(size) for size in range(10)] == [
        1,
        1,
        2,
        6,
        24,
        119,
        694,
        4582,
        33324,
        261808,
    ]


def test_a_specification_of_transposed_slides():
    """Av(1432) with column placements, whose slides are blocks of rows: the
    specification counts, samples, and survives a JSON round trip, which rebuilds
    each slide's child through its decomposition function."""
    spec = untracked_then_guided("1432", COL_PLACEMENTS, 2)
    rules = [
        step
        for rule in spec.rules_dict.values()
        for step in getattr(rule, "rules", (rule,))
    ]
    knuth = [
        step.strategy for step in rules if isinstance(step.strategy, KnuthSlideStrategy)
    ]
    assert any(strategy.transpose for strategy in knuth)
    expected = [1, 1, 2, 6, 23, 103, 513, 2761, 15767]
    assert [spec.count_objects_of_size(size) for size in range(9)] == expected
    again = CombinatorialSpecification.from_dict(
        json.loads(json.dumps(spec.to_jsonable()))
    )
    assert [again.count_objects_of_size(size) for size in range(9)] == expected
    assert spec.random_sample_object_of_size(7).patt.avoids(Perm((0, 3, 2, 1)))
    spec.sanity_check(4)

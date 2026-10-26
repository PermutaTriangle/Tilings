import json
import os
from itertools import combinations_with_replacement, permutations, product

import pytest

from comb_spec_searcher import CombinatorialSpecification
from comb_spec_searcher.rule_db import RuleDBForest
from permuta import Perm
from permuta.permutils import rsk
from tilings import GriddedPerm, Tiling
from tilings.algorithms.knuth_slide import KnuthSlide
from tilings.assumptions import (
    SkewComponentAssumption,
    SumComponentAssumption,
    TrackingAssumption,
)
from tilings.strategies import KnuthSlideFactory
from tilings.strategies.knuth_slide import KnuthSlideStrategy
from tilings.strategies.monotone_sliding import MonotoneSlidingFactory
from tilings.strategies.sliding import SlidingFactory
from tilings.strategy_pack import TileScopePack
from tilings.tilescope import GuidedSearcher, TrackedSearcher

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, "knuth_slide_15432.json")) as blocks_file:
    AV_15432_BLOCKS = {
        name: (Tiling.from_dict(entry["tiling"]), entry["start"], entry["width"])
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
        if rule.strategy.start == column and rule.strategy.width == width
    ]
    assert len(rules) == 1
    assert_bijection(tiling, rules[0].children[0], rules[0].strategy, 5)
    sanity_check(rules[0], 5)


def decreasing_staircase(lengths, mirrored=False):
    """Cells in one row, the run of columns from column i to the last avoiding
    together the decreasing pattern of length lengths[i]: for (5, 4, 3, 2), the
    staircase [Av(54321) | Av(4321) | Av(321) | Av(21)] of Av(165432)'s
    specification. With mirrored, the runs from the first column to the mirror of
    column i do."""
    cells = [(x, 0) for x in range(len(lengths))]
    obstructions = []
    for first, length in enumerate(lengths):
        decreasing = "".join(str(value) for value in range(length, 0, -1))
        run = cells[: len(lengths) - first] if mirrored else cells[first:]
        obstructions.extend(griddings(decreasing, run))
    return Tiling(obstructions)


def test_a_block_of_four_columns():
    """The staircase of four cells slides all at once to its mirror image, and so do
    its last three cells and its last two, but no other block of it. The factory
    offers the slide of the four only when max_width allows four columns."""
    staircase = decreasing_staircase([5, 4, 3, 2])
    knuth = KnuthSlide(staircase)
    assert [
        block for block in knuth.blocks(max_width=4) if knuth.why_not(*block) is None
    ] == [(2, 2), (1, 3), (0, 4)]
    (rule,) = [
        slide_rule
        for slide_rule in slides(staircase, max_width=4)
        if slide_rule.strategy.width == 4
    ]
    assert rule.children[0] == decreasing_staircase([5, 4, 3, 2], mirrored=True)
    assert counts(staircase, 6) == [1, 4, 19, 104, 641, 4364, 32293]
    assert counts(rule.children[0], 6) == counts(staircase, 6)
    assert_bijection(staircase, rule.children[0], rule.strategy, 5)
    sanity_check(rule, 5)
    assert not [
        slide_rule for slide_rule in slides(staircase) if slide_rule.strategy.width == 4
    ]


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
    """On the tilings of a search of Av(1432) with Tilings' sliding, every child of
    a sliding rule is the child of a Knuth slide."""
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
    """On the tilings of an untracked search of Av(1432) with Tilings' monotone
    sliding, and of the tracked search it guides, the child of every monotone
    sliding rule that changes the tiling is the child of a Knuth slide of two
    columns, assumptions included."""
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
        slide_rule
        for slide_rule in slides(tiling)
        if slide_rule.strategy.start == column
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
    assert {rule.strategy.width for rule in slides(tiling, max_width=2)} == {2}
    assert not [
        slide_rule
        for slide_rule in slides(two_rows(1, [(0, 0)]), one_line_only=True)
        if not slide_rule.strategy.transpose
    ]
    assert slides(babson_west.inverse())
    assert not slides(babson_west.inverse(), slide_rows=False)
    assert str(KnuthSlideFactory()) == "Knuth slides of up to 3 columns or rows"
    assert (
        str(KnuthSlideFactory(max_width=2, one_line_only=True, slide_rows=False))
        == "Knuth slides of up to 2 columns, in one line of cells"
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


def test_the_strategy_in_json_and_the_backward_map_of_no_object():
    """The JSON form of a strategy names its block and nothing else, as saved
    specifications have it; and as for any disjoint union, the backward map of no
    object raises."""
    from comb_spec_searcher.exception import ObjectMappingError

    strategy = KnuthSlideStrategy(1, 2, transpose=True)
    assert strategy.to_jsonable() == {
        "class_module": "tilings.strategies.knuth_slide",
        "strategy_class": "KnuthSlideStrategy",
        "start": 1,
        "width": 2,
        "transpose": True,
    }
    again = KnuthSlideStrategy.from_dict(strategy.to_jsonable())
    assert repr(again) == repr(strategy)
    (rule,) = slides(babson_west)
    with pytest.raises(ObjectMappingError):
        next(rule.strategy.backward_map(babson_west, (None,)))


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


def pair_above_a_column(height, mirrored=False):
    """Babson and West's pair in row height, with a column of height cells at its
    right, so that the pair is not in the lowest row. With mirrored, the pair's cells
    have changed places: the child of the slide."""
    cells = [(0, height), (1, height)]
    avoids_21, avoids_321 = reversed(cells) if mirrored else cells
    unused = [(x, y) for x in (0, 1) for y in range(height)] + [(2, height)]
    obstructions = (
        cell(avoids_21, "21")
        + cell(avoids_321, "321")
        + [GriddedPerm(Perm((2, 1, 0)), sorted([avoids_21, avoids_321, avoids_321]))]
        + [GriddedPerm((0,), (unused_cell,)) for unused_cell in unused]
    )
    for row in range(height):
        obstructions += cell((2, row), "21")
    return Tiling(obstructions)


@pytest.mark.parametrize("height", [2, 3])
def test_a_block_above_other_rows_slides_like_one_in_the_lowest_row(height):
    """The row bound of a regridding is open above when no point of the obstruction
    lies above the block points, however high the block's row and however short the
    obstruction: Av(21) in a cell of row 2 has two points, and the regridding of its
    own points to the other cell must still be there."""
    parent = pair_above_a_column(height)
    (rule,) = slides(parent)
    assert not rule.strategy.transpose
    assert rule.children[0] == pair_above_a_column(height, mirrored=True)
    assert_bijection(parent, rule.children[0], rule.strategy, 5)
    sanity_check(rule, 5)


def point_with_windows(above, below):
    """A point, and to its right the pair; the pair's word, when it lies above the
    point, avoids the patterns above, and when it lies below the point, the patterns
    below. The point is first in every word, being in the leftmost column."""
    point, x_cell, y_cell = (0, 0), (1, 0), (2, 0)
    obstructions = cell(point, "12", "21") + cell(x_cell, "21") + cell(y_cell, "321")
    for pattern in above:
        word = Perm((0,) + tuple(value + 1 for value in Perm.to_standard(pattern)))
        for choice in combinations_with_replacement([x_cell, y_cell], len(pattern)):
            obstructions.append(GriddedPerm(word, (point,) + choice))
    for pattern in below:
        block = Perm.to_standard(pattern)
        word = Perm((len(block),) + tuple(block))
        for choice in combinations_with_replacement([x_cell, y_cell], len(pattern)):
            obstructions.append(GriddedPerm(word, (point,) + choice))
    return Tiling(obstructions, [[GriddedPerm((0,), (point,))]])


def test_the_windows_above_and_below_a_point_are_closed_on_their_own():
    """Av(132) when the pair lies above the point and Av(312) when it lies below:
    {132, 312} is closed under Knuth moves, but neither pattern alone is, and a
    window is one of the patterns the block sees for one position of the other
    points among its values, so the slide must refuse."""
    tiling = point_with_windows(above=["132"], below=["312"])
    assert not any(obstruction.contradictory() for obstruction in tiling.obstructions)
    assert (
        KnuthSlide(tiling).why_not(1, 2)
        == "a window's patterns are not closed under Knuth moves"
    )
    assert not slides(tiling)


def split_by_outside_cell():
    """Two cells at the left of the pair, one below the other. A point of the lower
    one may not lie above and to the left of a point of the pair, whichever its
    column; a point of the upper one may not lie so to a point of the pair's first
    column, but may to one of its second. The two obstructions have the same pattern
    and the same cell for the pair's point: they differ in the cell outside the block
    only."""
    lower, upper, x_cell, y_cell = (0, 0), (0, 1), (1, 0), (2, 0)
    above = Perm((1, 0))
    return Tiling(
        [GriddedPerm((0,), (unused_cell,)) for unused_cell in [(1, 1), (2, 1)]]
        + cell(x_cell, "21")
        + cell(y_cell, "321")
        + [
            GriddedPerm(above, (lower, x_cell)),
            GriddedPerm(above, (lower, y_cell)),
            GriddedPerm(above, (upper, x_cell)),
        ]
    )


def test_each_family_of_regriddings_is_complete_on_its_own():
    """Whether every regridding of an obstruction's block points is forbidden depends
    on the cells outside the block, not only on the pattern and the block's cells:
    the family of the lower cell is complete, that of the upper cell is not."""
    tiling = split_by_outside_cell()
    assert (
        KnuthSlide(tiling).why_not(1, 2)
        == "an obstruction depends on how the block's points are split"
    )
    assert not slides(tiling)
    assert counts(tiling, 5) != counts(naive_one_row_slide(tiling, 1, 2), 5)


def test_a_cell_closed_under_knuth_moves_but_not_the_shape_stops_the_slide():
    """Av(132, 312) in the first cell is closed under Knuth moves, not determined by
    the shape; the second cell lacks it, so it is not a window either, and the slide
    must refuse for the run's patterns, not accept it as a window. The naive slide
    changes the counts."""
    tiling = Tiling(
        cell(LEFT, "132", "312")
        + cell(RIGHT, "21")
        + list(griddings("1234", [LEFT, RIGHT]))
    )
    assert (
        KnuthSlide(tiling).why_not(0, 2)
        == "a run's patterns are not determined by the RSK shape"
    )
    assert not slides(tiling)
    assert counts(tiling, 6) != counts(naive_one_row_slide(tiling, 0, 2), 6)


def test_an_outside_point_between_the_blocks_values_is_not_a_window():
    """102 with its first point outside the block, in every regridding of the other
    two over the block's columns: the outside value lies between the block's, so the
    slide must refuse. The naive slide changes the counts (at size 5)."""
    outside, x_cell, y_cell = (0, 0), (1, 0), (2, 0)
    between = [
        GriddedPerm(Perm((1, 0, 2)), (outside,) + pair)
        for pair in combinations_with_replacement([x_cell, y_cell], 2)
    ]
    tiling = Tiling(cell(y_cell, "231") + between)
    assert tiling.dimensions == (3, 1)
    assert (
        KnuthSlide(tiling).why_not(1, 2)
        == "an obstruction depends on how the block's points are split"
    )
    assert not slides(tiling)
    assert counts(tiling, 5) != counts(naive_one_row_slide(tiling, 1, 2), 5)


def point_at(cell_):
    return GriddedPerm((0,), (cell_,))


OUTSIDE, TOP_OF_FIRST = (0, 0), (1, 1)


def ferrers_with(requirements=(), assumptions=()):
    """Babson and West's picture with a short column at the left (block: columns 1
    and 2, rows 0 and 1; the cell (0, 0) outside it)."""
    return Tiling(two_rows(1, [(0, 0)]).obstructions, requirements, assumptions)


@pytest.mark.parametrize(
    "requirements, assumptions, reason",
    [
        (
            [[point_at(OUTSIDE), point_at(TOP_OF_FIRST)]],
            [],
            "a requirement is on part of a column of the block",
        ),
        (
            [],
            [TrackingAssumption([point_at(OUTSIDE), point_at(TOP_OF_FIRST)])],
            "an assumption covers part of the block's columns and rows",
        ),
        (
            [],
            [SkewComponentAssumption([point_at(OUTSIDE), point_at(TOP_OF_FIRST)])],
            "an assumption that does not count points covers the block",
        ),
        (
            [],
            [
                TrackingAssumption([point_at(OUTSIDE)]),
                TrackingAssumption([point_at(TOP_OF_FIRST)]),
            ],
            "an assumption covers part of the block's columns and rows",
        ),
    ],
    ids=[
        "requirement starting outside the block",
        "assumption starting outside the block",
        "component assumption starting outside the block",
        "assumption after one with no point in the block",
    ],
)
def test_every_point_and_every_assumption_is_checked(requirements, assumptions, reason):
    """The check reads all the points of a requirement or an assumption, and all the
    assumptions: what is wrong with the block is not hidden behind a point outside it
    that comes first, or an assumption with no point in the block."""
    tiling = ferrers_with(requirements, assumptions)
    assert KnuthSlide(tiling).why_not(1, 2) == reason
    assert not [
        slide_rule for slide_rule in slides(tiling) if not slide_rule.strategy.transpose
    ]


@pytest.mark.parametrize(
    "requirements, assumptions",
    [
        ([[point_at((1, 1)), point_at((2, 1))]], []),
        ([], [TrackingAssumption([point_at((1, 1)), point_at((2, 1))])]),
    ],
    ids=["requirement on a row of the block", "assumption on a row of the block"],
)
def test_a_requirement_or_an_assumption_on_a_whole_row_of_the_block_slides(
    requirements, assumptions
):
    """The top row of the block, which the mirror takes to itself: the slide is
    accepted, and the parameter of the assumption is kept."""
    tiling = ferrers_with(requirements, assumptions)
    (rule,) = [
        slide_rule for slide_rule in slides(tiling) if not slide_rule.strategy.transpose
    ]
    assert rule.children[0].requirements == tiling.requirements
    assert rule.children[0].assumptions == tiling.assumptions
    sanity_check(rule, 5)


@pytest.mark.parametrize(
    "tiling", [babson_west, babson_west.inverse()], ids=["columns", "rows"]
)
def test_a_strategy_rebuilds_the_child_of_its_rule(tiling):
    """Applied to the tiling alone, as when a specification is read from JSON, a
    strategy gives back its rule's child, whether it slides columns or rows."""
    (rule,) = slides(tiling)
    assert rule.strategy.decomposition_function(tiling) == rule.children
    assert rule.strategy(tiling).children == rule.children


def pair_and_ferrers_block():
    """Babson and West's pair in columns 0 and 1, in the lowest row, and next to it a
    block of two columns and two rows (everything avoids 321, and column 2 avoids
    21)."""
    cells = [(0, 0), (1, 0), (2, 0), (2, 1), (3, 0), (3, 1)]
    return Tiling(
        list(griddings("321", cells))
        + cell((0, 0), "21")
        + list(griddings("21", [(2, 0), (2, 1)]))
        + [GriddedPerm((0,), (unused_cell,)) for unused_cell in [(0, 1), (1, 1)]]
    )


def test_one_line_only_leaves_out_the_blocks_of_several_rows():
    """With one_line_only the factory offers the slide of the pair in one row, and
    not that of the block of two rows next to it, which it offers by default."""
    tiling = pair_and_ferrers_block()
    both = slides(tiling)
    assert {(rule.strategy.start, rule.strategy.width) for rule in both} == {
        (0, 2),
        (2, 2),
    }
    assert not any(rule.strategy.transpose for rule in both)
    (one_row,) = slides(tiling, one_line_only=True)
    assert (one_row.strategy.start, one_row.strategy.width) == (0, 2)
    for rule in both:
        sanity_check(rule, 4)


def columns_of_cells(*rows_of_column):
    """A tiling of decreasing cells: column i has one in each row of rows_of_column[i],
    and the other cells of the column are empty."""
    height = max(y for rows in rows_of_column for y in rows) + 1
    obstructions = []
    for x, rows in enumerate(rows_of_column):
        for y in range(height):
            if y in rows:
                obstructions += cell((x, y), "12")
            else:
                obstructions.append(GriddedPerm((0,), ((x, y),)))
    return Tiling(obstructions)


BLOCKS_TILING = columns_of_cells((0,), (0,), (0,), (0,), (0, 1), (0, 1), (1,), (1,))


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, [(0, 2), (1, 2), (2, 2), (0, 3), (1, 3), (4, 2), (6, 2)]),
        (
            {"max_width": 4},
            [(0, 2), (1, 2), (2, 2), (0, 3), (1, 3), (0, 4), (4, 2), (6, 2)],
        ),
        ({"max_width": 2}, [(0, 2), (1, 2), (2, 2), (4, 2), (6, 2)]),
        ({"one_line_only": True}, [(0, 2), (1, 2), (2, 2), (0, 3), (1, 3), (6, 2)]),
    ],
    ids=["default", "max_width 4", "max_width 2", "one_line_only"],
)
def test_the_blocks_of_a_tiling(kwargs, expected):
    """Runs of adjacent columns with the same rows of cells, of 2 to max_width
    columns; with one_line_only, only those within one row. A run ends where the
    rows change and at the last column."""
    assert sorted(KnuthSlide(BLOCKS_TILING).blocks(**kwargs)) == sorted(expected)


@pytest.mark.parametrize(
    "tiling",
    [
        BLOCKS_TILING,
        columns_of_cells((0,), (1,), (0,), (1,)),
        columns_of_cells((0, 1), (0, 1)),
        columns_of_cells((0,), (0, 1), (1,)),
        babson_west,
        two_rows(1, [(0, 0), (3, 1)]),
    ],
    ids=[
        "blocks",
        "none",
        "one block of two rows",
        "no equal neighbors",
        "pair",
        "ferrers",
    ],
)
@pytest.mark.parametrize("transpose", [False, True])
@pytest.mark.parametrize("one_line_only", [False, True])
def test_has_blocks_says_whether_there_are_blocks(tiling, transpose, one_line_only):
    """The cheap test agrees with the blocks, for columns and for rows."""
    frame = tiling.inverse() if transpose else tiling
    assert KnuthSlide.has_blocks(tiling, transpose, one_line_only) == bool(
        list(KnuthSlide(frame).blocks(2, one_line_only))
    )
    if not transpose and not one_line_only:
        assert KnuthSlide.has_blocks(tiling) == KnuthSlide.has_blocks(
            tiling, False, False
        )
    assert KnuthSlide.has_blocks(tiling) == bool(list(KnuthSlide(tiling).blocks()))


@pytest.mark.parametrize(
    "tiling",
    [Tiling(), Tiling.from_string("1"), Tiling([GriddedPerm.empty_perm()])],
    ids=["a free cell", "Av(1)", "the empty tiling"],
)
def test_a_tiling_of_one_cell_has_nothing_to_slide(tiling):
    assert tiling.dimensions == (1, 1)
    assert not slides(tiling)
    assert not list(KnuthSlide(tiling).blocks())
    assert not KnuthSlide.has_blocks(tiling) and not KnuthSlide.has_blocks(tiling, True)


@pytest.mark.parametrize("max_width, rules", [(0, 0), (1, 0), (2, 1), (10, 1)])
def test_the_largest_width_of_a_block(max_width, rules):
    """A pair of columns slides when blocks of two columns are allowed, whether or not
    the limit is larger than the tiling is wide."""
    assert len(slides(babson_west, max_width=max_width)) == rules


def test_columns_that_are_not_a_block():
    """A block is two or more adjacent columns with the same rows of active cells."""
    knuth = KnuthSlide(two_rows(1, [(0, 0)]))
    for column, width in [(0, 0), (0, 1), (0, 2), (0, 3), (2, 2), (3, 2)]:
        assert knuth.why_not(column, width) == "the columns are not a block"
    with pytest.raises(ValueError, match="the block does not slide"):
        knuth.slide(0, 2)


def test_cells_that_are_windows_slide_though_the_shape_does_not_close_them():
    """Av(132, 312) in both cells jointly, in every gridding of the pair. Each cell's
    patterns, {132, 312}, are closed under Knuth moves but not determined by the
    shape; as the constraints are windows, with complete families, the block slides."""
    both = list(griddings("132", [LEFT, RIGHT])) + list(griddings("312", [LEFT, RIGHT]))
    tiling = Tiling(both + cell(RIGHT, "321"))
    (rule,) = slides(tiling)
    assert rule.children[0] == Tiling(both + cell(LEFT, "321"))
    assert_bijection(tiling, rule.children[0], rule.strategy, 5)
    sanity_check(rule, 5)


def test_windows_with_different_points_outside_are_closed_on_their_own():
    """Two points in a cell at the left of the pair, below the pair's points: Av(132)
    when they form a 12, Av(312) when they form a 21. {132, 312} is closed under Knuth
    moves, but each pattern alone is not: the windows are told apart by the pattern
    of the points outside. The naive slide changes the counts."""
    outside, x_cell, y_cell = (0, 0), (1, 0), (2, 0)
    obstructions = cell(outside, "123") + cell(x_cell, "21") + cell(y_cell, "321")
    for outside_pattern, block_pattern in [("12", "132"), ("21", "312")]:
        pattern = Perm(
            tuple(Perm.to_standard(outside_pattern))
            + tuple(value + 2 for value in Perm.to_standard(block_pattern))
        )
        for choice in combinations_with_replacement([x_cell, y_cell], 3):
            obstructions.append(GriddedPerm(pattern, (outside, outside) + choice))
    tiling = Tiling(obstructions)
    assert (
        KnuthSlide(tiling).why_not(1, 2)
        == "a window's patterns are not closed under Knuth moves"
    )
    assert not slides(tiling)
    assert counts(tiling, 6) != counts(naive_one_row_slide(tiling, 1, 2), 6)


FRONT, FIRST, SECOND = (0, 0), (1, 0), (2, 0)


@pytest.mark.parametrize(
    "requirements, assumptions, identity",
    [
        ([], [], True),
        ([[point_at(FIRST)]], [], False),
        ([[point_at(FIRST), point_at(SECOND)]], [], True),
        ([], [TrackingAssumption([point_at(FIRST)])], False),
        ([], [TrackingAssumption([point_at(FIRST), point_at(SECOND)])], True),
    ],
    ids=[
        "twins",
        "requirement on one",
        "requirement on both",
        "assumption on one",
        "assumption on both",
    ],
)
def test_a_slide_is_an_identity_when_the_requirements_and_assumptions_are_symmetric(
    requirements, assumptions, identity
):
    """Two identical cells, with a cell in front of them, so that the block does not
    start at column 0: the slide is the identity exactly when its requirements and
    assumptions are the same with the block mirrored; otherwise it gives a rule."""
    tiling = Tiling(
        cell(FRONT, "12")
        + cell(FIRST, "21")
        + cell(SECOND, "21")
        + list(griddings("21", [FIRST, SECOND])),
        requirements,
        assumptions,
    )
    knuth = KnuthSlide(tiling)
    assert knuth.why_not(1, 2) is None
    assert knuth.is_identity(1, 2) == identity
    rules = [
        slide_rule
        for slide_rule in slides(tiling)
        if (slide_rule.strategy.start, slide_rule.strategy.width) == (1, 2)
    ]
    assert bool(rules) == (not identity)
    for rule in rules:
        assert rule.children[0] != tiling
        sanity_check(rule, 4)


def test_the_parameters_of_a_strategy_without_its_children():
    """The strategy maps the parent's parameters to the child's, whether or not it is
    given the child, and it reads as its step."""
    tiling = Tiling(
        babson_west.obstructions, [], [TrackingAssumption([point_at(LEFT)])]
    )
    (rule,) = slides(tiling)
    assert rule.strategy.extra_parameters(tiling) == ({"k_0": "k_0"},)
    assert rule.strategy.extra_parameters(tiling, rule.children) == ({"k_0": "k_0"},)
    assert rule.strategy.extra_parameters(babson_west) == ({},)
    assert not KnuthSlideStrategy(0, 2).transpose
    assert str(rule.strategy) == "Knuth slide of the 2 columns from column 0"
    (transposed,) = slides(babson_west.inverse())
    assert str(transposed.strategy) == "Knuth slide of the 2 rows from row 0"


def test_a_contradictory_obstruction_does_not_give_a_wrong_slide():
    """Tilings keeps an obstruction that no gridding can have: here the 10 from cell
    (0, 0) to cell (2, 1), whose higher value is on the left but in the lower row.
    It is all that keeps the free cell (0, 0) active, and it has no regriddings, so
    the child of the slide of the first two columns would lose a column: the slide
    refuses the block, and the factory offers no rule."""
    tiling = Tiling(
        [
            GriddedPerm(Perm((0, 1)), [(1, 0), (1, 0)]),
            GriddedPerm(Perm((1, 0)), [(1, 0), (1, 0)]),
            GriddedPerm(Perm((1, 0)), [(0, 0), (2, 1)]),
            GriddedPerm(Perm((1, 0)), [(2, 1), (2, 1)]),
        ]
    )
    assert [
        obstruction
        for obstruction in tiling.obstructions
        if obstruction.contradictory()
    ]
    assert (
        KnuthSlide(tiling).why_not(0, 2)
        == "an obstruction with points in the block is contradictory"
    )
    assert not slides(tiling)


def two_points_left_of_the_pair():
    """Two cells of at most one point each, left of Babson and West's pair and below
    it: the pair's word avoids 132 when the first has a point, and 312 when the
    second has one."""
    first, second, x_cell, y_cell = (0, 0), (1, 0), (2, 0), (3, 0)
    obstructions = (
        cell(first, "12", "21")
        + cell(second, "12", "21")
        + cell(x_cell, "21")
        + cell(y_cell, "321")
    )
    for point, pattern in ((first, "132"), (second, "312")):
        word = Perm((0,) + tuple(value + 1 for value in Perm.to_standard(pattern)))
        for choice in combinations_with_replacement([x_cell, y_cell], len(pattern)):
            obstructions.append(GriddedPerm(word, (point,) + choice))
    return Tiling(obstructions)


def test_windows_whose_outside_points_are_in_other_cells_are_closed_on_their_own():
    """{132, 312} is closed under Knuth moves, but neither pattern alone is: the two
    windows have the same outside pattern below the pair, in different cells, and
    each must be closed on its own, so the slide refuses. Were the two merged, the
    slide would map some gridded permutations out of the child, though the counts
    agree."""
    tiling = two_points_left_of_the_pair()
    assert not any(obstruction.contradictory() for obstruction in tiling.obstructions)
    assert (
        KnuthSlide(tiling).why_not(2, 2)
        == "a window's patterns are not closed under Knuth moves"
    )
    assert not [
        rule
        for rule in slides(tiling)
        if rule.strategy.start == 2 and not rule.strategy.transpose
    ]
    naive = naive_one_row_slide(tiling, 2, 2)
    assert counts(tiling, 5) == counts(naive, 5)
    images = {
        KnuthSlide.slide_gridded_perm(gridded_perm, 2, 2)
        for gridded_perm in tiling.objects_of_size(4)
    }
    assert not images <= set(naive.objects_of_size(4))


def test_a_contradictory_obstruction_away_from_the_block_does_not_stop_the_slide():
    """Only an obstruction with points in the block must be one some gridded
    permutation can have. Here the 10 from cell (2, 0) to cell (3, 1), whose higher
    value is on the left but in the lower row, is away from the pair in columns 0 and
    1: it stays in the child as it is, and the slide is a bijection."""
    away = GriddedPerm(Perm((1, 0)), [(2, 0), (3, 1)])
    assert away.contradictory()
    tiling = Tiling(babson_west.obstructions + (away,))
    assert tiling.dimensions == (4, 2)
    (rule,) = slides(tiling)
    assert (rule.strategy.start, rule.strategy.width) == (0, 2)
    assert rule.children[0] == Tiling(
        slides(babson_west)[0].children[0].obstructions + (away,)
    )
    assert away in rule.children[0].obstructions
    assert_bijection(tiling, rule.children[0], rule.strategy, 3)
    sanity_check(rule, 3)


def test_the_parameters_of_two_assumptions_change_places():
    """An assumption on each cell of the pair: the slide takes the parameter of each
    to the child's parameter of the other, for columns and for rows. An identity map
    would pass with one assumption, whose parameter is its own either way."""
    tiling = Tiling(
        babson_west.obstructions,
        [],
        [TrackingAssumption([point_at(LEFT)]), TrackingAssumption([point_at(RIGHT)])],
    )
    for frame in (tiling, tiling.inverse()):
        (rule,) = slides(frame)
        swapped = ({"k_0": "k_1", "k_1": "k_0"},)
        assert rule.strategy.extra_parameters(frame, rule.children) == swapped
        assert rule.strategy.extra_parameters(frame) == swapped
        sanity_check(rule, 5)


def test_a_requirement_or_an_assumption_on_more_than_a_point_stops_the_slide():
    """A requirement or an assumption whose gridded permutation has two points, in
    the block: the mirror would take its points out of order."""
    two_points = GriddedPerm(Perm((0, 1)), (LEFT, RIGHT))
    with_requirement = Tiling(babson_west.obstructions, [[two_points]])
    assert (
        KnuthSlide(with_requirement).why_not(0, 2)
        == "a requirement other than points has points in the block"
    )
    assert not slides(with_requirement)
    with_assumption = Tiling(
        babson_west.obstructions, [], [TrackingAssumption([two_points])]
    )
    assert (
        KnuthSlide(with_assumption).why_not(0, 2)
        == "an assumption on more than a point has points in the block"
    )
    assert not slides(with_assumption)


def test_a_tiling_with_an_empty_row_does_not_slide():
    """A block of two rows with an empty row between them: the child would lose the
    empty row, and the map would not fit it."""
    cells = [(0, 0), (0, 2), (1, 0), (1, 2)]
    tiling = Tiling(
        list(griddings("12", cells)) + [point_at((0, 1)), point_at((1, 1))],
        remove_empty_rows_and_cols=False,
    )
    assert tiling.dimensions == (2, 3)
    assert KnuthSlide(tiling).why_not(0, 2) == "the tiling has an empty row or column"
    assert not slides(tiling)


@pytest.mark.parametrize("transpose", [False, True])
@pytest.mark.parametrize(
    "start, width", [(-1, 2), (1, 2), (0, 3), (5, 2), (0, 0), (1, 1)]
)
def test_a_block_that_does_not_fit_the_tiling_is_refused(start, width, transpose):
    """A block that starts before the first column, ends after the last, or is
    narrower than two columns, as a saved specification could name for another
    tiling: the strategy does not apply, in columns and in rows."""
    from comb_spec_searcher.exception import StrategyDoesNotApply

    tiling = babson_west.inverse() if transpose else babson_west
    assert (
        KnuthSlide(babson_west).why_not(start, width) == "the columns are not a block"
    )
    with pytest.raises(StrategyDoesNotApply):
        KnuthSlideStrategy(start, width, transpose)(tiling)


def test_requirements_and_assumptions_next_to_the_block_stay_where_they_are():
    """Requirements and assumptions on a point in the cell before the block and on
    one in the cell after it are not mirrored: the block is the columns 1 and 2."""
    before, after = (0, 0), (3, 0)
    tiling = Tiling(
        cell(before, "12")
        + cell(FIRST, "21")
        + cell(SECOND, "321")
        + griddings_of("321", FIRST, SECOND, SECOND)
        + cell(after, "12"),
        [[point_at(before)], [point_at(after)]],
        [TrackingAssumption([point_at(before)]), TrackingAssumption([point_at(after)])],
    )
    (rule,) = [
        slide_rule
        for slide_rule in slides(tiling)
        if (slide_rule.strategy.start, slide_rule.strategy.width) == (1, 2)
    ]
    assert rule.children[0].requirements == tiling.requirements
    assert rule.children[0].assumptions == tiling.assumptions
    assert rule.strategy.extra_parameters(tiling, rule.children) == (
        {"k_0": "k_0", "k_1": "k_1"},
    )
    sanity_check(rule, 4)


@pytest.mark.parametrize("transpose", [False, True], ids=["columns", "rows"])
def test_requirements_and_assumptions_of_a_block_of_three(transpose):
    """A requirement and an assumption on the first of three columns (or rows) go to
    the third, and an assumption on the middle one stays: the mirror is not that of a
    block of two."""
    staircase = decreasing_staircase([4, 3, 2])
    columns = Tiling(
        staircase.obstructions,
        [[point_at((0, 0))]],
        [
            TrackingAssumption([point_at((0, 0))]),
            TrackingAssumption([point_at((1, 0))]),
        ],
    )
    tiling = columns.inverse() if transpose else columns
    (rule,) = [
        slide_rule for slide_rule in slides(tiling) if slide_rule.strategy.width == 3
    ]
    expected = Tiling(
        decreasing_staircase([4, 3, 2], mirrored=True).obstructions,
        [[point_at((2, 0))]],
        [
            TrackingAssumption([point_at((1, 0))]),
            TrackingAssumption([point_at((2, 0))]),
        ],
    )
    assert rule.strategy.transpose == transpose
    assert rule.children[0] == (expected.inverse() if transpose else expected)
    assert rule.strategy.extra_parameters(tiling, rule.children) == (
        {"k_0": "k_1", "k_1": "k_0"},
    )
    assert_bijection(tiling, rule.children[0], rule.strategy, 4)
    sanity_check(rule, 4)


def test_the_families_of_a_window_are_told_apart_by_the_rows_they_span():
    """Two columns and two rows, and a cell at the right of the block. The top row
    avoids 21 across both cells, so the 21s there, regridded over the columns, are all
    forbidden. In the bottom row only the second cell avoids 21, so the 21 there is
    not a complete family. The two have the same pattern, no points outside the block
    and the same columns: they differ in rows only, and the slide must refuse."""
    after = (2, 0)
    tiling = Tiling(
        list(griddings("21", [(0, 1), (1, 1)]))
        + cell((1, 0), "21")
        + griddings_of("12", (0, 0), after)
        + griddings_of("12", (1, 0), after)
    )
    assert tiling.dimensions == (3, 2)
    assert (
        KnuthSlide(tiling).why_not(0, 2)
        == "an obstruction depends on how the block's points are split"
    )
    assert not [
        slide_rule for slide_rule in slides(tiling) if not slide_rule.strategy.transpose
    ]


@pytest.mark.parametrize(
    "tiling",
    [
        two_rows(1, [(0, 0), (3, 1)]),
        pair_above_a_column(2),
        decreasing_staircase([4, 3, 2]),
    ],
    ids=["ferrers, both sides", "above a column", "three columns"],
)
def test_the_child_of_a_slide_has_only_possible_obstructions(tiling):
    """The regriddings of an obstruction are valid griddings without any bound on the
    rows, as the obstruction is not contradictory: no obstruction of the child is."""
    assert not any(obstruction.contradictory() for obstruction in tiling.obstructions)
    rules = slides(tiling)
    assert rules
    for rule in rules:
        assert not any(
            obstruction.contradictory() for obstruction in rule.children[0].obstructions
        )


def pair_and_point(window):
    """Babson and West's pair, and to its right a point that lies above the pair's
    points: the pair's word, with the point after it, avoids the window's patterns.
    The mirror image of point_and_pair's picture."""
    x_cell, y_cell, point = (0, 0), (1, 0), (2, 0)
    obstructions = cell(point, "12", "21") + cell(x_cell, "123") + cell(y_cell, "21")
    for pattern in window:
        word = Perm(tuple(Perm.to_standard(pattern)) + (len(pattern),))
        for choice in combinations_with_replacement([x_cell, y_cell], len(pattern)):
            obstructions.append(GriddedPerm(word, choice + (point,)))
    return Tiling(obstructions, [[GriddedPerm((0,), (point,))]])


def test_a_window_with_a_point_to_the_right_slides():
    """{132, 312} is closed under Knuth moves, and the pair's windows have the point
    after them, as point_and_pair's have it before: the patterns that the block sees
    are the pair's alone, not the pair with the point, and the slide is offered."""
    tiling = pair_and_point(["132", "312"])
    assert KnuthSlide(tiling).why_not(0, 2) is None
    (rule,) = [
        slide_rule
        for slide_rule in slides(tiling)
        if (slide_rule.strategy.start, slide_rule.strategy.width) == (0, 2)
    ]
    assert_bijection(tiling, rule.children[0], rule.strategy, 6)
    sanity_check(rule, 5)


@pytest.mark.parametrize(
    "increasing_cells",
    [[(0, 0), (1, 0), (1, 1)], [(0, 0), (0, 1), (1, 1)]],
    ids=["a 10 in the top row", "a 10 in the bottom row"],
)
@pytest.mark.parametrize("pattern", ["021", "102"])
def test_a_window_in_either_row_of_the_block_must_be_closed_under_knuth_moves(
    pattern, increasing_cells
):
    """The pattern avoided in the four cells of two columns and two rows jointly, with
    the 10s of three of the cells forbidden. 021 and 201, like 102 and 120, are Knuth
    equivalent, so the windows' patterns are not closed under Knuth moves, however
    few of a pattern's points lie in one of the block's rows."""
    cells = [(0, 0), (0, 1), (1, 0), (1, 1)]
    tiling = Tiling(
        list(griddings("10", increasing_cells)) + list(griddings(pattern, cells))
    )
    assert tiling.dimensions == (2, 2)
    assert (
        KnuthSlide(tiling).why_not(0, 2)
        == "a window's patterns are not closed under Knuth moves"
    )
    assert not [
        slide_rule for slide_rule in slides(tiling) if not slide_rule.strategy.transpose
    ]


def test_one_line_only_leaves_out_the_blocks_of_several_columns_of_cells():
    """The same for rows: with one_line_only the factory offers the slide of the pair
    in one column of cells, and not that of the block of two columns of cells next to
    it, which it offers by default."""
    tiling = pair_and_ferrers_block().inverse()
    both = slides(tiling)
    assert {(rule.strategy.start, rule.strategy.width) for rule in both} == {
        (0, 2),
        (2, 2),
    }
    assert all(rule.strategy.transpose for rule in both)
    (one_column,) = slides(tiling, one_line_only=True)
    assert (one_column.strategy.start, one_column.strategy.width) == (0, 2)
    assert one_column.strategy.transpose


@pytest.mark.parametrize(
    "requirements, assumptions",
    [
        ([[GriddedPerm(Perm((0, 1)), (OUTSIDE, OUTSIDE))]], []),
        ([], [TrackingAssumption([GriddedPerm(Perm((0, 1)), (OUTSIDE, OUTSIDE))])]),
        ([], [SumComponentAssumption([point_at(OUTSIDE)])]),
    ],
    ids=[
        "requirement of two points",
        "assumption on two points",
        "assumption counting components",
    ],
)
def test_a_requirement_or_an_assumption_away_from_the_block_does_not_stop_the_slide(
    requirements, assumptions
):
    """Only those with points in the block must be on points and count points: these
    are in the cell before the block, which the slide leaves as it is."""
    tiling = ferrers_with(requirements, assumptions)
    (rule,) = [
        slide_rule for slide_rule in slides(tiling) if not slide_rule.strategy.transpose
    ]
    assert rule.children[0].requirements == tiling.requirements
    assert rule.children[0].assumptions == tiling.assumptions
    sanity_check(rule, 4)


def test_the_factory_s_json_keys():
    """The keys a saved specification holds, which cannot change after release."""
    factory = KnuthSlideFactory(max_width=2, one_line_only=True, slide_rows=False)
    assert factory.to_jsonable() == {
        "class_module": "tilings.strategies.knuth_slide",
        "strategy_class": "KnuthSlideFactory",
        "max_width": 2,
        "one_line_only": True,
        "slide_rows": False,
    }

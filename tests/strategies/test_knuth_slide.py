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
with open(os.path.join(__location__, "knuth_slide_15432.json")) as fp:
    AV_15432_BLOCKS = {
        name: (Tiling.from_dict(d["tiling"]), d["col"], d["width"])
        for name, d in json.load(fp).items()
    }


def cell(cell_, *patts):
    return [GriddedPerm(Perm.to_standard(p), [cell_] * len(p)) for p in patts]


def griddings_of(patt, *cells):
    return [GriddedPerm(Perm.to_standard(patt), cells)]


def griddings(patt, cells):
    """Every valid gridding of patt over the cells."""
    patt = Perm.to_standard(patt)
    for pos in product(cells, repeat=len(patt)):
        if any(pos[i][0] > pos[i + 1][0] for i in range(len(patt) - 1)):
            continue
        if any(
            patt[i] < patt[j] and pos[i][1] > pos[j][1]
            for i in range(len(patt))
            for j in range(len(patt))
        ):
            continue
        yield GriddedPerm(patt, pos)


def assert_bijection(parent, child, strategy, length):
    """The forward map takes the parent's gridded permutations of each size onto the
    child's, and the backward map takes them back."""
    for n in range(length + 1):
        parent_gps = set(parent.objects_of_size(n))
        images = {strategy.forward_map(parent, gp)[0] for gp in parent_gps}
        assert images == set(child.objects_of_size(n))
        assert {next(strategy.backward_map(parent, (gp,))) for gp in images} == (
            parent_gps
        )


def sanity_check(rule, length):
    for n in range(length + 1):
        assert rule.sanity_check(n)


def slides(tiling, **kwargs):
    return list(KnuthSlideFactory(**kwargs)(tiling))


def naive_one_row_slide(tiling, col, width):
    """The child the slide would have if every obstruction inside one cell were the
    cell's own and every other one a window constraint: the cells' obstructions
    mirrored, the others regridded over the block."""
    cells = [(col + i, 0) for i in range(width)]
    mirror = {c: cells[width - 1 - i] for i, c in enumerate(cells)}
    obs = set()
    for ob in tiling.obstructions:
        idx = [i for i, c in enumerate(ob.pos) if c in cells]
        if not idx:
            obs.add(ob)
        elif len(idx) == len(ob) and len({ob.pos[i] for i in idx}) == 1:
            obs.add(GriddedPerm(ob.patt, [mirror[c] for c in ob.pos]))
        else:
            for choice in combinations_with_replacement(cells, len(idx)):
                pos = list(ob.pos)
                for i, c in zip(idx, choice):
                    pos[i] = c
                obs.add(GriddedPerm(ob.patt, pos))
    reqs = [
        [GriddedPerm(gp.patt, [mirror.get(c, c) for c in gp.pos]) for gp in req]
        for req in tiling.requirements
    ]
    return Tiling(obs, reqs)


ROW_PLACEMENTS = TileScopePack.row_and_col_placements(row_only=True).make_fusion(
    tracked=False
)
COL_PLACEMENTS = TileScopePack.row_and_col_placements(col_only=True).make_fusion(
    tracked=False
)


def counts(tiling, length):
    return [sum(1 for _ in tiling.objects_of_size(n)) for n in range(length + 1)]


# Babson and West's pair: an increasing cell next to a 321-avoiding one, jointly
# 321-avoiding (the Catalan numbers either way round).
X, Y = (0, 0), (1, 0)
babson_west = Tiling(
    cell(X, "21") + cell(Y, "321") + [GriddedPerm(Perm((2, 1, 0)), (X, Y, Y))]
)


def test_babson_west_pair():
    (rule,) = slides(babson_west)
    child = rule.children[0]
    assert child == Tiling(
        cell(Y, "21") + cell(X, "321") + [GriddedPerm(Perm((2, 1, 0)), (X, X, Y))]
    )
    assert (
        counts(babson_west, 7) == counts(child, 7) == [1, 2, 5, 14, 42, 132, 429, 1430]
    )
    assert_bijection(babson_west, child, rule.strategy, 6)
    sanity_check(rule, 6)


@pytest.mark.parametrize("name", sorted(AV_15432_BLOCKS))
def test_three_column_slides_of_av_15432(name):
    """The three blocks of three cells that Av(15432)'s specification reverses."""
    tiling, col, width = AV_15432_BLOCKS[name]
    rules = [
        rule
        for rule in slides(tiling)
        if rule.strategy.col == col and rule.strategy.width == width
    ]
    assert len(rules) == 1
    assert_bijection(tiling, rules[0].children[0], rules[0].strategy, 5)
    sanity_check(rules[0], 5)


def test_three_distinct_cells_do_not_slide_two_at_a_time():
    """[Av(15432) | Av(4321) | Av(321) | inc]: the last two cells avoid 321 together,
    and all three avoid 4321, so only the pair (Av(321), inc) slides; the naive slide
    of the others changes the counts."""
    tiling, _, _ = AV_15432_BLOCKS["04321|3210|210|10"]
    ks = KnuthSlide(tiling)
    assert ks.why_not(1, 3) is None
    assert ks.why_not(2, 2) is None
    for col in (0, 1):
        assert ks.why_not(col, 2) is not None
        assert counts(tiling, 5) != counts(naive_one_row_slide(tiling, col, 2), 5)


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
            children = {r.children[0] for r in slides(tiling)}
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
                children = {r.children[0] for r in slides(tiling, max_width=2)}
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
    strip = [c for c in cells if c[0] == strip_column]
    return Tiling(list(griddings("321", cells)) + list(griddings("21", strip)) + empty)


@pytest.mark.parametrize(
    "short_columns", [[(0, 0)], [(0, 0), (3, 1)]], ids=["left", "both sides"]
)
def test_the_ferrers_version(short_columns):
    parent = two_rows(1, short_columns)
    (rule,) = [r for r in slides(parent) if not r.strategy.transpose]
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
    obs = cell(point, "12", "21") + cell(x_cell, *x_basis) + cell(y_cell, *y_basis)
    for patt in window:
        lifted = (0,) + tuple(v + 1 for v in Perm.to_standard(patt))
        for choice in combinations_with_replacement([x_cell, y_cell], len(patt)):
            obs.append(GriddedPerm(Perm(lifted), (point,) + choice))
    return Tiling(obs, [[GriddedPerm((0,), (point,))]])


def shape_31():
    """The nine permutations of RSK shape (3, 1): a class determined by the shape,
    whose basis is not monotone."""
    return [
        Perm(p)
        for p in permutations(range(4))
        if tuple(len(row) for row in rsk(p)[0]) == (3, 1)
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
    "tiling, col",
    [
        (Tiling(cell(X, "132") + cell(Y, "21") + list(griddings("1234", [X, Y]))), 0),
        (point_and_pair(["21"], ["321"], ["132"]), 1),
        (
            Tiling(cell(X, "21") + cell(Y, "12") + [GriddedPerm(Perm((1, 0)), (X, Y))]),
            0,
        ),
    ],
    ids=["cell not shape-closed", "window not Knuth-closed", "split-dependent"],
)
def test_each_condition_is_needed(tiling, col):
    """Each tiling breaks one condition: the slide refuses it, and the naive slide
    changes the counts."""
    assert KnuthSlide(tiling).why_not(col, 2) is not None
    assert not [r for r in slides(tiling) if r.strategy.col == col]
    assert counts(tiling, 6) != counts(naive_one_row_slide(tiling, col, 2), 6)


def test_requirements_and_assumptions_follow_the_cells():
    tiling = Tiling(
        babson_west.obstructions,
        [[GriddedPerm((0,), (X,))]],
        [TrackingAssumption([GriddedPerm((0,), (X,))])],
    )
    (rule,) = slides(tiling)
    child = rule.children[0]
    assert child.requirements == ((GriddedPerm((0,), (Y,)),),)
    assert child.assumptions == (TrackingAssumption([GriddedPerm((0,), (Y,))]),)
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
    (rule,) = [r for r in slides(whole_column) if not r.strategy.transpose]
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
        TrackingAssumption([GriddedPerm((0, 1), (X, Y))]),
        SumComponentAssumption([GriddedPerm((0,), (X,)), GriddedPerm((0,), (Y,))]),
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
        babson_west.obstructions, [], [TrackingAssumption([GriddedPerm((0,), (X,))])]
    ).inverse()
    (rule,) = slides(tiling)
    assert rule.strategy.transpose
    assert rule.children[0] == slides(tiling.inverse())[0].children[0].inverse()
    assert_bijection(tiling, rule.children[0], rule.strategy, 5)
    sanity_check(rule, 6)


def test_identical_columns_give_no_rule():
    twins = Tiling(cell(X, "21") + cell(Y, "21") + list(griddings("21", [X, Y])))
    assert KnuthSlide(twins).why_not(0, 2) is None
    assert KnuthSlide(twins).is_identity(0, 2)
    assert not slides(twins)


def test_factory_options():
    tiling, _, _ = AV_15432_BLOCKS["04321|3210|10|210|3210"]
    widths = {rule.strategy.width for rule in slides(tiling)}
    assert 3 in widths
    assert {rule.strategy.width for rule in slides(tiling, max_width=2)} <= {2}
    assert not [
        r for r in slides(two_rows(1, [(0, 0)]), rows=False) if not r.strategy.transpose
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
            Tiling(cell(X, "21") + cell(Y, "12") + [GriddedPerm(Perm((1, 0)), (X, Y))])
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
    assert [spec.count_objects_of_size(n) for n in range(9)] == [
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
    assert [spec.count_objects_of_size(n) for n in range(10)] == [
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
        r for rule in spec.rules_dict.values() for r in getattr(rule, "rules", (rule,))
    ]
    knuth = [r.strategy for r in rules if isinstance(r.strategy, KnuthSlideStrategy)]
    assert any(strategy.transpose for strategy in knuth)
    expected = [1, 1, 2, 6, 23, 103, 513, 2761, 15767]
    assert [spec.count_objects_of_size(n) for n in range(9)] == expected
    again = CombinatorialSpecification.from_dict(
        json.loads(json.dumps(spec.to_jsonable()))
    )
    assert [again.count_objects_of_size(n) for n in range(9)] == expected
    assert spec.random_sample_object_of_size(7).patt.avoids(Perm((0, 3, 2, 1)))
    spec.sanity_check(4)

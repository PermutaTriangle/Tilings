import logging

import pytest
from logzero import logger

from tilings import GriddedPerm, Tiling, TrackingAssumption
from tilings.strategies.fusion import FusionStrategy

LOGGER = logging.getLogger(__name__)


def reverse_fusion_rules():
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (3, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (1, 0), (4, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (3, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (2, 0), (4, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (3, 0), (4, 0))),
            GriddedPerm((0, 1, 2), ((1, 0), (4, 0), (4, 0))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (3, 0))),
            GriddedPerm((0, 1, 2), ((2, 0), (2, 0), (4, 0))),
            GriddedPerm((0, 1, 2), ((2, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2), ((2, 0), (3, 0), (4, 0))),
            GriddedPerm((0, 1, 2), ((2, 0), (4, 0), (4, 0))),
            GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2), ((3, 0), (3, 0), (4, 0))),
            GriddedPerm((0, 1, 2), ((3, 0), (4, 0), (4, 0))),
            GriddedPerm((0, 1, 2), ((4, 0), (4, 0), (4, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (0, 0), (4, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (1, 0), (1, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (1, 0), (2, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (1, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (1, 0), (4, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (2, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (2, 0), (4, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (3, 0), (3, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (3, 0), (4, 0))),
            GriddedPerm((0, 1, 2, 3), ((0, 0), (0, 0), (4, 0), (4, 0))),
        ),
        requirements=(),
        assumptions=(),
    )
    left_overlap = TrackingAssumption.from_cells([(0, 0), (1, 0)])
    left = TrackingAssumption.from_cells([(1, 0)])
    right = TrackingAssumption.from_cells([(2, 0)])
    right_overlap = TrackingAssumption.from_cells([(2, 0), (3, 0)])
    # Only track left of the fuse region
    t1 = t.add_assumptions([left_overlap, right_overlap, left])
    yield FusionStrategy(col_idx=1, tracked=True)(t1).to_reverse_rule(0)
    # Only track right of the fuse region
    t2 = t.add_assumptions([left_overlap, right_overlap, right])
    yield FusionStrategy(col_idx=1, tracked=True)(t2).to_reverse_rule(0)
    # Only track the bottom of the fuse region
    yield FusionStrategy(row_idx=1, tracked=True)(t1.rotate270()).to_reverse_rule(0)
    # Only track the top of the fuse region
    yield FusionStrategy(row_idx=1, tracked=True)(t2.rotate270()).to_reverse_rule(0)
    # Track both side of the fuse region
    t3 = t.add_assumptions([left_overlap, right_overlap, left, right])
    yield FusionStrategy(col_idx=1, tracked=True)(t3).to_reverse_rule(0)
    yield FusionStrategy(row_idx=1, tracked=True)(t3.rotate270()).to_reverse_rule(0)

    left_requirement = [GriddedPerm.point_perm((1, 0))]
    right_requirement = [GriddedPerm.point_perm((2, 0))]
    t4 = t.add_assumptions([left_overlap, left]).add_list_requirement(right_requirement)
    yield FusionStrategy(col_idx=1, tracked=True)(t4).to_reverse_rule(0)
    t5 = t.add_assumptions([left_overlap, left]).add_list_requirement(left_requirement)
    yield FusionStrategy(col_idx=1, tracked=True)(t5).to_reverse_rule(0)

    # # FOR A MORE EXHAUSTIVE SET OF TESTS UNCOMMENT THE FOLLOWING
    # from itertools import chain, combinations
    #
    # for assumptions in chain.from_iterable(
    #     combinations([left, right, left_overlap, right_overlap], i) for i in range(5)
    # ):
    #     for reqs in chain.from_iterable(
    #         combinations([left_requirement, right_requirement], i) for i in range(2)
    #     ):
    #         tiling = t.add_assumptions(assumptions)
    #         for req in reqs:
    #             tiling = tiling.add_list_requirement(req)
    #         rule = FusionStrategy(col_idx=1, tracked=True)(tiling)
    #         rotate_tiling = tiling.rotate270()
    #         rotate_rule = FusionStrategy(row_idx=1, tracked=True)(rotate_tiling)
    #         yield rule
    #         if left in assumptions or right in assumptions:
    #             yield rule.to_reverse_rule(0)
    #             yield rotate_rule.to_reverse_rule(0)


@pytest.fixture
def both_reverse_fusion_rule():
    rule = list(reverse_fusion_rules())[4]
    assert len(rule.comb_class.assumptions) == 3
    assert len(rule.children[0].assumptions) == 4
    return rule


def test_forward_map(both_reverse_fusion_rule):
    constructor = both_reverse_fusion_rule.constructor
    assert constructor.forward_map((0, 0, 0, 0)) == (0, 0, 0)
    assert constructor.forward_map((1, 0, 0, 0)) == (1, 0, 0)
    assert constructor.forward_map((1, 1, 0, 0)) == (1, 1, 1)
    assert constructor.forward_map((0, 0, 1, 1)) == (1, 1, 1)
    assert constructor.forward_map((0, 0, 0, 1)) == (0, 0, 1)


@pytest.mark.parametrize("rule", reverse_fusion_rules())
def test_sanity_check(rule):
    for length in range(6):
        assert rule.sanity_check(length)


def test_positive_reverse_fusion(caplog):
    t = Tiling(
        obstructions=[
            GriddedPerm((0, 1), [(0, 0), (0, 0)]),
            GriddedPerm((0, 1), [(0, 0), (1, 0)]),
            GriddedPerm((0, 1), [(1, 0), (1, 0)]),
        ],
        requirements=[[GriddedPerm((0,), [(0, 0)])]],
        assumptions=[TrackingAssumption([GriddedPerm((0,), [(0, 0)])])],
    )
    rule = FusionStrategy(col_idx=0, tracked=True)(t)
    assert rule.is_reversible()
    reverse_rule = rule.to_reverse_rule(0)
    logger.propagate = True
    with caplog.at_level(logging.WARNING):
        assert reverse_rule.sanity_check(4)
        assert len(caplog.records) == 1
        assert "Skipping sanity checking generation" in caplog.text

import pytest

from tilings import GriddedPerm, Tiling, TrackingAssumption
from tilings.strategies.fusion import FusionStrategy


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

import pytest
import sympy

from tilings import GriddedPerm, Tiling, TrackingAssumption
from tilings.strategies.detect_components import DetectComponentsStrategy

x, u, v = sympy.symbols("x k_0 k_1")


@pytest.mark.parametrize(
    ("tracked_cell", "child_markers"),
    [((2, 0), (u * v,)), ((1, 0), (v, u))],
    ids=["shared-marker", "swapped-markers"],
)
def test_removed_point_and_surviving_markers(tracked_cell, child_markers):
    left, middle, right = (0, 0), (1, 0), (2, 0)
    # The left cell contains exactly one point. The other two are increasing.
    tiling = Tiling(
        obstructions=[
            GriddedPerm.single_cell((0, 1), left),
            *(GriddedPerm.single_cell((1, 0), cell) for cell in (left, middle, right)),
        ],
        requirements=[[GriddedPerm.point_perm(left)]],
        assumptions=[
            TrackingAssumption.from_cells([left, right]),
            TrackingAssumption.from_cells([tracked_cell]),
        ],
    )
    rule = DetectComponentsStrategy()(tiling)
    (child,) = rule.children
    labels = (tiling, child).index
    for n in range(1, 4):
        assert rule.constructor.get_terms(tiling.get_terms, (child.get_terms,), n) == (
            tiling.get_terms(n)
        )

    eq = rule.get_equation(lambda t: t.get_function(labels))
    assert eq == sympy.Eq(
        tiling.get_function(labels), u * sympy.Function("F_1")(x, *child_markers)
    )


def test_no_component_to_remove():
    tiling = Tiling.from_string("210").add_assumption(
        TrackingAssumption.from_cells([(0, 0)])
    )
    rule = DetectComponentsStrategy()(tiling)
    assert rule.children == (tiling,)
    assert rule.get_equation(lambda t: t.get_function(lambda _: 0)) == sympy.true

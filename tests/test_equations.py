import sympy

from tilings import GriddedPerm, Tiling, TrackingAssumption
from tilings.strategies.requirement_insertion import RequirementInsertionStrategy


def test_complement():
    parent = Tiling(
        obstructions=[
            GriddedPerm.single_cell((0, 1), (0, 0)),
            GriddedPerm.single_cell((0, 1), (1, 1)),
            GriddedPerm.single_cell((0, 1), (2, 2)),
        ],
        requirements=[
            [
                GriddedPerm.single_cell((0,), (0, 0)),
                GriddedPerm.single_cell((0,), (1, 1)),
                GriddedPerm.single_cell((0,), (2, 2)),
            ]
        ],
        assumptions=[
            TrackingAssumption([GriddedPerm.single_cell((0,), (0, 0))]),
            TrackingAssumption([GriddedPerm.single_cell((0,), (1, 1))]),
            TrackingAssumption([GriddedPerm.single_cell((0,), (2, 2))]),
        ],
    )
    strat = RequirementInsertionStrategy(
        [
            GriddedPerm.single_cell((0,), (1, 1)),
        ]
    )
    rule = strat(parent)
    all_tilings = (rule.comb_class,) + rule.children
    x = sympy.var("x")

    def get_function(t: Tiling):
        i = all_tilings.index(t)
        return sympy.Function(f"F_{i}")(x, *t.extra_parameters)

    eq = sympy.sympify(
        "Eq(F_0(x, k_0, k_1, k_2), F_1(x, k_0, k_2) + F_2(x, k_0, k_1, k_2))"
    )
    assert rule.get_equation(get_function) == eq + 1
    # The equation for the reverse is not implemented so we should get the normal one.
    reverse0 = rule.to_reverse_rule(0)
    assert reverse0.get_equation(get_function) == eq
    reverse1 = rule.to_reverse_rule(1)
    assert reverse1.get_equation(get_function) == eq

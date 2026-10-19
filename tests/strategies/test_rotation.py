import pytest
import sympy

from comb_spec_searcher.exception import StrategyDoesNotApply
from permuta import Av, Perm
from tilings import GriddedPerm, Tiling, TrackingAssumption
from tilings.strategies import RotationalCutFactory, RotationalCutStrategy
from tilings.strategies.rotation import (
    RotationalCutConstructor,
    is_rotationally_stable,
    max_cut,
    min_cut,
    rotation_of,
)
from tilings.tilescope import TileScope, TileScopePack


def basis(string):
    return [Perm.to_standard(map(int, patt)) for patt in string.split("_")]


# closed under rotation of the positions: the lift of 12, [1234], [1324], and
# [1324] with [1234]
POSITIONS = [
    "123_231_312",
    "1234_2341_3412_4123",
    "1324_2413_3241_4132",
    "1234_1324_2341_2413_3241_3412_4123_4132",
]
# closed under rotation of the values only: the inverse of [1423]
VALUES = ["1342_2413_3124_4231"]


def test_is_rotationally_stable():
    assert is_rotationally_stable(basis("123_231_312"))
    assert is_rotationally_stable(basis("1324_2413_3241_4132"))
    assert not is_rotationally_stable(basis("123_3412"))
    assert not is_rotationally_stable(basis(VALUES[0]))


def test_rotation_of():
    for string in POSITIONS:
        assert rotation_of(basis(string)) == "positions"
    for string in VALUES:
        assert rotation_of(basis(string)) == "values"
    assert rotation_of(basis("123_3412")) is None


def test_cuts():
    assert set(min_cut(basis("1234_2341_3412_4123"))) == set(
        basis("123_2341_3412_4123")
    )
    assert set(max_cut(basis("1324_2413_3241_4132"))) == set(
        basis("132_2413_3241_4132")
    )


def test_the_cuts_count_the_class():
    for string in POSITIONS + VALUES:
        whole = Av(basis(string))
        for cut in (min_cut, max_cut):
            part = Av(cut(basis(string)))
            for n in range(1, 9):
                assert whole.count(n) == n * part.count(n - 1), (string, cut, n)


def test_the_rules_pass_their_sanity_checks():
    for string in POSITIONS + VALUES:
        for tiling in (
            Tiling.from_perms(basis(string)),
            Tiling.from_perms(basis(string), [[Perm((0,))]]),
        ):
            rules = [strategy(tiling) for strategy in RotationalCutFactory()(tiling)]
            assert rules, (string, tiling)
            for rule in rules:
                for n in range(8):
                    assert rule.sanity_check(n), (rule, n)


def test_one_or_two_cuts():
    def cuts(string):
        tiling = Tiling.from_perms(basis(string))
        return [strategy.cut for strategy in RotationalCutFactory()(tiling)]

    assert cuts("1324_2413_3241_4132") == ["min", "max"]
    assert cuts("1234_2341_3412_4123") == ["min"]  # the two cuts are the same
    assert [
        strategy.rotation
        for strategy in RotationalCutFactory()(Tiling.from_perms(basis(VALUES[0])))
    ] == ["values", "values"]


def test_the_cut_of_a_cut():
    # the lifts of 12: [1 + 12] = {123, 231, 312}, counted by n, and its lift, the
    # 12 rotations of 1 + 123, 1 + 231 and 1 + 312, counted by n(n - 1)
    lift = basis("123_231_312")
    lift_of_lift = {
        Perm((0,) + tuple(val + 1 for val in patt)).shift_left(k)
        for patt in lift
        for k in range(4)
    }
    assert len(lift_of_lift) == 12
    tiling = Tiling.from_perms(lift_of_lift)
    strategy = next(iter(RotationalCutFactory()(tiling)))
    assert strategy.cut == "min"
    (cut,) = strategy(tiling).children
    assert cut == Tiling.from_perms(lift)
    assert list(RotationalCutFactory()(cut))
    assert [Av(lift_of_lift).count(n) for n in range(7)] == [1, 1, 2, 6, 12, 20, 30]


def test_where_it_does_not_apply():
    not_stable = Tiling.from_perms(basis("123_3412"))
    assert list(RotationalCutFactory()(not_stable)) == []
    with pytest.raises(StrategyDoesNotApply):
        RotationalCutStrategy()(not_stable)
    with pytest.raises(StrategyDoesNotApply):  # a class closed under the values only
        RotationalCutStrategy("min", "positions")(Tiling.from_perms(basis(VALUES[0])))
    stable = basis("123_231_312")
    two_cells = Tiling(
        [GriddedPerm.single_cell(patt, (0, 0)) for patt in stable]
        + [GriddedPerm.single_cell(patt, (1, 0)) for patt in stable]
    )
    pattern_requirement = Tiling.from_perms(stable, [[Perm((0, 1))]])
    tracked = Tiling.from_perms(stable).add_assumption(
        TrackingAssumption([GriddedPerm.point_perm((0, 0))])
    )
    only_the_empty_one = Tiling.from_perms([Perm((0,))])
    for tiling in (two_cells, pattern_requirement, tracked, only_the_empty_one):
        assert list(RotationalCutFactory()(tiling)) == [], tiling


def test_the_maps_are_inverse():
    for string in POSITIONS + VALUES:
        tiling = Tiling.from_perms(basis(string))
        for strategy in RotationalCutFactory()(tiling):
            (cut,) = strategy.decomposition_function(tiling)
            for n in range(6):
                images = []
                for obj in cut.objects_of_size(n):
                    for parent in strategy.backward_map(tiling, (obj,)):
                        assert parent in tiling
                        assert strategy.forward_map(tiling, parent) == (obj,)
                        images.append(parent)
                assert (
                    len(images)
                    == len(set(images))
                    == (n + 1) * len(list(cut.objects_of_size(n)))
                )
            assert strategy.forward_map(tiling, GriddedPerm.empty_perm()) == (None,)


def test_the_equation():
    x = sympy.var("x")
    lhs, rhs = sympy.Function("F")(x), sympy.Function("C")(x)
    for contains_empty, start in ((True, [1]), (False, [0])):
        eq = RotationalCutConstructor(contains_empty).get_equation(lhs, (rhs,))
        # the lift of 12 is counted by n, from its cut, the class of 12
        series = sympy.series(eq.rhs.subs(rhs, 1 / (1 - x)).doit(), x, 0, 6)
        terms = [series.removeO().coeff(x, n) for n in range(6)]
        assert terms == start + [1, 2, 3, 4, 5]


def test_a_rotational_pack():
    pack = TileScopePack.point_placements().make_rotational()
    assert pack.name == "point_placements_rotational"
    with pytest.raises(ValueError):
        pack.make_rotational()
    spec = TileScope("1234_2341_3412_4123", pack).auto_search(max_expansion_time=60)
    assert any(
        isinstance(rule.strategy, RotationalCutStrategy)
        for rule in spec.rules_dict.values()
    )
    try:
        counts = [spec.count_objects_of_size(n) for n in range(9)]
    except NotImplementedError:  # a class verified by its insertion encoding
        spec = spec.expand_verified()
        counts = [spec.count_objects_of_size(n) for n in range(9)]
    assert counts == [1, 1, 2, 6, 20, 65, 198, 560, 1480]

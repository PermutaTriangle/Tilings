import json

import pytest
import sympy

from comb_spec_searcher import Strategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from permuta import Av, Perm
from tilings import GriddedPerm, Tiling, TrackingAssumption
from tilings.hints import hints_for
from tilings.strategies import (
    BasicVerificationStrategy,
    RotationalCutFactory,
    RotationalCutStrategy,
)
from tilings.strategies.rotation import (
    RotationalCutConstructor,
    is_rotationally_stable,
    max_cut,
    min_cut,
    rotation_kind,
)
from tilings.tilescope import TileScope, TileScopePack


def basis(string):
    return [Perm.to_standard(map(int, pattern)) for pattern in string.split("_")]


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


def test_rotation_kind():
    for string in POSITIONS:
        assert rotation_kind(basis(string)) == "positions"
    for string in VALUES:
        assert rotation_kind(basis(string)) == "values"
    assert rotation_kind(basis("123_3412")) is None


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
            for size in range(1, 9):
                assert whole.count(size) == size * part.count(size - 1), (
                    string,
                    cut,
                    size,
                )


def test_the_rules_pass_their_sanity_checks():
    for string in POSITIONS + VALUES:
        for tiling in (
            Tiling.from_perms(basis(string)),
            Tiling.from_perms(basis(string), [[Perm((0,))]]),
        ):
            rules = [strategy(tiling) for strategy in RotationalCutFactory()(tiling)]
            assert rules, (string, tiling)
            for rule in rules:
                for size in range(8):
                    assert rule.sanity_check(size), (rule, size)


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
        Perm((0,) + tuple(value + 1 for value in pattern)).shift_left(shift)
        for pattern in lift
        for shift in range(4)
    }
    assert len(lift_of_lift) == 12
    tiling = Tiling.from_perms(lift_of_lift)
    strategy = next(iter(RotationalCutFactory()(tiling)))
    assert strategy.cut == "min"
    (cut,) = strategy(tiling).children
    assert cut == Tiling.from_perms(lift)
    assert list(RotationalCutFactory()(cut))
    assert [Av(lift_of_lift).count(size) for size in range(7)] == [
        1,
        1,
        2,
        6,
        12,
        20,
        30,
    ]


def test_where_it_does_not_apply():
    not_stable = Tiling.from_perms(basis("123_3412"))
    assert list(RotationalCutFactory()(not_stable)) == []
    with pytest.raises(StrategyDoesNotApply):
        RotationalCutStrategy()(not_stable)
    with pytest.raises(StrategyDoesNotApply):  # a class closed under the values only
        RotationalCutStrategy("min", "positions")(Tiling.from_perms(basis(VALUES[0])))
    stable = basis("123_231_312")
    two_cells = Tiling(
        [GriddedPerm.single_cell(pattern, (0, 0)) for pattern in stable]
        + [GriddedPerm.single_cell(pattern, (1, 0)) for pattern in stable]
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
            for size in range(6):
                images = []
                for gridded_perm in cut.objects_of_size(size):
                    for parent in strategy.backward_map(tiling, (gridded_perm,)):
                        assert parent in tiling
                        assert strategy.forward_map(tiling, parent) == (gridded_perm,)
                        images.append(parent)
                assert (
                    len(images)
                    == len(set(images))
                    == (size + 1) * len(list(cut.objects_of_size(size)))
                )
            assert strategy.forward_map(tiling, GriddedPerm.empty_perm()) == (None,)


def test_the_equation():
    x = sympy.var("x")
    parent_function, cut_function = sympy.Function("F")(x), sympy.Function("C")(x)
    for contains_empty, start in ((True, [1]), (False, [0])):
        equation = RotationalCutConstructor(contains_empty).get_equation(
            parent_function, (cut_function,)
        )
        # the lift of 12 is counted by n, from its cut, the class of 12
        series = sympy.series(
            equation.rhs.subs(cut_function, 1 / (1 - x)).doit(), x, 0, 6
        )
        terms = [series.removeO().coeff(x, size) for size in range(6)]
        assert terms == start + [1, 2, 3, 4, 5]


def test_a_rotational_pack():
    pack = TileScopePack.point_placements().add_rotational_cuts()
    assert pack.name == "point_placements_rotational_cuts"
    with pytest.raises(ValueError):
        pack.add_rotational_cuts()
    spec = TileScope("1234_2341_3412_4123", pack).auto_search(max_expansion_time=60)
    assert any(
        isinstance(rule.strategy, RotationalCutStrategy)
        for rule in spec.rules_dict.values()
    )
    try:
        counts = [spec.count_objects_of_size(size) for size in range(9)]
    except NotImplementedError:  # a class verified by its insertion encoding
        spec = spec.expand_verified()
        counts = [spec.count_objects_of_size(size) for size in range(9)]
    assert counts == [1, 1, 2, 6, 20, 65, 198, 560, 1480]


@pytest.mark.parametrize("string", ["123_231_312", "1234_2341_3412_4123"])
def test_a_bijection_through_a_cut_is_one_to_one(string):
    """A specification that uses a rotational cut, mapped by a bijection to itself:
    every object goes to itself, so the n rotations of a permutation stay apart."""
    pack = (
        TileScopePack.point_placements()
        .add_rotational_cuts()
        .add_verification(BasicVerificationStrategy(), replace=True)
    )
    spec = TileScope(string, pack).auto_search(max_expansion_time=60)
    assert any("rotation" in rule.formal_step for rule in spec.rules_dict.values())
    bijection = spec.get_bijection_to(spec)
    assert bijection is not None
    for size in range(1, 6):
        objects = list(spec.generate_objects_of_size(size))
        assert [bijection.map(obj) for obj in objects] == objects


def flags(strategy):
    return (
        strategy.ignore_parent,
        strategy.inferrable,
        strategy.possibly_empty,
        strategy.workable,
    )


def test_the_strategy_and_the_constructor_state_what_they_are():
    tiling = Tiling.from_perms(basis("123_231_312"))
    not_stable = Tiling.from_perms(basis("123_3412"))
    # the strategies the factory makes: the flags that decide how a search treats the
    # rule (a cut is never empty, is not a bijection, and has no reverse)
    for strategy in RotationalCutFactory()(tiling):
        assert flags(strategy) == (False, True, False, True)
        assert not strategy.can_be_equivalent()
        assert not strategy.is_two_way(tiling)
        assert not strategy.is_reversible(tiling)
        assert strategy.shifts(tiling) == (1,)
        rule = strategy(tiling)
        assert (rule.is_two_way(), rule.is_reversible(), rule.shifts()) == (
            False,
            False,
            (1,),
        )
    # flags that are set are kept, by the JSON encoding as well
    flagged = RotationalCutStrategy(
        "max",
        "values",
        ignore_parent=True,
        inferrable=False,
        possibly_empty=True,
        workable=False,
    )
    assert flags(flagged) == (True, False, True, False)
    decoded = Strategy.from_dict(json.loads(json.dumps(flagged.to_jsonable())))
    assert flags(decoded) == (True, False, True, False)
    assert (decoded.cut, decoded.rotation) == ("max", "values")
    assert decoded.__dict__ == flagged.__dict__
    # bad arguments, and a tiling it does not apply to
    with pytest.raises(ValueError):
        RotationalCutStrategy("middle")
    with pytest.raises(ValueError):
        RotationalCutStrategy("min", "diagonal")
    with pytest.raises(StrategyDoesNotApply):
        RotationalCutStrategy().constructor(not_stable)
    # the constructor: the parent has the empty object if it is the whole class
    whole, nonempty = RotationalCutConstructor(True), RotationalCutConstructor(False)
    assert not whole.can_be_equivalent()
    assert whole.reliance_profile(0) == ({"n": ()},)
    assert whole.reliance_profile(5) == ({"n": (4,)},)
    assert whole.equiv(RotationalCutConstructor(True)) == (True, None)
    assert whole.equiv(nonempty) == (False, None)
    assert not whole.equiv(object())[0]
    assert str(whole) == "n times the cut at n - 1"
    assert str(RotationalCutFactory()) == "rotational cuts"


def test_rotation_kind_of_a_basis_that_is_not_minimal():
    # Av(123, 231, 312, 1234) is Av(123, 231, 312), closed under rotation: 1234 is
    # redundant, as it contains 123, and its rotations are not in the list
    minimal = basis("123_231_312")
    redundant = basis("123_231_312_1234")
    assert Av(redundant).count(5) == Av(minimal).count(5)
    assert rotation_kind(minimal) == "positions"
    assert rotation_kind(redundant) == "positions"
    # hints, which minimalizes first, gets it right
    assert [hint.name for hint in hints_for(redundant)] == ["rotationally stable"]


@pytest.mark.parametrize("string", ["12_21", "1234_2341_3412_4123"])
def test_the_edge_classes_pass_their_sanity_checks(string):
    # Av(12, 21) = {empty, 1}: elements of length 2 in the basis, and the min cut,
    # Av(1, 21), is only the empty permutation. Av(1234, 2341, 3412, 4123) is closed
    # under both rotations: the strategy works with either.
    classes = basis(string)
    for tiling in (
        Tiling.from_perms(classes),
        Tiling.from_perms(classes, [[Perm((0,))]]),
    ):
        for cut in ("min", "max"):
            for rotation in ("positions", "values"):
                rule = RotationalCutStrategy(cut, rotation)(tiling)
                for size in range(7):
                    assert rule.sanity_check(size), (string, cut, rotation, size)
    if string == "12_21":
        assert [Av(classes).count(size) for size in range(5)] == [1, 1, 0, 0, 0]
        tiling = Tiling.from_perms(classes)
        assert [strategy.cut for strategy in RotationalCutFactory()(tiling)] == ["min"]


def test_a_cut_of_a_cut_is_cut_again_down_to_av_12():
    lift = basis("123_231_312")
    lift_of_lift = {
        Perm((0,) + tuple(value + 1 for value in pattern)).shift_left(shift)
        for pattern in lift
        for shift in range(4)
    }
    tiling = Tiling.from_perms(lift_of_lift)
    chain = [tiling]
    while True:
        strategies = list(RotationalCutFactory()(chain[-1]))
        if not strategies:
            break
        for strategy in strategies:
            rule = strategy(chain[-1])
            for size in range(7):
                assert rule.sanity_check(size)
        chain.append(strategies[0](chain[-1]).children[0])
    assert chain == [tiling, Tiling.from_perms(lift), Tiling.from_perms(basis("12"))]


def test_the_equation_for_a_cut_that_is_not_a_geometric_series():
    # x (x C)' is not x C^2 in general: for C = 1 / (1 - x)^2, the cut with m + 1
    # permutations of length m, the class has n * n of length n
    x = sympy.var("x")
    parent_function, cut_function = sympy.Function("F")(x), sympy.Function("C")(x)
    for contains_empty, start in ((True, [1]), (False, [0])):
        equation = RotationalCutConstructor(contains_empty).get_equation(
            parent_function, (cut_function,)
        )
        series = sympy.series(
            equation.rhs.subs(cut_function, 1 / (1 - x) ** 2).doit(), x, 0, 6
        )
        terms = [series.removeO().coeff(x, size) for size in range(6)]
        assert terms == start + [1, 4, 9, 16, 25]

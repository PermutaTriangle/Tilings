import argparse
import itertools
import json

import pytest
import sympy

from comb_spec_searcher.strategies.strategy import AbstractStrategy
from permuta import Av, Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST
from permuta.perm_sets.basis import Basis
from tilings import GriddedPerm, Tiling, cli
from tilings import strategies as strat
from tilings.cli import build_pack, parser
from tilings.hints import (
    OnePointExtension,
    extension_placement_arguments,
    find_one_point_extension,
    find_one_point_extension_chain,
    hints_for,
    one_point_extensions,
)
from tilings.strategies.requirement_placement import RequirementPlacementStrategy
from tilings.strategy_pack import TileScopePack
from tilings.tilescope import TileScope


def basis(string):
    return [Perm.to_standard(map(int, pattern)) for pattern in string.split("_")]


def test_a_class_closed_under_rotation():
    (hint,) = hints_for(basis("1324_2413_3241_4132"))
    assert hint.name == "rotationally stable"
    assert "closed under rotation of its positions" in hint.message
    assert "each of its cuts, Av(102,3021) and Av(021,2130)," in hint.message
    assert "Search for either instead" in hint.message
    assert hint.strategies == (strat.RotationalCutFactory(),)
    assert hint.followed_by(TileScopePack.point_placements().add_rotational_cuts())
    assert not hint.followed_by(TileScopePack.point_placements())


def test_one_cut_and_the_values():
    (hint,) = hints_for(basis("1234_2341_3412_4123"))  # the min and the max cut agree
    assert "as its cut, Av(012,2301), has of length n - 1" in hint.message
    assert "Search for Av(012,2301) instead" in hint.message
    (hint,) = hints_for(basis("1342_2413_3124_4231"))
    assert "closed under rotation of its values" in hint.message
    assert "a rotation of the values raises each by one" in hint.message


def test_the_cut_cut_again():
    """The lift of the lift of 12: its cut, the lift of 12, is closed under rotation
    too, and its cut is Av(12), the class to search for instead."""
    lift = basis("123_231_312")
    lift_of_lift = {
        Perm((0,) + tuple(value + 1 for value in pattern)).shift_left(shift)
        for pattern in lift
        for shift in range(4)
    }
    # it is also every one-point extension of the lift of 12 by a new minimum
    hint, extension_hint = hints_for(lift_of_lift)
    assert extension_hint.name == "one-point extension"
    assert "as its cut, Av(012,120,201), has of length n - 1" in hint.message
    assert (
        "That cut is closed under rotation too, and its cut is Av(01)" in hint.message
    )
    assert "n (n - 1) times as many permutations of length n as Av(01)" in hint.message
    assert "has of length n - 2. Search for Av(01) instead" in hint.message


def test_no_hint():
    for string in ("123_3412", "1", "1234"):
        assert hints_for(basis(string)) == [], string
    assert hints_for([]) == []


def test_the_flag():
    args = parser.parse_args(["spec", "123_231_312", "point_placements", "-r"])
    pack = build_pack(args)
    assert pack.name == "point_placements_rotational_cuts"
    assert strat.RotationalCutFactory() in pack
    args = parser.parse_args(["spec", "123_231_312", "point_placements"])
    assert strat.RotationalCutFactory() not in build_pack(args)
    # a namespace of the caller's own, made before the flag existed, still works
    args = argparse.Namespace(
        strategy_pack="point_placements",
        length=None,
        basis="123_231_312",
        fusion=False,
        symmetries=False,
        elementary=False,
    )
    assert strat.RotationalCutFactory() not in build_pack(args)


def logged(monkeypatch, argv):
    """Run 'tilescope spec' with the arguments, and return the exit code and what was
    logged at the info level."""
    messages = []
    monkeypatch.setattr(
        cli.logger,
        "info",
        lambda message, *args: messages.append(message % args if args else message),
    )
    return cli.search_spec(cli.parser.parse_args(argv)), messages


def test_spec_tells_of_the_hint_unless_the_pack_follows_it(monkeypatch):
    code, messages = logged(monkeypatch, ["spec", "123_231_312", "point_placements"])
    assert code == 0
    (hint,) = [message for message in messages if message.startswith("Hint: ")]
    assert "closed under rotation of its positions" in hint
    assert "--rotational-cuts" in hint
    # with the flag the pack follows the hint, and the search still finds the answer;
    # it has no generating function to show if its specification has a cut, which
    # depends on when the search looks
    code, messages = logged(
        monkeypatch, ["spec", "123_231_312", "point_placements", "-r"]
    )
    assert code == 0
    assert not [message for message in messages if message.startswith("Hint")]
    assert any(message.startswith("The generating function") for message in messages)
    # no hint for a class without one
    code, messages = logged(monkeypatch, ["spec", "12", "point_placements"])
    assert code == 0
    assert not [message for message in messages if message.startswith("Hint")]


def test_spec_says_when_it_cannot_compute_the_generating_function(monkeypatch):
    """comb_spec_searcher cannot solve a rotational cut's equation, which has a
    derivative: the command ends normally, and says so."""
    code, messages = logged(
        monkeypatch, ["spec", "1234_2341_3412_4123", "point_placements", "-r"]
    )
    assert code == 0
    assert any(
        message.startswith("The generating function cannot be computed")
        for message in messages
    )


DIRECTIONS = (DIR_NORTH, DIR_SOUTH, DIR_WEST, DIR_EAST)


def without_point(perm, direction):
    """The permutation without its point furthest in the direction."""
    entries = list(perm)
    if direction == DIR_NORTH:
        entries.remove(len(perm) - 1)
    elif direction == DIR_SOUTH:
        entries.remove(0)
    elif direction == DIR_WEST:
        entries = entries[1:]
    else:
        entries = entries[:-1]
    return Perm.to_standard(entries)


def extended(string, direction):
    """Every one-point extension in the direction of the patterns of the basis."""
    return sorted(
        set().union(
            *(one_point_extensions(pattern, direction) for pattern in basis(string))
        )
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_one_point_extensions(direction):
    """The permutations one point longer than the pattern that give it when their
    point furthest in the direction is taken out."""
    for pattern in (Perm(), Perm((0,)), Perm((0, 1, 2)), Perm((1, 3, 0, 2))):
        expected = {
            perm
            for perm in Perm.of_length(len(pattern) + 1)
            if without_point(perm, direction) == pattern
        }
        assert one_point_extensions(pattern, direction) == expected
    with pytest.raises(ValueError):
        one_point_extensions(Perm((0, 1)), 4)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("string", ["123", "132", "1342", "2413_3142", "123_3412"])
def test_one_point_extension_found_and_counted(string, direction):
    """The basis of every one-point extension is found to be one, in its direction,
    and its class has n times as many permutations of length n as the class of the
    basis extended has of length n - 1."""
    patterns = extended(string, direction)
    assert find_one_point_extension(patterns) == (
        direction,
        tuple(sorted(basis(string))),
    )
    small, large = Av(Basis(*basis(string))), Av(Basis(*patterns))
    assert [large.count(n) for n in range(1, 8)] == [
        n * small.count(n - 1) for n in range(1, 8)
    ]


def test_a_basis_not_minimal():
    """A pattern containing one of the basis is left out first, as Av ignores it."""
    patterns = extended("123", DIR_NORTH) + [Perm((0, 1, 2, 3, 4))]
    assert find_one_point_extension(patterns) == (DIR_NORTH, (Perm((0, 1, 2)),))


def test_not_a_one_point_extension():
    assert find_one_point_extension(basis("1234_1243_1423")) is None  # one is missing
    assert find_one_point_extension(basis("1234")) is None
    # it extends patterns of length 1
    assert find_one_point_extension(basis("12_21")) is None
    assert find_one_point_extension([]) is None


def test_the_extension_hint():
    (hint,) = hints_for(extended("123", DIR_NORTH))
    assert hint.name == "one-point extension"
    assert (
        "adding a new maximum to each pattern of the basis of Av(012)" in hint.message
    )
    assert "n times as many permutations of length n as that class" in hint.message
    assert "partial placement of the topmost point" in hint.message
    assert "Search for Av(012) instead" in hint.message
    assert "add_extension_placement((DIR_NORTH,), 3)" in hint.message
    placement, inferral = hint.strategies
    assert isinstance(placement, strat.RequirementPlacementFactory)
    assert placement.partial and placement.dirs == (DIR_NORTH,)
    assert inferral.maxlen == 3
    assert hint.followed_by(
        TileScopePack.point_placements().add_extension_placement((DIR_NORTH,), 3)
    )
    assert not hint.followed_by(TileScopePack.point_placements())
    # a pack with one of the two strategies does not follow it
    assert not hint.followed_by(TileScopePack.only_root_placements())
    (hint,) = hints_for(extended("1342", DIR_WEST))
    assert "adding a new leftmost point" in hint.message
    assert "add_extension_placement((DIR_WEST,), 4)" in hint.message


def test_both_hints_for():
    """Every permutation of length 3: closed under rotation, and every one-point
    extension of Av(01, 10)."""
    names = [hint.name for hint in hints_for(basis("123_132_213_231_312_321"))]
    assert names == ["rotationally stable", "one-point extension"]


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_the_extension_placement_finds_a_specification(direction):
    """With the hint's partial placement and obstruction inferral, point placements
    find a specification of every one-point extension of Av(012), in each direction,
    whose rules pass their sanity check, the partial placement in that direction
    among them. Point placements alone find none in a minute for the maximum's."""
    root = Tiling(
        [
            GriddedPerm.single_cell(pattern, (0, 0))
            for pattern in extended("123", direction)
        ]
    )
    pack = TileScopePack.point_placements().add_extension_placement((direction,), 3)
    spec = TileScope(root, pack).auto_search(max_expansion_time=30)  # under a second
    placements = [
        rule.strategy
        for rule in spec.rules_dict.values()
        if isinstance(rule.strategy, RequirementPlacementStrategy)
    ]
    assert [
        (placement.direction, placement.own_row and placement.own_col)
        for placement in placements
    ] == [(direction, False)]
    assert spec.sanity_check(6)


def test_the_extension_flag():
    args = parser.parse_args(["spec", "1234_1243_1423_4123", "point_placements", "-x"])
    pack = build_pack(args)
    assert pack.name == "point_placements_extension_placement"
    (placement,) = pack.expansion_strats[-1]
    assert isinstance(placement, strat.RequirementPlacementFactory)
    assert placement.partial and placement.dirs == (DIR_NORTH,)
    (inferral,) = [  # its subclasses, as ObstructionTransitivityFactory, left out
        strategy
        for strategy in pack.inferral_strats
        if type(strategy) is strat.ObstructionInferralFactory
    ]
    assert inferral.maxlen == 3
    for not_an_extension_or_a_pack_with_a_placement in (
        ["spec", "1234", "point_placements", "-x"],
        ["spec", "1234_1243_1423_4123", "only_root_placements", "-x"],
    ):
        args = parser.parse_args(not_an_extension_or_a_pack_with_a_placement)
        with pytest.raises(SystemExit):
            build_pack(args)


@pytest.mark.parametrize(
    "second, directions",
    [(DIR_NORTH, (DIR_NORTH,)), (DIR_SOUTH, (DIR_NORTH, DIR_SOUTH))],
    ids=["a maximum twice", "a maximum, then a minimum"],
)
def test_an_extension_of_an_extension(second, directions):
    """Every one-point extension of the extensions of 123 by a new maximum: the
    hint reduces it twice, to Av(012), the class to search for instead, and the
    pack places in each direction of the chain, with obstruction inferral to the
    length of the first reduction's patterns."""
    patterns = sorted(
        set().union(
            *(
                one_point_extensions(pattern, second)
                for pattern in extended("123", DIR_NORTH)
            )
        )
    )
    chain = find_one_point_extension_chain(patterns)
    assert tuple(direction for direction, _ in chain) == directions + (
        (DIR_NORTH,) if second == DIR_NORTH else ()
    )
    assert chain[-1][1] == (Perm((0, 1, 2)),)
    (hint,) = hints_for(patterns)
    assert (
        f"and taking out one more point, {TAKEN_OUT[directions[-1]]}, leaves a "
        "permutation of Av(012)" in hint.message
    )
    assert "n (n - 1) times as many permutations of length n as Av(012)" in hint.message
    assert "Search for Av(012) instead" in hint.message
    placement, inferral = hint.strategies
    assert placement.dirs == directions and inferral.maxlen == 4
    args = parser.parse_args(
        ["spec", "_".join(map(str, patterns)), "point_placements", "-x"]
    )
    assert build_pack(args).expansion_strats[-1][0].dirs == directions


def extended_by(patterns, direction):
    """Every permutation one point longer than a pattern that gives the pattern when
    its point furthest in the direction is taken out: found with without_point, not
    with one_point_extensions."""
    return sorted(
        {
            perm
            for pattern in patterns
            for perm in Perm.of_length(len(pattern) + 1)
            if without_point(perm, direction) == pattern
        }
    )


def extended_in(string, *directions):
    """The basis of the class that extends the basis, in the directions one after the
    other."""
    patterns = basis(string)
    for direction in directions:
        patterns = extended_by(patterns, direction)
    return patterns


def flag_args(patterns, pack="point_placements", *flags):
    """The arguments of 'tilescope spec' with the flag -x, for the basis (0-based)."""
    string = "_".join(map(str, patterns))
    return parser.parse_args(["spec", string, pack, "-x", *flags])


def extension_strategies(pack):
    """The partial placement and the obstruction inferral that add_extension_placement
    adds to the pack."""
    (placement,) = pack.expansion_strats[-1]
    (inferral,) = [
        strategy
        for strategy in pack.inferral_strats
        if type(strategy) is strat.ObstructionInferralFactory
    ]
    return placement, inferral


def counts(patterns, length=8):
    return [Av(Basis(*patterns)).count(n) for n in range(length)]


HINT_WORDS = {
    DIR_NORTH: ("a new maximum", "maximum, taken out", "of the topmost point", "NORTH"),
    DIR_SOUTH: (
        "a new minimum",
        "minimum, taken out",
        "of the bottommost point",
        "SOUTH",
    ),
    DIR_WEST: (
        "a new leftmost point",
        "leftmost point, taken out",
        "of the leftmost point",
        "WEST",
    ),
    DIR_EAST: (
        "a new rightmost point",
        "rightmost point, taken out",
        "of the rightmost point",
        "EAST",
    ),
}

# the point a step after the first takes out, in the hint's words
TAKEN_OUT = {
    DIR_NORTH: "the maximum",
    DIR_SOUTH: "the minimum",
    DIR_WEST: "the leftmost point",
    DIR_EAST: "the rightmost point",
}


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_the_hint_and_the_flag_in_each_direction(direction):
    """One step: the hint names the direction's point in each of its phrases, says
    nothing of reducing again, and the flag asks for the same strategies."""
    adding, taken_out, placing, name = HINT_WORDS[direction]
    patterns = extended_in("123", direction)
    (hint,) = hints_for(patterns)
    message = hint.message
    assert f"adding {adding} to each pattern of the basis of Av(012)" in message
    assert f"whose {taken_out}, leaves a permutation of that class" in message
    assert f"placement {placing}, with obstruction inferral to length 3" in message
    assert f"add_extension_placement((DIR_{name},), 3)" in message
    assert "such an extension too" not in message
    assert "has of length n - 1, for n >= 1. Search for Av(012) instead" in message
    assert "F = 1 + x (x G)'" in message
    assert "Or add to the pack" in message
    assert message.endswith(f"--extension-placement). {PLACEMENT_NEEDS}")
    placement, inferral = hint.strategies
    assert placement.partial and placement.dirs == (direction,)
    assert inferral.maxlen == 3
    pack = build_pack(flag_args(patterns))
    placement, inferral = extension_strategies(pack)
    assert placement.partial and placement.dirs == (direction,)
    assert inferral.maxlen == 3
    assert hint.followed_by(pack)


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("string", ["12", "21"])
def test_a_basis_of_one_pattern_of_length_two(string, direction):
    """The shortest basis B the hint takes: B' has patterns of length 3, and the
    class has n permutations of length n."""
    patterns = extended_in(string, direction)
    assert find_one_point_extension(patterns) == (direction, tuple(basis(string)))
    assert find_one_point_extension_chain(patterns) == [
        (direction, tuple(basis(string)))
    ]
    assert counts(patterns) == [1] + list(range(1, 8))


def test_a_class_that_is_an_extension_in_every_direction():
    """Every permutation of length 3 is one in all four: north is the first."""
    patterns = extended_in("12_21", DIR_NORTH)
    for direction in DIRECTIONS:
        assert extended_in("12_21", direction) == patterns
    assert find_one_point_extension(patterns) == (DIR_NORTH, tuple(basis("12_21")))
    rotation_hint, hint = hints_for(patterns)
    assert rotation_hint.name == "rotationally stable"
    assert "adding a new maximum" in hint.message
    assert hint.strategies[0].dirs == (DIR_NORTH,)
    placement, _ = extension_strategies(build_pack(flag_args(patterns)))
    assert placement.dirs == (DIR_NORTH,)


# For the class made by extending 123 in the two directions, one after the other: the
# directions of the steps find_one_point_extension_chain finds, the outermost first,
# and the direction in which 123 was extended to give the class that the first step
# leaves.
CHAINS = [
    ((DIR_NORTH, DIR_NORTH), (DIR_NORTH, DIR_NORTH), DIR_NORTH),
    ((DIR_NORTH, DIR_SOUTH), (DIR_NORTH, DIR_SOUTH), DIR_SOUTH),  # a tie: north first
    ((DIR_SOUTH, DIR_NORTH), (DIR_NORTH, DIR_SOUTH), DIR_SOUTH),
    ((DIR_NORTH, DIR_WEST), (DIR_WEST, DIR_NORTH), DIR_NORTH),
    ((DIR_WEST, DIR_NORTH), (DIR_NORTH, DIR_WEST), DIR_WEST),
    ((DIR_WEST, DIR_SOUTH), (DIR_SOUTH, DIR_WEST), DIR_WEST),
    ((DIR_EAST, DIR_WEST), (DIR_WEST, DIR_EAST), DIR_EAST),  # a tie: west first
    ((DIR_NORTH, DIR_EAST), (DIR_EAST, DIR_NORTH), DIR_NORTH),
]


@pytest.mark.parametrize("extending, steps, inner", CHAINS)
def test_two_steps_in_every_order_of_directions(extending, steps, inner):
    """The chain, the hint and the flag name the directions in the order of the steps,
    each once; the class has n (n - 1) times as many permutations of length n as
    Av(012) has of length n - 2."""
    patterns = extended_in("123", *extending)
    chain = find_one_point_extension_chain(patterns)
    assert tuple(direction for direction, _ in chain) == steps
    assert chain[-1][1] == (Perm((0, 1, 2)),)
    small = Av(Basis(*basis("123")))
    assert counts(patterns)[2:] == [
        n * (n - 1) * small.count(n - 2) for n in range(2, 8)
    ]
    (hint,) = hints_for(patterns)
    first = Av(Basis(*extended_in("123", inner)))
    assert f"to each pattern of the basis of {first}," in hint.message
    assert (
        "That class is such an extension too, and taking out one more point, "
        f"{TAKEN_OUT[steps[1]]}, leaves a permutation of Av(012)" in hint.message
    )
    assert "n (n - 1) times as many permutations of length n as Av(012)" in hint.message
    assert "has of length n - 2, for n >= 2. Search for Av(012) instead" in hint.message
    assert "F = 1 + x (x G)', applied twice." in hint.message
    if len(set(steps)) == 1:
        placed = HINT_WORDS[steps[0]][2]
        assert (
            f"a partial placement {placed}, with obstruction inferral" in hint.message
        )
    else:
        first_placed, second_placed = (HINT_WORDS[step][2] for step in steps)
        assert (
            f"partial placements {first_placed} and the "
            f"{second_placed.removeprefix('of the ')}, with" in hint.message
        )
    names = ", ".join(
        f"DIR_{HINT_WORDS[direction][3]}" for direction in dict.fromkeys(steps)
    )
    names += "," if len(set(steps)) == 1 else ""
    assert f"add_extension_placement(({names}), 4)" in hint.message
    placement, inferral = hint.strategies
    assert placement.dirs == tuple(dict.fromkeys(steps)) and inferral.maxlen == 4
    placement, inferral = extension_strategies(build_pack(flag_args(patterns)))
    assert placement.dirs == tuple(dict.fromkeys(steps))
    assert inferral.maxlen == 4  # the length of the first step's basis, not the last's


@pytest.mark.parametrize(
    "extending, steps",
    [
        ((DIR_NORTH, DIR_NORTH, DIR_NORTH), (DIR_NORTH, DIR_NORTH, DIR_NORTH)),
        ((DIR_NORTH, DIR_WEST, DIR_SOUTH), (DIR_SOUTH, DIR_WEST, DIR_NORTH)),
    ],
)
def test_three_steps(extending, steps):
    """Three steps: the sentence says 'taking out 2 more points', has n (n - 1) (n - 2),
    each step turns Av(012)'s series by the hint's F = 1 + x (x G)', and the flag
    and the hint ask for the directions in the steps' order, with length 5."""
    patterns = extended_in("123", *extending)
    assert (
        tuple(direction for direction, _ in find_one_point_extension_chain(patterns))
        == steps
    )
    (hint,) = hints_for(patterns)
    assert "and taking out 2 more points, the " in hint.message
    assert (
        "leaves a permutation of Av(012): the class has n (n - 1) (n - 2) times"
        in hint.message
    )
    assert "times as many permutations of length n as Av(012) has" in hint.message
    assert "of length n - 3, for n >= 3. Search for Av(012) instead" in hint.message
    assert "F = 1 + x (x G)', applied 3 times." in hint.message
    if len(set(steps)) == 3:
        assert (
            "partial placements of the bottommost point, the leftmost point and the "
            "topmost point, with" in hint.message
        )
    placement, inferral = hint.strategies
    assert placement.dirs == tuple(dict.fromkeys(steps)) and inferral.maxlen == 5
    placement, inferral = extension_strategies(build_pack(flag_args(patterns)))
    assert placement.dirs == tuple(dict.fromkeys(steps)) and inferral.maxlen == 5
    x = sympy.Symbol("x")
    series = sum(Av(Basis(*basis("123"))).count(n) * x**n for n in range(8))
    for _ in range(3):
        series = sympy.expand(1 + x * sympy.diff(x * series, x))
    assert [series.coeff(x, n) for n in range(7)] == counts(patterns, 7)


def test_a_basis_of_patterns_of_different_lengths():
    """B = {123, 3412}: obstruction inferral to the length of B's longest pattern."""
    patterns = extended_in("123_3412", DIR_NORTH)
    assert sorted({len(pattern) for pattern in patterns}) == [4, 5]
    (hint,) = hints_for(patterns)
    assert "add_extension_placement((DIR_NORTH,), 4)" in hint.message
    assert hint.strategies[1].maxlen == 4
    assert extension_strategies(build_pack(flag_args(patterns)))[1].maxlen == 4


def test_not_quite_a_one_point_extension():
    extensions = extended_in("123", DIR_NORTH)
    assert find_one_point_extension(extensions) == (DIR_NORTH, (Perm((0, 1, 2)),))
    assert (
        find_one_point_extension(extensions + [Perm((1, 0, 3, 2))]) is None
    )  # a pattern too many
    assert find_one_point_extension(extensions[1:]) is None  # or too few
    mixed = extensions[:3] + extended_in("123", DIR_SOUTH)[:1]  # of two directions
    assert find_one_point_extension(mixed) is None
    both = extensions + extended_in("123", DIR_SOUTH)
    assert find_one_point_extension(both) is None
    assert find_one_point_extension_chain(both) == []
    assert hints_for(both) == []
    assert hints_for(extensions + [Perm((1, 0, 3, 2))]) == []


def test_the_empty_and_the_short_and_the_repeated():
    assert find_one_point_extension([Perm()]) is None  # the empty class
    assert find_one_point_extension([Perm((0,))]) is None
    assert find_one_point_extension_chain([Perm()]) == []
    assert hints_for([Perm()]) == []
    extensions = extended_in("123", DIR_NORTH)
    expected = (DIR_NORTH, (Perm((0, 1, 2)),))
    assert find_one_point_extension(extensions + extensions) == expected  # repeats
    assert find_one_point_extension(reversed(extensions)) == expected  # any order
    assert find_one_point_extension(iter(extensions)) == expected  # once through
    assert find_one_point_extension(extensions + [Perm((0, 1, 2, 3, 4))]) == expected
    # with 012, the basis is {012}
    assert find_one_point_extension(extensions + [Perm((0, 1, 2))]) is None
    assert find_one_point_extension_chain(extensions) == [expected]


def test_the_extension_hint_formula():
    """F = 1 + x (x G)', the hint's, takes the series of Av(012) to the class of its
    one-point extensions in every direction, from Permuta's counts."""
    x = sympy.Symbol("x")
    series = sum(Av(Basis(*basis("123"))).count(n) * x**n for n in range(8))
    transformed = sympy.expand(1 + x * sympy.diff(x * series, x))
    for direction in DIRECTIONS:
        patterns = extended_in("123", direction)
        assert [transformed.coeff(x, n) for n in range(8)] == counts(patterns)


@pytest.mark.timeout(60)  # the command's search has no limit of its own
@pytest.mark.parametrize("direction", DIRECTIONS)
def test_the_flag_finds_the_generating_function(monkeypatch, direction):
    """The command with -x finds a specification of the one-point extensions of
    Av(012) in each direction, whose generating function has Permuta's counts, and
    does not tell of the hint, as its pack follows it."""
    patterns = extended_in("123", direction)
    string = "_".join(map(str, patterns))
    code, messages = logged(monkeypatch, ["spec", string, "point_placements", "-x"])
    assert code == 0
    assert not [message for message in messages if message.startswith("Hint")]
    (message,) = [
        message
        for message in messages
        if message.startswith("The generating function is ")
    ]
    x = sympy.Symbol("x")
    series = sympy.series(sympy.sympify(message.split(" is ", 1)[1]), x, 0, 8).removeO()
    assert [series.coeff(x, n) for n in range(8)] == counts(patterns)


@pytest.mark.parametrize(
    "extending",
    [(DIR_NORTH, DIR_NORTH), (DIR_NORTH, DIR_WEST), (DIR_WEST, DIR_NORTH)],
    ids=["north twice", "north, then west", "west, then north"],
)
def test_the_flag_finds_a_specification_for_two_steps(extending):
    """A chain of two steps, in the one direction and in two: point placements with
    the flag's partial placements find a specification whose rules pass their
    sanity check, and whose partial placements are in the chain's directions."""
    patterns = extended_in("123", *extending)
    pack = build_pack(flag_args(patterns))
    root = Tiling([GriddedPerm.single_cell(pattern, (0, 0)) for pattern in patterns])
    spec = TileScope(root, pack).auto_search(max_expansion_time=30)  # under a second
    directions = {
        rule.strategy.direction
        for rule in spec.rules_dict.values()
        if isinstance(rule.strategy, RequirementPlacementStrategy)
    }
    assert directions and directions <= set(extending)
    assert spec.sanity_check(5)


def test_spec_tells_of_the_extension_hint_unless_the_pack_follows_it(monkeypatch):
    """Without the flag the command logs the hint (its search would not end in a
    minute, so none is run); with it, not."""

    class Stop(Exception):
        pass

    def refuse(*args):
        raise Stop

    messages = []
    monkeypatch.setattr(
        cli.logger,
        "info",
        lambda message, *args: messages.append(message % args if args else message),
    )
    monkeypatch.setattr(cli, "TileScope", refuse)
    patterns = extended_in("123", DIR_NORTH)
    string = "_".join(map(str, patterns))
    with pytest.raises(Stop):
        cli.search_spec(parser.parse_args(["spec", string, "point_placements"]))
    (hint,) = [message for message in messages if message.startswith("Hint: ")]
    assert "adding a new maximum" in hint and "--extension-placement" in hint
    messages.clear()
    with pytest.raises(Stop):
        cli.search_spec(flag_args(patterns))
    assert not [message for message in messages if message.startswith("Hint")]


FLAG_WORDS = {
    "-s": "symmetries",
    "-f": "fusion",
    "-e": "elementary",
    "-r": "rotational_cuts",
}


@pytest.mark.parametrize(
    "name", [name for name in cli.BASE_PACK if name != "only_root_placements"]
)
@pytest.mark.parametrize("flags", [[], ["-s"], ["-f"], ["-e"], ["-r"]])
def test_the_flag_with_each_pack(name, flags):
    """Every pack takes the strategies, with each of the other flags, except
    only_root_placements, which has a requirement placement already (see the next
    test); regular_insertion_encoding asks for a basis it can encode."""
    patterns = extended_in("123", DIR_NORTH)
    if name == "regular_insertion_encoding":
        patterns = extended_in("12_21", DIR_NORTH)
    pack = build_pack(flag_args(patterns, name, *flags))
    assert pack.name.endswith("extension_placement")
    for flag in flags:  # the flags are all applied, the extension placement last
        assert FLAG_WORDS[flag] in pack.name
    placement, inferral = extension_strategies(pack)
    assert placement.dirs == (DIR_NORTH,)


NOT_AN_EXTENSION = (
    "is not every one-point extension",
    "--extension-placement does not apply",
)
CANNOT_TAKE_IT = (
    "--extension-placement does not go with this pack",
    "has a requirement placement or obstruction inferral already",
)


@pytest.mark.parametrize(
    "argv, said",
    [
        (["1234", "point_placements"], NOT_AN_EXTENSION),
        (["1234_1243_1423", "point_placements"], NOT_AN_EXTENSION),
        (["12", "point_placements"], NOT_AN_EXTENSION),
        (["", "point_placements"], NOT_AN_EXTENSION),
        (["1234_1243_1423_4123", "only_root_placements"], CANNOT_TAKE_IT),
        (["1234_1243_1423_4123", "only_root_placements", "-s"], CANNOT_TAKE_IT),
        (["1234_1243_1423_4123", "only_root_placements", "-r"], CANNOT_TAKE_IT),
    ],
)
def test_the_flag_refuses_with_a_message(capsys, argv, said):
    """A basis that is no one-point extension, or a pack that has a requirement
    placement already, is a parser error (exit code 2) that says which."""
    with pytest.raises(SystemExit) as error:
        build_pack(parser.parse_args(["spec", *argv, "-x"]))
    assert error.value.code == 2
    message = capsys.readouterr().err
    assert all(phrase in message for phrase in said)


def test_the_flag_reads_the_basis_as_the_command_does():
    """Zero- or one-based, with a pattern that is not minimal, or twice, and the
    flag's long form, as in the README."""
    for string in (
        "0123_0132_0312_3012",
        "1234_1243_1423_4123",
        "4123_1423_1243_1234_12345_1234",
    ):
        args = parser.parse_args(
            ["spec", string, "point_placements", "--extension-placement"]
        )
        placement, inferral = extension_strategies(build_pack(args))
        assert placement.dirs == (DIR_NORTH,) and inferral.maxlen == 3, string


def test_the_pack_method():
    pack = TileScopePack.point_placements().add_extension_placement(
        (direction for direction in (DIR_SOUTH, DIR_WEST)), 4  # any iterable
    )
    assert pack.name == "point_placements_extension_placement"
    placement, inferral = extension_strategies(pack)
    assert placement.partial and placement.dirs == (DIR_SOUTH, DIR_WEST)
    assert inferral.maxlen == 4
    assert (
        pack.expansion_strats[:-1] == TileScopePack.point_placements().expansion_strats
    )
    assert TileScopePack.from_dict(json.loads(json.dumps(pack.to_jsonable()))) == pack
    with pytest.raises(ValueError):  # twice
        pack.add_extension_placement((DIR_NORTH,), 3)
    with pytest.raises(ValueError):  # a requirement placement already
        TileScopePack.only_root_placements().add_extension_placement((DIR_NORTH,), 3)
    with_inferral = TileScopePack.point_placements().add_inferral(
        strat.ObstructionInferralFactory(2)
    )
    with pytest.raises(ValueError):  # an obstruction inferral already
        with_inferral.add_extension_placement((DIR_NORTH,), 3)
    sink = TileScopePack.point_placements().kitchen_sinkify(
        short_obs_len=4, obs_inferral_len=2, tracked=False, level=1
    )
    with pytest.raises(ValueError):
        sink.add_extension_placement((DIR_NORTH,), 3)


def test_the_pack_method_places_in_each_direction_once():
    pack = TileScopePack.point_placements().add_extension_placement(
        (DIR_WEST, DIR_NORTH, DIR_WEST), 3
    )
    placement, inferral = extension_strategies(pack)
    assert placement.dirs == (DIR_WEST, DIR_NORTH) and inferral.maxlen == 3


def test_the_steps_of_a_chain_and_their_placement():
    """Each step is a named tuple of its direction and the basis it leaves, and the
    placement that follows the chain is in its directions, in their order and each
    once, with the length of the first step's basis."""
    patterns = extended_in("123", DIR_NORTH, DIR_WEST, DIR_NORTH)
    chain = find_one_point_extension_chain(patterns)
    assert all(isinstance(step, OnePointExtension) for step in chain)
    assert [step.direction for step in chain] == [DIR_NORTH, DIR_WEST, DIR_NORTH]
    assert chain[0] == find_one_point_extension(patterns)
    assert chain[1] == find_one_point_extension(chain[0].reduced_basis)
    assert chain[-1].reduced_basis == (Perm((0, 1, 2)),)
    assert extension_placement_arguments(chain) == ((DIR_NORTH, DIR_WEST), 5)
    assert extension_placement_arguments(chain[1:]) == ((DIR_WEST, DIR_NORTH), 4)


def warnings(monkeypatch, argv):
    """Build the pack of 'tilescope spec' with the arguments, and return what was
    logged as a warning."""
    messages = []
    monkeypatch.setattr(
        cli.logger,
        "warning",
        lambda message, *args: messages.append(message % args if args else message),
    )
    build_pack(parser.parse_args(argv))
    return messages


@pytest.mark.parametrize(
    "pack", ["row_and_col_placements", "row_placements", "col_placements"]
)
def test_the_flag_warns_of_a_pack_that_inserts_no_points(monkeypatch, pack):
    """These packs insert no point requirements, so the placement has no point to
    place: the flag warns, but builds the pack."""
    (message,) = warnings(monkeypatch, ["spec", "1234_1243_1423_4123", pack, "-x"])
    assert "--extension-placement places the point of a point requirement" in message
    assert "point_placements does" in message


@pytest.mark.parametrize(
    "pack",
    [
        "point_placements",
        "insertion_point_placements",
        "all_the_strategies",
        "requirement_placements",
    ],
)
def test_the_flag_does_not_warn_of_a_pack_that_inserts_points(monkeypatch, pack):
    """These packs insert point requirements, through CellInsertionFactory or
    through RequirementInsertionFactory."""
    assert not warnings(monkeypatch, ["spec", "1234_1243_1423_4123", pack, "-x"])


# the message's sentence on the class to search for instead
SEARCH_FOR = (
    "Search for Av(012) instead: its generating function G gives the class's by "
    "F = 1 + x (x G)'"
)

# the message's last sentence, on what the placement needs, for one direction and for
# more
PLACEMENT_NEEDS = (
    "The placement places the point of a point requirement, so the pack must insert "
    "point requirements, as point_placements does."
)
PLACEMENTS_NEED = (
    "The placements place the point of a point requirement, so the pack must insert "
    "point requirements, as point_placements does."
)

# The hint's whole message for a chain of steps. Each case: the directions in which
# 123 is extended, one after the other (the last is the chain's first step), and
# what follows the message's first sentence, which is built from HINT_WORDS.
WHOLE_MESSAGES = [
    pytest.param(
        (DIR_NORTH,),
        f"{SEARCH_FOR}. Or add to the pack a partial placement of the topmost point, "
        "with obstruction inferral to length 3, which turns the class into that point "
        "and Av(012) (TileScopePack.add_extension_placement((DIR_NORTH,), 3), or "
        f"--extension-placement). {PLACEMENT_NEEDS}",
        id="one step",
    ),
    pytest.param(
        (DIR_NORTH, DIR_NORTH),
        "That class is such an extension too, and taking out one more point, the "
        "maximum, leaves a permutation of Av(012): the class has n (n - 1) times as "
        "many permutations of length n as Av(012) has of length n - 2, for n >= 2. "
        f"{SEARCH_FOR}, applied twice. Or "
        "add to the pack a partial placement of the topmost point, with obstruction "
        "inferral to length 4, which takes the points out one step at a time "
        "(TileScopePack.add_extension_placement((DIR_NORTH,), 4), or "
        f"--extension-placement). {PLACEMENT_NEEDS}",
        id="two steps in one direction",
    ),
    pytest.param(
        (DIR_NORTH, DIR_WEST),
        "That class is such an extension too, and taking out one more point, the "
        "maximum, leaves a permutation of Av(012): the class has n (n - 1) times as "
        "many permutations of length n as Av(012) has of length n - 2, for n >= 2. "
        f"{SEARCH_FOR}, applied twice. Or "
        "add to the pack partial placements of the leftmost point and the topmost "
        "point, with obstruction inferral to length 4, which take the points out one "
        "step at a time (TileScopePack.add_extension_placement((DIR_WEST, "
        f"DIR_NORTH), 4), or --extension-placement). {PLACEMENTS_NEED}",
        id="two steps in two directions",
    ),
    pytest.param(
        (DIR_NORTH, DIR_NORTH, DIR_NORTH),
        "That class is such an extension too, and taking out 2 more points, the "
        "maximum each time, leaves a permutation of Av(012): the class has n (n - 1) "
        "(n - 2) times as many permutations of length n as Av(012) has of length "
        "n - 3, for n >= 3. "
        f"{SEARCH_FOR}, applied 3 times. Or add to the pack a partial placement of the "
        "topmost point, with obstruction inferral to length 5, which takes the "
        "points out one step at a time "
        "(TileScopePack.add_extension_placement((DIR_NORTH,), 5), or "
        f"--extension-placement). {PLACEMENT_NEEDS}",
        id="three steps in one direction",
    ),
    pytest.param(
        (DIR_NORTH, DIR_NORTH, DIR_WEST),
        "That class is such an extension too, and taking out 2 more points, the "
        "maximum each time, leaves a permutation of Av(012): the class has n (n - 1) "
        "(n - 2) times as many permutations of length n as Av(012) has of length "
        "n - 3, for n >= 3. "
        f"{SEARCH_FOR}, applied 3 times. Or add to the pack partial placements of the "
        "leftmost point and the topmost point, with obstruction inferral to length "
        "5, which take the points out one step at a time "
        "(TileScopePack.add_extension_placement((DIR_WEST, DIR_NORTH), 5), or "
        f"--extension-placement). {PLACEMENTS_NEED}",
        id="three steps, the later two in one direction, the first in another",
    ),
    pytest.param(
        (DIR_NORTH, DIR_WEST, DIR_SOUTH),
        "That class is such an extension too, and taking out 2 more points, the "
        "leftmost point, then the maximum, leaves a permutation of Av(012): the class "
        "has n (n - 1) (n - 2) times as many permutations of length n as Av(012) has "
        f"of length n - 3, for n >= 3. {SEARCH_FOR}, applied 3 times. Or add to the "
        "pack partial "
        "placements of the bottommost point, the leftmost point and the topmost "
        "point, with obstruction inferral to length 5, which take the points out one "
        "step at a time (TileScopePack.add_extension_placement((DIR_SOUTH, "
        f"DIR_WEST, DIR_NORTH), 5), or --extension-placement). {PLACEMENTS_NEED}",
        id="three steps in three directions",
    ),
    pytest.param(
        (DIR_WEST, DIR_NORTH, DIR_NORTH),
        "That class is such an extension too, and taking out 2 more points, the "
        "maximum, then the leftmost point, leaves a permutation of Av(012): the class "
        "has n (n - 1) (n - 2) times as many permutations of length n as Av(012) has "
        f"of length n - 3, for n >= 3. {SEARCH_FOR}, applied 3 times. Or add to the "
        "pack partial "
        "placements of the topmost point and the leftmost point, with obstruction "
        "inferral to length 5, which take the points out one step at a time "
        "(TileScopePack.add_extension_placement((DIR_NORTH, DIR_WEST), 5), or "
        f"--extension-placement). {PLACEMENTS_NEED}",
        id="three steps, the later two in two directions, the first as the second",
    ),
]


@pytest.mark.parametrize("extending, rest", WHOLE_MESSAGES)
def test_the_whole_message(extending, rest):
    """The whole of the hint's message, with the class the first step leaves named
    once, the points the later steps take out ('each time' only past two steps, and
    only when the later steps agree), how often the transform is applied, the
    placements and what they need, for chains of one to three steps. The class
    names come from extended_in, not from the hint."""
    patterns = extended_in("123", *extending)
    adding, taken_out, _, _ = HINT_WORDS[extending[-1]]
    first = Av(Basis(*extended_in("123", *extending[:-1])))
    (hint,) = hints_for(patterns)
    assert hint.message == (
        f"The basis is every way of adding {adding} to each pattern of the basis of "
        f"{first}, so the class is the permutations whose {taken_out}, leaves a "
        "permutation of that class, and it has n times as many permutations of "
        f"length n as that class has of length n - 1, for n >= 1. {rest}"
    )


@pytest.mark.parametrize("direction", DIRECTIONS)
def test_the_pack_method_takes_an_inferral_of_length_1(direction):
    """The shortest inferral (the empty cell inferral's length): the boundary of
    'at least 1', which the method takes though the hint never asks for it."""
    pack = TileScopePack.point_placements().add_extension_placement((direction,), 1)
    placement, inferral = extension_strategies(pack)
    assert placement.dirs == (direction,) and inferral.maxlen == 1


@pytest.mark.parametrize(
    "directions, length, said",
    [
        ((), 3, "^The directions must be one or more of DIR_NORTH"),
        ((DIR_NORTH, 4), 3, "^The directions must be one or more of DIR_NORTH"),
        ((DIR_NORTH,), 0, "^The inferral's length must be at least 1, not 0"),
        ((DIR_NORTH,), -1, "^The inferral's length must be at least 1, not -1"),
    ],
    ids=["no directions", "not a direction", "length 0", "length -1"],
)
def test_the_pack_method_says_what_is_wrong(directions, length, said):
    """The error is the method's own check, not one from further in."""
    with pytest.raises(ValueError, match=said):
        TileScopePack.point_placements().add_extension_placement(directions, length)


def test_the_warning_names_the_pack(monkeypatch):
    argv = ["spec", "1234_1243_1423_4123", "row_and_col_placements", "-x"]
    (message,) = warnings(monkeypatch, argv)
    assert "and row_and_col_placements inserts none" in message


@pytest.mark.parametrize("length", [2.5, 3.0, True, None, "3"])
def test_the_pack_method_takes_only_an_integer_length(length):
    """A length that is not an integer is refused, where 2.5 and True were taken and
    the search then found nothing."""
    with pytest.raises(TypeError, match="^The inferral's length must be an integer"):
        TileScopePack.point_placements().add_extension_placement((DIR_NORTH,), length)


def test_no_chain_has_no_placement_arguments():
    """The chain of a basis that is no one-point extension is empty, and has no
    placement to follow it."""
    assert find_one_point_extension_chain(basis("123")) == []
    with pytest.raises(ValueError, match="^The chain has no steps"):
        extension_placement_arguments([])


def test_the_placement_arguments_of_any_iterable_of_steps():
    """A generator of steps, and steps written as pairs, give the same arguments."""
    chain_of_steps = find_one_point_extension_chain(
        extended_in("123", DIR_NORTH, DIR_WEST)
    )
    expected = extension_placement_arguments(chain_of_steps)
    assert expected == ((DIR_WEST, DIR_NORTH), 4)
    assert extension_placement_arguments(step for step in chain_of_steps) == expected
    pairs = [(step.direction, step.reduced_basis) for step in chain_of_steps]
    assert extension_placement_arguments(pairs) == expected


def inserts_a_point_into_the_class(pack, patterns):
    """Return True if a strategy that the pack expands classes with, applied to the
    class's 1x1 tiling, gives that tiling with a point requirement: the requirement
    whose point the partial placement places."""
    tiling = Tiling([GriddedPerm.single_cell(pattern, (0, 0)) for pattern in patterns])
    with_a_point = tiling.insert_cell((0, 0))
    for factory in itertools.chain(pack.initial_strats, *pack.expansion_strats):
        for made in factory(tiling):
            rule = made(tiling) if isinstance(made, AbstractStrategy) else made
            if with_a_point in rule.children:
                return True
    return False


@pytest.mark.parametrize(
    "name", [name for name in cli.BASE_PACK if name != "only_root_placements"]
)
def test_the_flag_warns_of_the_packs_that_insert_no_point_into_the_class(
    monkeypatch, name
):
    """The flag warns exactly of the packs none of whose strategies inserts a point
    requirement into the class's tiling, as the corroborations of
    row_and_col_placements do not: POINT_INSERTIONS names every strategy of the
    command's packs that does. regular_insertion_encoding asks for a basis it can
    encode, and only_root_placements cannot take the flag."""
    patterns = extended_in("123", DIR_NORTH)
    if name == "regular_insertion_encoding":
        patterns = extended_in("12_21", DIR_NORTH)
    string = "_".join(map(str, patterns))
    pack = build_pack(parser.parse_args(["spec", string, name]))
    warned = warnings(monkeypatch, ["spec", string, name, "-x"])
    assert bool(warned) != inserts_a_point_into_the_class(pack, patterns)


SEARCH_FOR_01 = SEARCH_FOR.replace("Av(012)", "Av(01)")

# Av(12) extended in the directions one after the other, the last the chain's first
# step: the directions of the steps are the reverse (no tie, as for the cases of
# WHOLE_MESSAGES), and the message follows its first sentence with
FOUR_STEP_MESSAGES = [
    pytest.param(
        (DIR_NORTH,) * 4,
        "That class is such an extension too, and taking out 3 more points, the "
        "maximum each time, leaves a permutation of Av(01): the class has n (n - 1) "
        "(n - 2) (n - 3) times as many permutations of length n as Av(01) has of "
        f"length n - 4, for n >= 4. {SEARCH_FOR_01}, applied 4 times. Or add to the "
        "pack a partial placement of the topmost point, with obstruction inferral to "
        "length 5, which takes the points out one step at a time "
        "(TileScopePack.add_extension_placement((DIR_NORTH,), 5), or "
        f"--extension-placement). {PLACEMENT_NEEDS}",
        id="four steps in one direction",
    ),
    pytest.param(
        (DIR_NORTH, DIR_WEST, DIR_SOUTH, DIR_EAST),
        "That class is such an extension too, and taking out 3 more points, the "
        "minimum, then the leftmost point, then the maximum, leaves a permutation "
        "of Av(01): the class has n (n - 1) (n - 2) (n - 3) times as many "
        "permutations of length n as Av(01) has of length n - 4, for n >= 4. "
        f"{SEARCH_FOR_01}, applied 4 times. Or add to the pack partial placements of "
        "the rightmost point, the bottommost point, the leftmost point and the "
        "topmost point, with obstruction inferral to length 5, which take the points "
        "out one step at a time (TileScopePack.add_extension_placement(("
        "DIR_EAST, DIR_SOUTH, DIR_WEST, DIR_NORTH), 5), or --extension-placement). "
        f"{PLACEMENTS_NEED}",
        id="four steps in four directions",
    ),
]


@pytest.mark.parametrize("extending, rest", FOUR_STEP_MESSAGES)
def test_four_steps(extending, rest):
    """Four steps: the whole message, the counts n (n - 1) (n - 2) (n - 3) times those
    of Av(01) from n = 4 on (by brute force), the transform applied 4 times to the
    series of Av(01), and the pack that follows the hint."""
    patterns = extended_in("12", *extending)
    steps = tuple(reversed(extending))
    chain = find_one_point_extension_chain(patterns)
    assert tuple(step.direction for step in chain) == steps
    # every permutation of length up to 3 is in the class, as the basis has patterns
    # of length 5 only
    assert counts(patterns) == [1, 1, 2, 6] + [
        n * (n - 1) * (n - 2) * (n - 3) for n in range(4, 8)
    ]
    adding, taken_out, _, _ = HINT_WORDS[extending[-1]]
    first = Av(Basis(*extended_in("12", *extending[:-1])))
    (hint,) = hints_for(patterns)
    assert hint.message == (
        f"The basis is every way of adding {adding} to each pattern of the basis of "
        f"{first}, so the class is the permutations whose {taken_out}, leaves a "
        "permutation of that class, and it has n times as many permutations of "
        f"length n as that class has of length n - 1, for n >= 1. {rest}"
    )
    x = sympy.Symbol("x")
    series = sum(x**n for n in range(8))  # Av(01) has one permutation of each length
    for _ in range(4):  # "applied 4 times"
        series = sympy.expand(1 + x * sympy.diff(x * series, x))
    assert [series.coeff(x, n) for n in range(8)] == counts(patterns)
    directions = tuple(dict.fromkeys(steps))
    assert extension_placement_arguments(chain) == (directions, 5)
    placement, inferral = hint.strategies
    assert placement.dirs == directions and inferral.maxlen == 5
    placement, inferral = extension_strategies(build_pack(flag_args(patterns)))
    assert placement.dirs == directions and inferral.maxlen == 5


@pytest.mark.parametrize("length", [False, 0.5, -0.5])
def test_a_length_below_1_that_is_not_an_integer_is_a_type_error(length):
    """The type is checked before the range: False is not an integer here, as True
    is not, and 0.5 is not one though it is below 1."""
    with pytest.raises(TypeError, match="^The inferral's length must be an integer"):
        TileScopePack.point_placements().add_extension_placement((DIR_NORTH,), length)


def test_no_steps_from_an_empty_iterator():
    with pytest.raises(ValueError, match="^The chain has no steps"):
        extension_placement_arguments(iter(()))


def test_the_warning_in_full(monkeypatch):
    argv = ["spec", "1234_1243_1423_4123", "row_and_col_placements", "-x"]
    (message,) = warnings(monkeypatch, argv)
    assert message == (
        "--extension-placement places the point of a point requirement in the class's "
        "tiling, and row_and_col_placements inserts none there, so the placement may "
        "not apply; point_placements does."
    )


def test_the_pack_method_takes_an_integral_length():
    """A length is an integer as operator.index takes one, such as an integer type
    of another library's."""

    class Three:
        def __index__(self):
            return 3

    pack = TileScopePack.point_placements().add_extension_placement(
        (DIR_NORTH,), Three()
    )
    _, inferral = extension_strategies(pack)
    assert inferral.maxlen == 3 and type(inferral.maxlen) is int

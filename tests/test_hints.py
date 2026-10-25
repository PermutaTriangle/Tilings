import argparse

import pytest

from permuta import Av, Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST
from permuta.perm_sets.basis import Basis
from tilings import GriddedPerm, Tiling, cli
from tilings import strategies as strat
from tilings.cli import build_pack, parser
from tilings.hints import (
    hints_for,
    one_point_extension,
    one_point_extension_chain,
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
    # with the flag the pack follows the hint, and the search still finds the answer
    code, messages = logged(
        monkeypatch, ["spec", "123_231_312", "point_placements", "-r"]
    )
    assert code == 0
    assert not [message for message in messages if message.startswith("Hint")]
    assert any(message.startswith("The generating function is") for message in messages)
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
        set().union(*(one_point_extensions(p, direction) for p in basis(string)))
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
    assert one_point_extension(patterns) == (direction, tuple(sorted(basis(string))))
    small, large = Av(Basis(*basis(string))), Av(Basis(*patterns))
    assert [large.count(n) for n in range(1, 8)] == [
        n * small.count(n - 1) for n in range(1, 8)
    ]


def test_a_basis_not_minimal():
    """A pattern containing one of the basis is left out first, as Av ignores it."""
    patterns = extended("123", DIR_NORTH) + [Perm((0, 1, 2, 3, 4))]
    assert one_point_extension(patterns) == (DIR_NORTH, (Perm((0, 1, 2)),))


def test_not_a_one_point_extension():
    assert one_point_extension(basis("1234_1243_1423")) is None  # one is missing
    assert one_point_extension(basis("1234")) is None
    assert one_point_extension(basis("12_21")) is None  # extends patterns of length 1
    assert one_point_extension([]) is None


def test_the_extension_hint():
    (hint,) = hints_for(extended("123", DIR_NORTH))
    assert hint.name == "one-point extension"
    assert "adding a new maximum to a pattern of the basis of Av(012)" in hint.message
    assert "n times as many permutations of length n as Av(012)" in hint.message
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
        [GriddedPerm.single_cell(p, (0, 0)) for p in extended("123", direction)]
    )
    pack = TileScopePack.point_placements().add_extension_placement((direction,), 3)
    spec = TileScope(root, pack).auto_search(max_expansion_time=30)  # under a second
    placements = [
        rule.strategy
        for rule in spec.rules_dict.values()
        if isinstance(rule.strategy, RequirementPlacementStrategy)
    ]
    assert [(p.direction, p.own_row and p.own_col) for p in placements] == [
        (direction, False)
    ]
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
            *(one_point_extensions(p, second) for p in extended("123", DIR_NORTH))
        )
    )
    chain = one_point_extension_chain(patterns)
    assert tuple(direction for direction, _ in chain) == directions + (
        (DIR_NORTH,) if second == DIR_NORTH else ()
    )
    assert chain[-1][1] == (Perm((0, 1, 2)),)
    (hint,) = hints_for(patterns)
    assert "is such an extension too, and reduced again it is Av(012)" in hint.message
    assert "n (n - 1) times as many permutations of length n as Av(012)" in hint.message
    assert "Search for Av(012) instead" in hint.message
    placement, inferral = hint.strategies
    assert placement.dirs == directions and inferral.maxlen == 4
    args = parser.parse_args(
        ["spec", "_".join(map(str, patterns)), "point_placements", "-x"]
    )
    assert build_pack(args).expansion_strats[-1][0].dirs == directions

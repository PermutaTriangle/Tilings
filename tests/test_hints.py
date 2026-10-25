import argparse

import pytest

from permuta import Av, Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST
from permuta.perm_sets.basis import Basis
from tilings import GriddedPerm, Tiling
from tilings import strategies as strat
from tilings.cli import build_pack, parser
from tilings.hints import hints, one_point_extension, one_point_extensions
from tilings.strategies.requirement_placement import RequirementPlacementStrategy
from tilings.strategy_pack import TileScopePack
from tilings.tilescope import TileScope

DIRECTIONS = (DIR_NORTH, DIR_SOUTH, DIR_WEST, DIR_EAST)


def basis(string):
    return [Perm.to_standard(map(int, pattern)) for pattern in string.split("_")]


def test_a_class_closed_under_rotation():
    (hint,) = hints(basis("1324_2413_3241_4132"))
    assert hint.name == "rotationally stable"
    assert "closed under rotation of its positions" in hint.message
    assert "Av(021,2130) and Av(102,3021)" in hint.message  # both of its cuts
    assert hint.pack_method == "add_rotational_cuts"
    assert hint.cli_flag == "--rotational-cuts"
    assert hasattr(TileScopePack, hint.pack_method)


def test_one_cut_and_the_values():
    (hint,) = hints(basis("1234_2341_3412_4123"))
    assert "its cut, Av(012,2301)," in hint.message  # the min and the max cut agree
    (hint,) = hints(basis("1342_2413_3124_4231"))
    assert "closed under rotation of its values" in hint.message


def test_no_hint():
    for string in ("123_3412", "1", "1234"):
        assert hints(basis(string)) == [], string
    assert hints([]) == []


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
    (hint,) = hints(extended("123", DIR_NORTH))
    assert hint.name == "one-point extension"
    assert "adding a new maximum to a pattern of the basis of Av(012)" in hint.message
    assert "n times as many permutations of length n as Av(012)" in hint.message
    assert "partial placement of the topmost point" in hint.message
    assert "add_extension_placement(DIR_NORTH, 3)" in hint.message
    assert hint.pack_method == "add_extension_placement"
    assert hasattr(TileScopePack, hint.pack_method)
    assert hint.cli_flag == "--extension-placement"
    (hint,) = hints(extended("1342", DIR_WEST))
    assert "adding a new leftmost point" in hint.message
    assert "add_extension_placement(DIR_WEST, 4)" in hint.message


def test_both_hints():
    """Every permutation of length 3: closed under rotation, and every one-point
    extension of Av(01, 10)."""
    names = [hint.name for hint in hints(basis("123_132_213_231_312_321"))]
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
    pack = TileScopePack.point_placements().add_extension_placement(direction, 3)
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

import argparse

from permuta import Perm
from tilings import strategies as strat
from tilings.cli import build_pack, parser
from tilings.hints import hints
from tilings.strategy_pack import TileScopePack


def basis(string):
    return [Perm.to_standard(map(int, patt)) for patt in string.split("_")]


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

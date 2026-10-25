import argparse

from permuta import Perm
from tilings import cli
from tilings import strategies as strat
from tilings.cli import build_pack, parser
from tilings.hints import hints_for
from tilings.strategy_pack import TileScopePack


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
    (hint,) = hints_for(lift_of_lift)
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

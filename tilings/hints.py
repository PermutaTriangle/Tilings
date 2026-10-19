"""
Hints: properties of a permutation class that make it likely that a change to a
strategy pack helps TileScope find a specification for it. Permuta's enumeration
strategies settle a class's count when one applies; a hint only says what is worth
adding to the pack, and why. `tilescope spec` tells the user of the hints that the
pack it runs does not follow.

The first hint: a class closed under rotation, of its positions or of its values,
has n times as many permutations of length n as each of its cuts has of length
n - 1, and the rotational cut strategies use that (TileScopePack.add_rotational_cuts,
or --rotational-cuts on the command line).
"""

from typing import Iterable, List, NamedTuple

from permuta import Av, Perm
from permuta.perm_sets.basis import Basis
from tilings.strategies.rotation import max_cut, min_cut, rotation_of

__all__ = ["Hint", "hints"]


class Hint(NamedTuple):
    """A hint for a class: its name, what was found and what to do, and the pack
    method and the 'tilescope spec' flag that follow it."""

    name: str
    message: str
    pack_method: str
    cli_flag: str


def hints(basis: Iterable[Perm]) -> List[Hint]:
    """Return the hints for the class with the basis.

    Examples:
        >>> [hint.name for hint in hints(Perm.to_standard(p) for p in
        ...     ("1324", "2413", "3241", "4132"))]
        ['rotationally stable']
        >>> hints([Perm((0, 1, 2)), Perm((2, 3, 0, 1))])
        []
    """
    patts = tuple(Basis.from_iterable(basis))
    out: List[Hint] = []
    if patts and all(len(patt) > 1 for patt in patts):
        rotation = rotation_of(patts)
        if rotation is not None:
            cuts = sorted(
                {Basis.from_iterable(cut(patts)) for cut in (min_cut, max_cut)},
                key=str,
            )
            if len(cuts) == 1:
                counted = f"its cut, {Av(cuts[0])},"
            else:
                counted = f"each of its cuts, {Av(cuts[0])} and {Av(cuts[1])},"
            why = (
                "its basis is rotationally stable"
                if rotation == "positions"
                else "its inverse basis is rotationally stable"
            )
            out.append(
                Hint(
                    "rotationally stable",
                    f"The class is closed under rotation of its {rotation} ({why}), "
                    f"so it has n times as many permutations of length n as "
                    f"{counted} has of length n - 1. Add the rotational cuts to the "
                    "pack (TileScopePack.add_rotational_cuts, or --rotational-cuts) "
                    "to use them, on every 1x1 tiling closed under rotation that "
                    "the search finds.",
                    "add_rotational_cuts",
                    "--rotational-cuts",
                )
            )
    return out

"""
Hints: properties of a permutation class that make it likely that a simpler class,
or a change to a strategy pack, helps TileScope find a specification for it.
Permuta's enumeration strategies settle a class's count when one applies; a hint
only says what is worth doing, and why. `tilescope spec` tells the user of the
hints that the pack it runs does not follow.

The first hint: a class closed under rotation, of its positions or of its values,
has n times as many permutations of length n as its cut has of length n - 1, and
the cut can be closed under rotation again. The rotation of a permutation is here
the cyclic shift that moves its first entry to the end. The hint names the class to
search for instead, the cut cut again while it is closed under rotation, whose
generating function gives the class's; or the rotational cuts can be added to the
pack (TileScopePack.add_rotational_cuts, or --rotational-cuts on the command line),
which cut every such tiling the search finds.
"""

from typing import Iterable, List, NamedTuple, Optional, Tuple

from comb_spec_searcher import StrategyPack
from comb_spec_searcher.typing import CSSstrategy
from permuta import Av, Perm
from permuta.perm_sets.basis import Basis
from tilings.strategies.rotation import (
    RotationalCutFactory,
    max_cut,
    max_cut_differs,
    min_cut,
    rotation_kind,
)

__all__ = ["Hint", "hints_for"]


class Hint(NamedTuple):
    """A hint for a class: its name, what was found and what to do, and the
    strategies a pack has when it follows the hint."""

    name: str
    message: str
    strategies: Tuple[CSSstrategy, ...]

    def followed_by(self, pack: StrategyPack) -> bool:
        """Return True if the pack has the hint's strategies (a pack holds one
        strategy of each class, whatever its parameters)."""
        return all(strategy in pack for strategy in self.strategies)


def _closed_under_rotation(patterns: Basis) -> bool:
    """Return True if the rotational cut applies to the class of the minimal basis:
    the class is closed under rotation, and no pattern of the basis is shorter than
    2."""
    return (
        bool(patterns)
        and all(len(pattern) > 1 for pattern in patterns)
        and rotation_kind(patterns) is not None
    )


def _cuts(patterns: Basis) -> List[Basis]:
    """Return the minimal bases of the class's min cut and, if it is another class,
    of its max cut."""
    cuts = [Basis.from_iterable(min_cut(patterns))]
    if max_cut_differs(patterns):
        cuts.append(Basis.from_iterable(max_cut(patterns)))
    return cuts


def _longest_chain_of_cuts(patterns: Basis) -> List[Basis]:
    """Return the class, its cut, the cut's cut and so on, while each is closed
    under rotation: of the chains the two cuts begin, the longest, the min cut's when
    they are as long. Its last class is the one to search for instead."""
    chains = [
        _longest_chain_of_cuts(cut) if _closed_under_rotation(cut) else [cut]
        for cut in _cuts(patterns)
    ]
    return [patterns] + max(chains, key=len)


def _rotation_hint(patterns: Basis) -> Optional[Hint]:
    """Return the hint for a class closed under rotation, None for any other."""
    if not _closed_under_rotation(patterns):
        return None
    rotation = rotation_kind(patterns)
    why = (
        "its basis is rotationally stable; a rotation moves the first entry to "
        "the end"
        if rotation == "positions"
        else "its inverse basis is rotationally stable; a rotation of the values "
        "raises each by one, the largest becoming the smallest"
    )
    chain = _longest_chain_of_cuts(patterns)
    cuts = len(chain) - 1
    end = Av(chain[-1])
    if cuts == 1 and max_cut_differs(patterns):
        min_class, max_class = (Av(cut) for cut in _cuts(patterns))
        counted = f"each of its cuts, {min_class} and {max_class}, has"
        search = "either"
    else:
        counted = f"its cut, {Av(chain[1])}, has"
        search = str(end)
    again = ""
    if cuts > 1:
        cut_again = "its cut is" if cuts == 2 else f"cut {cuts - 1} more times it is"
        times = " ".join(["n"] + [f"(n - {index})" for index in range(1, cuts)])
        again = (
            f" That cut is closed under rotation too, and {cut_again} {end}: the "
            f"class has {times} times as many permutations of length n as {end} has "
            f"of length n - {cuts}."
        )
    return Hint(
        "rotationally stable",
        f"The class is closed under rotation of its {rotation} ({why}), so it has n "
        f"times as many permutations of length n as {counted} of length n - 1."
        f"{again} Search for {search} instead: its generating function G gives the "
        "class's, F = 1 + x (x G)', once for each cut. Or add the rotational cuts to "
        "the pack "
        "(TileScopePack.add_rotational_cuts, or --rotational-cuts), which cut every "
        "1x1 tiling closed under rotation that the search finds, though "
        "comb_spec_searcher cannot compute a generating function through them.",
        (RotationalCutFactory(),),
    )


def hints_for(basis: Iterable[Perm]) -> List[Hint]:
    """Return the hints for the class with the basis.

    Examples:
        >>> [hint.name for hint in hints_for(Perm.to_standard(p) for p in
        ...     ("1324", "2413", "3241", "4132"))]
        ['rotationally stable']
        >>> hints_for([Perm((0, 1, 2)), Perm((2, 3, 0, 1))])
        []
    """
    patterns = Basis.from_iterable(basis)
    found: List[Hint] = []
    rotation_hint = _rotation_hint(patterns)
    if rotation_hint is not None:
        found.append(rotation_hint)
    return found

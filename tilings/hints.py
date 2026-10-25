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

The second: a class whose basis is every one-point extension of the patterns of a
basis B in one direction, every way of adding to each a new maximum, say, is the
permutations whose maximum, taken out, leaves a permutation of Av(B). It has n
times as many permutations of length n as Av(B) has of length n - 1, and a partial
placement of the topmost point, with obstruction inferral to the length of B's
longest pattern, turns it into that point and Av(B)
(TileScopePack.add_extension_placement, or --extension-placement).
"""

from typing import Iterable, List, NamedTuple, Optional, Set, Tuple

from permuta import Av, Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST
from permuta.perm_sets.basis import Basis
from tilings.strategies.rotation import max_cut, min_cut, rotation_of

__all__ = ["Hint", "hints", "one_point_extension", "one_point_extensions"]

# For each direction, in the order one_point_extension tries them: the point a
# one-point extension adds, that point once added, the point the placement places,
# and the direction's name.
EXTENSION_WORDS = {
    DIR_NORTH: ("a new maximum", "maximum", "topmost point", "DIR_NORTH"),
    DIR_SOUTH: ("a new minimum", "minimum", "bottommost point", "DIR_SOUTH"),
    DIR_WEST: ("a new leftmost point", "leftmost point", "leftmost point", "DIR_WEST"),
    DIR_EAST: (
        "a new rightmost point",
        "rightmost point",
        "rightmost point",
        "DIR_EAST",
    ),
}


class Hint(NamedTuple):
    """A hint for a class: its name, what was found and what to do, and the pack
    method and the 'tilescope spec' flag that follow it."""

    name: str
    message: str
    pack_method: str
    cli_flag: str


def one_point_extensions(pattern: Perm, direction: int) -> Set[Perm]:
    """Return every way of adding to the pattern a new point that is its maximum
    (DIR_NORTH), its minimum (DIR_SOUTH), its leftmost point (DIR_WEST) or its
    rightmost point (DIR_EAST).

    Examples:
        >>> sorted(one_point_extensions(Perm((0, 1)), DIR_NORTH))
        [Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((2, 0, 1))]
        >>> sorted(one_point_extensions(Perm((0, 1)), DIR_WEST))
        [Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((2, 0, 1))]
    """
    size = len(pattern)
    if direction == DIR_NORTH:
        return {pattern.insert(index, size) for index in range(size + 1)}
    if direction == DIR_SOUTH:
        return {pattern.insert(index, 0) for index in range(size + 1)}
    if direction == DIR_WEST:
        return {pattern.insert(0, value) for value in range(size + 1)}
    if direction == DIR_EAST:
        return {pattern.insert(size, value) for value in range(size + 1)}
    raise ValueError(f"Invalid direction {direction}")


def _without_extreme_point(pattern: Perm, direction: int) -> Perm:
    """Return the pattern without its point furthest in the direction."""
    if direction == DIR_NORTH:
        return pattern.remove(pattern.index(len(pattern) - 1))
    if direction == DIR_SOUTH:
        return pattern.remove(pattern.index(0))
    if direction == DIR_WEST:
        return pattern.remove(0)
    return pattern.remove(len(pattern) - 1)


def one_point_extension(
    basis: Iterable[Perm],
) -> Optional[Tuple[int, Tuple[Perm, ...]]]:
    """Return the first direction, of north, south, west and east, in which the
    basis is every one-point extension (one_point_extensions) of the patterns of a
    basis B of patterns of length at least 2, with B; None if there is none. The
    class is then the permutations whose point furthest in that direction, taken
    out, leaves a permutation of Av(B).

    Examples:
        >>> one_point_extension(
        ...     Perm.to_standard(p) for p in ("1234", "1243", "1423", "4123")
        ... ) == (DIR_NORTH, (Perm((0, 1, 2)),))
        True
        >>> one_point_extension([Perm((0, 1, 2))]) is None
        True
    """
    patterns = set(Basis.from_iterable(basis))
    if not patterns or any(len(pattern) < 3 for pattern in patterns):
        return None
    for direction in EXTENSION_WORDS:
        reduced = {_without_extreme_point(pattern, direction) for pattern in patterns}
        extended = set().union(
            *(one_point_extensions(pattern, direction) for pattern in reduced)
        )
        if extended == patterns:
            return direction, tuple(sorted(reduced))
    return None


def hints(basis: Iterable[Perm]) -> List[Hint]:
    """Return the hints for the class with the basis.

    Examples:
        >>> [hint.name for hint in hints(Perm.to_standard(p) for p in
        ...     ("1324", "2413", "3241", "4132"))]
        ['rotationally stable']
        >>> hints([Perm((0, 1, 2)), Perm((2, 3, 0, 1))])
        []
        >>> [hint.name for hint in hints(Perm.to_standard(p) for p in
        ...     ("1234", "1243", "1423", "4123"))]
        ['one-point extension']
    """
    patterns = tuple(Basis.from_iterable(basis))
    out: List[Hint] = []
    if patterns and all(len(pattern) > 1 for pattern in patterns):
        rotation = rotation_of(patterns)
        if rotation is not None:
            cuts = sorted(
                {Basis.from_iterable(cut(patterns)) for cut in (min_cut, max_cut)},
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
    extension_hint = _extension_hint(patterns)
    if extension_hint is not None:
        out.append(extension_hint)
    return out


def _extension_hint(patterns: Iterable[Perm]) -> Optional[Hint]:
    """Return the one-point extension hint for a basis that is one
    (one_point_extension), None for any other."""
    extension = one_point_extension(patterns)
    if extension is None:
        return None
    direction, reduced = extension
    new_point, added, placed, name = EXTENSION_WORDS[direction]
    length = max(len(pattern) for pattern in reduced)
    small = Av(Basis(*reduced))
    return Hint(
        "one-point extension",
        f"The basis is every way of adding {new_point} to a pattern of the basis of "
        f"{small}, so the class is the permutations whose {added}, taken out, "
        f"leaves a permutation of {small}, and it has n times as many permutations "
        f"of length n as {small} has of length n - 1. A partial placement of the "
        f"{placed}, with obstruction inferral to length {length}, turns the class "
        f"into that point and {small}: add them to the pack "
        f"(TileScopePack.add_extension_placement({name}, {length}), or "
        "--extension-placement).",
        "add_extension_placement",
        "--extension-placement",
    )

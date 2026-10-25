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

The second: a class whose basis is every one-point extension of the patterns of a
basis B in one direction, every way of adding a new maximum to each, say, is the
permutations whose maximum, taken out, leaves a permutation of Av(B). It has n
times as many permutations of length n as Av(B) has of length n - 1, and Av(B) can
be such an extension again. The hint names the class to search for instead, B
reduced again while it is such an extension; or a partial placement of the
topmost point, with obstruction inferral to the length of B's longest pattern, can
be added to the pack (TileScopePack.add_extension_placement, or
--extension-placement), which turns the class into that point and Av(B).
"""

from typing import Iterable, List, NamedTuple, Optional, Set, Tuple

from comb_spec_searcher import StrategyPack
from comb_spec_searcher.typing import CSSstrategy
from permuta import Av, Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST
from permuta.perm_sets.basis import Basis
from tilings.strategies.obstruction_inferral import ObstructionInferralFactory
from tilings.strategies.requirement_placement import RequirementPlacementFactory
from tilings.strategies.rotation import (
    RotationalCutFactory,
    max_cut,
    max_cut_differs,
    min_cut,
    rotation_kind,
)

__all__ = [
    "Hint",
    "hints_for",
    "one_point_extension",
    "one_point_extension_chain",
    "one_point_extensions",
]

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


def one_point_extension_chain(
    basis: Iterable[Perm],
) -> List[Tuple[int, Tuple[Perm, ...]]]:
    """Return the steps of reducing the basis while it is every one-point extension
    of a basis (one_point_extension): the direction of each and the basis it leaves.
    The last basis is the class to search for instead; the list is empty if the
    basis is no such extension."""
    chain: List[Tuple[int, Tuple[Perm, ...]]] = []
    step = one_point_extension(basis)
    while step is not None:
        chain.append(step)
        step = one_point_extension(step[1])
    return chain


def _reduced_again(chain: List[Tuple[int, Tuple[Perm, ...]]]) -> str:
    """Return the sentence on reducing the class again, for a chain of more than
    one step (one_point_extension_chain), and nothing for one step."""
    steps = len(chain)
    if steps == 1:
        return ""
    first, end = Av(Basis(*chain[0][1])), Av(Basis(*chain[-1][1]))
    reduce_again = (
        "reduced again it is" if steps == 2 else f"reduced {steps - 1} more times it is"
    )
    times = " ".join(["n"] + [f"(n - {index})" for index in range(1, steps)])
    return (
        f" {first} is such an extension too, and {reduce_again} {end}: the class has "
        f"{times} times as many permutations of length n as {end} has of length "
        f"n - {steps}."
    )


def _extension_hint(patterns: Basis) -> Optional[Hint]:
    """Return the one-point extension hint for a basis that is one, None for any
    other."""
    chain = one_point_extension_chain(patterns)
    if not chain:
        return None
    direction, reduced = chain[0]
    new_point, added, placed, _ = EXTENSION_WORDS[direction]
    first, end = Av(Basis(*reduced)), Av(Basis(*chain[-1][1]))
    length = max(len(pattern) for pattern in reduced)
    directions = tuple(dict.fromkeys(step_direction for step_direction, _ in chain))
    names = ", ".join(EXTENSION_WORDS[each][3] for each in directions)
    return Hint(
        "one-point extension",
        f"The basis is every way of adding {new_point} to a pattern of the basis of "
        f"{first}, so the class is the permutations whose {added}, taken out, "
        f"leaves a permutation of {first}, and it has n times as many permutations "
        f"of length n as {first} has of length n - 1.{_reduced_again(chain)} "
        f"Search for {end} "
        "instead: its generating function G gives the class's, F = 1 + x (x G)', "
        "once for each step. Or add to the pack a partial placement of the "
        f"{placed}, with obstruction inferral to length {length}, which turns the "
        f"class into that point and {first} "
        f"(TileScopePack.add_extension_placement(({names},), {length}), or "
        "--extension-placement).",
        (
            RequirementPlacementFactory(partial=True, dirs=directions),
            ObstructionInferralFactory(length),
        ),
    )


def hints_for(basis: Iterable[Perm]) -> List[Hint]:
    """Return the hints for the class with the basis.

    Examples:
        >>> [hint.name for hint in hints_for(Perm.to_standard(p) for p in
        ...     ("1324", "2413", "3241", "4132"))]
        ['rotationally stable']
        >>> hints_for([Perm((0, 1, 2)), Perm((2, 3, 0, 1))])
        []
        >>> [hint.name for hint in hints_for(Perm.to_standard(p) for p in
        ...     ("1234", "1243", "1423", "4123"))]
        ['one-point extension']
    """
    patterns = Basis.from_iterable(basis)
    found: List[Hint] = []
    for hint in (_rotation_hint(patterns), _extension_hint(patterns)):
        if hint is not None:
            found.append(hint)
    return found

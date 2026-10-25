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

The second is for a class whose basis is every one-point extension of a basis B:
every way of adding a new maximum to each pattern of B, say, or a new minimum,
leftmost or rightmost point. The class is then the permutations whose maximum,
taken out, leaves a permutation of Av(B), so it has n times as many permutations of
length n as Av(B) has of length n - 1, and Av(B) may be such an extension in turn.
The hint names the class to search for instead, B reduced while it is such an
extension. Or the pack can be given a partial placement of the topmost point, with
obstruction inferral to the length of B's longest pattern, which turns the class
into that point and Av(B) (TileScopePack.add_extension_placement, or
--extension-placement on the command line).
"""

from typing import Iterable, List, NamedTuple, Optional, Sequence, Set, Tuple

from comb_spec_searcher import StrategyPack
from comb_spec_searcher.typing import CSSstrategy
from permuta import Av, Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST
from permuta.perm_sets.basis import Basis
from tilings.strategies.obstruction_inferral import ObstructionInferralFactory
from tilings.strategies.requirement_placement import (
    DIR_REPR,
    RequirementPlacementFactory,
)
from tilings.strategies.rotation import (
    RotationalCutFactory,
    max_cut,
    max_cut_differs,
    min_cut,
    rotation_kind,
)

__all__ = [
    "Hint",
    "OnePointExtension",
    "extension_placement",
    "hints_for",
    "one_point_extension_chain",
    "one_point_extension_of",
    "one_point_extensions",
]

# The directions of one-point extensions, in the order one_point_extension_of tries
# them.
_DIRECTIONS = (DIR_NORTH, DIR_SOUTH, DIR_WEST, DIR_EAST)


class _ExtensionWords(NamedTuple):
    """How the extension hint speaks of a direction: the point a one-point extension
    adds, that point in the class, and the point the placement places."""

    new_point: str
    point: str
    placed: str


_EXTENSION_WORDS = {
    DIR_NORTH: _ExtensionWords("a new maximum", "maximum", "topmost point"),
    DIR_SOUTH: _ExtensionWords("a new minimum", "minimum", "bottommost point"),
    DIR_WEST: _ExtensionWords(
        "a new leftmost point", "leftmost point", "leftmost point"
    ),
    DIR_EAST: _ExtensionWords(
        "a new rightmost point", "rightmost point", "rightmost point"
    ),
}


class OnePointExtension(NamedTuple):
    """How a basis is every one-point extension of another (one_point_extension_of):
    the direction of the extensions, and the other basis."""

    direction: int
    basis: Tuple[Perm, ...]


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
    if direction == DIR_EAST:
        return pattern.remove(len(pattern) - 1)
    raise ValueError(f"Invalid direction {direction}")


def one_point_extension_of(basis: Iterable[Perm]) -> Optional[OnePointExtension]:
    """Return how the basis, once minimized, is every one-point extension
    (one_point_extensions) of the patterns of a basis B of patterns of length at
    least 2: the first direction, of north, south, west and east, in which it is,
    and B. Return None if it is no such extension. The class is then the
    permutations whose point furthest in that direction, taken out, leaves a
    permutation of Av(B).

    Examples:
        >>> one_point_extension_of(
        ...     Perm.to_standard(word) for word in ("1234", "1243", "1423", "4123")
        ... ) == (DIR_NORTH, (Perm((0, 1, 2)),))
        True
        >>> one_point_extension_of([Perm((0, 1, 2))]) is None
        True
    """
    return _extension_of_minimal(set(Basis.from_iterable(basis)))


def _extension_of_minimal(patterns: Set[Perm]) -> Optional[OnePointExtension]:
    """one_point_extension_of for a minimal basis."""
    if not patterns or any(len(pattern) < 3 for pattern in patterns):
        return None
    for direction in _DIRECTIONS:
        reduced = {_without_extreme_point(pattern, direction) for pattern in patterns}
        # a pattern of length k has k + 1 extensions in a direction, and distinct
        # patterns have none in common, as taking the point out gives the pattern
        if sum(len(pattern) + 1 for pattern in reduced) != len(patterns):
            continue
        extended = set().union(
            *(one_point_extensions(pattern, direction) for pattern in reduced)
        )
        if extended == patterns:
            return OnePointExtension(direction, tuple(sorted(reduced)))
    return None


def one_point_extension_chain(basis: Iterable[Perm]) -> List[OnePointExtension]:
    """Return the steps of reducing the basis while it is every one-point extension
    of a basis (one_point_extension_of): each step's direction, and the basis it
    leaves. The last step's basis is the class to search for instead. The list is
    empty if the basis is no such extension.

    Examples:
        >>> [step.direction == DIR_NORTH for step in one_point_extension_chain(
        ...     Perm.to_standard(word) for word in ("1234", "1243", "1423", "4123")
        ... )]
        [True]
    """
    return _chain_of_minimal(set(Basis.from_iterable(basis)))


def _chain_of_minimal(patterns: Set[Perm]) -> List[OnePointExtension]:
    """one_point_extension_chain for a minimal basis."""
    chain: List[OnePointExtension] = []
    step = _extension_of_minimal(patterns)
    while step is not None:
        chain.append(step)
        # B is minimal: a pattern of B containing another would have an extension
        # containing one of the other's, and the basis extended is minimal
        step = _extension_of_minimal(set(step.basis))
    return chain


def extension_placement(
    chain: Sequence[OnePointExtension],
) -> Tuple[Tuple[int, ...], int]:
    """Return the directions and the length of the partial placement and obstruction
    inferral that follow the one-point extension hint for a chain of steps
    (one_point_extension_chain): the steps' directions in their order, each once,
    and the length of the longest pattern of the first step's basis."""
    directions = tuple(dict.fromkeys(step.direction for step in chain))
    return directions, max(len(pattern) for pattern in chain[0].basis)


def _factor(steps: int) -> str:
    """Return "n (n - 1) ... (n - steps + 1)"."""
    return " ".join(["n"] + [f"(n - {index})" for index in range(1, steps)])


def _reduced_again(chain: Sequence[OnePointExtension]) -> str:
    """Return the sentence on the chain's steps after the first, for a chain of more
    than one step."""
    steps = len(chain)
    end = Av(Basis(*chain[-1].basis))
    later = [_EXTENSION_WORDS[step.direction].new_point for step in chain[1:]]
    if len(set(later)) == 1:
        by = f"by {later[0]}" + (" each time" if steps > 2 else "")
    else:
        by = "by " + ", then ".join(later)
    reduced = (
        f"{by}, and reduced again it is"
        if steps == 2
        else f"and reduced {steps - 1} more times, {by}, it is"
    )
    return (
        f"That class is such an extension too, {reduced} {end}: the class has "
        f"{_factor(steps)} times as many permutations of length n as {end} has of "
        f"length n - {steps}, for n >= {steps}."
    )


def _extension_message(chain: Sequence[OnePointExtension]) -> str:
    """Return the one-point extension hint's message for a chain of steps, which
    names the class the first step leaves once, as "that class" after."""
    steps = len(chain)
    words = _EXTENSION_WORDS[chain[0].direction]
    first, end = Av(Basis(*chain[0].basis)), Av(Basis(*chain[-1].basis))
    directions, length = extension_placement(chain)
    sentences = [
        f"The basis is every way of adding {words.new_point} to a pattern of the "
        f"basis of {first}, so the class is the permutations whose {words.point}, "
        "taken out, leaves a permutation of that class, and it has n times as many "
        "permutations of length n as that class has of length n - 1, for n >= 1."
    ]
    if steps > 1:
        sentences.append(_reduced_again(chain))
    applied = {1: "", 2: ", applied twice"}.get(steps, f", applied {steps} times")
    sentences.append(
        f"Search for {end} instead: its generating function G gives the class's by "
        f"F = 1 + x (x G)'{applied}."
    )
    placed = [_EXTENSION_WORDS[direction].placed for direction in directions]
    if len(placed) == 1:
        placements = f"a partial placement of the {placed[0]}"
        effect = (
            "which turns the class into that point and that class"
            if steps == 1
            else "which takes the points out one step at a time"
        )
    else:
        placements = (
            f"partial placements of the {', the '.join(placed[:-1])} and the "
            f"{placed[-1]}"
        )
        effect = "which take the points out one step at a time"
    names = ", ".join(DIR_REPR[direction] for direction in directions)
    if len(directions) == 1:
        names += ","
    sentences.append(
        f"Or add to the pack {placements}, with obstruction inferral to length "
        f"{length}, {effect} (TileScopePack.add_extension_placement(({names}), "
        f"{length}), or --extension-placement)."
    )
    return " ".join(sentences)


def _extension_hint(patterns: Basis) -> Optional[Hint]:
    """Return the one-point extension hint for a minimal basis that is one, and None
    for any other."""
    chain = _chain_of_minimal(set(patterns))
    if not chain:
        return None
    directions, length = extension_placement(chain)
    return Hint(
        "one-point extension",
        _extension_message(chain),
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
        >>> [hint.name for hint in hints_for(Perm.to_standard(word) for word in
        ...     ("1234", "1243", "1423", "4123"))]
        ['one-point extension']
    """
    patterns = Basis.from_iterable(basis)
    found: List[Hint] = []
    for hint in (_rotation_hint(patterns), _extension_hint(patterns)):
        if hint is not None:
            found.append(hint)
    return found

"""
The rotational cut strategy, for a 1x1 tiling whose class is closed under rotation.

The rotation of a permutation is here the cyclic shift that moves its first entry to
the end (Perm.shift_left), not the quarter turn of Perm.rotate. A class is closed
under rotation when its minimal basis is, that is when the basis is rotationally
stable. The n rotations of a permutation of
length n are distinct, and exactly one of them starts with its minimum. So the
class has n times as many permutations of length n as its min cut,
{p : 1 + p is in the class}, has of length n - 1. Exactly one of them ends with its
maximum, so the max cut, {p : p + 1 is in the class}, counts the class in the same
way, and it can be a different class. A class closed under the cyclic shift of the
values, which is a class whose inverse basis is rotationally stable, has the same
two cuts and is counted by them in the same way. A cut can be closed under
rotation again, and the strategy then applies to it too.

A rule to a cut sends the n rotations of 1 + p, or of p + 1, to p, so it is not a
bijection: RotationalCutRule tells them apart by their index among the rotations, as
FusionRule does for the objects a fused one splits into.

As generating functions, F(x) = x (x C(x))' for the nonempty permutations of the
class, where C(x) is the cut's, and F(x) = 1 + x (x C(x))' for the whole class.
"""

from collections import Counter
from itertools import islice
from typing import Callable, Iterable, Iterator, List, Optional, Tuple

import sympy

from comb_spec_searcher import Constructor, Strategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies.rule import NonBijectiveRule
from comb_spec_searcher.typing import (
    Parameters,
    RelianceProfile,
    SubObjects,
    SubRecs,
    SubSamplers,
    SubTerms,
    Terms,
)
from permuta import Perm
from permuta.perm_sets.basis import Basis
from permuta.permutils import inverse_set
from tilings import GriddedPerm, Tiling

__all__ = [
    "RotationalCutConstructor",
    "RotationalCutFactory",
    "RotationalCutRule",
    "RotationalCutStrategy",
    "is_rotationally_stable",
    "max_cut",
    "max_cut_differs",
    "min_cut",
    "rotation_kind",
]

CUTS = ("min", "max")
ROTATIONS = ("positions", "values")


def is_rotationally_stable(basis: Iterable[Perm]) -> bool:
    """Return True if the minimal basis of the class with the basis is closed under
    rotation, so that the class is closed under rotation too. A pattern that contains
    another of the basis is left out first.

    Examples:
        >>> is_rotationally_stable([Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((2, 0, 1))])
        True
        >>> is_rotationally_stable([Perm((0, 1, 2)), Perm((2, 3, 0, 1))])
        False
    """
    patterns = frozenset(Basis.from_iterable(basis))
    return all(pattern.shift_left() in patterns for pattern in patterns)


def _closed(basis: Iterable[Perm], rotation: str) -> bool:
    """Return True if the class with the basis is closed under the rotation of its
    positions, or of its values, which is the rotation of its inverse's positions."""
    if rotation == "positions":
        return is_rotationally_stable(basis)
    return is_rotationally_stable(inverse_set(basis))


def rotation_kind(basis: Iterable[Perm]) -> Optional[str]:
    """Return the kind of rotation the class with the basis is closed under:
    "positions", or "values" if it is closed only under the cyclic shift of its values
    (its inverse basis is rotationally stable), or None if neither.

    Examples:
        >>> rotation_kind([Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((2, 0, 1))])
        'positions'
        >>> rotation_kind([Perm((0, 1, 2)), Perm((2, 3, 0, 1))]) is None
        True
    """
    patterns = tuple(basis)
    return next(
        (rotation for rotation in ROTATIONS if _closed(patterns, rotation)), None
    )


def min_cut(basis: Iterable[Perm]) -> Tuple[Perm, ...]:
    """Return a basis, not necessarily minimal, of the permutations p for which
    1 + p is in the class with the basis.

    Examples:
        >>> min_cut([Perm((0, 1, 2, 3)), Perm((1, 2, 3, 0)), Perm((2, 3, 0, 1))])
        (Perm((0, 1, 2)), Perm((1, 2, 3, 0)), Perm((2, 3, 0, 1)))
    """
    return tuple(
        pattern.remove(0) if pattern and pattern[0] == 0 else pattern
        for pattern in basis
    )


def max_cut(basis: Iterable[Perm]) -> Tuple[Perm, ...]:
    """Return a basis, not necessarily minimal, of the permutations p for which
    p + 1 is in the class with the basis.

    Examples:
        >>> max_cut([Perm((0, 2, 1, 3)), Perm((2, 1, 3, 0)), Perm((1, 3, 0, 2))])
        (Perm((0, 2, 1)), Perm((2, 1, 3, 0)), Perm((1, 3, 0, 2)))
    """
    return tuple(
        pattern.remove() if pattern and pattern[-1] == len(pattern) - 1 else pattern
        for pattern in basis
    )


def max_cut_differs(basis: Iterable[Perm]) -> bool:
    """Return True if the max cut of the class with the basis is a different class
    from its min cut."""
    patterns = tuple(basis)
    return Basis.from_iterable(max_cut(patterns)) != Basis.from_iterable(
        min_cut(patterns)
    )


def _rotations(pattern: Perm, rotation: str) -> Iterator[Perm]:
    """Yield the n rotations of the permutation, of its positions or of its values,
    which are distinct."""
    length = len(pattern)
    for shift in range(length):
        if rotation == "positions":
            yield pattern.shift_left(shift)
        else:
            yield pattern.shift_up(shift)


def _basis(tiling: Tiling) -> Optional[Tuple[Perm, ...]]:
    """Return the basis of the tiling if the strategy can apply to it: a 1x1 tiling
    without assumptions, of a class with a pattern of length at least 2 in each
    basis element, with no requirement (the whole class) or with a point (its
    nonempty permutations). Otherwise return None."""
    if tiling.dimensions != (1, 1) or tiling.assumptions:
        return None
    if tiling.requirements and tiling.requirements != (
        (GriddedPerm.point_perm((0, 0)),),
    ):
        return None
    basis = tuple(obstruction.patt for obstruction in tiling.obstructions)
    if not basis or any(len(pattern) < 2 for pattern in basis):
        return None
    return basis


class RotationalCutConstructor(Constructor[Tiling, GriddedPerm]):
    """The parent has n times as many objects of size n as its one child has of size
    n - 1, for n >= 1. At size 0 it has the empty object if it contains it."""

    def __init__(self, contains_empty: bool) -> None:
        self.contains_empty = contains_empty

    def can_be_equivalent(self) -> bool:
        return False

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        x = sympy.var("x")
        return sympy.Eq(
            lhs_func, int(self.contains_empty) + x * sympy.diff(x * rhs_funcs[0], x)
        )

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        assert not parameters, "only implemented in one variable, namely 'n'"
        return ({"n": (n - 1,) if n > 0 else ()},)

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        if n == 0:
            return Counter({(): 1}) if self.contains_empty else Counter()
        return Counter(
            {param: n * value for param, value in subterms[0](n - 1).items()}
        )

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[Tuple[Parameters, Tuple[List[Optional[GriddedPerm]], ...]]]:
        if n == 0:
            if self.contains_empty:
                yield (), ([None],)  # the empty object, which no child object gives
            return
        for param, objects in subobjs[0](n - 1).items():
            yield param, (objects,)

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        if n == 0:
            return (None,)
        return (subsamplers[0](n - 1, **parameters),)

    def equiv(
        self, other: Constructor, data: Optional[object] = None
    ) -> Tuple[bool, Optional[object]]:
        return (
            isinstance(other, RotationalCutConstructor)
            and other.contains_empty == self.contains_empty,
            None,
        )

    def __str__(self) -> str:
        return "n times the cut at n - 1"


class RotationalCutStrategy(Strategy[Tiling, GriddedPerm]):
    """The rule from a 1x1 tiling of a class closed under rotation, of its positions
    or of its values, to its min cut or its max cut: see the module's docstring."""

    def __init__(
        self,
        cut: str = "min",
        rotation: str = "positions",
        ignore_parent: bool = False,
        inferrable: bool = True,
        possibly_empty: bool = False,
        workable: bool = True,
    ) -> None:
        if cut not in CUTS:
            raise ValueError(f"cut must be one of {CUTS}")
        if rotation not in ROTATIONS:
            raise ValueError(f"rotation must be one of {ROTATIONS}")
        self.cut = cut
        self.rotation = rotation
        super().__init__(
            ignore_parent=ignore_parent,
            inferrable=inferrable,
            possibly_empty=possibly_empty,
            workable=workable,
        )

    def can_be_equivalent(self) -> bool:
        return False

    def __call__(
        self,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> "RotationalCutRule":
        if children is None:
            children = self.decomposition_function(comb_class)
        return RotationalCutRule(self, comb_class, children=children)

    def is_two_way(self, comb_class: Tiling) -> bool:
        return False

    def is_reversible(self, comb_class: Tiling) -> bool:
        return False

    def shifts(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[int, ...]:
        return (1,)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        basis = _basis(comb_class)
        if basis is None or not _closed(basis, self.rotation):
            raise StrategyDoesNotApply(
                f"Not a 1x1 tiling of a class closed under rotation of {self.rotation}"
            )
        cut = min_cut(basis) if self.cut == "min" else max_cut(basis)
        return (Tiling.from_perms(cut),)

    def formal_step(self) -> str:
        return f"the {self.cut} cut of a class closed under rotation ({self.rotation})"

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> RotationalCutConstructor:
        if children is None:  # raises StrategyDoesNotApply where the cut does not apply
            self.decomposition_function(comb_class)
        return RotationalCutConstructor(contains_empty=not comb_class.requirements)

    def reverse_constructor(
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        raise NotImplementedError

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        """Yield the n rotations of 1 + p, for the min cut, or of p + 1, for the max
        cut, where p is the child's object."""
        (child_object,) = objs
        if child_object is None:
            yield GriddedPerm.empty_perm()
            return
        if self.cut == "min":
            pattern = Perm((0,) + tuple(value + 1 for value in child_object.patt))
        else:
            pattern = Perm(tuple(child_object.patt) + (len(child_object.patt),))
        for rotated in _rotations(pattern, self.rotation):
            yield GriddedPerm.single_cell(rotated, (0, 0))

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        """Return the cut of the one rotation of the object that starts with its
        minimum, for the min cut, or that ends with its maximum, for the max cut."""
        pattern = obj.patt
        if not pattern:
            return (None,)
        for rotated in _rotations(pattern, self.rotation):
            if self.cut == "min" and rotated[0] == 0:
                return (GriddedPerm.single_cell(Perm.to_standard(rotated[1:]), (0, 0)),)
            if self.cut == "max" and rotated[-1] == len(rotated) - 1:
                return (
                    GriddedPerm.single_cell(Perm.to_standard(rotated[:-1]), (0, 0)),
                )
        raise ValueError(f"{obj} has no rotation with the {self.cut} cut")

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(cut={self.cut!r}, "
            f"rotation={self.rotation!r}, ignore_parent={self.ignore_parent}, "
            f"inferrable={self.inferrable}, possibly_empty={self.possibly_empty}, "
            f"workable={self.workable})"
        )

    def to_jsonable(self) -> dict:
        jsonable = super().to_jsonable()
        jsonable["cut"] = self.cut
        jsonable["rotation"] = self.rotation
        return jsonable

    @classmethod
    def from_dict(cls, d: dict) -> "RotationalCutStrategy":
        return cls(**d)


class RotationalCutRule(NonBijectiveRule[Tiling, GriddedPerm]):
    """The rule of a rotational cut. Its forward map sends the n rotations of 1 + p,
    or of p + 1, to p, so an object is told apart from the other rotations by its
    index among those that the backward map yields, in their fixed order."""

    def _forward_order(
        self,
        obj: GriddedPerm,
        image: Tuple[Optional[GriddedPerm], ...],
        data: Optional[object] = None,
    ) -> int:
        return next(
            index
            for index, rotated in enumerate(self.backward_map(image))
            if rotated == obj
        )

    def _backward_order_item(
        self,
        idx: int,
        objs: Tuple[Optional[GriddedPerm], ...],
        data: Optional[object] = None,
    ) -> GriddedPerm:
        return next(islice(self.backward_map(objs), idx, None))


class RotationalCutFactory(StrategyFactory[Tiling]):
    """Yield the rotational cut strategies for a 1x1 tiling of a class closed under
    rotation, of its positions or of its values: its min cut, and its max cut when
    that is a different class."""

    def __call__(self, comb_class: Tiling) -> Iterator[RotationalCutStrategy]:
        basis = _basis(comb_class)
        if basis is None:
            return
        rotation = rotation_kind(basis)
        if rotation is None:
            return
        yield RotationalCutStrategy("min", rotation)
        if max_cut_differs(basis):
            yield RotationalCutStrategy("max", rotation)

    def __str__(self) -> str:
        return "rotational cuts"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    @classmethod
    def from_dict(cls, d: dict) -> "RotationalCutFactory":
        assert not d
        return cls()

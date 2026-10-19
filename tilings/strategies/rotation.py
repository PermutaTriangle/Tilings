"""
The rotational cut strategy, for a 1x1 tiling whose class is closed under rotation.

The rotation of a permutation is the cyclic shift that moves its first entry to the
end (Perm.shift_left). A class is closed under rotation when its basis is, that
is when the basis is rotationally stable. The n rotations of a permutation of
length n are distinct, and exactly one of them starts with its minimum. So the
class has n times as many permutations of length n as its min cut,
{p : 1 + p is in the class}, has of length n - 1. Exactly one of them ends with its
maximum, so the max cut, {p : p + 1 is in the class}, counts the class in the same
way, and it can be a different class. A class closed under the cyclic shift of the
values, which is a class whose inverse basis is rotationally stable, has the same
two cuts and is counted by them in the same way. A cut can be closed under
rotation again, and the strategy then applies to it too.

As generating functions, F(x) = x (x C(x))' for the nonempty permutations of the
class, where C(x) is the cut's, and F(x) = 1 + x (x C(x))' for the whole class.
"""

from collections import Counter
from typing import Callable, Iterable, Iterator, List, Optional, Tuple

import sympy

from comb_spec_searcher import Constructor, Strategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
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
from tilings import GriddedPerm, Tiling

__all__ = [
    "RotationalCutConstructor",
    "RotationalCutFactory",
    "RotationalCutStrategy",
    "is_rotationally_stable",
    "max_cut",
    "min_cut",
    "rotation_of",
]

CUTS = ("min", "max")
ROTATIONS = ("positions", "values")


def is_rotationally_stable(basis: Iterable[Perm]) -> bool:
    """Return True if the basis is closed under rotation. The class it is the basis
    of is then closed under rotation too.

    Examples:
        >>> is_rotationally_stable([Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((2, 0, 1))])
        True
        >>> is_rotationally_stable([Perm((0, 1, 2)), Perm((2, 3, 0, 1))])
        False
    """
    patts = frozenset(basis)
    return all(patt.shift_left() in patts for patt in patts)


def rotation_of(basis: Iterable[Perm]) -> Optional[str]:
    """Return "positions" if the class with the basis is closed under rotation,
    "values" if it is not but is closed under the cyclic shift of the values (its
    inverse basis is rotationally stable), and None otherwise."""
    patts = tuple(basis)
    if is_rotationally_stable(patts):
        return "positions"
    if is_rotationally_stable(patt.inverse() for patt in patts):
        return "values"
    return None


def min_cut(basis: Iterable[Perm]) -> Tuple[Perm, ...]:
    """Return a basis, not necessarily minimal, of the permutations p for which
    1 + p is in the class with the basis.

    Examples:
        >>> min_cut([Perm((0, 1, 2, 3)), Perm((1, 2, 3, 0)), Perm((2, 3, 0, 1))])
        (Perm((0, 1, 2)), Perm((1, 2, 3, 0)), Perm((2, 3, 0, 1)))
    """
    return tuple(
        Perm.to_standard(patt[1:]) if patt and patt[0] == 0 else patt for patt in basis
    )


def max_cut(basis: Iterable[Perm]) -> Tuple[Perm, ...]:
    """Return a basis, not necessarily minimal, of the permutations p for which
    p + 1 is in the class with the basis.

    Examples:
        >>> max_cut([Perm((0, 2, 1, 3)), Perm((2, 1, 3, 0)), Perm((1, 3, 0, 2))])
        (Perm((0, 2, 1)), Perm((2, 1, 3, 0)), Perm((1, 3, 0, 2)))
    """
    return tuple(
        Perm.to_standard(patt[:-1]) if patt and patt[-1] == len(patt) - 1 else patt
        for patt in basis
    )


def _rotations(patt: Perm, rotation: str) -> Iterator[Perm]:
    """Yield the n rotations of the permutation, of its positions or of its values,
    which are distinct."""
    n = len(patt)
    for k in range(n):
        if rotation == "positions":
            yield patt.shift_left(k)
        else:
            yield Perm(tuple((val + k) % n for val in patt))


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
    basis = tuple(ob.patt for ob in tiling.obstructions)
    if not basis or any(len(patt) < 2 for patt in basis):
        return None
    return basis


def _closed(basis: Tuple[Perm, ...], rotation: str) -> bool:
    if rotation == "positions":
        return is_rotationally_stable(basis)
    return is_rotationally_stable(patt.inverse() for patt in basis)


class RotationalCutConstructor(Constructor[Tiling, GriddedPerm]):
    """The parent has n times as many objects of size n as its one child has of size
    n - 1, for n >= 1. At size 0 it has the empty object if it contains it."""

    def __init__(self, contains_empty: bool):
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
        for param, objs in subobjs[0](n - 1).items():
            yield param, (objs,)

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
    ):
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
        if children is None:
            children = self.decomposition_function(comb_class)
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
        (obj,) = objs
        if obj is None:
            yield GriddedPerm.empty_perm()
            return
        if self.cut == "min":
            patt = Perm((0,) + tuple(val + 1 for val in obj.patt))
        else:
            patt = Perm(tuple(obj.patt) + (len(obj.patt),))
        for rotated in _rotations(patt, self.rotation):
            yield GriddedPerm.single_cell(rotated, (0, 0))

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        """Return the cut of the one rotation of the object that starts with its
        minimum, for the min cut, or that ends with its maximum, for the max cut."""
        patt = obj.patt
        if not patt:
            return (None,)
        for rotated in _rotations(patt, self.rotation):
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
        d = super().to_jsonable()
        d["cut"] = self.cut
        d["rotation"] = self.rotation
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RotationalCutStrategy":
        return cls(**d)


class RotationalCutFactory(StrategyFactory[Tiling]):
    """Yield the rotational cut strategies for a 1x1 tiling of a class closed under
    rotation, of its positions or of its values: its min cut, and its max cut when
    that is a different class."""

    def __call__(self, comb_class: Tiling) -> Iterator[RotationalCutStrategy]:
        basis = _basis(comb_class)
        if basis is None:
            return
        rotation = rotation_of(basis)
        if rotation is None:
            return
        yield RotationalCutStrategy("min", rotation)
        if Tiling.from_perms(max_cut(basis)) != Tiling.from_perms(min_cut(basis)):
            yield RotationalCutStrategy("max", rotation)

    def __str__(self) -> str:
        return "rotational cuts"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    @classmethod
    def from_dict(cls, d: dict) -> "RotationalCutFactory":
        assert not d
        return cls()

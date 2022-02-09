import abc
from functools import partial
from itertools import chain, combinations
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple, cast

from comb_spec_searcher import StrategyFactory, SymmetryStrategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from permuta import Perm
from tilings import GriddedPerm, Tiling

__all__ = ("SymmetriesFactory",)


class TilingSymmetryStrategy(SymmetryStrategy[Tiling, GriddedPerm]):
    @abc.abstractmethod
    def gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        pass

    @abc.abstractmethod
    def inverse_gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        pass

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, ...]:
        return (
            Tiling(
                tuple(
                    map(partial(self.gp_transform, comb_class), comb_class.obstructions)
                ),
                tuple(
                    tuple(map(partial(self.gp_transform, comb_class), req))
                    for req in comb_class.requirements
                ),
                tuple(
                    ass.__class__(map(partial(self.gp_transform, comb_class), ass.gps))
                    for ass in comb_class.assumptions
                ),
                remove_empty_rows_and_cols=False,
                derive_empty=False,
                simplify=False,
            ),
        )

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if not comb_class.extra_parameters:
            return super().extra_parameters(comb_class, children)
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        child = children[0]
        mapped_assumptions = tuple(
            ass.__class__(tuple(self.gp_transform(comb_class, gp) for gp in ass.gps))
            for ass in comb_class.assumptions
        )
        return (
            {
                comb_class.get_assumption_parameter(
                    assumption
                ): child.get_assumption_parameter(mapped_assumption)
                for assumption, mapped_assumption in zip(
                    comb_class.assumptions, mapped_assumptions
                )
            },
        )

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        """This method will enable us to generate objects, and sample."""
        yield self.inverse_gp_transform(comb_class, cast(GriddedPerm, objs[0]))

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm]:
        """This function will enable us to have a quick membership test."""
        return (self.gp_transform(comb_class, obj),)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d: dict) -> "TilingSymmetryStrategy":
        return cls()


class TilingReverse(TilingSymmetryStrategy):
    """
    Flips the tiling on its vertical axis.
    """

    def gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        def reverse_cell(cell):
            return (tiling.dimensions[0] - cell[0] - 1, cell[1])

        return gp.reverse(reverse_cell)

    def inverse_gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        return self.gp_transform(tiling, gp)

    @staticmethod
    def formal_step() -> str:
        return "reverse of the tiling"

    def __str__(self) -> str:
        return "reverse"


class TilingComplement(TilingSymmetryStrategy):
    """
    Flips the tiling over the horizontal axis.
    """

    def gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        def complement_cell(cell):
            return (cell[0], tiling.dimensions[1] - cell[1] - 1)

        return gp.complement(complement_cell)

    def inverse_gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        return self.gp_transform(tiling, gp)

    @staticmethod
    def formal_step() -> str:
        return "complement of the tiling"

    def __str__(self) -> str:
        return "complement"


class TilingInverse(TilingSymmetryStrategy):
    """
    Flips the tiling over the diagonal.
    """

    def gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        def inverse_cell(cell):
            return (cell[1], cell[0])

        return gp.inverse(inverse_cell)

    def inverse_gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        return self.gp_transform(tiling, gp)

    @staticmethod
    def formal_step() -> str:
        return "inverse of the tiling"

    def __str__(self) -> str:
        return "inverse"


class TilingAntidiagonal(TilingSymmetryStrategy):
    """
    Flips the tiling over the antidiagonal.
    """

    def gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        def antidiagonal_cell(cell):
            return (
                tiling.dimensions[1] - cell[1] - 1,
                tiling.dimensions[0] - cell[0] - 1,
            )

        return gp.antidiagonal(antidiagonal_cell)

    def inverse_gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        def antidiagonal_cell(cell):
            return (
                tiling.dimensions[0] - cell[1] - 1,
                tiling.dimensions[1] - cell[0] - 1,
            )

        return gp.antidiagonal(antidiagonal_cell)

    @staticmethod
    def formal_step() -> str:
        return "antidiagonal of the tiling"

    def __str__(self) -> str:
        return "antidiagonal"


class TilingRotate90(TilingSymmetryStrategy):
    """
    Rotate the tiling 90 degrees clockwise.
    """

    def gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        def rotate90_cell(cell):
            return (cell[1], tiling.dimensions[0] - cell[0] - 1)

        return gp.rotate90(rotate90_cell)

    def inverse_gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        def rotate270_cell(cell):
            return (tiling.dimensions[0] - cell[1] - 1, cell[0])

        return gp.rotate270(rotate270_cell)

    @staticmethod
    def formal_step() -> str:
        return "rotate the tiling 90 degrees clockwise"

    def __str__(self) -> str:
        return "rotate90"


class TilingRotate180(TilingSymmetryStrategy):
    """
    Rotate the tiling 180 degrees clockwise.
    """

    def gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        def rotate180_cell(cell):
            return (
                tiling.dimensions[0] - cell[0] - 1,
                tiling.dimensions[1] - cell[1] - 1,
            )

        return gp.rotate180(rotate180_cell)

    def inverse_gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        return self.gp_transform(tiling, gp)

    @staticmethod
    def formal_step() -> str:
        return "rotate the tiling 180 degrees clockwise"

    def __str__(self) -> str:
        return "rotate180"


class TilingRotate270(TilingSymmetryStrategy):
    """
    Rotate the tiling 270 degrees clockwise.
    """

    def gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        def rotate270_cell(cell):
            return (tiling.dimensions[1] - cell[1] - 1, cell[0])

        return gp.rotate270(rotate270_cell)

    def inverse_gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        def rotate90_cell(cell):
            return (cell[1], tiling.dimensions[1] - cell[0] - 1)

        return gp.rotate90(rotate90_cell)

    @staticmethod
    def formal_step() -> str:
        return "rotate the tiling 270 degrees clockwise"

    def __str__(self) -> str:
        return "rotate270"


class SymmetriesFactory(StrategyFactory[Tiling]):
    """
    Yield all symmetry strategies for a tiling.
    """

    def __call__(self, comb_class: Tiling) -> Iterator[TilingSymmetryStrategy]:
        def strategy(rotations: int, inverse: bool) -> TilingSymmetryStrategy:
            # pylint: disable=too-many-return-statements
            if rotations == 0:
                if inverse:
                    return TilingInverse()
            if rotations == 1:
                if inverse:
                    return TilingReverse()
                return TilingRotate90()
            if rotations == 2:
                if inverse:
                    return TilingAntidiagonal()
                return TilingRotate180()
            if rotations == 3:
                if inverse:
                    return TilingComplement()
                return TilingRotate270()

        symmetries = set([comb_class])
        for rotations in range(4):
            if comb_class not in symmetries:
                yield strategy(rotations, False)
            symmetries.add(comb_class)
            comb_class_inverse = comb_class.inverse()
            if comb_class_inverse not in symmetries:
                yield strategy(rotations, True)
            symmetries.add(comb_class_inverse)
            comb_class = comb_class.rotate90()
            if comb_class in symmetries:
                break

    def __str__(self) -> str:
        return "all symmetries"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d: dict) -> "SymmetriesFactory":
        return cls()


class JaysSymmetriesFactory(StrategyFactory[Tiling]):
    """
    Yield symmetry strategies such that all of the underlying patterns of
    obstructions of the symmetric tiling are subpatterns of the given basis.
    """

    def __init__(
        self,
        basis: Optional[Iterable[Perm]] = None,
    ):
        self._basis = tuple(basis) if basis is not None else tuple()
        assert all(
            isinstance(p, Perm) for p in self._basis
        ), "Element of the basis must be Perm"
        self.subpatterns: Set[Perm] = set(
            chain.from_iterable(self._subpatterns(p) for p in self._basis)
        )
        self.acceptablesubpatterns: List[Set[Perm]] = [
            set(p for p in self.subpatterns if p.rotate() in self.subpatterns),
            set(p for p in self.subpatterns if p.rotate(2) in self.subpatterns),
            set(p for p in self.subpatterns if p.rotate(3) in self.subpatterns),
            set(p for p in self.subpatterns if p.inverse() in self.subpatterns),
            set(p for p in self.subpatterns if p.reverse() in self.subpatterns),
            set(
                p for p in self.subpatterns if p.flip_antidiagonal() in self.subpatterns
            ),
            set(p for p in self.subpatterns if p.complement() in self.subpatterns),
        ]
        super().__init__()

    def __call__(self, tiling: Tiling) -> Iterator[TilingSymmetryStrategy]:
        underlying_patts = set(gp.patt for gp in tiling.obstructions)
        if all(p in self.acceptablesubpatterns[0] for p in underlying_patts):
            yield TilingRotate90()
        if all(p in self.acceptablesubpatterns[1] for p in underlying_patts):
            yield TilingRotate180()
        if all(p in self.acceptablesubpatterns[2] for p in underlying_patts):
            yield TilingRotate270()
        if all(p in self.acceptablesubpatterns[3] for p in underlying_patts):
            yield TilingInverse()
        if all(p in self.acceptablesubpatterns[4] for p in underlying_patts):
            yield TilingReverse()
        if all(p in self.acceptablesubpatterns[5] for p in underlying_patts):
            yield TilingAntidiagonal()
        if all(p in self.acceptablesubpatterns[6] for p in underlying_patts):
            yield TilingComplement()

    @staticmethod
    def _subpatterns(perm: Perm) -> Iterator[Perm]:
        for n in range(len(perm) + 1):
            for indices in combinations(range(len(perm)), n):
                yield Perm.to_standard([perm[i] for i in indices])

    def change_basis(
        self,
        basis: Iterable[Perm],
    ) -> "JaysSymmetriesFactory":
        """
        Return the version of the strategy with the given basis instead
        of the current one.
        """
        return self.__class__(tuple(basis))

    @property
    def basis(self) -> Tuple[Perm, ...]:
        return self._basis

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["basis"] = self._basis
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "JaysSymmetriesFactory":
        if "basis" in d and d["basis"] is not None:
            basis: Optional[List[Perm]] = [Perm(p) for p in d.pop("basis")]
        else:
            basis = d.pop("basis", None)
        return cls(basis=basis)

    def __str__(self) -> str:
        return "jays symmetries"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(basis={self._basis})"

import abc
from functools import partial
from typing import Dict, Iterator, Optional, Tuple, cast

from comb_spec_searcher import StrategyFactory, SymmetryStrategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from tilings import GriddedPerm, Tiling

__all__ = ("SymmetriesFactory",)


class TilingSymmetryStrategy(SymmetryStrategy[Tiling, GriddedPerm]):
    @abc.abstractmethod
    def gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        pass

    @abc.abstractmethod
    def inverse_gp_transform(self, tiling: Tiling, gp: GriddedPerm) -> GriddedPerm:
        pass

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, ...]:
        return (
            Tiling(
                tuple(map(partial(self.gp_transform, tiling), tiling.obstructions)),
                tuple(
                    tuple(map(partial(self.gp_transform, tiling), req))
                    for req in tiling.requirements
                ),
                tuple(
                    ass.__class__(map(partial(self.gp_transform, tiling), ass.gps))
                    for ass in tiling.assumptions
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
        tiling: Tiling,
        gps: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        """This method will enable us to generate objects, and sample. """
        yield self.inverse_gp_transform(tiling, cast(GriddedPerm, gps[0]))

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm]:
        """This function will enable us to have a quick membership test."""
        return (self.gp_transform(tiling, gp),)

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

    def __call__(
        self, comb_class: Tiling, **kwargs
    ) -> Iterator[TilingSymmetryStrategy]:
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

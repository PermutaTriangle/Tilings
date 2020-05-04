from functools import partial
from typing import Iterator, Optional, Tuple
import abc

from comb_spec_searcher import StrategyGenerator, SymmetryStrategy
from tilings import GriddedPerm, Tiling


__all__ = ("AllSymmetriesStrategy",)


class TilingSymmetryStrategy(SymmetryStrategy[Tiling]):
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
                remove_empty=False,
                derive_empty=False,
                minimize=False,
            ),
        )

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[GriddedPerm, ...],
        children: Optional[Tuple[GriddedPerm, ...]] = None,
    ) -> GriddedPerm:
        """This method will enable us to generate objects, and sample. """
        return self.inverse_gp_transform(tiling, gps[0])

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[GriddedPerm, ...]] = None,
    ) -> Tuple[GriddedPerm, ...]:
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

    def formal_step(self) -> str:
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

    def formal_step(self) -> str:
        return "complement of the tiing"

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

    def formal_step(self) -> str:
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
        return self.gp_transform(tiling, gp)

    def formal_step(self) -> str:
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

    def formal_step(self) -> str:
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

    def formal_step(self) -> str:
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

    def formal_step(self) -> str:
        return "rotate the tiling 270 degrees clockwise"

    def __str__(self) -> str:
        return "rotate270"


class AllSymmetriesStrategy(StrategyGenerator):
    """
    Yield all symmetry strategies for a tiling.
    """

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[TilingSymmetryStrategy]:
        def strategy(rotations: int, inverse: bool) -> TilingSymmetryStrategy:
            if rotations == 0:
                if inverse:
                    return TilingInverse()
            if rotations == 1:
                if inverse:
                    return TilingReverse()
                else:
                    return TilingRotate90()
            if rotations == 2:
                if inverse:
                    return TilingAntidiagonal()
                else:
                    return TilingRotate180()
            if rotations == 3:
                if inverse:
                    return TilingComplement()
                else:
                    return TilingRotate270()

        t = tiling
        symmetries = set([t])
        for rotations in range(4):
            if t not in symmetries:
                yield strategy(rotations, False)
            symmetries.add(t)
            if t not in symmetries:
                yield strategy(rotations, True)
            symmetries.add(t.inverse())
            t = t.rotate90()
            if t in symmetries:
                break

    def __str__(self) -> str:
        return "all symmetries"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d: dict) -> "AllSymmetriesStrategy":
        return cls()

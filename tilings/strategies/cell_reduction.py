"""The cell reduction strategy, the reduction of a single cell.

`ReductionStrategy` and `ReductionFactory` (`tilings.strategies.reduction`) reduce
any set of cells. These are the reductions of single cells, kept with their names
and encodings for the packs and specifications that use them.
"""

from typing import Tuple, cast

from .reduction import ReductionConstructor, ReductionFactory, ReductionStrategy

__all__ = ("CellReductionConstructor", "CellReductionStrategy", "CellReductionFactory")

Cell = Tuple[int, int]

CellReductionConstructor = ReductionConstructor


class CellReductionStrategy(ReductionStrategy):
    """A strategy that replaces the cell with an increasing or decreasing cell."""

    def __init__(
        self,
        cell: Cell,
        increasing: bool,
        tracked: bool = True,
        minimal: bool = True,
    ):
        self.cell = cast(Cell, tuple(cell))
        super().__init__((self.cell,), increasing, tracked, minimal)

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d.pop("cells")
        d["cell"] = self.cell
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "CellReductionStrategy":
        cell = cast(Cell, tuple(d.pop("cell")))
        tracked = d.pop("tracked")
        increasing = d.pop("increasing")
        # encoded before the choice existed: the cell kept and tracked as it was
        minimal = d.pop("minimal", False)
        assert not d
        return cls(cell, increasing, tracked, minimal)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(cell={self.cell!r}, "
            f"increasing={self.increasing!r}, tracked={self.tracked!r}, "
            f"minimal={self.minimal!r})"
        )


class CellReductionFactory(ReductionFactory):
    """The reductions of single cells: `ReductionFactory` with the region "cell"."""

    def __init__(self, tracked: bool, minimal: bool = True):
        super().__init__(tracked, "cell", None, minimal)

    def strategy(self, cells: Tuple[Cell, ...], increasing: bool) -> ReductionStrategy:
        (cell,) = cells
        return CellReductionStrategy(cell, increasing, self.tracked, self.minimal)

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.tracked})"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d.pop("region")
        d.pop("max_cells")
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "CellReductionFactory":
        return cls(d["tracked"], d.get("minimal", True))

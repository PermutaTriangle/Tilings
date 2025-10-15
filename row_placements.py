from typing import Iterator
from tilings.tilescope import TileScopePack
from tilings import GriddedPerm, Tiling, strategies


class MaxMinRowPlacementFactory(
    strategies.requirement_placement.AbstractRequirementPlacementFactory
):
    def __init__(self, **kwargs) -> None:
        super().__init__(include_empty=True, **kwargs)

    def req_indices_and_directions_to_place(
        self, tiling: Tiling
    ) -> Iterator[tuple[tuple[GriddedPerm, ...], tuple[int, ...], int]]:
        gps = tuple(GriddedPerm((0,), (cell,)) for cell in tiling.cells_in_row(0))
        indices = tuple(0 for _ in gps)
        yield gps, indices, 2

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "MinRowPlacementFactory":
        return cls(**d)


class MinRowPlacementFactory(MaxMinRowPlacementFactory):
    def req_indices_and_directions_to_place(
        self, tiling: Tiling
    ) -> Iterator[tuple[tuple[GriddedPerm, ...], tuple[int, ...], int]]:
        amp = tiling.active_cells - tiling.point_cells
        if not amp:
            i = 0
        else:
            i = next(iter(amp))[1]
        gps = tuple(GriddedPerm((0,), (cell,)) for cell in tiling.cells_in_row(i))
        indices = tuple(0 for _ in gps)
        yield gps, indices, 3

    def __str__(self) -> str:
        return "minimum row placements"

    @classmethod
    def from_dict(cls, d: dict) -> "MinRowPlacementFactory":
        return cls(**d)


class MaxRowPlacementFactory(MaxMinRowPlacementFactory):
    def req_indices_and_directions_to_place(
        self, tiling: Tiling
    ) -> Iterator[tuple[tuple[GriddedPerm, ...], tuple[int, ...], int]]:
        amp = tiling.active_cells - tiling.point_cells
        if not amp:
            i = 0
        else:
            i = next(iter(amp))[1]
        gps = tuple(GriddedPerm((0,), (cell,)) for cell in tiling.cells_in_row(i))
        indices = tuple(0 for _ in gps)
        yield gps, indices, 1

    def __str__(self) -> str:
        return "maximum row placements"

    @classmethod
    def from_dict(cls, d: dict) -> "MaxRowPlacementFactory":
        return cls(**d)


class LeftRightColPlacementFactory(
    strategies.requirement_placement.AbstractRequirementPlacementFactory
):
    def __init__(self, **kwargs) -> None:
        super().__init__(include_empty=True, **kwargs)

    def req_indices_and_directions_to_place(
        self, tiling: Tiling
    ) -> Iterator[tuple[tuple[GriddedPerm, ...], tuple[int, ...], int]]:
        amp = tiling.active_cells - tiling.point_cells
        if not amp:
            i = 0
        else:
            i = next(iter(amp))[0]
        gps = tuple(GriddedPerm((0,), (cell,)) for cell in tiling.cells_in_col(i))
        indices = tuple(0 for _ in gps)
        yield gps, indices, 2

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "LeftColPlacementFactory":
        return cls(**d)


class LeftColPlacementFactory(LeftRightColPlacementFactory):
    def req_indices_and_directions_to_place(
        self, tiling: Tiling
    ) -> Iterator[tuple[tuple[GriddedPerm, ...], tuple[int, ...], int]]:
        amp = tiling.active_cells - tiling.point_cells
        if not amp:
            i = 0
        else:
            i = min(cell[0] for cell in amp)
        gps = tuple(GriddedPerm((0,), (cell,)) for cell in tiling.cells_in_col(i))
        indices = tuple(0 for _ in gps)
        yield gps, indices, 2

    def __str__(self) -> str:
        return "leftmost column placements"

    @classmethod
    def from_dict(cls, d: dict) -> "LeftColPlacementFactory":
        return cls(**d)


class RightColPlacementFactory(LeftRightColPlacementFactory):
    def req_indices_and_directions_to_place(
        self, tiling: Tiling
    ) -> Iterator[tuple[tuple[GriddedPerm, ...], tuple[int, ...], int]]:
        amp = tiling.active_cells - tiling.point_cells
        if not amp:
            i = 0
        else:
            i = max(cell[0] for cell in amp)
        gps = tuple(GriddedPerm((0,), (cell,)) for cell in tiling.cells_in_col(i))
        indices = tuple(0 for _ in gps)
        yield gps, indices, 0

    def __str__(self) -> str:
        return "rightmost column placements"

    @classmethod
    def from_dict(cls, d: dict) -> "RightColPlacementFactory":
        return cls(**d)


max_row_placements = TileScopePack(
    [strategies.FactorFactory()],
    [
        strategies.RowColumnSeparationStrategy(),
    ],
    [[MaxRowPlacementFactory()]],
    [strategies.BasicVerificationStrategy()],
    name="max_row_placements",
)

min_row_placements = TileScopePack(
    [strategies.FactorFactory()],
    [
        strategies.RowColumnSeparationStrategy(),
    ],
    [[MinRowPlacementFactory()]],
    [strategies.BasicVerificationStrategy()],
    name="min_row_placements",
)

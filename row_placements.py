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
        gps = tuple(GriddedPerm((0,), (cell,)) for cell in tiling.cells_in_row(0))
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
        gps = tuple(
            GriddedPerm((0,), (cell,))
            for cell in tiling.cells_in_row(tiling.dimensions[1] - 1)
        )
        indices = tuple(0 for _ in gps)
        yield gps, indices, 1

    def __str__(self) -> str:
        return "maximum row placements"

    @classmethod
    def from_dict(cls, d: dict) -> "MaxRowPlacementFactory":
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

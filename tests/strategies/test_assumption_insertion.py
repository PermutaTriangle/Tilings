from tilings import GriddedPerm, Tiling
from tilings.assumptions import ComponentAssumption, TrackingAssumption
from tilings.strategies.assumption_insertion import AddAssumptionsStrategy


def test_component_not_reversible():
    ass = ComponentAssumption.from_cells([(0, 0)])
    tiling = Tiling.from_string("123")
    assert not AddAssumptionsStrategy([ass]).is_reversible(tiling)


def test_cover_all_cells_reversible():
    tiling = Tiling(
        [
            GriddedPerm.single_cell((0, 1), (0, 0)),
            GriddedPerm.single_cell((0, 1), (0, 1)),
        ]
    )
    ass1 = TrackingAssumption.from_cells([(0, 0), (0, 1)])
    ass2 = TrackingAssumption.from_cells([(0, 0)])
    assert AddAssumptionsStrategy([ass1]).is_reversible(tiling)
    assert not AddAssumptionsStrategy([ass2]).is_reversible(tiling)
    assert not AddAssumptionsStrategy([ass1, ass2]).is_reversible(tiling)

from tilings.algorithms import (EmptyCellInferral, ObstructionTransitivity,
                                RowColSeparation, SubobstructionInferral)


def obstruction_transitivity(tiling, **kwargs):
    """
    The obstruction transitivity strategy.

    The obstruction transitivity considers all length 2 obstructions with both
    points in the same row or some column. By considering these length 2
    obstructions in similar manner as the row and column separation, as
    inequality relations. When the obstructions use a positive cell,
    transitivity applies, i.e. if a < b < c and b is positive, then a < c.
    """
    obs_trans = ObstructionTransitivity(tiling)
    return obs_trans.rule()


def row_and_column_separation(tiling, **kwargs):
    """
    An inferral function that tries to separate cells in rows and columns.
    """
    rcs = RowColSeparation(tiling)
    return rcs.rule()


def empty_cell_inferral(tiling, **kwargs):
    """
    The empty cell inferral strategy.

    The strategy considers each active but non-positive cell and inserts a
    point requirement. If the resulting tiling is empty, then a point
    obstruction can be added into the cell, i.e. the cell is empty."""
    eci = EmptyCellInferral(tiling)
    return eci.rule()


def subobstruction_inferral(tiling, **kwargs):
    """
    Return tiling created by adding all subobstructions which can be
    added.
    """
    soi = SubobstructionInferral(tiling)
    return soi.rule()

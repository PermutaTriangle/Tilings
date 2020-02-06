from itertools import product
from typing import Iterable, List, Optional

from comb_spec_searcher import BatchRule, Rule
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST
from tilings import Tiling
from tilings.algorithms import (CellInsertion, ColInsertion, CrossingInsertion,
                                FactorInsertion, RequirementCorroboration,
                                RequirementExtension, RequirementPlacement,
                                RowInsertion)


# -------------------------------------
#   Requirement Insertion             |
# -------------------------------------
def all_cell_insertions(tiling: Tiling, maxreqlen: int = 1, extra_basis:
                        Optional[List[Perm]] = None,
                        ignore_parent: bool = False,
                        **kwargs) -> Iterable[Rule]:
    """
    The cell insertion strategy.

    The cell insertion strategy is a batch strategy that considers each active
    cells, excluding positive cells. For each of these cells, the strategy
    considers all patterns (up to some maximum length given by maxreqlen, and
    some maximum number given by maxreqnum) and returns two tilings; one which
    requires the pattern in the cell and one where the pattern is obstructed.
    """
    yield from CellInsertion(tiling, maxreqlen,
                             extra_basis).rules(ignore_parent)


def root_requirement_insertion(tiling, **kwargs) -> Iterable[Rule]:
    """
    The cell insertion strategy performed only on 1 by 1 tilings.
    """
    if tiling.dimensions != (1, 1) or tiling.requirements:
        return
    yield from all_cell_insertions(tiling, **kwargs)


def all_point_insertions(tiling, **kwargs) -> Iterable[Rule]:
    """
    The cell insertion strategy using only points.
    """
    yield from all_cell_insertions(tiling, maxreqlen=1, **kwargs)


def all_requirement_extensions(tiling: Tiling, maxreqlen: int = 2,
                               extra_basis: Optional[List[Perm]] = None,
                               ignore_parent: bool = False,
                               **kwargs) -> Iterable[Rule]:
    """
    Insert longer requirements in to cells which contain a requirement
    """
    yield from RequirementExtension(tiling, maxreqlen,
                                    extra_basis).rules(ignore_parent)


def all_row_insertions(tiling: Tiling, ignore_parent: bool = False,
                       **kwargs) -> Iterable[Rule]:
    """Insert a list requirement into every possibly empty row."""
    yield from RowInsertion(tiling).rules(ignore_parent)


def all_col_insertions(tiling, ignore_parent: bool = False,
                       **kwargs) -> Iterable[Rule]:
    """Insert a list requirement into every possibly empty column."""
    yield from ColInsertion(tiling).rules(ignore_parent)


def all_requirement_insertions(tiling: Tiling, maxreqlen: int = 1,
                               extra_basis: Optional[List[Perm]] = None,
                               ignore_parent: bool = False,
                               **kwargs) -> Iterable[Rule]:
    """
    Insert all possible requirements the obstruction allows if the tiling does
    not have requirements.
    """
    if tiling.requirements:
        return
    yield from CrossingInsertion(tiling, maxreqlen,
                                 extra_basis).rules(ignore_parent)


def all_factor_insertions(tiling: Tiling, ignore_parent: bool = False,
                          **kwargs) -> Iterable[Rule]:
    """
    Insert all proper factor of the requirement or obstructions on the tiling.
    """
    yield from FactorInsertion(tiling).rules(ignore_parent)


def requirement_corroboration(tiling: Tiling, ignore_parent: bool = True,
                              **kwargs) -> Iterable[Rule]:
    """
    The requirement corroboration strategy.

    The requirement corroboration strategy is a batch strategy that considers
    each requirement of each requirement list. For each of these requirements,
    the strategy returns two tilings; one where the requirement has been turned
    into an obstruction and another where the requirement has been singled out
    and a new requirement list added with only the requirement. This new
    requirement list contains only the singled out requirement.

    This implements the notion of partitioning the set of gridded permutations
    into those that satisfy this requirement and those that avoid it. Those
    that avoid the requirement, must therefore satisfy another requirement from
    the same list and hence the requirement list must be of length at least 2.
    """
    yield from RequirementCorroboration(tiling).rules(ignore_parent)


# -------------------------------------
#   Row and column placement          |
# -------------------------------------
def row_placements(tiling, **kwargs):
    yield from RequirementPlacement(tiling).all_row_placement_rules()


def col_placements(tiling, **kwargs):
    yield from RequirementPlacement(tiling).all_col_placement_rules()


def row_and_col_placements(tiling, **kwargs):
    req_placements = RequirementPlacement(tiling)
    yield from req_placements.all_row_placement_rules()
    yield from req_placements.all_col_placement_rules()


def partial_row_placements(tiling, **kwargs):
    req_placements = (RequirementPlacement(tiling, own_row=False),
                      RequirementPlacement(tiling, own_col=False))
    for req_placement in req_placements:
        yield from req_placement.all_row_placement_rules()


def partial_col_placements(tiling, **kwargs):
    req_placements = (RequirementPlacement(tiling, own_row=False),
                      RequirementPlacement(tiling, own_col=False))
    for req_placement in req_placements:
        yield from req_placement.all_col_placement_rules()


def partial_row_and_col_placements(tiling, **kwargs):
    req_placements = (RequirementPlacement(tiling, own_row=False),
                      RequirementPlacement(tiling, own_col=False))
    for req_placement in req_placements:
        yield from req_placement.all_row_placement_rules()
        yield from req_placement.all_col_placement_rules()

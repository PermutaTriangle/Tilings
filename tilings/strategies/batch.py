from typing import Iterable, Iterator, List, Optional

from comb_spec_searcher import Rule
from permuta import Perm
from tilings import Tiling
from tilings.algorithms import (CellInsertion, ColInsertion, CrossingInsertion,
                                FactorInsertion, RequirementCorroboration,
                                RequirementExtension, RequirementPlacement,
                                RowInsertion)
from tilings.strategies.abstract_strategy import Strategy

# -------------------------------------
#   Requirement Insertion             |
# -------------------------------------


class AllCellInsertionStrategy(Strategy):
    """
    The cell insertion strategy.

    The cell insertion strategy is a batch strategy that considers each active
    cells, excluding positive cells. For each of these cells, the strategy
    considers all patterns (up to some maximum length given by maxreqlen, and
    some maximum number given by maxreqnum) and returns two tilings; one which
    requires the pattern in the cell and one where the pattern is obstructed.
    """
    def __init__(self, maxreqlen: int = 1,
                 extra_basis: Optional[List[Perm]] = None,
                 ignore_parent: bool = False,
                 ) -> None:
        self.maxreqlen = maxreqlen
        self.extra_basis = extra_basis
        self.ignore_parent = ignore_parent

    def __call__(self, tiling: Tiling) -> Iterator[Rule]:
        yield from (CellInsertion(tiling, self.maxreqlen, self.extra_basis)
                    .rules(self.ignore_parent))

    def __str__(self) -> str:
        if self.extra_basis is not None:
            return ('restricted cell insertion up to '
                    'length {}'.format(self.maxreqlen))
        return 'cell insertion up to length {}'.format(self.maxreqlen)

    def __repr__(self) -> str:
        return ('AllCellInsertionStrategy(maxreqlen={}, extra_basis={}, '
                'ignore_parent={})'.format(self.maxreqlen, self.extra_basis,
                                           self.ignore_parent))

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d['maxreqlen'] = self.maxreqlen
        d['extra_basis'] = self.extra_basis
        d['ignore_parent'] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'AllCellInsertionStrategy':
        return cls(
            d['maxreqlen'],
            [Perm(p) for p in d['extra_basis']],
            d['ignore_parent'],
        )


class RootInsertionStrategy(AllCellInsertionStrategy):
    """
    The cell insertion strategy performed only on 1 by 1 tilings.
    """
    def __call__(self, tiling: Tiling) -> Iterator[Rule]:
        if tiling.dimensions != (1, 1) or tiling.requirements:
            return
        yield from (CellInsertion(tiling, self.maxreqlen, self.extra_basis)
                    .rules(self.ignore_parent))

    def __str__(self) -> str:
        if self.extra_basis is None:
            return 'root insertion up to length {}'.format(self.maxreqlen)
        return ('restricted root insertion up to '
                'length {}'.format(self.maxreqlen))

    def __repr__(self) -> str:
        return ('RootInsertionStrategy(maxreqlen={}, extra_basis={}, '
                'ignore_parent={})'.format(self.maxreqlen, self.extra_basis,
                                           self.ignore_parent))


class AllPointInsertionStrategy(Strategy):
    def __init__(self, ignore_parent: bool = False) -> None:
        self.ignore_parent = ignore_parent

    def __call__(self, tiling: Tiling) -> Iterator[Rule]:
        yield from (CellInsertion(tiling, maxreqlen=1, extra_basis=[])
                    .rules(self.ignore_parent))

    def __str__(self) -> str:
        return 'point insertion'

    def __repr__(self) -> str:
        return ('AllPointInsertionStrategy(ignore_parent={})'
                .format(self.ignore_parent))

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d['ignore_parent'] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'AllPointInsertionStrategy':
        return cls(**d)


class AllRequirementExtensionStrategy(Strategy):
    """
    Insert longer requirements in to cells which contain a requirement
    """
    def __init__(self, maxreqlen: int = 2,
                 extra_basis: Optional[List[Perm]] = None,
                 ignore_parent: bool = False,
                 ) -> None:
        self.maxreqlen = maxreqlen
        self.extra_basis = extra_basis
        self.ignore_parent = ignore_parent

    def __call__(self, tiling: Tiling) -> Iterator[Rule]:
        yield from (
            RequirementExtension(tiling, self.maxreqlen, self.extra_basis)
            .rules(self.ignore_parent)
        )

    def __str__(self) -> str:
        if self.extra_basis is not None:
            return ('restricted requirement extension up to '
                    'length {}'.format(self.maxreqlen))
        return ('requirement extension insertion up to '
                'length {}'.format(self.maxreqlen))

    def __repr__(self) -> str:
        return ('AllRequirementExtensionStrategy(maxreqlen={}, extra_basis={},'
                ' ignore_parent={})'.format(self.maxreqlen, self.extra_basis,
                                            self.ignore_parent))

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d['maxreqlen'] = self.maxreqlen
        d['extra_basis'] = self.extra_basis
        d['ignore_parent'] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'AllRequirementExtensionStrategy':
        return cls(
            d['maxreqlen'],
            [Perm(p) for p in d['extra_basis']],
            d['ignore_parent'],
        )


class AllRowInsertionStrategy(Strategy):
    """Insert a list requirement into every possibly empty row."""
    def __init__(self, ignore_parent: bool = False) -> None:
        self.ignore_parent = ignore_parent

    def __call__(self, tiling: Tiling) -> Iterable[Rule]:
        yield from RowInsertion(tiling).rules(self.ignore_parent)

    def __str__(self) -> str:
        return 'row insertion'

    def __repr__(self) -> str:
        return 'AllRowInsertionStrategy(ignore_parent={})'.format(
            self.ignore_parent)

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d['ignore_parent'] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'AllRowInsertionStrategy':
        return cls(**d)


class AllColInsertionStrategy(Strategy):
    """Insert a list requirement into every possibly empty row."""
    def __init__(self, ignore_parent: bool = False) -> None:
        self.ignore_parent = ignore_parent

    def __call__(self, tiling: Tiling) -> Iterable[Rule]:
        yield from ColInsertion(tiling).rules(self.ignore_parent)

    def __str__(self) -> str:
        return 'column insertion'

    def __repr__(self) -> str:
        return 'AllColInsertionStrategy(ignore_parent={})'.format(
            self.ignore_parent)

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d['ignore_parent'] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'AllColInsertionStrategy':
        return cls(**d)


class AllRequirementInsertionStrategy(Strategy):
    """
    Insert all possible requirements the obstruction allows if the tiling does
    not have requirements.
    """
    def __init__(self, maxreqlen: int = 1,
                 extra_basis: Optional[List[Perm]] = None,
                 ignore_parent: bool = False,
                 ) -> None:
        self.maxreqlen = maxreqlen
        self.extra_basis = extra_basis
        self.ignore_parent = ignore_parent

    def __call__(self, tiling: Tiling) -> Iterator[Rule]:
        if tiling.requirements:
            return
        yield from (CrossingInsertion(tiling, self.maxreqlen, self.extra_basis)
                    .rules(self.ignore_parent))

    def __str__(self) -> str:
        if self.extra_basis is not None:
            return ('restricted requirement insertion up to '
                    'length {}'.format(self.maxreqlen))
        return ('requirement insertion up to '
                'length {}'.format(self.maxreqlen))

    def __repr__(self) -> str:
        return ('AllRequirementExtensionStrategy(maxreqlen={}, extra_basis={},'
                ' ignore_parent={})'.format(self.maxreqlen, self.extra_basis,
                                            self.ignore_parent))

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d['maxreqlen'] = self.maxreqlen
        d['extra_basis'] = self.extra_basis
        d['ignore_parent'] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'AllRequirementInsertionStrategy':
        return cls(
            d['mare glen'],
            [Perm(p) for p in d['extra_basis']],
            d['ignore_parent'],
        )


class AllFactorInsertionStrategy(Strategy):
    """
    Insert all proper factor of the requirement or obstructions on the tiling.
    """
    def __init__(self, ignore_parent: bool = True) -> None:
        self.ignore_parent = ignore_parent

    def __call__(self, tiling: Tiling) -> Iterator[Rule]:
        yield from FactorInsertion(tiling).rules(self.ignore_parent)

    def __str__(self) -> str:
        return 'all factor insertion'

    def __repr__(self) -> str:
        return 'AllFactorInsertionStrategy(ignore_parent={})'.format(
            self.ignore_parent)

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d['ignore_parent'] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class RequirementCorroborationStrategy(Strategy):
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
    def __init__(self, ignore_parent: bool = True):
        self.ignore_parent = ignore_parent

    def __call__(self, tiling: Tiling) -> Iterator[Rule]:
        yield from (RequirementCorroboration(tiling)
                    .rules(self.ignore_parent))

    def __str__(self) -> str:
        return 'requirement corroboration'

    def __repr__(self) -> str:
        return ('RequirementCorroborationStrategy(ignore_parent={})'
                .format(self.ignore_parent))

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d['ignore_parent'] = self.ignore_parent

    @classmethod
    def from_dict(cls, d: dict) -> 'RequirementCorroborationStrategy':
        return cls(**d)


# -------------------------------------
#   Row and column placement          |
# -------------------------------------

class RowAndColumnPlacementStrategy(Strategy):
    def __init__(self, place_row: bool, place_col: bool,
                 partial: bool = False) -> None:
        assert place_col or place_row, 'Must place column or row'
        self.place_row = place_row
        self.place_col = place_col
        self.partial = partial

    def __call__(self, tiling: Tiling) -> Iterator[Rule]:
        if self.partial:
            req_placements = [RequirementPlacement(tiling, own_row=False),
                              RequirementPlacement(tiling, own_col=False)]
        else:
            req_placements = [RequirementPlacement(tiling)]
        for req_placement in req_placements:
            if self.place_row:
                yield from req_placement.all_row_placement_rules()
            if self.place_col:
                yield from req_placement.all_col_placement_rules()

    def __str__(self) -> str:
        s = '{} placement'
        if self.place_col and self.place_col:
            s.format('row and column')
        elif self.place_row:
            s.format('row')
        else:
            s.format('column')
        if self.partial:
            s = ' '.join(['partial', s])
        return s

    def __repr__(self) -> str:
        return ('RowAndColumnPlacementStrategy(place_row={}, '
                'place_col={}, partial={})'.format(self.place_row,
                                                   self.place_col,
                                                   self.partial))

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d['place_row'] = self.place_row
        d['place_col'] = self.place_col
        d['partial'] = self.partial
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'RowAndColumnPlacementStrategy':
        return cls(*d)


class AllPlacementsStrategy(Strategy):
    def __call__(self, tiling: Tiling) -> Iterator[Rule]:
        req_placements = (RequirementPlacement(tiling),
                          RequirementPlacement(tiling, own_row=False),
                          RequirementPlacement(tiling, own_col=False))
        for req_placement in req_placements:
            yield from req_placement.all_point_placement_rules()
            yield from req_placement.all_requirement_placement_rules()
            yield from req_placement.all_col_placement_rules()
            yield from req_placement.all_row_placement_rules()

    def __str__(self) -> str:
        return 'all placements'

    def __repr__(self) -> str:
        return 'AllPlacementsStrategy()'

    @classmethod
    def from_dict(cls, d: dict) -> 'AllPlacementsStrategy':
        return AllPlacementsStrategy()

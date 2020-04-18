from typing import Iterator, List, Optional

from comb_spec_searcher import Strategy
from permuta import Av, Perm
from tilings import Tiling
from tilings.algorithms import (
    CellInsertion,
    CrossingInsertion,
    FactorInsertion,
    RequirementCorroboration,
    RequirementExtension,
    RequirementPlacement,
)

__all__ = [
    "AllCellInsertionStrategy",
    "RootInsertionStrategy",
    "AllRequirementExtensionStrategy",
    "AllRequirementInsertionStrategy",
    "AllFactorInsertionStrategy",
    "RequirementCorroborationStrategy",
    "RowAndColumnPlacementStrategy",
    "AllPlacementsStrategy",
]


class AllCellInsertionStrategy(Strategy):
    """
    The cell insertion strategy.

    The cell insertion strategy is a batch strategy that considers each active
    cells. For each of these cells, the strategy
    considers all patterns (up to some maximum length given by `maxreqlen`)
    and returns two tilings; one which requires the pattern in the cell and
    one where the pattern is obstructed.
    """

    def __init__(
        self,
        maxreqlen: int = 1,
        extra_basis: Optional[List[Perm]] = None,
        ignore_parent: bool = False,
    ) -> None:
        self.maxreqlen = maxreqlen
        self.extra_basis = extra_basis
        self.ignore_parent = ignore_parent

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        yield from (
            CellInsertion(tiling, self.maxreqlen, self.extra_basis).rules(
                self.ignore_parent
            )
        )

    def __str__(self) -> str:
        if self.maxreqlen == 1:
            return "point insertion"
        if self.extra_basis is not None:
            perm_class = Av(self.extra_basis)
            return "cell insertion from {} up to " "length {}".format(
                perm_class, self.maxreqlen
            )
        return "cell insertion up to length {}".format(self.maxreqlen)

    def __repr__(self) -> str:
        return (
            "AllCellInsertionStrategy(maxreqlen={}, extra_basis={}, "
            "ignore_parent={})".format(
                self.maxreqlen, self.extra_basis, self.ignore_parent
            )
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["maxreqlen"] = self.maxreqlen
        d["extra_basis"] = self.extra_basis
        d["ignore_parent"] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AllCellInsertionStrategy":
        if d["extra_basis"] is None:
            extra_basis = None
        else:
            extra_basis = [Perm(p) for p in d["extra_basis"]]
        return cls(d["maxreqlen"], extra_basis, d["ignore_parent"],)


class RootInsertionStrategy(AllCellInsertionStrategy):
    """
    The cell insertion strategy performed only on 1 by 1 tilings.
    """

    def __init__(
        self,
        maxreqlen: int = 3,
        extra_basis: Optional[List[Perm]] = None,
        ignore_parent: bool = False,
        max_num_req: Optional[int] = None,
    ) -> None:
        super().__init__(maxreqlen, extra_basis, ignore_parent)
        self.max_num_req = max_num_req

    def _good_rule(self, rule: Strategy) -> bool:
        """
        Check the number of requirements in the rule's tilings satisfy the
        max_num_req
        """
        if self.max_num_req is None:
            return True
        return all(len(t.requirements) <= self.max_num_req for t in rule.comb_classes)

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        if tiling.dimensions != (1, 1):
            return
        rules = CellInsertion(tiling, self.maxreqlen, self.extra_basis).rules(
            self.ignore_parent
        )
        yield from filter(self._good_rule, rules)

    def __str__(self) -> str:
        if self.extra_basis is None:
            s = "root insertion up to length {}".format(self.maxreqlen)
        else:
            perm_class = Av(self.extra_basis)
            s = "root insertion from {} up to length {}".format(
                perm_class, self.maxreqlen
            )
        if self.max_num_req is not None:
            s += " (up to {} requirements)".format(self.max_num_req)
        return s

    def __repr__(self) -> str:
        return (
            "RootInsertionStrategy(maxreqlen={}, extra_basis={}, "
            "ignore_parent={}, max_num_req={})".format(
                self.maxreqlen, self.extra_basis, self.ignore_parent, self.max_num_req
            )
        )

    def to_jsonable(self):
        d = super().to_jsonable()
        d["max_num_req"] = self.max_num_req
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RootInsertionStrategy":
        if d["extra_basis"] is None:
            extra_basis = None
        else:
            extra_basis = [Perm(p) for p in d["extra_basis"]]
        return cls(
            maxreqlen=d["maxreqlen"],
            extra_basis=extra_basis,
            ignore_parent=d["ignore_parent"],
            max_num_req=d.get("max_num_req", None),
        )


class AllRequirementExtensionStrategy(Strategy):
    """
    Insert longer requirements in to cells which contain a requirement
    """

    def __init__(
        self,
        maxreqlen: int = 2,
        extra_basis: Optional[List[Perm]] = None,
        ignore_parent: bool = False,
    ) -> None:
        self.maxreqlen = maxreqlen
        self.extra_basis = extra_basis
        self.ignore_parent = ignore_parent

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        yield from (
            RequirementExtension(tiling, self.maxreqlen, self.extra_basis).rules(
                self.ignore_parent
            )
        )

    def __str__(self) -> str:
        if self.extra_basis is not None:
            perm_class = Av(self.extra_basis)
            return "requirement extension from {} up to " "length {}".format(
                perm_class, self.maxreqlen
            )
        return "requirement extension insertion up to " "length {}".format(
            self.maxreqlen
        )

    def __repr__(self) -> str:
        return (
            "AllRequirementExtensionStrategy(maxreqlen={}, extra_basis={},"
            " ignore_parent={})".format(
                self.maxreqlen, self.extra_basis, self.ignore_parent
            )
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["maxreqlen"] = self.maxreqlen
        d["extra_basis"] = self.extra_basis
        d["ignore_parent"] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AllRequirementExtensionStrategy":
        if d["extra_basis"] is None:
            extra_basis = None
        else:
            extra_basis = [Perm(p) for p in d["extra_basis"]]
        return cls(d["maxreqlen"], extra_basis, d["ignore_parent"],)


class AllRequirementInsertionStrategy(Strategy):
    """
    Insert all possible requirements the obstruction allows if the tiling does
    not have requirements.
    """

    def __init__(
        self,
        maxreqlen: int = 2,
        extra_basis: Optional[List[Perm]] = None,
        ignore_parent: bool = False,
    ) -> None:
        self.maxreqlen = maxreqlen
        self.extra_basis = extra_basis
        self.ignore_parent = ignore_parent

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        if tiling.requirements:
            return
        yield from (
            CrossingInsertion(tiling, self.maxreqlen, self.extra_basis).rules(
                self.ignore_parent
            )
        )

    def __str__(self) -> str:
        if self.maxreqlen == 1:
            return "point insertion"
        if self.extra_basis is not None:
            perm_class = Av(self.extra_basis)
            return "requirement insertion from {} up to " "length {}".format(
                perm_class, self.maxreqlen
            )
        return "requirement insertion up to " "length {}".format(self.maxreqlen)

    def __repr__(self) -> str:
        return (
            "AllRequirementInsertionStrategy(maxreqlen={}, extra_basis={},"
            " ignore_parent={})".format(
                self.maxreqlen, self.extra_basis, self.ignore_parent
            )
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["maxreqlen"] = self.maxreqlen
        d["extra_basis"] = self.extra_basis
        d["ignore_parent"] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AllRequirementInsertionStrategy":
        if d["extra_basis"] is None:
            extra_basis = None
        else:
            extra_basis = [Perm(p) for p in d["extra_basis"]]
        return cls(d["maxreqlen"], extra_basis, d["ignore_parent"],)


class AllFactorInsertionStrategy(Strategy):
    """
    Insert all proper factor of the requirement or obstructions on the tiling.
    """

    def __init__(self, ignore_parent: bool = True) -> None:
        self.ignore_parent = ignore_parent

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        yield from FactorInsertion(tiling).rules(self.ignore_parent)

    def __str__(self) -> str:
        return "all factor insertion"

    def __repr__(self) -> str:
        return "AllFactorInsertionStrategy(ignore_parent={})".format(self.ignore_parent)

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["ignore_parent"] = self.ignore_parent
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

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        yield from (RequirementCorroboration(tiling).rules(self.ignore_parent))

    def __str__(self) -> str:
        return "requirement corroboration"

    def __repr__(self) -> str:
        return "RequirementCorroborationStrategy(ignore_parent={})".format(
            self.ignore_parent
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["ignore_parent"] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementCorroborationStrategy":
        return cls(**d)


class RowAndColumnPlacementStrategy(Strategy):
    def __init__(self, place_row: bool, place_col: bool, partial: bool = False) -> None:
        assert place_col or place_row, "Must place column or row"
        self.place_row = place_row
        self.place_col = place_col
        self.partial = partial

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        if self.partial:
            req_placements = [
                RequirementPlacement(tiling, own_row=False),
                RequirementPlacement(tiling, own_col=False),
            ]
        else:
            req_placements = [RequirementPlacement(tiling)]
        for req_placement in req_placements:
            if self.place_row:
                yield from req_placement.all_row_placement_rules()
            if self.place_col:
                yield from req_placement.all_col_placement_rules()

    def __str__(self) -> str:
        s = "{} placement"
        if self.place_col and self.place_col:
            s = s.format("row and column")
        elif self.place_row:
            s = s.format("row")
        else:
            s = s.format("column")
        if self.partial:
            s = " ".join(["partial", s])
        return s

    def __repr__(self) -> str:
        return (
            "RowAndColumnPlacementStrategy(place_row={}, "
            "place_col={}, partial={})".format(
                self.place_row, self.place_col, self.partial
            )
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["place_row"] = self.place_row
        d["place_col"] = self.place_col
        d["partial"] = self.partial
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RowAndColumnPlacementStrategy":
        return cls(**d)


class AllPlacementsStrategy(Strategy):
    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        req_placements = (
            RequirementPlacement(tiling),
            RequirementPlacement(tiling, own_row=False),
            RequirementPlacement(tiling, own_col=False),
        )
        for req_placement in req_placements:
            yield from req_placement.all_point_placement_rules()
            yield from req_placement.all_requirement_placement_rules()
            yield from req_placement.all_col_placement_rules()
            yield from req_placement.all_row_placement_rules()

    def __str__(self) -> str:
        return "all placements"

    def __repr__(self) -> str:
        return "AllPlacementsStrategy()"

    @classmethod
    def from_dict(cls, d: dict) -> "AllPlacementsStrategy":
        return AllPlacementsStrategy()

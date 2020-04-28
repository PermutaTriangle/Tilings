import abc
from itertools import chain, product
from typing import TYPE_CHECKING, Iterable, Iterator, List, Optional, Tuple

from comb_spec_searcher import (
    Constructor,
    DisjointUnionStrategy,
    Rule,
    Strategy,
    StrategyGenerator,
)
from permuta import Av, Perm
from tilings import GriddedPerm, Obstruction, Requirement, Tiling

ListRequirement = Tuple[Requirement, ...]

EXTRA_BASIS_ERR = "'extra_basis' should be a list of Perm to avoid"

__all__ = [
    "AllCellInsertionStrategy",
    "RootInsertionStrategy",
    "AllRequirementExtensionStrategy",
    "AllRequirementInsertionStrategy",
    "AllFactorInsertionStrategy",
    "RequirementCorroborationStrategy",
]


class RequirementInsertionStrategy(DisjointUnionStrategy):
    def __init__(self, gps: Iterable[GriddedPerm], ignore_parent: bool = False):
        super().__init__(ignore_parent=ignore_parent)
        self.gps = frozenset(gps)

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, Tiling]:
        """
        Return a tuple of tiling. The first one avoids all the pattern in the
        list while the other contain one of the patterns in the list.
        """
        return tiling.add_obstructions(self.gps), tiling.add_list_requirement(self.gps)

    def formal_step(self) -> str:
        """
        Return the formal step for the insertion according to the req_list
        inserted.

        This needs to be redefined if you want to insert list requirement with
        more than one requirement.
        """
        if len(self.gps) == 1:
            req = tuple(self.gps)[0]
            if req.is_localized():
                return "Insert {} in cell {}.".format(req.patt, req.pos[0])
            return "Insert {}.".format(req)
        else:
            raise NotImplementedError

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[GriddedPerm, ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> GriddedPerm:
        if children is None:
            children = self.decomposition_function(tiling)
        idx = DisjointUnionStrategy.backward_map_index(gps)
        return children[idx].backward_map(gps[idx])

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm, ...]:
        raise NotImplementedError
        # t_av, t_co = self.decomposition_function(tiling)
        # if gp.avoids(*self.gps):
        #     return t_av.forward_map(gp)
        # else:
        #     return t_co.forward_map(gp)

    def __repr__(self) -> str:
        return "RequirementInsertionStrategy(gps={}, ignore_parent={})".format(
            self.gps, self.ignore_parent
        )

    def __str__(self) -> str:
        return "requirement insertion"

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the strategy."""
        d = super().to_jsonable()
        d["gps"] = [gp.to_jsonable() for gp in self.gps]
        return

    @classmethod
    def from_dict(cls, d: dict) -> "ObstructionInferralStrategy":
        gps = [GriddedPerm.from_dict(gp) for gp in d["gps"]]
        return cls(gps=gps, ignore_parent=d["ignore_parent"])


class RequirementInsertionStrategyGenerator(StrategyGenerator):
    """
    Bases class for requirement insertion on tilings.

    It will create batch rules based on the containment or not of
    requirements.  The requirement  used are  provided by `req_list_to_insert`
    """

    def __init__(self, ignore_parent: bool = False):
        self.ignore_parent = ignore_parent

    @abc.abstractmethod
    def req_lists_to_insert(self, tiling: Tiling) -> Iterable[ListRequirement]:
        """
        Iterator over all the requirement list to insert to create the batch
        rules.
        """

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        """
        Iterator over all the requirement insertion rules.
        """
        for req_list in self.req_lists_to_insert(tiling):
            yield RequirementInsertionStrategy(req_list, self.ignore_parent)

    def to_jsonable(self):
        d = super().to_jsonable()
        d["ignore_parent"] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementInsertionStrategyGenerator":
        return cls(ignore_parent=d["ignore_parent"])

    def __repr__(self) -> str:
        return "{}(ignore_parent={})".format(
            self.__class__.__name__, self.ignore_parent
        )


class RequirementInsertionWithRestrictionStrategyGenerator(
    RequirementInsertionStrategyGenerator
):
    """
    As RequirementInsertion, but a set of pattern to avoids and a maximum
    length can be provided.
    """

    def __init__(
        self,
        maxreqlen: int,
        extra_basis: Optional[List[Perm]] = None,
        ignore_parent: bool = False,
    ):
        if extra_basis is None:
            self.extra_basis = []
        else:
            assert isinstance(extra_basis, list), EXTRA_BASIS_ERR
            assert all(isinstance(p, Perm) for p in extra_basis), EXTRA_BASIS_ERR
            self.extra_basis = extra_basis
        self.maxreqlen = maxreqlen
        super().__init__(ignore_parent)

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["maxreqlen"] = self.maxreqlen
        d["extra_basis"] = self.extra_basis
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AllCellInsertionStrategy":
        if d["extra_basis"] is None:
            extra_basis = None
        else:
            extra_basis = [Perm(p) for p in d["extra_basis"]]
        return cls(
            maxreqlen=d["maxreqlen"],
            extra_basis=extra_basis,
            ignore_parent=d["ignore_parent"],
        )

    def __repr__(self) -> str:
        return "{}(maxreqlen={}, extra_basis={}, " "ignore_parent={})".format(
            self.__class__.__name__,
            self.maxreqlen,
            self.extra_basis,
            self.ignore_parent,
        )


class AllCellInsertionStrategy(RequirementInsertionWithRestrictionStrategyGenerator):
    """
    The cell insertion strategy.

    The cell insertion strategy is a disjoint union strategy.
    For each active cell, the strategy considers all patterns (up to some maximum
    length given by `maxreqlen`) and returns two tilings; one which requires the
    pattern in the cell and one where the pattern is obstructed.
    """

    def __init__(
        self,
        maxreqlen: int = 1,
        extra_basis: Optional[List[Perm]] = None,
        ignore_parent: bool = False,
    ) -> None:
        super().__init__(maxreqlen, extra_basis, ignore_parent)

    def req_lists_to_insert(self, tiling: Tiling) -> Iterable[ListRequirement]:
        active = tiling.active_cells
        bdict = tiling.cell_basis()
        for cell, length in product(active, range(1, self.maxreqlen + 1)):
            basis = bdict[cell][0] + self.extra_basis
            yield from (
                (Requirement.single_cell(patt, cell),)
                for patt in Av(basis).of_length(length)
                if not any(patt in perm for perm in bdict[cell][1])
            )

    def __str__(self) -> str:
        if self.maxreqlen == 1:
            return "point insertion"
        if self.extra_basis:
            perm_class = Av(self.extra_basis)
            return "cell insertion from {} up to " "length {}".format(
                perm_class, self.maxreqlen
            )
        return "cell insertion up to length {}".format(self.maxreqlen)


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

    def _good_rule(self, rule: Rule) -> bool:
        """
        Check the number of requirements in the rule's tilings satisfy the
        max_num_req
        """
        if self.max_num_req is None:
            return True
        return all(len(t.requirements) <= self.max_num_req for t in rule.children)

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Rule]:
        if tiling.dimensions != (1, 1):
            return
        for strategy in super().__call__(tiling):
            rule = strategy(tiling)
            if self._good_rule(rule):
                yield rule

    def __str__(self) -> str:
        if not self.extra_basis:
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
            "{}(maxreqlen={}, extra_basis={}, "
            "ignore_parent={}, max_num_req={})".format(
                self.__class__.__name__,
                self.maxreqlen,
                self.extra_basis,
                self.ignore_parent,
                self.max_num_req,
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


class AllRequirementExtensionStrategy(
    RequirementInsertionWithRestrictionStrategyGenerator
):
    """
    Insert longer requirements in to cells which contain a requirement
    """

    def __init__(
        self,
        maxreqlen: int = 2,
        extra_basis: Optional[List[Perm]] = None,
        ignore_parent: bool = False,
    ) -> None:
        super().__init__(maxreqlen, extra_basis, ignore_parent)

    def req_lists_to_insert(self, tiling: Tiling) -> Iterable[ListRequirement]:
        bdict = tiling.cell_basis()
        cell_with_req = (
            (cell, obs, reqlist[0])
            for cell, (obs, reqlist) in bdict.items()
            if len(reqlist) == 1
        )
        for cell, obs, curr_req in cell_with_req:
            for length in range(len(curr_req) + 1, self.maxreqlen + 1):
                for patt in Av(obs + self.extra_basis).of_length(length):
                    if curr_req in patt:
                        yield (Requirement.single_cell(patt, cell),)

    def __str__(self) -> str:
        if self.extra_basis:
            perm_class = Av(self.extra_basis)
            return "requirement extension from {} up to " "length {}".format(
                perm_class, self.maxreqlen
            )
        return "requirement extension insertion up to " "length {}".format(
            self.maxreqlen
        )


class AllRequirementInsertionStrategy(
    RequirementInsertionWithRestrictionStrategyGenerator
):
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
        super().__init__(maxreqlen, extra_basis, ignore_parent)

    def req_lists_to_insert(self, tiling: Tiling) -> Iterable[ListRequirement]:
        obs_tiling = Tiling(
            tiling.obstructions,
            remove_empty=False,
            derive_empty=False,
            minimize=False,
            sorted_input=True,
        )
        for length in range(1, self.maxreqlen + 1):
            for gp in obs_tiling.gridded_perms_of_length(length):
                if len(gp.factors()) == 1 and all(
                    p not in gp.patt for p in self.extra_basis
                ):
                    yield (Requirement(gp.patt, gp.pos),)

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        if tiling.requirements:
            return
        yield from super().__call__(tiling, **kwargs)

    def __str__(self) -> str:
        if self.maxreqlen == 1:
            return "point insertion"
        if self.extra_basis:
            perm_class = Av(self.extra_basis)
            return "requirement insertion from {} up to " "length {}".format(
                perm_class, self.maxreqlen
            )
        return "requirement insertion up to " "length {}".format(self.maxreqlen)


class AllFactorInsertionStrategy(RequirementInsertionStrategyGenerator):
    """
    Insert all proper factor of the requirement or obstructions on the tiling.
    """

    def __init__(self, ignore_parent: bool = True) -> None:
        super().__init__(ignore_parent)

    def req_lists_to_insert(self, tiling: Tiling) -> Iterable[ListRequirement]:
        gp_facts = map(
            GriddedPerm.factors, chain(tiling.obstructions, *tiling.requirements),
        )
        proper_facts = chain.from_iterable(f for f in gp_facts if len(f) > 1)
        for f in proper_facts:
            yield (Requirement(f.patt, f.pos),)

    def __str__(self) -> str:
        return "all factor insertion"


class RequirementCorroborationStrategy(RequirementInsertionStrategyGenerator):
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
        super().__init__(ignore_parent)

    def req_lists_to_insert(self, tiling: Tiling) -> Iterable[ListRequirement]:
        to_insert = chain.from_iterable(
            reqs for reqs in tiling.requirements if len(reqs) > 1
        )
        for req in to_insert:
            yield (req,)

    def __str__(self) -> str:
        return "requirement corroboration"

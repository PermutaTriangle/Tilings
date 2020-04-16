import abc
from itertools import chain, product
from typing import TYPE_CHECKING, Iterable, List, Optional, Tuple

from comb_spec_searcher import Constructor, DisjointUnion, Rule
from permuta import Av, Perm
from tilings import GriddedPerm, Obstruction, Requirement

if TYPE_CHECKING:
    from tilings import Tiling
ListRequirement = Tuple[Requirement, ...]

EXTRA_BASIS_ERR = "'extra_basis' should be a list of Perm to avoid"


class RequirementInsertionRule(Rule):
    def __init__(self, gps: Iterable[GriddedPerm], ignore_parent: bool = False):
        self._ignore_parent = ignore_parent
        self.gps = frozenset(gps)

    @property
    def ignore_parent(self):
        return self._ignore_parent

    def constructor(self, tiling: "Tiling") -> Constructor:
        return DisjointUnion()

    def children(self, tiling: "Tiling") -> Tuple["Tiling", "Tiling"]:
        """
        Return a tuple of tiling. The first one avoids all the pattern in the
        list while the other contain one of the patterns in the list.
        """
        obs = tiling.obstructions
        reqs = tiling.requirements
        t_co = tiling.add_list_requirement(map(Requirement.from_gridded_perm, self.gps))
        new_obs = chain(obs, (Obstruction(req.patt, req.pos) for req in self.gps))
        t_av = tiling.__class__(obstructions=new_obs, requirements=reqs)
        return (t_av, t_co)

    def backward_map(
        self, tiling: "Tiling", gps: Tuple[Tuple[GriddedPerm, "Tiling"]]
    ) -> GriddedPerm:
        return tiling.backward_map(gp[0])

    def forward_map(
        self, tiling: "Tiling", gp: GriddedPerm
    ) -> Tuple[Tuple[GriddedPerm, "Tiling"], ...]:
        t_av, t_co = self.children(tiling)
        if gp.avoids(*self.gps):
            return t_av.forward_map(gp)
        else:
            return t_co.forward_map(gp)


# Abstract classes
class RequirementInsertion(abc.ABC):
    """
    Bases class for requirement insertion on tilings.

    It will create batch rules based on the containment or not of
    requirements.  The requirement  used are  provided by `req_list_to_insert`
    """

    def __init__(self, tiling: "Tiling"):
        self.tiling = tiling

    @abc.abstractmethod
    def req_lists_to_insert(self) -> Iterable[ListRequirement]:
        """
        Iterator over all the requirement list to insert to create the batch
        rules.
        """

    @staticmethod
    def formal_step(req_list: ListRequirement) -> str:
        """
        Return the formal step for the insertion according to the req_list
        inserted.

        This needs to be redefined if you want to insert list requirement with
        more than one requirement.
        """
        if len(req_list) != 1:
            raise NotImplementedError
        req = req_list[0]
        if req.is_localized():
            return "Insert {} in cell {}.".format(req.patt, req.pos[0])
        return "Insert {}.".format(req)

    def rules(self, ignore_parent: bool = False) -> Iterable[Rule]:
        """
        Iterator over all the requirement insertion rules.
        """
        for req_list in self.req_lists_to_insert():
            yield RequirementInsertionRule(req_list)


class RequirementInsertionWithRestriction(RequirementInsertion):
    """
    As RequirementInsertion, but a set of pattern to avoids and a maximum
    length can be provided.
    """

    def __init__(
        self, tiling: "Tiling", maxreqlen: int, extra_basis: Optional[List[Perm]] = None
    ):
        super().__init__(tiling)
        if extra_basis is None:
            self.extra_basis = []
        else:
            assert isinstance(extra_basis, list), EXTRA_BASIS_ERR
            assert all(isinstance(p, Perm) for p in extra_basis), EXTRA_BASIS_ERR
            self.extra_basis = extra_basis
        self.maxreqlen = maxreqlen


# Concrete classes
class CrossingInsertion(RequirementInsertionWithRestriction):
    """
    Insert all possible requirement, crossing and non-crossing of length at
    most `maxreqlen` that avoid the pattern in `extra_basis`.
    """

    def req_lists_to_insert(self) -> Iterable[ListRequirement]:
        obs_tiling = self.tiling.__class__(
            self.tiling.obstructions,
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


class CellInsertion(RequirementInsertionWithRestriction):
    """
    Inserting single cell requirements.
    """

    def req_lists_to_insert(self) -> Iterable[ListRequirement]:
        active = self.tiling.active_cells
        bdict = self.tiling.cell_basis()
        for cell, length in product(active, range(1, self.maxreqlen + 1)):
            basis = bdict[cell][0] + self.extra_basis
            yield from (
                (Requirement.single_cell(patt, cell),)
                for patt in Av(basis).of_length(length)
                if not any(patt in perm for perm in bdict[cell][1])
            )


class RequirementExtension(RequirementInsertionWithRestriction):
    """
    Inserting longer requirement in cells that  already have requirement.
    """

    def req_lists_to_insert(self) -> Iterable[ListRequirement]:
        bdict = self.tiling.cell_basis()
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


class FactorInsertion(RequirementInsertion):
    """
    Insert the proper factor of any obstruction or requirements.
    """

    def req_lists_to_insert(self) -> Iterable[ListRequirement]:
        gp_facts = map(
            GriddedPerm.factors,
            chain(self.tiling.obstructions, *self.tiling.requirements),
        )
        proper_facts = chain.from_iterable(f for f in gp_facts if len(f) > 1)
        for f in proper_facts:
            yield (Requirement(f.patt, f.pos),)


class RequirementCorroboration(RequirementInsertion):
    """
    Insert one requirement from a requirement list.
    """

    def req_lists_to_insert(self) -> Iterable[ListRequirement]:
        to_insert = chain.from_iterable(
            reqs for reqs in self.tiling.requirements if len(reqs) > 1
        )
        for req in to_insert:
            yield (req,)

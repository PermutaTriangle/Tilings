import abc
from itertools import chain, product
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple, cast

from comb_spec_searcher import DisjointUnionStrategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
from comb_spec_searcher.strategies.strategy import VerificationStrategy
from permuta import Av, Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Factor
from tilings.strategies import (
    BasicVerificationStrategy,
    InsertionEncodingVerificationStrategy,
    LocallyFactorableVerificationStrategy,
    OneByOneVerificationStrategy,
)

ListRequirement = Tuple[GriddedPerm, ...]

EXTRA_BASIS_ERR = "'extra_basis' should be a list of Perm to avoid"

__all__ = [
    "CellInsertionFactory",
    "RootInsertionFactory",
    "RequirementExtensionFactory",
    "RequirementInsertionFactory",
    "FactorInsertionFactory",
    "RequirementCorroborationFactory",
]


class RequirementInsertionStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    def __init__(self, gps: Iterable[GriddedPerm], ignore_parent: bool = False):
        super().__init__(ignore_parent=ignore_parent)
        self.gps = frozenset(gps)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling, Tiling]:
        """
        Return a tuple of tiling. The first one avoids all the pattern in the
        list while the other contain one of the patterns in the list.
        """
        return comb_class.add_obstructions(self.gps), comb_class.add_list_requirement(
            self.gps
        )

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
                return f"insert {req.patt} in cell {req.pos[0]}"
            return f"insert {req}"
        raise NotImplementedError

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        if children is None:
            children = self.decomposition_function(comb_class)
        idx = DisjointUnionStrategy.backward_map_index(objs)
        yield children[idx].backward_map.map_gp(cast(GriddedPerm, objs[idx]))

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], Optional[GriddedPerm]]:
        if children is None:
            children = self.decomposition_function(comb_class)
        if obj.avoids(*self.gps):
            return (children[0].forward_map.map_gp(obj), None)
        return (None, children[1].forward_map.map_gp(obj))

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if not comb_class.extra_parameters:
            return super().extra_parameters(comb_class, children)
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        av, co = children
        av_params: Dict[str, str] = {}
        co_params: Dict[str, str] = {}
        for assumption in comb_class.assumptions:
            parent_var = comb_class.get_assumption_parameter(assumption)
            av_mapped_assumption = av.forward_map.map_assumption(assumption).avoiding(
                av.obstructions
            )
            if av_mapped_assumption.gps:
                child_var = av.get_assumption_parameter(av_mapped_assumption)
                av_params[parent_var] = child_var
            co_mapped_assumption = co.forward_map.map_assumption(assumption).avoiding(
                co.obstructions
            )
            if co_mapped_assumption.gps:
                child_var = co.get_assumption_parameter(co_mapped_assumption)
                co_params[parent_var] = child_var
        return av_params, co_params

    def __repr__(self) -> str:
        args = ", ".join([f"gps={self.gps}", f"ignore_parent={self.ignore_parent}"])
        return f"{self.__class__.__name__}({args})"

    def __str__(self) -> str:
        return "requirement insertion"

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the strategy."""
        d: dict = super().to_jsonable()
        d.pop("inferrable")
        d.pop("possibly_empty")
        d.pop("workable")
        d["gps"] = [gp.to_jsonable() for gp in self.gps]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementInsertionStrategy":
        gps = [GriddedPerm.from_dict(gp) for gp in d.pop("gps")]
        return cls(gps=gps, **d)


class AbstractRequirementInsertionFactory(StrategyFactory[Tiling]):
    """
    Bases class for requirement insertion on tilings.

    It will create batch rules based on the containment or not of
    requirements.  The requirement  used are  provided by `req_list_to_insert`
    """

    def __init__(self, ignore_parent: bool = False):
        self.ignore_parent = ignore_parent

    @abc.abstractmethod
    def req_lists_to_insert(self, tiling: Tiling) -> Iterator[ListRequirement]:
        """
        Iterator over all the requirement list to insert to create the batch
        rules.
        """

    def __call__(self, comb_class: Tiling) -> Iterator[RequirementInsertionStrategy]:
        """
        Iterator over all the requirement insertion rules.
        """
        for req_list in self.req_lists_to_insert(comb_class):
            yield RequirementInsertionStrategy(req_list, self.ignore_parent)

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["ignore_parent"] = self.ignore_parent
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AbstractRequirementInsertionFactory":
        return cls(**d)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(ignore_parent={self.ignore_parent})"


class RequirementInsertionWithRestrictionFactory(AbstractRequirementInsertionFactory):
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
        d: dict = super().to_jsonable()
        d["maxreqlen"] = self.maxreqlen
        d["extra_basis"] = self.extra_basis
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementInsertionWithRestrictionFactory":
        if d["extra_basis"] is None:
            extra_basis = None
        else:
            extra_basis = [Perm(p) for p in d["extra_basis"]]
        d.pop("extra_basis")
        return cls(extra_basis=extra_basis, **d)

    def __repr__(self) -> str:
        args = ", ".join(
            [
                f"maxreqlen={self.maxreqlen}",
                f"extra_basis={self.extra_basis}",
                f"ignore_parent={self.ignore_parent}",
            ]
        )
        return f"{self.__class__.__name__}({args})"


class CellInsertionFactory(RequirementInsertionWithRestrictionFactory):
    """
    The cell insertion strategy.

    The cell insertion strategy is a disjoint union strategy.
    For each active cell, the strategy considers all patterns (up to some maximum
    length given by `maxreqlen`) and returns two tilings; one which requires the
    pattern in the cell and one where the pattern is obstructed.

    The one_cell_only flag will ensure that the strategy only inserts into the
    'smallest' non-positive cell. This is used for 'insertion' packs where
    we are intending to make every cell positive, so with this setting we have
    a unique path to the fully positive tilings.
    """

    def __init__(
        self,
        maxreqlen: int = 1,
        extra_basis: Optional[List[Perm]] = None,
        ignore_parent: bool = False,
        one_cell_only: bool = False,
    ) -> None:
        super().__init__(maxreqlen, extra_basis, ignore_parent)
        self.one_cell_only = one_cell_only

    def req_lists_to_insert(self, tiling: Tiling) -> Iterator[ListRequirement]:
        if self.one_cell_only:
            assert self.maxreqlen == 1 and self.ignore_parent
            cells = sorted(
                frozenset(tiling.active_cells) - frozenset(tiling.positive_cells)
            )
            if cells:
                yield (GriddedPerm.single_cell((0,), cells[0]),)
            return

        active = tiling.active_cells
        bdict = tiling.cell_basis()
        for cell, length in product(active, range(1, self.maxreqlen + 1)):
            basis = bdict[cell][0] + self.extra_basis
            patterns = Av(basis).of_length(length) if basis else Perm.of_length(length)
            yield from (
                (GriddedPerm.single_cell(patt, cell),)
                for patt in patterns
                if not any(patt in perm for perm in bdict[cell][1])
            )

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["one_cell_only"] = self.one_cell_only
        return d

    def __str__(self) -> str:
        if self.maxreqlen == 1:
            return "point insertion"
        if self.extra_basis:
            perm_class = Av(self.extra_basis)
            return f"cell insertion from {perm_class} up to length {self.maxreqlen}"
        return f"cell insertion up to length {self.maxreqlen}"

    def __repr__(self) -> str:
        args = ", ".join(
            [
                f"maxreqlen={self.maxreqlen}",
                f"extra_basis={self.extra_basis!r}",
                f"ignore_parent={self.ignore_parent}",
                f"one_cell_only={self.one_cell_only}",
            ]
        )
        return f"{self.__class__.__name__}({args})"


class RootInsertionFactory(CellInsertionFactory):
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

    def __call__(self, comb_class: Tiling) -> Iterator[RequirementInsertionStrategy]:
        if comb_class.dimensions != (1, 1):
            return
        for strategy in super().__call__(comb_class):
            t_with_new_req = comb_class.add_list_requirement(strategy.gps)
            if (
                self.max_num_req is None
                or len(t_with_new_req.requirements) <= self.max_num_req
            ):
                yield strategy

    def __str__(self) -> str:
        if not self.extra_basis:
            s = f"root insertion up to length {self.maxreqlen}"
        else:
            perm_class = Av(self.extra_basis)
            s = f"root insertion from {perm_class} up to length {self.maxreqlen}"
        if self.max_num_req is not None:
            s += f" (up to {self.max_num_req} requirements)"
        return s

    def __repr__(self) -> str:
        args = ", ".join(
            [
                f"maxreqlen={self.maxreqlen}",
                f"extra_basis={self.extra_basis}",
                f"ignore_parent={self.ignore_parent}",
                f"max_num_req={self.max_num_req}",
            ]
        )
        return f"{self.__class__.__name__}({args})"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["max_num_req"] = self.max_num_req
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RootInsertionFactory":
        if d["extra_basis"] is None:
            extra_basis = None
        else:
            extra_basis = [Perm(p) for p in d["extra_basis"]]
        d.pop("extra_basis")
        d.pop("one_cell_only")
        return cls(extra_basis=extra_basis, **d)


class RequirementExtensionFactory(RequirementInsertionWithRestrictionFactory):
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

    def req_lists_to_insert(self, tiling: Tiling) -> Iterator[ListRequirement]:
        bdict = tiling.cell_basis()
        cell_with_req = (
            (cell, obs, reqlist[0])
            for cell, (obs, reqlist) in bdict.items()
            if len(reqlist) == 1
        )
        for cell, obs, curr_req in cell_with_req:
            for length in range(len(curr_req) + 1, self.maxreqlen + 1):
                basis = obs + self.extra_basis
                patterns = (
                    Av(basis).of_length(length) if basis else Perm.of_length(length)
                )
                for patt in patterns:
                    if curr_req in patt:
                        yield (GriddedPerm.single_cell(patt, cell),)

    def __str__(self) -> str:
        if self.extra_basis:
            perm_class = f" from {Av(self.extra_basis)}"
        else:
            perm_class = ""
        return f"requirement extension{perm_class} up to length {self.maxreqlen}"


class RequirementInsertionFactory(RequirementInsertionWithRestrictionFactory):
    """
    Insert all possible requirements the obstruction allows if the tiling does
    not have requirements.

    If <limited_insertion> is true, the default behavior, requirements will only be
    inserted on Tilings that have no requirements.
    """

    def __init__(
        self,
        maxreqlen: int = 2,
        extra_basis: Optional[List[Perm]] = None,
        limited_insertion: bool = True,
        ignore_parent: bool = False,
    ) -> None:
        self.limited_insertion = limited_insertion
        super().__init__(maxreqlen, extra_basis, ignore_parent)

    def req_lists_to_insert(self, tiling: Tiling) -> Iterator[ListRequirement]:
        obs_tiling = Tiling(
            tiling.obstructions,
            remove_empty_rows_and_cols=False,
            derive_empty=False,
            simplify=False,
            sorted_input=True,
        )
        for length in range(1, self.maxreqlen + 1):
            for gp in obs_tiling.gridded_perms_of_length(length):
                if len(gp.factors()) == 1 and all(
                    p not in gp.patt for p in self.extra_basis
                ):
                    yield (GriddedPerm(gp.patt, gp.pos),)

    def __call__(self, comb_class: Tiling) -> Iterator[RequirementInsertionStrategy]:
        if self.limited_insertion and comb_class.requirements:
            return
        yield from super().__call__(comb_class)

    def __str__(self) -> str:
        if self.maxreqlen == 1:
            return "point insertion"
        if self.extra_basis:
            perm_class = f" from {Av(self.extra_basis)}"
        else:
            perm_class = ""
        return f"requirement insertion{perm_class} up to length {self.maxreqlen}"

    def __repr__(self) -> str:
        args = ", ".join(
            [
                f"maxreqlen={self.maxreqlen}",
                f"extra_basis={self.extra_basis!r}",
                f"limited_insertion={self.limited_insertion}",
                f"ignore_parent={self.ignore_parent}",
            ]
        )
        return f"{self.__class__.__name__}({args})"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["limited_insertion"] = self.limited_insertion
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementInsertionWithRestrictionFactory":
        if d["limited_insertion"] is None:
            extra_basis = None
        else:
            extra_basis = [Perm(p) for p in d["extra_basis"]]
        d.pop("extra_basis")
        limited_insertion = d.pop("limited_insertion")
        maxreqlen = d.pop("maxreqlen")
        return cls(
            maxreqlen=maxreqlen,
            extra_basis=extra_basis,
            limited_insertion=limited_insertion,
            **d,
        )


class FactorInsertionFactory(AbstractRequirementInsertionFactory):
    """
    Insert all proper factor of the requirement or obstructions on the tiling.
    """

    def __init__(self, ignore_parent: bool = True) -> None:
        super().__init__(ignore_parent)

    def req_lists_to_insert(self, tiling: Tiling) -> Iterator[ListRequirement]:
        reqs_and_obs: Iterator[GriddedPerm] = chain(
            tiling.obstructions, *tiling.requirements
        )
        gp_facts = map(GriddedPerm.factors, reqs_and_obs)
        proper_facts = chain.from_iterable(f for f in gp_facts if len(f) > 1)
        for f in proper_facts:
            yield (GriddedPerm(f.patt, f.pos),)

    def __str__(self) -> str:
        return "all factor insertion"


class RequirementCorroborationFactory(AbstractRequirementInsertionFactory):
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

    def req_lists_to_insert(self, tiling: Tiling) -> Iterator[ListRequirement]:
        to_insert = chain.from_iterable(
            reqs for reqs in tiling.requirements if len(reqs) > 1
        )
        for req in to_insert:
            yield (req,)

    def __str__(self) -> str:
        return "requirement corroboration"


class RemoveRequirementFactory(StrategyFactory[Tiling]):
    """
    For a tiling T, and each requirement R on T, create the rules that
    cell inserts R onto the tiling T without R.
    """

    def __call__(self, comb_class: Tiling) -> Iterator[Rule[Tiling, GriddedPerm]]:
        for req_list in comb_class.requirements:
            remove_req = comb_class.remove_requirement(req_list)
            yield RequirementInsertionStrategy(req_list)(remove_req)

    def __str__(self) -> str:
        return "remove requirements"

    @classmethod
    def from_dict(cls, d: dict) -> "RemoveRequirementFactory":
        return cls()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class FactorRowCol(Factor):
    def _unite_all(self) -> None:
        self._unite_rows_and_cols()


class TargetedCellInsertionFactory(AbstractRequirementInsertionFactory):
    """
    Insert factors requirements or obstructions on the tiling if it can lead
    to separating a verified factor.
    """

    def __init__(self, ignore_parent: bool = True) -> None:
        super().__init__(ignore_parent)

    def req_lists_to_insert(self, tiling: Tiling) -> Iterator[ListRequirement]:
        factor_class = FactorRowCol(tiling)
        potential_factors = factor_class.get_components()
        reqs_and_obs: Set[GriddedPerm] = set(
            chain(tiling.obstructions, *tiling.requirements)
        )
        verification_strats: List[VerificationStrategy] = [
            BasicVerificationStrategy(),
            InsertionEncodingVerificationStrategy(),
            OneByOneVerificationStrategy(),
            LocallyFactorableVerificationStrategy(),
        ]
        potential_verified = [False for _ in potential_factors]
        for idx, cells in enumerate(potential_factors):
            sub_tiling = tiling.sub_tiling(cells)
            for strategy in verification_strats:
                potential_verified[idx] |= strategy.verified(sub_tiling)

        for idx, cells in enumerate(potential_factors):
            if potential_verified[idx]:
                for gp in reqs_and_obs:
                    if any(cell in cells for cell in gp.pos) and any(
                        cell not in cells for cell in gp.pos
                    ):
                        yield (gp.get_gridded_perm_in_cells(cells),)

    def __str__(self) -> str:
        return "targeted cell insertions"

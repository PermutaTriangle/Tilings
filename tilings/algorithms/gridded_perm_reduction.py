from collections import defaultdict
from functools import partial
from typing import Iterable, Iterator, List, Optional, Set, Tuple

from comb_spec_searcher.utils import cssmethodtimer
from ..griddedperm import GriddedPerm

Cell = Tuple[int, int]
Requirement = Tuple[GriddedPerm, ...]

func_calls = defaultdict(int)
func_times = defaultdict(float)


class MinimalGriddedPermSet:

    func_calls = func_calls
    func_times = func_times

    def __init__(self, griddedperms: Iterable[GriddedPerm]):
        self.griddedperms: Tuple[GriddedPerm, ...] = tuple(sorted(griddedperms))
        self._minimize()

    @cssmethodtimer("MinimalGriddedPermSet._minimize")
    def _minimize(self) -> None:
        """
        Removes non minimal gridded permutations from the set.
        """
        res: List[GriddedPerm] = []
        for gp_to_add in self.griddedperms:
            if all(gp_already_added not in gp_to_add for gp_already_added in res):
                res.append(gp_to_add)
        if len(res) != len(self.griddedperms):
            # self.griddedperms = tuple(sorted(res))
            self.casting(res)

    @cssmethodtimer("MinimalGriddedPermSet._recasting")
    def casting(self, res):
        self.griddedperms = tuple(sorted(res))

    @cssmethodtimer("MinimalGriddedPermSet.factors")
    def factors(self) -> Set[GriddedPerm]:
        if self.griddedperms:
            res: Set[GriddedPerm] = set(self.griddedperms[0].factors())
            for gp in self.griddedperms[1:]:
                if not res:
                    break
                res = res.intersection(gp.factors())
        return res

    def __bool__(self):
        return bool(self.griddedperms)

    def __eq__(self, other):
        return self.griddedperms == other.griddedperms

    def __len__(self) -> int:
        return len(self.griddedperms)

    @cssmethodtimer("MinimalGriddedPermSet.__lt__")
    def __lt__(self, other):
        if isinstance(other, MinimalGriddedPermSet):
            return self.griddedperms < other.griddedperms
        raise NotImplementedError("Can only compare two MinimalGriddedPermSet")

    def __iter__(self) -> Iterator[GriddedPerm]:
        return iter(self.griddedperms)

    def __getitem__(self, idx: int):
        return self.griddedperms[idx]

    def __repr__(self):
        return self.__class__.__name__ + "({})".format(
            ", ".join(repr(gp) for gp in self.griddedperms)
        )

    def __str__(self):
        return "{{{}}}".format(", ".join(str(gp) for gp in self.griddedperms))


class GriddedPermReduction:
    func_calls = func_calls
    func_times = func_times

    @cssmethodtimer("GriddedPermReduction.__init__")
    def __init__(
        self,
        obstructions: Iterable[GriddedPerm],
        requirements: Iterable[Iterable[GriddedPerm]],
    ):
        self._requirements = tuple(
            sorted(MinimalGriddedPermSet(r) for r in requirements)
        )
        self._obstructions = MinimalGriddedPermSet(obstructions)
        self._minimize_griddedperms()

    @property
    def obstructions(self):
        return tuple(sorted(self._obstructions))

    @property
    def requirements(self):
        return tuple(
            sorted(tuple(sorted(requirement)) for requirement in self._requirements)
        )

    @cssmethodtimer("GriddedPermReduction._clean_isolated")
    def _clean_isolated(self, obstruction: GriddedPerm) -> GriddedPerm:
        """Remove the isolated factors that are implied by requirements
        from all obstructions."""
        for factor in obstruction.factors():
            if self._griddedperm_implied_by_some_requirement(factor):
                obstruction = obstruction.remove_cells(factor.pos)
        return obstruction

    @cssmethodtimer("GriddedPermReduction._minimize_griddedperms")
    def _minimize_griddedperms(self) -> None:
        """Minimizes the set of obstructions and the set of requirement lists.
        The set of obstructions are first reduced to a minimal set. The
        requirements that contain any obstructions are removed from their
        respective lists. If any requirement list is empty, then the tiling is
        empty.
        """

        def set_empty():
            self._obstructions = MinimalGriddedPermSet([GriddedPerm.empty_perm()])
            self._requirements = tuple()

        while True:
            # Minimize the set of obstructions
            minimized_obs = self.minimal_obs()

            # TODO: this is sorted, only check the first one?
            if any(len(gp) == 0 for gp in minimized_obs):
                set_empty()
                break

            # Minimize the set of requiriments
            minimized_requirements = self.minimal_reqs(minimized_obs)

            # TODO: this is sorted, only check the first one?
            if any(not r for r in minimized_requirements):
                set_empty()
                break

            if (
                self._obstructions == minimized_obs
                and self._requirements == minimized_requirements
            ):
                break

            self._obstructions = minimized_obs
            self._requirements = minimized_requirements

    @cssmethodtimer("GriddedPermReduction.minimal_obs")
    def minimal_obs(self) -> MinimalGriddedPermSet:
        changed = False
        cleanedobs = []
        for ob in self.obstructions:
            cleanedob = self._clean_isolated(ob)
            if len(cleanedob) != len(ob):
                changed = True
            cleanedobs.append(cleanedob)
        if changed:
            # TODO: smarted to update?
            return MinimalGriddedPermSet(cleanedobs)
        else:
            return self._obstructions

    @cssmethodtimer("GriddedPermReduction.minimal_reqs")
    def minimal_reqs(self, obstructions: MinimalGriddedPermSet):
        algos = (
            self.factored_reqs,
            self.cleaned_requirements,
            partial(self.remove_avoided, obstructions=obstructions),
            self.remove_redundant_requirements,
        )
        minimized_requirements = self._requirements
        for algo in algos:
            minimized_requirements = algo(minimized_requirements)
            if any(not r for r in minimized_requirements):
                return [MinimalGriddedPermSet([])]
        return minimized_requirements

    @cssmethodtimer("GriddedPermReduction.factored_reqs")
    def factored_reqs(
        self, requirements: Iterable[MinimalGriddedPermSet],
    ) -> List[MinimalGriddedPermSet]:
        """
        Add factors of requirements as size one requirements, removing them
        from each of the gridded permutations in the requirement it is
        contained in.
        """
        res: List[MinimalGriddedPermSet] = list()
        for requirement in requirements:
            if not requirement:
                # If req is empty, then this requirement can't be satisfied, so
                # return it and mark obstructions and requirements as empty.
                return [MinimalGriddedPermSet([])]
            # If any gridded permutation in list is empty then you vacuously
            # contain this requirement
            if all(requirement):
                factors = requirement.factors()
                if len(factors) == 0 or (len(factors) == 1 and len(requirement) == 1):
                    # if there are no factors in the intersection, or it is just
                    # the same req as the first, we do nothing and add the original
                    res.append(requirement)
                    continue
                # add each of the factors as a single requirement, and then remove
                # these from each of the other requirements in the list
                remaining_cells = set(c for gp in requirement for c in gp.pos) - set(
                    c for gp in factors for c in gp.pos
                )
                for factor in factors:
                    res.append(MinimalGriddedPermSet((factor,)))
                # TODO: smarter to update the requirement?
                rem_requirement = MinimalGriddedPermSet(
                    gp.get_gridded_perm_in_cells(remaining_cells) for gp in requirement
                )
                res.append(rem_requirement)
        return res

    @cssmethodtimer("GriddedPermReduction.cleaned_requirements")
    def cleaned_requirements(
        self, requirements: List[MinimalGriddedPermSet]
    ) -> List[MinimalGriddedPermSet]:
        """
        Remove the factors of a gridded permutation in a requirement if it is
        implied by another requirement.
        """
        cleaned_reqs: List[MinimalGriddedPermSet] = []
        for requirement in requirements:
            if not all(requirement):
                continue
            changed = False
            newgps: List[GriddedPerm] = []
            for gp in requirement:
                cells: List[Cell] = []
                for f in gp.factors():
                    # if factor implied by some requirement list then we
                    # remove it from the gridded perm
                    if not self._griddedperm_implied_by_some_requirement(
                        f,
                        (
                            other_requirement
                            for other_requirement in requirements
                            if not self._requirement_implied_by_requirement(
                                other_requirement, requirement
                            )
                        ),
                    ):
                        cells.extend(f.pos)
                newgp = gp.get_gridded_perm_in_cells(cells)
                newgps.append(newgp)
                if len(gp) != len(newgp):
                    changed = True
            if changed:
                # TODO: smarter to update requirement?
                cleaned_reqs.append(MinimalGriddedPermSet(newgps))
            else:
                cleaned_reqs.append(requirement)

        return cleaned_reqs

    @cssmethodtimer("GriddedPermReduction.remove_avoided")
    def remove_avoided(
        self,
        requirements: List[MinimalGriddedPermSet],
        obstructions: Optional[MinimalGriddedPermSet] = None,
    ) -> List[MinimalGriddedPermSet]:
        if obstructions is None:
            obstructions = self._obstructions
        res: List[MinimalGriddedPermSet] = list()
        for requirement in requirements:
            # If any gridded permutation in list is empty then you vacuously
            # contain this requirement
            if not all(requirement):
                continue
            redundant: Set[int] = set()
            for i, gpi in enumerate(requirement):
                for j in range(i + 1, len(requirement)):
                    if j not in redundant:
                        if gpi in requirement[j]:
                            redundant.add(j)
                if i not in redundant:
                    if any(ob in gpi for ob in obstructions):
                        redundant.add(i)
            if redundant:
                # TODO: this doesn't need to be minimized
                cleanreq = MinimalGriddedPermSet(
                    gp for i, gp in enumerate(requirement) if i not in redundant
                )
                # If cleanreq is empty, then can not contain this requirement so
                # the tiling is empty.
                if not cleanreq:
                    return [MinimalGriddedPermSet([])]
                res.append(cleanreq)
            else:
                res.append(requirement)
        return res

    @cssmethodtimer("GriddedPermReduction.remove_redundant_requirements")
    def remove_redundant_requirements(
        self, requirements: List[MinimalGriddedPermSet],
    ) -> Tuple[MinimalGriddedPermSet, ...]:
        """
        Remove all redundant requirement lists.
        It is redundant if either:
            - all of gridded perms contain some gridded permutation in the
            same other requirement.
            - all of the factors of the gridded permutations in the requirement
            are contained in some other gridded permutation from the same other
            requirement. (Is checking just this enough?)
        """
        idx_to_remove: Set[int] = set()
        for i, requirement in enumerate(requirements):
            if i not in idx_to_remove:
                for j, other_requirement in enumerate(requirements):
                    if i != j and j not in idx_to_remove:
                        if all(
                            self._griddedperm_implied_by_requirement(
                                gp, other_requirement
                            )
                            for gp in requirement
                        ):
                            idx_to_remove.add(i)

        for i, requirement in enumerate(requirements):
            if i in idx_to_remove:
                continue
            factored_requirement = [r.factors() for r in requirement]
            # if every factor of every requirement in a list is implied by
            # another requirement then we can remove this requirement list
            for factors in factored_requirement:
                if all(
                    self._griddedperm_implied_by_some_requirement(
                        factor,
                        (
                            other_requirement
                            for j, other_requirement in enumerate(requirements)
                            if i != j and j not in idx_to_remove
                        ),
                    )
                    for factor in factors
                ):
                    idx_to_remove.add(i)
                    break
        return tuple(
            sorted(
                requirement
                for idx, requirement in enumerate(requirements)
                if idx not in idx_to_remove
            )
        )

    @cssmethodtimer("GriddedPermReduction._griddedperm_implied_by_requirement")
    def _griddedperm_implied_by_requirement(
        self, griddedperm: GriddedPerm, requirement: Iterable[GriddedPerm]
    ):
        """
        Return True, if the containment of the gridded perm is implied by
        the containment of the requirement.
        """
        return all(griddedperm in gp for gp in requirement)

    @cssmethodtimer("GriddedPermReduction._griddedperm_implied_by_some_requirement")
    def _griddedperm_implied_by_some_requirement(
        self,
        griddedperm: GriddedPerm,
        requirements: Optional[Iterable[MinimalGriddedPermSet]] = None,
    ):
        """
        Return True if the containiment some requirement implies the
        containment griddedperm.
        """
        if requirements is None:
            requirements = self._requirements
        return any(
            self._griddedperm_implied_by_requirement(griddedperm, requirement)
            for requirement in requirements
        )

    @cssmethodtimer("_requirement_implied_by_requirement")
    def _requirement_implied_by_requirement(
        self,
        requirement: Iterable[GriddedPerm],
        other_requirement: Iterable[GriddedPerm],
    ):
        """
        Return True if the containment of requirement is implied by the
        containment of other_requirement.
        """
        return all(any(g2 in g1 for g2 in other_requirement) for g1 in requirement)

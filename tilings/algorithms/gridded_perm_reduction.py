from collections import defaultdict
from functools import partial
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

from comb_spec_searcher.utils import cssmethodtimer

from ..griddedperm import GriddedPerm

Cell = Tuple[int, int]
Requirement = Tuple[GriddedPerm, ...]

func_calls: Dict[str, int] = defaultdict(int)
func_times: Dict[str, float] = defaultdict(float)


class GriddedPermReduction:
    func_calls = func_calls
    func_times = func_times
    passes: Dict[int, int] = defaultdict(int)

    @cssmethodtimer("GriddedPermReduction.__init__")
    def __init__(
        self,
        obstructions: Tuple[GriddedPerm, ...],
        requirements: Tuple[Tuple[GriddedPerm, ...], ...],
        sorted_input: bool = False,
    ):
        # Only using MGP for typing purposes.
        if sorted_input:
            self._obstructions = obstructions
            self._requirements = requirements
        else:
            self._obstructions = tuple(sorted(obstructions))
            self._requirements = tuple(sorted(tuple(sorted(r)) for r in requirements))

        self._minimize_griddedperms()

    @property
    def obstructions(self):
        return tuple(self._obstructions)

    @property
    def requirements(self):
        return tuple(tuple(requirement) for requirement in self._requirements)

    @cssmethodtimer("GriddedPermReduction._minimize_griddedperms")
    def _minimize_griddedperms(self) -> None:
        """Minimizes the set of obstructions and the set of requirement lists.
        The set of obstructions are first reduced to a minimal set. The
        requirements that contain any obstructions are removed from their
        respective lists. If any requirement list is empty, then the tiling is
        empty.
        """

        def set_empty():
            self._obstructions = (GriddedPerm.empty_perm(),)
            self._requirements = tuple()

        self._obstructions = self._minimize(self._obstructions)

        i = 0
        while True:
            i += 1
            # Minimize the set of obstructions
            minimized_obs = self.minimal_obs()

            if minimized_obs and not minimized_obs[0]:
                set_empty()
                break

            # Minimize the set of requiriments
            minimized_requirements = self.minimal_reqs(minimized_obs)

            if minimized_requirements and not minimized_requirements[0]:
                set_empty()
                break

            if (
                self._obstructions == minimized_obs
                and self._requirements == minimized_requirements
            ):
                break

            self._obstructions = minimized_obs
            self._requirements = minimized_requirements
        GriddedPermReduction.passes[i] += 1

    @cssmethodtimer("GriddedPermReduction._clean_isolated")
    def _clean_isolated(self, obstruction: GriddedPerm) -> GriddedPerm:
        """Remove the isolated factors that are implied by requirements
        from all obstructions."""
        for factor in obstruction.factors():
            if self._griddedperm_implied_by_some_requirement(factor):
                obstruction = obstruction.remove_cells(factor.pos)
        return obstruction

    @cssmethodtimer("GriddedPermReduction.minimal_obs")
    def minimal_obs(self) -> Tuple[GriddedPerm, ...]:
        return self._minimize(self._clean_isolated(ob) for ob in self._obstructions)

    @cssmethodtimer("GriddedPermReduction.minimal_reqs")
    def minimal_reqs(
        self, obstructions: Tuple[GriddedPerm, ...]
    ) -> Tuple[Tuple[GriddedPerm, ...], ...]:
        algos: Tuple[Callable, ...] = (
            self.factored_reqs,
            self.cleaned_requirements,
            partial(self.remove_avoided, obstructions=obstructions),
            self.remove_redundant_requirements,
        )
        minimized_requirements = self._requirements
        for algo in algos:
            minimized_requirements = algo(minimized_requirements)
            if any(not r for r in minimized_requirements):
                return (tuple(),)
        return tuple(minimized_requirements)

    @cssmethodtimer("GriddedPermReduction.factored_reqs")
    def factored_reqs(
        self, requirements: Iterable[Tuple[GriddedPerm, ...]],
    ) -> List[Tuple[GriddedPerm, ...]]:
        """
        Add factors of requirements as size one requirements, removing them
        from each of the gridded permutations in the requirement it is
        contained in.
        """
        res: List[Tuple[GriddedPerm, ...]] = list()
        for requirement in requirements:
            if not requirement:
                # If req is empty, then this requirement can't be satisfied, so
                # return it and mark obstructions and requirements as empty.
                return [tuple()]
            # If any gridded permutation in list is empty then you vacuously
            # contain this requirement
            if all(requirement):
                factors = self.factors(requirement)
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
                    res.append((factor,))
                res.append(
                    tuple(
                        gp.get_gridded_perm_in_cells(remaining_cells)
                        for gp in requirement
                    )
                )
        return res

    @cssmethodtimer("GriddedPermReduction.cleaned_requirements")
    def cleaned_requirements(
        self, requirements: List[Tuple[GriddedPerm, ...]]
    ) -> List[Tuple[GriddedPerm, ...]]:
        """
        Remove the factors of a gridded permutation in a requirement if it is
        implied by another requirement.
        """
        cleaned_reqs: List[Tuple[GriddedPerm, ...]] = []
        for requirement in requirements:
            if not all(requirement):
                continue
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
            cleaned_reqs.append(tuple(newgps))
        return cleaned_reqs

    @cssmethodtimer("GriddedPermReduction.remove_avoided")
    def remove_avoided(
        self,
        requirements: List[Tuple[GriddedPerm, ...]],
        obstructions: Optional[Tuple[GriddedPerm, ...]] = None,
    ) -> List[Tuple[GriddedPerm, ...]]:
        if obstructions is None:
            obstructions = self._obstructions
        res: List[Tuple[GriddedPerm, ...]] = []
        for requirement in requirements:
            # If any gridded permutation in list is empty then you vacuously
            # contain this requirement
            if not all(requirement):
                continue
            cleanreq = tuple(
                gp for gp in self._minimize(requirement) if gp.avoids(*obstructions)
            )
            # If cleanreq is empty, then can not contain this requirement so
            # the tiling is empty.
            if not cleanreq:
                return [tuple()]
            res.append(cleanreq)
        return res

    @cssmethodtimer("GriddedPermReduction.remove_redundant_requirements")
    def remove_redundant_requirements(
        self, requirements: List[Tuple[GriddedPerm, ...]],
    ) -> List[Tuple[GriddedPerm, ...]]:
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
            for j, other_requirement in enumerate(requirements):
                if i != j and j not in idx_to_remove:
                    if all(
                        self._griddedperm_implied_by_requirement(gp, other_requirement)
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
        return sorted(
            requirement
            for idx, requirement in enumerate(requirements)
            if idx not in idx_to_remove
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
        requirements: Optional[Iterable[Tuple[GriddedPerm, ...]]] = None,
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

    @cssmethodtimer("GriddPermReduction._minimize")
    def _minimize(self, griddedperms: Iterable[GriddedPerm]) -> Tuple[GriddedPerm, ...]:
        """
        Removes non minimal gridded permutations from the set.
        """
        res: Set[GriddedPerm] = set()
        for gp_to_add in tuple(sorted(griddedperms)):
            if gp_to_add not in res and all(
                gp_already_added not in gp_to_add
                for gp_already_added in res
                if len(gp_already_added) < len(gp_to_add)
            ):
                res.add(gp_to_add)
        return tuple(res)

    @cssmethodtimer("GriddedPermReduction.factors")
    def factors(self, griddedperms: Tuple[GriddedPerm, ...]) -> Set[GriddedPerm]:
        res: Set[GriddedPerm] = set(griddedperms[0].factors())
        for gp in griddedperms[1:]:
            if not res:
                break
            res = res.intersection(gp.factors())
        return res

    @cssmethodtimer("GriddedPermReduction.union_subgps")
    def union_subgps(
        self, griddedperms: Iterable[GriddedPerm], other: Iterable[GriddedPerm]
    ) -> Tuple[GriddedPerm, ...]:
        other = self._minimize(other)
        return tuple(
            sorted(tuple(gp for gp in griddedperms if gp.avoids(*other)) + other)
        )

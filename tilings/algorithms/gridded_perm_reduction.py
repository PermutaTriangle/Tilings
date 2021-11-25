from collections import defaultdict
from functools import partial
from itertools import chain, combinations, islice
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

from ..griddedperm import GriddedPerm

Cell = Tuple[int, int]
Requirement = Tuple[GriddedPerm, ...]


class GriddedPermReduction:
    def __init__(
        self,
        obstructions: Tuple[GriddedPerm, ...],
        requirements: Tuple[Tuple[GriddedPerm, ...], ...],
        sorted_input: bool = False,
        already_minimized_obs: bool = False,
    ):
        # Only using MGP for typing purposes.
        if sorted_input:
            self._obstructions = obstructions
            self._requirements = requirements
        else:
            self._obstructions = tuple(sorted(obstructions))
            self._requirements = tuple(sorted(tuple(sorted(r)) for r in requirements))

        self._minimize_griddedperms(already_minimized_obs=already_minimized_obs)

    @property
    def obstructions(self) -> Tuple[GriddedPerm, ...]:
        return self._obstructions

    @property
    def requirements(self) -> Tuple[Requirement, ...]:
        return self._requirements

    def _minimize_griddedperms(self, already_minimized_obs=False) -> None:
        """Minimizes the set of obstructions and the set of requirement lists.
        The set of obstructions are first reduced to a minimal set. The
        requirements that contain any obstructions are removed from their
        respective lists. If any requirement list is empty, then the tiling is
        empty.
        """

        def set_empty():
            self._obstructions = (GriddedPerm.empty_perm(),)
            self._requirements = tuple()

        while True:
            # Minimize the set of obstructions
            minimized_obs = self.minimal_obs(
                already_minimized_obs=already_minimized_obs
            )

            if minimized_obs and not minimized_obs[0]:
                set_empty()
                break

            self._obstructions = tuple(sorted(minimized_obs))

            # Minimize the set of requiriments
            minimized_requirements = self.minimal_reqs(minimized_obs)
            minimized_requirements = tuple(
                sorted(tuple(sorted(set(req))) for req in minimized_requirements)
            )

            if minimized_requirements and not minimized_requirements[0]:
                set_empty()
                break

            if self._requirements == minimized_requirements:
                break

            self._requirements = minimized_requirements

    def _set_of_implied_obstructions(
        self, obstruction: GriddedPerm, requirementgp: GriddedPerm
    ) -> List[GriddedPerm]:
        """
        Detects all factors of <obstruction> whose existence is implied by
        <requirementgp>, and then returns the list of size 2^|factors| of obstructions
        formed by deleting any subset of the factors.
        """
        factor_cells: List[Set[Cell]] = []
        for factor in obstruction.factors():
            if self._griddedperm_implied_by_requirement(factor, (requirementgp,)):
                factor_cells.append(set(factor.pos))
        powerset = chain.from_iterable(
            combinations(factor_cells, r) for r in range(len(factor_cells) + 1)
        )
        return [
            obstruction.remove_cells(set.union(*cell_set)) if cell_set else obstruction
            for cell_set in powerset
        ]

    def minimal_obs(
        self, already_minimized_obs: bool = False
    ) -> Tuple[GriddedPerm, ...]:
        min_perms = (
            self._obstructions
            if already_minimized_obs
            else GriddedPermReduction._minimize(self._obstructions)
        )

        # helper function for combining sets of implied obs
        def _obs_star(
            obs1: Tuple[GriddedPerm, ...], obs2: Tuple[GriddedPerm, ...]
        ) -> Tuple[GriddedPerm, ...]:
            """
            Let A = <obs1> and B = <obs2>. A * B is the set
                {a in A : b <= a for some b in B}
                union
                {b in B : a <= b for some a in A}
            In the context of a full set O that A and B come from, A * B is the set of all
            sub-factor-perms of O that contain both a perm in A and a perm in B.
            """
            return tuple(
                {o1 for o1 in obs1 if any(o1.contains(o2) for o2 in obs2)}.union(
                    {o2 for o2 in obs2 if any(o2.contains(o1) for o1 in obs1)}
                )
            )

        new_obs = min_perms
        while new_obs:
            next_obs = new_obs
            for requirement in self._requirements:
                this_req_obs: Tuple[GriddedPerm, ...] = tuple()
                if requirement:
                    for req_gp in requirement:
                        union_set: Set[GriddedPerm] = set()
                        implied_obs = tuple(
                            union_set.union(
                                *[
                                    self._set_of_implied_obstructions(ob, req_gp)
                                    for ob in next_obs
                                ]
                            )
                        )
                        if not this_req_obs:
                            # if this is the first time that we have interesting
                            #  implied_obs, just save them
                            this_req_obs = implied_obs
                        else:
                            # otherwise we have to do the * operation
                            this_req_obs = _obs_star(this_req_obs, implied_obs)
                next_obs = GriddedPermReduction._minimize(this_req_obs)
            # if nothing changed, break out of the while loop
            next_obs = tuple(sorted(next_obs))
            if next_obs == new_obs:
                break
            new_obs = next_obs
        return new_obs

    def minimal_reqs(
        self, obstructions: Tuple[GriddedPerm, ...]
    ) -> Tuple[Requirement, ...]:
        algos: Tuple[Callable, ...] = (
            GriddedPermReduction.factored_reqs,
            self.remove_redundant,
            self.cleaned_requirements,
            partial(self.remove_avoided, obstructions=obstructions),
        )
        minimized_requirements = self._requirements
        for algo in algos:
            minimized_requirements = algo(minimized_requirements)
            if any(not r for r in minimized_requirements):
                return (tuple(),)
        return tuple(minimized_requirements)

    def remove_redundant(self, requirements: List[Requirement]) -> List[Requirement]:
        relevant_reqs: List[Requirement] = []
        for idx, requirement in enumerate(requirements):
            if not all(requirement):
                continue
            if self._requirement_implied_by_some_requirement(
                requirement,
                chain(
                    islice(requirements, idx),
                    (
                        gps
                        for gps in islice(requirements, idx + 1, None)
                        if gps != requirement
                    ),
                ),
            ):
                # we only keep requirements which are not implies by other
                # requirements
                continue
            relevant_reqs.append(requirement)
        return relevant_reqs

    # If all of the gp's in a requirment list contain the same factor, you can remove
    # that factor from all of them and add it as it's own size one requirement list
    # [size one requirement list inferral]
    @staticmethod
    def factored_reqs(requirements: Iterable[Requirement]) -> List[Requirement]:
        """
        Add factors of requirements as size one requirements, removing them
        from each of the gridded permutations in the requirement it is
        contained in.
        """
        res: List[Requirement] = []
        for requirement in requirements:
            if not requirement:
                # If req is empty, then this requirement can't be satisfied, so
                # return it and mark obstructions and requirements as empty.
                return [tuple()]
            # If any gridded permutation in list is empty then you vacuously
            # contain this requirement
            if all(requirement):
                factors = GriddedPermReduction.factors(requirement)
                if not factors or (len(factors) == 1 and len(requirement) == 1):
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

    # if a gridded perm G in a requirment has a factor that appears in EVERY gridded
    # perm of some other requirement, then that factor can be removed from G
    # [subrequirement inferral]
    def cleaned_requirements(
        self, requirements: List[Requirement]
    ) -> List[Requirement]:
        """
        Remove the factors of a gridded permutation in a requirement if it is
        implied by another requirement.
        """
        for idx, requirement in enumerate(requirements):
            newgps: List[GriddedPerm] = []
            for gp in requirement:
                cells: List[Cell] = []
                for f in gp.factors():
                    if not self._griddedperm_implied_by_some_requirement(
                        f,
                        chain(
                            islice(requirements, idx),
                            islice(requirements, idx + 1, None),
                        ),
                    ):
                        cells.extend(f.pos)
                newgp = gp.get_gridded_perm_in_cells(cells)
                newgps.append(newgp)
            requirements[idx] = tuple(newgps)
        return requirements

    # We can remove any gridded perm in any requirement if the gridded perm contains
    # an obstruction
    # [requirement component deletion]
    def remove_avoided(
        self,
        requirements: List[Requirement],
        obstructions: Optional[Tuple[GriddedPerm, ...]] = None,
    ) -> List[Requirement]:
        if obstructions is None:
            obstructions = self._obstructions
        res: List[Requirement] = []
        for requirement in requirements:
            # If any gridded permutation in list is empty then you vacuously
            # contain this requirement
            if not all(requirement):
                continue
            cleanreq = tuple(
                gp
                for gp in GriddedPermReduction._minimize(requirement)
                if gp.avoids(*obstructions)
            )
            # If cleanreq is empty, then can not contain this requirement so
            # the tiling is empty.
            if not cleanreq:
                return [tuple()]
            if not (len(cleanreq) == 1 and not cleanreq[0]):
                res.append(cleanreq)
        return res

    @staticmethod
    def _griddedperm_implied_by_requirement(
        griddedperm: GriddedPerm, requirement: Iterable[GriddedPerm]
    ):
        """
        Return True, if the containment of the gridded perm is implied by
        the containment of the requirement.
        """
        return all(griddedperm in gp for gp in requirement)

    # detect if there exists a requirement such that every component in that requirement
    # contains griddedperm
    def _griddedperm_implied_by_some_requirement(
        self,
        griddedperm: GriddedPerm,
        requirements: Optional[Iterable[Requirement]] = None,
    ):
        """
        Return True if the containiment some requirement implies the
        containment griddedperm.
        """
        if requirements is None:
            requirements = self._requirements
        return any(
            GriddedPermReduction._griddedperm_implied_by_requirement(
                griddedperm, requirement
            )
            for requirement in requirements
        )

    def _requirement_implied_by_some_requirement(
        self,
        requirement: Requirement,
        requirements: Iterable[Requirement],
    ) -> bool:
        """
        Return True if one of the requirements implies the containment of requirement.
        """
        return any(
            self._requirement_implied_by_requirement(requirement, req)
            for req in requirements
        )

    @staticmethod
    def _requirement_implied_by_requirement(
        requirement: Requirement, other_requirement: Requirement
    ) -> bool:
        """
        Return True if the containment of other implies a containment of requirement.
        """
        return all(
            any(other_gp.contains(gp) for gp in requirement)
            for other_gp in other_requirement
        )

    @staticmethod
    def _minimize(griddedperms: Iterable[GriddedPerm]) -> Tuple[GriddedPerm, ...]:
        """
        Removes non-minimal gridded permutations from the set.
        """
        perms_by_size: Dict[int, List[GriddedPerm]] = defaultdict(list)
        for gp in griddedperms:
            perms_by_size[len(gp)].append(gp)
        sizes = sorted(perms_by_size.keys())
        if not sizes:
            return tuple()
        minimal_perms = set(perms_by_size[sizes[0]])
        for size in sizes[1:]:
            next_layer = set()
            for gp in perms_by_size[size]:
                if gp.avoids(*minimal_perms):
                    next_layer.add(gp)
            minimal_perms |= next_layer
        return tuple(minimal_perms)

    @staticmethod
    def factors(griddedperms: Tuple[GriddedPerm, ...]) -> Set[GriddedPerm]:
        res: Set[GriddedPerm] = set(griddedperms[0].factors())
        for gp in griddedperms[1:]:
            if not res:
                break
            res = res.intersection(gp.factors())
        return res

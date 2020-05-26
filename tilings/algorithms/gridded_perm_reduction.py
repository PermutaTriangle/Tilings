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

    @cssmethodtimer("GriddedPermReduction.__init__")
    def __init__(
        self,
        obstructions: Tuple[GriddedPerm, ...],
        requirements: Tuple[Tuple[GriddedPerm, ...], ...],
        sorted_input: bool = False,
        already_min: bool = False,
    ):
        # Only using MGP for typing purposes.
        if sorted_input:
            self._obstructions = obstructions
            self._requirements = requirements
        else:
            self._obstructions = tuple(sorted(obstructions))
            self._requirements = tuple(sorted(tuple(sorted(r)) for r in requirements))

        self._minimize_griddedperms(already_min=already_min)

    @property
    def obstructions(self):
        return tuple(self._obstructions)

    @property
    def requirements(self):
        return tuple(tuple(requirement) for requirement in self._requirements)

    @cssmethodtimer("GriddedPermReduction._minimize_griddedperms")
    def _minimize_griddedperms(self, already_min=False) -> None:
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
            minimized_obs = self.minimal_obs(already_min=already_min)

            if minimized_obs and not minimized_obs[0]:
                set_empty()
                break

            self._obstructions = tuple(sorted(minimized_obs))

            # Minimize the set of requiriments
            minimized_requirements = self.minimal_reqs(minimized_obs)
            minimized_requirements = tuple(
                [tuple(sorted(req)) for req in minimized_requirements]
            )

            if minimized_requirements and not minimized_requirements[0]:
                set_empty()
                break

            if self._requirements == minimized_requirements:
                break

            self._requirements = minimized_requirements

    # if there is a requirement for which every component contains the same factor of
    # obstruction, then that factor can be removed from obstruction
    # [subobstruction inferral]
    @cssmethodtimer("GriddedPermReduction._clean_isolated")
    def _clean_isolated(self, obstruction: GriddedPerm) -> GriddedPerm:
        """Remove the isolated factors that are implied by requirements
        from all obstructions."""
        cells_to_remove: Set[Cell] = set()
        for factor in obstruction.factors():
            if self._griddedperm_implied_by_some_requirement(factor):
                cells_to_remove.update(factor.pos)
        if len(cells_to_remove) > 0:
            obstruction = obstruction.remove_cells(cells_to_remove)
        return obstruction

    @cssmethodtimer("GriddedPermReduction.minimal_obs")
    def minimal_obs(self, already_min=False) -> Tuple[GriddedPerm, ...]:
        min_perms = (
            self._obstructions
            if already_min
            else GriddedPermReduction._minimize(self._obstructions)
        )
        changed = []
        unchanged = []
        for ob in min_perms:
            cleaned_perm = self._clean_isolated(ob)
            if cleaned_perm == ob:
                unchanged.append(cleaned_perm)
            else:
                changed.append(cleaned_perm)
        if len(changed) == 0:
            return tuple(unchanged)

        return GriddedPermReduction._minimize(changed) + tuple(
            [gp for gp in unchanged if gp.avoids(*changed)]
        )

    @cssmethodtimer("GriddedPermReduction.minimal_reqs")
    def minimal_reqs(
        self, obstructions: Tuple[GriddedPerm, ...]
    ) -> Tuple[Tuple[GriddedPerm, ...], ...]:
        algos: Tuple[Callable, ...] = (
            GriddedPermReduction.factored_reqs,
            self.cleaned_requirements,
            partial(self.remove_avoided, obstructions=obstructions),
        )
        minimized_requirements = self._requirements
        for algo in algos:
            minimized_requirements = algo(minimized_requirements)
            if any(not r for r in minimized_requirements):
                return (tuple(),)
        return tuple(sorted(minimized_requirements))

    # If all of the gp's in a requirment list contain the same factor, you can remove
    # that factor from all of them and add it as it's own size one requirement list
    # [size one requirement list inferral]
    # @cssmethodtimer("GriddedPermReduction.factored_reqs")
    @staticmethod
    def factored_reqs(
        requirements: Iterable[Tuple[GriddedPerm, ...]],
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
                factors = GriddedPermReduction.factors(requirement)
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

    # if a gridded perm G in a requirment has a factor that appears in EVERY gridded
    # perm of some other requirement, then that factor can be removed from G
    # [subrequirement inferral]
    # NOTE: This handles the following case:
    #   requirement R2 makes requirement R1 redundant if:
    #   For all G in R2, there exists H in R1 such that H <= G
    @cssmethodtimer("GriddedPermReduction.cleaned_requirements")
    def cleaned_requirements(
        self, requirements: List[Tuple[GriddedPerm, ...]]
    ) -> List[Tuple[GriddedPerm, ...]]:
        """
        Remove the factors of a gridded permutation in a requirement if it is
        implied by another requirement.
        """
        for idx, requirement in enumerate(requirements):
            if not all(requirement):
                continue
            newgps: List[GriddedPerm] = []
            for gp in requirement:
                cells: List[Cell] = []
                for f in gp.factors():
                    if not self._griddedperm_implied_by_some_requirement(
                        f,
                        (
                            other_requirement
                            for other_idx, other_requirement in enumerate(requirements)
                            if idx != other_idx
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
                gp
                for gp in GriddedPermReduction._minimize(requirement)
                if gp.avoids(*obstructions)
            )
            # If cleanreq is empty, then can not contain this requirement so
            # the tiling is empty.
            if not cleanreq:
                return [tuple()]
            if not (len(cleanreq) == 1 and len(cleanreq[0]) == 0):
                res.append(cleanreq)
        return res

    # @cssmethodtimer("GriddedPermReduction._griddedperm_implied_by_requirement")
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
            GriddedPermReduction._griddedperm_implied_by_requirement(
                griddedperm, requirement
            )
            for requirement in requirements
        )

    # Is this not a staticmethod because then it messes with cssmethodtimer?
    @staticmethod
    # @cssmethodtimer("GriddedPermReduction._minimize")
    def _minimize(griddedperms: Iterable[GriddedPerm]) -> Tuple[GriddedPerm, ...]:
        """
        Removes non-minimal gridded permutations from the set.
        """
        perms_by_size: Dict[int, List[GriddedPerm]] = defaultdict(list)
        for gp in griddedperms:
            perms_by_size[len(gp)].append(gp)
        sizes = sorted(perms_by_size.keys())
        if len(sizes) == 0:
            return tuple()
        minimal_perms = set(perms_by_size[sizes[0]])
        for size in sizes[1:]:
            next_layer = set()
            for gp in perms_by_size[size]:
                if gp.avoids(*minimal_perms):
                    next_layer.add(gp)
            minimal_perms |= next_layer
        return tuple(minimal_perms)

    @cssmethodtimer("GriddedPermReduction._OLD_minimize")
    def _OLD_minimize(
        self, griddedperms: Iterable[GriddedPerm]
    ) -> Tuple[GriddedPerm, ...]:
        """
        Removes non minimal gridded permutations from the set.
        """
        # assert False, "Use the new one!"
        res: Set[GriddedPerm] = set()
        for gp_to_add in tuple(sorted(griddedperms)):
            if all(
                gp_already_added not in gp_to_add
                for gp_already_added in res
                if len(gp_already_added) < len(gp_to_add)
            ):
                res.add(gp_to_add)
        return tuple(res)

    # @cssmethodtimer("GriddedPermReduction.factors")
    @staticmethod
    def factors(griddedperms: Tuple[GriddedPerm, ...]) -> Set[GriddedPerm]:
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
        other = GriddedPermReduction._minimize(other)
        return tuple(
            sorted(tuple(gp for gp in griddedperms if gp.avoids(*other)) + other)
        )

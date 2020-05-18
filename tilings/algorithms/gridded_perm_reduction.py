from typing import Iterable, Iterator, List, Set, Tuple

from ..griddedperm import GriddedPerm

Cell = Tuple[int, int]
Requirement = Tuple[GriddedPerm, ...]


class MinimalGriddedPermSet:
    def __init__(self, griddedperms: Iterable[GriddedPerm]):
        self.griddedperms: Tuple[GriddedPerm, ...] = tuple(sorted(griddedperms))
        self._minimize()

    def _minimize(self) -> None:
        """
        Removes non minimal gridded permutations from the set.
        """
        res: List[GriddedPerm] = []
        for gp_to_add in self.griddedperms:
            if all(gp_already_added not in gp_to_add for gp_already_added in res):
                res.append(gp_to_add)
        self.griddedperms = tuple(sorted(res))

    def factors(self) -> Set[GriddedPerm]:
        if self.griddedperms:
            res: Set[GriddedPerm] = set(self.griddedperms[0].factors())
            for gp in self.griddedperms[1:]:
                if not res:
                    break
                res = res.intersection(gp.factors())
        return res

    def __eq__(self, other):
        return self.griddedperms == other.griddedperms

    def __len__(self) -> int:
        return len(self.griddedperms)

    def __lt__(self, other):
        if isinstance(other, MinimalGriddedPermSet):
            return self.griddedperms < other.griddedperms
        raise NotImplementedError("Can only compare two MinimalGriddedPermSet")

    def __iter__(self) -> Iterator[GriddedPerm]:
        return iter(self.griddedperms)

    def __repr__(self):
        return self.__class__.__name__ + "({})".format(
            ", ".join(repr(gp) for gp in self.griddedperms)
        )

    def __str__(self):
        return "{{{}}}".format(", ".join(str(gp) for gp in self.griddedperms))


class GriddedPermReduction:
    def __init__(
        self,
        obstructions: Iterable[GriddedPerm],
        requirements: Iterable[Iterable[GriddedPerm]],
    ):
        self._requirements = tuple(
            sorted(MinimalGriddedPermSet(r) for r in requirements)
        )
        self._obstructions = MinimalGriddedPermSet(
            [self._clean_isolated(ob) for ob in obstructions]
        )
        self._minimize_griddedperms()

    @property
    def obstructions(self):
        return tuple(sorted(self._obstructions))

    @property
    def requirements(self):
        return tuple(
            sorted(tuple(sorted(requirement)) for requirement in self._requirements)
        )

    def _clean_isolated(self, obstruction: GriddedPerm) -> GriddedPerm:
        """Remove the isolated factors that are implied by requirements
        from all obstructions."""
        for factor in obstruction.factors():
            if any(
                all(factor in gp for gp in requirement)
                for requirement in self._requirements
            ):
                obstruction = obstruction.remove_cells(factor.pos)
        return obstruction

    def _minimize_griddedperms(self) -> None:
        """Minimizes the set of obstructions and the set of requirement lists.
        The set of obstructions are first reduced to a minimal set. The
        requirements that contain any obstructions are removed from their
        respective lists. If any requirement list is empty, then the tiling is
        empty.
        """
        while True:
            # Minimize the set of obstructions
            minimized_obs = MinimalGriddedPermSet(
                [self._clean_isolated(ob) for ob in self._obstructions]
            )
            # Minimize the set of requiriments
            factored_reqs = self.factored_reqs(self._requirements)
            cleaned_requirements = self.cleaned_requirements(factored_reqs)
            relevant_requirements = self.remove_avoided(cleaned_requirements)
            minimized_requirements = self.remove_redundant_requirements(
                relevant_requirements
            )
            if any(not r for r in minimized_requirements) or any(
                len(gp) == 0 for gp in minimized_obs
            ):
                self._obstructions = MinimalGriddedPermSet([GriddedPerm.empty_perm()])
                self._requirements = tuple()
                break

            if (
                self._obstructions == minimized_obs
                and self._requirements == minimized_requirements
            ):
                break
            self._obstructions = minimized_obs
            self._requirements = minimized_requirements

    @staticmethod
    def factored_reqs(
        requirements: Iterable[MinimalGriddedPermSet],
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
                factors = requirement.factors()
                if len(factors) == 0 or (len(factors) == 1 and len(requirement) == 1):
                    # if there are no factors in the intersection, or it is just
                    # the same req as the first, we do nothing and add the original
                    res.append(tuple(requirement))
                    continue
                # add each of the factors as a single requirement, and then remove
                # these from each of the other requirements in the list
                remaining_cells = set(c for gp in requirement for c in gp.pos) - set(
                    c for gp in factors for c in gp.pos
                )
                for factor in factors:
                    res.append((factor,))
                rem_requirement = tuple(
                    gp.get_gridded_perm_in_cells(remaining_cells) for gp in requirement
                )
                res.append(rem_requirement)
        return res

    @staticmethod
    def cleaned_requirements(
        requirements: List[Tuple[GriddedPerm, ...]]
    ) -> List[List[GriddedPerm]]:
        """
        Remove the factors of a gridded permutation in a requirement if it is
        implied by another requirement.
        """
        cleaned_reqs: List[List[GriddedPerm]] = []
        for requirement in requirements:
            if all(requirement):
                cleaned_req = []
                for gp in requirement:
                    cells: List[Cell] = []
                    for f in gp.factors():
                        # if factor implied by some requirement list then we
                        # remove it from the gridded perm
                        if not any(
                            all(f in g for g in other_requirement)
                            for other_requirement in requirements
                            if not all(
                                any(g2 in g1 for g2 in requirement)
                                for g1 in other_requirement
                            )
                        ):
                            cells.extend(f.pos)
                    cleaned_req.append(gp.get_gridded_perm_in_cells(cells))
            cleaned_reqs.append(cleaned_req)
        return cleaned_reqs

    def remove_avoided(
        self, requirements: List[List[GriddedPerm]]
    ) -> List[List[GriddedPerm]]:
        res: List[List[GriddedPerm]] = list()
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
                    if any(ob in gpi for ob in self._obstructions):
                        redundant.add(i)
            cleanreq = [gp for i, gp in enumerate(requirement) if i not in redundant]
            # If cleanreq is empty, then can not contain this requirement so
            # the tiling is empty.
            if not cleanreq:
                return [[]]
            res.append(cleanreq)
        return res

    @staticmethod
    def remove_redundant_requirements(
        requirements: List[List[GriddedPerm]],
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
                            any(g2 in g1 for g2 in other_requirement)
                            for g1 in requirement
                        ):
                            idx_to_remove.add(j)

        for i, requirement in enumerate(requirements):
            if i not in idx_to_remove:
                factored_requirement = [r.factors() for r in requirement]
                # if every factor of every requirement in a list is implied by
                # another requirement then we can remove this requirement list
                for factors in factored_requirement:
                    if all(
                        any(
                            all(factor in gp for gp in other_requirement)
                            for j, other_requirement in enumerate(requirements)
                            if i != j and j not in idx_to_remove
                        )
                        for factor in factors
                    ):
                        idx_to_remove.add(i)
                        break
        return tuple(
            sorted(
                MinimalGriddedPermSet(requirement)
                for idx, requirement in enumerate(requirements)
                if idx not in idx_to_remove
            )
        )

import itertools
import logging
from typing import Dict, Optional, Set, Tuple

from logzero import logger

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
)
from comb_spec_searcher.strategies.constructor import CartesianProduct, DisjointUnion
from comb_spec_searcher.strategies.rule import Rule, VerificationRule
from permuta import Basis, Perm
from tilings import GriddedPerm, Tiling


class LocallyFactorableShift:
    def __init__(
        self, rule: VerificationRule[Tiling, GriddedPerm], basis: Tuple[Perm, ...]
    ) -> None:
        self.rule = rule
        self.basis = Basis(*basis)
        self.spec = self._get_spec()
        self.traverse_cache: Dict[Tiling, Optional[int]] = {}

    def _get_spec(self) -> CombinatorialSpecification[Tiling, GriddedPerm]:
        pack = self.rule.pack()
        logger.setLevel(logging.WARN)
        css = CombinatorialSpecificationSearcher(self.rule.comb_class, pack)
        spec = css.auto_search()
        logger.setLevel(logging.INFO)
        return spec

    @staticmethod
    def cell_basis(t: Tiling) -> Set[Basis]:
        """
        Return the one by one classes in the cells.
        """
        all_bases: Set[Basis] = set()
        for obs, _ in t.cell_basis().values():
            b = Basis.from_iterable(obs)
            all_bases.add(b)
        return all_bases

    def _reliance(self, t: Tiling) -> Optional[int]:
        """
        Return the reliance of the tiling on the basis according to the spec.
        """
        rule = self.spec.rules_dict[t]
        if t in self.traverse_cache:
            return self.traverse_cache[t]
        if self.basis not in self.cell_basis(t):
            res = None
        elif t.dimensions == (1, 1):
            res = 0
        elif isinstance(rule, VerificationRule):
            res = LocallyFactorableShift(rule, self.basis).shift()
        elif isinstance(rule, Rule) and isinstance(rule.constructor, DisjointUnion):
            children_reliance = [self._reliance(c) for c in rule.children]
            res = min([r for r in children_reliance if r is not None], default=None)
        elif isinstance(rule, Rule) and isinstance(rule.constructor, CartesianProduct):
            min_points = [len(next(c.minimal_gridded_perms())) for c in rule.children]
            point_sum = sum(min_points)
            shifts = [point_sum - mpoint for mpoint in min_points]
            children_reliance = [self._reliance(c) for c in rule.children]
            res = min(
                [r + s for r, s in zip(children_reliance, shifts) if r is not None],
                default=None,
            )
        else:
            raise NotImplementedError(rule)
        self.traverse_cache[t] = res
        return res

    def shift_from_spec(self) -> int:
        res = self._reliance(self.rule.comb_class)
        assert res is not None
        return res

    def shift_from_theory(self) -> int:
        """
        The shift from the conjectured formula.
        """
        min_gps = self.rule.comb_class.minimal_gridded_perms()
        cells_with_basis = [
            cell
            for cell, (obs, _) in self.rule.comb_class.cell_basis().items()
            if Basis.from_iterable(obs) == self.basis
        ]
        return min(
            sum(1 for c in gp.pos if c != cell)
            for cell, gp in itertools.product(cells_with_basis, min_gps)
        )

    def shift(self) -> int:
        from_spec = self.shift_from_spec()
        from_conjecture = self.shift_from_theory()
        assert from_spec == from_conjecture
        return from_conjecture

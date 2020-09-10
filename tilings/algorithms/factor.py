from collections import defaultdict
from itertools import chain, combinations
from typing import TYPE_CHECKING, Dict, Iterable, Iterator, List, Optional, Set, Tuple

from permuta.misc import UnionFind
from tilings import GriddedPerm
from tilings.assumptions import ComponentAssumption, TrackingAssumption
from tilings.misc import partitions_iterator

if TYPE_CHECKING:
    from tilings import Tiling


Cell = Tuple[int, int]
ReqList = Tuple[GriddedPerm, ...]


class Factor:
    """
    Algorithm to compute the factorisation of a tiling.

    Two active cells are in the same factor if they are in the same row
    or column, or they share an obstruction or a requirement.

    If using tracking assumptions, then two cells will also be in the same
    factor if they are covered by the same assumption.
    """

    def __init__(self, tiling: "Tiling") -> None:
        self._tiling = tiling
        self._active_cells = tiling.active_cells
        nrow = tiling.dimensions[1]
        ncol = tiling.dimensions[0]
        self._cell_unionfind = UnionFind(nrow * ncol)
        self._components: Optional[Tuple[Set[Cell], ...]] = None
        self._factors_obs_and_reqs: Optional[
            List[
                Tuple[
                    Tuple[GriddedPerm, ...],
                    Tuple[ReqList, ...],
                    Tuple[TrackingAssumption, ...],
                ]
            ]
        ] = None

    def _cell_to_int(self, cell: Cell) -> int:
        nrow = self._tiling.dimensions[1]
        return cell[0] * nrow + cell[1]

    def _int_to_cell(self, i: int) -> Cell:
        nrow = self._tiling.dimensions[1]
        return (i // nrow, i % nrow)

    def _get_cell_representative(self, cell: Cell) -> Cell:
        """
        Return the representative of a cell in the union find.
        """
        i = self._cell_to_int(cell)
        return self._cell_unionfind.find(i)  # type: ignore

    def _unite_cells(self, cells: Iterable[Cell]) -> None:
        """
        Put all the cells of `cells` in the same component of the UnionFind.
        """
        cell_iterator = iter(cells)
        try:
            c1 = next(cell_iterator)
        except StopIteration:
            return
        c1_int = self._cell_to_int(c1)
        for c2 in cell_iterator:
            c2_int = self._cell_to_int(c2)
            self._cell_unionfind.unite(c1_int, c2_int)

    def _unite_assumptions(self) -> None:
        """
        For each TrackingAssumption unite all the positions of the gridded perms.
        """
        for assumption in self._tiling.assumptions:
            if isinstance(assumption, ComponentAssumption):
                for comp in assumption.get_components(self._tiling):
                    self._unite_cells(chain.from_iterable(gp.pos for gp in comp))
            else:
                for gp in assumption.gps:
                    self._unite_cells(gp.pos)

    def _unite_obstructions(self) -> None:
        """
        For each obstruction unite all the position of the obstruction.
        """
        for ob in self._tiling.obstructions:
            self._unite_cells(ob.pos)

    def _unite_requirements(self) -> None:
        """
        For each requirement unite all the cell in all the requirements of the
        list.
        """
        for req_list in self._tiling.requirements:
            req_cells = chain.from_iterable(req.pos for req in req_list)
            self._unite_cells(req_cells)

    @staticmethod
    def _same_row_or_col(cell1: Cell, cell2: Cell) -> bool:
        """
        Test if `cell1` and `cell2` or in the same row or columns
        """
        return cell1[0] == cell2[0] or cell1[1] == cell2[1]

    def _unite_rows_and_cols(self) -> None:
        """
        Unite all the active cell that are on the same row or column.
        """
        cell_pair_to_unite = (
            c
            for c in combinations(self._active_cells, r=2)
            if self._same_row_or_col(c[0], c[1])
        )
        for c1, c2 in cell_pair_to_unite:
            self._unite_cells((c1, c2))

    def _unite_all(self) -> None:
        """
        Unite all the cells that share an obstruction, a requirement list,
        a row or a column.
        """
        self._unite_obstructions()
        self._unite_requirements()
        self._unite_assumptions()
        self._unite_rows_and_cols()

    def get_components(self) -> Tuple[Set[Cell], ...]:
        """
        Returns the tuple of all the components. Each component is set of
        cells.
        """
        if self._components is not None:
            return self._components
        self._unite_all()
        all_components: Dict[Cell, Set[Cell]] = defaultdict(set)
        for cell in self._active_cells:
            rep = self._get_cell_representative(cell)
            all_components[rep].add(cell)
        self._components = tuple(all_components.values())
        return self._components

    def _get_factors_obs_and_reqs(
        self,
    ) -> List[
        Tuple[
            Tuple[GriddedPerm, ...], Tuple[ReqList, ...], Tuple[TrackingAssumption, ...]
        ],
    ]:
        """
        Returns a list of all the irreducible factors of the tiling.
        Each factor is a tuple (obstructions, requirements)
        """
        if self._factors_obs_and_reqs is not None:
            return self._factors_obs_and_reqs
        if self._tiling.is_empty():
            return [((GriddedPerm((), []),), tuple(), tuple())]
        factors = []
        for component in self.get_components():
            obstructions = tuple(
                ob for ob in self._tiling.obstructions if ob.pos[0] in component
            )
            requirements = tuple(
                req for req in self._tiling.requirements if req[0].pos[0] in component
            )
            # TODO: consider skew/sum assumptions
            assumptions = tuple(
                ass.__class__(gp for gp in ass.gps if gp.pos[0] in component)
                for ass in self._tiling.assumptions
            )
            factors.append(
                (
                    obstructions,
                    requirements,
                    tuple(set(ass for ass in assumptions if ass.gps)),
                )
            )
        self._factors_obs_and_reqs = factors
        return self._factors_obs_and_reqs

    def factorable(self) -> bool:
        """
        Returns `True` if the tiling has more than one factor.
        """
        return len(self.get_components()) > 1

    def factors(self) -> Tuple["Tiling", ...]:
        """
        Returns all the irreducible factors of the tiling.
        """
        return tuple(
            self._tiling.__class__(
                obstructions=f[0],
                requirements=f[1],
                assumptions=tuple(sorted(f[2])),
                simplify=False,
            )
            for f in self._get_factors_obs_and_reqs()
        )

    def reducible_factorisations(self) -> Iterator[Tuple["Tiling", ...]]:
        """
        Iterator over all reducible factorisation that can be obtained by
        grouping of irreducible factors.

        Each factorisation is a list of tiling.

        For example if T = T1 x T2 x T3 then (T1 x T3) x T2 is a possible
        reducible factorisation.
        """
        min_comp = self._get_factors_obs_and_reqs()
        for partition in partitions_iterator(min_comp):
            factors = []
            for part in partition:
                obstructions, requirements, assumptions = zip(*part)
                factors.append(
                    self._tiling.__class__(
                        obstructions=chain(*obstructions),
                        requirements=chain(*requirements),
                        assumptions=tuple(sorted(chain(*assumptions))),
                        simplify=False,
                    )
                )
            yield tuple(factors)


class FactorWithMonotoneInterleaving(Factor):
    """
    Algorithm to compute the factorisation with monotone interleaving of a
    tiling.

    Two active cells are in the same factor if they share an obstruction or
    a requirement or if they are on the same row or column and are both
    non-monotone.
    """

    def _unite_rows_and_cols(self) -> None:
        """
        Unite all active cell that are on the same row or column if both of
        them are not monotone.

        Override `Factor._unite_rows_and_cols`.
        """
        cell_pair_to_unite = (
            c
            for c in combinations(self._active_cells, r=2)
            if (
                self._same_row_or_col(c[0], c[1])
                and not self._tiling.is_monotone_cell(c[0])
                and not self._tiling.is_monotone_cell(c[1])
            )
        )
        for c1, c2 in cell_pair_to_unite:
            self._unite_cells((c1, c2))


class FactorWithInterleaving(Factor):
    """
    Algorithm to compute the factorisation with interleaving of a tiling.

    Two non-empty cells are in the same factor if they share an obstruction or
    a requirement.
    """

    def _unite_rows_and_cols(self) -> None:
        """
        Override the `Factor._unite_rows_and_cols` to do nothing since
        interleaving is allowed on row and column.
        """

    def _unite_all(self) -> None:
        """
        Unite all the cells that share an obstruction or a requirement list.
        """
        self._unite_assumptions()
        self._unite_obstructions()
        self._unite_requirements()

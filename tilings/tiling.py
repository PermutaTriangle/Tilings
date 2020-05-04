# pylint: disable=too-many-locals,too-many-lines,too-many-branches
# pylint: disable=arguments-differ,attribute-defined-outside-init,
# pylint: disable=too-many-return-statements,too-many-statements
# pylint: disable=import-outside-toplevel
import json
from array import array
from collections import Counter, defaultdict
from functools import partial
from itertools import chain, product
from operator import xor
from typing import (
    Callable,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
)

import sympy

from comb_spec_searcher import CombinatorialClass
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_WEST

from .algorithms import (
    AllObstructionInferral,
    ComponentFusion,
    EmptyCellInferral,
    Factor,
    FactorWithInterleaving,
    FactorWithMonotoneInterleaving,
    Fusion,
    GriddedPermsOnTiling,
    MinimalGriddedPerms,
    ObstructionTransitivity,
    RequirementPlacement,
    RowColSeparation,
    SubobstructionInferral,
)
from .algorithms.enumeration import (
    BasicEnumeration,
    DatabaseEnumeration,
    LocallyFactorableEnumeration,
    MonotoneTreeEnumeration,
)
from .exception import InvalidOperationError
from .griddedperm import GriddedPerm
from .misc import intersection_reduce, map_cell, union_reduce
from .obstruction import Obstruction
from .requirement import Requirement

__all__ = "Tiling"


Cell = Tuple[int, int]


class Tiling(CombinatorialClass):
    """Tiling class.

    Zero-indexed coordinates/cells from bottom left corner where the (x, y)
    cell is the cell in the x-th column and y-th row.

    Tilings store the obstructions and requirements but also caches the empty
    cells and the active cells.
    """

    def __init__(
        self,
        obstructions: Iterable[Obstruction] = tuple(),
        requirements: Iterable[Iterable[Requirement]] = tuple(),
        remove_empty: bool = True,
        derive_empty: bool = True,
        minimize: bool = True,
        sorted_input: bool = False,
    ):
        super().__init__()
        if sorted_input:
            # Set of obstructions
            self._obstructions = tuple(obstructions)
            # Set of requirement lists
            self._requirements = tuple(tuple(r) for r in requirements)
        else:
            # Set of obstructions
            self._obstructions = tuple(sorted(obstructions))
            # Set of requirement lists
            self._requirements = Tiling.sort_requirements(requirements)

        # Minimize the set of obstructions and the set of requirement lists
        if minimize:
            self._minimize_griddedperms()

        if not any(ob.is_empty() for ob in self.obstructions):
            # If assuming the non-active cells are empty, then add the
            # obstructions
            if derive_empty:
                self._fill_empty()

            # Remove empty rows and empty columns
            if remove_empty:
                self._minimize_tiling()
        self._cell_basis: Optional[Dict[Cell, Tuple[List[Perm], List[Perm]]]] = None

    @classmethod
    def from_perms(
        cls,
        obstructions: Iterable[Perm] = tuple(),
        requirements: Iterable[Iterable[Perm]] = tuple(),
    ) -> "Tiling":
        """
        Return a 1x1 tiling from that avoids permutation in `obstructions`
        and contains one permutation form each iterable of `requirements`.
        """
        t = Tiling(
            obstructions=(Obstruction(p, ((0, 0),) * len(p)) for p in obstructions)
        )
        for req_list in requirements:
            req_list = [Requirement(p, ((0, 0),) * len(p)) for p in req_list]
            t = t.add_list_requirement(req_list)
        return t

    def _fill_empty(self) -> None:
        """Add size one obstructions to cells that are empty."""
        add = []
        (i, j) = self.dimensions
        for x in range(i):
            for y in range(j):
                if (x, y) not in self.active_cells and (x, y) not in self.empty_cells:
                    add.append(Obstruction.single_cell(Perm((0,)), (x, y)))
        self._obstructions = tuple(sorted(tuple(add) + self._obstructions))

    def _minimize_griddedperms(self) -> None:
        """Minimizes the set of obstructions and the set of requirement lists.
        The set of obstructions are first reduced to a minimal set. The
        requirements that contain any obstructions are removed from their
        respective lists. If any requirement list is empty, then the tiling is
        empty.
        """
        while True:
            # Minimize the set of obstructions
            minimized_obs = self._minimal_obs()
            # Minimize the set of requiriments
            minimized_obs, minimized_reqs = self._minimal_reqs(minimized_obs)
            if (
                self._obstructions == minimized_obs
                and self._requirements == minimized_reqs
            ):
                break
            self._obstructions = minimized_obs
            self._requirements = minimized_reqs

    def _minimize_tiling(self) -> None:
        """Remove empty rows and columns."""
        # Produce the mapping between the two tilings
        if not self.active_cells:
            self._forward_map: Dict[Cell, Cell] = {}
            self._obstructions = (Obstruction.single_cell(Perm((0,)), (0, 0)),)
            self._requirements = tuple()
            self._dimensions = (1, 1)
            return
        col_mapping, row_mapping = self._minimize_mapping()
        cell_map = partial(map_cell, col_mapping, row_mapping)

        # For tracking regions.
        self._forward_map = {
            (k_x, k_y): (v_x, v_y)
            for k_x, v_x in col_mapping.items()
            for k_y, v_y in row_mapping.items()
        }
        new_obs = []
        for ob in self._obstructions:
            cell = ob.pos[0]
            if not ob.is_point_obstr() or (
                cell[0] in col_mapping and cell[1] in row_mapping
            ):
                new_obs.append(ob.apply_map(cell_map))
        self._obstructions = tuple(new_obs)
        self._requirements = tuple(
            tuple(req.apply_map(cell_map) for req in reqlist)
            for reqlist in self._requirements
        )
        self._dimensions = (
            max(col_mapping.values()) + 1,
            max(row_mapping.values()) + 1,
        )

    def _minimize_mapping(self) -> Tuple[Dict[int, int], Dict[int, int]]:
        """Returns a pair of dictionaries, that map rows/columns to an
        equivalent set of rows/columns where empty ones have been removed. """
        active_cells = self.active_cells
        assert active_cells

        col_set, row_set = map(set, zip(*active_cells))

        col_list, row_list = sorted(col_set), sorted(row_set)
        col_mapping = {x: actual for actual, x in enumerate(col_list)}
        row_mapping = {y: actual for actual, y in enumerate(row_list)}
        return (col_mapping, row_mapping)

    def _clean_isolated(self, obstruction: Obstruction) -> Obstruction:
        """Remove the isolated factors that are implied by requirements
        from all obstructions."""
        for req_list in self._requirements:
            for factor in obstruction.factors():
                if all(factor in req for req in req_list):
                    obstruction = obstruction.remove_cells(factor.pos)
        return obstruction

    def _minimal_obs(self) -> Tuple[Obstruction, ...]:
        """Returns a new list of minimal obstructions from the obstruction set
        of self. Every obstruction in the new list will have any isolated
        points in positive cells removed."""
        clean_ones = sorted(self._clean_isolated(co) for co in self._obstructions)
        cleanobs: List[Obstruction] = list()
        for cleanob in clean_ones:
            add = True
            for co in cleanobs:
                if co in cleanob:
                    add = False
                    break
            if add:
                cleanobs.append(cleanob)
        return tuple(cleanobs)

    def _minimal_reqs(
        self, obstructions: Tuple[Obstruction, ...]
    ) -> Tuple[Tuple[Obstruction, ...], Tuple[Tuple[Requirement, ...]]]:
        """Returns a new set of minimal lists of requirements from the
        requirement set of self, and a list of further reduced obstructions.
        # TODO: obstruction don't change in the function, so stop returning."""
        factored_reqs: List[Tuple[Requirement, ...]] = list()
        for reqs in self._requirements:
            # If any gridded permutation in list is empty then you vacuously
            # contain this requirement
            if not all(reqs):
                continue
            if not reqs:
                # If req is empty, then can not contain this requirement so
                # the tiling is empty
                return (Obstruction.empty_perm(),), tuple()
            factors = set(reqs[0].factors())
            for req in reqs[1:]:
                if not factors:
                    break
                factors = factors.intersection(req.factors())
            if len(factors) == 0 or (len(factors) == 1 and len(reqs) == 1):
                # if there are no factors in the intersection, or it is just
                # the same req as the first, we do nothing and add the original
                factored_reqs.append(reqs)
                continue
            # add each of the factors as a single requirement, and then remove
            # these from each of the other requirements in the list
            remaining_cells = set(c for req in reqs for c in req.pos) - set(
                c for req in factors for c in req.pos
            )
            for factor in factors:
                factored_reqs.append((factor,))
            rem_req = tuple(
                req.get_gridded_perm_in_cells(remaining_cells) for req in reqs
            )
            factored_reqs.append(rem_req)

        cleaned_reqs: List[List[Requirement]] = []
        for reqs in factored_reqs:
            if not all(reqs):
                continue
            cleaned_req = []
            for req in reqs:
                cells: List[Cell] = []
                for f in req.factors():
                    # if factor implied by some requirement list then we
                    # remove it from the gridded perm
                    if not any(
                        all(f in r for r in req_list)
                        for req_list in factored_reqs
                        if not all(any(r2 in r1 for r2 in reqs) for r1 in req_list)
                    ):
                        cells.extend(f.pos)
                cleaned_req.append(req.get_gridded_perm_in_cells(cells))
            cleaned_reqs.append(cleaned_req)

        cleanreqs: List[List[Requirement]] = list()
        for req_list in cleaned_reqs:
            # If any gridded permutation in list is empty then you vacuously
            # contain this requirement
            if not all(req_list):
                continue
            redundant = set()
            for i, req_i in enumerate(req_list):
                for j in range(i + 1, len(req_list)):
                    if j not in redundant:
                        if req_i in req_list[j]:
                            redundant.add(j)
                if i not in redundant:
                    if any(ob in req_i for ob in obstructions):
                        redundant.add(i)
            cleanreq = [req for i, req in enumerate(req_list) if i not in redundant]
            # If cleanreq is empty, then can not contain this requirement so
            # the tiling is empty.
            if not cleanreq:
                return (Obstruction.empty_perm(),), tuple()
            cleanreqs.append(cleanreq)

        ind_to_remove = set()
        for i, req_list in enumerate(cleanreqs):
            if i not in ind_to_remove:
                for j, req_list2 in enumerate(cleanreqs):
                    if i != j and j not in ind_to_remove:
                        if all(any(r2 in r1 for r2 in req_list2) for r1 in req_list):
                            ind_to_remove.add(j)

        for i, req_list in enumerate(cleanreqs):
            if i in ind_to_remove:
                continue
            factored = [r.factors() for r in req_list]
            # if every factor of every requirement in a list is implied by
            # another requirement then we can remove this requirement list
            for factors in factored:
                if all(
                    any(
                        all(factor in req for req in other_req)
                        for j, other_req in enumerate(cleanreqs)
                        if i != j and j not in ind_to_remove
                    )
                    for factor in factors
                ):
                    ind_to_remove.add(i)
                    break

        return (
            obstructions,
            Tiling.sort_requirements(
                reqs for i, reqs in enumerate(cleanreqs) if i not in ind_to_remove
            ),
        )

    # -------------------------------------------------------------
    # Compression
    # -------------------------------------------------------------

    def to_bytes(self) -> bytes:
        """Compresses the tiling by flattening the sets of cells into lists of
        integers which are concatenated together, every list preceeded by its
        size. The obstructions are compressed and concatenated to the list, as
        are the requirement lists."""

        def split_16bit(n) -> Tuple[int, int]:
            """Takes a 16 bit integer and splits it into
               (lower 8bits, upper 8bits)"""
            return (n & 0xFF, (n >> 8) & 0xFF)

        result = []  # type: List[int]
        result.extend(split_16bit(len(self.obstructions)))
        result.extend(
            chain.from_iterable([len(ob)] + ob.compress() for ob in self.obstructions)
        )
        result.extend(split_16bit(len(self.requirements)))
        for reqlist in self.requirements:
            result.extend(split_16bit(len(reqlist)))
            result.extend(
                chain.from_iterable([len(req)] + req.compress() for req in reqlist)
            )
        res = array("B", result)
        return res.tobytes()

    @classmethod
    def from_bytes(
        cls,
        arrbytes,
        remove_empty=False,
        derive_empty=False,
        minimize=False,
        sorted_input=True,
    ) -> "Tiling":
        """Given a compressed tiling in the form of an 1-byte array, decompress
        it and return a tiling."""

        def merge_8bit(lh, uh):
            """Takes two 16 bit integers and merges them into
               one 16 bit integer assuming lh is lower half and
               uh is the upper half."""
            return lh | (uh << 8)

        arr = array("B", arrbytes)
        offset = 2
        nobs = merge_8bit(arr[offset - 2], arr[offset - 1])
        obstructions = []
        for _ in range(nobs):
            pattlen = arr[offset]
            offset += 1
            obstructions.append(
                Obstruction.decompress(arr[offset : offset + 3 * pattlen])
            )
            offset += 3 * pattlen

        nreqs = merge_8bit(arr[offset], arr[offset + 1])
        offset += 2
        requirements = []
        for _ in range(nreqs):
            reqlistlen = merge_8bit(arr[offset], arr[offset + 1])
            offset += 2
            reqlist = []
            for _ in range(reqlistlen):
                pattlen = arr[offset]
                offset += 1
                reqlist.append(
                    Requirement.decompress(arr[offset : offset + 3 * pattlen])
                )
                offset += 3 * pattlen
            requirements.append(reqlist)

        return cls(
            obstructions=obstructions,
            requirements=requirements,
            remove_empty=remove_empty,
            derive_empty=derive_empty,
            minimize=minimize,
            sorted_input=sorted_input,
        )

    @classmethod
    def from_string(cls, string: str) -> "Tiling":
        """Return a 1x1 tiling from string of form 'p1_p2'"""
        basis = [
            Obstruction.single_cell(Perm.to_standard(p), (0, 0))
            for p in string.split("_")
        ]
        return cls(obstructions=basis)

    # -------------------------------------------------------------
    # JSON methods
    # -------------------------------------------------------------

    def to_jsonable(self) -> dict:
        """Returns a dictionary object which is JSON serializable which
        represents a Tiling."""
        output: dict = super().to_jsonable()
        output["obstructions"] = [gp.to_jsonable() for gp in self.obstructions]
        output["requirements"] = [
            [gp.to_jsonable() for gp in req] for req in self.requirements
        ]
        return output

    @classmethod
    def from_json(cls, jsonstr: str) -> "Tiling":
        """Returns a Tiling object from JSON string."""
        jsondict = json.loads(jsonstr)
        return cls.from_dict(jsondict)

    @classmethod
    def from_dict(cls, jsondict: dict) -> "Tiling":
        """Returns a Tiling object from a dictionary loaded from a JSON
        serialized Tiling object."""
        obstructions = map(Obstruction.from_dict, jsondict["obstructions"])
        requirements = map(
            lambda x: map(Requirement.from_dict, x), jsondict["requirements"]
        )
        return cls(obstructions=obstructions, requirements=requirements)

    # -------------------------------------------------------------
    # Cell methods
    # -------------------------------------------------------------

    def cell_within_bounds(self, cell: Cell) -> bool:
        """Checks if a cell is within the bounds of the tiling."""
        (i, j) = self.dimensions
        return cell[0] >= 0 and cell[0] < i and cell[1] >= 0 and cell[1] < j

    def empty_cell(self, cell: Cell) -> "Tiling":
        """Empties a cell in the tiling by adding a point obstruction into the
        cell.
        """
        if not self.cell_within_bounds(cell):
            raise ValueError(
                "Cell {} is not within the bounds of the tiling.".format(cell)
            )
        return self.add_single_cell_obstruction(Perm((0,)), cell)

    def insert_cell(self, cell: Cell) -> "Tiling":
        """Performs 'cell insertion', adds a point requirement into the given
        cell. Cell should be active.
        """
        if not self.cell_within_bounds(cell):
            raise ValueError(
                "Cell {} is not within the bounds of the tiling.".format(cell)
            )
        return self.add_single_cell_requirement(Perm((0,)), cell)

    def add_obstruction(self, patt: Perm, pos: Iterable[Cell]) -> "Tiling":
        """Returns a new tiling with the obstruction of the pattern
        patt with positions pos."""
        return Tiling(
            self._obstructions + (Obstruction(patt, pos),), self._requirements
        )

    def add_obstructions(self, gps: Iterable[GriddedPerm]) -> "Tiling":
        """Returns a new tiling with the obstructions added."""
        new_obs = tuple(map(Obstruction.from_gridded_perm, gps))
        return Tiling(self._obstructions + new_obs, self._requirements)

    def add_list_requirement(self, req_list: Iterable[GriddedPerm]) -> "Tiling":
        """
        Return a new tiling with the requirement list added.
        """
        new_req = tuple(map(Requirement.from_gridded_perm, req_list))
        return Tiling(self._obstructions, self._requirements + (new_req,),)

    def add_requirement(self, patt: Perm, pos: Iterable[Cell]) -> "Tiling":
        """Returns a new tiling with the requirement of the pattern
        patt with position pos."""
        new_req_list = (Requirement(patt, pos),)
        return self.add_list_requirement(new_req_list)

    def add_single_cell_obstruction(self, patt: Perm, cell: Cell) -> "Tiling":
        """Returns a new tiling with the single cell obstruction of the pattern
        patt in the given cell."""
        return Tiling(
            self._obstructions + (Obstruction.single_cell(patt, cell),),
            self._requirements,
        )

    def add_single_cell_requirement(self, patt: Perm, cell: Cell) -> "Tiling":
        """Returns a new tiling with the single cell requirement of the pattern
        patt in the given cell."""
        new_req_list = (Requirement.single_cell(patt, cell),)
        return self.add_list_requirement(new_req_list)

    def fully_isolated(self) -> bool:
        """Check if all cells are isolated on their rows and columns."""
        seen_row = []
        seen_col = []
        for i, j in self.active_cells:
            if i in seen_col or j in seen_row:
                return False
            seen_col.append(i)
            seen_row.append(j)
        return True

    def only_positive_in_row_and_col(self, cell: Cell) -> bool:
        """Check if the cell is the only positive cell in row and column."""
        if cell not in self.positive_cells:
            return False
        return (
            sum(1 for (x, y) in self.positive_cells if y == cell[1] or x == cell[0])
            == 1
        )

    def only_positive_in_row(self, cell: Cell) -> bool:
        """Check if the cell is the only positive cell in row."""
        if cell not in self.positive_cells:
            return False
        inrow = sum(1 for (x, y) in self.positive_cells if y == cell[1])
        return inrow == 1

    def only_positive_in_col(self, cell: Cell) -> bool:
        """Check if the cell is the only positive cell in column."""
        if cell not in self.positive_cells:
            return False
        incol = sum(1 for (x, y) in self.positive_cells if x == cell[0])
        return incol == 1

    def only_cell_in_col(self, cell: Cell) -> bool:
        """Checks if the cell is the only active cell in the column."""
        return sum(1 for (x, y) in self.active_cells if x == cell[0]) == 1

    def only_cell_in_row(self, cell: Cell) -> bool:
        """Checks if the cell is the only active cell in the row."""
        return sum(1 for (x, y) in self.active_cells if y == cell[1]) == 1

    def only_cell_in_row_and_col(self, cell: Cell) -> bool:
        """Checks if the cell is the only active cell in the row."""
        return (
            sum(1 for (x, y) in self.active_cells if y == cell[1] or x == cell[0]) == 1
        )

    def cells_in_row(self, row: int) -> FrozenSet[Cell]:
        """Return all active cells in row."""
        return frozenset((x, y) for (x, y) in self.active_cells if y == row)

    def cells_in_col(self, col: int) -> FrozenSet[Cell]:
        """Return all active cells in column."""
        return frozenset((x, y) for (x, y) in self.active_cells if x == col)

    def cell_basis(self) -> Dict[Cell, Tuple[List[Perm], List[Perm]]]:
        """Returns a dictionary from cells to basis.

        The basis for each cell is a tuple of two lists of permutations.  The
        first list contains the patterns of the obstructions localized in the
        cell and the second contains the intersections of requirement lists
        that are localized in the cell.
        """
        if self._cell_basis is not None:
            return self._cell_basis
        obdict: Dict[Cell, List[Perm]] = defaultdict(list)
        reqdict: Dict[Cell, List[Perm]] = defaultdict(list)
        for ob in self.obstructions:
            if ob.is_localized():
                cell = ob.pos[0]
                obdict[cell].append(ob.patt)

        for req_list in self.requirements:
            for req in req_list:
                for cell in set(req.pos):
                    gp = req.get_gridded_perm_in_cells([cell])
                    if gp not in reqdict[cell] and all(gp in r for r in req_list):
                        reqdict[cell].append(gp.patt)
        for cell, contain in reqdict.items():
            ind_to_remove = set()
            for i, req in enumerate(contain):
                if any(req in other for j, other in enumerate(contain) if i != j):
                    ind_to_remove.add(i)
            reqdict[cell] = [
                req for i, req in enumerate(contain) if i not in ind_to_remove
            ]

        all_cells = product(range(self.dimensions[0]), range(self.dimensions[1]))
        resdict = {cell: (obdict[cell], reqdict[cell]) for cell in all_cells}
        self._cell_basis = resdict
        return self._cell_basis

    def cell_graph(self) -> Set[Tuple[Cell, Cell]]:
        """
        Return the set of edges in the cell graph of the tiling.
        """
        edges = set()
        cells = sorted(self.active_cells)
        for c1, c2 in zip(cells[:-1], cells[1:]):
            if c1[0] == c2[0]:
                edges.add((c1, c2))
        cells = sorted(self.active_cells, key=lambda x: (x[1], x[0]))
        for c1, c2 in zip(cells[:-1], cells[1:]):
            if c1[1] == c2[1]:
                edges.add((c1, c2))
        return edges

    def sum_decomposition(self, skew: bool = False) -> List[List[Cell]]:
        """
        Returns the sum decomposition of the tiling with respect to the cells.
        If skew is True then returns the skew decomposition instead.
        """
        cells = sorted(self.active_cells)
        decomposition: List[List[Cell]] = []
        while len(cells) > 0:
            x = cells[0][0]  # x boundary, maximum in both cases
            y = cells[0][1]  # y boundary, maximum in sum, minimum in skew
            change = True
            while change:
                change = False
                for c in cells:
                    if c[0] <= x:
                        if (skew and c[1] < y) or (not skew and c[1] > y):
                            y = c[1]
                            change = True
                    if (skew and c[1] >= y) or (not skew and c[1] <= y):
                        if c[0] > x:
                            x = c[0]
                            change = True
            decomposition.append([])
            new_cells = []
            for c in cells:
                if c[0] <= x:
                    decomposition[-1].append(c)
                else:
                    new_cells.append(c)
            cells = new_cells
        return decomposition

    def skew_decomposition(self) -> List[List[Cell]]:
        """
        Returns the skew decomposition of the tiling with respect to the cells
        """
        return self.sum_decomposition(skew=True)

    @staticmethod
    def sort_requirements(
        requirements: Iterable[Iterable[Requirement]],
    ) -> Tuple[Tuple[Requirement, ...], ...]:
        return tuple(sorted(tuple(sorted(set(reqlist))) for reqlist in requirements))

    def backward_map(self, gp: GriddedPerm) -> GriddedPerm:
        return GriddedPerm(gp.patt, [self.backward_cell_map[cell] for cell in gp.pos])

    def forward_map(self, gp: GriddedPerm) -> GriddedPerm:
        return GriddedPerm(gp.patt, [self.forward_cell_map[cell] for cell in gp.pos])

    @property
    def forward_cell_map(self) -> Dict[Cell, Cell]:
        if not hasattr(self, "_forward_map"):
            self._minimize_tiling()
        return self._forward_map

    @property
    def backward_cell_map(self) -> Dict[Cell, Cell]:
        if not hasattr(self, "_backward_map"):
            if not hasattr(self, "_forward_map"):
                self._minimize_tiling()
            self._backward_map = {b: a for a, b in self._forward_map.items()}
        return self._backward_map

    # -------------------------------------------------------------
    # Symmetries
    # -------------------------------------------------------------

    def _transform(
        self, transf, gptransf: Callable[[GriddedPerm], GriddedPerm]
    ) -> "Tiling":
        """ Transforms the tiling according to the two transformation functions
        given. The first transf is mapping of cells while gptransf is a
        transformation of GriddedPerm that calls some internal method.
        # TODO: transf is not used...
        """
        return Tiling(
            obstructions=(gptransf(ob) for ob in self.obstructions),
            requirements=(
                [gptransf(req) for req in reqlist] for reqlist in self.requirements
            ),
        )

    def reverse(self, regions=False):
        """ |
        Reverses the tiling within its boundary. Every cell and obstruction
        gets flipped over the vertical middle axis.
        # TODO: remove weird regions flag? """

        def reverse_cell(cell: Cell) -> Cell:
            return (self.dimensions[0] - cell[0] - 1, cell[1])

        reversed_tiling = self._transform(
            reverse_cell, lambda gp: gp.reverse(reverse_cell)
        )
        if not regions:
            return reversed_tiling
        return (
            [reversed_tiling],
            [{c: frozenset([reverse_cell(c)]) for c in self.active_cells}],
        )

    def complement(self) -> "Tiling":
        """ -
        Flip over the horizontal axis.  """

        def complement_cell(cell: Cell) -> Cell:
            return (cell[0], self.dimensions[1] - cell[1] - 1)

        return self._transform(
            complement_cell, lambda gp: gp.complement(complement_cell)
        )

    def inverse(self) -> "Tiling":
        """ /
        Flip over the diagonal"""

        def inverse_cell(cell: Cell) -> Cell:
            return (cell[1], cell[0])

        return self._transform(inverse_cell, lambda gp: gp.inverse(inverse_cell))

    def antidiagonal(self) -> "Tiling":
        """ \\
        Flip over the anti-diagonal"""

        def antidiagonal_cell(cell: Cell) -> Cell:
            return (self.dimensions[1] - cell[1] - 1, self.dimensions[0] - cell[0] - 1)

        return self._transform(
            antidiagonal_cell, lambda gp: gp.antidiagonal(antidiagonal_cell)
        )

    def rotate270(self) -> "Tiling":
        """Rotate 270 degrees"""

        def rotate270_cell(cell: Cell) -> Cell:
            return (self.dimensions[1] - cell[1] - 1, cell[0])

        return self._transform(rotate270_cell, lambda gp: gp.rotate270(rotate270_cell))

    def rotate180(self) -> "Tiling":
        """Rotate 180 degrees"""

        def rotate180_cell(cell: Cell) -> Cell:
            return (self.dimensions[0] - cell[0] - 1, self.dimensions[1] - cell[1] - 1)

        return self._transform(rotate180_cell, lambda gp: gp.rotate180(rotate180_cell))

    def rotate90(self) -> "Tiling":
        """Rotate 90 degrees"""

        def rotate90_cell(cell: Cell) -> Cell:
            return (cell[1], self.dimensions[0] - cell[0] - 1)

        return self._transform(rotate90_cell, lambda gp: gp.rotate90(rotate90_cell))

    def all_symmetries(self) -> Set["Tiling"]:
        """
        Return all the symmetries of a tiling in a set.
        """
        symmetries = set()
        t = self
        for _ in range(4):
            symmetries.add(t)
            symmetries.add(t.inverse())
            t = t.rotate90()
            if t in symmetries:
                break
        return symmetries

    # -------------------------------------------------------------
    # Algorithms
    # -------------------------------------------------------------

    def _fusion(self, row, col, fusion_class):
        """
        Fuse the tilings using the fusion class.

        If `row` is not `None` then `row` and `row+1` are fused together.
        If `col` is not `None` then `col` and `col+1` are fused together.
        """
        assert xor(row is None, col is None), "Specify only `row` or `col`"
        if not (
            row in range(self.dimensions[1] - 1) or col in range(self.dimensions[0] - 1)
        ):
            raise InvalidOperationError("`row` or `column` out or range")
        fusion = fusion_class(self, row_idx=row, col_idx=col)
        if not fusion.fusable():
            fus_type = "Rows" if row is not None else "Columns"
            idx = row if row is not None else col
            message = "{} {} and {} are not fusable.".format(fus_type, idx, idx + 1)
            raise InvalidOperationError(message)
        return fusion.fused_tiling()

    def fusion(self, row=None, col=None):
        """
        Fuse the tilings.

        If `row` is not `None` then `row` and `row+1` are fused together.
        If `col` is not `None` then `col` and `col+1` are fused together.
        """
        return self._fusion(row, col, Fusion)

    def component_fusion(self, row=None, col=None):
        """
        Fuse the tilings in such a way that it can be unfused by drawing a line
        between skew/sum-components.

        If `row` is not `None` then `row` and `row+1` are fused together.
        If `col` is not `None` then `col` and `col+1` are fused together.
        """
        return self._fusion(row, col, ComponentFusion)

    def sub_tiling(self, cells: Iterable[Cell], factors: bool = False) -> "Tiling":
        """Return the tiling using only the obstructions and requirements
        completely contained in the given cells. If factors is set to True,
        then it assumes that the first cells confirms if a gridded perm uses only
        the cells."""
        obstructions = tuple(
            ob
            for ob in self.obstructions
            if (factors and ob.pos[0] in cells) or all(c in cells for c in ob.pos)
        )
        requirements = tuple(
            req
            for req in self.requirements
            if (factors and req[0].pos[0] in cells)
            or all(c in cells for c in chain.from_iterable(r.pos for r in req))
        )
        return self.__class__(obstructions, requirements)

    def find_factors(self, interleaving: str = "none") -> Tuple["Tiling", ...]:
        """
        Return list with the factors of the tiling.

        Two non-empty cells are in the same factor if they are in the same row
        or column, or they share an obstruction or requirement. However, if
        `interleaving` is set to 'monotone' cell on the same row do not need to
        be in the same factor if one of them is monotone. If interleaving is
        set 'all' then cells on the same row or columns don't need to be in
        the same factor.
        """
        factor_class = {
            "none": Factor,
            "monotone": FactorWithMonotoneInterleaving,
            "any": FactorWithInterleaving,
        }
        if interleaving in factor_class:
            factor = factor_class[interleaving](self)
        else:
            raise InvalidOperationError(
                "interleaving option must be in {}".format(list(factor_class.keys()))
            )
        return factor.factors()

    def row_and_column_separation(self) -> "Tiling":
        """
        Splits the row and columns of a tilings using the inequalities implied
        by the length two obstructions.
        """
        rcs = RowColSeparation(self)
        return rcs.separated_tiling()

    def obstruction_transitivity(self) -> "Tiling":
        """
        Add length 2 obstructions to the tiling using transitivity over
        positive cells.

        For three cells A, B and C on the same row or column, if A < B, B < C
        and B is positive then the obstruction for A < C is added.
        """
        obs_trans = ObstructionTransitivity(self)
        return obs_trans.obstruction_transitivity()

    def all_obstruction_inferral(self, obstruction_length: int) -> "Tiling":
        """
        Adds all the obstruction of length up to `obstruction_length` that
        does not change the set of gridded permutations of the tiling.
        """
        obs_inf = AllObstructionInferral(self, obstruction_length)
        return obs_inf.obstruction_inferral()

    def empty_cell_inferral(self) -> "Tiling":
        """
        Adds point obstruction in the cell of the tilings that should be empty.

        Equivalent to `self.all_obstruction_inferral(1)`
        """
        obs_inf = EmptyCellInferral(self)
        return obs_inf.obstruction_inferral()

    def subobstruction_inferral(self) -> "Tiling":
        """
        Adds all the subobstruction of the tiling's obstruction that doesn't
        change the set of gridded permutations of the tiling.
        """
        obs_inf = SubobstructionInferral(self)
        return obs_inf.obstruction_inferral()

    def place_point_in_cell(self, cell: Cell, direction: int) -> "Tiling":
        """
        Return the tiling where a point is placed in the given cell and
        direction.
        """
        req_placement = RequirementPlacement(self)
        return req_placement.place_point_in_cell(cell, direction)

    def place_point_of_gridded_permutation(
        self, gp: GriddedPerm, idx: int, direction: int
    ) -> "Tiling":
        """
        Return the tiling where the directionmost occurrence of the idx point
        in the gridded permutaion gp is placed.
        """
        req_placement = RequirementPlacement(self)
        return req_placement.place_point_of_gridded_permutation(gp, idx, direction)

    def place_row(self, idx: int, direction: int) -> List["Tiling"]:
        """
        Return the list of tilings in which the directionmost point in the row
        is placed.
        """
        req_placement = RequirementPlacement(self)
        return req_placement.row_placement(idx, direction)

    def place_col(self, idx: int, direction: int) -> List["Tiling"]:
        """
        Return the list of tilings in which the directionmost point in the
        column is placed.
        """
        req_placement = RequirementPlacement(self)
        return req_placement.col_placement(idx, direction)

    def partial_place_point_in_cell(self, cell: Cell, direction: int) -> "Tiling":
        """
        Return the tiling where a point is placed in the given cell and
        direction. The point is placed onto its own row or own column
        depending on the direction.
        """
        if direction in (DIR_EAST, DIR_WEST):
            req_placement = RequirementPlacement(self, own_row=False)
        else:
            req_placement = RequirementPlacement(self, own_col=False)
        return req_placement.place_point_in_cell(cell, direction)

    def partial_place_point_of_gridded_permutation(
        self, gp: GriddedPerm, idx: int, direction: int
    ) -> "Tiling":
        """
        Return the tiling where the directionmost occurrence of the idx point
        in the gridded permutaion gp is placed. The point is placed onto its
        own row or own column depending on the direction.
        """
        if direction in (DIR_EAST, DIR_WEST):
            req_placement = RequirementPlacement(self, own_row=False)
        else:
            req_placement = RequirementPlacement(self, own_col=False)
        return req_placement.place_point_of_gridded_permutation(gp, idx, direction)

    def partial_place_row(self, idx: int, direction: int) -> List["Tiling"]:
        """
        Return the list of tilings in which the directionmost point in the row
        is placed. The points are placed onto thier own row.
        """
        req_placement = RequirementPlacement(self, own_row=True, own_col=False)
        return req_placement.row_placement(idx, direction)

    def partial_place_col(self, idx: int, direction: int) -> List["Tiling"]:
        """
        Return the list of tilings in which the directionmost point in the
        column is placed. The points are placed onto their own column.
        """
        req_placement = RequirementPlacement(self, own_row=False, own_col=True)
        return req_placement.col_placement(idx, direction)

    # -------------------------------------------------------------
    # Properties and getters
    # -------------------------------------------------------------

    def maximum_length_of_minimum_gridded_perm(self) -> int:
        """Returns the maximum length of the minimum gridded permutation that
        can be gridded on the tiling.
        """
        return sum(max(map(len, reqs)) for reqs in self.requirements)

    def is_empty(self) -> bool:
        """Checks if the tiling is empty.

        Tiling is empty if it has been inferred to be contradictory due to
        contradicting requirements and obstructions or no gridded permutation
        can be gridded on the tiling.
        """
        if any(ob.is_empty() for ob in self.obstructions):
            return True
        if len(self.requirements) <= 1:
            return False
        MGP = MinimalGriddedPerms(self)
        return all(False for _ in MGP.minimal_gridded_perms(yield_non_minimal=True))

    def is_finite(self) -> bool:
        """Returns True if all active cells have finite basis."""
        increasing = set()
        decreasing = set()
        for ob in self.obstructions:
            if ob.is_single_cell():
                if ob.patt.is_increasing():
                    increasing.add(ob.pos[0])
                if ob.patt.is_decreasing():
                    decreasing.add(ob.pos[0])
        return all(
            cell in increasing and cell in decreasing for cell in self.active_cells
        )

    def objects_of_size(self, size: int) -> Iterator[GriddedPerm]:
        yield from self.gridded_perms_of_length(size)

    def gridded_perms_of_length(self, length: int) -> Iterator[GriddedPerm]:
        for gp in self.gridded_perms(maxlen=length):
            if len(gp) == length:
                yield gp

    def gridded_perms(self, maxlen: Optional[int] = None) -> Iterator[GriddedPerm]:
        """
        Iterator of all gridded permutations griddable on the tiling.

        The gridded permutations are up to length of the longest minimum
        gridded permutations that is griddable on the tiling.
        """
        yield from GriddedPermsOnTiling(self, maxlen=maxlen)

    def merge(self) -> "Tiling":
        """Return an equivalent tiling with a single requirement list.
        # TODO: this doesn't work due to minimization on initialising"""
        if len(self.requirements) <= 1:
            return self
        mgps = MinimalGriddedPerms(self)
        requirements = tuple(
            Requirement(gp.patt, gp.pos) for gp in mgps.minimal_gridded_perms()
        )
        return self.__class__(self.obstructions, (requirements,))

    def minimal_gridded_perms(self) -> Iterator[GriddedPerm]:
        """
        An iterator over all minimal gridded permutations.
        """
        MGP = MinimalGriddedPerms(self)
        yield from MGP.minimal_gridded_perms()

    def is_epsilon(self) -> bool:
        """Returns True if the generating function for the tiling is 1."""
        return (
            self.dimensions == (1, 1)
            and len(self.obstructions) == 1
            and len(self.obstructions[0]) == 1
        )

    def is_positive(self) -> bool:
        """Returns True if tiling does not contain the empty permutation."""
        return bool(self.requirements)

    def is_point_tiling(self) -> bool:
        """
        Returns True if the only gridded permutations of the tiling is
        1: (0, 0)
        """
        return self.dimensions == (1, 1) and (0, 0) in self.point_cells

    is_atom = is_point_tiling

    def is_point_or_empty(self) -> bool:
        point_or_empty_tiling = Tiling(
            obstructions=(
                Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
                Obstruction(Perm((1, 0)), ((0, 0), (0, 0))),
            )
        )
        return self == point_or_empty_tiling

    def is_empty_cell(self, cell: Cell) -> bool:
        """Check if the cell of the tiling is empty."""
        return cell in self.empty_cells

    def is_monotone_cell(self, cell: Cell) -> bool:
        """
        Check if the cell is decreasing or increasing.

        If the cell is empty it is considered as monotone.
        """
        local_obs = self.cell_basis()[cell][0]
        return any(ob in [Perm((0,)), Perm((0, 1)), Perm((1, 0))] for ob in local_obs)

    @property
    def point_cells(self) -> FrozenSet[Cell]:
        if not hasattr(self, "_point_cells"):
            local_length2_obcells = Counter(
                ob.pos[0]
                for ob in self._obstructions
                if ob.is_localized() and len(ob) == 2
            )
            self._point_cells = frozenset(
                cell for cell in self.positive_cells if local_length2_obcells[cell] == 2
            )
        return self._point_cells

    @property
    def total_points(self) -> int:
        return len(self.point_cells)

    @property
    def positive_cells(self) -> FrozenSet[Cell]:
        if not hasattr(self, "_positive_cells"):
            self._positive_cells = frozenset(
                union_reduce(
                    intersection_reduce(req.pos for req in reqs)
                    for reqs in self._requirements
                )
            )
        return self._positive_cells

    def total_positive(self) -> int:
        return len(self.positive_cells)

    @property
    def possibly_empty(self) -> FrozenSet[Cell]:
        """Computes the set of possibly empty cells on the tiling."""
        return self.active_cells - self.positive_cells

    @property
    def obstructions(self) -> Tuple[Obstruction, ...]:
        return self._obstructions

    def total_obstructions(self) -> int:
        return len(self._obstructions)

    @property
    def requirements(self) -> Tuple[Tuple[Requirement, ...], ...]:
        return self._requirements

    def total_requirements(self) -> int:
        return len(self._requirements)

    @property
    def empty_cells(self) -> FrozenSet[Cell]:
        """Returns a set of all cells that contain a point obstruction, i.e.,
        are empty.
        """
        return frozenset(gp.pos[0] for gp in self.obstructions if gp.is_point_obstr())

    @property
    def active_cells(self) -> FrozenSet[Cell]:
        """Returns a set of all cells that do not contain a point obstruction,
        i.e., not empty.
        """
        return union_reduce(
            ob.pos for ob in self._obstructions if not ob.is_point_obstr()
        ) | union_reduce(
            union_reduce(req.pos for req in reqs) for reqs in self._requirements
        )

    @property
    def dimensions(self) -> Tuple[int, int]:
        if not hasattr(self, "_dimensions"):
            obcells = union_reduce(ob.pos for ob in self._obstructions)
            reqcells = union_reduce(
                union_reduce(req.pos for req in reqlist)
                for reqlist in self._requirements
            )
            all_cells = obcells | reqcells
            rows = set(x for (x, y) in all_cells)
            cols = set(y for (x, y) in all_cells)
            if not rows and not cols:
                self._dimensions = (1, 1)
            else:
                self._dimensions = (max(rows) + 1, max(cols) + 1)
        return self._dimensions

    def add_obstruction_in_all_ways(self, patt: Perm) -> "Tiling":
        """
        Adds an obstruction of the pattern patt in all possible ways to
        a fully separated (no interleaving rows or columns) tiling t.
        """

        def rec(
            cols: List[List[Cell]],
            p: Perm,
            pos: List[Cell],
            used: Dict[int, Cell],
            i: int,
            j: int,
            res: List[Obstruction],
        ) -> None:
            """
            Recursive helper function
            cols: List of columns in increasing order, each column is a list of
            cells
            p: The pattern
            pos: List of the pattern's positions
            used: Dictionary mapping permutation values to cells for pruning
            i: Index in cells
            j: Index in p
            res: Resulting list of obstructions
            """
            if j == len(p):
                res.append(Obstruction(p, tuple(x for x in pos)))
            elif i == len(cols):
                return
            else:
                upper = min(v[1] for k, v in used.items() if k > p[j])
                lower = max(v[1] for k, v in used.items() if k < p[j])
                for cell in cols[i]:
                    if lower <= cell[1] <= upper:
                        used[p[j]] = cell
                        pos.append(cell)
                        rec(cols, p, pos, used, i, j + 1, res)
                        pos.pop()
                        del used[p[j]]
                rec(cols, p, pos, used, i + 1, j, res)

        cols: List[List[Cell]] = [[] for i in range(self.dimensions[0])]
        for x in self.active_cells:
            cols[x[0]].append(x)
        used = {-1: (-1, -1), len(patt): self.dimensions}
        pos: List[Cell] = []
        res: List[Obstruction] = []
        rec(cols, patt, pos, used, 0, 0, res)
        return Tiling(
            obstructions=list(self.obstructions) + res, requirements=self.requirements
        )

    @classmethod
    def tiling_from_perm(cls, p: Perm) -> "Tiling":
        """
        Returns a tiling with point requirements corresponding to the
        permutation 'p'
        """
        return cls(
            requirements=[
                [Requirement(Perm((0,)), ((i, p[i]),))] for i in range(len(p))
            ]
        )

    def get_genf(self, *args, **kwargs) -> sympy.Expr:
        """
        Return generating function of a tiling.
        """
        # If root has been given a function, return it if you see the root or a
        # symmetries.
        if (
            kwargs.get("root_func") is not None
            and kwargs.get("root_class") in self.all_symmetries()
        ):
            return kwargs["root_func"]
        if self.is_empty():
            return sympy.sympify(0)
        # Can count by counting the tiling with a requirement removed and
        # subtracting the tiling with it added as an obstruction.
        if self.requirements:
            ignore = Tiling(
                obstructions=self.obstructions, requirements=self.requirements[1:]
            )
            req = self.requirements[0]
            t_avoid_req = Tiling(
                obstructions=(
                    chain(self.obstructions, (Obstruction(r.patt, r.pos) for r in req))
                ),
                requirements=self.requirements[1:],
            )
            return ignore.get_genf(*args, **kwargs) - t_avoid_req.get_genf(
                *args, **kwargs
            )
        # Try using some of the enumeration strategy
        enum_stragies = [
            BasicEnumeration,
            LocallyFactorableEnumeration,
            MonotoneTreeEnumeration,
            DatabaseEnumeration,
        ]
        for enum_strat in enum_stragies:
            if enum_strat(self).verified():
                return enum_strat(self).get_genf()
        raise ValueError("We were unable to enumerate this tiling:\n" + str(self))

    # -------------------------------------------------------------
    # Dunder methods
    # -------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._requirements) ^ hash(self._obstructions)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tiling):
            return False
        return (self.obstructions == other.obstructions) and (
            self.requirements == other.requirements
        )

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Tiling):
            return True
        return (self.obstructions != other.obstructions) or (
            self.requirements != other.requirements
        )

    def __repr__(self) -> str:
        format_string = "Tiling(obstructions={}, requirements={})"
        return format_string.format(self.obstructions, self.requirements)

    def __str__(self) -> str:
        dim_i, dim_j = self.dimensions
        result = []
        # Create tiling lines
        for j in range(2 * dim_j + 1):
            for i in range(2 * dim_i + 1):
                # Whether or not a vertical line and a horizontal line is
                # present
                vertical = i % 2 == 0
                horizontal = j % 2 == 0
                if vertical:
                    if horizontal:
                        result.append("+")
                    else:
                        result.append("|")
                elif horizontal:
                    result.append("-")
                else:
                    result.append(" ")
            result.append("\n")

        labels: Dict[Tuple[Tuple[Perm, ...], bool], str] = dict()

        # Put the sets in the tiles

        # How many characters are in a row in the grid
        row_width = 2 * dim_i + 2
        curr_label = 1
        for cell, gridded_perms in sorted(self.cell_basis().items()):
            obstructions, _ = gridded_perms
            basis = list(sorted(obstructions))
            if basis == [Perm((0,))]:
                continue
            # the block, is the basis and whether or not positive
            block = (tuple(basis), cell in self.positive_cells)
            label = labels.get(block)
            if label is None:
                if basis == [Perm((0, 1)), Perm((1, 0))]:
                    if cell in self.positive_cells:
                        label = "\u25cf"
                    else:
                        label = "\u25cb"
                elif basis == [Perm((0, 1))]:
                    label = "\\"
                elif basis == [Perm((1, 0))]:
                    label = "/"
                else:
                    label = str(curr_label)
                    curr_label += 1
                labels[block] = label
            row_index_from_top = dim_j - cell[1] - 1
            index = (2 * row_index_from_top + 1) * row_width + 2 * cell[0] + 1
            result[index] = label

        # Legend at bottom
        for block, label in sorted(labels.items(), key=lambda x: x[1]):
            basis, positive = block
            result.append(label)
            result.append(": ")
            if basis == (Perm((0, 1)), Perm((1, 0))) and positive:
                result.append("point")
            else:
                result.append(
                    "Av{}({})".format(
                        "+" if positive else "", ", ".join(str(p) for p in basis)
                    )
                )
            result.append("\n")

        if any(not ob.is_single_cell() for ob in self.obstructions):
            result.append("Crossing obstructions:\n")
            for ob in self.obstructions:
                if not ob.is_single_cell():
                    result.append(str(ob))
                    result.append("\n")
        for i, req in enumerate(self.requirements):
            result.append("Requirement {}:\n".format(str(i)))
            for r in req:
                result.append(str(r))
                result.append("\n")
        if self.requirements:
            result = result[:-1]

        return "".join(result)

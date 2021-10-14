# pylint: disable=too-many-lines
import json
from array import array
from collections import Counter, defaultdict
from functools import reduce
from itertools import chain, filterfalse, product
from operator import mul, xor
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
from typing_extensions import TypedDict

from comb_spec_searcher import CombinatorialClass, VerificationStrategy
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.typing import Parameters
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_WEST

from .algorithms import (
    AllObstructionInferral,
    EmptyCellInferral,
    Factor,
    FactorWithInterleaving,
    FactorWithMonotoneInterleaving,
    Fusion,
    GriddedPermReduction,
    GriddedPermsOnTiling,
    MinimalGriddedPerms,
    ObstructionTransitivity,
    RequirementPlacement,
    RowColSeparation,
    SubclassVerificationAlgorithm,
    SubobstructionInferral,
    guess_obstructions,
)
from .exception import InvalidOperationError
from .griddedperm import GriddedPerm
from .gui_launcher import run_gui
from .map import CellMap, RowColMap
from .misc import intersection_reduce, union_reduce
from .parameter_counter import ParameterCounter

__all__ = ["Tiling"]


Cell = Tuple[int, int]
ReqList = Tuple[GriddedPerm, ...]
CellBasis = Dict[Cell, Tuple[List[Perm], List[Perm]]]
CellFrozenSet = FrozenSet[Cell]
Dimension = Tuple[int, int]


CachedProperties = TypedDict(
    "CachedProperties",
    {
        "active_cells": CellFrozenSet,
        "backward_map": RowColMap,
        "cell_basis": CellBasis,
        "dimensions": Dimension,
        "empty_cells": CellFrozenSet,
        "forward_map": RowColMap,
        "point_cells": CellFrozenSet,
        "positive_cells": CellFrozenSet,
        "possibly_empty": CellFrozenSet,
    },
    total=False,
)


class Tiling(CombinatorialClass):
    """Tiling class.

    Zero-indexed coordinates/cells from bottom left corner where the (x, y)
    cell is the cell in the x-th column and y-th row.

    Tilings store the obstructions and requirements but also caches the empty
    cells and the active cells.
    """

    def __init__(
        self,
        obstructions: Iterable[GriddedPerm] = tuple(),
        requirements: Iterable[Iterable[GriddedPerm]] = tuple(),
        parameters: Iterable[ParameterCounter] = tuple(),
        remove_empty_rows_and_cols: bool = True,
        derive_empty: bool = True,
        simplify: bool = True,
        sorted_input: bool = False,
        already_minimized_obs: bool = False,
    ) -> None:
        """
        - if remove_empty_rows_and_cols, then remove empty rows and columns.
        - if derive empty, then assume non-active cells are empty
        - if simplify, then obstructions and requirements will be simplifed
        - if not sorted_input, input will be sorted
        - already_minimized_obs indicates if the obstructions are already minimized
            we pass this through to GriddedPermReduction
        """
        self._cached_properties: CachedProperties = {}

        super().__init__()
        if sorted_input:
            # Set of obstructions
            self._obstructions = tuple(obstructions)
            # Set of requirement lists
            self._requirements = tuple(tuple(r) for r in requirements)
            # Set of parameters
            self._parameters = tuple(parameters)
        else:
            # Set of obstructions
            self._obstructions = tuple(sorted(obstructions))
            # Set of requirement lists
            self._requirements = Tiling.sort_requirements(requirements)
            # Set of parameters
            self._parameters = tuple(sorted(parameters))

        # Simplify the set of obstructions and the set of requirement lists
        if simplify:
            self._simplify_griddedperms(already_minimized_obs=already_minimized_obs)

        if not any(ob.is_empty() for ob in self.obstructions):
            # Fill empty
            if derive_empty:
                if "empty_cells" not in self._cached_properties:
                    self._prepare_properties()

            # Remove empty rows and empty columns
            if remove_empty_rows_and_cols:
                self._remove_empty_rows_and_cols()

        else:
            self._obstructions = (GriddedPerm.empty_perm(),)
            self._requirements = tuple()
            self._parameters = tuple()
            self._cached_properties["active_cells"] = frozenset()
            self._cached_properties["backward_map"] = RowColMap.identity((0, 0))
            self._cached_properties["cell_basis"] = {(0, 0): ([Perm()], [])}
            self._cached_properties["dimensions"] = (1, 1)
            self._cached_properties["empty_cells"] = frozenset([(0, 0)])
            self._cached_properties["forward_map"] = RowColMap.identity((0, 0))
            self._cached_properties["point_cells"] = frozenset()
            self._cached_properties["positive_cells"] = frozenset()
            self._cached_properties["possibly_empty"] = frozenset()

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
            obstructions=(GriddedPerm(p, ((0, 0),) * len(p)) for p in obstructions)
        )
        for perms in requirements:
            req_list = [GriddedPerm(p, ((0, 0),) * len(p)) for p in perms]
            t = t.add_list_requirement(req_list)
        return t

    def _prepare_properties(self) -> None:
        """
        Compute _active_cells, _empty_cells, _dimensions, and store them
        """
        active_cells = union_reduce(
            set(ob.pos) for ob in self.obstructions if len(ob) > 1
        )
        active_cells.update(
            *(union_reduce(set(comp.pos) for comp in req) for req in self.requirements)
        )

        max_row = 0
        max_col = 0
        for cell in active_cells:
            max_col = max(max_col, cell[0])
            max_row = max(max_row, cell[1])
        dimensions = (max_col + 1, max_row + 1)

        empty_cells = tuple(
            cell
            for cell in product(range(dimensions[0]), range(dimensions[1]))
            if cell not in active_cells
        )

        # If the first obstruction is the empty perm, we shouldn't do any of this.
        if len(self._obstructions) > 0 and len(self._obstructions[0]) > 0:
            # We can assume that self._obstructions is sorted at this point, so to
            #   extract the point obstructions, we just pass though them until we've
            #   found the last one, then we slice the list there.
            index = 0
            for ob in self._obstructions:
                if len(ob) > 1:
                    break
                index += 1  # Now the last point obstruction is at index [index-1]
            non_point_obstructions = self._obstructions[index:]

            new_point_obstructions = tuple(
                GriddedPerm((0,), (cell,)) for cell in empty_cells
            )
            self._obstructions = new_point_obstructions + non_point_obstructions

        self._cached_properties["active_cells"] = frozenset(active_cells)
        self._cached_properties["empty_cells"] = frozenset(empty_cells)
        self._cached_properties["dimensions"] = dimensions

    def _simplify_griddedperms(self, already_minimized_obs=False) -> None:
        """
        Simplifies the set of obstructions and the set of requirement lists.
        The set of obstructions are first reduced to a minimal set. The
        requirements that contain any obstructions are removed from their
        respective lists. If any requirement list is empty, then the tiling is
        empty.
        """
        GPR = GriddedPermReduction(
            self.obstructions,
            self.requirements,
            sorted_input=True,
            already_minimized_obs=already_minimized_obs,
        )

        self._obstructions = GPR.obstructions
        self._requirements = GPR.requirements

    def _remove_empty_rows_and_cols(self) -> None:
        """Remove empty rows and columns."""
        # Produce the mapping between the two tilings
        if not self.active_cells:
            assert GriddedPerm.empty_perm() not in self.obstructions
            self._cached_properties["forward_map"] = RowColMap.identity((0, 0))
            self._obstructions = (GriddedPerm.single_cell((0,), (0, 0)),)
            self._requirements = tuple()
            assert not self._parameters, "UH OH - we gotta think now"
            self._parameters = tuple()
            self._cached_properties["dimensions"] = (1, 1)
            return
        forward_map = self._minimize_mapping()
        self._cached_properties["forward_map"] = forward_map
        # We still may need to remove point obstructions if the empty row or col
        # was on the end so we do it outside the next if statement.
        self._obstructions = tuple(
            forward_map.map_gp(ob)
            for ob in self.obstructions
            if not ob.is_point_perm() or forward_map.is_mappable_gp(ob)
        )
        if not forward_map.is_identity():
            self._requirements = tuple(
                tuple(forward_map.map_gp(req) for req in reqlist)
                for reqlist in self._requirements
            )
            self._parameters = tuple(
                sorted(
                    param_counter.apply_row_col_map(forward_map)
                    for param_counter in self._parameters
                )
            )
            self._cached_properties["active_cells"] = frozenset(
                forward_map.map_cell(cell)
                for cell in self._cached_properties["active_cells"]
                if forward_map.is_mappable_cell(cell)
            )
            self._cached_properties["empty_cells"] = frozenset(
                forward_map.map_cell(cell)
                for cell in self._cached_properties["empty_cells"]
                if forward_map.is_mappable_cell(cell)
            )
            self._cached_properties["dimensions"] = (
                forward_map.max_col() + 1,
                forward_map.max_row() + 1,
            )

    def _minimize_mapping(self) -> RowColMap:
        """
        Returns a pair of dictionaries, that map rows/columns to an
        equivalent set of rows/columns where empty ones have been removed.
        Also returns a boolean describing whether this mapping is the identity
        mapping which saves some later computation.
        """
        active_cells = self.active_cells
        assert active_cells
        col_set = set(c[0] for c in active_cells)
        row_set = set(c[1] for c in active_cells)
        col_list, row_list = sorted(col_set), sorted(row_set)
        identity = (self.dimensions[0] == len(col_list)) and (
            self.dimensions[1] == len(row_list)
        )
        col_mapping = {x: actual for actual, x in enumerate(col_list)}
        row_mapping = {y: actual for actual, y in enumerate(row_list)}
        return RowColMap(row_map=row_mapping, col_map=col_mapping, is_identity=identity)

    @classmethod
    def guess_from_gridded_perms(
        cls, gps: Iterable[GriddedPerm], max_len: int = -1
    ) -> "Tiling":
        """Given a collection of gridded permutations, attempt to find the Tilings T
        such that the collection of gridded permutations belong to Grid(T). The method
        only looks for obstructions.

        Raises:
        ValueError: If the collection does not contain a pattern that is not avoided
        by all.
        """
        return cls(
            obstructions=guess_obstructions(gps, max_len),
            requirements=(),
            parameters=(),
        )

    def generate_known_equinumerous_tilings(self) -> Set["Tiling"]:
        """Generate all tilings from known equinumerous mappings."""
        stack, visited = [self], {self}
        while stack:
            for neighbor in Tiling._equinumerous_transpositions(stack.pop()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        return visited

    @staticmethod
    def _equinumerous_transpositions(tiling: "Tiling") -> Iterator["Tiling"]:
        columns, rows = tiling.dimensions
        yield from tiling.all_symmetries()
        yield from (tiling.column_reverse(c) for c in range(columns))
        yield from (tiling.permute_columns(perm) for perm in Perm.of_length(columns))
        for cell in (
            (c, r)
            for c in range(columns)
            for r in range(rows)
            if tiling.contains_all_patterns_locally_for_crossing((c, r))
            and (
                rows == 1
                or all(
                    tiling.is_empty_cell((c, _r))
                    for _r in chain(range(0, r - 1), range(r + 1, rows))
                )
            )
        ):
            yield from Tiling._apply_all_symmetries_to_cell(tiling, cell)
        # Add other pre-existing here:

    @staticmethod
    def _apply_all_symmetries_to_cell(
        tiling: "Tiling", cell: Cell
    ) -> Iterator["Tiling"]:
        yield from (
            tiling.apply_perm_map_to_cell(mapping, cell)
            for mapping in (
                lambda perm: perm.rotate(),
                lambda perm: perm.rotate().inverse(),
                lambda perm: perm.rotate(2),
                lambda perm: perm.rotate(2).inverse(),
                lambda perm: perm.rotate(3),
                lambda perm: perm.rotate(3).inverse(),
            )
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
            """
            Takes a 16 bit integer and splits it into
            (lower 8bits, upper 8bits).
            """
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
        if self.parameters:
            raise NotImplementedError
        res = array("B", result)
        return res.tobytes()

    @classmethod
    def from_bytes(cls, b: bytes) -> "Tiling":
        """Given a compressed tiling in the form of an 1-byte array, decompress
        it and return a tiling."""
        # pylint: disable=too-many-locals

        def merge_8bit(lh, uh):
            """
            Takes two 16 bit integers and merges them into
            one 16 bit integer assuming lh is lower half and
            uh is the upper half.
            """
            return lh | (uh << 8)

        def recreate_gp_list(offset):
            """
            Return the gplist implied started at the offset, together
            with the offset after reading it.
            """
            ngps = merge_8bit(arr[offset], arr[offset + 1])
            offset += 2
            res = []
            for _ in range(ngps):
                pattlen = arr[offset]
                offset += 1
                res.append(GriddedPerm.decompress(arr[offset : offset + 3 * pattlen]))
                offset += 3 * pattlen
            return res, offset

        arr = array("B", b)
        obstructions, offset = recreate_gp_list(0)

        nreqs = merge_8bit(arr[offset], arr[offset + 1])
        offset += 2
        requirements = []
        for _ in range(nreqs):
            reqlist, offset = recreate_gp_list(offset)
            requirements.append(reqlist)

        parameters: List[ParameterCounter] = []
        if offset < len(arr):
            raise NotImplementedError
        return cls(
            obstructions=obstructions,
            requirements=requirements,
            parameters=parameters,
            remove_empty_rows_and_cols=False,
            derive_empty=False,
            simplify=False,
            sorted_input=True,
        )

    @classmethod
    def from_string(cls, string: str) -> "Tiling":
        """Return a 1x1 tiling from string of form 'p1_p2'"""
        basis = [
            GriddedPerm.single_cell(Perm.to_standard(p), (0, 0))
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
        output["parameters"] = [param.to_jsonable() for param in self.parameters]
        return output

    @classmethod
    def from_json(cls, jsonstr: str) -> "Tiling":
        """Returns a Tiling object from JSON string."""
        jsondict = json.loads(jsonstr)
        return cls.from_dict(jsondict)

    @classmethod
    def from_dict(cls, d: dict) -> "Tiling":
        """Returns a Tiling object from a dictionary loaded from a JSON
        serialized Tiling object."""
        obstructions = map(GriddedPerm.from_dict, d["obstructions"])
        requirements = map(lambda x: map(GriddedPerm.from_dict, x), d["requirements"])
        parameters = map(ParameterCounter.from_dict, d.get("parameters", []))
        return cls(
            obstructions=obstructions,
            requirements=requirements,
            parameters=parameters,
        )

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

    def add_obstruction(
        self, patt: Perm, pos: Iterable[Cell], remove_empty_rows_and_cols: bool = True
    ) -> "Tiling":
        """Returns a new tiling with the obstruction of the pattern
        patt with positions pos."""
        return self.add_obstructions(
            (GriddedPerm(patt, pos),),
            remove_empty_rows_and_cols=remove_empty_rows_and_cols,
        )

    def add_obstructions(
        self, gps: Iterable[GriddedPerm], remove_empty_rows_and_cols: bool = True
    ) -> "Tiling":
        """Returns a new tiling with the obstructions added."""
        return self.add_obstructions_and_requirements(
            gps, [], remove_empty_rows_and_cols
        )

    def add_obstructions_and_requirements(
        self,
        obs: Iterable[GriddedPerm],
        reqs: Iterable[Iterable[GriddedPerm]],
        remove_empty_rows_and_cols: bool = True,
    ) -> "Tiling":
        """Returns a new tiling with the obstructions and requirements added."""
        new_obs = tuple(obs)
        new_reqs = tuple(tuple(gp) for gp in reqs)
        return Tiling(
            self._obstructions + new_obs,
            self._requirements + new_reqs,
            [
                param_counter.add_obstructions_and_requirements(new_obs, new_reqs)
                for param_counter in self._parameters
            ],
            remove_empty_rows_and_cols=remove_empty_rows_and_cols,
        )

    def add_list_requirement(
        self, req_list: Iterable[GriddedPerm], remove_empty_rows_and_cols: bool = True
    ) -> "Tiling":
        """
        Return a new tiling with the requirement list added.
        """
        return self.add_obstructions_and_requirements(
            [], [req_list], remove_empty_rows_and_cols
        )

    def add_requirement(
        self,
        patt: Perm,
        pos: Iterable[Cell],
        remove_empty_rows_and_cols: bool = True,
    ) -> "Tiling":
        """Returns a new tiling with the requirement of the pattern
        patt with position pos."""
        new_req_list = (GriddedPerm(patt, pos),)
        return self.add_list_requirement(
            new_req_list,
            remove_empty_rows_and_cols=remove_empty_rows_and_cols,
        )

    def add_single_cell_obstruction(
        self,
        patt: Perm,
        cell: Cell,
        remove_empty_rows_and_cols: bool = True,
    ) -> "Tiling":
        """Returns a new tiling with the single cell obstruction of the pattern
        patt in the given cell."""
        return self.add_obstructions(
            (GriddedPerm.single_cell(patt, cell),),
            remove_empty_rows_and_cols=remove_empty_rows_and_cols,
        )

    def add_single_cell_requirement(
        self, patt: Perm, cell: Cell, remove_empty_rows_and_cols: bool = True
    ) -> "Tiling":
        """Returns a new tiling with the single cell requirement of the pattern
        patt in the given cell."""
        new_req_list = (GriddedPerm.single_cell(patt, cell),)
        return self.add_list_requirement(
            new_req_list,
            remove_empty_rows_and_cols=remove_empty_rows_and_cols,
        )

    def add_parameter(self, parameter: ParameterCounter) -> "Tiling":
        """Returns a new tiling with the added parameter."""
        return self.add_parameters((parameter,))

    def add_parameters(self, parameters: Iterable[ParameterCounter]) -> "Tiling":
        """Returns a new tiling with the added parameters."""
        tiling = Tiling(
            self._obstructions,
            self._requirements,
            self._parameters + tuple(parameters),
            remove_empty_rows_and_cols=False,
            derive_empty=False,
            simplify=False,
            sorted_input=True,
        )
        return tiling

    def remove_parameter(self, parameter: Iterable[ParameterCounter]):
        """Returns a new tiling with parameter removed."""
        parameter = tuple(sorted(set(parameter)))
        try:
            idx = self._parameters.index(parameter)
        except ValueError as e:
            raise ValueError(f"following parameter not on tiling: '{parameter}'") from e
        tiling = Tiling(
            self._obstructions,
            self._requirements,
            self._parameters[:idx] + self._parameters[idx + 1 :],
            remove_empty_rows_and_cols=False,
            derive_empty=False,
            simplify=False,
            sorted_input=True,
        )
        return tiling

    def remove_parameters(self):
        """
        Return the tiling with all parameters removed.
        """
        return self.__class__(
            self._obstructions,
            self._requirements,
            remove_empty_rows_and_cols=False,
            derive_empty=False,
            simplify=False,
            sorted_input=True,
        )

    def remove_requirements(self):
        """
        Return the same tiling without the requirements.
        """
        assert not self.parameters, "Now think"
        return self.__class__(
            obstructions=self._obstructions,
            requirements=[],
            remove_empty_rows_and_cols=False,
            derive_empty=False,
            simplify=False,
            sorted_input=True,
        )

    def fully_isolated(self) -> bool:
        """Check if all cells are isolated on their rows and columns."""
        seen_row: List[int] = []
        seen_col: List[int] = []
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

    def cells_in_row(self, row: int) -> CellFrozenSet:
        """Return all active cells in row."""
        return frozenset((x, y) for (x, y) in self.active_cells if y == row)

    def cells_in_col(self, col: int) -> CellFrozenSet:
        """Return all active cells in column."""
        return frozenset((x, y) for (x, y) in self.active_cells if x == col)

    def cell_basis(self) -> Dict[Cell, Tuple[List[Perm], List[Perm]]]:
        """Returns a dictionary from cells to basis.

        The basis for each cell is a tuple of two lists of permutations.  The
        first list contains the patterns of the obstructions localized in the
        cell and the second contains the intersections of requirement lists
        that are localized in the cell.
        """
        try:
            return self._cached_properties["cell_basis"]
        except KeyError:
            obdict: Dict[Cell, List[Perm]] = defaultdict(list)
            reqdict: Dict[Cell, List[Perm]] = defaultdict(list)
            for ob in self.obstructions:
                if ob.is_localized():
                    cell = ob.pos[0]
                    obdict[cell].append(ob.patt)

            for req_list in self.requirements:
                for gp in req_list:
                    for cell in set(gp.pos):
                        subgp = gp.get_gridded_perm_in_cells([cell])
                        if subgp not in reqdict[cell] and all(
                            subgp in r for r in req_list
                        ):
                            reqdict[cell].append(subgp.patt)
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
            self._cached_properties["cell_basis"] = resdict
            return resdict

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
        requirements: Iterable[Iterable[GriddedPerm]],
    ) -> Tuple[Tuple[GriddedPerm, ...], ...]:
        return tuple(sorted(tuple(sorted(set(reqlist))) for reqlist in requirements))

    @property
    def forward_map(self) -> RowColMap:
        try:
            return self._cached_properties["forward_map"]
        except KeyError:
            self._remove_empty_rows_and_cols()
            return self._cached_properties["forward_map"]

    @property
    def backward_map(self) -> RowColMap:
        try:
            return self._cached_properties["backward_map"]
        except KeyError:
            backward_map = self.forward_map.inverse()
            self._cached_properties["backward_map"] = backward_map
            return backward_map

    # -------------------------------------------------------------
    # Symmetries
    # -------------------------------------------------------------

    def _transform(
        self, transf, gptransf: Callable[[GriddedPerm], GriddedPerm]
    ) -> "Tiling":
        """
        Transforms the tiling according to the two transformation functions
        given. The first transf is mapping of cells while gptransf is a
        transformation of GriddedPerm that calls some internal method.
        # TODO: transf is not used...
        """
        if self._parameters:
            raise NotImplementedError
        return Tiling(
            obstructions=(gptransf(ob) for ob in self.obstructions),
            requirements=(
                [gptransf(req) for req in reqlist] for reqlist in self.requirements
            ),
        )

    def reverse(self, regions=False):
        """
        Reverses the tiling within its boundary. Every cell and obstruction
        gets flipped over the vertical middle axis.
        # TODO: remove weird regions flag?
        """

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
        """Flip over the horizontal axis."""

        def complement_cell(cell: Cell) -> Cell:
            return (cell[0], self.dimensions[1] - cell[1] - 1)

        return self._transform(
            complement_cell, lambda gp: gp.complement(complement_cell)
        )

    def inverse(self) -> "Tiling":
        """Flip over the diagonal"""

        def inverse_cell(cell: Cell) -> Cell:
            return (cell[1], cell[0])

        return self._transform(inverse_cell, lambda gp: gp.inverse(inverse_cell))

    def antidiagonal(self) -> "Tiling":
        """Flip over the anti-diagonal"""

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

    def column_reverse(self, column: int) -> "Tiling":
        """Reverse a given column in the tiling."""
        return self._transform(lambda _c: _c, lambda gp: gp.column_reverse(column))

    def row_complement(self, row: int) -> "Tiling":
        """Changes a row to its complement."""
        return self._transform(lambda _c: _c, lambda gp: gp.row_complement(row))

    def permute_columns(self, perm: Iterable[int]) -> "Tiling":
        """Given an initial state of columns 12...n, permute them using the provided
        permutation.."""
        if not isinstance(perm, Perm):
            perm = Perm(perm)
        assert len(perm) == self.dimensions[0]
        return self._transform(lambda _c: _c, lambda gp: gp.permute_columns(perm))

    def permute_rows(self, perm: Iterable[int]) -> "Tiling":
        """Given an initial state of rows 12...n, permute them using the provided
        permutation.."""
        if not isinstance(perm, Perm):
            perm = Perm(perm)
        assert len(perm) == self.dimensions[1]
        return self._transform(lambda _c: _c, lambda gp: gp.permute_rows(perm))

    def apply_perm_map_to_cell(
        self,
        perm_mapping: Callable[[Perm], Perm],
        cell: Cell,
    ) -> "Tiling":
        """Apply a permutation mapping on anything within a cell."""
        return self._transform(
            lambda _c: _c, lambda gp: gp.apply_perm_map_to_cell(perm_mapping, cell)
        )

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
        raise NotImplementedError("Update to use general fusion algorithm.")

    def sub_tiling(
        self,
        cells: Iterable[Cell],
        factors: bool = False,
        add_parameters: Iterable[ParameterCounter] = tuple(),
    ) -> "Tiling":
        """Return the tiling using only the obstructions and requirements
        completely contained in the given cells. If factors is set to True,
        then it assumes that the first cells confirms if a gridded perm uses only
        the cells."""
        obstructions = tuple(
            ob
            for ob in self.obstructions
            if (factors and ob.pos[0] in cells) or all(c in cells for c in ob.pos)
        )
        requirements = Tiling.sort_requirements(
            req
            for req in self.requirements
            if (factors and req[0].pos[0] in cells)
            or all(c in cells for c in chain.from_iterable(r.pos for r in req))
        )
        if self._parameters:
            raise NotImplementedError
        return self.__class__(
            obstructions,
            requirements,
            simplify=False,
            sorted_input=True,
        )

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

    def row_and_column_separation_with_mapping(
        self,
    ) -> Tuple["Tiling", CellMap]:
        rcs = RowColSeparation(self)
        return rcs.separated_tiling(), rcs.get_cell_map()

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

    def place_row(self, idx: int, direction: int) -> Tuple["Tiling", ...]:
        """
        Return the list of tilings in which the directionmost point in the row
        is placed.
        """
        req_placement = RequirementPlacement(self)
        return req_placement.row_placement(idx, direction)

    def place_col(self, idx: int, direction: int) -> Tuple["Tiling", ...]:
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

    def partial_place_row(self, idx: int, direction: int) -> Tuple["Tiling", ...]:
        """
        Return the list of tilings in which the directionmost point in the row
        is placed. The points are placed onto thier own row.
        """
        req_placement = RequirementPlacement(self, own_row=True, own_col=False)
        return req_placement.row_placement(idx, direction)

    def partial_place_col(self, idx: int, direction: int) -> Tuple["Tiling", ...]:
        """
        Return the list of tilings in which the directionmost point in the
        column is placed. The points are placed onto their own column.
        """
        req_placement = RequirementPlacement(self, own_row=False, own_col=True)
        return req_placement.col_placement(idx, direction)

    def is_subclass(self, perms_to_check: Iterable[Perm]):
        """
        Returns true if the underlying permutations of all the gridded permutations
        on the tiling lie within one of the principal classes whose basis elements
        are given in perms_to_check.
        """
        return SubclassVerificationAlgorithm(self, set(perms_to_check)).is_verified()

    # -------------------------------------------------------------
    # HTML methods
    # -------------------------------------------------------------

    def _handle_html_parameter(self, result: List[str], style) -> List[str]:
        """adds background color in cells where parameter happens"""
        # pylint: disable=too-many-locals
        colors = [
            "#b0dbff",
            "#d1f0af",
            "#db8686",
            "#FCC997",
            "#b0ffd0",
            "#FCEB97",
            "#fc97b4",
            "#4b45ff",
            "#c8bdff",
            "#bfbfbf",
        ]
        has_param: Dict[int, List[str]] = {}
        for c, param_counter in enumerate(self.parameters):
            for i, j in param_counter.active_region():
                dim_i, dim_j = self.dimensions
                index = (dim_j - j - 1) * (3 * dim_i + 2) + i * 3 + 2
                if c >= len(colors):
                    pass
                elif index in has_param.keys():
                    has_param[index].append(colors[c])
                else:
                    has_param[index] = [colors[c]]

                if c >= len(colors) or len(has_param[index]) > 4:
                    # display gray lines if out of color or
                    # more than 4 parameters in single cell
                    background_image = """background-image:
                        repeating-linear-gradient(
                        45deg, #ffffff, #ffffff 6px, #00000080 1px, #00000080 7px
                        );"""
                else:
                    # display stripes
                    background_image = "background-image: linear-gradient(180deg"
                    stripe_size = 24 // len(has_param[index])
                    for idx, color in enumerate(has_param[index]):
                        background_image += f""",
                            {color} {idx*stripe_size}px,
                            {color} {(idx+1)*stripe_size}px"""
                    background_image += ");"
                result[index] = f'<th style="{background_image}{style}">'
        return result

    def to_html_representation(self) -> str:
        """Returns an html representation of the tilings object"""
        # pylint: disable=too-many-locals
        # stylesheet for tiling
        style = """
            border: 1px solid;
            width: 24px;
            height: 24px;
            text-align: center;
            """
        dim_i, dim_j = self.dimensions
        result = []
        # Create tiling html table
        result.append("<table> ")
        for _ in range(dim_j):
            result.append("<tr>")
            for _ in range(dim_i):
                result.append(f"<th style='{style}'>")
                result.append(" ")
                result.append("</th>")
            result.append("</tr>")
        result.append("</table>")
        labels: Dict[Tuple[Tuple[Perm, ...], bool], str] = dict()

        # Put the sets in the tiles

        # How many characters are in a row in the grid
        row_width = 3 * dim_i + 2
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
            index = row_index_from_top * row_width + cell[0] * 3 + 3
            result[index] = label

        # adds background color in cells where parameter happens
        result = self._handle_html_parameter(result, style)
        return "".join(result)

    # -------------------------------------------------------------
    # Properties and getters
    # -------------------------------------------------------------

    @property
    def extra_parameters(self) -> Tuple[str, ...]:
        return tuple("k_{}".format(i) for i in range(len(self._parameters)))

    def get_parameters(self, obj: GriddedPerm) -> Parameters:
        return tuple(param.get_value(obj) for param in self.parameters)

    def get_parameter_name(self, parameter: ParameterCounter) -> str:
        """
        Return the variable associated with the given parameter.

        Raise ValueError if the parameter is not on the tiling.
        """
        try:
            idx = self._parameters.index(parameter)
        except ValueError as e:
            raise ValueError(f"following parameter not on tiling: '{parameter}'") from e
        return "k_{}".format(idx)

    def get_parameter(self, parameter: str) -> ParameterCounter:
        idx = parameter.split("_")[1]
        return self.parameters[int(idx)]

    def get_minimum_value(self, parameter: str) -> int:
        """
        Return the minimum value that can be taken by the parameter.
        """
        actual_parameter = self.get_parameter(parameter)
        return min(
            actual_parameter.get_value(gp) for gp in self.minimal_gridded_perms()
        )

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

    def objects_of_size(self, n: int, **parameters: int) -> Iterator[GriddedPerm]:
        for gp in self.gridded_perms_of_length(n):
            if all(
                self.get_parameter(k).get_value(gp) == val
                for k, val in parameters.items()
            ):
                yield gp

    def gridded_perms_of_length(self, length: int) -> Iterator[GriddedPerm]:
        for gp in self.gridded_perms(maxlen=length):
            if len(gp) == length:
                yield gp

    def initial_conditions(self, check: int = 6) -> List[sympy.Expr]:
        """
        Returns a list with the initial conditions to size `check` of the
        CombinatorialClass.
        """
        res = [0 for _ in range(check + 1)]
        extra_params = self.extra_parameters
        param_counter = [
            (sympy.var(k), self.get_parameter(k).get_value) for k in extra_params
        ]
        for gp in self.gridded_perms(check):
            res[len(gp)] += reduce(
                mul,
                (var ** func(gp) for var, func in param_counter),
                sympy.Number(1),
            )
        return res

    def gridded_perms(self, maxlen: Optional[int] = None) -> Iterator[GriddedPerm]:
        """
        Iterator of all gridded permutations griddable on the tiling.

        The gridded permutations are up to length of the longest minimum
        gridded permutations that is griddable on the tiling.
        """
        maxlen = (
            maxlen
            if maxlen is not None
            else self.maximum_length_of_minimum_gridded_perm()
        )
        yield from GriddedPermsOnTiling(self).gridded_perms(maxlen)

    def enmerate_gp_up_to(self, max_length: int) -> List[int]:
        """Count gridded perms of each length up to a max length."""
        cnt = Counter(len(gp) for gp in self.gridded_perms(max_length))
        return [cnt[i] for i in range(max_length + 1)]

    def merge(self) -> "Tiling":
        """Return an equivalent tiling with a single requirement list.
        # TODO: this doesn't work due to minimization on initialising"""
        if len(self.requirements) <= 1:
            return self
        mgps = MinimalGriddedPerms(self)
        requirements = tuple(
            GriddedPerm(gp.patt, gp.pos) for gp in mgps.minimal_gridded_perms()
        )
        return self.__class__(self.obstructions, (requirements,), self.parameters)

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

    def is_atom(self) -> bool:
        """Return True if tiling is a single gridded permutation."""
        return (
            (self.active_cells == self.point_cells)
            and self.fully_isolated()
            and not any(ob.is_empty() for ob in self.obstructions)
        )

    def minimum_size_of_object(self) -> int:
        """Return the size of the smallest gridded perm contained on the tiling."""
        if not self.requirements:
            return 0
        if len(self.requirements) == 1:
            return min(len(gp) for gp in self.requirements[0])
        return len(next(self.minimal_gridded_perms()))

    def is_point_or_empty(self) -> bool:
        point_or_empty_tiling = Tiling(
            obstructions=(
                GriddedPerm((0, 1), ((0, 0), (0, 0))),
                GriddedPerm((1, 0), ((0, 0), (0, 0))),
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

    def contains_all_patterns_locally_for_crossing(self, cell: Cell) -> bool:
        """Check if for all crossing obstructions and requirements through a given cell,
        the tiling contains the same crossing obstructions and requirements but with all
        permutations of its subpattern within the cell.
        """
        return all(
            Tiling._contains_all_subpatterns_in_cell(gp_set, cell)
            for gp_set in chain(
                (
                    {
                        req
                        for req in req_list
                        if not req.is_localized() and req.occupies(cell)
                    }
                    for req_list in self.requirements
                ),
                (
                    {
                        obs
                        for obs in self.obstructions
                        if not obs.is_localized() and obs.occupies(cell)
                    },
                ),
            )
        )

    @staticmethod
    def _contains_all_subpatterns_in_cell(gps: Set[GriddedPerm], cell: Cell) -> bool:
        while gps:
            gp = next(iter(gps))
            perm = tuple(gp.patt[i] for i in gp.points_in_cell(cell))
            back_map = dict(zip(Perm.to_standard(perm), perm))
            for patt in Perm.of_length(len(perm)):
                it = iter(patt)
                gp = GriddedPerm(
                    (back_map[next(it)] if c == cell else val for val, c in gp),
                    gp.pos,
                )
                try:
                    gps.remove(gp)
                except KeyError:
                    return False
        return True

    @property
    def point_cells(self) -> CellFrozenSet:
        try:
            return self._cached_properties["point_cells"]
        except KeyError:
            local_length2_obcells = Counter(
                ob.pos[0]
                for ob in self._obstructions
                if ob.is_localized() and len(ob) == 2
            )
            point_cells = frozenset(
                cell for cell in self.positive_cells if local_length2_obcells[cell] == 2
            )
            self._cached_properties["point_cells"] = point_cells
            return point_cells

    @property
    def total_points(self) -> int:
        return len(self.point_cells)

    @property
    def positive_cells(self) -> CellFrozenSet:
        try:
            return self._cached_properties["positive_cells"]
        except KeyError:
            positive_cells = frozenset(
                union_reduce(
                    intersection_reduce(req.pos for req in reqs)
                    for reqs in self._requirements
                )
            )
            self._cached_properties["positive_cells"] = positive_cells
            return positive_cells

    def total_positive(self) -> int:
        return len(self.positive_cells)

    @property
    def possibly_empty(self) -> CellFrozenSet:
        """Computes the set of possibly empty cells on the tiling."""
        try:
            return self._cached_properties["possibly_empty"]
        except KeyError:
            possibly_empty = self.active_cells - self.positive_cells
            self._cached_properties["possibly_empty"] = possibly_empty
            return possibly_empty

    @property
    def obstructions(self) -> Tuple[GriddedPerm, ...]:
        return self._obstructions

    def total_obstructions(self) -> int:
        return len(self._obstructions)

    @property
    def requirements(self) -> Tuple[Tuple[GriddedPerm, ...], ...]:
        return self._requirements

    def total_requirements(self) -> int:
        return len(self._requirements)

    @property
    def parameters(self) -> Tuple[ParameterCounter, ...]:
        return self._parameters

    def total_parameters(self) -> int:
        return len(self._parameters)

    @property
    def empty_cells(self) -> CellFrozenSet:
        """Returns a set of all cells that contain a point obstruction, i.e.,
        are empty.
        """
        try:
            return self._cached_properties["empty_cells"]
        except KeyError:
            self._prepare_properties()
            return self._cached_properties["empty_cells"]

    @property
    def active_cells(self) -> CellFrozenSet:
        """
        Returns a set of all cells that do not contain a point obstruction,
        i.e., not empty.
        """
        try:
            return self._cached_properties["active_cells"]
        except KeyError:
            self._prepare_properties()
            return self._cached_properties["active_cells"]

    @property
    def dimensions(self) -> Dimension:
        try:
            return self._cached_properties["dimensions"]
        except KeyError:
            self._prepare_properties()
            return self._cached_properties["dimensions"]

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
            res: List[GriddedPerm],
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
                res.append(GriddedPerm(p, tuple(x for x in pos)))
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
        res: List[GriddedPerm] = []
        rec(cols, patt, pos, used, 0, 0, res)
        return Tiling(
            obstructions=list(self.obstructions) + res,
            requirements=self.requirements,
            parameters=self.parameters,
        )

    @classmethod
    def tiling_from_perm(cls, p: Perm) -> "Tiling":
        """
        Returns a tiling with point requirements corresponding to the
        permutation 'p'
        """
        return cls(
            requirements=[[GriddedPerm((0,), ((i, p[i]),))] for i in range(len(p))]
        )

    def get_genf(self, *args, **kwargs) -> sympy.Expr:
        # pylint: disable=import-outside-toplevel
        if self.is_empty():
            return sympy.sympify(0)
        from .strategies import (
            BasicVerificationStrategy,
            DatabaseVerificationStrategy,
            InsertionEncodingVerificationStrategy,
            LocallyFactorableVerificationStrategy,
            LocalVerificationStrategy,
            MonotoneTreeVerificationStrategy,
            OneByOneVerificationStrategy,
        )

        enum_stragies: List[VerificationStrategy] = [
            BasicVerificationStrategy(),
            OneByOneVerificationStrategy(),
            LocallyFactorableVerificationStrategy(),
            InsertionEncodingVerificationStrategy(),
            MonotoneTreeVerificationStrategy(),
            DatabaseVerificationStrategy(),
            LocalVerificationStrategy(),
        ]
        for enum_strat in enum_stragies:
            try:
                return enum_strat.get_genf(self)
            except StrategyDoesNotApply:
                continue
        raise NotImplementedError(
            "We were unable to enumerate this tiling:\n" + str(self)
        )

    def to_gui(self):
        """Try to open the current tiling in the GUI."""
        run_gui(json.dumps(self.to_jsonable(), separators=(",", ":")))

    # -------------------------------------------------------------
    # Dunder methods
    # -------------------------------------------------------------

    def __hash__(self) -> int:
        return (
            hash(self._requirements) ^ hash(self._obstructions) ^ hash(self._parameters)
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tiling):
            return NotImplemented
        return (
            self.obstructions == other.obstructions
            and self.requirements == other.requirements
            and self.parameters == other.parameters
        )

    def __contains__(self, gp: GriddedPerm) -> bool:
        """Test if a gridded permtuaiton is griddable on the given tiling."""
        return gp.avoids(*self.obstructions) and all(
            gp.contains(*req) for req in self.requirements
        )

    def __repr__(self) -> str:
        format_string = "Tiling(obstructions={}, requirements={}, parameters={})"
        non_point_obstructions = tuple(
            filterfalse(GriddedPerm.is_point_perm, self.obstructions)
        )
        return format_string.format(
            non_point_obstructions, self.requirements, self.parameters
        )

    def __str__(self) -> str:
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
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
            basis_el, positive = block
            result.append(label)
            result.append(": ")
            if basis_el == (Perm((0, 1)), Perm((1, 0))) and positive:
                result.append("point")
            else:
                result.append(
                    "Av{}({})".format(
                        "+" if positive else "", ", ".join(str(p) for p in basis_el)
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
        for i, param in enumerate(self.parameters):
            result.append("Parameter {}:\n".format(str(i)))
            result.append(str(param))
            result.append("\n")
        if self.parameters or self.requirements:
            result = result[:-1]

        return "".join(result)

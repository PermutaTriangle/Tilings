from collections import defaultdict
from functools import partial, reduce
from itertools import chain
from grids import Cell
from permuta import PermSet

from .misc import map_cell
from .obstruction import Obstruction

__all__ = ("Tiling")


class Tiling():
    """Tiling class.

    Zero-indexed coordinates/cells from bottom left corner where the (x, y)
    cell is the cell in the x-th column and y-th row.
    """

    def __init__(self, point_cells=list(), positive_cells=list(),
                 possibly_empty=list(), obstructions=list(),
                 remove_empty=True):
        # Set of the cells that have points in them
        self._point_cells = frozenset(point_cells)
        # Set of the cells that are positive, i.e. contain a point
        self._positive_cells = frozenset(positive_cells)
        # Set of possibly empty cells
        self._possibly_empty = frozenset(possibly_empty)
        # Set of obstructions
        self._obstructions = tuple(sorted(obstructions))

        self._dimensions = None
        self.back_map = None

        # The cell sets should all be disjoint
        if self._positive_cells & self._possibly_empty:
            raise ValueError(("The set of positive cells and the set of "
                              "possibly empty cells should be disjoint."))
        if self._positive_cells & self._point_cells:
            raise ValueError(("The set of positive cells and the set of point"
                              " cells should be disjoint."))
        if self._possibly_empty & self._point_cells:
            raise ValueError(("The set of possibly empty cells and the set of "
                              "point cells should be disjoint."))

        # Check if positive_cells and possibly_empty cells cover the indices of
        # the obstructions.
        all_cells = (self._positive_cells |
                     self._possibly_empty |
                     self._point_cells)
        all_obstruction_cells = reduce(
            set.__or__, (set(ob.pos) for ob in self._obstructions), set())
        if not all_obstruction_cells <= all_cells:
            raise ValueError(("The set of positive cells and the set of "
                              "possibly empty cells should cover the cells "
                              "of the obstructions."))

        self._minimize(remove_empty)
        self.dimensions

    def _minimize(self, remove_empty):
        """Minimizes the set of obstructions and for each single-point
        obstruction, removes the corresponding cell from the possibly empty
        set. Finally, removes all empty rows and columns and updates
        obstructions.
        """
        # Minimize the set of obstructions
        cleanobs = self._clean_obs()
        # Compute the single-point obstructions
        empty_cells = set(ob.is_point_obstr()
                          for ob in cleanobs if ob.is_point_obstr())

        # Remove the empty cells
        self._possibly_empty = frozenset(self._possibly_empty - empty_cells)
        # Produce the mapping between the two tilings
        self._col_mapping, self._row_mapping = self._minimize_mapping()
        cell_map = partial(map_cell, self._col_mapping, self._row_mapping)

        # For backwards compatability only, will be removed in future.
        # TODO: Not use Cell, and convert the dictionary to Cell dictionary
        # when needed.
        self.back_map = {Cell(*cell_map(cell)): Cell(*cell)
                         for cell in (self.point_cells |
                                      self.possibly_empty |
                                      self._positive_cells)}

        if remove_empty:
            self._obstructions = tuple(ob.minimize(cell_map) for ob in cleanobs
                                       if ob.is_point_obstr() is None)
            self._point_cells = frozenset(map(cell_map,
                                              self._point_cells))
            self._positive_cells = frozenset(map(cell_map,
                                                 self._positive_cells))
            self._possibly_empty = frozenset(map(cell_map,
                                                 self._possibly_empty))
        else:
            self._obstructions = tuple(ob for ob in cleanobs
                                       if ob.is_point_obstr() is None)

    def _minimize_mapping(self):
        """Returns a pair of dictionaries, that map rows/columns to an
        equivalent set of rows/columns where empty ones have been removed. """
        all_cells = (self._positive_cells |
                     self._possibly_empty |
                     self._point_cells)

        if not all_cells:
            (i, j) = self.dimensions
            return ({x: 0 for x in range(i)},
                    {y: 0 for y in range(j)})

        col_set, row_set = map(set, zip(*all_cells))

        col_list, row_list = sorted(col_set), sorted(row_set)
        col_mapping = {x: actual for actual, x in enumerate(col_list)}
        row_mapping = {y: actual for actual, y in enumerate(row_list)}
        return (col_mapping, row_mapping)

    def _clean_isolated(self, obstruction):
        """Remove the isolated cells that are point cells or positive cells
        from all obstructions."""
        remove = [cell for cell in obstruction.isolated_cells()
                  if (cell in self._point_cells or
                      cell in self._positive_cells)]
        return obstruction.remove_cells(remove)

    def _clean_obs(self):
        """Returns a new list of minimal obstructions from the obstruction set
        of self."""
        cleanobs = list()
        for ob in sorted(map(self._clean_isolated, self._obstructions)):
            add = True
            for co in cleanobs:
                if co in ob:
                    add = False
                    break
            if add:
                cleanobs.append(ob)
        return cleanobs

    def to_old_tiling(self):
        import grids
        basi = defaultdict(list)
        for ob in self._obstructions:
            cell = ob.is_single_cell()
            if cell is not None:
                basi[cell].append(ob.patt)
        blocks = dict()
        for cell in self._point_cells:
            blocks[cell] = grids.Block.point
        for cell in self._possibly_empty:
            if cell not in basi:
                blocks[cell] = PermSet.avoiding(())
        for cell in self._positive_cells:
            if cell not in basi:
                blocks[cell] = grids.PositiveClass(PermSet.avoiding(()))
        for (cell, basis) in basi.items():
            if cell in self._positive_cells:
                blocks[cell] = grids.PositiveClass(PermSet.avoiding(basis))
            else:
                blocks[cell] = PermSet.avoiding(basis)
        return grids.Tiling(blocks)

    def delete_cell(self, cell):
        """Deletes a cell from every obstruction and returns a new tiling. The
        cell must be in the set of possibly empty cells."""
        if cell not in self._possibly_empty:
            raise ValueError("Cell {} is not deletable.".format(cell))
        newobs = [ob for ob in self._obstructions if not ob.occupies(cell)]
        return Tiling(self._point_cells,
                      self._positive_cells,
                      self._possibly_empty - {cell},
                      newobs)

    def insert_cell(self, cell):
        """Inserts a cell into every obstruction and returns a new tiling. The
        cell must be in the set of possibly empty cells."""
        if cell not in self._possibly_empty:
            raise ValueError(
                "Cell {} is positive or not in the tiling.".format(cell))
        return Tiling(self._point_cells,
                      self._positive_cells | {cell},
                      self._possibly_empty - {cell},
                      self._obstructions)

    def only_positive_in_row_and_column(self, cell):
        if cell not in self._positive_cells and cell not in self._point_cells:
            return False
        inrow = sum(1 for (x, y) in
                    chain(self._point_cells, self._positive_cells)
                    if y == cell[1])
        incol = sum(1 for (x, y) in
                    chain(self._point_cells, self._positive_cells)
                    if x == cell[0])
        return (inrow == 1 and incol == 1)

    def only_positive_in_row(self, cell):
        inrow = sum(1 for (x, y) in
                    chain(self._point_cells, self._positive_cells)
                    if y == cell[1])
        return inrow == 1

    def only_positive_in_col(self, cell):
        incol = sum(1 for (x, y) in
                    chain(self._point_cells, self._positive_cells)
                    if x == cell[0])
        return incol == 1

    def get_cells_in_row(self, row):
        return [(x, y) for (x, y) in chain(self._point_cells, self._positive_cells, self._possibly_empty) if y == row]

    def get_cells_in_col(self, col):
        return [(x, y) for (x, y) in chain(self._point_cells, self._positive_cells, self._possibly_empty) if x == col]
    #
    # Properties and getters
    #

    def is_empty(self):
        return any(ob.is_empty() for ob in self)

    @property
    def point_cells(self):
        return self._point_cells

    @property
    def total_points(self):
        return len(self._point_cells)

    @property
    def possibly_empty(self):
        return self._possibly_empty

    @property
    def positive_cells(self):
        return self._positive_cells

    @property
    def total_positive(self):
        return len(self._positive_cells)

    @property
    def obstructions(self):
        return self._obstructions

    @property
    def total_obstructions(self):
        return len(self._obstructions)

    @property
    def dimensions(self):
        if self._dimensions is None:
            all_cells = (self._positive_cells |
                         self._possibly_empty |
                         self._point_cells)

            rows = set(x for (x, y) in all_cells | all_cells)
            cols = set(y for (x, y) in all_cells | all_cells)
            if not rows and not cols:
                self._dimensions = (1,1)
                return self._dimensions
            self._dimensions = (max(rows) - min(rows) + 1,
                                max(cols) - min(cols) + 1)
        return self._dimensions

    #
    # Dunder methods
    #

    def __contains__(self, item):
        if isinstance(item, Obstruction):
            return item in self._obstructions
        return False

    def __hash__(self):
        return (hash(self._point_cells) ^ hash(self._possibly_empty) ^
                hash(self._positive_cells) ^ hash(self._obstructions))

    def __eq__(self, other):
        return (self.point_cells == other.point_cells and
                self.possibly_empty == other.possibly_empty and
                self.positive_cells == other.positive_cells and
                self.obstructions == other.obstructions)

    def __iter__(self):
        for ob in self._obstructions:
            yield ob

    def __len__(self):
        return len(self._obstructions)

    def __repr__(self):
        format_string = "<A tiling of {} points and {} obstructions>"
        return format_string.format(self.total_points, self.total_obstructions)

    def __str__(self):
        return "\n".join([
            "Point cells: " + str(self._point_cells),
            "Positive cells: " + str(self._positive_cells),
            "Possibly empty cells: " + str(self._possibly_empty),
            "Obstructions: " + ", ".join(list(map(str, self._obstructions)))])

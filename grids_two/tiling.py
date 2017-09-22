from functools import partial, reduce

from .misc import map_cell
from .obstruction import Obstruction

__all__ = ("Tiling")


class Tiling():
    """Tiling class.

    Zero-indexed coordinates/cells from bottom left corner where the (x, y)
    cell is the cell in the x-th column and y-th row.
    """

    def __init__(self, point_cells=list(), positive_cells=list(),
                 possibly_empty=list(), obstructions=list()):
        # Set of the cells that have points in them
        self._point_cells = frozenset(point_cells)
        # Set of the cells that are positive, i.e. contain a point
        self._positive_cells = frozenset(positive_cells)
        # Set of possibly empty cells
        self._possibly_empty = frozenset(possibly_empty)
        # Set of obstructions
        self._obstructions = tuple(sorted(obstructions))

        # The cell sets should all be disjoint
        all_obstruction_cells = reduce(
            set.__or__, (set(ob.pos) for ob in self._obstructions), set())
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
        if not all_obstruction_cells <= all_cells:
            raise ValueError(("The set of positive cells and the set of "
                              "possibly empty cells should cover the cells "
                              "of the obstructios."))

        # self._hash = hash(hash_sum)
        self._minimize()

    def _minimize(self):
        """Minimizes the set of obstructions and for each single-point
        obstruction, removes the corresponding cell from the possibly empty
        set. Finally, removes all empty rows and columns and updates
        obstructions.
        """
        # Minimize the set of obstructions
        cleanobs = self._clean_obs()
        # Compute the single-point obstructions
        empty_cells = set(ob.point_cell()
                          for ob in cleanobs if ob.point_cell())
        # Produce the mapping between the two tilings
        self._col_mapping, self._row_mapping = self._minimize_mapping()
        cell_map = partial(map_cell, self._col_mapping, self._row_mapping)

        self._point_cells = frozenset(map(cell_map, self._point_cells))
        self._positive_cells = frozenset(map(cell_map, self._positive_cells))
        self._possibly_empty = frozenset(map(
            cell_map, self._possibly_empty - empty_cells))

        self._obstructions = tuple(ob.minimize(cell_map) for ob in cleanobs
                                   if ob.point_cell() is None)

    def _minimize_mapping(self):
        """Returns a pair of dictionaries, that map rows/columns to an
        equivalent set of rows/columns where empty ones have been removed. """
        all_cells = (self._positive_cells |
                     self._possibly_empty |
                     self._point_cells)

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
                if ob in cleanobs:
                    add = False
                    break
            if add:
                cleanobs.append(ob)
        return cleanobs

    def delete_cell(self, cell):
        """Deletes a cell from every obstruction and returns a new tiling. The
        cell must be in the set of possibly empty cells."""
        if cell not in self._possibly_empty:
            raise ValueError("Cell {} is not deletable.".format(cell))
        newobs = [ob for ob in self._obstructions if not ob.occupies(cell)]
        return Tiling(self._point_cells,
                      self._positive_cells,
                      self._possible_empty - {cell},
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

    #
    # Properties and getters
    #

    @property
    def point_cells(self):
        return self._point_cells

    @property
    def total_points(self):
        return len(self._point_cells)

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
            rows = set(x for (x, y) in all_cells)
            cols = set(y for (x, y) in all_cells)
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

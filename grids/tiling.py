# TODO: Docstring
# TODO: Make python2.7 compatible once permuta is
from collections import OrderedDict, defaultdict, namedtuple
from itertools import product  # For old of_length code

from permuta import Perm, PermSet
from permuta.misc import flatten, ordered_set_partitions

from . import elementaryblocks as eb
from .factor import Factor
from .jsonable import JsonAble
from .positiveclass import PositiveClass

__all__ = ["Cell", "Tiling"]

Cell = namedtuple("Cell", ["i", "j"])


class Tiling(JsonAble):
    """Tiling class.

    Zero-indexed coordinates/cells from bottom left corner where the (i, j)
    cell is the cell in the i-th column and j-th row.
    """

    def __init__(self, obstructions=list()):
        # List of obstructions
        obstructions = list()

        # The horizontal and vertical dimensions, respectively
        width = height = 1

        # The integer that is hashed to get the hash of the tiling
        hash_sum = 0

        # A list of the cells that have points in them
        point_cells = frozenset()
        # List of cells that are positive
        positive_cells = frozenset()
        obstruction_mapping = frozenset()

        if blocks:
            # The set of all indices
            i_set, j_set = map(set, zip(*blocks))

            # The sorted list of all indices
            i_list, j_list = sorted(i_set), sorted(j_set)

            # The i and j dimensions of the tiling
            i_dimension = len(i_list)
            j_dimension = len(j_list)

            # Mappings from indices to actual indices
            i_actual = {i: actual for actual, i in enumerate(i_list)}
            j_actual = {j: actual for actual, j in enumerate(j_list)}

            rows = [[] for _ in range(j_dimension)]
            cols = [[] for _ in range(i_dimension)]

            for item in sorted(blocks.items()):
                # Unpack item
                cell, block = item
                # Calculate actual cell
                actual_cell = Cell(i_actual[cell[0]], j_actual[cell[1]])
                # Add to back map and cell map
                the_cell = Cell(*cell)  # Make sure is Cell
                back_map[actual_cell] = the_cell
                cell_map[the_cell] = actual_cell
                # Create the new item
                item = actual_cell, block
                # Add to row and col cache
                rows[actual_cell.j].append(item)
                cols[actual_cell.i].append(item)
                # Add to tiling
                tiling[actual_cell] = block
                # Add hash to hash sum
                hash_sum += hash(item)
                # Add to caches
                if block == eb.point:
                    point_cells.append(actual_cell)
                else:
                    non_points.append(item)
                    if isinstance(block, PositiveClass):
                        other.append((actual_cell, block))
                    else:
                        classes.append((actual_cell, block))

        self._blocks = tiling

        self._dimensions = Cell(i_dimension, j_dimension)
        self._hash = hash(hash_sum)
        self._point_cells = tuple(point_cells)
        self._non_points = tuple(non_points)
        self._classes = tuple(classes)
        self._other = tuple(other)
        self._rows = tuple(map(tuple, rows))
        self._cols = tuple(map(tuple, cols))
        self._back_map = back_map
        self._cell_map = cell_map

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
    def non_points(self):
        return self._non_points

    @property
    def classes(self):
        return self._classes

    @property
    def other(self):
        return self._other

    @property
    def total_other(self):
        return len(self._other)

    @property
    def dimensions(self):
        return self._dimensions

    @property
    def area(self):
        return self._dimensions.i*self._dimensions.j

    def get_row(self, number):
        return self._rows[number]

    def get_col(self, number):
        return self._cols[number]

    def back_map(self, cell):
        return self._back_map[cell]

    def cell_map(self, cell):
        return self._cell_map[cell]

    #
    # General methods
    #

    def basis_partitioning(self, length, basis):
        """Partitions perms with cell info into containing and avoiding
        perms."""
        avoiding_perms = {}
        containing_perms = {}

        for perm, cell_info in self.perms_of_length_with_cell_info(length):
            belonging_partition = avoiding_perms if perm.avoids(*basis) \
                                  else containing_perms
            belonging_partition.setdefault(perm, []).append(cell_info)

        return containing_perms, avoiding_perms

    #
    # Dunder methods
    #

    def __contains__(self, item):
        return item in self._blocks

    def __iter__(self):
        # TODO: Should return self
        for row_number in range(self.dimensions.j):
            for item in self.get_row(row_number):
                yield item

    def __eq__(self, other):
        return isinstance(other, Tiling) \
           and hash(self) == hash(other) \
           and self.point_cells == other.point_cells \
           and self.non_points == other.non_points

    def __getitem__(self, key):
        return self._blocks[key]

    def __hash__(self):
        return self._hash

    def __len__(self):
        return len(self._blocks)

    def __repr__(self):
        format_string = "<A tiling of {} points and {} non-points>"
        return format_string.format(self.total_points, len(self.non_points))

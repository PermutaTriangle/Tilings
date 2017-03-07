# TODO: Docstring
# TODO: Make python2.7 compatible once permuta is


__all__ = ["Cell", "Block", "Tiling"]


import warnings

from builtins import dict
from collections import OrderedDict
from collections import namedtuple  # For Cell class
from itertools import product  # For old of_length code

from permuta import Perm
from permuta import PermSet
from permuta import Av
from permuta.misc import ordered_set_partitions, flatten
from permuta.descriptors import Descriptor

from .JsonAble import JsonAble
from .PositiveClass import PositiveClass


Cell = namedtuple("Cell", ["i", "j"])


class Block(object):
    """Different blocks for Tilings, for convenience."""
    all = PermSet()
    point = PermSet([Perm(0,)])  # TODO: Make a new optimized perm set if this is a bottleneck
    point_or_empty = PermSet.avoiding(PermSet(2))
    increasing = PermSet.avoiding(Perm((1, 0)))
    decreasing = PermSet.avoiding(Perm((0, 1)))
    def __new__(_cls):
        raise RuntimeError("Block class should not be instantiated")


class Tiling(JsonAble):
    """Tiling class.

    Zero-indexed coordinates/cells from bottom left corner where the (i, j)
    cell is the cell in the i-th column and j-th row.
    """

    def __init__(self, blocks={}):
        # The dictionary of blocks
        tiling = {}
        # The horizontal and vertical dimensions, respectively
        i_dimension = j_dimension = 1
        # The integer that is hashed to get the hash of the tiling
        hash_sum = 0
        # A list of the cells that have points in them
        point_cells = []
        non_points = []
        classes = []
        other = []
        rows = [[]]
        cols = [[]]
        # A map from the new values of the cells to the old
        back_map = {}

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
                # Add to back map
                back_map[actual_cell] = Cell(*cell)  # Make sure is Cell
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
                if block == Block.point:
                    point_cells.append(actual_cell)
                else:
                    non_points.append(item)
                    if isinstance(block, PositiveClass):
                        other.append(block)
                    else:
                        classes.append(block)

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

    #
    # JsonAble interface
    #

    @classmethod
    def _from_attr_dict(cls, attr_dict):
        # TODO: eval probably isn't the best way to do this
        blocks = {}
        for cell_string, block_string in attr_dict.items():
            cell = Cell(*eval(cell_string))
            if block_string == "point":
                block = Block.point
            elif block_string.startswith("Av+"):
                perms = map(Perm, eval(block_string[3:-1] + ",)"))
                av_class = PermSet.avoiding(perms)
                block = PositiveClass(av_class)
            elif block_string.startswith("Av"):
                perms = map(Perm, eval(block_string[2:-1] + ",)"))
                block = PermSet.avoiding(perms)
            else:
                raise RuntimeError("Unexpected block")
            blocks[cell] = block
        return cls(blocks)

    def _get_attr_dict(self):
        return {str(list(cell)): "point" if block is Block.point else repr(block)
                for cell, block in self}

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

    #
    # General methods
    #

    def basis_partitioning(self, length, basis):
        """Partitions perms with cell info into containing and avoiding perms."""
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

    def __str__(self):
        dim_i, dim_j = self.dimensions

        result = []

        # Create tiling lines
        for j in range(2*dim_j + 1):
            for i in range(2*dim_i + 1):
                # Whether or not a vertical line and a horizontal line is present
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

        labels = OrderedDict()

        # Put the sets in the tiles

        # How many characters are in a row in the grid
        row_width = 2*dim_i + 2
        for cell, block in self:
        #    # Check if label has been specified
        #    #specified_label = self.__specified_labels.get(perm_set)
        #    #if specified_label is None:
        #    #    # Use generic label (could reuse specified label)
        #    #    label = labels.get(perm_set)
        #    #    if label is None:
        #    #        label = str(len(labels) + 1)
        #    #        labels[perm_set] = label
        #    #else:
        #    #    # If label specified, then use it
        #    #    label = specified_label
            label = labels.get(block)
            if label is None:
                label = str(len(labels) + 1)
                labels[block] = label
            row_index_from_top = dim_j - cell.j - 1
            index = (2*row_index_from_top + 1)*row_width + 2*cell.i + 1
            result[index] = label

        # Legend at bottom
        for block, label in labels.items():
            result.append(label)
            result.append(": ")
            if block is Block.point:
                result.append("point")
            else:
                result.append(repr(block))
            result.append("\n")

        if len(labels) > 0:
            result.pop()

        return "".join(result)

    #
    # Terrifying code ahead! Be warned!
    #

    def perms_of_length(self, n):
        """Yield all possible (not necessarily unique) perms in tiling."""
        # TODO: Make not disgusting
        dim_j = self._dimensions.j
        tiling = list(((dim_j - 1 - cell.j, cell.i), block)
                      for cell, block
                      in self._blocks.items())
        h = max( k[0] for k,v in tiling ) + 1 if tiling else 1
        w = max( k[1] for k,v in tiling ) + 1 if tiling else 1

        def permute(arr, perm):
            res = [None] * len(arr)
            for i in range(len(arr)):
                res[i] = arr[perm[i]]
            return res

        def count_assignments(at, left):

            if at == len(tiling):
                if left == 0:
                    yield []
            elif tiling[at][1] is Block.point:
                # this doesn't need to be handled separately,
                # it's just an optimization
                if left > 0:
                    for ass in count_assignments(at + 1, left - 1):
                        yield [1] + ass
            else:
                for cur in range(left+1):
                    for ass in count_assignments(at + 1, left - cur):
                        yield [cur] + ass

        for count_ass in count_assignments(0, n):

            cntz = [ [ 0 for j in range(w) ] for i in range(h) ]

            for i, k in enumerate(count_ass):
                cntz[tiling[i][0][0]][tiling[i][0][1]] = k

            rowcnt = [ sum( cntz[row][col] for col in range(w) ) for row in range(h) ]
            colcnt = [ sum( cntz[row][col] for row in range(h) ) for col in range(w) ]

            for colpart in product(*[ ordered_set_partitions(range(colcnt[col]), [ cntz[row][col] for row in range(h) ]) for col in range(w) ]):
                scolpart = [ [ sorted(colpart[i][j]) for j in range(h) ] for i in range(w) ]
                for rowpart in product(*[ ordered_set_partitions(range(rowcnt[row]), [ cntz[row][col] for col in range(w) ]) for row in range(h) ]):
                    srowpart = [ [ sorted(rowpart[i][j]) for j in range(w) ] for i in range(h) ]
                    for perm_ass in product(*[ s[1].of_length(cnt) for cnt, s in zip(count_ass, tiling) ]):
                        arr = [ [ [] for j in range(w) ] for i in range(h) ]

                        for i, perm in enumerate(perm_ass):
                            arr[tiling[i][0][0]][tiling[i][0][1]] = perm

                        res = [ [None]*colcnt[col] for col in range(w) ]

                        cumul = 0
                        for row in range(h-1,-1,-1):
                            for col in range(w):
                                for idx, val in zip(scolpart[col][row], permute(srowpart[row][col], arr[row][col])):
                                    res[col][idx] = cumul + val
                            cumul += rowcnt[row]
                        yield Perm(flatten(res))

    def perms_of_length_with_cell_info(self, n):
        """Yield tuples of perms with their respective cell info.
 
        The cell info of a perm is a dictionary of cells to 3-tuples
        consisting of:
            - the standardized perm in the cell (the cell perm),
            - the values of the cell perm with regards to the perm, and
            - the indices of the cell perm with regards to the perm.
        """
        # TODO: Make not disgusting
        dim_j = self._dimensions.j
        tiling = list(((dim_j - 1 - cell.j, cell.i), block)
                      for cell, block
                      in self._blocks.items())
        h = max( k[0] for k,v in tiling ) + 1 if tiling else 1
        w = max( k[1] for k,v in tiling ) + 1 if tiling else 1

        def permute(arr, perm):
            res = [None] * len(arr)
            for i in range(len(arr)):
                res[i] = arr[perm[i]]
            return res

        def count_assignments(at, left):

            if at == len(tiling):
                if left == 0:
                    yield []
            elif tiling[at][1] is Block.point:
                # this doesn't need to be handled separately,
                # it's just an optimization
                if left > 0:
                    for ass in count_assignments(at + 1, left - 1):
                        yield [1] + ass
            else:
                for cur in range(left+1):
                    for ass in count_assignments(at + 1, left - cur):
                        yield [cur] + ass

        for count_ass in count_assignments(0, n):

            cntz = [ [ 0 for j in range(w) ] for i in range(h) ]

            for i, k in enumerate(count_ass):
                cntz[tiling[i][0][0]][tiling[i][0][1]] = k

            rowcnt = [ sum( cntz[row][col] for col in range(w) ) for row in range(h) ]
            colcnt = [ sum( cntz[row][col] for row in range(h) ) for col in range(w) ]

            for colpart in product(*[ ordered_set_partitions(range(colcnt[col]), [ cntz[row][col] for row in range(h) ]) for col in range(w) ]):
                scolpart = [ [ sorted(colpart[i][j]) for j in range(h) ] for i in range(w) ]
                for rowpart in product(*[ ordered_set_partitions(range(rowcnt[row]), [ cntz[row][col] for col in range(w) ]) for row in range(h) ]):
                    srowpart = [ [ sorted(rowpart[i][j]) for j in range(w) ] for i in range(h) ]
                    for perm_ass in product(*[ s[1].of_length(cnt) for cnt, s in zip(count_ass, tiling) ]):
                        arr = [ [ [] for j in range(w) ] for i in range(h) ]

                        for i, perm in enumerate(perm_ass):
                            arr[tiling[i][0][0]][tiling[i][0][1]] = perm

                        res = [ [None]*colcnt[col] for col in range(w) ]

                        cumul = 0
                        cell_info = {}
                        for row in range(h-1,-1,-1):
                            cumul_col = 0  # This records the current index inside the perm being created
                            for col in range(w):  # We're still building from left to right and bottom to top
                                unmixed = []  # The un-standardized perm inside the current cell we're working on
                                my_indices = []  # The indices of the current cell we're working on with regards to the final perm we're working on
                                for idx, val in zip(scolpart[col][row], permute(srowpart[row][col], arr[row][col])):  # Magic
                                    res[col][idx] = cumul + val  # I am within a single cell and we read from left to right and we get the next value to add
                                    unmixed.append(cumul + val)  # Samesies as one line above, but for us to keep later
                                    my_indices.append(idx + cumul_col)  # Reading left to right within a cell placing the index
                                if arr[row][col]:  # Cell is not empty
                                    cell = Cell(col, dim_j - row - 1)  # Getting the bottom left indexed cell back from the old indexing
                                    if cell not in cell_info:  # Not needed? But for sanity
                                        # We add cell information gathered to our dictionary
                                        cell_info[cell] = arr[row][col], tuple(unmixed), tuple(my_indices)
                                cumul_col += colcnt[col]  # Assuming colcnt[col] is the number of points in the column numbered 'col', this adds that amount to our total points of the permutation already placed when reading left to right
                            cumul += rowcnt[row]  # Similar to the cumul_col thing
                        yield Perm(flatten(res)), cell_info  # Yield the results, flatten here only removes brackets, e.g. [[0], [1]] becomes [0, 1] so it is ready to become the perm 01

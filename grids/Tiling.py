# TODO: Docstring
# TODO: Make python2.7 compatible once permuta is


import warnings

from builtins import dict
from collections import OrderedDict
from collections import namedtuple  # For Cell class
from itertools import product
from operator import itemgetter
from permuta import Perm
from permuta import PermSet
from permuta import Av
from permuta.misc import ordered_set_partitions, flatten
from permuta.descriptors import Descriptor

from .JsonAble import JsonAble


Cell = namedtuple("cell", ["i", "j"])


class Block(object):
    """Different blocks for Tilings, for convenience."""
    all = PermSet()
    point = PermSet([Perm(0,)])  # TODO: Make a new optimized perm set if this is a bottleneck
    increasing = PermSet.avoiding(Perm((1, 0)))
    decreasing = PermSet.avoiding(Perm((0, 1)))
    def __new__(_cls):
        raise RuntimeError("Block class should not be instantiated")


class Tiling(JsonAble):
    """Tiling class.

    Zero-indexed coordinates/cells from bottom left corner where the (i, j)
    cell is the cell in the i-th column and j-th row.
    """

    def __init__(self, tiles={}):
        # The dictionary of tiles
        tiling = {}
        # The horizontal and vertical dimensions, respectively
        i_dimension = j_dimension = 1
        # The integer that is hashed to get the hash of the tiling
        hash_sum = 0
        # A list of the cells that have points in them
        point_cells = []
        classes = []
        rows = []
        cols = []

        if tiles:
            # The set of all indices
            i_set, j_set = map(set, zip(*tiles))

            # The sorted list of all indices
            i_list, j_list = sorted(i_set), sorted(j_set)

            # The i and j dimensions of the tiling
            i_dimension = len(i_list)
            j_dimension = len(j_list)

            # Mappings from indices to actual indices
            i_actual = {i: actual for actual, i in enumerate(i_list)}
            j_actual = {j: actual for actual, j in enumerate(j_list)}


            for item in sorted(tiles.items()):
                # Add hash to hash sum
                hash_sum += hash(item)
                # Unpack item
                cell, block = item
                # Calculate actual cell
                actual_cell = Cell(i_actual[cell.i], j_actual[cell.j])
                # Add to row and col cache
                rows[actual_cell.j].append((actual_cell, block))
                cols[actual_cell.i].append((actual_cell, block))
                # Add to tiling
                tiling[actual_cell] = block
                # kk
                if block == Block.point:
                    point_cells.append(actual_cell)
                else:
                    classes.append(item)

        self._dict = tiling

        self._dimensions = Cell(i_dimension, j_dimension)
        self._hash = hash(hash_sum)
        self._point_cells = tuple(point_cells)
        self._classes = tuple(classes)
        self._rows = rows
        self._cols = cols

    @classmethod
    def _prepare_attr_dict(cls, attr_dict):
        # TODO: eval probably isn't the best way to do this
        return {"tiles": {eval(cell): eval("Av([" + block[3:-1] + "])" if block.startswith("Av") else block) for cell, block in attr_dict.items()}}

    def _to_json(self):
        return {str(cell): "Block.point" if block is Block.point else repr(block)
                for cell, block in self.items()}

    @property
    def point_cells(self):
        return self._point_cells

    @property
    def total_points(self):
        return len(self._point_cells)

    @property
    def classes(self):
        return self._classes

    def get_row(number):
        return self._rows[number]

    def get_col(number):
        return self._cols[number]

    def __eq__(self, other):
        return isinstance(other, Tiling) and hash(self) == hash(other) \
                                         and self.point_cells == other.point_cells \
                                         and self.classes == other.classes

    def __hash__(self):
        return self._hash

    def __repr__(self):
        format_string = "<A tiling of {} points and {} perm classes>"
        return format_string.format(self.total_points, len(self.classes))

    def __str__(self):
        max_i = self._max_i
        max_j = self._max_j

        result = []

        # Create tiling lines
        for i in range(2*max_i + 3):
            for j in range(2*max_j + 3):
                # Whether or not a vertical line and a horizontal line is present
                vertical = j % 2 == 0
                horizontal = i % 2 == 0
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
        row_width = 2*max_j + 4
        for (i, j), perm_set in self.items():
            # Check if label has been specified
            specified_label = self.__specified_labels.get(perm_set)
            if specified_label is None:
                # Use generic label (could reuse specified label)
                label = labels.get(perm_set)
                if label is None:
                    label = str(len(labels) + 1)
                    labels[perm_set] = label
            else:
                # If label specified, then use it
                label = specified_label
            index = (2*i + 1)*row_width + 2*j + 1
            result[index] = label

        # Legend at bottom
        for perm_set, label in labels.items():
            result.append(label)
            result.append(": ")
            result.append(str(perm_set))
            result.append("\n")

        return "".join(result)


class PermSetTiled(object):  # Really, it should be a described perm set
    """A perm set containing all perms that can be generated with a tiling."""
    def __init__(self, tiling):
        self.tiling = tiling

    def of_length(self, n):
        perms = set()

        tiling = list(self.tiling.items())
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
                        perms.add(Perm(flatten(res)))
        return perms

    def of_length_with_positions(self, n):
        perms_with_positions = []

        tiling = list(self.tiling.items())
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
                        where = {}
                        for row in range(h-1,-1,-1):
                            for col in range(w):
                                for idx, val in zip(scolpart[col][row], permute(srowpart[row][col], arr[row][col])):
                                    res[col][idx] = cumul + val
                                    where[res[col][idx]] = (row,col)
                            cumul += rowcnt[row]
                        perms_with_positions.append(( Perm(flatten(res) ), where ))
        return perms_with_positions

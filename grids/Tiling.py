# TODO: Docstring
# TODO: Make python2.7 compatible once permuta is


import warnings

from builtins import dict
from collections import OrderedDict
from itertools import product
from operator import itemgetter
from permuta import Perm
from permuta import PermSet
from permuta.misc import ordered_set_partitions, flatten
from permuta.descriptors import Descriptor


class Block(object):
    """Different blocks for Tilings, for convenience."""
    all = PermSet()
    point = PermSet([Perm(0,)])  # TODO: Make a new optimized perm set if this is a bottleneck
    increasing = PermSet.avoiding(Perm((1, 0)))
    decreasing = PermSet.avoiding(Perm((0, 1)))
    def __new__(_cls):
        warnings.warn("Block class should not be instantiated")


class Tiling(dict, Descriptor):
    """Tiling class.

    Coordinates/cells are tuples of (i, j) which work in the traditional matrix way.
    """

    __specified_labels = {}

    def __init__(self, tiles=()):
        info = []
        super(Tiling, self).__init__(self._init_helper(tiles, info))
        self._hash, self._max_i, self._max_j, self._point_cells = info
        #for key, value in iteritems(tiles):
        #    print(key, value)
        #if isinstance(rule, list):
        #    self.rule = {(i, j): rule[i][j]
        #                 for i in range(len(rule))
        #                 for j in range(len(rule[i]))
        #                 if rule[i][j] is not None}
        #else:
        #    self.rule = {(i, j): s
        #                 for ((i,j), s) in rule.items()
        #                 if s is not None}

    def _init_helper(self, tiles, info):
        point_perm_set = Block.point
        point_cells = []
        hash_sum = 0
        max_i = 0
        max_j = 0
        for key_val in tiles.items():  # Builds the tuple in python2
            hash_sum += hash(key_val)
            cell, perm_set = key_val
            if perm_set is point_perm_set:
                point_cells.append(cell)
            i, j = cell
            max_i = max(max_i, i)
            max_j = max(max_j, j)
            yield key_val
        info.append(hash(hash_sum))
        info.append(max_i)
        info.append(max_j)
        info.append(point_cells)

    @classmethod
    def label(cls, block, label):
        warnings.warn("Method signature may change", PendingDeprecationWarning)
        cls.__specified_labels[block] = label

    @property
    def point_cells(self):
        return self._point_cells

    @property
    def total_points(self):
        return len(self._point_cells)

    def get_row(number):
        return {cell: block for cell, block in self.items() if cell[0] == number}

    def get_col(number):
        return {cell: block for cell, block in self.items() if cell[1] == number}

    def __hash__(self):
        return self._hash

    def __repr__(self):
        format_string = "<A tiling of {} non-empty tiles>"
        return format_string.format(len(self))

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

    def rank(self):
        """Ranks Tiling by difficulty.
        
        0 - Empty Tiling
        1 - Tiling consisting only of points where none interleave.
        2 - Tiling consisting of points and sets where none interleave.
        3 - Tiling consisting of points and sets where points interleave in a column or row.
        4 - Tiling consisting of points and sets where a point and set interleave in a column or row.
        5 - Tiling consisting of points and sets where points interleave in an L or square shape.
        6 - Tiling consisting of points and sets where sets and points interleave in an L  or square shape but no sets interleave in a column or row.
        7 - Tiling consisting of points and sets where sets interleave in a column or row.
        8 - Tiling consisting of points and sets where sets interleave in an L shape.
        9 - Tiling consisting of points and sets where sets interleave in a square shape.
        """
        n = self._max_i + 1
        m = self._max_j + 1
        rows = [0]*n
        cols = [0]*m
        sets = []
        for i,j in self:
            if self[(i,j)] is Block.point:
                if rows[i] in (1,2):
                    rows[i] += 2
                else:
                    rows[i] = max(1, rows[i])
                if cols[j] in (1,2):
                    cols[j] += 2
                else:
                    cols[j] = max(1, cols[j])
            else:
                sets.append((i,j))
                if rows[i] in (1,3):
                    rows[i] = 4
                elif rows[i] in (2,4):
                    rows[i] = 7
                else:
                    rows[i] = max(2, rows[i])
                if cols[j] in (1,3):
                    cols[j] = 4
                elif cols[j] in (2,4):
                    cols[j] = 7
                else:
                    cols[j] = max(2, cols[j])

        res = max(max(rows), max(cols))
        
        for i,j in self:
            if self[(i,j)] is Block.point:
                if rows[i] == 3 and cols[j] == 3:
                    res = max(res, 5)
                elif rows[i] in (3,4) and cols[j] in (3,4):
                    res = max(res, 6) 
            else:
                if rows[i] == 4 and cols[j] == 4:
                    res = max(res, 6)
                elif rows[i] == 7 and cols[j] == 7:
                    res = max(res, 8)

        if res == 8:
            for i, a in enumerate(sets):
                for j, b in enumerate(sets[i+1:]):
                    for k, c in enumerate(sets[i+j+1:]):
                        for d in sets[i+j+k+1:]:
                            x, y, z, w = sorted((a,b,c,d))
                            if x[0] == y[0] and z[0] == w[0] and x[1] == z[1] and y[1] == w[1]:
                                res = 9

        return res


Tiling.label(Block.increasing, "/")
Tiling.label(Block.decreasing, "\\")
Tiling.label(Block.point, "o")


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

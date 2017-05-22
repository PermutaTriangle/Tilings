from .misc import compress_dict
from permuta.permutils import *
from permuta import Av
from collections import OrderedDict, defaultdict
from .Block import Block
from .PositiveClass import PositiveClass



class Factor():
    def __init__(self, blocks={}):
        if not blocks:
            raise ValueError('Factor cannot be empty')
        blocks = compress_dict(blocks)
        hash_sum = 0
        for cell, block in blocks.items():
            if block is not Block.point:
                if isinstance(block, PositiveClass):
                    blocks[cell] = PositiveClass(Av(lex_min(list(block.basis))))
                else:
                    blocks[cell] = Av(lex_min(list(block.basis)))
            hash_sum += hash((cell, blocks[cell]))
        dim_i = max(i for i,_ in blocks)+1
        dim_j = max(j for _,j in blocks)+1
        
        g = defaultdict(set)
        row = defaultdict(set)
        column = defaultdict(set)
        rev = {}
        for v, item in enumerate(blocks.items()):
            cell, block = item
            for u in row[cell[1]] | column[cell[0]]:
                g[v].add(u)
                g[u].add(v)
            row[cell[1]].add(v)
            column[cell[0]].add(v)
            rev[v] = block
        
        queue = [0]
        visited = {0}
        while queue:
            v = queue.pop(0)
            for u in g[v]:
                if u in visited:
                    continue
                visited.add(u)
                queue.append(u)
        if len(visited) != len(blocks):
            raise ValueError('Underlying graph of input dictionary is not connected and thus not a Factor')

        self.factor = OrderedDict(blocks)
        self.dimensions = dim_i, dim_j
        self._hash = hash(hash_sum)
        self._graph = dict(g), rev

    @property
    def graph(self):
        return self._graph

    def rotate(self):
        """Rotates factor 90 degrees positive."""
        new_blocks = dict()
        _, dim_j = self.dimensions
        for i, j in self.factor:
            new_blocks[(dim_j - j, i)] = self.factor[(i, j)]
        return Factor(new_blocks)

    def mirror(self):
        """Mirrors factor over x=y."""
        new_blocks = dict()
        for i, j in self.factor:
            new_blocks[(j, i)] = self.factor[(i, j)]
        return Factor(new_blocks)

    def minimum(self):
        all_symmetries = set()
        item = self
        for i in range(4):
            all_symmetries.add(item)
            all_symmetries.add(item.mirror())
            if i != 4:
                item = item.rotate()
        return min(all_symmetries)

    def lex_eq(self, other):
        if type(other) != type(self):
            return NotImplemented
        return self.minimum() == other.minimum()

    def isomorphic(self, other):
        if type(other) != type(self):
            return NotImplemented
        if len(other) != len(self):
            return False

        self_g, self_rev = self.graph
        other_g, other_rev = other.graph
        candidate_vertices = {}

        for vertex, neighbors in self_g.items():
            candidates = set()
            for other_vertex , other_neighbors in other_g.items():
                if len(neighbors) == len(other_neighbors) and self_rev[vertex] == other_rev[other_vertex]:
                    candidates.add(other_vertex)
            if len(candidates) == 0:
                return False
            candidate_vertices[vertex] = candidates

        src = min(candidate_vertices.items(), key=lambda x: len(x[1]))[0]

        def verify_graph(isomorphism, src):
            for candidate in candidate_vertices[src] - set(isomorphism.values()):
                for neighbor in self_g[src] & set(isomorphism.keys()):

                    if isomorphism[neighbor] not in other_g[candidate]:
                        return False
                new_isomorphism = isomorphism.copy()
                new_isomorphism[src] = candidate

                if len(new_isomorphism) == len(self_g):
                    return True
                for vertex in set(self_g.keys()) - set(isomorphism.keys()):
                    if verify_graph(new_isomorphism, vertex):
                        return True
            return False

        return verify_graph({}, src)

    def rank(self):
        """Ranks Tiling by difficulty.
        0 - Empty Tiling
        1 - Tiling consisting only of points with no interleaving.
        2 - Tiling consisting of points and sets where none interleave.
        3 - Tiling consisting of points and at least one set where points interleave in a column or row.
        4 - Tiling consisting of points and sets where a point and set interleave in a column or row.
        5 - Tiling consisting of points and at least one set where points interleave in an L or square shape.
        6 - Tiling consisting of points and sets where sets and points interleave in an L  or square shape but no sets interleave in a column or row.
        7 - Tiling consisting of points and sets where sets interleave in a column or row.
        8 - Tiling consisting of points and sets where sets interleave in an L shape.
        9 - Tiling consisting of points and sets where sets interleave in a square shape.
        """
        n, m = self.dimensions
        rows = [0] * n
        cols = [0] * m
        sets = []

        # Checks for column or row interleaving
        for i, j in self.factor:
            if self.factor[(i, j)] is Block.point:
                # Check for point-point or point-set interleaving
                if rows[i] in (1, 2):
                    rows[i] += 2
                # Otherwise we use the max of the previous value and the rank of having only a point
                else:
                    rows[i] = max(1, rows[i])
                # Identical to above but for columns
                if cols[j] in (1, 2):
                    cols[j] += 2
                else:
                    cols[j] = max(1, cols[j])
            else:
                sets.append((i, j))  # Store it as we need it to check for squares
                # Checks for point-set interleaving
                if rows[i] in (1, 3):
                    rows[i] = 4
                # Checks for set-set interleaving
                elif rows[i] in (2, 4):
                    rows[i] = 7
                # Otherwise we use the max of the previous value and the rank of having only a set
                else:
                    rows[i] = max(2, rows[i])
                # Identical to above but for rows
                if cols[j] in (1, 3):
                    cols[j] = 4
                elif cols[j] in (2, 4):
                    cols[j] = 7
                else:
                    cols[j] = max(2, cols[j])

        res = max(max(rows), max(cols))

        # Checks for L shaped interleaving
        for i, j in self.factor:
            if self.factor[(i, j)] is Block.point:
                # Checks if there is an L shape consisting of only points
                if rows[i] == 3 and cols[j] == 3:
                    res = max(res, 5)
                # Checks if there is an L shape with points and sets mixed
                elif rows[i] in (3, 4) and cols[j] in (3, 4):
                    res = max(res, 6)
            else:
                # Checks if there is an L shape with points and sets mixed
                if rows[i] == 4 and cols[j] == 4:
                    res = max(res, 6)
                # Checks if there is an L shape consisting only of sets
                elif rows[i] == 7 and cols[j] == 7:
                    res = max(res, 8)

        if res == 8:  # We only need to check if sets form a square if we already established L shape
            # Checks if sets form a square. Picks 4 points and sorts them then it's enough to check
            # that x_1 == x_2, y_1 == y_3, x_3 == x_4 and y_2 == y_4 to know if it's a square.
            for i, a in enumerate(sets):
                for j, b in enumerate(sets[i + 1:]):
                    for k, c in enumerate(sets[i + j + 1:]):
                        for d in sets[i + j + k + 1:]:
                            x, y, z, w = sorted((a, b, c, d))
                            if x[0] == y[0] and z[0] == w[0] and x[1] == z[1] and y[1] == w[1]:
                                res = 9

        return res

    # Dunder functions
    # Rich comparisons

    def __lt__(self, other):
        if type(other) != type(self):
            return NotImplemented
        if len(self) != len(other):
            return len(self) < len(other)
        self_keys = sorted(self.factor.keys())
        other_keys = sorted(other.factor.keys())
        if self_keys != other_keys:
            return self_keys < other_keys
        for key in self_keys:
            self_val = self.factor[key]
            other_val = other.factor[key]
            if self_val != other_val:
                if self_val == Av(Perm((0,))):
                    return True
                if other_val == Av(Perm((0,))):
                    return False
                if self_val == Block.point:
                    return True
                if other_val == Block.point:
                    return False
                return self.factor[key].basis < other.factor[key].basis
        return False

    def __eq__(self, other):
        if type(other) != type(self):
            return NotImplemented
        if len(self) != len(other):
            return False
        self_keys = sorted(self.factor.keys())
        other_keys = sorted(other.factor.keys())
        if self_keys != other_keys:
            return False
        for key in self_keys:
            if self.factor[key] != other.factor[key]:
                return False
        return True

    def __ne__(self, other):
        if type(other) != type(self):
            return NotImplemented
        if len(self) != len(other):
            return True
        self_keys = sorted(self.factor.keys())
        other_keys = sorted(other.factor.keys())
        if self_keys != other_keys:
            return True
        for key in self_keys:
            if self.factor[key] != other.factor[key]:
                return True
        return False

    def __gt__(self, other):
        return not (self < other or self == other)

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return not self < other

    # Other dunders

    def __hash__(self):
        return self._hash

    def __len__(self):
        return len([x for x in self.factor.values() if x is not None])

    def __repr__(self):
        format_string = "<A factor of {} points>"
        return format_string.format(len(self.factor))

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
        for cell, block in self.factor.items():
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
            row_index_from_top = dim_j - cell[1] - 1
            index = (2*row_index_from_top + 1)*row_width + 2*cell[0] + 1
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
   


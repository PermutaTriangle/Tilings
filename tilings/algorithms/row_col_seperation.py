from itertools import combinations


class Graph(object):
    """
    A weighted directed graph implemented with an adjacency matrix.

    The graph is made such that it is easy to merge to vertices. Merging
    vertices collapse to vertices together such that
        - The weight of the new vertex is the sum of the weights
        - The weight of the edges is the sum of the weight of the edges that
        went to any of the merged vertices before the merge.


    The graph supports 2 operations
        - `reduce`: who merge two vertices that were not connected by an edges
        and repeat as long as possible.
        - `break_cycle_in_all_ways`: Take a cycle in the graph and return a
        copy of the graph with a removed edges for each edges in the cycle.

    Moreover, one can also ask:
        - if the graph is acyclic with `is_acyclic`
        - if the graph is reduced with `is_acyclic`
        - for a cycle of the graph with `find_cycle`
        - For the vertex order implied by a reduced acyclic graph
    """

    def __init__(self, vertices, matrix=None):
        self._vertex_labels = [set([v]) for v in vertices]
        self._vertex_weights = [1 for _ in self._vertex_labels]
        self._matrix = matrix
        assert len(matrix) == len(self._vertex_labels)
        assert all(len(row) == len(self._matrix) for row in matrix)
        self._reduced = False
        self._is_acyclic = False

    @property
    def num_vertices(self):
        """
        The number of vertices of the graph
        """
        return len(self._vertex_weights)

    def _merge_vertices(self, v1, v2):
        """
        Merge the two vertices.

        Vertex and edges are merged and the weight are added. Then edges with a
        weight that is to small are discarded.
        """
        v2_label = self._vertex_labels.pop(v2)
        self._vertex_labels[v1].update(v2_label)
        v2_weight = self._vertex_weights.pop(v2)
        self._vertex_weights[v1] += v2_weight
        self._add_matrix_rows(v1, v2)
        self._add_matrix_columns(v1, v2)
        self._trim_edges(v1)

    def reduce(self):
        if self._reduced:
            return
        non_edge = self.find_non_edge()
        while non_edge:
            self._merge_vertices(non_edge[0], non_edge[1])
            non_edge = self.find_non_edge()
        self._reduced = True

    def find_non_edge(self):
        """
        Return a non-edge of the graph.

        A non edges is a pair of vertices `(v1, v2)` such that neither
        `(v1, v2)` or `(v2, v1)` is an edge in the graph.
        """
        for v1, v2 in combinations(range(self.num_vertices), 2):
            if not self._is_edge(v1, v2) and not self._is_edge(v2, v1):
                return (v1, v2)

    def is_acyclic(self):
        """
        Check if the graph is acyclic.

        To perform that check, the graph must first be reduced with the
        `reduce` method.
        """
        assert self._reduced, "Graph must first be reduced"
        if self._is_acyclic:
            return True
        for row in self._matrix:
            if row.count(0) == self.num_vertices:
                self._is_acyclic = True
                return True
        return False

    def _find_cycle(self):
        """
        Return the edges of a cycle of the graphs. The graphs first need to be
        reduced

        If the graph is acyclic returns None.
        """
        assert self._reduced, "Graph must first be reduced"
        for v1, v2 in combinations(range(self.num_vertices), 2):
            if self._is_edge(v1, v2) and self._is_edge(v2, v1):
                return ((v1, v2), (v2, v1))
        for v1, v2, v3 in combinations(range(self.num_vertices), 3):
            if self._matrix[v1][v2] != 0 and self._matrix[v2][v1] != 0:
                cycle = self._length_3_cyle(v1, v2, v3)
                if cycle:
                    return cycle
        self._is_acyclic = True
        return None

    def break_cycle_in_all_ways(self, edges):
        """
        Generator over Graph object obtained by removing one edge of the
        `edges` iterator.
        """
        for e in edges:
            new_graph = Graph.__new__(Graph)
            new_graph._vertex_labels = [vl.copy()
                                        for vl in self._vertex_labels]
            new_graph._vertex_weights = self._vertex_weights.copy()
            new_graph._matrix = [row.copy() for row in self._matrix]
            new_graph._matrix[e[0]][e[1]] = 0
            new_graph._reduced = False
            new_graph._is_acyclic = False
            yield new_graph

    def vertex_order(self):
        """
        Return the order of the vertex in a reduced acyclic graph.

        A reduced acyclic graph is an acyclic orientation of a complete graph.
        There it equivalent to an ordering of its vertices.

        To compute the vertex order, the graph must be reduced and acyclic.
        """
        assert self._reduced, "Graph must first be reduced"
        assert self.is_acyclic(), "Graph must be acyclic"
        vert_num_parent = [row.count(0) for row in self._matrix]
        print(vert_num_parent)
        print(self)
        return [
            p[1] for p in sorted(zip(vert_num_parent, self._vertex_labels))
        ]

    def _add_matrix_rows(self, row1_idx, row2_idx):
        """
        Deletes row 2 from the graph matrix and change row 1 to
        the sum of both row.
        """
        assert row1_idx != row2_idx
        row1 = self._matrix[row1_idx]
        row2 = self._matrix.pop(row2_idx)
        self._matrix[row1_idx] = list(map(sum, zip(row1, row2)))

    def _add_matrix_columns(self, col1_idx, col2_idx):
        """
        Deletes column 2 from the graph matrix and change column 1 to
        the sum of both column.
        """
        assert col1_idx != col2_idx
        for row in self._matrix:
            c2_value = row.pop(col2_idx)
            row[col1_idx] += c2_value

    def _trim_edges(self, vertex):
        """
        Remove all the edges that touch vertex that that have a weight which is
        too small.

        The weight of a vertex is too small if it is smaller than the product
        of the weights of the two vertex it connects.
        """
        v1 = vertex
        v1_weight = self._vertex_weights[v1]
        for v2 in range(self.num_vertices):
            v2_weight = self._vertex_weights[v2]
            weight_prod = v1_weight * v2_weight
            self._delete_edge_if_small(v1, v2, weight_prod)
            self._delete_edge_if_small(v2, v1, weight_prod)

    def _delete_edge_if_small(self, head, tail, cap):
        """
        Delete the edges that goes from head to tail if its weight is lower
        than the cap.
        """
        weight = self._matrix[head][tail]
        if weight < cap:
            self._matrix[head][tail] = 0

    def _is_edge(self, v1, v2):
        return self._matrix[v1][v2] != 0

    def _lenght3_cycle(self, v1, v2, v3):
        """
        Return the edges of a length 3 cycle containing the three vertices if
        such a cycle exist. Otherwise return None
        """
        def is_cycle(edges):
            return all(self._is_edge(*e) for e in edges)
        orientation1 = ((v1, v2), (v2, v3), (v3, v1))
        if is_cycle(orientation1):
            return orientation1
        orientation2 = ((v1, v3), (v3, v2), (v2, v1))
        if is_cycle(orientation2):
            return orientation2

    def __repr__(self):
        s = f'Graph over the vertices {self._vertex_labels}\n'
        s += f'Vertex weight is {self._vertex_weights}\n'
        for row in self._matrix:
            s += f'{row}\n'
        return s

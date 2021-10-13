"""
The row and columns separation algorithm.

The main algorithm for the separation is contained in the class
`_RowColSeparationSingleApplication`. The new separated tiling have new
length 2 crossing obstructions that would allow more separation.
The role of the class `RowColSeparation` is to make sure that row columns
separation is idempotent by applying the core algorithm until it stabilises.
"""
import heapq
from itertools import combinations, product
from typing import (
    TYPE_CHECKING,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

from tilings.map import CellMap

if TYPE_CHECKING:
    from tilings import GriddedPerm, Tiling
    from tilings.parameter_counter import ParameterCounter

Cell = Tuple[int, int]
Edge = Tuple[int, int]
Matrix = List[List[int]]
T = TypeVar("T")


class Graph(Generic[T]):
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
        - for a cycle of the graph with `find_cycle`
        - For the vertex order implied by a reduced acyclic graph
    """

    def __init__(self, vertices: Iterable[T], matrix: Matrix):
        self._vertex_labels = [set([v]) for v in vertices]
        self._vertex_weights = [1 for _ in self._vertex_labels]
        self._matrix = matrix
        assert len(matrix) == len(self._vertex_labels)
        assert all(len(row) == len(self._matrix) for row in matrix)
        self._reduced = False
        self._is_acyclic = False

    @property
    def num_vertices(self) -> int:
        """
        The number of vertices of the graph
        """
        return len(self._vertex_weights)

    def _merge_vertices(self, v1: int, v2: int) -> None:
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

    def reduce(self) -> None:
        if self._reduced:
            return
        non_edge = self.find_non_edge()
        while non_edge:
            self._merge_vertices(non_edge[0], non_edge[1])
            non_edge = self.find_non_edge()
        self._reduced = True

    def find_non_edge(self) -> Tuple[int, int]:
        """
        Return a non-edge of the graph.

        A non edges is a pair of vertices `(v1, v2)` such that neither
        `(v1, v2)` or `(v2, v1)` is an edge in the graph.
        """
        for v1, v2 in combinations(range(self.num_vertices), 2):
            if not self._is_edge(v1, v2) and not self._is_edge(v2, v1):
                return (v1, v2)

    def is_acyclic(self) -> bool:
        """
        Check if the graph is acyclic.

        To perform that check, the graph must first be reduced with the
        `reduce` method.
        """
        assert self._reduced, "Graph must first be reduced"
        if self._is_acyclic or self.num_vertices == 0:
            return True
        return self.find_cycle() is None

    def find_cycle(self) -> Optional[Union[Tuple[Edge, Edge], Tuple[Edge, Edge, Edge]]]:
        """
        Return the edges of a cycle of the graphs. The graphs first need to be
        reduced

        If a cycle of length 3 is return it means that no cycle of length 2
        exist.

        If the graph is acyclic, returns None.

        NOTE:

            One can prove that if a reduced graph is not acyclic it has either
            a cycle of length 2 or 3.
        """
        assert self._reduced, "Graph must first be reduced"
        for v1, v2 in combinations(range(self.num_vertices), 2):
            if self._is_edge(v1, v2) and self._is_edge(v2, v1):
                return ((v1, v2), (v2, v1))
        for v1, v2, v3 in combinations(range(self.num_vertices), 3):
            cycle = self._length3_cycle(v1, v2, v3)
            if cycle:
                return cycle
        self._is_acyclic = True
        return None

    def break_cycle_in_all_ways(self, edges: Iterable[Edge]) -> Iterator["Graph"]:
        """
        Generator over Graph object obtained by removing one edge of the
        `edges` iterator.
        """
        # pylint: disable=protected-access
        for e in edges:
            new_graph = Graph.__new__(Graph)
            new_graph._vertex_labels = [vl.copy() for vl in self._vertex_labels]
            new_graph._vertex_weights = self._vertex_weights.copy()
            new_graph._matrix = [row.copy() for row in self._matrix]
            new_graph._matrix[e[0]][e[1]] = 0
            new_graph._reduced = False
            new_graph._is_acyclic = False
            yield new_graph

    def vertex_order(self) -> List[Set[T]]:
        """
        Return the order of the vertex in a reduced acyclic graph.

        A reduced acyclic graph is an acyclic orientation of a complete graph.
        There it equivalent to an ordering of its vertices.

        To compute the vertex order, the graph must be reduced and acyclic.
        """
        assert self._reduced, "Graph must first be reduced"
        assert self.is_acyclic(), "Graph must be acyclic"
        vert_num_parent = [row.count(0) for row in self._matrix]
        return [p[1] for p in sorted(zip(vert_num_parent, self._vertex_labels))]

    def _add_matrix_rows(self, row1_idx: int, row2_idx: int) -> None:
        """
        Deletes row 2 from the graph matrix and change row 1 to
        the sum of both row.
        """
        assert row1_idx != row2_idx
        row1 = self._matrix[row1_idx]
        row2 = self._matrix.pop(row2_idx)
        self._matrix[row1_idx] = list(map(sum, zip(row1, row2)))

    def _add_matrix_columns(self, col1_idx: int, col2_idx: int) -> None:
        """
        Deletes column 2 from the graph matrix and change column 1 to
        the sum of both column.
        """
        assert col1_idx != col2_idx
        for row in self._matrix:
            c2_value = row.pop(col2_idx)
            row[col1_idx] += c2_value

    def _trim_edges(self, vertex: int) -> None:
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

    def _delete_edge_if_small(self, head: int, tail: int, cap: int) -> None:
        """
        Delete the edges that goes from head to tail if its weight is lower
        than the cap.
        """
        weight = self._matrix[head][tail]
        if weight < cap:
            self._matrix[head][tail] = 0

    def _is_edge(self, v1: int, v2: int) -> bool:
        return self._matrix[v1][v2] != 0

    def _length3_cycle(self, v1: int, v2: int, v3: int) -> Tuple[Edge, Edge, Edge]:
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

    def __repr__(self) -> str:
        s = "Graph over the vertices {}\n".format(self._vertex_labels)
        s += "Vertex weight is {}\n".format(self._vertex_weights)
        for row in self._matrix:
            s += "{}\n".format(row)
        return s

    def __lt__(self, other: object) -> bool:
        """
        A graph is 'smaller if it as more vertices.
        Useful for the priority queue
        """
        if not isinstance(other, Graph):
            return NotImplemented
        return self.num_vertices > other.num_vertices

    def __le__(self, other: object) -> bool:
        """
        A graph is 'smaller if it as more vertices.
        Useful for the priority queue
        """
        if not isinstance(other, Graph):
            return NotImplemented
        return self.num_vertices >= other.num_vertices


class _RowColSeparationSingleApplication:
    """
    Make the row separation of the tiling.
    """

    def __init__(self, tiling: "Tiling"):
        self._tiling = tiling
        self._active_cells = tuple(sorted(tiling.active_cells))
        self._ineq_matrices: Optional[Tuple[Matrix, Matrix]] = None
        self._max_row_order: Optional[List[Set[Cell]]] = None
        self._max_col_order: Optional[List[Set[Cell]]] = None

    def cell_at_idx(self, idx: int) -> Cell:
        """Return the cell at index `idx`."""
        return self._active_cells[idx]

    def cell_idx(self, cell: Cell) -> int:
        """Return the index of the cell"""
        return self._active_cells.index(cell)

    def _basic_matrix(self, row: bool) -> Matrix:
        """
        Compute the basic matrix of inequalities based only on difference in
        row and columns. If `row` is True return the matrix for the row,
        otherwise return if for the columns.
        """
        idx = 1 if row else 0
        m = []
        for c1 in self._active_cells:
            new_row = [1 if c1[idx] < c2[idx] else 0 for c2 in self._active_cells]
            m.append(new_row)
        return m

    @staticmethod
    def _row_cell_order(ob: "GriddedPerm") -> Tuple[Cell, Cell]:
        """
        Return the order of the two cells of a length 2 obstruction localized
        in a row.


        A cell `c1` is smaller than cell `c2` if all the points in `c1` are
        lower than all the point in `c2`.

        OUTPUT:
            A tuple (smaller_cell, bigger_cell)
        """
        assert len(ob) == 2, "Obstruction must be of length 2"
        c1, c2 = ob.pos
        assert c1[1] == c2[1], "Obstruction not a row obstruction"
        assert c1[0] != c2[0], "Obstruction is single cell"
        if ob.patt[0] == 0:
            return c2, c1
        return c1, c2

    @staticmethod
    def _col_cell_order(ob: "GriddedPerm") -> Tuple[Cell, Cell]:
        """
        Return the order of the two cells of a length 2 obstruction.

        A cell `c1` is smaller than a cell `c2` if all the points in `c1` must
        be on the left all points in `c2`.

        OUTPUT:
            A tuple (smaller_cell, bigger_cell)
        """
        assert len(ob) == 2, "Obstruction must be of length 2"
        c1, c2 = ob.pos
        assert c1[0] == c2[0], "Obstruction not a col obstruction"
        assert not c1[1] == c2[1], "Obstruction is single cell"
        return c2, c1

    def _add_ineq(self, ineq: Tuple[Cell, Cell], matrix: Matrix) -> None:
        """
        Add an inequalities to the matrix.

        The inequalities must a tuple (smaller_cell, bigger_cell).
        """
        small_c, big_c = ineq
        matrix[self.cell_idx(small_c)][self.cell_idx(big_c)] = 1

    def _complete_ineq_matrices(self) -> Tuple[Matrix, Matrix]:
        """
        Return the matrices of inequalities between the cells.

        OUTPUT:
            tuple `(row_matrix, col_matrix)`
        """
        if self._ineq_matrices is not None:
            return self._ineq_matrices
        row_m = self._basic_matrix(row=True)
        col_m = self._basic_matrix(row=False)
        filtered_obs = (
            ob
            for ob in self._tiling.obstructions
            if len(ob) == 2 and not ob.is_single_cell()
        )
        for ob in filtered_obs:
            c1, c2 = ob.pos
            if c1[1] == c2[1]:
                ineq = self._row_cell_order(ob)
                self._add_ineq(ineq, row_m)
            elif c1[0] == c2[0]:
                ineq = self._col_cell_order(ob)
                self._add_ineq(ineq, col_m)
        self._ineq_matrices = row_m, col_m
        return self._ineq_matrices

    def row_ineq_graph(self) -> Graph:
        return Graph(self._active_cells, self._complete_ineq_matrices()[0])

    def col_ineq_graph(self) -> Graph:
        return Graph(self._active_cells, self._complete_ineq_matrices()[1])

    @staticmethod
    def _all_order(graph: Graph, only_max: bool = False) -> Iterator[List[Set[Cell]]]:
        """
        Generator of ordering of the active cells.

        One can get only the maximal separation by setting `only_max` to
        `True`.

        The order are yielded in decreasing order of size.
        """
        max_sep_seen = 0
        graph.reduce()
        heap = [graph]
        while heap and (not only_max or max_sep_seen <= graph.num_vertices):
            graph = heapq.heappop(heap)
            cycle = graph.find_cycle()
            if cycle is None:
                yield graph.vertex_order()
            else:
                for g in graph.break_cycle_in_all_ways(cycle):
                    g.reduce()
                    heapq.heappush(heap, g)

    @staticmethod
    def _maximal_order(graph: Graph) -> List[Set[Cell]]:
        """Returns a order that maximise separation."""
        return next(_RowColSeparationSingleApplication._all_order(graph))

    def _separates_tiling(
        self, row_order: List[Set[Cell]], col_order: List[Set[Cell]]
    ) -> "Tiling":
        cell_map = self._get_cell_map(row_order, col_order)
        return cell_map.map_tiling(self._tiling)

    @staticmethod
    def _get_cell_map(
        row_order: List[Set[Cell]], col_order: List[Set[Cell]]
    ) -> CellMap:
        """
        Return the position of the according to the given row_order and
        col_order.

        This method does not account for any cleaning occuring in the initializer. For
        the complete cell map use `get_cell_map`.
        """
        row_cell_map = dict()
        for i, row in enumerate(row_order):
            for cell in row:
                row_cell_map[cell] = i
        cell_map = dict()
        for i, col in enumerate(col_order):
            for cell in col:
                cell_map[cell] = (i, row_cell_map[cell])
        return CellMap(cell_map)

    @property
    def max_row_order(self) -> List[Set[Cell]]:
        """A maximal order on the rows."""
        if self._max_row_order is not None:
            return self._max_row_order
        self._max_row_order = self._maximal_order(self.row_ineq_graph())
        return self._max_row_order

    @property
    def max_col_order(self) -> List[Set[Cell]]:
        """A maximal order on the columns."""
        if self._max_col_order is not None:
            return self._max_col_order
        self._max_col_order = self._maximal_order(self.col_ineq_graph())
        return self._max_col_order

    def separable(self) -> bool:
        """
        Test if the tiling is separable.

        A tiling is not separable the separation does not creates any new row
        or column.
        """
        ncol, nrow = self._tiling.dimensions
        return len(self.max_row_order) > nrow or len(self.max_col_order) > ncol

    def separated_tiling(self) -> "Tiling":
        """
        Return the one the possible maximal separation of the tiling.
        """
        return self._separates_tiling(self.max_row_order, self.max_col_order)

    def seperation_map(self) -> CellMap:
        """
        Return the position of map from the orginal tiling to the seperated tiling.

        This does not account for rows or column becoming empty.
        """
        row_order = self.max_row_order
        col_order = self.max_col_order
        return self._get_cell_map(row_order, col_order)

    def get_cell_map(self) -> CellMap:
        """
        Return the position of map from the orginal tiling to the seperated tiling.

        This is the cell map for the separated tiling returned by `separated_tiling`.
        """
        sep_tiling = self.separated_tiling()
        sep_cell_map = self.seperation_map()
        init_cell_map = sep_tiling.forward_map
        return sep_cell_map.compose(init_cell_map)

    def all_separated_tiling(self, only_max: bool = False) -> Iterator["Tiling"]:
        """
        Generator over all the possibles separation of the tiling.

        One can only get the maximal one by setting `only_max=True`.

        NOTE: The same tiling might be returned many times.
        """
        orders = product(
            self._all_order(self.row_ineq_graph(), only_max=only_max),
            self._all_order(self.col_ineq_graph(), only_max=only_max),
        )
        for row_order, col_order in orders:
            yield self._separates_tiling(row_order, col_order)


class RowColSeparation:
    """
    This is basically a simple wrapper around
    `_RowColSeparationSingleApplication` to ensure the separation is
    idempotent.

    It applies the row columns separation until it does not change the tiling.
    """

    def __init__(self, tiling: "Tiling") -> None:
        self._tiling = tiling
        self._separated_tilings: List["Tiling"] = []
        separation_algo = _RowColSeparationSingleApplication(self._tiling)
        while separation_algo.separable():
            new_sep = separation_algo.separated_tiling()
            self._separated_tilings.append(new_sep)
            separation_algo = _RowColSeparationSingleApplication(new_sep)

    def separable(self) -> bool:
        """
        Test if the tiling is separable.

        A tiling is not separable the separation does not creates any new row
        or column.
        """
        return bool(self._separated_tilings)

    def separated_tiling(self) -> "Tiling":
        """
        Return the one the possible maximal separation of the tiling.
        """
        if not self._separated_tilings:
            return self._tiling
        return self._separated_tilings[-1]

    def get_cell_map(self) -> CellMap:
        """
        Return the cell map obtained by applying the algorithm until no change.
        """
        cell_map = CellMap.identity(self._tiling.dimensions)
        separation_algo = _RowColSeparationSingleApplication(self._tiling)
        while separation_algo.separable():
            cell_map = cell_map.compose(separation_algo.get_cell_map())
            new_sep = separation_algo.separated_tiling()
            separation_algo = _RowColSeparationSingleApplication(new_sep)
        return cell_map

    def map_param(self, param: "ParameterCounter") -> "ParameterCounter":
        """
        Map the parameter the parent tiling to the corresponding parameters on the
        child.
        """
        separation_algo = _RowColSeparationSingleApplication(self._tiling)
        while separation_algo.separable():
            new_sep = separation_algo.separated_tiling()
            separation_map = separation_algo.seperation_map()
            param = separation_map.map_param(param)
            param.apply_row_col_map(new_sep.forward_map)
            separation_algo = _RowColSeparationSingleApplication(new_sep)
        return param

import pytest

from permuta import Perm
from tilings import Obstruction, Tiling
from tilings.algorithms.row_col_seperation import Graph


@pytest.fixture
def not_separable_tilings():
    t1 = Tiling(obstructions=[
        Obstruction(Perm((0, 1, 2)), ((0, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((1, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((2, 0),)*3),
        Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (2, 0)))
    ])
    t2 = Tiling(obstructions=[
        Obstruction(Perm((0, 1, 2)), ((0, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((1, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((2, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((3, 0),)*3),
        Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
        Obstruction(Perm((0, 1)), ((0, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((2, 0), (3, 0))),
    ])
    t3 = Tiling(obstructions=[
        Obstruction(Perm((0, 1, 2)), ((0, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((1, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((2, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((3, 0),)*3),
        Obstruction(Perm((0, 1)), ((0, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((0, 0), (3, 0))),
        Obstruction(Perm((1, 0)), ((1, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (3, 0))),
    ])
    return [t1, t2, t3]


@pytest.fixture
def seperable_tilings():
    t1 = Tiling(obstructions=[
        Obstruction(Perm((0, 1, 2)), ((0, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((1, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((2, 0),)*3),
        Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((0, 0), (2, 0))),
    ])
    t2 = Tiling(obstructions=[
        Obstruction(Perm((0, 1, 2)), ((0, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((1, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((2, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((3, 0),)*3),
        Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
        Obstruction(Perm((0, 1)), ((0, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((0, 0), (3, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((2, 0), (3, 0))),
    ])
    # Separation of many cell togheter
    t3 = Tiling(obstructions=[
        Obstruction(Perm((0, 1, 2)), ((0, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((1, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((2, 0),)*3),
        Obstruction(Perm((0, 1, 2)), ((3, 0),)*3),
        Obstruction(Perm((0, 1)), ((0, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((0, 0), (3, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (2, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (3, 0))),
    ])
    return [t1, t2, t3]


# ----------------------------------------------------------------------------
#           Test for the Graph class
# ----------------------------------------------------------------------------


@pytest.fixture
def matrix():
    return [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


@pytest.fixture
def edges():
    return ((0, 1), (0, 3), (2, 3), (3, 3))


@pytest.fixture
def graph_with_matrix(matrix):
    G = Graph(range(3), [])
    G._matrix = matrix
    return G


@pytest.fixture
def graph1(edges):
    return Graph(range(5), edges)


@pytest.fixture
def graph2():
    edges = ((0, 2), (1, 0), (1, 2), (1, 3), (2, 0), (2, 3), (3, 2))
    return Graph(range(4), edges)


@pytest.fixture
def graph3():
    edges = ((0, 1), (0, 2))
    return Graph(range(3), edges)


def test_init(edges):
    G = Graph('abcde', edges)
    assert G._matrix == Graph._adjacency_matrix(5, edges)
    assert G._vertex_labels == [set(c) for c in 'abcde']
    assert G._vertex_weights == [1 for _ in range(5)]
    assert not G._reduced
    assert not G._is_acyclic


def test_num_vertices(graph_with_matrix):
    assert graph_with_matrix.num_vertices == 3


def test_adjacency_matrix(edges):
    assert (Graph._adjacency_matrix(5, edges) ==
            [[0, 1, 0, 1, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 1, 0],
             [0, 0, 0, 1, 0],
             [0, 0, 0, 0, 0]])


def test_add_matrix_rows1(graph_with_matrix):
    graph_with_matrix._add_matrix_rows(0, 1)
    assert graph_with_matrix._matrix == [[5, 7, 9], [7, 8, 9]]


def test_add_matrix_rows2(graph_with_matrix):
    graph_with_matrix._add_matrix_rows(0, 2)
    assert graph_with_matrix._matrix == [[8, 10, 12], [4, 5, 6]]


def test_add_matrix_rows3(graph_with_matrix):
    graph_with_matrix._add_matrix_rows(1, 2)
    assert graph_with_matrix._matrix == [[1, 2, 3], [11, 13, 15]]


def test_add_matrix_columns1(graph_with_matrix):
    graph_with_matrix._add_matrix_columns(0, 1)
    assert graph_with_matrix._matrix == [[3, 3], [9, 6], [15, 9]]


def test_add_matrix_columns2(graph_with_matrix):
    graph_with_matrix._add_matrix_columns(0, 2)
    assert graph_with_matrix._matrix == [[4, 2], [10, 5], [16, 8]]


def test_add_matrix_columns3(graph_with_matrix):
    graph_with_matrix._add_matrix_columns(1, 2)
    assert graph_with_matrix._matrix == [[1, 5], [4, 11], [7, 17]]


def test_merge_vertices(graph1, graph2):
    graph1._merge_vertices(2, 4)
    assert graph1.num_vertices == 4
    assert graph1._vertex_labels == [{0}, {1}, {2, 4}, {3}]
    assert graph1._vertex_weights == [1, 1, 2, 1]
    assert (graph1._matrix == [
        [0, 1, 0, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1],
    ])
    graph1._merge_vertices(0, 2)
    assert graph1.num_vertices == 3
    assert graph1._vertex_labels == [{0, 2, 4}, {1}, {3}]
    assert graph1._vertex_weights == [3, 1, 1]
    assert (graph1._matrix == [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 1],
    ])
    graph2._merge_vertices(0, 3)
    assert graph2.num_vertices == 3
    assert graph2._vertex_labels == [{0, 3}, {1}, {2}]
    assert graph2._vertex_weights == [2, 1, 1]
    assert (graph2._matrix == [
        [0, 0, 2],
        [2, 0, 1],
        [2, 0, 0],
    ])


def test_delete_edge_if_smaller(graph_with_matrix):
    graph_with_matrix._delete_edge_if_small(0, 1, 1)
    assert graph_with_matrix._matrix[0][1] == 2
    graph_with_matrix._delete_edge_if_small(0, 1, 2)
    assert graph_with_matrix._matrix[0][1] == 2
    graph_with_matrix._delete_edge_if_small(0, 1, 3)
    assert graph_with_matrix._matrix[0][1] == 0
    assert graph_with_matrix._matrix == [[1, 0, 3], [4, 5, 6], [7, 8, 9]]


def test_trim_edges(graph_with_matrix):
    graph_with_matrix._vertex_weights[1] = 3
    graph_with_matrix._trim_edges(1)
    assert (graph_with_matrix._matrix == [
        [1, 0, 3],
        [4, 0, 6],
        [7, 8, 9],
    ])


def test_find_non_edges(graph2):
    assert set(graph2.find_non_edge()) == {0, 3}


def test_reduce(graph1, graph2):
    graph2.reduce()
    assert graph2._matrix == [[0, 0, 2], [2, 0, 1], [2, 0, 0]]
    graph1.reduce()
    assert graph1._matrix == [[0]]
    assert graph1._reduced


def test_is_acyclic(graph1, graph2, graph3):
    graph2.reduce()
    assert not graph2.is_acyclic()
    for g in graph2.break_cycle_in_all_ways([(0, 2), (2, 0)]):
        g.reduce()
        assert g.is_acyclic()
    graph1.reduce()
    assert graph1.is_acyclic()
    graph3.reduce()
    print(graph3)
    assert graph3.is_acyclic()


def test_find_cyle(graph1, graph2):
    graph2.reduce()
    assert set(graph2._find_cycle()) == set([(0, 2), (2, 0)])
    graph1.reduce()
    assert graph1._find_cycle() is None


def test_break_cycle_in_all_ways(graph2):
    graph2.reduce()
    childs = list(graph2.break_cycle_in_all_ways([(0, 2), (2, 0)]))
    assert len(childs) == 2
    g = childs[0]
    assert g._matrix == [[0, 0, 0], [2, 0, 1], [2, 0, 0]]
    g = childs[1]
    assert g._matrix == [[0, 0, 2], [2, 0, 1], [0, 0, 0]]
    assert g._vertex_labels == graph2._vertex_labels
    assert g._vertex_weights == graph2._vertex_weights
    # Test that changes on g does not affect graph2
    g._matrix[0][1] = 10
    assert graph2._matrix[0][1] == 0
    g._matrix[0] = None
    assert graph2._matrix[0] is not None
    g._vertex_labels[0].add(10)
    assert graph2._vertex_labels[0] == set([0, 3])
    g._vertex_labels[0] = None
    assert graph2._vertex_labels[0] == set([0, 3])
    g._vertex_weights[1] = 10
    assert graph2._vertex_weights[1] == 1


def test_vertex_order(graph2, graph3):
    graph2.reduce()
    vertices = graph2._vertex_labels
    childs = list(graph2.break_cycle_in_all_ways([(0, 2), (2, 0)]))
    g = childs[0]
    g.reduce()
    assert g.vertex_order() == [vertices[1], vertices[2], vertices[0]]
    g = childs[1]
    g.reduce()
    assert g.vertex_order() == [vertices[1], vertices[0], vertices[2]]

    print(graph3)
    graph3.reduce()
    assert graph3.vertex_order() == [set([0]), set([1, 2])]

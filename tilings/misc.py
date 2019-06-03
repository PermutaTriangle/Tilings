from collections import defaultdict
from functools import reduce


def map_cell(col_mapping, row_mapping, cell):
    return (col_mapping[cell[0]], row_mapping[cell[1]])


def union_reduce(iterable):
    """Returns the union of the elements contained in the iterables."""
    return reduce(set.__or__, map(set, iterable), set())


def intersection_reduce(iterable):
    """Returns the intersection of the iterables."""
    try:
        return reduce(set.__and__, map(set, iterable))
    except Exception:
        return set()


def is_tree(edges):
    """
    Return True if the undirected graph is a tree.

    That is, it is has no cycles and is connected.
    """
    adj_table = adjacency_table(edges)
    return len(edges) + 1 == len(adj_table) and is_connected(adj_table)


def adjacency_table(edges):
    """Return adjacency table of edges."""
    adj_table = defaultdict(set)
    for c1, c2 in edges:
        adj_table[c1].add(c2)
        adj_table[c2].add(c1)
    return adj_table


def is_connected(adj_table):
    """Return True if graph with adjacency table is connected."""
    if not adj_table:
        return True
    visited = {cell: False for cell in adj_table}

    # pick some start vertex
    for start in adj_table:
        break

    queue = [start]
    while queue:
        curr = queue.pop()
        for vertex in adj_table[curr]:
            if not visited[vertex]:
                queue.append(vertex)
                visited[vertex] = True
    return all(x for x in visited.values())

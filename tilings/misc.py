"""
Collection of function that are not directly related to the code but still
useful.
"""
from functools import reduce
from typing import Dict, Iterable, Iterator, Sequence, Set, Tuple, TypeVar

Vertex = TypeVar("Vertex")
T = TypeVar("T")
AdjTable = Dict[Vertex, Set[Vertex]]
Cell = Tuple[int, int]


def map_cell(col_mapping: Dict[int, int], row_mapping: Dict[int, int], cell: Cell):
    return (col_mapping[cell[0]], row_mapping[cell[1]])


def union_reduce(iterables: Iterable[Iterable[T]]) -> Set[T]:
    """
    Returns the union of the elements contained in the iterables.

    >>> sorted(union_reduce(([1,2], [2,3])))
    [1, 2, 3]
    >>> sorted(union_reduce(([], range(0, 10, 2))))
    [0, 2, 4, 6, 8]
    >>> union_reduce(([], []))
    set()
    """
    sets: Iterator[Set[T]] = map(set, iterables)
    return reduce(set.__or__, sets, set())


def intersection_reduce(iterables: Iterable[Iterable[T]]) -> Set[T]:
    """Returns the intersection of the iterables."""
    try:
        sets: Iterator[Set[T]] = map(set, iterables)
        return reduce(set.__and__, sets)
    except TypeError:
        return set()


def is_tree(vertices: Sequence[Vertex], edges: Sequence[Tuple[Vertex, Vertex]]) -> bool:
    """
    Return True if the undirected graph is a tree.

    That is, it is has no cycles and is connected.
    """
    if not vertices:
        return True
    adj_table = adjacency_table(vertices, edges)
    return len(edges) + 1 == len(vertices) and is_connected(adj_table)


def adjacency_table(
    vertices: Sequence[Vertex], edges: Sequence[Tuple[Vertex, Vertex]]
) -> AdjTable:
    """Return adjacency table of edges."""
    adj_table = {v: set() for v in vertices}  # type: AdjTable
    for c1, c2 in edges:
        adj_table[c1].add(c2)
        adj_table[c2].add(c1)
    return adj_table


def is_connected(adj_table: AdjTable) -> bool:
    """Return True if graph with adjacency table is connected."""
    if not adj_table:
        return True
    visited = {cell: False for cell in adj_table}
    start_vertex = next(iter(adj_table.keys()))
    visited[start_vertex] = True
    stack = [start_vertex]
    while stack:
        curr = stack.pop()
        for vertex in adj_table[curr]:
            if not visited[vertex]:
                stack.append(vertex)
                visited[vertex] = True
    return all(visited.values())


def multinomial(lst):
    """
    Returns the multinomial. Taken from
    https://stackoverflow.com/questions/46374185/does-python-have-a-function-which-computes-multinomial-coefficients
    """
    res, i = 1, sum(lst)
    i0 = lst.index(max(lst))
    for a in lst[:i0] + lst[i0 + 1 :]:
        for j in range(1, a + 1):
            res *= i
            res //= j
            i -= 1
    return res


# The code below is magical and comes from
# https://codereview.stackexchange.com/questions/1526/finding-all-k-subset-partitions


def partitions_iterator(lst: Sequence[T]) -> Iterator[Tuple[Tuple[T, ...], ...]]:
    """
    Iterator over all the possible partitions of a list. A partition is yielded
    as a list of list.

    The partition in a single part and the parition consisting of only
    singleton are not returned.

    >>> for partition in partitions_iterator([1, 2, 3]):
    ...     print(partition)
    ((1, 2), (3,))
    ((1,), (2, 3))
    ((1, 3), (2,))
    """
    for i in range(2, len(lst)):
        for part in algorithm_u(lst, i):
            yield tuple(map(tuple, part))


def algorithm_u(ns, m):
    # pylint: disable=too-many-statements,too-many-branches
    def visit(n, a):
        ps = [[] for i in range(m)]
        for j in range(n):
            ps[a[j + 1]].append(ns[j])
        return ps

    def f(mu, nu, sigma, n, a):
        if mu == 2:
            yield visit(n, a)
        else:
            for v in f(mu - 1, nu - 1, (mu + sigma) % 2, n, a):
                yield v
        if nu == mu + 1:
            a[mu] = mu - 1
            yield visit(n, a)
            while a[nu] > 0:
                a[nu] = a[nu] - 1
                yield visit(n, a)
        elif nu > mu + 1:
            if (mu + sigma) % 2 == 1:
                a[nu - 1] = mu - 1
            else:
                a[mu] = mu - 1
            if (a[nu] + sigma) % 2 == 1:
                for v in b(mu, nu - 1, 0, n, a):
                    yield v
            else:
                for v in f(mu, nu - 1, 0, n, a):
                    yield v
            while a[nu] > 0:
                a[nu] = a[nu] - 1
                if (a[nu] + sigma) % 2 == 1:
                    for v in b(mu, nu - 1, 0, n, a):
                        yield v
                else:
                    for v in f(mu, nu - 1, 0, n, a):
                        yield v

    def b(mu, nu, sigma, n, a):
        if nu == mu + 1:
            while a[nu] < mu - 1:
                yield visit(n, a)
                a[nu] = a[nu] + 1
            yield visit(n, a)
            a[mu] = 0
        elif nu > mu + 1:
            if (a[nu] + sigma) % 2 == 1:
                for v in f(mu, nu - 1, 0, n, a):
                    yield v
            else:
                for v in b(mu, nu - 1, 0, n, a):
                    yield v
            while a[nu] < mu - 1:
                a[nu] = a[nu] + 1
                if (a[nu] + sigma) % 2 == 1:
                    for v in f(mu, nu - 1, 0, n, a):
                        yield v
                else:
                    for v in b(mu, nu - 1, 0, n, a):
                        yield v
            if (mu + sigma) % 2 == 1:
                a[nu - 1] = 0
            else:
                a[mu] = 0
        if mu == 2:
            yield visit(n, a)
        else:
            for v in b(mu - 1, nu - 1, (mu + sigma) % 2, n, a):
                yield v

    n = len(ns)
    a = [0] * (n + 1)
    for j in range(1, m + 1):
        a[n - m + j] = j - 1
    return f(m, n, 0, n, a)

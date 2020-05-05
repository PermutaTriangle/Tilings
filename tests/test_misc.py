from tilings.misc import intersection_reduce, is_tree, partitions_iterator


def test_partitions_iterator():
    actual_partition = sorted([((1, 2), (3,)), ((1,), (2, 3)), ((1, 3), (2,))])
    assert sorted(partitions_iterator([1, 2, 3])) == actual_partition
    assert list(partitions_iterator([1])) == []
    assert list(partitions_iterator([])) == []


def test_intersection_reduce():
    assert intersection_reduce([]) == set()
    assert intersection_reduce([(1, 2, 3), (2, 3, 4), (3, 4, 5)]) == set([3])
    assert intersection_reduce([(1, 2, 3)]) == set([1, 2, 3])


def test_is_tree():
    assert is_tree([], [])
    assert is_tree([0], [])
    assert not is_tree([0, 1], [])
    assert not is_tree([0, 1, 2], [(0, 1)])
    assert is_tree([0, 1, 2], [(0, 1), (1, 2)])
    assert not is_tree([0, 1, 2], [(0, 1), (1, 2), (2, 0)])

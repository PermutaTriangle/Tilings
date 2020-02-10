from tilings.misc import intersection_reduce, partitions_iterator


def test_partitions_iterator():
    actual_partition = sorted([
        [[1, 2], [3]],
        [[1], [2, 3]],
        [[1, 3], [2]],
    ])
    assert sorted(partitions_iterator([1, 2, 3])) == actual_partition
    assert list(partitions_iterator([1])) == []
    assert list(partitions_iterator([])) == []


def test_intersection_reduce():
    assert intersection_reduce([]) == set()
    assert intersection_reduce([(1, 2, 3), (2, 3, 4), (3, 4, 5)]) == set([3])
    assert intersection_reduce([(1, 2, 3)]) == set([1, 2, 3])

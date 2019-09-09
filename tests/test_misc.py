from tilings.misc import partitions_iterator


def test_partitions_iterator():
    actual_partition = sorted([
        [[1, 2], [3]],
        [[1], [2, 3]],
        [[1, 3], [2]],
        [[1], [2], [3]],
    ])
    assert sorted(partitions_iterator([1, 2, 3])) == actual_partition
    assert list(partitions_iterator([1])) == []
    assert list(partitions_iterator([])) == []

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

from permuta import Perm
from grids_two import Tiling, Obstruction


def test_compression():
    tiling = Tiling(
        positive_cells=frozenset({(2, 0), (1, 0), (3, 1)}),
        possibly_empty=frozenset({(3, 0)}),
        obstructions=[
            Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
            Obstruction(Perm((0, 1)), ((1, 0), (2, 0))),
            Obstruction(Perm((0, 1)), ((1, 0), (3, 0))),
            Obstruction(Perm((0, 1)), ((2, 0), (2, 0))),
            Obstruction(Perm((0, 1)), ((2, 0), (3, 0))),
            Obstruction(Perm((0, 1)), ((3, 1), (3, 1))),
            Obstruction(Perm((1, 0)), ((3, 0), (3, 0))),
            Obstruction(Perm((1, 0)), ((3, 1), (3, 0))),
            Obstruction(Perm((1, 0)), ((3, 1), (3, 1))),
            Obstruction(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 0))),
            Obstruction(Perm((0, 1, 2)), ((3, 0), (3, 0), (3, 1))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (1, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (1, 0), (3, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (2, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((1, 0), (2, 0), (3, 0))),
            Obstruction(Perm((2, 1, 0)), ((2, 0), (2, 0), (2, 0))),
            Obstruction(Perm((2, 1, 0)), ((2, 0), (2, 0), (3, 0)))])

    assert tiling == Tiling.decompress(tiling.compress())

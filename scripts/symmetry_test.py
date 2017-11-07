import random
import sys

from grids_two import Obstruction, Tiling
from permuta import Perm


def random_obstruction(length, i, j):
    perm = Perm.random(length)
    pos = [(random.randint(0, i), random.randint(0, j)) for x in range(length)]
    return Obstruction(perm, pos)


def random_tiling():
    dimensions = (random.randint(3, 15), random.randint(3, 15))
    if dimensions[0] > dimensions[1]:
        dimensions = (dimensions[1], dimensions[0])
    nobs = random.randint(3, 10)
    possibly_empty = set()
    positive_cells = set()
    point_cells = set()
    obstructions = []
    for i in range(nobs):
        length = random.randint(2, 5)
        ob = random_obstruction(length, *dimensions)
        for p in ob.pos:
            if p not in possibly_empty:
                possibly_empty.add(p)
        obstructions.append(ob)
    return Tiling(possibly_empty=possibly_empty,
                  positive_cells=positive_cells,
                  point_cells=point_cells,
                  obstructions=obstructions)


cnt = 0

while True:
    tiling = random_tiling()

    # print(tiling)
    # sys.exit(0)

    if tiling.rotate90().rotate90() != tiling.rotate180():
        print(tiling)
        assert tiling.rotate90().rotate90() == tiling.rotate180()

    if tiling.rotate90().rotate90().rotate90() != tiling.rotate270():
        print(tiling)
        assert tiling.rotate90().rotate90().rotate90() == tiling.rotate270()

    if tiling.rotate90().rotate90().rotate90().rotate90() != tiling:
        print(tiling)
        assert tiling.rotate90().rotate90().rotate90().rotate90() == tiling

    if tiling.rotate90().rotate180() != tiling.rotate270():
        print(tiling)
        assert tiling.rotate90().rotate180() == tiling.rotate270()

    if tiling.rotate180().rotate90() != tiling.rotate270():
        print(tiling)
        assert tiling.rotate180().rotate90() == tiling.rotate270()

    if tiling.rotate180().rotate180() != tiling:
        print(tiling)
        assert tiling.rotate180().rotate180() == tiling

    if tiling.rotate270().rotate90() != tiling:
        print(tiling)
        assert tiling.rotate270().rotate90() == tiling

    if tiling.rotate90().rotate270() != tiling:
        print(tiling)
        assert tiling.rotate90().rotate270() == tiling

    if tiling.reverse().reverse() != tiling:
        print(tiling)
        assert tiling.reverse().reverse() == tiling

    if tiling.complement().complement() != tiling:
        print(tiling)
        assert tiling.complement().complement() == tiling

    if tiling.inverse().inverse() != tiling:
        print(tiling)
        assert tiling.inverse().inverse() == tiling

    if tiling.antidiagonal().antidiagonal() != tiling:
        print(tiling)
        assert tiling.antidiagonal().antidiagonal() == tiling

    if tiling.reverse().complement() != tiling.complement().reverse():
        print(tiling)
        assert tiling.reverse().complement() == tiling.complement().reverse()

    if tiling.reverse().complement() != tiling.rotate180():
        print(tiling)
        assert tiling.reverse().complement() == tiling.rotate180()

    if tiling.rotate180().inverse() != tiling.antidiagonal():
        print(tiling)
        assert tiling.rotate180().inverse() == tiling.antidiagonal()

    cnt += 1

    # if not cnt % 1000000:
    if not cnt % 10:
        print(cnt)

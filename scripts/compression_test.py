from permuta import Perm
from grids_two import Obstruction, Tiling
import random


def random_obstruction(length, i, j):
    perm = Perm.random(length)
    pos = [(random.randint(0, i), random.randint(0, j)) for x in range(length)]
    return Obstruction(perm, pos)


def random_tiling():
    dimensions = (random.randint(3, 15), random.randint(3, 15))
    if dimensions[0] > dimensions[1]:
        dimensions = (dimensions[1], dimensions[0])
    nobs = random.randint(3, dimensions[0] * dimensions[1])
    possibly_empty = set()
    positive_cells = set()
    point_cells = set()
    obstructions = []
    for i in range(nobs):
        length = random.randint(2, 5)
        ob = random_obstruction(length, *dimensions)
        for p in ob.pos:
            if p not in possibly_empty and p not in positive_cells:
                choice = random.randint(0, 1)
                if choice:
                    possibly_empty.add(p)
                else:
                    positive_cells.add(p)
        obstructions.append(ob)
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            if (i, j) not in positive_cells and (i, j) not in possibly_empty:
                choice = random.randint(0, 3)
                if not choice:
                    point_cells.add((i, j))
    return Tiling(possibly_empty=possibly_empty,
                  positive_cells=positive_cells,
                  point_cells=point_cells,
                  obstructions=obstructions)


permmap = dict()
permlist = list()
cnt = 0

while True:
    tiling = random_tiling()
    for ob in tiling.obstructions:
        if ob.patt not in permmap:
            permmap[ob.patt] = len(permmap)
            permlist.append(ob.patt)
    # print(tiling)
    # print(tiling.compress(permmap))
    # print(Tiling.decompress(tiling.compress(permmap), permlist))

    if tiling != Tiling.decompress(tiling.compress(permmap), permlist):
        print(tiling)
        print(permmap)
        print(permlist)
        assert tiling == Tiling.decompress(tiling.compress(permmap), permlist)
    cnt += 1

    # if not cnt % 1000000:
    if not cnt % 1000000:
        print(cnt)

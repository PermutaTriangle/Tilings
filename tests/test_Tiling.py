import pytest
import random

from permuta import Perm
from permuta import PermSet

from grids import Cell
from grids import Block
from grids import Tiling


#
# Fixtures
#


@pytest.fixture(scope="module",
        params=[{cell: random.choice([PermSet.avoiding(Perm.random(random.randint(0, 15))),
                                      Block.point,
                                      Block.increasing,
                                      Block.decreasing])
                 for cell in set((random.randint(0, 127),
                                  random.randint(0, 127))
                                  for _ in range(random.randint(0, 15)))}
                for _ in range(32)] + [{}])
def random_tiling_dict(request):
    return request.param


@pytest.fixture(scope="module",
                params=[
                    dict(tilings=[Tiling({Cell(0, 0): PermSet.avoiding(Perm((1, 2, 0)))})],
                         basis=[Perm((1, 2, 0))]),
                    dict(tilings=[Tiling({Cell(0, 0): PermSet.avoiding(Perm((4, 0, 1, 2, 3)))})],
                         basis=[Perm((4, 0, 1, 2, 3))]),
                    dict(tilings=[Tiling({Cell(0, 0): Block.increasing,
                                          Cell(1, 0): Block.increasing}),
                                 ],
                         basis=[Perm((2, 1, 0)),
                                Perm((2, 0, 3, 1)),
                                Perm((1, 0, 3, 2))]),
                    dict(tilings=[Tiling({Cell(0, 0): Block.decreasing,
                                          Cell(1, 0): Block.increasing}),
                                 ],
                         basis=[Perm((1, 2, 0)),
                                Perm((0, 2, 1))]),
                    dict(tilings=[Tiling({Cell(0, 0): Block.increasing,
                                          Cell(1, 0): Block.increasing}),
                                  Tiling({Cell(0, 0): Block.increasing,
                                          Cell(0, 1): Block.increasing}),
                                 ],
                         basis=[Perm((2, 1, 0)),
                                Perm((1, 0, 3, 2))]),
                    dict(tilings=[Tiling({Cell(0, 0): Block.increasing,
                                          Cell(0, 1): Block.decreasing,
                                          Cell(1, 0): Block.decreasing,
                                          Cell(1, 1): Block.increasing}),
                                 ],
                         basis=[Perm((1, 0, 3, 2)),
                                Perm((2, 3, 0, 1))]),
                    dict(tilings=[Tiling({Cell(0, 3): Block.increasing,
                                          Cell(1, 1): Block.decreasing,
                                          Cell(1, 2): Block.increasing,
                                          Cell(2, 0): Block.decreasing,
                                          Cell(2, 4): Block.increasing}),
                                 ],
                         basis=[Perm((0, 2, 1)),
                                Perm((3, 2, 0, 1))]),
                    dict(tilings=[Tiling({Cell(0, 0): PermSet.avoiding(Perm((1, 2, 0))),
                                          Cell(1, 0): PermSet.avoiding(Perm((0, 1)))}),

                                 ],
                         basis=[Perm((1, 2, 0, 3)),
                                Perm((1, 3, 0, 2)),
                                Perm((2, 3, 0, 1))]),
                    dict(tilings=[Tiling({Cell(0, 0): PermSet.avoiding(Perm((2, 1, 0))),
                                          Cell(1, 0): PermSet.avoiding(Perm((1, 0)))}),
                                 ],
                         basis=[Perm((3, 2, 1, 0)),
                                Perm((2, 1, 0, 4, 3)),
                                Perm((3, 1, 0, 4, 2)),
                                Perm((4, 1, 0, 3, 2)),
                                Perm((3, 2, 0, 4, 1)),
                                Perm((4, 2, 0, 3, 1))]),
                    dict(tilings=[Tiling({Cell(0, 0): PermSet.avoiding(Perm((2, 0, 1))),
                                          Cell(1, 0): PermSet.avoiding(Perm((1, 0)))}),
                                 ],
                         basis=[Perm((3, 0, 2, 1)),
                                Perm((3, 1, 2, 0)),
                                Perm((2, 0, 1, 4, 3)),
                                Perm((3, 0, 1, 4, 2))]),
                ],
                ids=[
                    "Av(120)",
                    "Av(40123)",
                    "Av(10|10)",
                    "Av(01|10)",
                    "Atkinson (1999): Union",
                    "Stankova (1994); Atkinson (1999): Skew merged perms",
                    "Murphy (2003): Av(021, 3201)",
                    "Brignall, Sliacan: Av(120|01)",
                    "Brignall, Sliacan: Av(210|10)",
                    "Brignall, Sliacan: Av(201|10)",
                ]
)
def perm_class_and_tilings(request):
    tilings = request.param["tilings"]
    perm_class = PermSet.avoiding(request.param["basis"])
    return perm_class, tilings


#
# Tests
#


def test_tuple_cell_input(random_tiling_dict):
    """Test that cells can be input as tuples."""
    tiling = Tiling(random_tiling_dict)
    for cell, _ in tiling:
        assert isinstance(cell, Cell)


def test_cell_cell_input(random_tiling_dict):
    """Test that cells can be input as cells."""
    tiling = Tiling({Cell(*cell): block
                     for cell, block
                     in random_tiling_dict.items()})
    for cell, _ in tiling:
        assert isinstance(cell, Cell)


def test_tiling_cleanup(random_tiling_dict):
    """Tests whether the cells of a Tiling are properly reduced."""
    i_list = sorted(set(cell[0] for cell in random_tiling_dict))
    j_list = sorted(set(cell[1] for cell in random_tiling_dict))
    i_map = {}
    for i_value in i_list:
        i_map[i_value] = len(i_map)
    j_map = {}
    for j_value in j_list:
        j_map[j_value] = len(j_map)
    cleaned_tiling_dict = {Cell(i_map[i_value], j_map[j_value]): block
                           for (i_value, j_value), block
                           in random_tiling_dict.items()}
    assert cleaned_tiling_dict == dict(Tiling(random_tiling_dict))


def test_dimensions(random_tiling_dict):
    """Tests whether the dimensions attribute works."""
    i_total = len(set(cell[0] for cell in random_tiling_dict))
    j_total = len(set(cell[1] for cell in random_tiling_dict))
    if i_total == 0:
        i_total = 1
    if j_total == 0:
        j_total = 1
    tiling = Tiling(random_tiling_dict)
    assert isinstance(tiling.dimensions, Cell)
    assert i_total == tiling.dimensions.i
    assert (i_total, j_total) == tiling.dimensions
    assert Cell(i_total, j_total) == tiling.dimensions
    if i_total != j_total:
        assert (j_total, i_total) != tiling.dimensions
        assert Cell(j_total, i_total) != tiling.dimensions


def test_area(random_tiling_dict):
    """Tests whether the area attribute works."""
    tiling = Tiling(random_tiling_dict)
    assert tiling.area == tiling.dimensions.i*tiling.dimensions.j


def test_hash(random_tiling_dict):
    """Test whether the hash is correctly calculated."""
    tiling = Tiling(random_tiling_dict)
    hash_sum = 0
    for item in tiling:
        hash_sum += hash(item)
    assert hash(tiling) == hash(hash_sum)


def test_perm_generation(perm_class_and_tilings):
    """Test that the perm generation code generates the correct perms."""
    perm_class, tilings = perm_class_and_tilings
    for length in range(10):
        from_tiling = set()
        for tiling in tilings:
            from_tiling.update(tiling.perms_of_length(length))
        from_perm_class = set(perm_class.of_length(length))
        assert from_tiling == from_perm_class

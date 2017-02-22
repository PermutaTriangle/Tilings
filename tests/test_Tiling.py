import pytest

from permuta import Perm
from permuta import PermSet

from grids import Cell
from grids import Block
from grids import Tiling


@pytest.fixture(scope="module",
                params=[
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


def test_perm_generation(perm_class_and_tilings):
    perm_class, tilings = perm_class_and_tilings
    for length in range(10):
        from_tiling = set()
        for tiling in tilings:
            from_tiling.update(tiling.perms_of_length(length))
        from_perm_class = set(perm_class.of_length(length))
        assert from_tiling == from_perm_class

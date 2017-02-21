import pytest

from permuta import Perm
from permuta import PermSet

from grids import Cell
from grids import Block
from grids import Tiling


#
# Fixtures
#


@pytest.fixture(scope="module")
def skew_merged_tiling():
    """The tiling corresponding to Av(Perm((2, 3, 0, 1)), Perm((1, 0, 3, 2)))."""
    # TODO: Find and credit those smart people that originally proved this
    return Tiling({Cell(0, 0): Block.increasing,
                   Cell(0, 1): Block.decreasing,
                   Cell(1, 0): Block.decreasing,
                   Cell(1, 1): Block.increasing})


@pytest.fixture(scope="module")
def skew_merged_perm_class():
    return PermSet.avoiding([Perm((2, 3, 0, 1)), Perm((1, 0, 3, 2))])


#
# Fixtures (from "Juxtaposing ..." paper of Brignall and Sliacan)
#


# TODO: I can do these parametrized as well?

#A = 231|12 = 2314, 2413, 3412


@pytest.fixture(scope="module")
def juxtaposed_A_tiling():
    return Tiling({Cell(0, 0): PermSet.avoiding(Perm((1, 2, 0))),
                   Cell(1, 0): PermSet.avoiding(Perm((0, 1)))})


@pytest.fixture(scope="module")
def juxtaposed_A_perm_class():
    return PermSet.avoiding([Perm((1, 2, 0, 3)),
                             Perm((1, 3, 0, 2)),
                             Perm((2, 3, 0, 1))])


#B = 321|21 = 4321, 32154, 42153, 52143, 43152, 53142


@pytest.fixture(scope="module")
def juxtaposed_B_tiling():
    return Tiling({Cell(0, 0): PermSet.avoiding(Perm((2, 1, 0))),
                   Cell(1, 0): PermSet.avoiding(Perm((1, 0)))})


@pytest.fixture(scope="module")
def juxtaposed_B_perm_class():
    return PermSet.avoiding([Perm((3, 2, 1, 0)),
                             Perm((2, 1, 0, 4, 3)),
                             Perm((3, 1, 0, 4, 2)),
                             Perm((4, 1, 0, 3, 2)),
                             Perm((3, 2, 0, 4, 1)),
                             Perm((4, 2, 0, 3, 1))])


#C = 312|21 = 4132, 4231, 31254, 41253


@pytest.fixture(scope="module")
def juxtaposed_C_tiling():
    return Tiling({Cell(0, 0): PermSet.avoiding(Perm((2, 0, 1))),
                   Cell(1, 0): PermSet.avoiding(Perm((1, 0)))})


@pytest.fixture(scope="module")
def juxtaposed_C_perm_class():
    return PermSet.avoiding([Perm((3, 0, 2, 1)),
                             Perm((3, 1, 2, 0)),
                             Perm((2, 0, 1, 4, 3)),
                             Perm((3, 0, 1, 4, 2))])


#
# Tests for the perm generating code
#


pgtd = [  # perm_generating_test_data
    [skew_merged_perm_class, skew_merged_tiling, "skew merged generating code"],
    [juxtaposed_A_perm_class, juxtaposed_A_tiling, "juxtaposed A generating code"],
    [juxtaposed_B_perm_class, juxtaposed_B_tiling, "juxtaposed B generating code"],
    [juxtaposed_C_perm_class, juxtaposed_C_tiling, "juxtaposed C generating code"]
]
pgtd_grouped = list(zip(*pgtd))
pgtd_args = list(zip(*pgtd_grouped[:-1]))
pgtd_id = pgtd_grouped[-1]


@pytest.mark.parametrize("perm_class, tiling", pgtd_args, ids=pgtd_id)
def test_perm_generation(perm_class, tiling):
    # TODO: Not call the fixtures... why do I need this?
    perm_class = perm_class()
    tiling = tiling()
    for length in range(10):
        from_tiling = set(tiling.perms_of_length(length))
        from_perm_class = set(perm_class.of_length(length))
        assert from_tiling == from_perm_class

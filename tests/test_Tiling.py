import json
import pytest

from permuta import Perm
from permuta import PermSet

from grids import Cell
from grids import Block
from grids import Tiling


#
# Test Cell class
#


def test_cell_to_json():
    """This is how we will be dumping the cells."""
    assert json.dumps(Cell(3, 5)) == "[3, 5]"


def test_json_to_cell():
    """This is how we will be loading the cells."""
    assert Cell(3, 5) == Cell(*json.loads("[3, 5]"))


#
# Test Tiling class
#


@pytest.fixture(scope="module")
def skew_merged_tiling():
    """The tiling corresponding to Av(Perm((2, 3, 0, 1)), Perm((1, 0, 3, 2)))."""
    return Tiling({Cell(0, 0): Block.increasing,
                   Cell(0, 1): Block.decreasing,
                   Cell(1, 0): Block.decreasing,
                   Cell(1, 1): Block.increasing})


@pytest.fixture(scope="module")
def skew_merged_perm_class():
    return PermSet.avoiding([Perm((2, 3, 0, 1)), Perm((1, 0, 3, 2))])


def test_skew_merged_tiling(skew_merged_perm_class, skew_merged_tiling):
    """Test whether the skew merged tiling works properly.

    This has been proven by TODO
    """  # TODO: Find and credit those smart people that originally proved this
    for length in range(10):
        from_tiling = set(skew_merged_tiling.perms_of_length(length))
        from_perm_class = set(skew_merged_perm_class.of_length(length))
        assert from_tiling == from_perm_class

import json
import pytest

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

import json

from grids import Cell


def test_cell_to_json():
    """This is how we will be dumping the cells."""
    assert json.dumps(Cell(3, 5)) == "[3, 5]"


def test_json_to_cell():
    """This is how we will be loading the cells."""
    assert Cell(3, 5) == Cell(*json.loads("[3, 5]"))

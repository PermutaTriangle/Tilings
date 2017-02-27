import pytest
from grids import recurrence
from bson import *


def test_find_recurrence():
    inp = [
            {
                "_id": ObjectId("5882153c7e98af0c473a874e"),
                "avoid": "o",
                "tile": [[{"point": [0, 0], "val": "o"}]],
                "examples": {"1": ["1"]},
                "recurrence": {"0": "0", "1": "1", "n": "0"},
                "genf": "F(x) = x",
                "solved_genf": "F(x) = x",
                "coeffs": [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            },
            {
                "_id": ObjectId("5882153c7e98af0c473a874e"),
                "avoid": "1",
                "tile": [[]],
                "examples": {"0": [""]},
                "recurrence": {"0": "1", "n": "0"},
                "genf": "F(x) = 1",
                "solved_genf": "F(x) = 1",
                "coeffs": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            },
            {
                "_id": ObjectId("5882153c7e98af0c473a874e"),
                "avoid": "21",
                "tile": [
                            [

                            ],
                            [
                                {"point": [0, 1], "val": "o"},
                                {"point": [1, 0], "val": "X"}
                            ]
                        ],
                "examples": {"1": ["1"]},
                "recurrence": {"0": "1", "n": "1"},
                "genf": "F(x) = 1 + x*F(x)",
                "solved_genf": "F(x) = x/(1 - x)",
                "coeffs": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            }
        ]

    input_keys = ["_id", "avoid", "tile"]
    output_keys = ["_id", "avoid", "tile", "recurrence"]

    for tiling_obj in inp:
        inp_obj = dict([(key, tiling_obj[key]) for key in input_keys])
        outp_obj = dict([(key, tiling_obj[key]) for key in output_keys])
        assert recurrence.find_recurrence(inp_obj) == outp_obj
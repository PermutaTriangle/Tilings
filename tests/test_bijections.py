import json
from pathlib import Path

from comb_spec_searcher import CombinatorialSpecification

data = Path(__file__).parent.joinpath("resources", "specs")


def test_bijections():
    for char in "abce":
        spec = CombinatorialSpecification.from_dict(
            json.loads(data.joinpath(f"{char}1.json").read_text())
        )
        other = CombinatorialSpecification.from_dict(
            json.loads(data.joinpath(f"{char}2.json").read_text())
        )
        bijection = spec.get_bijection_to(other)
        assert all(
            {bijection.map(gp) for gp in spec.generate_objects_of_size(i)}
            == set(other.generate_objects_of_size(i))
            for i in range(10)
        )

import pytest

from comb_spec_searcher import CombinatorialSpecification
from tilings.tilescope import ParityScope, TileScopePack

point_placements = TileScopePack.point_placements()


@pytest.mark.timeout(20)
def test_132():
    searcher = ParityScope("132", point_placements, max_assumptions=100)
    spec = searcher.auto_search(smallest=True)
    assert isinstance(spec, CombinatorialSpecification)
    spec = spec.expand_verified()
    for i in range(10):
        actual = set(spec.root.objects_of_size(i))
        assert actual == set(spec.generate_objects_of_size(i))
        assert spec.random_sample_object_of_size(i) in actual
    assert [
        1,
        1,
        1,
        2,
        3,
        7,
        12,
        30,
        55,
        143,
        273,
        728,
    ] == [spec.count_objects_of_size(i) for i in range(12)]

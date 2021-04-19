from comb_spec_searcher.bijection import ParallelSpecFinder
from permuta.permutils.statistics import PermutationStatistic


def test_something_only_on_dev():
    assert ParallelSpecFinder._INVALID == -1
    assert PermutationStatistic.get_by_index(2).name == "Major index"

import pytest
import random

from permuta import *
from grids import PositiveClass


@pytest.fixture(scope="module",
                params=[PermSet.avoiding(Perm.random(random.randint(2, 7)))
                        for _ in range(16)])
def random_class(request):
    """Random av class."""
    return request.param


def test_av_empty():
    perm_class = Av(Perm())
    with pytest.raises(TypeError):
        positive_class = PositiveClass(perm_class)


def test_random_class(random_class):
    positive_class = PositiveClass(random_class)
    assert list(random_class.of_length(0)) == [Perm()]
    assert list(positive_class.of_length(0)) == []
    for length in range(1, 9):
        assert set(positive_class.of_length(length)) == set(random_class.of_length(length))

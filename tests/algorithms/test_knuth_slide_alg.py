import random
from collections import defaultdict
from itertools import combinations, permutations

import pytest

from permuta import Perm
from tilings.algorithms.knuth_slide import (
    evacuation,
    is_knuth_closed,
    is_shape_closed,
    knuth_slide_word,
    rsk,
    rsk_inverse,
)


def shape(word):
    return tuple(len(row) for row in rsk(word)[0])


def perms(n):
    return (list(p) for p in permutations(range(n)))


@pytest.mark.parametrize("n", range(8))
def test_rsk_and_its_inverse(n):
    for perm in perms(n):
        p_tab, q_tab = rsk(perm)
        assert [len(row) for row in p_tab] == [len(row) for row in q_tab]
        assert rsk_inverse(p_tab, q_tab) == perm


def test_rsk_of_words_with_gaps():
    word = [7, 2, 9, 4]
    p_tab, q_tab = rsk(word)
    assert p_tab == [[2, 4], [7, 9]]
    assert q_tab == [[1, 3], [2, 4]]
    assert rsk_inverse(p_tab, q_tab) == word


@pytest.mark.parametrize("n", range(8))
def test_evacuation_is_a_shape_preserving_involution(n):
    for perm in perms(n):
        q_tab = rsk(perm)[1]
        evac = evacuation(q_tab)
        assert [len(row) for row in evac] == [len(row) for row in q_tab]
        assert evacuation(evac) == q_tab


@pytest.mark.parametrize("n", range(8))
def test_evacuation_records_the_reverse_complement(n):
    """Schutzenberger: Q(w^#) = evac(Q(w)) for the reverse-complement w^#."""
    for perm in perms(n):
        reverse_complement = [n - 1 - v for v in reversed(perm)]
        assert rsk(reverse_complement)[1] == evacuation(rsk(perm)[1])


@pytest.mark.parametrize("n", range(8))
def test_the_slide_of_a_word(n):
    """It keeps the insertion tableau, gives every factor the shape of the mirrored
    factor of the word, and is an involution."""
    for perm in perms(n):
        image = knuth_slide_word(perm)
        assert rsk(image)[0] == rsk(perm)[0]
        assert knuth_slide_word(image) == perm
        for i in range(n):
            for j in range(i, n):
                assert shape(image[n - 1 - j : n - i]) == shape(perm[i : j + 1])


def test_the_slide_keeps_the_knuth_class_on_every_window_of_values():
    for perm in perms(6):
        image = knuth_slide_word(perm)
        for low in range(6):
            for high in range(low, 6):
                window = [v for v in perm if low <= v <= high]
                image_window = [v for v in image if low <= v <= high]
                assert rsk(window)[0] == rsk(image_window)[0]


def brute_force_knuth_closed(patts, length):
    for n in range(length + 1):
        classes = defaultdict(list)
        for perm in permutations(range(n)):
            classes[tuple(map(tuple, rsk(perm)[0]))].append(Perm(perm))
        for knuth_class in classes.values():
            if len({perm.avoids(*patts) for perm in knuth_class}) > 1:
                return False
    return True


def test_knuth_closure_against_brute_force():
    """Any failure of closure shows on permutations at most one entry longer than
    the longest pattern, so the brute force to that length decides it."""
    s3 = [Perm(p) for p in permutations(range(3))]
    s4 = [Perm(p) for p in permutations(range(4))]
    rng = random.Random(2026)
    bases = [list(b) for size in range(1, 7) for b in combinations(s3, size)]
    bases += [rng.sample(s4, rng.randint(1, 6)) for _ in range(40)]
    bases += [rng.sample(s3, 1) + rng.sample(s4, rng.randint(1, 3)) for _ in range(20)]
    for basis in bases:
        length = max(len(p) for p in basis) + 1
        assert is_knuth_closed(frozenset(basis)) == brute_force_knuth_closed(
            basis, length
        ), basis


def test_shape_closure():
    def basis(*patts):
        return frozenset(Perm.to_standard(p) for p in patts)

    for n in range(1, 6):
        assert is_shape_closed(frozenset([Perm(range(n))]))
        assert is_shape_closed(frozenset([Perm(range(n - 1, -1, -1))]))
    shape_31 = frozenset(
        Perm(p) for p in permutations(range(4)) if shape(list(p)) == (3, 1)
    )
    assert len(shape_31) == 9 and is_shape_closed(shape_31)
    # Henning's stable Knuth class: Knuth-closed, but not determined by the shape
    k1 = basis("1243", "1423", "4123")
    assert is_knuth_closed(k1) and not is_shape_closed(k1)
    assert not is_knuth_closed(basis("132"))
    assert is_knuth_closed(basis("132", "312"))
    assert not is_shape_closed(basis("132", "312"))
    assert is_knuth_closed(frozenset()) and is_shape_closed(frozenset())

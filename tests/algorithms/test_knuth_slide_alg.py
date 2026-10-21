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


def perms(size):
    return (list(perm) for perm in permutations(range(size)))


@pytest.mark.parametrize("size", range(8))
def test_rsk_and_its_inverse(size):
    for perm in perms(size):
        insertion_tableau, recording_tableau = rsk(perm)
        assert [len(row) for row in insertion_tableau] == [
            len(row) for row in recording_tableau
        ]
        assert rsk_inverse(insertion_tableau, recording_tableau) == perm


def test_rsk_of_words_with_gaps():
    word = [7, 2, 9, 4]
    insertion_tableau, recording_tableau = rsk(word)
    assert insertion_tableau == [[2, 4], [7, 9]]
    assert recording_tableau == [[1, 3], [2, 4]]
    assert rsk_inverse(insertion_tableau, recording_tableau) == word


@pytest.mark.parametrize("size", range(8))
def test_evacuation_is_a_shape_preserving_involution(size):
    for perm in perms(size):
        recording_tableau = rsk(perm)[1]
        evacuated = evacuation(recording_tableau)
        assert [len(row) for row in evacuated] == [
            len(row) for row in recording_tableau
        ]
        assert evacuation(evacuated) == recording_tableau


@pytest.mark.parametrize("size", range(8))
def test_evacuation_records_the_reverse_complement(size):
    """Schutzenberger: Q(w^#) = evac(Q(w)) for the reverse-complement w^#."""
    for perm in perms(size):
        reverse_complement = [size - 1 - value for value in reversed(perm)]
        assert rsk(reverse_complement)[1] == evacuation(rsk(perm)[1])


@pytest.mark.parametrize("size", range(8))
def test_the_slide_of_a_word(size):
    """It keeps the insertion tableau, gives every factor the shape of the mirrored
    factor of the word, and is an involution."""
    for perm in perms(size):
        image = knuth_slide_word(perm)
        assert rsk(image)[0] == rsk(perm)[0]
        assert knuth_slide_word(image) == perm
        for i in range(size):
            for j in range(i, size):
                assert shape(image[size - 1 - j : size - i]) == shape(perm[i : j + 1])


def test_the_slide_keeps_the_knuth_class_on_every_window_of_values():
    for perm in perms(6):
        image = knuth_slide_word(perm)
        for low in range(6):
            for high in range(low, 6):
                window = [value for value in perm if low <= value <= high]
                image_window = [value for value in image if low <= value <= high]
                assert rsk(window)[0] == rsk(image_window)[0]


def brute_force_knuth_closed(patterns, length):
    for size in range(length + 1):
        classes = defaultdict(list)
        for perm in permutations(range(size)):
            classes[tuple(map(tuple, rsk(perm)[0]))].append(Perm(perm))
        for knuth_class in classes.values():
            if len({perm.avoids(*patterns) for perm in knuth_class}) > 1:
                return False
    return True


def test_knuth_closure_against_brute_force():
    """Any failure of closure shows on permutations at most one entry longer than
    the longest pattern, so the brute force to that length decides it."""
    perms_of_length_3 = [Perm(perm) for perm in permutations(range(3))]
    perms_of_length_4 = [Perm(perm) for perm in permutations(range(4))]
    generator = random.Random(2026)
    bases = [
        list(chosen)
        for size in range(1, 7)
        for chosen in combinations(perms_of_length_3, size)
    ]
    bases += [
        generator.sample(perms_of_length_4, generator.randint(1, 6)) for _ in range(40)
    ]
    bases += [
        generator.sample(perms_of_length_3, 1)
        + generator.sample(perms_of_length_4, generator.randint(1, 3))
        for _ in range(20)
    ]
    for basis in bases:
        length = max(len(pattern) for pattern in basis) + 1
        assert is_knuth_closed(frozenset(basis)) == brute_force_knuth_closed(
            basis, length
        ), basis


def test_shape_closure():
    def basis(*patterns):
        return frozenset(Perm.to_standard(pattern) for pattern in patterns)

    for size in range(1, 6):
        assert is_shape_closed(frozenset([Perm(range(size))]))
        assert is_shape_closed(frozenset([Perm(range(size - 1, -1, -1))]))
    shape_31 = frozenset(
        Perm(perm) for perm in permutations(range(4)) if shape(list(perm)) == (3, 1)
    )
    assert len(shape_31) == 9 and is_shape_closed(shape_31)
    # Henning's stable Knuth class: Knuth-closed, but not determined by the shape
    stable_knuth_class = basis("1243", "1423", "4123")
    assert is_knuth_closed(stable_knuth_class) and not is_shape_closed(
        stable_knuth_class
    )
    assert not is_knuth_closed(basis("132"))
    assert is_knuth_closed(basis("132", "312"))
    assert not is_shape_closed(basis("132", "312"))
    assert is_knuth_closed(frozenset()) and is_shape_closed(frozenset())

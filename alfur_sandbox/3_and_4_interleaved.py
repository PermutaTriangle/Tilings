from permuta import *
from permuta.misc.symmetry import *
from collections import defaultdict


def all_sets_of_perms_of_set(perms):
    all_sets = []
    all_perms = list(perms)
    for i in range(2**len(all_perms)):
        temp_set = []
        my_count = 0
        while i > 0:
            if i % 2 == 1:
                temp_set.append(all_perms[my_count])
            my_count += 1
            i //= 2
        all_sets.append(tuple(temp_set))
    assert len(all_sets) == 2**len(all_perms)
    return sorted(set(all_sets))


def perms_not_covered_by(perms_to_cover, coverers):
    covered = set()
    for coverer in coverers:
        for perm in perms_to_cover:
            if perm.contains(coverer):
                covered.add(perm)
    return sorted(set(perms_to_cover).difference(covered))


def len_3_and_4_interleaved():
    output_set = defaultdict(set)
    len_3 = all_sets_of_perms_of_set(list(PermSet(3)))
    len_3 = sorted(set([lex_min(x) for x in len_3]))
    len_3.remove(())
    len_4 = list(PermSet(4))

    for perms_3 in len_3:
        temp_len_4 = perms_not_covered_by(len_4, perms_3)
        for perms_4 in all_sets_of_perms_of_set(temp_len_4):
            if perms_4 == ():
                continue
            output_set[perms_3].add((*perms_3, *perms_4))
    return output_set



if __name__ == "__main__":
    print((all_sets_of_perms_of_set([Perm((1, 2, 0)), Perm((0, 1, 2)), Perm(())])))
    print(perms_not_covered_by([Perm((1, 2, 0)), Perm((0, 1, 2))], [Perm((1, 0))]))
    #s = len_3_and_4_interleaved()
    #print(len(s))
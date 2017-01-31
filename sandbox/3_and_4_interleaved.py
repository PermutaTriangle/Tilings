from permuta import *
from permuta.misc.symmetry import *
from collections import defaultdict
from itertools import chain, combinations


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def perms_not_covered_by(perms_to_cover, coverers):
    covered = set()
    for coverer in coverers:
        for perm in perms_to_cover:
            if perm.contains(coverer):
                covered.add(perm)
    return sorted(set(perms_to_cover).difference(covered))


def len_3_and_4_interleaved():
    output_set = defaultdict(set)
    len_3 = powerset(PermSet(3))
    len_3 = sorted(set([lex_min(x) for x in len_3]))
    len_3.remove(())
    len_4 = PermSet(4)

    for perms_3 in len_3:
        temp_len_4 = perms_not_covered_by(len_4, perms_3)
        for perms_4 in powerset(temp_len_4):
            if perms_4 == ():
                continue
            output_set[perms_3].add((*perms_3, *perms_4))
    return output_set



if __name__ == "__main__":
    print((powerset([Perm((1, 2, 0)), Perm((0, 1, 2)), Perm(())])))
    print(perms_not_covered_by([Perm((1, 2, 0)), Perm((0, 1, 2))], [Perm((1, 0))]))
    s = len_3_and_4_interleaved()
    print(len(s))
    my_count = 0
    print("This may take a while...")
    for x in s:
        my_count += len(set([lex_min(i) for i in s[x]]))
        print("...")
    print("Total count: ", my_count)
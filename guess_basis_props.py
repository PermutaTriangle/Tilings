from math import factorial
from random import shuffle
import random
from tilings import *
from permuta import Perm, Av, Basis
from permuta.permutils import (
    is_insertion_encodable_maximum,
    is_insertion_encodable_rightmost,
    all_symmetry_sets,
    reverse_set,
    is_polynomial,
)

from itertools import chain, combinations


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def profiles(r, c):
    # r rows, c columns
    if r == 0 or c == 0:
        assert 0
    else:
        all_cells = set((i, j) for i in range(r) for j in range(c))
        for inc in powerset(all_cells):
            inc_obs = [GriddedPerm((0, 1), ((i, j), (i, j))) for (i, j) in inc]
            for dec in powerset(all_cells - set(inc)):
                all_obs = list(inc_obs)
                all_obs.extend(
                    [GriddedPerm((1, 0), ((i, j), (i, j))) for (i, j) in dec]
                )
                yield Tiling(obstructions=all_obs)


# # added more obstruction types
# def profiles(r, c):
#     # r rows, c columns
#     if r == 0 or c == 0:
#         assert 0
#     else:
#         all_cells = set((i, j) for i in range(r) for j in range(c))
#         for inc in powerset(all_cells):
#             inc_obs = [GriddedPerm((0, 1), ((i, j), (i, j))) for (i, j) in inc]
#             all_obs = list(inc_obs)

#             for dec in powerset(all_cells - set(inc)):
#                 dec_obs = [GriddedPerm((1, 0), ((i, j), (i, j))) for (i, j) in dec]
#                 all_obs.extend(dec_obs)
#                 for rest in powerset((all_cells - set(inc)) - set(dec)):
#                     all_obs.extend(
#                         [
#                             GriddedPerm((2, 1, 0), ((i, j), (i, j), (i, j)))
#                             for (i, j) in rest
#                         ]
#                     )
#                     all_obs.extend(
#                         [
#                             GriddedPerm((1, 2, 0), ((i, j), (i, j), (i, j)))
#                             for (i, j) in rest
#                         ]
#                     )
#                     all_obs.extend(
#                         [
#                             GriddedPerm((2, 0, 1), ((i, j), (i, j), (i, j)))
#                             for (i, j) in rest
#                         ]
#                     )
#                     yield Tiling(obstructions=all_obs)


def p_in_P(p, P):

    if p.dimensions[0] > P.dimensions[0]:
        return False
    if p.dimensions[1] > P.dimensions[1]:
        return False

    pac = p.active_cells
    Pac = P.active_cells

    if len(pac) > len(Pac):
        return False

    for kill in combinations(list(P.active_cells), len(Pac) - len(pac)):
        # print(p)
        # print(P)
        # print(P.active_cells)
        # print("kill: ", kill)
        # print(P.add_obstructions(GriddedPerm((0,), (c,)) for c in kill))
        if p == P.add_obstructions(GriddedPerm((0,), (c,)) for c in kill):
            return True
    return False


# for p in set(profiles(2, 2)):
#     print(p)

profs = list(profiles(2, 2))
N = 4

D = {}
for p in profs:
    D[p] = set(gp.patt for i in range(N + 1) for gp in p.objects_of_size(i))

# The bases listed as insertion encodable from Wikipedia
bases = [
    (Perm((3, 2, 1, 0)), Perm((0, 1, 2, 3))),
    (Perm((3, 2, 0, 1)), Perm((0, 1, 2, 3))),
    (Perm((3, 2, 1, 0)), Perm((2, 0, 1, 3))),
    (Perm((3, 2, 0, 1)), Perm((1, 0, 2, 3))),
    (Perm((3, 2, 1, 0)), Perm((0, 2, 1, 3))),
    (Perm((3, 1, 0, 2)), Perm((1, 2, 3, 0))),
    (Perm((3, 1, 0, 2)), Perm((0, 1, 3, 2))),
    (Perm((3, 2, 1, 0)), Perm((2, 0, 3, 1))),
    (Perm((3, 1, 0, 2)), Perm((0, 2, 3, 1))),
    (Perm((3, 2, 0, 1)), Perm((1, 2, 3, 0))),
    (Perm((3, 2, 1, 0)), Perm((3, 0, 1, 2))),
    (Perm((3, 2, 1, 0)), Perm((2, 3, 0, 1))),
    (Perm((3, 0, 1, 2)), Perm((2, 1, 0, 3))),
]

# bases = ["0231_0321_2301", "0231_0321_2031", "0213_0231_3021", "0213_0231_0321"]
# bases = [
#     tuple(
#         Perm(tuple(int(c) for c in b.split("_")[i])) for i in range(len(b.split("_")))
#     )
#     for b in bases
# ]
# print(bases)

# The bases listed as having a finite enumeration scheme by Vatter
# bases = [
#     (Perm((0, 2, 3, 1)), Perm((1, 2, 3, 0))),
#     (Perm((0, 2, 3, 1)), Perm((0, 3, 2, 1))),
#     (Perm((2, 1, 3, 0)), Perm((2, 3, 1, 0))),
#     # (Perm((2, 1, 3, 0)), Perm((3, 2, 1, 0))),
#     (Perm((2, 3, 0, 1)), Perm((2, 3, 1, 0))),
#     # (Perm((2, 3, 1, 0)), Perm((3, 2, 1, 0))),
#     (Perm((2, 3, 1, 0)), Perm((3, 1, 2, 0))),
#     (Perm((0, 1, 2, 3)),),
#     # (
#     #     Perm((2, 1, 0)),
#     #     Perm((3, 5, 6, 0, 7, 1, 2, 4)),
#     #     Perm((3, 5, 6, 7, 0, 1, 2, 4)),
#     #     Perm((4, 5, 6, 0, 7, 1, 2, 3)),
#     #     Perm((4, 5, 6, 7, 0, 1, 2, 3)),
#     # ),  # 321, 46718235, 46781235, 56718234, 56781234
#     (Perm((1, 2, 0)),),
#     # (Perm((2, 1, 0)),),
# ]

# good_bases = []
# for b in bases:
#     good_bases.append(b)
#     good_bases.append(tuple(reverse_set(b)))

from kseparable import eventually_bounded_with_row_col_placements, placement_seqsN

# # Alternatively, read the good bases from a file
# with open("good_bases.txt", "r") as f:
#     good_bases = []
#     for line in f:
#         basis = line.strip().split("_")
#         basis = tuple(Perm(tuple(int(c) for c in b)) for b in basis)
#         good_bases.append(basis)

K = 6

# good_bases2_3x5s = []
# for j in range(2, 3):
#     for basis in combinations(Perm.of_length(5), j):
#         basis = tuple(sorted(basis))
#         new_basis = True
#         for gb in good_bases2_3x5s:
#             if set(gb).issubset(set(basis)):
#                 new_basis = False
#                 print("Skipping basis ", basis, " as it contains good basis ", gb)
#                 break
#         if not new_basis:
#             continue
#         print("Trying basis ", basis)
#         if is_insertion_encodable_maximum(basis):
#             good_bases2_3x5s.append(basis)
#         else:
#             print("Basis ", basis, " is not insertion encodable maximum")
#             basis = "_".join(str(b) for b in basis)
#             T = Tiling.from_string(basis)

#             T_is_k_sep_top = False
#             for k in range(1, K + 1):
#                 for seq in list(placement_seqsN(k)):  # + list(placement_seqsS(k)):
#                     if eventually_bounded_with_row_col_placements(T, seq):
#                         print(
#                             f"Basis: {basis} is bounded after {k} placements using {seq}!!!!!!!!!!!!!!!!!!!"
#                         )
#                         good_bases2_3x5s.append(basis)
#                         T_is_k_sep_top = True
#                         break
#                 if T_is_k_sep_top:
#                     break

# Write good_bases2_3x5s to a file in the format 0123_0321
# with open("good_bases2_3x5s.txt", "w") as f:
#     for b in good_bases2_3x5s:
#         textbasis = "_".join(str(p) for p in b)
#         f.write(textbasis + "\n")

# # Write more_good_bases to a file in the format 0123_0321
# with open("more_good_bases.txt", "w") as f:
#     for b in more_good_bases:
#         textbasis = "_".join(str(p) for p in b)
#         f.write(textbasis + "\n")

# final_good_bases = good_bases2_3x5s
# print("Number of good bases: ", len(good_bases))

# Filter out bases that are a superset of another basis in good_bases
# final_good_bases = []
# for b in good_bases:
#     is_minimal = True
#     for b2 in good_bases:
#         if b != b2 and set(b2).issubset(set(b)):
#             is_minimal = False
#             break
#     if is_minimal:
#         final_good_bases.append(b)

K = 7
good_bases = []
for j in range(3, 4):

    total = 0
    ins_enc = 0
    k_sep_top = 0
    rest = 0

    # number of ways to choose j permutations from S4
    grand_total = factorial(24) // (factorial(24 - j) * factorial(j))

    # shuffle the list of perms

    perms = list(Perm.of_length(4))
    random.seed(42)
    shuffle(perms)
    for basis4 in combinations(perms, j):
        total += 1
        # for q in Av(Basis(*basis4)).of_length(5):
        # basis = tuple(sorted(list(basis4) + [q]))
        basis = tuple(sorted(basis4))
        textbasis = "_".join(str(b) for b in basis)
        new_basis = True
        # for gb in good_bases:
        #     if set(gb).issubset(set(basis)):
        #         new_basis = False
        #         print("Skipping basis ", basis, " as it contains good basis ", gb)
        #         break
        # if not new_basis:
        #     continue
        print("Trying basis ", textbasis)
        if is_insertion_encodable_maximum(basis):
            ins_enc += 1
            print("The basis is insertion encodable maximum!")
            print()
            good_bases.append(basis)
        else:
            print("The basis is not insertion encodable maximum")
            print("Trying k-separable top...")
            T = Tiling.from_string(textbasis)

            T_is_k_sep_top = False
            for k in range(1, K + 1):
                for seq in list(placement_seqsN(k)):  # + list(placement_seqsS(k)):
                    if eventually_bounded_with_row_col_placements(T, seq):
                        print(
                            f"The basis is bounded after {k} placements using {seq}!!!!!!!!!!!!!!!!!!!"
                        )
                        k_sep_top += 1
                        # input("Press Enter to continue...")
                        good_bases.append(basis)
                        T_is_k_sep_top = True
                        break
                if T_is_k_sep_top:
                    break
            if not T_is_k_sep_top:
                rest += 1
                print("The basis is not k-separable top for k up to ", K)
                print()
        print("Totals so far: ")
        print(f"Total: {total} / {grand_total}")
        print(f"Insertion Encodable: {ins_enc}")
        print(f"K-Separable Top: {k_sep_top}")
        print(f"Rest: {rest}")

print("Number of minimal good bases: ", len(good_bases))
print("The size of the largest basis is: ", max(len(b) for b in good_bases))

# input()

# K-sep top but not insertion encodable maximum:
# 1302_1320_2031_2130
# 1302_2031_2130_3120
# 1320_2031_2130_3120
# 1032_1320_2031_2130
# 1320_2031_2130_3102
# Hypothesis: Up-up, down-down, (up-down or up-enough seqparations), (down-up or down-enough separations)
# 0213_0321_2031 checks out
# 0231_0321_2031 checks out
# 0213_0321_2301
# 0231_0321_2301
# 0231_0321_2013
# 0213_0231_0321
# 0213_2031_3201
# 0213_2031_3021
# 0231_2031_3201
# 0231_2031_3021
# 1023_1302_1320
# 1230_1302_1320
# 1203_1302_1320
# 1023_1302_3120
# 1230_1302_3120
# 1203_1302_3120 checks out
# 1023_1320_3120
# 1230_1320_3120
# 1203_1320_3120
# 1023_1032_1320
# 1023_1320_3102
# 1032_1230_1320
# 1230_1320_3102
# 1032_1203_1320
# 1203_1320_3102
# 0213_2301_3201
# 0213_2301_3021
# 0231_2301_3201
# 0231_2301_3021 5 placements
# 0231_2013_3201
# 0231_2013_3021
# 1023_1032_3120
# 1032_1230_3120
# 1032_1203_3120
# 0213_0231_3201
# 0213_0231_3021


# good_bases = []
# for b in bases:
#     for sb in all_symmetry_sets(b):
#         if is_insertion_encodable_maximum(sb):
#             good_bases.append(sb)

# good_bases = bases

# for b in bases:
#     B = Av(b)
#     print(B.is_insertion_encodable())
#     print(is_insertion_encodable_rightmost(B.basis))
#     print(is_insertion_encodable_maximum(B.basis))

# assert 0

# Write good_bases to a file in the format 0123_0321_01234
with open("good_bases3x4_K7.txt", "w") as f:
    for b in good_bases:
        textbasis = "_".join(str(p) for p in b)
        f.write(textbasis + "\n")


def guess_bases_props(good_bases, profdims=(2, 2)):
    profs = list(profiles(profdims[0], profdims[1]))
    N = max(len(patt) for patt in chain.from_iterable(good_bases))

    D = {}
    for p in profs:
        D[p] = set(gp.patt for i in range(N + 1) for gp in p.objects_of_size(i))

    E = {}
    for b in good_bases:
        # Progress bar

        basis_hits = []
        for p in profs:
            # print(D[p])
            if any(basis_elt in D[p] for basis_elt in b):
                basis_hits.append(p)
        E[b] = set(basis_hits)

    b = good_bases[0]
    comm = E[b]
    for i in range(len(good_bases)):
        if i == 0:
            pass
        else:
            comm = comm.intersection(E[good_bases[i]])

    minimal_comm = []
    for P in comm:
        P_minimal = True
        for p in comm:
            if p != P:
                if p_in_P(p, P):
                    P_minimal = False
                    break
        if P_minimal:
            minimal_comm.append(P)

    # for p in comm:
    #     print(p)

    for p in minimal_comm:
        print(p)

    print(len(minimal_comm))


# Guess the properties of the good bases
print("profdims = (2, 2)")
guess_bases_props(good_bases, profdims=(2, 2))

print("profdims = (2, 3)")
guess_bases_props(good_bases, profdims=(2, 3))

print("profdims = (3, 2)")
guess_bases_props(good_bases, profdims=(3, 2))

print("profdims = (3, 3)")
guess_bases_props(good_bases, profdims=(3, 3))


"""
profdims = (2, 2)
+-+
|/|
+-+
|/|
+-+
/: Av(10)

+-+-+
|/| |
+-+-+
|\|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/| |
+-+-+
|\|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
|/|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
|\|\|
+-+-+
/: Av(10)
\: Av(01)

===============================

+-+
|\|
+-+
|\|
+-+
\: Av(01)

+-+-+
|\| |
+-+-+
|/|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|/|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|\|/|
+-+-+
/: Av(10)
\: Av(01)

===============================

+-+-+
|/|/|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|\|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|/|
+-+-+
| |\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|\|
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\|\|
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\|\|
+-+-+
|/| |
+-+-+
/: Av(10)
\: Av(01)


"""


# From 3x4 K=7
"""
profdims = (2, 2)
+-+
|/|
+-+
|/|
+-+
/: Av(10)

+-+-+
|/| |
+-+-+
|\|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|/|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
|/|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|/|
+-+-+
| |\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|/|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|\|
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+
|\|
+-+
|\|
+-+
\: Av(01)

+-+-+
|/| |
+-+-+
|\|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
|\|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|\|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|\|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\|\|
+-+-+
|/| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\|\|
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)
===============================
profdims = (2, 3)
+-+
|/|
+-+
|/|
+-+
/: Av(10)

+-+-+
|/| |
+-+-+
|\|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|/|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/| |
+-+-+
| |/|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/| |
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
|/|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|/|
+-+-+
| |\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|/|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
| |\|
+-+-+
|/| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|\|
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|/| |
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+
|\|
+-+
|\|
+-+
\: Av(01)

+-+-+
|/| |
+-+-+
|\|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
|\|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|\|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/| |
+-+-+
| |\|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|\|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
| |\|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\|\|
+-+-+
|/| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\|\|
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|\| |
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/| |
+-+-+
| |\|
+-+-+
/: Av(10)
\: Av(01)
-==============================
profdims = (3, 2)
+-+
|/|
+-+
|/|
+-+
/: Av(10)

+-+-+-+
|/|/|/|
+-+-+-+
/: Av(10)

+-+-+
|/| |
+-+-+
|\|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|/|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\|/|/|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
|/|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|/|
+-+-+
| |\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|/|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|\|
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/|/|\|
+-+-+-+
/: Av(10)
\: Av(01)

+-+
|\|
+-+
|\|
+-+
\: Av(01)

+-+-+
|/| |
+-+-+
|\|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
|\|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\|\|/|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|\|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|\|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\|\|
+-+-+
|/| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\|\|
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/|\|\|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\|\|\|
+-+-+-+
\: Av(01)

22

=========================================
profdims = (3, 3)
+-+
|/|
+-+
|/|
+-+
/: Av(10)

+-+-+-+
|/|/|/|
+-+-+-+
/: Av(10)

+-+-+
|/| |
+-+-+
|\|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|/|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/| |
+-+-+
| |/|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\|/|/|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
| |/|/|
+-+-+-+
|/| | |
+-+-+-+
|\| | |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
| |/|/|
+-+-+-+
|\| | |
+-+-+-+
|/| | |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/| | |
+-+-+-+
|\| | |
+-+-+-+
| |/|/|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/| |
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\| | |
+-+-+-+
| |/|/|
+-+-+-+
|/| | |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
|/|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|/|
+-+-+
| |\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/| |/|
+-+-+-+
| |/| |
+-+-+-+
| |\| |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|/|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
| |\|
+-+-+
|/| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|\|
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/| |/|
+-+-+-+
| |\| |
+-+-+-+
| |/| |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|/| |
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/|/|\|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
| | |/|
+-+-+-+
|/|/| |
+-+-+-+
| | |\|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/|/| |
+-+-+-+
| | |/|
+-+-+-+
| | |\|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/|/| |
+-+-+-+
| | |\|
+-+-+-+
| | |/|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
| | |\|
+-+-+-+
| | |/|
+-+-+-+
|/|/| |
+-+-+-+
/: Av(10)
\: Av(01)

+-+
|\|
+-+
|\|
+-+
\: Av(01)

+-+-+
|/| |
+-+-+
|\|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
|\|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\|\|/|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/|\|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|/| |
+-+-+
| |\|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|\|/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |/|
+-+-+
| |\|
+-+-+
|\| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/|\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\|\|
+-+-+
|/| |
+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\|\|
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+
| |\|
+-+-+
|\| |
+-+-+
| |/|
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
| |\| |
+-+-+-+
|\| |/|
+-+-+-+
|/| | |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/| | |
+-+-+-+
|\| | |
+-+-+-+
| |/|\|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
| |/| |
+-+-+-+
|\| |/|
+-+-+-+
| | |\|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+
|\| |
+-+-+
|/| |
+-+-+
| |\|
+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\| | |
+-+-+-+
| |/|\|
+-+-+-+
|/| | |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/|\|\|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
| | |\|
+-+-+-+
| | |/|
+-+-+-+
|/|\| |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/| |\|
+-+-+-+
| |/| |
+-+-+-+
| |\| |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
| | |/|
+-+-+-+
|/|\| |
+-+-+-+
| | |\|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/| |\|
+-+-+-+
| |\| |
+-+-+-+
| |/| |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\|\|\|
+-+-+-+
\: Av(01)

+-+-+-+
| | |\|
+-+-+-+
| | |/|
+-+-+-+
|\|\| |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
| |\|\|
+-+-+-+
|/| | |
+-+-+-+
|\| | |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|/| | |
+-+-+-+
|\| | |
+-+-+-+
| |\|\|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
| | |/|
+-+-+-+
|\|\| |
+-+-+-+
| | |\|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
| |\|\|
+-+-+-+
|\| | |
+-+-+-+
|/| | |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\| |\|
+-+-+-+
| |/| |
+-+-+-+
| |\| |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\| | |
+-+-+-+
| |\|\|
+-+-+-+
|/| | |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\| |\|
+-+-+-+
| |\| |
+-+-+-+
| |/| |
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\|\| |
+-+-+-+
| | |/|
+-+-+-+
| | |\|
+-+-+-+
/: Av(10)
\: Av(01)

+-+-+-+
|\|\| |
+-+-+-+
| | |\|
+-+-+-+
| | |/|
+-+-+-+
/: Av(10)
\: Av(01)

58
"""

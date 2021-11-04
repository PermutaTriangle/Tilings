# pylint: skip-file
from itertools import chain
from typing import Counter, Dict, Iterator, List, Optional

from tilings.algorithms import Factor
from tilings.algorithms.fusion import Fusion as GeneralFusion
from tilings.assumptions import TrackingAssumption
from tilings.griddedperm import GriddedPerm
from tilings.tiling import Tiling


def test_ass_map(tiling, original_tiling, verbose=False):
    if verbose:
        print("=" * 10)
        print("TESTING ASS MAP")
        print(tiling)
        print(original_tiling)
    for i in range(6):  # these counts should match!
        terms = tiling.get_terms(i)
        actual = len(list(original_tiling.remove_parameters().objects_of_size(i)))
        computed = sum(k[0] * v for k, v in terms.items())
        assert actual == computed, (i, actual, computed, terms, tiling, original_tiling)


tiling = Tiling.from_dict(
    {
        "class_module": "tilings.tiling",
        "comb_class": "Tiling",
        "obstructions": [
            {"patt": [0, 1], "pos": [[0, 0], [1, 0]]},
            {"patt": [0, 1], "pos": [[0, 0], [3, 0]]},
            {"patt": [0, 1], "pos": [[1, 0], [3, 0]]},
            {"patt": [0, 1], "pos": [[2, 0], [3, 0]]},
            {"patt": [0, 2, 1], "pos": [[0, 0], [0, 0], [0, 0]]},
            {"patt": [0, 2, 1], "pos": [[0, 0], [0, 0], [2, 0]]},
            {"patt": [0, 2, 1], "pos": [[0, 0], [2, 0], [2, 0]]},
            {"patt": [0, 2, 1], "pos": [[1, 0], [1, 0], [1, 0]]},
            {"patt": [0, 2, 1], "pos": [[1, 0], [1, 0], [2, 0]]},
            {"patt": [0, 2, 1], "pos": [[1, 0], [2, 0], [2, 0]]},
            {"patt": [0, 2, 1], "pos": [[2, 0], [2, 0], [2, 0]]},
            {"patt": [0, 2, 1], "pos": [[3, 0], [3, 0], [3, 0]]},
            {"patt": [0, 2, 1, 3], "pos": [[0, 0], [0, 0], [4, 0], [4, 0]]},
            {"patt": [0, 2, 1, 3], "pos": [[0, 0], [2, 0], [4, 0], [4, 0]]},
            {"patt": [0, 2, 1, 3], "pos": [[0, 0], [4, 0], [4, 0], [4, 0]]},
            {"patt": [0, 2, 1, 3], "pos": [[1, 0], [1, 0], [4, 0], [4, 0]]},
            {"patt": [0, 2, 1, 3], "pos": [[1, 0], [2, 0], [4, 0], [4, 0]]},
            {"patt": [0, 2, 1, 3], "pos": [[1, 0], [4, 0], [4, 0], [4, 0]]},
            {"patt": [0, 2, 1, 3], "pos": [[2, 0], [2, 0], [4, 0], [4, 0]]},
            {"patt": [0, 2, 1, 3], "pos": [[2, 0], [4, 0], [4, 0], [4, 0]]},
            {"patt": [0, 2, 1, 3], "pos": [[3, 0], [3, 0], [4, 0], [4, 0]]},
            {"patt": [0, 2, 1, 3], "pos": [[3, 0], [4, 0], [4, 0], [4, 0]]},
            {"patt": [0, 2, 1, 3], "pos": [[4, 0], [4, 0], [4, 0], [4, 0]]},
        ],
        "requirements": [],
        "assumptions": [],
    }
)
print(tiling)
gf = GeneralFusion(tiling, col_idx=0, tracked=True)
print(gf.fusable())
print(gf.fused_tiling())
test_ass_map(gf.fused_tiling(), tiling)

fusable = Tiling(
    [
        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
        GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
        GriddedPerm((0, 1), ((1, 0), (1, 0))),
        GriddedPerm((0, 1), ((1, 0), (2, 0))),
        GriddedPerm((0, 1), ((2, 0), (2, 0))),
    ]
)

gf = GeneralFusion(tiling=fusable, col_idx=1, tracked=True)

print(gf.fusable())
print(gf.fused_tiling())

test_ass_map(gf.fused_tiling(), fusable)

for i in range(5):
    terms = gf.fused_tiling().get_terms(i)
    print(i, terms)
    print("actual:", len(list(gf.tiling.objects_of_size(i))))
    print("computed:", sum(k[0] * v for k, v in terms.items()))

comp_fusable = Tiling(
    obstructions=(
        GriddedPerm((0, 1), ((0, 0), (0, 1))),
        GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 2))),
        GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (0, 2))),
        GriddedPerm((0, 2, 1), ((0, 0), (0, 2), (0, 0))),
        GriddedPerm((0, 2, 1), ((0, 1), (0, 2), (0, 1))),
        GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
        GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
        GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
        GriddedPerm((0, 3, 1, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
        GriddedPerm((0, 3, 1, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
        GriddedPerm((0, 3, 1, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
    ),
    requirements=(),
    parameters=(),
)  # 3 without parameter

gf = GeneralFusion(comp_fusable, row_idx=0, tracked=True)
fused_tiling = gf.fused_tiling()  # 2 with parameter

test_ass_map(fused_tiling, comp_fusable)

ass = fused_tiling.parameters[0]
print("===== component fusable tiling =====")
print(comp_fusable)
print("==== end ====")

print("===== the fused tiling =====")
print(fused_tiling)
print("==== end ====")
# for gp in sorted(fused_tiling.objects_of_size(3)):
#     print(gp)
#     for gp2 in sorted(fused_tiling.parameters[0].gridding_counter._griddings(3)[gp]):
#         print("\t", gp2)
# assert 0

for i in range(6):
    terms = fused_tiling.get_terms(i)
    print(i, terms)
    print("actual:", len(list(gf.tiling.objects_of_size(i))))
    print("computed:", sum(k[0] * v for k, v in terms.items()))

unfused_positive_tiling = comp_fusable.insert_cell((0, 2))

positive_fused_tiling = fused_tiling.insert_cell((0, 1))

test_ass_map(positive_fused_tiling, unfused_positive_tiling)

print("===== the positive tiling =====")
print(positive_fused_tiling)  # 5 with parameter?
print("==== end ====")

unfused_placed_tiling = unfused_positive_tiling.place_point_in_cell((0, 2), 0)

placed_fused_tiling = positive_fused_tiling.place_point_in_cell((0, 1), 0)

test_ass_map(placed_fused_tiling, unfused_placed_tiling, verbose=False)

print("===== the placed tiling =====")
print(placed_fused_tiling)  # 5.5, i.e. the one in the middle of the eqv path 5 -> 6
print("==== end ====")
separated_tiling = placed_fused_tiling.row_and_column_separation()
unfused_separated_tiling = Tiling(
    obstructions=(
        GriddedPerm((0, 1), ((0, 1), (0, 3))),
        GriddedPerm((0, 1), ((0, 1), (0, 4))),
        GriddedPerm((0, 1), ((0, 1), (2, 2))),
        GriddedPerm((0, 1), ((0, 3), (0, 4))),
        GriddedPerm((0, 1), ((1, 5), (1, 5))),
        GriddedPerm((0, 1), ((2, 0), (2, 2))),
        GriddedPerm((1, 0), ((1, 5), (1, 5))),
        GriddedPerm((0, 1, 2), ((0, 1), (0, 6), (0, 6))),
        GriddedPerm((0, 1, 2), ((0, 3), (0, 6), (0, 6))),
        GriddedPerm((0, 1, 2), ((0, 4), (0, 6), (0, 6))),
        GriddedPerm((0, 2, 1), ((0, 1), (0, 6), (0, 1))),
        GriddedPerm((0, 2, 1), ((0, 3), (0, 6), (0, 3))),
        GriddedPerm((0, 2, 1), ((0, 4), (0, 6), (0, 4))),
        GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
        GriddedPerm((0, 2, 3, 1), ((0, 3), (0, 3), (0, 3), (0, 3))),
        GriddedPerm((0, 2, 3, 1), ((0, 4), (0, 4), (0, 4), (0, 4))),
        GriddedPerm((0, 2, 3, 1), ((0, 6), (0, 6), (0, 6), (0, 6))),
        GriddedPerm((0, 2, 3, 1), ((2, 0), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((0, 2, 3, 1), ((2, 2), (2, 2), (2, 2), (2, 2))),
        GriddedPerm((0, 3, 1, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
        GriddedPerm((0, 3, 1, 2), ((0, 3), (0, 3), (0, 3), (0, 3))),
        GriddedPerm((0, 3, 1, 2), ((0, 4), (0, 4), (0, 4), (0, 4))),
        GriddedPerm((0, 3, 1, 2), ((0, 6), (0, 6), (0, 6), (0, 6))),
        GriddedPerm((0, 3, 1, 2), ((2, 0), (2, 0), (2, 0), (2, 0))),
        GriddedPerm((0, 3, 1, 2), ((2, 2), (2, 2), (2, 2), (2, 2))),
    ),
    requirements=((GriddedPerm((0,), ((1, 5),)),),),
    parameters=(),
)  # only separating rows, so can't use row_column_separation method

print(repr(unfused_separated_tiling))
print(separated_tiling)
test_ass_map(separated_tiling, unfused_separated_tiling, verbose=True)

# separated_assless_tiling = (
#     placed_fused_tiling.remove_parameters().row_and_column_separation()
# )
# print(separated_assless_tiling)
# separated_comp_fusable = Tiling(
#     [
#         GriddedPerm((0, 1), ((0, 1), (2, 2))),
#         GriddedPerm((0, 1), ((2, 0), (2, 2))),
#         GriddedPerm((0, 1), ((0, 1), (0, 3))),
#     ],
#     remove_empty_rows_and_cols=False,
# )
# print(separated_comp_fusable)
# separable_map = {
#     (0, 1): (0, 1),
#     (0, 3): (0, 1),
#     (1, 0): (1, 0),
#     (2, 2): (2, 0),
#     (2, 0): (2, 0),
# }

# separable_ass = TrackingAssumption(separated_comp_fusable, separable_map)
# unfused_separated_tiling = unfused_placed_tiling.row_and_column_separation()
# separated_tiling = separated_assless_tiling.add_parameter(separable_ass)
print("===== the separated tiling =====")
print(separated_tiling)  # 6, i.e. the one in the middle of the eqv path 5 -> 6
print("==== end ====")

# TODO: unfused tiling should not separate last column
# test_ass_map(separated_tiling, unfused_separated_tiling)

for i in range(6):  # these counts should match!
    print("====placed====")
    terms = placed_fused_tiling.get_terms(i)
    print(i, terms)
    print(
        "actual:",
        len(list(unfused_placed_tiling.objects_of_size(i))),
    )
    print("computed:", sum(k[0] * v for k, v in terms.items()))
    print("====positive====")
    terms = positive_fused_tiling.get_terms(i)
    print(i, terms)
    print(
        "actual:",
        len(list(unfused_positive_tiling.objects_of_size(i))),
    )
    print("computed:", sum(k[0] * v for k, v in terms.items()))
    print("====separated====")
    terms = separated_tiling.get_terms(i)
    print(i, terms)
    print(
        "actual:",
        len(list(unfused_separated_tiling.objects_of_size(i))),
    )
    print("computed:", sum(k[0] * v for k, v in terms.items()))
    print()

from tilings.strategies import FactorFactory

for t in FactorFactory()(separated_tiling):
    print(t(separated_tiling))

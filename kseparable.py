from tilings import *
from tilings import strategies
from tilings.tilescope import *
from tilings.algorithms import obstruction_transitivity, RowColSeparation
from tilings.strategies import (
    RowAndColumnPlacementFactory,
    FactorFactory,
    RowColumnSeparationStrategy,
)


from permuta.misc import DIR_NORTH, DIR_SOUTH, DIR_EAST, DIR_WEST
from permuta.permutils import (
    is_insertion_encodable_maximum,
    is_insertion_encodable_rightmost,
)

from itertools import chain, combinations
from permuta import Perm

# Import max_row_placements and min_row_placements from the file row_placements.py
from row_placements import (
    MinRowPlacementFactory,
    MaxRowPlacementFactory,
    LeftColPlacementFactory,
    RightColPlacementFactory,
    max_row_placements,
    min_row_placements,
)

import json

# Load all lex-min symmetry of non-insertion encodable bases with length 4 patterns
all_sizes = []
for size in range(1, 13):
    with open(f"bases_size_{size}.json", "r") as f:
        bases = json.load(f)
    all_sizes.extend(bases)
    print(f"Size {size}: {len(bases)}")
print(f"All bases loaded")


def placement_seqsN(k):
    # Generate all sequences of length k with entries in {1}, for placements in top row
    if k == 0:
        yield []
    else:
        yield [1] * k


def placement_seqsS(k):
    # Generate all sequences of length k with entries in {3}, for placements in bottom row
    if k == 0:
        yield []
    else:
        yield [3] * k


def placement_seqsNS(k):
    # Generate all sequences of length k with entries in {1,3}, for placements in top or bottom row
    # The sequences start with 1s and then end with 3s, because top and bottom row placements commute
    if k == 0:
        yield []
    else:
        # step backwards, to prioritize top placements (1s)
        for i in range(k, -1, -1):
            yield [1] * i + [3] * (k - i)


def placement_seqsNSWE(k):
    # Generate all sequences of length k with entries in {1,2,3,4}, for placements in top or bottom row, leftmost or rightmost column
    # The sequences start with 1s, continue with 3s (so we do rows first), then 2s, and then finally 4s.
    if k == 0:
        yield []
    else:
        # step backwards, to prioritize top placements (1s)
        for i in range(k, -1, -1):
            for j in range(k - i, -1, -1):
                for ell in range(k - i - j, -1, -1):
                    yield [1] * i + [3] * j + [2] * ell + [4] * (k - i - j - ell)


def delete_non_local_obstructions(tiling):
    """
    Delete all non-local obstructions from a tiling.
    Non-local obstructions are those that span more than one cell.

    Args:
        tiling: A Tiling object
        Returns: A new Tiling object with non-local obstructions removed
    """
    new_obs = [obs for obs in tiling.obstructions if obs.is_localized()]
    return Tiling(new_obs)


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


# Things to try:
# 1. This function can be applied to a general tiling, and could be used as a verification strategy in TileScope
# .   It would still be best if we wouldn't have to run all the placements, just have a test on the tiling to see if
#    it would satisfy the conditions after placements. A middle ground would be be to just run monotone placements
# 2. Can we make this function mimic precisely the insertion encoding check, by just checking for cells becoming empty?
#    Then it would be interesting to check a top and bottom placement version to see what the conditions for success are
# 3. It would be really helpful if (independent of the placement sequence) we could just use monotone placements
#


def eventually_bounded_with_row_col_placements(
    tiling, seq=[1], fusion=False, verbose=False
):
    """
    Check if a 1x1 tiling is separable after top and bottom row placements according to seq.
    The set of tilings to check are all row tilings, with length at most k+1.

    Returns True these tilings (with the points factored out) each satisfy at least one of:
    - They have at least one empty cell (so they have length less than k+1)
    - They are row-separable (note that there may still be obstructions crossing rows)

    Args:
        tiling: A 1x1 Tiling object
        seq: A sequence of placements (1 for top row, 3 for bottom row)
        verbose: If True, give information about the process (default: False)
        fusion: If True, try fusing to make the tilings smaller. In this case separation is NOT allowed (default: False)

    Returns:
        bool: True if the conditions mentioned above are satisfied, False otherwise
    """
    if fusion:
        raise NotImplementedError("Fusion not implemented yet")

    # Start with the original tiling
    current_tilings = [tiling]

    # Apply top row placement strategy
    # top_row_factory = RowAndColumnPlacementFactory(
    #     place_row=True, place_col=False, dirs=[DIR_NORTH]
    # )
    top_row_factory = MaxRowPlacementFactory()
    # Apply bottom row placement strategy
    # bottom_row_factory = RowAndColumnPlacementFactory(
    #     place_row=True, place_col=False, dirs=[DIR_SOUTH]
    # )
    bottom_row_factory = MinRowPlacementFactory()

    # Apply leftmost column placement strategy
    # left_col_factory = RowAndColumnPlacementFactory(
    #     place_row=False, place_col=True, dirs=[DIR_WEST]
    # )
    left_col_factory = LeftColPlacementFactory()

    # Apply rightmost column placement strategy
    # right_col_factory = RowAndColumnPlacementFactory(
    #     place_row=False, place_col=True, dirs=[DIR_EAST]
    # )
    right_col_factory = RightColPlacementFactory()

    k = len(seq)
    # Count 1s and 3s in seq
    ns = sum(1 for x in seq if x == 1 or x == 3)
    we = sum(1 for x in seq if x == 2 or x == 4)

    expected_cur_ns = 1
    expected_cur_we = 1

    for i in range(k):
        if verbose:
            print(
                f"Applying top or bottom row placement {i+1}/{k} (counting from 1) to {len(current_tilings)} tilings"
            )
            for t in current_tilings:
                print(t)
            print("-------------------------------------")
        if seq[i] == 1:
            expected_cur_ns += 2
            expected_cur_we += 1
        elif seq[i] == 3:
            expected_cur_ns += 2
            expected_cur_we += 1
        elif seq[i] == 2:
            expected_cur_we += 2
            expected_cur_ns += 1
        elif seq[i] == 4:
            expected_cur_we += 2
            expected_cur_ns += 1
        next_tilings = []
        for current_tiling in current_tilings:
            # Apply top or bottom row placement to current tiling
            if seq[i] == 1:
                placement_rules = list(top_row_factory(current_tiling))
            elif seq[i] == 3:
                placement_rules = list(bottom_row_factory(current_tiling))
            elif seq[i] == 2:
                placement_rules = list(left_col_factory(current_tiling))
            elif seq[i] == 4:
                placement_rules = list(right_col_factory(current_tiling))
            else:
                raise ValueError(f"Invalid placement direction {seq[i]}")

            if placement_rules:
                # Take first applicable rule and add all its children
                rule = placement_rules[0]
                # TODO Keep track of what the maximum dimensions are up to now, and get rid of any children that are too small
                for rchild in rule.children:
                    # The dimensions of this child are:
                    # print(f"Child tiling:\n {rchild}")
                    # print(f"Dimensions: {rchild.dimensions}")
                    # print(f"Expected ({expected_cur_ns}, {expected_cur_we})")
                    # input("Press Enter to continue...")
                    if (
                        rchild.dimensions[0] < expected_cur_ns
                        or rchild.dimensions[1] < expected_cur_we
                    ):
                        if verbose:
                            print(
                                f"Discarding child {rchild} as it is too small (need at least ({expected_cur_ns}, {expected_cur_we}))"
                            )
                    else:
                        next_tilings.append(rchild)
            else:
                # If no placement rule applies, keep the current tiling
                next_tilings.append(current_tiling)

        current_tilings = next_tilings
        if (
            not current_tilings
        ):  # I need to think about this more. Finite tilings should run out of placements, but return True
            return True  # No tilings to continue with

    # Show final tilings if verbose
    if verbose:
        print(f"Final tilings after {k} placement(s) ({len(current_tilings)} total):")
        for j, final_tiling in enumerate(current_tilings):
            print(f"  Final tiling {j}:")
            print(final_tiling)

    # Now check separability for all resulting tilings
    factor_factory = FactorFactory()

    for final_tiling in current_tilings:
        # Apply factor strategy to each final tiling
        factor_rules = list(factor_factory(final_tiling))
        if factor_rules:
            for factor_rule in factor_rules:
                # Get the factored children
                factored_children = factor_rule.decomposition_function(final_tiling)

                # Check each factor (ignoring single-cell factors with requirements)
                for factored_child in factored_children:
                    if factored_child.dimensions == (1, 1):
                        if factored_child.requirements:
                            continue  # Ignore non-empty single-cell factors (points)

                    # Check if this factor is row-separable
                    try:
                        if (
                            factored_child.dimensions[0] <= ns
                            or factored_child.dimensions[1] <= we
                        ):
                            continue  # This factor is small enough to be OK

                        # Add a point requirement in all possible ways to the active cells and make the rest of the cells empty
                        if verbose:
                            print("Factored child:")
                            print(factored_child)
                            print(
                                f"  This is a factor of size (ns+1, we+1) = ({ns+1}, {we+1})"
                            )
                            print(
                                "... so it must be factorable into tilings of smaller dimensions, if we are to return True"
                            )
                            print("Checking separability...")

                        tilings_to_check = []
                        for cells in powerset(factored_child.active_cells):
                            new_obs = list(factored_child.obstructions) + [
                                GriddedPerm((0,), (cell,)) for cell in cells
                            ]
                            new_reqs = [
                                (GriddedPerm((0,), (cell,)),)
                                for cell in factored_child.active_cells - set(cells)
                            ]

                            ttc = Tiling(new_obs, new_reqs).obstruction_transitivity()
                            if ttc.dimensions[0] > ns and ttc.dimensions[1] > we:
                                # Only check if the tiling is too big to be OK already
                                # (otherwise we know it is OK)
                                if not ttc.is_empty():
                                    tilings_to_check.append(ttc)
                        # print("factored child:")
                        # print(factored_child)
                        # print("tilings to check for separability:")
                        # for ttc in tilings_to_check:
                        #     print(ttc)

                        # THERE IS SOMETHING BROKEN ABOVE BECAUSE THE TTCs ARE NOT ALL FULLY POSITIVE
                        for ttc in tilings_to_check:
                            if verbose:
                                print("Looking at ttc:")
                                print(ttc)
                                input()

                            # FIRST CALL OBSTRUCTIONS TRANSITIVITY TO MAKE SURE ALL OBSTRUCTIONS ARE PRESENT
                            row_col_sep = RowColSeparation(ttc)
                            # Now we delete all non-local obstructions, to see if the tiling would factor after row/col separation
                            # and proper targeted requirement placements
                            localized_ttc = delete_non_local_obstructions(
                                row_col_sep.separated_tiling()
                            )
                            factor_rules_for_ttc = list(factor_factory(localized_ttc))
                            if factor_rules_for_ttc:
                                for factor_rule in factor_rules_for_ttc:
                                    # Get the factored children
                                    factored_children_of_localized_ttc = (
                                        factor_rule.decomposition_function(
                                            localized_ttc
                                        )
                                    )
                            else:
                                factored_children_of_localized_ttc = [localized_ttc]

                            if verbose:
                                print("Row/col separated ttc:")
                                print(row_col_sep.separated_tiling())
                                print("Localized ttc (non-local obstructions removed):")
                                print(localized_ttc)
                                print(
                                    "Factors of localized ttc after row/col separation:"
                                )
                                for fclc in factored_children_of_localized_ttc:
                                    print(fclc)

                            # print("Factored children of localized ttc:")
                            # for fclc in factored_children_of_localized_ttc:
                            #     print(fclc)
                            # print("----")
                            # if verbose:
                            #     print(f"Now looking at factor:")
                            #     print(factored_child)

                            #     print("This is a factor of size (ns+1, we+1)")
                            #     print(
                            #         "... so it must be factorable into tilings of smaller dimensions, if we are to return True"
                            #     )
                            #     print("Checking separability...")
                            #     if any(
                            #         (
                            #             fclc.dimensions[0] >= (ns + 1)
                            #             and fclc.dimensions[1] >= (we + 1)
                            #         )
                            #         for fclc in factored_children_of_localized_child
                            #     ):
                            #         print("... and it is NOT!")
                            #     else:
                            #         print("... and it IS!")
                            #         print(" it factors into:")
                            #         for fclc in factored_children_of_localized_child:
                            #             print(fclc)
                            if any(
                                (
                                    fclc.dimensions[0] >= (ns + 1)
                                    and fclc.dimensions[1] >= (we + 1)
                                )
                                for fclc in factored_children_of_localized_ttc
                            ):
                                if verbose:
                                    print("Found non-separable factor:")
                                    print(factored_child)
                                return False  # Found a non-separable factor
                            else:
                                if verbose:
                                    print("This factor is separable :)")
                                    input()
                    except Exception as e:
                        print("Error checking separability for factor:")
                        print(factored_child)
                        raise e  # Error checking separability

    return True  # All factors in all tilings are separable


# K = 6  # 6 is enough for insertion encodable bases with 3 length 4 patterns
# ell = 3

# for basis in combinations(Perm.of_length(4), ell):
#     basis = list(sorted(basis))
#     if not is_insertion_encodable_maximum(basis):
#         basis = "_".join(str(b) for b in basis)
#         T = Tiling.from_string(basis)

#         T_is_k_sep_top = False
#         T_is_k_sep_left = False
#         for k in range(1, K + 1):
#             for seq in list(placement_seqsN(k)):  # + list(placement_seqsS(k)):
#                 if eventually_bounded_with_row_col_placements(T, seq):
#                     print(f"Basis: {basis} is bounded after {k} placements using {seq}")
#                     # if k >= 6:
#                     #     print("Stop press!")
#                     #     input("Press Enter to continue...")
#                     T_is_k_sep_top = True
#                     break
#             if T_is_k_sep_top:
#                 break
#         if not T_is_k_sep_top:
#             print(f"Basis: {basis} is NOT bounded after {K} placements")
# input("Press Enter to continue...")

# input("Press Enter to continue...")

# basis = "021"
# basis = "012"
# basis = "0213_1032_1320_2130"
# basis = "0213_0231_0321"
# basis = "0213_1302_1320_2130"
# basis = "01"
# basis = "01_10"
# basis = "0132_0231_0321_2301"
# basis = "0231_1320"
# basis = "0213"
# basis = "0321_2301"
# basis = "0132_1302"
# basis = "0231_2130"
# basis = "012_102"
# basis = "0123_1032"
# basis = "0123_0132_3201"


# T = Tiling.from_string(basis)
# print("Original tiling:")
# print(T)

# # print(T.complement())
# # print(T.inverse())
# # print(T.inverse().complement())
# # assert 0

# for seq in placement_seqsN(6):
#     print(f"Testing sequence {seq}:")
#     print(
#         f"Is separable after placements {seq}: {eventually_bounded_with_row_col_placements(T, seq=seq, verbose=True)}"
#     )
#     input("Press Enter to continue...")

# K = 5

# for basis in reversed(all_sizes):
#     print(f"Checking basis: {basis}")
#     T = Tiling.from_string(basis)

#     T_is_k_sep_top = False
#     T_is_k_sep_left = False
#     for k in range(1, K + 1):
#         for seq in placement_seqsN(k):
#             if eventually_bounded_with_row_col_placements(T, seq):
#                 print(f"Basis: {basis} is bounded after {k} placements using {seq}")
#                 if k >= 6:
#                     print("Stop press!")
#                     input("Press Enter to continue...")
#                 T_is_k_sep_top = True
#                 break
#         if T_is_k_sep_top:
#             break
#     if not T_is_k_sep_top:
#         print(f"Basis: {basis} is NOT bounded after {K} placements")
#     continue  # The stuff below is no longer necessary because we do both row and column placements above
#     if not T_is_k_sep_top:
#         print(f"Basis: {basis} is NOT bounded after {K} placements")
#         Ti = T.inverse()
#         for k in range(1, K + 1):
#             for seq in placement_seqsNS(k):
#                 if eventually_bounded_with_row_col_placements(Ti, seq):
#                     print(
#                         f"Basis: {basis} is inverse bounded after {k} placements using {seq}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
#                     )
#                     if k >= 5:
#                         print("Stop press!")
#                         input("Press Enter to continue...")
#                     T_is_k_sep_left = True
#                     break
#             if T_is_k_sep_left:
#                 break
#     if (not T_is_k_sep_top) and (not T_is_k_sep_left):
#         print(f"Basis: {basis} is NOT inverse bounded after {K} placements")
#     input("Press Enter to continue...")

# First basis that is not top separable, but is left separable
# 0132_0231_0312_0321_1032_1302_1320_3021_3120

# Data from a partial run
"""
Basis: 0213_0231_0321 is separable after 3 placements
Basis: 0213_0231_0321 is separable after 4 placements
Basis: 0213_0231_0321 is separable after 5 placements

Basis: 0213_0231_3021 is separable after 3 placements
Basis: 0213_0231_3021 is separable after 4 placements
Basis: 0213_0231_3021 is separable after 5 placements

Basis: 0231_0321_2031 is separable after 3 placements
Basis: 0231_0321_2031 is separable after 4 placements
Basis: 0231_0321_2031 is separable after 5 placements

Basis: 0231_0321_2301 is separable after 4 placements
Basis: 0231_0321_2301 is separable after 5 placements


Basis: 0132_0213_0231_0321 is separable after 3 placements
Basis: 0132_0213_0231_0321 is separable after 4 placements
Basis: 0132_0213_0231_0321 is separable after 5 placements

Basis: 0132_0213_0231_3021 is separable after 3 placements
Basis: 0132_0213_0231_3021 is separable after 4 placements
Basis: 0132_0213_0231_3021 is separable after 5 placements

Basis: 0132_0213_0231_3120 is separable after 3 placements
Basis: 0132_0213_0231_3120 is separable after 4 placements
Basis: 0132_0213_0231_3120 is separable after 5 placements

Basis: 0132_0231_0321_2031 is separable after 3 placements
Basis: 0132_0231_0321_2031 is separable after 4 placements
Basis: 0132_0231_0321_2031 is separable after 5 placements

Basis: 0132_0231_0321_2301 is separable after 4 placements
Basis: 0132_0231_0321_2301 is separable after 5 placements
"""

# basis = "0213_0231_0312_0321_1032"
# basis = "0132_0213_0231_0312_0321"
# basis = "0213_1302_1320_2130"


# pack = TileScopePack.row_and_col_placements(row_only=True)

# max_row_placements = TileScopePack(
#     [strategies.FactorFactory()],
#     [
#         strategies.RowColumnSeparationStrategy(),
#     ],
#     [[strategies.RowAndColumnPlacementFactory(place_col=False, dirs=[1])]],
#     [strategies.BasicVerificationStrategy()],
#     name="max_row_placements",
# )

# min_row_placements = TileScopePack(
#     [strategies.FactorFactory()],
#     [
#         strategies.RowColumnSeparationStrategy(),
#     ],
#     [[strategies.RowAndColumnPlacementFactory(place_col=False, dirs=[3])]],
#     [strategies.BasicVerificationStrategy()],
#     name="min_row_placements",
# )

# tilescope = TileScope(basis, max_row_placements)
# spec = tilescope.auto_search(status_update=10)
# print(spec)

from tilings import *
from tilings import strategies
from tilings.tilescope import *
from tilings.algorithms import obstruction_transitivity, RowColSeparation
from tilings.strategies import (
    RowAndColumnPlacementFactory,
    FactorFactory,
    RowColumnSeparationStrategy,
)
from permuta.misc import DIR_NORTH

import json

# TODO: Add a check to allow tilings to have empty cells - probably best to check if dimensions are smaller than expected
# TODO: Also make the point check more robust - currently only checks for (1,1) with requirements

# Load all lex-min symmetry of non-insertion encodable bases with length 4 patterns
all_sizes = []
for size in range(1, 13):
    with open(f"bases_size_{size}.json", "r") as f:
        bases = json.load(f)
    all_sizes.extend(bases)
    print(f"Size {size}: {len(bases)}")
print(f"All bases loaded")


def is_separable_after_point_placement(tiling, verbose=False):
    """
    Check if a 1x1 tiling is separable after point placement.

    Returns True if after placing one point, factoring, and ignoring the point,
    every factor is separable. Otherwise returns False.

    Args:
        tiling: A 1x1 Tiling object
        verbose: If True, print the tilings after placement (default: False)

    Returns:
        bool: True if all factors are separable, False otherwise
    """
    # Apply top row placement strategy
    top_row_factory = RowAndColumnPlacementFactory(
        place_row=True, place_col=False, dirs=[DIR_NORTH]
    )

    factor_factory = FactorFactory()

    # Check all rules from top row placement
    for rule in top_row_factory(tiling):
        if verbose:
            print(f"After 1 placement, checking {len(rule.children)} tilings:")
        # Check all children from the placement
        for i, child in enumerate(rule.children):
            if verbose:
                print(f"  Tiling {i}: {child}")
            # Apply factor strategy to each child
            factor_rules = list(factor_factory(child))
            if factor_rules:
                for factor_rule in factor_rules:
                    # Get the factored children
                    factored_children = factor_rule.decomposition_function(child)

                    # Check each factor (ignoring single-cell factors with requirements)
                    for factored_child in factored_children:
                        if factored_child.dimensions == (1, 1):
                            if factored_child.requirements:
                                continue  # Ignore non-empty single-cell factors (points)

                        # Check if this factor is row-separable
                        try:
                            row_col_sep = RowColSeparation(factored_child)
                            if (
                                factored_child.dimensions[0] == 2
                                and not row_col_sep.separable()
                            ):
                                if verbose:
                                    print("Found non-separable factor:")
                                    print(factored_child)
                                return False  # Found a non-separable factor
                        except Exception as e:
                            print("Error checking separability for factor:")
                            print(factored_child)
                            raise e  # Error checking separability

        # Only check first applicable rule
        break

    return True  # All factors are separable


def is_k_separable_after_point_placement(tiling, k, verbose=False):
    """
    Check if a 1x1 tiling is separable after k top row placements.
    The set of tilings we get are all row tilings, with length at most k+1.

    Returns True these tilings (with the points factored out) each satisfy at least one of:
    - They have at least one empty cell
    - They are row-separable

    Args:
        tiling: A 1x1 Tiling object
        k: Number of times to apply the top row placement strategy
        verbose: If True, give information about the process (default: False)

    Returns:
        bool: True if the conditions mentioned above are satisfied, False otherwise
    """
    # Start with the original tiling
    current_tilings = [tiling]

    # Apply top row placement strategy k times
    top_row_factory = RowAndColumnPlacementFactory(
        place_row=True, place_col=False, dirs=[DIR_NORTH]
    )

    for i in range(k):
        if verbose:
            print(
                f"Applying top row placement {i}/{k} (counting from 0) to {len(current_tilings)} tilings"
            )
        next_tilings = []

        for current_tiling in current_tilings:
            # Apply top row placement to current tiling
            placement_rules = list(top_row_factory(current_tiling))
            if placement_rules:
                # Take first applicable rule and add all its children
                rule = placement_rules[0]
                next_tilings.extend(rule.children)
            else:
                # If no placement rule applies, keep the current tiling
                next_tilings.append(current_tiling)

        current_tilings = next_tilings
        if (
            not current_tilings
        ):  # I need to think about this more. Finite tilings should run out of placements, but return True
            return False  # No tilings to continue with

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
                        row_col_sep = RowColSeparation(factored_child)
                        if verbose:
                            print(f"Now looking at factor:")
                            print(factored_child)
                            if factored_child.dimensions[0] == (k + 1):
                                print("This is a factor of size k+1")
                                print(
                                    "... so it must be separable, if we are to return True"
                                )
                                print("Checking separability...")
                                if not row_col_sep.separable():
                                    print("... and it is NOT separable!")
                                else:
                                    print("... and it IS separable.")
                                    print(" it separates into:")
                                    print(row_col_sep.separated_tiling())
                        if (
                            factored_child.dimensions[0] == (k + 1)
                            and not row_col_sep.separable()
                        ):
                            if verbose:
                                print("Found non-separable factor:")
                                print(factored_child)
                            return False  # Found a non-separable factor
                    except Exception as e:
                        print("Error checking separability for factor:")
                        print(factored_child)
                        raise e  # Error checking separability

    return True  # All factors in all tilings are separable


# basis = "021"
# basis = "012"
# basis = "0213_1032_1320_2130"
# basis = "0213_0231_0321"
# basis = "0213_1302_1320_2130"
# basis = "01"
# basis = "01_10"
basis = "0132_0231_0321_2301"

T = Tiling.from_string(basis)
print("Original tiling:")
print(T)

# # Test the separability functions
print(
    f"\nIs separable after 1 point placement: {is_separable_after_point_placement(T)}"
)

print(
    f"Is separable after 1 point placements: {is_k_separable_after_point_placement(T, 1)}"
)
print(
    f"Is separable after 2 point placements: {is_k_separable_after_point_placement(T, 2)}"
)
print(
    f"Is separable after 3 point placements: {is_k_separable_after_point_placement(T, 3)}"
)
print(
    f"Is separable after 4 point placements: {is_k_separable_after_point_placement(T, 4)}"
)
print(
    f"Is separable after 5 point placements: {is_k_separable_after_point_placement(T, 5)}"
)


# Test with verbose mode
print(f"\nTesting with verbose mode:")
print(
    f"Is separable after 3 point placements (verbose): {is_k_separable_after_point_placement(T, 3, verbose=True)}"
)
print(
    f"Is separable after 4 point placements (verbose): {is_k_separable_after_point_placement(T, 4, verbose=True)}"
)


for basis in all_sizes:
    print(f"Checking basis: {basis}")
    T = Tiling.from_string(basis)
    if is_separable_after_point_placement(T) != is_k_separable_after_point_placement(
        T, 1
    ):
        print(f"Discrepancy found for basis: {basis}")
        assert 0

    for k in range(1, 9):
        if is_k_separable_after_point_placement(T, k):
            print(f"Basis: {basis} is separable after {k} placements")

    if is_k_separable_after_point_placement(
        T, 5
    ) != is_k_separable_after_point_placement(T, 4):
        print(f"Basis: {basis} is only separable after 5 placements")


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

# Import max_row_placements and min_row_placements from the file row_placements.py
# from row_placements import max_row_placements, min_row_placements

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

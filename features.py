import re
import json
from collections import Counter
from typing import Dict, List, Any, Tuple
import statistics


def extract_basis_features(basis: str) -> Dict[str, Any]:
    """
    Extract features from a basis string

    Args:
        basis: Basis string like "0123", "021", "0123_3102"

    Returns:
        Dict of features for machine learning
    """
    features = {}

    # Basic length and structure
    features["length"] = len(basis)
    features["has_underscore"] = "_" in basis

    # Split by underscore if present
    parts = basis.split("_")
    features["num_parts"] = len(parts)

    # Process each part separately
    all_chars = []
    part_lengths = []

    for part in parts:
        part_lengths.append(len(part))
        all_chars.extend(list(part))

    # Character statistics
    char_counts = Counter(all_chars)
    unique_chars = set(all_chars)

    features["num_unique_chars"] = len(unique_chars)
    features["total_chars"] = len(all_chars)
    features["char_diversity"] = len(unique_chars) / len(all_chars) if all_chars else 0

    # Most common character
    if char_counts:
        most_common_char, max_count = char_counts.most_common(1)[0]
        features["most_common_char"] = most_common_char
        features["most_common_char_count"] = max_count
        features["most_common_char_freq"] = max_count / len(all_chars)
    else:
        features["most_common_char"] = None
        features["most_common_char_count"] = 0
        features["most_common_char_freq"] = 0

    # Character frequency distribution
    if all_chars:
        char_freqs = list(char_counts.values())
        features["char_freq_mean"] = statistics.mean(char_freqs)
        features["char_freq_std"] = (
            statistics.stdev(char_freqs) if len(char_freqs) > 1 else 0
        )
        features["char_freq_max"] = max(char_freqs)
        features["char_freq_min"] = min(char_freqs)
    else:
        features["char_freq_mean"] = 0
        features["char_freq_std"] = 0
        features["char_freq_max"] = 0
        features["char_freq_min"] = 0

    # Part length statistics
    if part_lengths:
        features["part_length_mean"] = statistics.mean(part_lengths)
        features["part_length_std"] = (
            statistics.stdev(part_lengths) if len(part_lengths) > 1 else 0
        )
        features["part_length_max"] = max(part_lengths)
        features["part_length_min"] = min(part_lengths)
        features["part_length_range"] = max(part_lengths) - min(part_lengths)
    else:
        features["part_length_mean"] = 0
        features["part_length_std"] = 0
        features["part_length_max"] = 0
        features["part_length_min"] = 0
        features["part_length_range"] = 0

    # Numerical pattern analysis (for parts that are numeric)
    numeric_features = {}
    for i, part in enumerate(parts):
        if part.isdigit():
            # Convert to list of integers
            digits = [int(c) for c in part]

            # Basic stats
            numeric_features[f"part_{i}_sum"] = sum(digits)
            numeric_features[f"part_{i}_mean"] = (
                statistics.mean(digits) if digits else 0
            )
            numeric_features[f"part_{i}_max"] = max(digits) if digits else 0
            numeric_features[f"part_{i}_min"] = min(digits) if digits else 0
            numeric_features[f"part_{i}_range"] = (
                max(digits) - min(digits) if digits else 0
            )

            # Sequence properties
            if len(digits) > 1:
                diffs = [digits[j + 1] - digits[j] for j in range(len(digits) - 1)]
                numeric_features[f"part_{i}_diff_mean"] = statistics.mean(diffs)
                numeric_features[f"part_{i}_diff_std"] = (
                    statistics.stdev(diffs) if len(diffs) > 1 else 0
                )
                numeric_features[f"part_{i}_is_increasing"] = all(d >= 0 for d in diffs)
                numeric_features[f"part_{i}_is_decreasing"] = all(d <= 0 for d in diffs)
                numeric_features[f"part_{i}_is_monotonic"] = (
                    numeric_features[f"part_{i}_is_increasing"]
                    or numeric_features[f"part_{i}_is_decreasing"]
                )
            else:
                numeric_features[f"part_{i}_diff_mean"] = 0
                numeric_features[f"part_{i}_diff_std"] = 0
                numeric_features[f"part_{i}_is_increasing"] = True
                numeric_features[f"part_{i}_is_decreasing"] = True
                numeric_features[f"part_{i}_is_monotonic"] = True

            # Pattern detection
            numeric_features[f"part_{i}_is_consecutive"] = (
                len(digits) > 1 and all(d == 1 for d in diffs)
                if len(digits) > 1
                else False
            )
            numeric_features[f"part_{i}_has_repeats"] = len(set(digits)) < len(digits)

    features.update(numeric_features)

    # Global numeric features (if the whole basis can be interpreted numerically)
    try:
        # Try to extract all digits from the basis
        all_digits_str = re.sub(r"[^0-9]", "", basis)
        if all_digits_str:
            all_digits = [int(c) for c in all_digits_str]

            features["all_digits_sum"] = sum(all_digits)
            features["all_digits_mean"] = statistics.mean(all_digits)
            features["all_digits_max"] = max(all_digits)
            features["all_digits_min"] = min(all_digits)
            features["all_digits_range"] = max(all_digits) - min(all_digits)
            features["all_digits_unique_count"] = len(set(all_digits))
            features["all_digits_has_zero"] = 0 in all_digits
            features["all_digits_max_digit"] = max(all_digits)
        else:
            features["all_digits_sum"] = 0
            features["all_digits_mean"] = 0
            features["all_digits_max"] = 0
            features["all_digits_min"] = 0
            features["all_digits_range"] = 0
            features["all_digits_unique_count"] = 0
            features["all_digits_has_zero"] = False
            features["all_digits_max_digit"] = 0
    except:
        features["all_digits_sum"] = 0
        features["all_digits_mean"] = 0
        features["all_digits_max"] = 0
        features["all_digits_min"] = 0
        features["all_digits_range"] = 0
        features["all_digits_unique_count"] = 0
        features["all_digits_has_zero"] = False
        features["all_digits_max_digit"] = 0

    return features


def extract_pack_features(pack_name: str, pack_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract features from a strategy pack

    Args:
        pack_name: Name of the pack
        pack_dict: Dictionary containing pack configuration

    Returns:
        Dict of features for machine learning
    """
    features = {}

    # Basic pack properties
    features["pack_name"] = pack_name
    features["pack_name_length"] = len(pack_name)
    features["has_tracked"] = "tracked" in pack_name.lower()
    features["has_fusion"] = "fusion" in pack_name.lower()
    features["has_placement"] = "placement" in pack_name.lower()
    features["has_point"] = "point" in pack_name.lower()
    features["has_row"] = "row" in pack_name.lower()
    features["has_col"] = "col" in pack_name.lower()
    features["has_insertion"] = "insertion" in pack_name.lower()

    # Count underscores in name (complexity indicator)
    features["name_underscore_count"] = pack_name.count("_")

    # Strategy configuration analysis
    expansion_strats = pack_dict.get("expansion_strats", [])
    inferral_strats = pack_dict.get("inferral_strats", [])
    initial_strats = pack_dict.get("initial_strats", [])
    ver_strats = pack_dict.get("ver_strats", [])

    # Count strategies
    features["num_expansion_strats"] = len(expansion_strats)
    features["num_inferral_strats"] = len(inferral_strats)
    features["num_initial_strats"] = len(initial_strats)
    features["num_ver_strats"] = len(ver_strats)
    features["total_strats"] = (
        features["num_expansion_strats"]
        + features["num_inferral_strats"]
        + features["num_initial_strats"]
        + features["num_ver_strats"]
    )

    # Strategy complexity (nested strategies in expansion)
    expansion_complexity = 0
    for expansion_group in expansion_strats:
        if isinstance(expansion_group, list):
            expansion_complexity += len(expansion_group)
        else:
            expansion_complexity += 1
    features["expansion_complexity"] = expansion_complexity

    # Configuration flags
    features["iterative"] = pack_dict.get("iterative", False)
    features["num_symmetries"] = len(pack_dict.get("symmetries", []))

    # Strategy type analysis
    strategy_types = set()

    # Extract strategy class names from all strategy groups
    for strat_group in [expansion_strats, inferral_strats, initial_strats, ver_strats]:
        for strat in strat_group:
            if isinstance(strat, list):
                for sub_strat in strat:
                    if isinstance(sub_strat, dict):
                        strategy_types.add(sub_strat.get("strategy_class", "unknown"))
            elif isinstance(strat, dict):
                strategy_types.add(strat.get("strategy_class", "unknown"))

    features["num_unique_strategy_types"] = len(strategy_types)

    # Specific strategy presence
    strategy_type_features = {
        "has_placement_factory": any("PlacementFactory" in s for s in strategy_types),
        "has_insertion_factory": any("InsertionFactory" in s for s in strategy_types),
        "has_fusion_factory": any("FusionFactory" in s for s in strategy_types),
        "has_factor_factory": any("FactorFactory" in s for s in strategy_types),
        "has_verification_strategy": any(
            "VerificationStrategy" in s for s in strategy_types
        ),
        "has_separation_strategy": any(
            "SeparationStrategy" in s for s in strategy_types
        ),
        "has_transitivity_factory": any(
            "TransitivityFactory" in s for s in strategy_types
        ),
        "has_assumption_factory": any("AssumptionFactory" in s for s in strategy_types),
    }
    features.update(strategy_type_features)

    # Pack size approximation (total dictionary size as complexity measure)
    features["pack_dict_size"] = len(str(pack_dict))

    return features


def create_feature_vectors(
    bases: List[str], packs: List[Tuple[str, Dict]]
) -> Tuple[List[Dict], List[str]]:
    """
    Create feature vectors for all basis-pack combinations

    Args:
        bases: List of basis strings
        packs: List of (pack_name, pack_dict) tuples

    Returns:
        Tuple of (feature_dicts, combination_ids)
    """
    feature_vectors = []
    combination_ids = []

    for basis in bases:
        basis_features = extract_basis_features(basis)

        for pack_name, pack_dict in packs:
            pack_features = extract_pack_features(pack_name, pack_dict)

            # Combine features
            combined_features = {}

            # Add basis features with prefix
            for key, value in basis_features.items():
                combined_features[f"basis_{key}"] = value

            # Add pack features with prefix
            for key, value in pack_features.items():
                combined_features[f"pack_{key}"] = value

            # Add combination identifier
            combination_id = f"{basis}___{pack_name}"
            combined_features["combination_id"] = combination_id

            feature_vectors.append(combined_features)
            combination_ids.append(combination_id)

    return feature_vectors, combination_ids


def save_features(feature_vectors: List[Dict], filename: str = "features.json"):
    """Save feature vectors to JSON file"""
    with open(filename, "w") as f:
        json.dump(feature_vectors, f, indent=2)
    print(f"Saved {len(feature_vectors)} feature vectors to {filename}")


def load_features(filename: str = "features.json") -> List[Dict]:
    """Load feature vectors from JSON file"""
    with open(filename, "r") as f:
        feature_vectors = json.load(f)
    print(f"Loaded {len(feature_vectors)} feature vectors from {filename}")
    return feature_vectors


if __name__ == "__main__":
    # Test feature extraction
    print("Testing feature extraction...")

    # Test basis features
    test_bases = ["0123", "021", "0123_3102", "0132_0213_0231"]

    for basis in test_bases:
        features = extract_basis_features(basis)
        print(f"\nBasis: {basis}")
        print(f"  Length: {features['length']}")
        print(f"  Parts: {features['num_parts']}")
        print(f"  Unique chars: {features['num_unique_chars']}")
        print(f"  Has underscore: {features['has_underscore']}")

    # Test with actual data
    print("\nTesting with real data...")

    # Load a small sample
    with open("bases_size_1.json", "r") as f:
        small_bases = json.load(f)[:3]

    with open("all_packs.json", "r") as f:
        all_packs = json.load(f)[:2]

    features, ids = create_feature_vectors(small_bases, all_packs)
    print(f"Created {len(features)} feature vectors")

    # Show first feature vector
    if features:
        print(f"\nFirst feature vector (keys): {list(features[0].keys())}")
        print(f"First combination ID: {ids[0]}")

    save_features(features, "test_features.json")

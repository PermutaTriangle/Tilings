import json
import random
import statistics
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any, Optional
from benchmark_collection import (
    load_all_bases,
    load_all_packs,
    collect_benchmark_data,
    save_benchmark_results,
    load_benchmark_results,
    analyze_results,
)
from features import create_feature_vectors, save_features, load_features


def create_train_test_split(
    bases: List[str], test_ratio: float = 0.2, random_seed: int = 42
) -> Tuple[List[str], List[str]]:
    """
    Create train/test split by randomly sampling within each basis size

    Args:
        bases: List of all bases
        test_ratio: Fraction of bases to use for testing
        random_seed: Random seed for reproducibility

    Returns:
        Tuple of (train_bases, test_bases)
    """
    random.seed(random_seed)

    # Group bases by size
    size_groups = defaultdict(list)
    for basis in bases:
        # Remove underscores and count digits to get size
        digits_only = "".join(c for c in basis if c.isdigit())
        if digits_only:
            size = len(set(digits_only))  # Count unique digits as a size measure
            size_groups[size].append(basis)

    train_bases = []
    test_bases = []

    # Split each size group
    for size, size_bases in size_groups.items():
        n_test = max(1, int(len(size_bases) * test_ratio))
        n_test = min(n_test, len(size_bases) - 1)  # Ensure at least 1 for training

        # Random split within this size
        shuffled = size_bases.copy()
        random.shuffle(shuffled)

        test_bases.extend(shuffled[:n_test])
        train_bases.extend(shuffled[n_test:])

        print(
            f"Size {size}: {len(size_bases)} total, {n_test} test, {len(shuffled[n_test:])} train"
        )

    print(f"\nTotal: {len(bases)} bases")
    print(f"Training: {len(train_bases)} bases ({len(train_bases)/len(bases):.1%})")
    print(f"Testing: {len(test_bases)} bases ({len(test_bases)/len(bases):.1%})")

    return train_bases, test_bases


def prepare_training_data(
    benchmark_results: List[Dict[str, Any]], feature_vectors: List[Dict[str, Any]]
) -> Tuple[List[Dict], List[float], List[str]]:
    """
    Prepare training data by combining features with benchmark results

    Args:
        benchmark_results: List of benchmark results
        feature_vectors: List of feature vectors

    Returns:
        Tuple of (features, targets, combination_ids)
        - features: Feature dictionaries
        - targets: Target values (time for successful runs, timeout_time for failures)
        - combination_ids: Combination identifiers
    """

    # Create lookup from combination_id to benchmark result
    results_lookup = {}
    for result in benchmark_results:
        combination_id = f"{result['basis']}___{result['pack_name']}"
        results_lookup[combination_id] = result

    # Create lookup from combination_id to features
    features_lookup = {}
    for feature_dict in feature_vectors:
        combination_id = feature_dict["combination_id"]
        features_lookup[combination_id] = feature_dict

    # Combine data
    combined_features = []
    targets = []
    valid_combination_ids = []

    for combination_id in results_lookup:
        if combination_id in features_lookup:
            result = results_lookup[combination_id]
            features = features_lookup[combination_id]

            # Create target based on result
            if result["status"] == "completed" and result["success"]:
                # Successful completion - use actual time
                target = result["time_taken"]
            elif result["status"] == "timeout":
                # Timeout - use timeout time (penalty)
                target = result["time_taken"]  # Should be timeout_seconds
            elif result["status"] == "error":
                # Error - treat as maximum penalty
                target = 300.0  # 5 minutes as maximum penalty
            else:
                # Other cases - skip
                continue

            combined_features.append(features)
            targets.append(target)
            valid_combination_ids.append(combination_id)

    print(f"Prepared {len(combined_features)} training examples")
    return combined_features, targets, valid_combination_ids


class SimpleBaselineModel:
    """
    Simple baseline model for predicting pack performance
    Uses basic heuristics and statistical rules
    """

    def __init__(self):
        self.pack_performance = {}  # Average performance per pack
        self.basis_size_performance = {}  # Average performance per basis size
        self.global_mean = None
        self.is_trained = False

    def train(
        self, features: List[Dict], targets: List[float], combination_ids: List[str]
    ):
        """Train the baseline model"""
        print("Training baseline model...")

        # Global statistics
        self.global_mean = statistics.mean(targets)

        # Pack performance statistics
        pack_times = defaultdict(list)
        basis_size_times = defaultdict(list)

        for i, (feature_dict, target) in enumerate(zip(features, targets)):
            pack_name = feature_dict["pack_pack_name"]
            basis_length = feature_dict["basis_length"]

            pack_times[pack_name].append(target)
            basis_size_times[basis_length].append(target)

        # Calculate average performance per pack
        for pack_name, times in pack_times.items():
            self.pack_performance[pack_name] = {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "count": len(times),
                "std": statistics.stdev(times) if len(times) > 1 else 0,
            }

        # Calculate average performance per basis size
        for basis_size, times in basis_size_times.items():
            self.basis_size_performance[basis_size] = {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "count": len(times),
                "std": statistics.stdev(times) if len(times) > 1 else 0,
            }

        self.is_trained = True
        print(f"Model trained on {len(features)} examples")
        print(f"Global mean time: {self.global_mean:.2f}s")
        print(f"Learned {len(self.pack_performance)} pack profiles")
        print(f"Learned {len(self.basis_size_performance)} basis size profiles")

    def predict(self, features: List[Dict]) -> List[float]:
        """Predict performance for given features"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        predictions = []

        for feature_dict in features:
            pack_name = feature_dict["pack_pack_name"]
            basis_length = feature_dict["basis_length"]

            # Start with global mean
            prediction = self.global_mean

            # Adjust based on pack performance
            if pack_name in self.pack_performance:
                pack_mean = self.pack_performance[pack_name]["mean"]
                prediction = 0.6 * pack_mean + 0.4 * prediction

            # Adjust based on basis size
            if basis_length in self.basis_size_performance:
                size_mean = self.basis_size_performance[basis_length]["mean"]
                prediction = 0.7 * prediction + 0.3 * size_mean

            predictions.append(prediction)

        return predictions

    def get_pack_rankings(self) -> List[Tuple[str, float]]:
        """Get packs ranked by average performance (best first)"""
        pack_scores = [
            (pack, stats["mean"]) for pack, stats in self.pack_performance.items()
        ]
        pack_scores.sort(key=lambda x: x[1])  # Sort by time (lower is better)
        return pack_scores

    def recommend_pack(self, basis: str, top_k: int = 3) -> List[str]:
        """Recommend top-k packs for a given basis"""
        rankings = self.get_pack_rankings()
        return [pack for pack, score in rankings[:top_k]]


def evaluate_model(
    model: SimpleBaselineModel,
    test_features: List[Dict],
    test_targets: List[float],
    test_ids: List[str],
) -> Dict[str, float]:
    """Evaluate model performance"""

    predictions = model.predict(test_features)

    # Calculate metrics
    mse = statistics.mean(
        [(pred - actual) ** 2 for pred, actual in zip(predictions, test_targets)]
    )
    mae = statistics.mean(
        [abs(pred - actual) for pred, actual in zip(predictions, test_targets)]
    )
    rmse = mse**0.5

    # Calculate baseline metrics (always predict global mean)
    global_mean = statistics.mean(test_targets)
    baseline_mse = statistics.mean(
        [(global_mean - actual) ** 2 for actual in test_targets]
    )
    baseline_mae = statistics.mean(
        [abs(global_mean - actual) for actual in test_targets]
    )

    # R² score
    ss_res = sum(
        [(pred - actual) ** 2 for pred, actual in zip(predictions, test_targets)]
    )
    ss_tot = sum([(actual - global_mean) ** 2 for actual in test_targets])
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    metrics = {
        "mse": mse,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "baseline_mse": baseline_mse,
        "baseline_mae": baseline_mae,
        "improvement_mse": (baseline_mse - mse) / baseline_mse
        if baseline_mse > 0
        else 0,
        "improvement_mae": (baseline_mae - mae) / baseline_mae
        if baseline_mae > 0
        else 0,
    }

    return metrics


def run_full_pipeline(
    max_combinations: int = 100,
    timeout_seconds: int = 60,
    test_ratio: float = 0.2,
    random_seed: int = 42,
):
    """Run the complete ML pipeline"""

    print("=== Machine Learning Pipeline for Strategy Pack Optimization ===\n")

    # 1. Load data
    print("1. Loading bases and packs...")
    all_bases = load_all_bases()
    all_packs = load_all_packs()

    # 2. Create train/test split
    print("\n2. Creating train/test split...")
    train_bases, test_bases = create_train_test_split(
        all_bases, test_ratio, random_seed
    )

    # 3. Sample for initial experiment
    if max_combinations:
        # Sample packs and limit combinations
        n_packs = min(3, len(all_packs))  # Use up to 3 packs for testing
        sampled_packs = random.sample(all_packs, n_packs)

        # Limit bases too if needed
        max_bases_per_split = max(1, max_combinations // (2 * n_packs))
        if len(train_bases) > max_bases_per_split:
            train_bases = train_bases[:max_bases_per_split]
        if len(test_bases) > max_bases_per_split:
            test_bases = test_bases[:max_bases_per_split]

        print(
            f"Limited to {len(train_bases)} train bases, {len(test_bases)} test bases, {n_packs} packs"
        )
    else:
        sampled_packs = all_packs

    # 4. Collect benchmark data
    print("\n3. Collecting benchmark data...")

    try:
        # Try to load existing results
        train_results = load_benchmark_results("train_benchmark_results.json")
        test_results = load_benchmark_results("test_benchmark_results.json")
        print("Loaded existing benchmark results")
    except FileNotFoundError:
        print("Collecting new benchmark data...")

        train_results = collect_benchmark_data(
            bases=train_bases, packs=sampled_packs, timeout_seconds=timeout_seconds
        )
        save_benchmark_results(train_results, "train_benchmark_results.json")

        test_results = collect_benchmark_data(
            bases=test_bases, packs=sampled_packs, timeout_seconds=timeout_seconds
        )
        save_benchmark_results(test_results, "test_benchmark_results.json")

    print("\nTraining data:")
    analyze_results(train_results)

    print("\nTest data:")
    analyze_results(test_results)

    # 5. Create features
    print("\n4. Creating features...")
    train_feature_vectors, train_ids = create_feature_vectors(
        train_bases, sampled_packs
    )
    test_feature_vectors, test_ids = create_feature_vectors(test_bases, sampled_packs)

    save_features(train_feature_vectors, "train_features.json")
    save_features(test_feature_vectors, "test_features.json")

    # 6. Prepare training data
    print("\n5. Preparing training data...")
    train_features, train_targets, train_valid_ids = prepare_training_data(
        train_results, train_feature_vectors
    )
    test_features, test_targets, test_valid_ids = prepare_training_data(
        test_results, test_feature_vectors
    )

    # 7. Train model
    print("\n6. Training baseline model...")
    model = SimpleBaselineModel()
    model.train(train_features, train_targets, train_valid_ids)

    # 8. Evaluate model
    print("\n7. Evaluating model...")
    metrics = evaluate_model(model, test_features, test_targets, test_valid_ids)

    print("\n=== Model Performance ===")
    print(f"RMSE: {metrics['rmse']:.2f}s")
    print(f"MAE: {metrics['mae']:.2f}s")
    print(f"R²: {metrics['r2']:.3f}")
    print(f"MSE Improvement over baseline: {metrics['improvement_mse']:.1%}")
    print(f"MAE Improvement over baseline: {metrics['improvement_mae']:.1%}")

    # 9. Show pack rankings
    print("\n=== Pack Rankings (Best to Worst) ===")
    rankings = model.get_pack_rankings()
    for i, (pack, score) in enumerate(rankings[:10]):
        print(f"{i+1:2d}. {pack:<40} {score:6.2f}s")

    # 10. Example recommendations
    print("\n=== Example Recommendations ===")
    example_bases = test_bases[:5]
    for basis in example_bases:
        recommendations = model.recommend_pack(basis, top_k=3)
        print(f"{basis:<20} → {', '.join(recommendations)}")

    return model, metrics


if __name__ == "__main__":
    # Run with small dataset for testing
    model, metrics = run_full_pipeline(
        max_combinations=50,  # Small test
        timeout_seconds=60,  # 1 minute timeout for experimentation
        test_ratio=0.3,  # 30% for testing
        random_seed=42,
    )

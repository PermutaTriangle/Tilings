from ml_pipeline import SimpleBaselineModel, evaluate_model, prepare_training_data
from features import create_feature_vectors
from benchmark_collection import load_benchmark_results, analyze_results
import json


def demo_ml_pipeline():
    print("=== Demo ML Pipeline for Strategy Pack Optimization ===\n")

    # 1. Load the small benchmark data we collected
    print("1. Loading benchmark results...")
    try:
        results = load_benchmark_results("small_benchmark_results.json")
        analyze_results(results)
    except FileNotFoundError:
        print(
            "Error: small_benchmark_results.json not found. Run collect_small_benchmark.py first."
        )
        return

    # 2. Extract successful results and extract basis/pack info
    print("\n2. Processing results...")
    successful_results = [
        r for r in results if r["status"] == "completed" and r["success"]
    ]
    error_results = [r for r in results if r["status"] == "error"]

    print(f"Successful: {len(successful_results)}")
    print(f"Errors: {len(error_results)}")

    if len(successful_results) < 2:
        print("Not enough successful results for ML demo")
        return

    # 3. Extract basis and pack info from successful results
    bases = list(set(r["basis"] for r in successful_results))
    pack_info = {}

    # Load pack data to reconstruct features
    with open("all_packs.json", "r") as f:
        all_packs = json.load(f)

    pack_lookup = {name: pack_dict for name, pack_dict in all_packs}

    # Filter to only packs that worked
    working_pack_names = set()
    for result in successful_results:
        pack_name = result["pack_name"]
        if pack_name in pack_lookup:
            working_pack_names.add(pack_name)

    # Convert to list of tuples
    working_packs = [(name, pack_lookup[name]) for name in working_pack_names]

    print(f"Bases with successful results: {len(bases)}")
    print(f"Packs with successful results: {len(working_packs)}")

    # 4. Create features for successful combinations
    print("\n3. Creating features...")
    feature_vectors, combination_ids = create_feature_vectors(bases, working_packs)

    # 5. Prepare training data
    print("\n4. Preparing training data...")
    train_features, train_targets, train_ids = prepare_training_data(
        successful_results, feature_vectors
    )

    if len(train_features) < 2:
        print("Not enough training data for ML demo")
        return

    # 6. Split into train/test (simple split for demo)
    split_idx = len(train_features) // 2
    test_features = train_features[split_idx:]
    test_targets = train_targets[split_idx:]
    test_ids = train_ids[split_idx:]

    train_features = train_features[:split_idx]
    train_targets = train_targets[:split_idx]
    train_ids = train_ids[:split_idx]

    print(f"Training examples: {len(train_features)}")
    print(f"Test examples: {len(test_features)}")

    # 7. Train model
    print("\n5. Training baseline model...")
    model = SimpleBaselineModel()
    model.train(train_features, train_targets, train_ids)

    # 8. Evaluate if we have test data
    if len(test_features) > 0:
        print("\n6. Evaluating model...")
        metrics = evaluate_model(model, test_features, test_targets, test_ids)

        print(f"RMSE: {metrics['rmse']:.2f}s")
        print(f"MAE: {metrics['mae']:.2f}s")
        print(f"R²: {metrics['r2']:.3f}")
        print(f"MSE Improvement: {metrics['improvement_mse']:.1%}")
    else:
        print("\n6. Not enough test data for evaluation")

    # 9. Show pack rankings
    print("\n7. Pack Rankings (Best to Worst):")
    rankings = model.get_pack_rankings()
    for i, (pack, score) in enumerate(rankings):
        print(f"{i+1:2d}. {pack:<50} {score:6.2f}s")

    # 10. Example recommendations
    print("\n8. Example Recommendations:")
    for basis in bases[:3]:
        recommendations = model.recommend_pack(basis, top_k=2)
        print(f"{basis:<30} → {', '.join(recommendations)}")

    print("\n=== Demo completed successfully! ===")
    return model


if __name__ == "__main__":
    demo_ml_pipeline()

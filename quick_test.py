from ml_pipeline import run_full_pipeline

if __name__ == "__main__":
    # Run with very small dataset for quick testing
    print("Running quick test of ML pipeline...")

    model, metrics = run_full_pipeline(
        max_combinations=15,  # Very small test
        timeout_seconds=60,  # 1 minute timeout
        test_ratio=0.4,  # 40% for testing (small numbers)
        random_seed=42,
    )

    print(f"\nQuick test completed!")
    print(f"RMSE: {metrics['rmse']:.2f}s")
    print(f"R²: {metrics['r2']:.3f}")
    print(f"Improvement over baseline: {metrics['improvement_mae']:.1%}")

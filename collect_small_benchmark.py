from benchmark_collection import (
    load_all_bases,
    load_all_packs,
    collect_benchmark_data,
    save_benchmark_results,
)
import random

# Load data
all_bases = load_all_bases()
all_packs = load_all_packs()

print(f"Total bases: {len(all_bases)}")
print(f"Total packs: {len(all_packs)}")

# Take very small sample for testing
random.seed(42)
small_bases = random.sample(all_bases, 5)  # Just 5 bases
small_packs = random.sample(all_packs, 3)  # Just 3 packs

print(f"\nSelected bases: {small_bases}")
print(f"Selected packs: {[pack[0] for pack in small_packs]}")

# Collect benchmark data
print("\nCollecting benchmark data...")
results = collect_benchmark_data(
    bases=small_bases, packs=small_packs, timeout_seconds=60
)

save_benchmark_results(results, "small_benchmark_results.json")
print(f"\nCollected {len(results)} benchmark results")

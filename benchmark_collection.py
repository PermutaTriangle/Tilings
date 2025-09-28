import json
import time
import signal
import random
import statistics
from contextlib import contextmanager
from tilings.tilescope import TileScope, TileScopePack
from typing import Dict, List, Tuple, Optional, Any


class TimeoutException(Exception):
    pass


@contextmanager
def timeout(seconds):
    """Context manager for timing out function calls"""

    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    # Set the signal handler and alarm
    old_handler = signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Restore the old handler and cancel the alarm
        signal.signal(signal.SIGALRM, old_handler)
        signal.alarm(0)


def load_all_bases() -> List[str]:
    """Load all bases from the size-specific JSON files"""
    all_bases = []
    for size in range(1, 13):
        try:
            with open(f"bases_size_{size}.json", "r") as f:
                bases = json.load(f)
            all_bases.extend(bases)
            print(f"Loaded {len(bases)} bases of size {size}")
        except FileNotFoundError:
            print(f"Warning: bases_size_{size}.json not found")
    return all_bases


def load_all_packs() -> List[Tuple[str, Dict]]:
    """Load all strategy packs from all_packs.json"""
    with open("all_packs.json", "r") as f:
        loaded_packs = json.load(f)
    print(f"Loaded {len(loaded_packs)} strategy packs")
    return loaded_packs


def run_basis_pack_benchmark(
    basis: str, pack_name: str, pack_dict: Dict, timeout_seconds: int = 60
) -> Dict[str, Any]:
    """
    Run a single basis-pack combination and measure performance

    Returns:
        Dict containing: basis, pack_name, status, time_taken, success, specification
    """
    result = {
        "basis": basis,
        "pack_name": pack_name,
        "status": "unknown",
        "time_taken": None,
        "success": False,
        "specification": None,
        "error": None,
    }

    try:
        # Create pack and tilescope objects
        pack = TileScopePack.from_dict(pack_dict)
        tilescope = TileScope(basis, pack)

        # Run with timeout
        start_time = time.time()

        with timeout(timeout_seconds):
            spec = tilescope.auto_search()

        end_time = time.time()

        # Record results
        result["time_taken"] = end_time - start_time
        result["status"] = "completed"
        result["success"] = spec is not None
        result["specification"] = str(spec) if spec is not None else None

    except TimeoutException:
        result["status"] = "timeout"
        result["time_taken"] = timeout_seconds
        result["error"] = "Timeout after {} seconds".format(timeout_seconds)

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def collect_benchmark_data(
    bases: List[str] = None,
    packs: List[Tuple[str, Dict]] = None,
    timeout_seconds: int = 60,
    max_combinations: int = None,
    sample_ratio: float = None,
    delay_between_tests: float = 1.0,
) -> List[Dict[str, Any]]:
    """
    Collect benchmark data for basis-pack combinations

    Args:
        bases: List of bases to test (if None, loads all)
        packs: List of (name, dict) pack tuples (if None, loads all)
        timeout_seconds: Timeout for each run
        max_combinations: Maximum number of combinations to test
        sample_ratio: Fraction of combinations to sample randomly
        delay_between_tests: Seconds to wait between each test

    Returns:
        List of benchmark results
    """

    # Load data if not provided
    if bases is None:
        bases = load_all_bases()
    if packs is None:
        packs = load_all_packs()

    print(f"Starting benchmark with {len(bases)} bases and {len(packs)} packs")
    total_combinations = len(bases) * len(packs)
    print(f"Total combinations: {total_combinations}")

    # Generate all combinations
    combinations = [
        (basis, pack_name, pack_dict)
        for basis in bases
        for pack_name, pack_dict in packs
    ]

    # Sample if requested
    if sample_ratio is not None:
        sample_size = int(len(combinations) * sample_ratio)
        combinations = random.sample(combinations, sample_size)
        print(f"Sampling {len(combinations)} combinations ({sample_ratio:.1%})")

    if max_combinations is not None and len(combinations) > max_combinations:
        combinations = combinations[:max_combinations]
        print(f"Limited to first {max_combinations} combinations")

    # Run benchmarks
    results = []
    start_total = time.time()

    for i, (basis, pack_name, pack_dict) in enumerate(combinations):
        print(f"[{i+1}/{len(combinations)}] Testing {basis} with {pack_name}")

        result = run_basis_pack_benchmark(basis, pack_name, pack_dict, timeout_seconds)
        results.append(result)

        # Print progress
        if result["status"] == "completed":
            print(
                f"  ✓ Completed in {result['time_taken']:.2f}s, success: {result['success']}"
            )
        elif result["status"] == "timeout":
            print(f"  ⏰ Timeout after {timeout_seconds}s")
        else:
            print(f"  ❌ Error: {result['error']}")

        # Estimate remaining time
        if i > 0:
            elapsed = time.time() - start_total
            avg_time = elapsed / (i + 1)
            remaining = avg_time * (len(combinations) - i - 1)
            print(f"  Estimated remaining: {remaining/60:.1f} minutes")

        # Add delay between tests to help with potential signal/state issues
        if (
            delay_between_tests > 0 and i < len(combinations) - 1
        ):  # Don't delay after last test
            time.sleep(delay_between_tests)

    return results


def save_benchmark_results(
    results: List[Dict[str, Any]], filename: str = "benchmark_results.json"
):
    """Save benchmark results to JSON file"""
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} results to {filename}")


def load_benchmark_results(
    filename: str = "benchmark_results.json",
) -> List[Dict[str, Any]]:
    """Load benchmark results from JSON file"""
    with open(filename, "r") as f:
        results = json.load(f)
    print(f"Loaded {len(results)} results from {filename}")
    return results


def analyze_results(results: List[Dict[str, Any]]):
    """Print basic analysis of benchmark results"""
    total = len(results)

    if total == 0:
        print(f"\n=== Benchmark Results Analysis ===")
        print(f"Total combinations tested: {total}")
        print("No results to analyze")
        return

    completed = sum(1 for r in results if r["status"] == "completed")
    timeouts = sum(1 for r in results if r["status"] == "timeout")
    errors = sum(1 for r in results if r["status"] == "error")
    successful = sum(1 for r in results if r["success"])

    print(f"\n=== Benchmark Results Analysis ===")
    print(f"Total combinations tested: {total}")
    print(f"Completed: {completed} ({completed/total:.1%})")
    print(f"Timeouts: {timeouts} ({timeouts/total:.1%})")
    print(f"Errors: {errors} ({errors/total:.1%})")
    print(f"Successful (found spec): {successful} ({successful/total:.1%})")

    if completed > 0:
        completed_results = [r for r in results if r["status"] == "completed"]
        times = [r["time_taken"] for r in completed_results]
        print(f"\nTiming stats for completed runs:")
        print(f"  Mean time: {statistics.mean(times):.2f}s")
        print(f"  Median time: {statistics.median(times):.2f}s")
        print(f"  Min time: {min(times):.2f}s")
        print(f"  Max time: {max(times):.2f}s")


if __name__ == "__main__":
    # Quick test with small sample
    print("Running small benchmark test...")

    # Test with just a few combinations
    bases = load_all_bases()[:5]  # First 5 bases
    packs = load_all_packs()[:3]  # First 3 packs

    results = collect_benchmark_data(
        bases=bases,
        packs=packs,
        timeout_seconds=60,  # 1 minute timeout for experimentation
    )

    save_benchmark_results(results, "test_benchmark_results.json")
    analyze_results(results)

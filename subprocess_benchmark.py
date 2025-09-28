import subprocess
import json
import time
from typing import Dict, List, Tuple, Any


def run_single_test_subprocess(
    basis: str, pack_name: str, pack_dict: Dict, timeout_seconds: int = 60
) -> Dict[str, Any]:
    """
    Run a single basis-pack test in a separate subprocess to avoid state corruption
    """

    # Create a temporary script that runs the test
    # Use proper Python repr for the pack_dict instead of JSON
    test_script = f"""
import json
import sys
import time
import signal
import traceback
from tilings.tilescope import TileScope, TileScopePack

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Timeout")

# Set up the test
basis = {repr(basis)}
pack_name = {repr(pack_name)}
pack_dict = {repr(pack_dict)}

result = {{
    "basis": basis,
    "pack_name": pack_name,
    "status": "unknown",
    "time_taken": None,
    "success": False,
    "specification": None,
    "error": None
}}

try:
    # Set timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm({timeout_seconds})

    # Create pack and run test
    start_time = time.time()
    pack = TileScopePack.from_dict(pack_dict)
    tilescope = TileScope(basis, pack)
    spec = tilescope.auto_search()
    end_time = time.time()

    # Record success
    result["time_taken"] = end_time - start_time
    result["status"] = "completed"
    result["success"] = spec is not None
    result["specification"] = str(spec) if spec is not None else None

    signal.alarm(0)  # Cancel timeout

except TimeoutException:
    result["status"] = "timeout"
    result["time_taken"] = {timeout_seconds}
    result["error"] = "Timeout after {{}} seconds".format({timeout_seconds})

except Exception as e:
    result["status"] = "error"
    result["error"] = str(e)

# Output result as JSON
print("RESULT_START")
print(json.dumps(result))
print("RESULT_END")
"""

    try:
        # Run the script in a subprocess
        process = subprocess.run(
            ["python", "-c", test_script],
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 10,  # Extra buffer for subprocess overhead
        )

        # Parse the result from stdout
        stdout = process.stdout
        if "RESULT_START" in stdout and "RESULT_END" in stdout:
            start_idx = stdout.find("RESULT_START") + len("RESULT_START\n")
            end_idx = stdout.find("RESULT_END")
            result_json = stdout[start_idx:end_idx].strip()
            result = json.loads(result_json)
        else:
            # Fallback if parsing fails
            result = {
                "basis": basis,
                "pack_name": pack_name,
                "status": "error",
                "time_taken": None,
                "success": False,
                "specification": None,
                "error": f"Subprocess parsing failed. Return code: {process.returncode}",
            }

        # Check for errors in stderr
        if process.stderr:
            if result["status"] != "error":
                result["subprocess_stderr"] = process.stderr

    except subprocess.TimeoutExpired:
        result = {
            "basis": basis,
            "pack_name": pack_name,
            "status": "timeout",
            "time_taken": timeout_seconds,
            "success": False,
            "specification": None,
            "error": f"Subprocess timeout after {timeout_seconds} seconds",
        }
    except Exception as e:
        result = {
            "basis": basis,
            "pack_name": pack_name,
            "status": "error",
            "time_taken": None,
            "success": False,
            "specification": None,
            "error": f"Subprocess error: {str(e)}",
        }

    return result


def collect_benchmark_subprocess(
    bases: List[str], packs: List[Tuple[str, Dict]], timeout_seconds: int = 60
) -> List[Dict[str, Any]]:
    """
    Collect benchmark data using subprocess isolation
    """

    print(
        f"Starting subprocess benchmark with {len(bases)} bases and {len(packs)} packs"
    )
    total_combinations = len(bases) * len(packs)
    print(f"Total combinations: {total_combinations}")

    results = []
    start_total = time.time()

    i = 0
    for basis in bases:
        for pack_name, pack_dict in packs:
            i += 1
            print(f"[{i}/{total_combinations}] Testing {basis} with {pack_name}")

            result = run_single_test_subprocess(
                basis, pack_name, pack_dict, timeout_seconds
            )
            results.append(result)

            # Print result
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
                avg_time = elapsed / i
                remaining = avg_time * (total_combinations - i)
                print(f"  Estimated remaining: {remaining/60:.1f} minutes")

    return results


if __name__ == "__main__":
    # Test the same combinations that failed before
    failing_bases = [
        "0213_0321_1320_2301",
        "0132_1203_1230",
        "0231_1032_1302_1320_2031",
        "0213_0231_1302_1320_3120",
    ]

    with open("all_packs.json", "r") as f:
        all_packs = json.load(f)

    failing_pack_names = [
        "root_then_row_length_1_tracked_fusion_isolated",
        "point_and_row_placements_tracked_fusion_req_corrob_expand_verified",
        "row_and_col_placements_tracked_fusion_isolated_single_fusion",
    ]

    failing_packs = [
        (name, pack_dict) for name, pack_dict in all_packs if name in failing_pack_names
    ]

    print("Testing with subprocess isolation...")
    results = collect_benchmark_subprocess(
        failing_bases, failing_packs, timeout_seconds=60
    )

    # Analyze results
    from benchmark_collection import analyze_results

    analyze_results(results)

    # Count specific errors
    errors = [r for r in results if r["status"] == "error"]
    class_module_errors = [r for r in errors if "class_module" in str(r["error"])]

    print(f"\nDetailed analysis:")
    print(f"Total errors: {len(errors)}")
    print(f"Class module errors: {len(class_module_errors)}")

    if len(class_module_errors) == 0:
        print("✅ Subprocess isolation eliminated class_module errors!")
    else:
        print("❌ Subprocess isolation didn't fix the issue")

    # Save results
    with open("subprocess_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to subprocess_benchmark_results.json")

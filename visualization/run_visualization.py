#!/usr/bin/env python3
"""
Complete example: Generate visualization data and launch the browser interface.
"""
import sys
import os
import subprocess
import time
from pathlib import Path

# Add the parent directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from tilescope_visualizer import VisualizationTileScope
from tilings.tilescope import TileScopePack


def generate_example_data(pattern="231", pack_type="point_placements"):
    """Generate example visualization data."""
    print(f"Generating visualization data for pattern '{pattern}'...")

    # Create strategy pack
    if pack_type == "point_placements":
        pack = TileScopePack.point_placements()
    else:
        raise ValueError(f"Unknown pack type: {pack_type}")

    # Create visualization TileScope
    print("Setting up TileScope with visualization...")
    tilescope = VisualizationTileScope(pattern, pack)

    # Run the search
    print("Running auto search...")
    spec = tilescope.auto_search()

    # Save visualization data
    data_file = "web/visualization_data.json"  # Save in web directory
    tilescope.save_visualization_data(data_file)

    print(f"\nSearch Results:")
    print(f"- Pattern: {pattern}")
    print(f"- Specification found: {spec is not None}")
    print(f"- Nodes explored: {len(tilescope.search_data['nodes'])}")
    print(f"- Strategies applied: {len(tilescope.search_data['strategies_applied'])}")
    print(f"- Data saved to: {data_file}")

    return data_file, spec


def launch_server(port=8000):
    """Launch the visualization server."""
    print(f"\nLaunching visualization server on port {port}...")

    server_script = Path(__file__).parent / "server.py"
    try:
        # Launch server in the background
        subprocess.run([sys.executable, str(server_script), "--port", str(port)])
    except KeyboardInterrupt:
        print("\nVisualization stopped.")


def run_complete_example():
    """Run the complete example with multiple patterns."""
    print("TileScope Visualization Example")
    print("==============================\n")

    examples = [
        ("231", "Basic example - avoiding pattern 231"),
        ("1324", "More complex example - avoiding pattern 1324"),
        ("123", "Simple increasing pattern"),
    ]

    print("Available examples:")
    for i, (pattern, description) in enumerate(examples, 1):
        print(f"  {i}. {pattern}: {description}")

    print(f"  {len(examples) + 1}. Custom pattern")
    print()

    # Get user choice
    try:
        choice = input(
            f"Select an example (1-{len(examples) + 1}) or press Enter for default: "
        ).strip()
        if not choice:
            choice = "1"

        choice_idx = int(choice) - 1

        if 0 <= choice_idx < len(examples):
            pattern = examples[choice_idx][0]
            description = examples[choice_idx][1]
            print(f"Selected: {pattern} - {description}")
        elif choice_idx == len(examples):
            pattern = input("Enter your custom pattern: ").strip()
            if not pattern:
                pattern = "231"
                print(f"Using default pattern: {pattern}")
        else:
            print("Invalid choice, using default.")
            pattern = "231"

    except (ValueError, KeyboardInterrupt):
        print("Using default pattern: 231")
        pattern = "231"

    # Generate data
    try:
        data_file, spec = generate_example_data(pattern)

        if spec:
            print(f"\nSpecification preview:")
            print("-" * 40)
            print(str(spec)[:500] + "..." if len(str(spec)) > 500 else str(spec))
            print("-" * 40)

        # Ask if user wants to launch server
        launch = input("\nLaunch visualization server? (Y/n): ").strip().lower()
        if launch != "n":
            launch_server()

    except Exception as e:
        print(f"Error generating visualization: {e}")
        sys.exit(1)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="TileScope Visualization Runner")
    parser.add_argument(
        "pattern",
        nargs="?",
        default=None,
        help='Permutation pattern to analyze (e.g., "231")',
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the visualization server (default: 8000)",
    )
    parser.add_argument(
        "--no-server",
        action="store_true",
        help="Generate data only, do not launch server",
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Run in interactive mode"
    )

    args = parser.parse_args()

    if args.interactive or args.pattern is None:
        run_complete_example()
    else:
        # Direct pattern specification
        try:
            data_file, spec = generate_example_data(args.pattern)
            if not args.no_server:
                launch_server(args.port)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()

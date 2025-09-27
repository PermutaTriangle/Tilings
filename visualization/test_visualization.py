"""
Test script for the TileScope visualizer.
"""
from tilescope_visualizer import VisualizationTileScope
from tilings.tilescope import TileScopePack


def test_visualization():
    """Run a simple test and generate visualization data."""

    print("Setting up TileScope with visualization...")

    # Create strategy pack
    pack = TileScopePack.point_placements()

    # Create visualization TileScope
    tilescope = VisualizationTileScope("231", pack)

    print("Running auto search...")

    # Run the search
    spec = tilescope.auto_search()

    print(f"Search completed. Result: {spec}")

    # Save visualization data
    data_file = tilescope.save_visualization_data("visualization_data.json")

    print(f"Visualization data saved to: {data_file}")
    print(f"Number of nodes explored: {len(tilescope.search_data['nodes'])}")
    print(
        f"Number of strategies applied: {len(tilescope.search_data['strategies_applied'])}"
    )

    return data_file


if __name__ == "__main__":
    test_visualization()

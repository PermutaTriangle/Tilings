#!/usr/bin/env python3
"""
Demo script for TileScope visualization.
"""
import webbrowser
import subprocess
import sys
import time
from pathlib import Path


def run_demo():
    """Run a quick demo of the visualization."""
    print("TileScope Visualization Demo")
    print("===========================\n")

    # Generate fresh data
    print("1. Generating visualization data for pattern '231'...")
    subprocess.run([sys.executable, "run_visualization.py", "231", "--no-server"])

    print("\n2. Starting visualization server...")
    print("   Server will run at: http://localhost:8000")
    print("   The browser should open automatically.")
    print("   Press Ctrl+C to stop the server.\n")

    # Start server
    try:
        subprocess.run([sys.executable, "server.py"])
    except KeyboardInterrupt:
        print("\nDemo completed!")


if __name__ == "__main__":
    run_demo()

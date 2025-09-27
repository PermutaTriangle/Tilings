#!/usr/bin/env python3
"""
Demo script for real-time TileScope visualization.
This demonstrates the live visualization of pattern "123" which will run for a long time.
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def run_realtime_demo():
    """Run the real-time visualization demo."""
    print("TileScope Real-time Visualization Demo")
    print("=====================================\n")

    print("This demo will:")
    print("1. Start the visualization server")
    print("2. Open your browser to the visualization interface")
    print("3. You can then click 'Start Real-time Search' to see live updates")
    print("4. Pattern '123' will run indefinitely - perfect for testing pause/resume")
    print("\nStarting server...")

    try:
        # Start the server
        server_process = subprocess.Popen(
            [sys.executable, "server.py", "--port", "8080"], cwd=Path(__file__).parent
        )

        print("Server started! Opening browser...")
        time.sleep(2)  # Give server time to start

        # Open browser
        webbrowser.open("http://localhost:8080")

        print("\nInstructions:")
        print("- Click 'Start Real-time Search' in the browser")
        print("- Choose pattern '123' (default) for a long-running search")
        print("- Watch nodes appear in real-time!")
        print("- Use the Pause/Resume button to control the search")
        print("- Press Ctrl+C here OR click 'Stop Server' in browser to stop")

        # Monitor server process with polling
        print("\nServer running... (monitoring for shutdown)")
        try:
            while server_process.poll() is None:
                time.sleep(1)  # Check every second if process is still alive

            # If we get here, the server process has ended
            return_code = server_process.returncode
            if return_code == 0:
                print("Server shut down successfully via 'Stop Server' button")
            else:
                print(f"Server exited with code {return_code}")

        except KeyboardInterrupt:
            print("\nReceived Ctrl+C, stopping server...")
            server_process.terminate()
            server_process.wait()  # Wait for clean shutdown

    except Exception as e:
        print(f"Error: {e}")
        if "server_process" in locals():
            server_process.terminate()
            server_process.wait()

    finally:
        print("Demo completed!")


if __name__ == "__main__":
    run_realtime_demo()

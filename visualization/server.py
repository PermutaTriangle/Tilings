#!/usr/bin/env python3
"""
Simple HTTP server for TileScope visualization.
"""
import http.server
import socketserver
import webbrowser
import os
import sys
import json
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Import our visualization classes
sys.path.insert(0, str(Path(__file__).parent))
from tilescope_visualizer import VisualizationTileScope
from tilings.tilescope import TileScopePack

# Global search instance
current_search = None
search_thread = None
server_instance = None


class TileScopeVisualizationHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for the TileScope visualization server."""

    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        super().__init__(*args, directory=str(Path(__file__).parent / "web"), **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)

        # Serve the main page
        if parsed_path.path == "/" or parsed_path.path == "/index.html":
            self.path = "/index.html"

        # Handle API endpoints
        elif parsed_path.path == "/api/data":
            self.serve_visualization_data()
            return

        # Serve static files
        super().do_GET()

    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/api/start-search":
            self.handle_start_search()
        elif self.path == "/api/pause-search":
            self.handle_pause_search()
        elif self.path == "/api/resume-search":
            self.handle_resume_search()
        elif self.path == "/api/stop-server":
            self.handle_stop_server()
        else:
            self.send_error(404, "Not Found")

    def serve_visualization_data(self):
        """Serve the latest visualization data file."""
        data_file = Path(__file__).parent / "web" / "visualization_data.json"

        if data_file.exists():
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            with open(data_file, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "Visualization data not found")

    def handle_start_search(self):
        """Handle starting a new real-time search."""
        global current_search, search_thread

        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode("utf-8"))

            pattern = request_data.get("pattern", "123")

            # Stop any existing search
            if current_search:
                current_search.pause_search()

            # Create new search instance
            pack = TileScopePack.point_placements()
            current_search = VisualizationTileScope(pattern, pack)

            # Start search in background thread
            def run_search():
                try:
                    result = current_search.start_realtime_search(
                        "web/visualization_data.json"
                    )
                    print(f"Search completed with result: {result is not None}")
                except Exception as e:
                    print(f"Search error: {e}")

            search_thread = threading.Thread(target=run_search, daemon=True)
            search_thread.start()

            # Send success response
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            response = {
                "status": "success",
                "message": f"Search started for pattern {pattern}",
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))

        except Exception as e:
            self.send_error(400, f"Error starting search: {str(e)}")

    def handle_pause_search(self):
        """Handle pausing the current search."""
        global current_search

        try:
            if current_search:
                current_search.pause_search()
                message = "Search paused"
            else:
                message = "No active search to pause"

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            response = {"status": "success", "message": message}
            self.wfile.write(json.dumps(response).encode("utf-8"))

        except Exception as e:
            self.send_error(400, f"Error pausing search: {str(e)}")

    def handle_resume_search(self):
        """Handle resuming the current search."""
        global current_search

        try:
            if current_search:
                current_search.resume_search()
                message = "Search resumed"
            else:
                message = "No active search to resume"

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            response = {"status": "success", "message": message}
            self.wfile.write(json.dumps(response).encode("utf-8"))

        except Exception as e:
            self.send_error(400, f"Error resuming search: {str(e)}")

    def handle_stop_server(self):
        """Handle stopping the server."""
        global server_instance, current_search

        try:
            # Send success response first
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            response = {"status": "success", "message": "Server shutting down..."}
            self.wfile.write(json.dumps(response).encode("utf-8"))

            # Schedule server shutdown and cleanup in a separate thread
            def shutdown_server():
                time.sleep(0.5)  # Give time for response to be sent

                print("\nPerforming comprehensive cleanup...")

                # Stop any active search
                if current_search:
                    try:
                        current_search.pause_search()
                        print("  ↳ Stopped active search")
                    except:
                        pass

                # Run the comprehensive cleanup utility
                try:
                    import subprocess

                    cleanup_script = Path(__file__).parent / "cleanup.py"
                    if cleanup_script.exists():
                        print("  ↳ Running comprehensive cleanup...")
                        subprocess.run(
                            [sys.executable, str(cleanup_script)],
                            cwd=str(Path(__file__).parent),
                        )
                    else:
                        print(
                            "  ↳ Cleanup script not found, performing basic cleanup..."
                        )
                        # Fallback to basic cleanup
                        data_files = [
                            Path(__file__).parent / "web" / "visualization_data.json",
                            Path(__file__).parent / "visualization_data.json",
                        ]
                        for data_file in data_files:
                            if data_file.exists():
                                try:
                                    data_file.unlink()
                                    print(f"    • Removed {data_file.name}")
                                except Exception as e:
                                    print(
                                        f"    • Could not remove {data_file.name}: {e}"
                                    )
                except Exception as e:
                    print(f"  ↳ Cleanup error: {e}")

                # Shutdown server
                if server_instance:
                    print("  ↳ Shutting down server...")
                    server_instance.shutdown()

                # Force kill the process to ensure complete shutdown
                print("  ↳ Terminating process...")
                os._exit(0)

            threading.Thread(target=shutdown_server, daemon=True).start()

        except Exception as e:
            self.send_error(400, f"Error stopping server: {str(e)}")

    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"[{self.address_string()}] {format % args}")


def run_server(port=8000, open_browser=True):
    """Run the visualization server."""

    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    print(f"TileScope Visualization Server")
    print(f"==============================")
    print(f"Starting server on port {port}")
    print(f"Server directory: {script_dir}")

    try:
        global server_instance
        server_instance = socketserver.TCPServer(
            ("", port), TileScopeVisualizationHandler
        )

        server_url = f"http://localhost:{port}"
        print(f"Server running at: {server_url}")
        print(f"Press Ctrl+C to stop the server")

        if open_browser:
            print(f"Opening browser...")
            webbrowser.open(server_url)

        print()
        server_instance.serve_forever()

    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Error: Port {port} is already in use")
            print("Try a different port with: python server.py --port 8080")
        else:
            print(f"Error starting server: {e}")
        sys.exit(1)
    finally:
        # Cleanup server instance
        if server_instance:
            try:
                server_instance.server_close()
            except:
                pass


def main():
    """Main function with command line argument parsing."""
    import argparse

    parser = argparse.ArgumentParser(description="TileScope Visualization Server")
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Do not automatically open browser"
    )

    args = parser.parse_args()

    run_server(port=args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()

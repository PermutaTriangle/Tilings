#!/usr/bin/env python3
"""
Cleanup utility for TileScope visualization servers.
Use this to clean up any hanging server processes and free ports.
"""
import subprocess
import sys
import time
import os


def cleanup_servers():
    """Clean up any running TileScope server processes."""
    print("🧹 Cleaning up TileScope visualization servers...")

    try:
        # Kill any processes using our target ports
        print("  ↳ Killing processes using target ports...")
        ports_to_clean = [8080, 8085, 8086, 8087, 8088, 8089, 8090]
        for port in ports_to_clean:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split("\n")
                for pid in pids:
                    if pid.strip():
                        try:
                            subprocess.run(
                                ["kill", "-9", pid.strip()],
                                capture_output=True,
                                text=True,
                            )
                            print(
                                f"    • Killed process {pid.strip()} using port {port}"
                            )
                        except:
                            pass

        # Kill any server.py processes
        print("  ↳ Killing server.py processes...")
        result = subprocess.run(
            [
                "bash",
                "-c",
                "ps aux | grep \"server.py\" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null",
            ],
            capture_output=True,
            text=True,
        )

        # Kill any demo_realtime.py processes (except current one)
        print("  ↳ Killing demo_realtime.py processes...")
        current_pid = str(os.getpid())
        result = subprocess.run(
            [
                "bash",
                "-c",
                "ps aux | grep \"demo_realtime.py\" | grep -v grep | awk '{print $2}'",
            ],
            capture_output=True,
            text=True,
        )

        if result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            for pid in pids:
                if pid.strip() and pid.strip() != current_pid:
                    try:
                        subprocess.run(
                            ["kill", "-9", pid.strip()], capture_output=True, text=True
                        )
                        print(f"    • Killed demo process {pid.strip()}")
                    except:
                        pass

        # Wait a moment for processes to die
        time.sleep(1)

        # Clean up visualization data files
        print("  ↳ Cleaning up visualization data files...")
        data_files = ["web/visualization_data.json", "visualization_data.json"]

        for data_file in data_files:
            try:
                if os.path.exists(data_file):
                    os.remove(data_file)
                    print(f"    • Removed {data_file}")
            except Exception as e:
                print(f"    • Could not remove {data_file}: {e}")

        # Check if common ports are free
        ports_to_check = [8080, 8085, 8086, 8087, 8088, 8089, 8090]
        free_ports = []
        occupied_ports = []

        for port in ports_to_check:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], capture_output=True, text=True
            )
            if result.returncode == 0:
                occupied_ports.append(port)
            else:
                free_ports.append(port)

        print(f"  ↳ Free ports: {free_ports}")
        if occupied_ports:
            print(f"  ↳ Still occupied ports: {occupied_ports}")
            print("    (These might be used by other applications)")

        print("✅ Cleanup complete!")

        if 8080 in free_ports:
            print("🎯 Port 8080 is free - demo_realtime.py should work now!")
        else:
            print(
                "⚠️  Port 8080 is still occupied - you may need to manually kill that process"
            )

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cleanup_servers()

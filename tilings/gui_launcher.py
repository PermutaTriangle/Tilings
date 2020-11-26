import re
import subprocess
import sys
from importlib.util import find_spec
from typing import Optional, Tuple

try:
    if tuple(
        map(lambda z: int(re.sub("[^0-9]", "", z)), sys.version.split()[0].split("."))
    ) < (3, 8, 0):
        from importlib_metadata import version  # pylint: disable=import-error
    else:
        from importlib.metadata import version  # pylint: disable=ungrouped-imports
except ImportError:

    def _fake_version(_str: str) -> str:

        print("=== If you are using older version of python than 3.8 ===")
        print(f"To use for {sys.executable} you need importlib-metadata.")
        print(f"{sys.executable} -m pip install importlib-metadata", flush=True)
        return "0.0.0"

    version = _fake_version


_MIN_VERSION = (0, 2, 1)
_NOT_FOUND, _OLD_VERSION, _SUCCESS = range(3)


def in_path_version(interpreter: str) -> Optional[Tuple[int, ...]]:
    try:
        return next(
            (
                tuple(map(int, line.split(" ")[1].split(".")))
                for line in subprocess.run(
                    [
                        interpreter,
                        "-m",
                        "pip",
                        "show",
                        "tilingsgui",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
                .stdout.decode("utf-8")
                .splitlines()
                if line.startswith("Version")
            ),
            None,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def search_path_interpreter(interpreter) -> Tuple[int, str]:
    vers = in_path_version(interpreter)
    if vers is None:
        return _NOT_FOUND, interpreter
    if vers < _MIN_VERSION:
        return _OLD_VERSION, interpreter
    return _SUCCESS, interpreter


def search_current_interpreter() -> Tuple[int, str]:
    spec = find_spec("tilingsgui")
    if spec is None or spec.loader is None:
        return _NOT_FOUND, sys.executable
    if tuple(map(int, version("tilingsgui").split("."))) < _MIN_VERSION:
        return _OLD_VERSION, sys.executable
    return _SUCCESS, sys.executable


def look_for_tilingsgui() -> Tuple[int, str]:
    best_status = -1
    for search in (
        search_current_interpreter,
        lambda: search_path_interpreter("python"),
        lambda: search_path_interpreter("python3"),
        lambda: search_path_interpreter("pypy3"),
        lambda: search_path_interpreter("python3.8"),
        lambda: search_path_interpreter("python3.7"),
        lambda: search_path_interpreter("python3.6"),
        lambda: search_path_interpreter("python3.9"),
    ):
        status, interpreter = search()
        best_status = max(best_status, status)
        if best_status == _SUCCESS:
            break
    return best_status, interpreter


def run_gui(tiling_json: str) -> None:
    status, interpreter = look_for_tilingsgui()
    if status == _SUCCESS:
        subprocess.run(
            [interpreter, "-m", "tilingsgui.main", "-j", tiling_json], check=True
        )
    elif status == _OLD_VERSION:
        print("Found tilingsgui but version is outdated.")
        print("your_python_interpreter -m pip install tilingsgui --upgrade", flush=True)
    else:
        print("Did not find tilingsgui.")
        print("your_python_interpreter -m pip install tilingsgui", flush=True)

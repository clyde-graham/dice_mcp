"""
check_env.py — Environment check for dice-mcp

Run with: uv run python check_env.py

Verifies that all required dependencies are importable and the
Python version meets the minimum requirement.
"""

import sys

REQUIRED_PYTHON = (3, 10)

def check_python_version():
    v = sys.version_info[:2]
    if v < REQUIRED_PYTHON:
        print(f"FAIL  Python {v[0]}.{v[1]} — requires {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+")
        return False
    print(f"OK    Python {v[0]}.{v[1]}")
    return True

def check_import(module, package=None):
    label = package or module
    try:
        __import__(module)
        print(f"OK    {label}")
        return True
    except ImportError as e:
        print(f"FAIL  {label} — {e}")
        return False

def main():
    print("dice-mcp environment check\n")
    results = [
        check_python_version(),
        check_import("d20"),
        check_import("mcp", "mcp[cli]"),
    ]
    print()
    if all(results):
        print("All checks passed. Ready to run.")
    else:
        print("One or more checks failed. Run: uv sync")
        sys.exit(1)

if __name__ == "__main__":
    main()

# mypy: ignore-errors
import argparse
import importlib.metadata
import tomllib

import toml


def increment_patch_version(version: str) -> str:
    major, minor, patch = map(int, version.split("."))
    return f"{major}.{minor}.{patch + 1}"

# Set up argument parser
parser = argparse.ArgumentParser(description="Increment patch version or set a specific version.")
parser.add_argument('--version', type=str, help='Set a specific version (e.g., 1.2.3).')

# Parse arguments
args = parser.parse_args()
if args.version:
    if not all(x.isdigit() for x in args.version.split(".")):
        print("Version must be in the form of x.y.z, where x, y, and z are integers.")
        exit(1)

try:
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        version = data["tool"]["poetry"]["version"]
    data["tool"]["poetry"]["version"] = args.version or increment_patch_version(version)
    with open("pyproject.toml", "w") as f:
        toml.dump(data, f)
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        version = data["tool"]["poetry"]["version"]
        print(version)
except importlib.metadata.PackageNotFoundError:
    print("Package not found.")

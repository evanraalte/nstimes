import importlib.metadata
import tomllib
import toml
def increment_patch_version(version: str) -> str:
    major, minor, patch = map(int, version.split('.'))
    return f"{major}.{minor}.{patch + 1}"

try:
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        version = data["tool"]["poetry"]["version"]
    data["tool"]["poetry"]["version"] = increment_patch_version(version)
    with open("pyproject.toml", "w") as f:
        toml.dump(data, f)
    print(f"v{version}")
except importlib.metadata.PackageNotFoundError:
    print("Package not found.")

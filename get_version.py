import importlib.metadata

try:
    version = importlib.metadata.version("nstimes")
    print(f"v{version}")
except importlib.metadata.PackageNotFoundError:
    print("Package not found.")

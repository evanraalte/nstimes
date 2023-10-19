#!/bin/bash

poetry install
VERSION=$(python get_version.py)

if [ "$VERSION" = "Package not found." ]; then
    echo "Tagging aborted. Package not found."
else
    echo "Tagging to $VERSION"

    if git rev-parse "$VERSION" >/dev/null 2>&1; then
        echo "Tag '$VERSION' already exists. Aborting."
    else
        echo "tagging.."
        git tag "$VERSION"
        git push --tags
    fi
fi

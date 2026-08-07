#!/bin/sh
set -eu

# Run verification tools in order, stopping on first failure
# Uses Ruff, mypy, and pytest as configured in the project

echo "Running Ruff..."
ruff check . || exit 1

echo "Running mypy..."
python -m mypy . || exit 1

echo "Running pytest..."
python -m pytest . || exit 1

echo "All verification checks passed!"

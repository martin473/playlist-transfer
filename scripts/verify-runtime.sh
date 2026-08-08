#!/bin/sh
set -eu

# Run verification tools in order, stopping on first failure
# Uses Ruff, mypy, and pytest as configured in the project

# Navigate to the runtime directory where the Python project lives
cd "$(dirname "$0")/.." || exit 1
cd runtime || exit 1

# Use the virtual environment if it exists
if [ -d ".venv/bin" ]; then
    PATH=".venv/bin:$PATH"
    export PATH
fi

echo "Running Ruff..."
ruff check . || exit 1

echo "Running mypy..."
python -m mypy . || exit 1

echo "Running pytest..."
python -m pytest . || exit 1

echo "All verification checks passed!"

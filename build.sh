#!/bin/bash
set -e

# Render is selecting Python 3.14.3 despite runtime.txt
# This build script fails to force Render to read runtime.txt

echo "Current Python version:"
python --version
python3 --version

# Check if we have python3.12
if command -v python3.12 &> /dev/null; then
    echo "Using python3.12"
    python3.12 --version
    python3.12 -m pip install --no-cache-dir -e .
else
    # Fall back to system python, but it must be 3.12 or 3.13
    PY_VERSION=$(python --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    if [[ "$PY_VERSION" != "3.12" ]] && [[ "$PY_VERSION" != "3.13" ]]; then
        echo "ERROR: Python $PY_VERSION is not supported. Need 3.12 or 3.13"
        exit 1
    fi
    python -m pip install --no-cache-dir -e .
fi


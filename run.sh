#!/bin/bash

# Loggin Genie - Convenience wrapper script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python executable path
PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"

# Check if virtual environment exists
if [ ! -f "$PYTHON_BIN" ]; then
    echo "Virtual environment not found. Setting up..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    echo "Installing dependencies..."
    "$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
    echo "Setup complete!"
fi

# Run the main script with all arguments passed through
"$PYTHON_BIN" "$SCRIPT_DIR/loggin_genie.py" "$@"

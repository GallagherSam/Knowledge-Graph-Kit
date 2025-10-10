#!/bin/bash

# Default config file path
CONFIG_FILE="config.json"

# Check if a config file path is provided as an argument
if [ -n "$1" ]; then
    CONFIG_FILE="$1"
fi

PYTHONPATH=. uv run app.main -- --config "$CONFIG_FILE"
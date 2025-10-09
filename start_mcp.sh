#!/bin/bash

PYTHONPATH=. uv run fastmcp run app/main.py:mcp --transport http --port 8000
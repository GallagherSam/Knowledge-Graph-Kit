# Project Architecture: Current State

This document outlines the refactored architecture of the Notes Graph MCP application as of October 7, 2025. The primary goal of this refactor was to resolve circular dependencies and create a clear separation of concerns between the API layer and the business logic.

## 1. Core Concept: Centralized Tool Registration

The main architectural pattern is the centralization of all tool definitions (`@mcp.tool`) within a single file, `app/main.py`. This file acts as the sole entry point for the `FastMCP` server and is responsible for exposing the application's capabilities.

Business logic, which was previously mixed with the tool definitions, has been moved into dedicated "service" modules.

## 2. Directory & File Structure

The key components of the application are now organized as follows:

*   `app/main.py`:
    *   Initializes the `FastMCP` instance (`mcp`).
    *   Imports all service modules from `app/tools`.
    *   Defines all public-facing tools (e.g., `create_task`, `get_notes`).
    *   Each tool function is a simple wrapper that calls the corresponding function in a service module.
    *   Contains the main execution block to run the server.

*   `app/tools/*.py`: (e.g., `task.py`, `note.py`)
    *   These are now considered **service modules**.
    *   They contain the core business logic for each domain (Tasks, Notes, etc.).
    *   They **do not** import the `mcp` instance or have any `@mcp.tool` decorators.
    *   They are imported by `app/main.py`.

*   `app/crud.py`:
    *   The single source of truth for data manipulation.
    *   Contains generic functions like `create_node`, `get_nodes`, `update_node`, and `create_edge`.
    *   It interacts directly with the state manager.

*   `app/state.py`:
    *   Manages the physical reading and writing of data to the JSON files in the `/data` directory. No other part of the app should interact with the filesystem directly.

*   `app/models.py`:
    *   Defines the Pydantic data models (`Node`, `Edge`, `TaskProperties`, etc.) used for validation and data consistency throughout the application.

*   `start_mcp.sh`:
    *   The script used to launch the server. It correctly points to the `mcp` instance within `app/main.py`.

*   `test.py`:
    *   A client script in the root directory used to make live API calls to the running server, verifying its functionality.

## 3. Execution Flow (Example: `create_task`)

1.  A client (e.g., `test.py`) sends a request to the `create_task` tool endpoint.
2.  The `FastMCP` server, defined in `app/main.py`, receives the request.
3.  The `@mcp.tool`-decorated `create_task` function in `app/main.py` is executed.
4.  This function immediately calls `task_service.create_task(...)`, passing along the arguments.
5.  The `create_task` function in `app/tools/task.py` executes the business logic:
    *   It creates and validates a `TaskProperties` Pydantic model.
    *   It calls `crud.create_node()` with the node type and properties.
6.  The `create_node` function in `app/crud.py` handles the data persistence:
    *   It reads the current nodes from `data/nodes.json` via `state_manager`.
    *   It appends the new task node.
    *   It writes the updated list of nodes back to the file.
7.  The newly created node is returned up the call stack and sent back to the client.

This clear, unidirectional flow prevents import errors and makes the system easier to understand and maintain.

# Implementation Plan: Notes Graph Application

This document outlines the steps to build the Notes Graph application based on the project specification. We will prioritize simplicity by using JSON files for data storage initially, with the goal of migrating to SQLite later.

## Phase 1: Project Scaffolding and Data Modeling

**Objective:** Set up the project structure and define the core data models.

1.  **Create Directory Structure:**
    *   Create a `data/` directory to store our JSON database files.
    *   Create the following empty Python files to establish the architecture:
        *   `src/__init__.py`
        *   `src/models.py`
        *   `src/database.py`
        *   `src/crud.py`

2.  **Define Pydantic Models (`src/models.py`):**
    *   Implement the Pydantic models for all node types (`Task`, `Note`, `Person`, `Project`) and the `Edge` type as specified in `specs/app_spec.md`.
    *   These models will be used for data validation in the API and for serialization.

## Phase 2: JSON Database and CRUD Logic

**Objective:** Implement the logic for interacting with the JSON data files.

1.  **JSON Database Module (`src/database.py`):**
    *   Define the path to the data files: `DATA_DIR` and `NODES_FILE`, `EDGES_FILE`.
    *   Create a `Database` class or a set of functions to handle file I/O.
    *   **Functions:**
        *   `_initialize_database()`: Creates the `data/` directory and empty `nodes.json` and `edges.json` files if they don't exist.
        *   `read_nodes()`: Reads and returns the list of nodes from `nodes.json`.
        *   `write_nodes(nodes)`: Writes the list of nodes to `nodes.json`.
        *   `read_edges()`: Reads and returns the list of edges from `edges.json`.
        *   `write_edges(edges)`: Writes the list of edges to `edges.json`.

2.  **CRUD Operations Module (`src/crud.py`):**
    *   This module will contain the business logic for manipulating the data. It will use `database.py` for persistence.
    *   **Node Functions:**
        *   `create_node(node_type, properties)`:
            *   Generates a unique ID (e.g., using `uuid`).
            *   Validates the incoming `properties` against the corresponding Pydantic model from `models.py`.
            *   Appends the new node to the list from `database.read_nodes()`.
            *   Writes the updated list back using `database.write_nodes()`.
            *   Returns the created node.
        *   `get_nodes(type, **kwargs)`:
            *   Reads all nodes.
            *   Filters nodes based on the provided `type` and any other property filters (e.g., `status='todo'`).
            *   Returns the list of matching nodes.
        *   `update_node(node_id, properties)`:
            *   Finds the node with the matching `node_id`.
            *   Updates its properties with the new data.
            *   Validates the updated data.
            *   Writes the entire list of nodes back to the file.
            *   Returns the updated node.
    *   **Edge Functions:**
        *   `create_edge(source_id, label, target_id)`:
            *   Creates a new `Edge` object.
            *   Appends it to the list from `database.read_edges()`.
            *   Writes the updated list back using `database.write_edges()`.
            *   Returns the created edge.

## Phase 3: API Endpoint Implementation

**Objective:** Expose the CRUD functionality through a `FastMCP` server.

1.  **Refactor API Server (`src/main.py`):**
    *   Remove the old `roll_dice`, `greet`, and `say_bye` tools.
    *   Import the functions from `crud.py` and the models from `models.py`.
    *   Implement the API endpoints as specified:
        *   **`POST /nodes` -> `create_node_tool`**:
            *   Accepts a node `type` and `properties`.
            *   Calls `crud.create_node()` and returns the result.
        *   **`GET /nodes` -> `get_nodes_resource`**:
            *   Uses FastMCP's resource capabilities to handle query parameters.
            *   Calls `crud.get_nodes()` with the filters and returns the results.
        *   **`PUT /nodes/{node_id}` -> `update_node_tool`**:
            *   Accepts a `node_id` and `properties`.
            *   Calls `crud.update_node()` and returns the result.
        *   **`POST /edges` -> `create_edge_tool`**:
            *   Accepts `source_id`, `label`, and `target_id`.
            *   Calls `crud.create_edge()` and returns the result.
    *   Ensure the server is runnable via `if __name__ == "__main__":`.

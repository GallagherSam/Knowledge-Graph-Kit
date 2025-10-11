# Knowledge Graph Kit

Knowledge Graph Kit is a Python-based framework for building AI agents that can reason about and interact with a knowledge graph. It provides a flexible and extensible toolkit for creating, managing, and querying interconnected data, making it easy to build applications that require complex data relationships and semantic search capabilities.

## Core Concepts

The kit is built around a simple yet powerful knowledge graph model:

*   **Nodes:** Represent entities such as tasks, notes, people, or projects. Each node has a specific type and a set of properties.
*   **Edges:** Define the relationships between nodes, such as `part_of`, `mentions`, or `related_to`.

This structure allows you to create a rich, interconnected web of information that your AI agents can traverse and query.

## Features

*   **Flexible Node Types:** Pre-built schemas for Tasks, Notes, Persons, and Projects.
*   **Extensible:** Easily add new node and edge types to fit your specific domain.
*   **Semantic Search:** Find conceptually related nodes even without keyword matches.
*   **Full-Text Search:** Powerful keyword-based search across all nodes.
*   **Tagging System:** Organize and filter nodes with a flexible tagging system.
*   **FastAPI Integration:** Exposes a clean, tool-based API for your AI agents.

## Getting Started

### Prerequisites

*   Python 3.11+
*   `uv` (or `pip`) for package management

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/knowledge-graph-kit.git
    cd knowledge-graph-kit
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    uv venv
    uv pip install -e ".[dev]"
    ```

3.  **Run the server:**
    ```bash
    python app/main.py
    ```
    The API server will be running at `http://0.0.0.0:8000`.

## Gemini CLI Integration

To use the Knowledge Graph Kit as a tool provider for the Gemini CLI, you need to run it as a Managed Component Proxy (MCP) server.

1.  **Start the MCP server:**
    A convenience script is provided to run the server in this mode.
    ```bash
    ./scripts/start_mcp.sh
    ```

2.  **Configure Gemini CLI:**
    Add the following configuration to your `~/.gemini/settings.json` file. This tells the Gemini CLI where to find the Knowledge Graph Kit's tools.

    ```json
    {
      "mcpServers": {
        "Knowledge Graph Kit": {
          "httpUrl": "http://localhost:8000/mcp"
        }
      }
    }
    ```
    *Note: If you are running the Gemini CLI in a different environment (like a Docker container), replace `localhost` with the appropriate IP address of the machine running the server.*

    Once configured, you can interact with your knowledge graph directly from the Gemini CLI.

## API & Tools

The Knowledge Graph Kit exposes a comprehensive set of tools for interacting with the knowledge graph. These tools are designed to be used by an AI agent to perform CRUD operations on nodes and edges, as well as to search and discover relationships.

For a complete reference of all available tools and their parameters, please see the [LLM Operating Manual](./INSTRUCTIONS.md).

### Example Workflow

Here's a simple example of how an agent might use the tools to create a project, add a task, and link them together:

1.  **Create a project:**
    ```python
    create_project(name='Website Redesign', description='A project to redesign the company website.')
    ```

2.  **Create a task:**
    ```python
    create_task(description='Gather requirements')
    ```

3.  **Link the task to the project:**
    ```python
    # First, find the project and task IDs
    project = get_projects(name='Website Redesign')[0]
    task = get_tasks(description='Gather requirements')[0]

    # Create the edge
    create_edge(source_id=task['id'], label='part_of', target_id=project['id'])
    ```

## Development

### Adding a New Node Type

To add a new type of node to the knowledge graph, you'll need to:

1.  **Define a Pydantic model** for the node's properties in `app/models.py`.
2.  **Create a new service module** in the `app/tools/` directory (e.g., `app/tools/document.py`).
3.  **Implement the CRUD functions** for your new node type in the service module.
4.  **Expose the functions as tools** in `app/main.py` using the `@mcp.tool` decorator.

By following this pattern, you can easily extend the Knowledge Graph Kit to support any kind of interconnected data your application requires.

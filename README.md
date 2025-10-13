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
*   **Graph Traversal:** Explore connections between nodes up to a specified depth.
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

## Configuration

The application can be configured via a JSON file. By default, it looks for a `config.json` file in the root of the project. You can also specify a different configuration file when starting the application.

### Usage

To run the application with the default configuration, use the following command:

```bash
./start_mcp.sh
```

To use a custom configuration file, pass the path as an argument:

```bash
./start_mcp.sh /path/to/your/config.json
```

### Configuration Options

The following options are available for configuration:

| Key | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `SQLALCHEMY_DATABASE_URL` | string | The connection string for the SQLite database. | `sqlite:///./graph.db` |
| `CHROMA_DATA_PATH` | string | The directory to store ChromaDB data. | `chroma_data` |
| `EMBEDDING_MODEL` | string | The name of the sentence-transformer model to use for embeddings. | `all-MiniLM-L6-v2` |
| `HOST` | string | The host address for the MCP server. | `0.0.0.0` |
| `PORT` | integer | The port for the MCP server. | `8000` |

An example configuration file, `config.json`, is provided in the root of the repository.

## Development

### Adding a New Node Type

To add a new type of node to the knowledge graph (e.g., "Document"), follow the established class-based pattern:

1.  **Define a Pydantic model** for the node's properties in `app/models.py`. This defines the data schema for your new node type.
2.  **Create a new tool class** in the `app/tools/` directory (e.g., `app/tools/document.py` would contain a `Documents` class).
3.  **Implement the tool logic** inside your new class. The constructor should accept `mcp_instance` and a `provider`, and it should register its public methods as tools with `mcp_instance.tool()`. Use the `provider` to access the database and vector store.
4.  **Register the new tool class** by importing it and instantiating it in `app/tools/tool.py` within the `Tools` class constructor.

By following this pattern, you can easily extend the Knowledge Graph Kit to support any kind of interconnected data your application requires.


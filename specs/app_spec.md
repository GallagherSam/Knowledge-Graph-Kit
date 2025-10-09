# Project Specification: Notes Interface Application

## 1. Objective

To develop a dedicated application that acts as an intelligent, autonomous interface between a user and a personal knowledge base. This application will replace the current manual, conversational workflow with a structured, command-driven system that manages a knowledge graph of notes, tasks, projects, and people.

## 2. Background & Problem Statement

The current workflow, which relies on the Gemini CLI and direct manipulation of markdown files, has several friction points that hinder efficiency and scalability:

*   **Manual Session Initialization:** Each session requires manually providing context (the operating manual, directory structure).
*   **Context Blindness:** The LLM lacks persistent awareness of the file system, leading to inconsistent state and redundant file creation.
*   **Destructive Edits:** The default file writing behavior can lead to accidental data loss by overwriting content instead of appending.
*   **Manual Task Migration:** Incomplete tasks must be manually carried forward each day.
*   **Tedious Approvals:** Every file system modification requires explicit user confirmation, slowing down the workflow.

This project aims to solve these issues by creating a trusted application layer (a Managed Component) that handles the underlying data management, allowing for a seamless and autonomous user experience.

## 3. Core Concept: The Knowledge Graph

The application will be built around a knowledge graph data model. This provides a flexible and powerful way to represent and connect information.

*   **Nodes:** The primary entities in the system.
    *   **Tasks:** Actionable items.
    *   **Notes:** Unstructured text and information.
    *   **People:** Individuals.
    *   **Projects:** High-level initiatives.
*   **Edges:** The relationships that connect the nodes, giving the data context and structure (e.g., a Task is `part_of` a Project; a Note `mentions` a Person).

## 4. System Architecture

The application will be a server-side application that exposes a set of tools (API endpoints) for an LLM to consume.

*   **Backend Framework:** **FastAPI (Python)** for its speed, automatic documentation, and Pydantic integration.
*   **Database:** **SQLite** for its simplicity, serverless nature, and single-file portability.
*   **Data Validation:** **Pydantic** to define and enforce the schema for our data models.

## 5. Data Model Specification

### Node Types

| Node | Properties |
| :--- | :--- |
| **Task** | `id`, `description` (text), `status` (e.g., 'todo', 'done'), `created_at`, `due_date` (optional) |
| **Note** | `id`, `title` (text), `content` (markdown), `created_at`, `modified_at` |
| **Person** | `id`, `name` (text), `metadata` (JSON for contact info, role, etc.) |
| **Project**| `id`, `name` (text), `description` (text), `status` (e.g., 'active', 'archived') |

### Edge Types

| Source(s) | Relationship | Target(s) | Description |
| :--- | :--- | :--- | :--- |
| Task | `part_of` | Project | A task is a component of a project. |
| Project | `subproject_of`| Project | A project is part of a larger project. |
| Note | `documents` | Project | A note's primary purpose is to describe a project. |
| Note, Task, Project | `mentions` | Person | An entity references a person. |
| Note | `related_to` | Note, Task | An entity is conceptually linked to another. |

## 6. API Specification (MCP Tools)

The server will expose the following primary endpoints for the LLM:

*   **`POST /nodes`**: A generic endpoint to create any type of node.
    *   *Body:* `{ "type": "Task", "properties": { "description": "New task" } }`
*   **`GET /nodes`**: A powerful query endpoint to find nodes.
    *   *Query Params:* `?type=Task&status=todo&project=Notes App`
*   **`PUT /nodes/{node_id}`**: Updates the properties of a specific node.
    *   *Body:* `{ "properties": { "status": "done" } }`
*   **`POST /edges`**: Creates a relationship between two nodes.
    *   *Body:* `{ "source_id": "task_123", "label": "part_of", "target_id": "project_456" }`

## 7. Functional Requirements

*   **Automated Session Management:** The application must automatically load context for the LLM on startup.
*   **Command-Driven Interface:** The primary user interaction will be through slash commands (e.g., `/task`, `/note`).
*   **Automated Task Management:** The system will automatically manage the lifecycle of tasks, including carrying over incomplete tasks.
*   **Safe File Operations:** The application logic will enforce append-only operations by default to prevent data loss.
*   **Autonomous Operation:** The application will not require user confirmation for file system or database modifications.

## 8. Future Enhancements

*   A simple web UI to display dynamic views of the knowledge graph (e.g., a dashboard of all open tasks for a project).
*   Integration with local LLMs (e.g., Ollama) for offline capability.
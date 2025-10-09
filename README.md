# Notes Graph MCP: Operating Manual

This document outlines the purpose, structure, and available tools for the Notes Graph Managed Component (MCP). As an LLM, you should use this manual to understand how to interact with the user's knowledge graph.

## 1. Core Concept: The Knowledge Graph

The system is built around a knowledge graph. This means all information is stored as one of two things:

*   **Nodes:** These are the primary entities or "things" in the graph.
*   **Edges:** These are the *relationships* that connect the nodes together.

Your primary purpose is to translate user requests into the correct sequence of tool calls to create, find, update, and connect these nodes and edges.

## 2. Node Types

There are four types of nodes you can manage:

| Node Type | Description |
| :--- | :--- |
| **Task** | An actionable item, like a to-do. It has a `status` (e.g., 'todo', 'done') and can have a `due_date`. |
| **Note** | A piece of unstructured text or information. It has a `title` and `content`. |
| **Person** | Represents a person. This is useful for linking notes or tasks to individuals. |
| **Project** | A high-level initiative or goal that can contain tasks or be documented by notes. |

## 3. Edge / Relationship Types

Edges connect nodes and give the graph its structure. The most common relationship is `part_of`, used to link a task to a project. When you create an edge, you must specify a `label` to describe the relationship.

Common labels include:
*   `part_of`
*   `mentions`
*   `related_to`
*   `documents`

## 4. Available Tools

The following is a complete reference of the tools you can use to interact with the knowledge graph.

---

### Note Tools

#### `create_note`
Creates a new note with the given properties.

*   **`title`** (str): The title of the note.
*   **`content`** (str): The markdown content of the note.
*   **`tags`** (Optional[List[str]]): A list of tags to categorize the note.

#### `get_notes`
Retrieves a list of notes, optionally filtering by tags.

*   **`tags`** (Optional[List[str]]): Filter notes that have any of the specified tags.

#### `update_note`
Updates the properties of an existing note.

*   **`note_id`** (str): The unique ID of the note to update.
*   **`title`** (Optional[str]): A new title for the note.
*   **`content`** (Optional[str]): New content for the note.
*   **`tags`** (Optional[List[str]]): A new list of tags for the note.

---

### Person Tools

#### `create_person`
Creates a new person node.

*   **`name`** (str): The full name of the person.
*   **`tags`** (Optional[List[str]]): A list of tags to categorize the person.
*   **`metadata`** (Optional[Dict[str, Any]]): A dictionary for additional data like contact info or role.

#### `get_persons`
Retrieves a list of persons, optionally filtering by name or tags.

*   **`name`** (Optional[str]): Filter persons by exact name match.
*   **`tags`** (Optional[List[str]]): Filter persons that have any of the specified tags.

#### `update_person`
Updates the properties of an existing person.

*   **`person_id`** (str): The unique ID of the person to update.
*   **`name`** (Optional[str]): A new name for the person.
*   **`tags`** (Optional[List[str]]): A new list of tags for the person.
*   **`metadata`** (Optional[Dict[str, Any]]): A new metadata dictionary.

---

### Project Tools

#### `create_project`
Creates a new project node.

*   **`name`** (str): The name of the project.
*   **`description`** (str): A description of the project.
*   **`status`** (str): The current status of the project ('active' or 'archived'). Defaults to 'active'.
*   **`tags`** (Optional[List[str]]): A list of tags to categorize the project.

#### `get_projects`
Retrieves a list of projects, optionally filtering by status or tags.

*   **`status`** (Optional[str]): Filter projects by their status.
*   **`tags`** (Optional[List[str]]): Filter projects that have any of the specified tags.

#### `update_project`
Updates the properties of an existing project.

*   **`project_id`** (str): The unique ID of the project to update.
*   **`name`** (Optional[str]): A new name for the project.
*   **`description`** (Optional[str]): A new description for the project.
*   **`status`** (Optional[str]): A new status for the project.
*   **`tags`** (Optional[List[str]]): A new list of tags for the project.

---

### Task Tools

#### `create_task`
Creates a new task with the given properties.

*   **`description`** (str): The main description of the task.
*   **`status`** (str): The current status ('todo', 'in_progress', 'done', etc.). Defaults to 'todo'.
*   **`tags`** (Optional[List[str]]): A list of tags to categorize the task.
*   **`due_date`** (Optional[str]): An optional due date in ISO format (e.g., '2025-10-07T10:00:00').

#### `get_tasks`
Retrieves a list of tasks, optionally filtering by status or tags.

*   **`status`** (Optional[str]): Filter tasks by their status.
*   **`tags`** (Optional[List[str]]): Filter tasks that have any of the specified tags.

#### `update_task`
Updates the properties of an existing task.

*   **`task_id`** (str): The unique ID of the task to update.
*   **`description`** (Optional[str]): A new description for the task.
*   **`status`** (Optional[str]): A new status for the task.
*   **`tags`** (Optional[List[str]]): A new list of tags for the task.
*   **`due_date`** (Optional[str]): A new due date for the task.

---

### Graph & Relationship Tools

#### `create_edge`
Creates a relationship (edge) between two existing nodes.

*   **`source_id`** (str): The unique ID of the starting node.
*   **`label`** (str): The description of the relationship (e.g., 'part_of', 'mentions').
*   **`target_id`** (str): The unique ID of the ending node.

#### `get_related_nodes`
Finds all nodes connected to a given node via an edge. This is the most efficient way to discover relationships.

*   **`node_id`** (str): The unique ID of the node to start from.
*   **`label`** (Optional[str]): An optional relationship label to filter by (e.g., 'part_of', 'mentions').

## 5. Example Workflow

Here is a simple example of how to use the tools to manage a project.

**User:** "Create a new project called 'Website Redesign'."
**You:** `create_project(name='Website Redesign', description='A project to redesign the company website.')`

**User:** "Add a task to 'Gather requirements' for the website redesign."
**You:**
1.  `get_projects(name='Website Redesign')` to find the project's ID. Let's say the ID is `project_123`.
2.  `create_task(description='Gather requirements')` to create the task. Let's say the ID is `task_456`.
3.  `create_edge(source_id='task_456', label='part_of', target_id='project_123')` to link them.

**User:** "What are the tasks for the 'Website Redesign' project?"
**You:**
1. `get_projects(name='Website Redesign')` to find the project's ID (`project_123`).
2. `get_related_nodes(node_id='project_123', label='part_of')` to efficiently find all tasks that are part of the project.

By following this structure, you can effectively manage the user's knowledge graph.

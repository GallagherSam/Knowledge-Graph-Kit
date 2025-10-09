from typing import List, Optional, Dict, Any
from fastmcp import FastMCP

# Import the service modules that contain the business logic
from app.tools import note as note_service
from app.tools import person as person_service
from app.tools import project as project_service
from app.tools import shared as shared_service
from app.tools import task as task_service

# This is the central FastMCP application instance.
mcp = FastMCP(
    name="Notes Graph MCP",
    instructions="You are an agent managing a knowledge graph. Use the available tools to create, retrieve, update, and connect nodes (tasks, notes, people, projects) to fulfill user requests."
)

# --- Note Tools ---

@mcp.tool
def create_note(
    title: str,
    content: str,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Creates a new note with the given properties.

    Args:
        title: The title of the note.
        content: The markdown content of the note.
        tags: A list of tags to categorize the note.

    Returns:
        A dictionary representing the newly created note node.
    """
    return note_service.create_note(title=title, content=content, tags=tags)

@mcp.tool
def get_notes(
    tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of notes, optionally filtering by tags.

    Args:
        tags: Filter notes that have any of the specified tags.

    Returns:
        A list of note nodes that match the filter criteria.
    """
    return note_service.get_notes(tags=tags)

@mcp.tool
def update_note(
    note_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Updates the properties of an existing note.

    Args:
        note_id: The unique ID of the note to update.
        title: A new title for the note.
        content: New content for the note.
        tags: A new list of tags for the note.

    Returns:
        The updated note node.
    """
    return note_service.update_note(note_id=note_id, title=title, content=content, tags=tags)

# --- Person Tools ---

@mcp.tool
def create_person(
    name: str,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Creates a new person node.

    Args:
        name: The full name of the person.
        tags: A list of tags to categorize the person.
        metadata: A dictionary for additional data like contact info or role.

    Returns:
        A dictionary representing the newly created person node.
    """
    return person_service.create_person(name=name, tags=tags, metadata=metadata)

@mcp.tool
def get_persons(
    name: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of persons, optionally filtering by name or tags.

    Args:
        name: Filter persons by exact name match.
        tags: Filter persons that have any of the specified tags.

    Returns:
        A list of person nodes that match the filter criteria.
    """
    return person_service.get_persons(name=name, tags=tags)

@mcp.tool
def update_person(
    person_id: str,
    name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Updates the properties of an existing person.

    Args:
        person_id: The unique ID of the person to update.
        name: A new name for the person.
        tags: A new list of tags for the person.
        metadata: A new metadata dictionary.

    Returns:
        The updated person node.
    """
    return person_service.update_person(person_id=person_id, name=name, tags=tags, metadata=metadata)

# --- Project Tools ---

@mcp.tool
def create_project(
    name: str,
    description: str,
    status: str = 'active',
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Creates a new project node.

    Args:
        name: The name of the project.
        description: A description of the project.
        status: The current status of the project ('active' or 'archived').
        tags: A list of tags to categorize the project.

    Returns:
        A dictionary representing the newly created project node.
    """
    return project_service.create_project(name=name, description=description, status=status, tags=tags)

@mcp.tool
def get_projects(
    status: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of projects, optionally filtering by status or tags.

    Args:
        status: Filter projects by their status.
        tags: Filter projects that have any of the specified tags.

    Returns:
        A list of project nodes that match the filter criteria.
    """
    return project_service.get_projects(status=status, tags=tags)

@mcp.tool
def update_project(
    project_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Updates the properties of an existing project.

    Args:
        project_id: The unique ID of the project to update.
        name: A new name for the project.
        description: A new description for the project.
        status: A new status for the project.
        tags: A new list of tags for the project.

    Returns:
        The updated project node.
    """
    return project_service.update_project(
        project_id=project_id, name=name, description=description, status=status, tags=tags
    )

# --- Task Tools ---

@mcp.tool
def create_task(
    description: str,
    status: str = 'todo',
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates a new task with the given properties.

    Args:
        description: The main description of the task.
        status: The current status ('todo', 'in_progress', 'done', etc.).
        tags: A list of tags to categorize the task.
        due_date: An optional due date in ISO format (e.g., '2025-10-07T10:00:00').

    Returns:
        A dictionary representing the newly created task node.
    """
    return task_service.create_task(description=description, status=status, tags=tags, due_date=due_date)

@mcp.tool
def get_tasks(
    status: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of tasks, optionally filtering by status or tags.

    Args:
        status: Filter tasks by their status.
        tags: Filter tasks that have any of the specified tags.

    Returns:
        A list of task nodes that match the filter criteria.
    """
    return task_service.get_tasks(status=status, tags=tags)

@mcp.tool
def update_task(
    task_id: str,
    description: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Updates the properties of an existing task.

    Args:
        task_id: The unique ID of the task to update.
        description: A new description for the task.
        status: A new status for the task.
        tags: A new list of tags for the task.
        due_date: A new due date for the task.

    Returns:
        The updated task node.
    """
    return task_service.update_task(
        task_id=task_id, description=description, status=status, tags=tags, due_date=due_date
    )

# --- Shared Tools ---

@mcp.tool
def create_edge(source_id: str, label: str, target_id: str) -> dict:
    """
    Creates a relationship (edge) between two existing nodes.

    Args:
        source_id: The unique ID of the starting node.
        label: The description of the relationship (e.g., 'part_of', 'mentions').
        target_id: The unique ID of the ending node.

    Returns:
        A dictionary representing the newly created edge.
    """
    return shared_service.create_edge(source_id=source_id, label=label, target_id=target_id)

@mcp.tool
def get_related_nodes(node_id: str, label: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Finds all nodes connected to a given node via an edge.

    This is useful for finding all tasks for a project, or all notes
    that mention a specific person.

    Args:
        node_id: The unique ID of the node to start from.
        label: An optional relationship label to filter by (e.g., 'part_of', 'mentions').

    Returns:
        A list of connected node dictionaries.
    """
    return shared_service.get_related_nodes(node_id=node_id, label=label)


if __name__ == "__main__":
    # Run the MCP server.
    mcp.run()
from typing import List, Optional, Dict, Any
from fastmcp import FastMCP
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide
import argparse

# Import the service modules that contain the business logic
from app.tools import note as note_service
from app.tools import person as person_service
from app.tools import project as project_service
from app.tools import shared as shared_service
from app.tools import task as task_service
from app.models import AnyNode
from app.config import load_config, config
from app.vector_store import VectorStore
from app.database import Session
from app.containers import Container


# This is the central FastMCP application instance.
mcp = FastMCP(
    name="Knowledge Graph Kit",
    instructions="You are an agent managing a knowledge graph. Use the available tools to create, retrieve, update, and connect nodes (tasks, notes, people, projects) to fulfill user requests."
)

# --- Note Tools ---

@mcp.tool
@inject
def create_note(
    title: str,
    content: str,
    tags: Optional[List[str]] = None,
    db: Session = Provide[Container.db],
    vector_store: VectorStore = Provide[Container.vector_store]
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
    return note_service.create_note(db=db, vector_store=vector_store, title=title, content=content, tags=tags)

@mcp.tool
def get_notes(
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of notes, optionally filtering by tags.

    Args:
        tags: Filter notes that have any of the specified tags.

    Returns:
        A list of note nodes that match the filter criteria.
    """
    return note_service.get_notes(db=db, tags=tags)

@mcp.tool
def update_note(
    note_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None,
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
    return note_service.update_note(db=db, vector_store=vector_store, note_id=note_id, title=title, content=content, tags=tags)

# --- Person Tools ---

@mcp.tool
def create_person(
    name: str,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
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
    return person_service.create_person(db=db, vector_store=vector_store, name=name, tags=tags, metadata=metadata)

@mcp.tool
def get_persons(
    name: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of persons, optionally filtering by name or tags.

    Args:
        name: Filter persons by exact name match.
        tags: Filter persons that have any of the specified tags.

    Returns:
        A list of person nodes that match the filter criteria.
    """
    return person_service.get_persons(db=db, name=name, tags=tags)

@mcp.tool
def update_person(
    person_id: str,
    name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
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
    return person_service.update_person(db=db, vector_store=vector_store, person_id=person_id, name=name, tags=tags, metadata=metadata)

# --- Project Tools ---

@mcp.tool
def create_project(
    name: str,
    description: str,
    status: str = 'active',
    tags: Optional[List[str]] = None,
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
    return project_service.create_project(db=db, vector_store=vector_store, name=name, description=description, status=status, tags=tags)

@mcp.tool
def get_projects(
    status: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of projects, optionally filtering by status or tags.

    Args:
        status: Filter projects by their status.
        tags: Filter projects that have any of the specified tags.

    Returns:
        A list of project nodes that match the filter criteria.
    """
    return project_service.get_projects(db=db, status=status, tags=tags)

@mcp.tool
def update_project(
    project_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[str]] = None,
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
        db=db, vector_store=vector_store, project_id=project_id, name=name, description=description, status=status, tags=tags
    )

# --- Task Tools ---

@mcp.tool
def create_task(
    description: str,
    status: str = 'todo',
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
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
    return task_service.create_task(db=db, vector_store=vector_store, description=description, status=status, tags=tags, due_date=due_date)

@mcp.tool
def get_tasks(
    status: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of tasks, optionally filtering by status or tags.

    Args:
        status: Filter tasks by their status.
        tags: Filter tasks that have any of the specified tags.

    Returns:
        A list of task nodes that match the filter criteria.
    """
    return task_service.get_tasks(db=db, status=status, tags=tags)

@mcp.tool
def update_task(
    task_id: str,
    description: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
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
        db=db, vector_store=vector_store, task_id=task_id, description=description, status=status, tags=tags, due_date=due_date
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
    return shared_service.create_edge(db=db, source_id=source_id, label=label, target_id=target_id)

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
    return shared_service.get_related_nodes(db=db, node_id=node_id, label=label)


@mcp.tool
def search_nodes(
    query: Optional[str] = None,
    node_type: Optional[AnyNode] = None,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """

    Searches for nodes based on a query string, type, and tags.

    Args:
        query: A string to search for in the relevant fields of the nodes.
        node_type: The type of nodes to filter by (e.g., "Task", "Note").
        tags: A list of tags to filter by.

    Returns:
        A list of nodes that match the search criteria.
    """
    return shared_service.search_nodes(db=db, query=query, node_type=node_type, tags=tags)


@mcp.tool
def get_all_tags() -> List[str]:
    """
    Retrieves a sorted list of all unique tags from all nodes.

    Returns:
        A list of unique tag strings.
    """
    return shared_service.get_all_tags(db=db)


@mcp.tool
def delete_node(node_id: str) -> bool:
    """
    Deletes a node by its unique ID.

    Args:
        node_id: The ID of the node to delete.

    Returns:
        True if the node was successfully deleted, False otherwise.
    """
    return shared_service.delete_node(db=db, vector_store=vector_store, node_id=node_id)


@mcp.tool
def delete_edge(source_id: str, target_id: str, label: str) -> bool:
    """
    Deletes an edge between two nodes, specified by the source and target IDs and the edge label.

    Args:
        source_id: The ID of the source node.
        target_id: The ID of the target node.
        label: The label of the edge to delete.

    Returns:
        True if the edge was successfully deleted, False otherwise.
    """
    return shared_service.delete_edge(
        db=db, source_id=source_id, target_id=target_id, label=label
    )


@mcp.tool
def rename_tag(old_tag: str, new_tag: str) -> List[Dict[str, Any]]:
    """
    Renames a specific tag on all nodes where it is present.

    Args:
        old_tag: The current name of the tag.
        new_tag: The new name for the tag.

    Returns:
        A list of the node objects that were updated.
    """
    return shared_service.rename_tag(db=db, old_tag=old_tag, new_tag=new_tag)


@mcp.tool
def semantic_search(
    query: str,
    node_type: Optional[AnyNode] = None,
) -> List[Dict[str, Any]]:
    """
    Performs a semantic search for nodes based on a query string.

    Args:
        query: The query string to search for.
        node_type: The type of nodes to filter by (e.g., "Task", "Note").

    Returns:
        A list of nodes that are semantically similar to the query.
    """
    return shared_service.semantic_search(db=db, vector_store=vector_store, query=query, node_type=node_type)


def main():
    """
    Main function to run the MCP server.
    """
    parser = argparse.ArgumentParser(description="Run the Notes Graph MCP server.")
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to the configuration file.'
    )
    args = parser.parse_args()

    # Load the configuration
    load_config(args.config)

    # Get host and port from config
    host = config["HOST"]
    port = config["PORT"]

    # Run the MCP server
    mcp.run(transport='http', host=host, port=port)

if __name__ == "__main__":
    main()
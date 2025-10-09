from typing import List, Optional, Dict, Any
from app import crud
from app.models import TaskProperties

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
    properties = TaskProperties(
        description=description,
        status=status,
        tags=tags or [],
        due_date=due_date
    )
    return crud.create_node(node_type="Task", properties=properties.model_dump())

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
    filters = {}
    if status:
        filters['status'] = status
    if tags:
        # This is a simple implementation. For more complex tag filtering
        # (e.g., all tags), the CRUD function would need to be updated.
        all_nodes = crud.get_nodes(node_type="Task")
        
        # Manual filtering for tags
        if tags:
            tagged_nodes = []
            for node in all_nodes:
                node_tags = node.get("properties", {}).get("tags", [])
                if any(t in node_tags for t in tags):
                    tagged_nodes.append(node)
            return tagged_nodes
        return all_nodes

    return crud.get_nodes(node_type="Task", **filters)

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
    properties_to_update = {
        k: v for k, v in {
            "description": description,
            "status": status,
            "tags": tags,
            "due_date": due_date
        }.items() if v is not None
    }
    
    if not properties_to_update:
        raise ValueError("No properties provided to update.")

    return crud.update_node(node_id=task_id, properties=properties_to_update)
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app import crud
from app.models import ProjectProperties
from app.vector_store import VectorStore

def create_project(
    db: Session,
    vector_store: VectorStore,
    name: str,
    description: str,
    status: str = 'active',
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Creates a new project node.

    Args:
        db: The SQLAlchemy database session.
        vector_store: The vector store instance.
        name: The name of the project.
        description: A description of the project.
        status: The current status of the project ('active' or 'archived').
        tags: A list of tags to categorize the project.

    Returns:
        A dictionary representing the newly created project node.
    """

    properties = ProjectProperties(
        name=name,
        description=description,
        status=status,
        tags=tags or []
    )
    return crud.create_node(db=db, vector_store=vector_store, node_type="Project", properties=properties.model_dump())

def get_projects(
    db: Session,
    status: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of projects, optionally filtering by status or tags.

    Args:
        db: The SQLAlchemy database session.
        status: Filter projects by their status.
        tags: Filter projects that have any of the specified tags.

    Returns:
        A list of project nodes that match the filter criteria.
    """
    filters = {}
    if status:
        filters['status'] = status
    
    nodes = crud.get_nodes(db=db, node_type="Project", **filters)

    if tags:
        tagged_nodes = []
        for node in nodes:
            node_tags = node.get("properties", {}).get("tags", [])
            if any(t in node_tags for t in tags):
                tagged_nodes.append(node)
        return tagged_nodes
        
    return nodes

def update_project(
    db: Session,
    vector_store: VectorStore,
    project_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Updates the properties of an existing project.

    Args:
        db: The SQLAlchemy database session.
        vector_store: The vector store instance.
        project_id: The unique ID of the project to update.
        name: A new name for the project.
        description: A new description for the project.
        status: A new status for the project.
        tags: A new list of tags for the project.

    Returns:
        The updated project node.
    """
    properties_to_update = {
        k: v for k, v in {
            "name": name,
            "description": description,
            "status": status,
            "tags": tags
        }.items() if v is not None
    }

    if not properties_to_update:
        raise ValueError("No properties provided to update.")

    return crud.update_node(db=db, vector_store=vector_store, node_id=project_id, properties=properties_to_update)
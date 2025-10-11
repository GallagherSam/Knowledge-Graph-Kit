from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app import crud
from app.models import PersonProperties
from app.vector_store import VectorStore

def create_person(
    db: Session,
    vector_store: VectorStore,
    name: str,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Creates a new person node.

    Args:
        db: The SQLAlchemy database session.
        vector_store: The vector store instance.
        name: The full name of the person.
        tags: A list of tags to categorize the person.
        metadata: A dictionary for additional data like contact info or role.

    Returns:
        A dictionary representing the newly created person node.
    """
    properties = PersonProperties(
        name=name,
        tags=tags or [],
        metadata=metadata or {}
    )
    return crud.create_node(db=db, vector_store=vector_store, node_type="Person", properties=properties.model_dump())

def get_persons(
    db: Session,
    name: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of persons, optionally filtering by name or tags.

    Args:
        db: The SQLAlchemy database session.
        name: Filter persons by exact name match.
        tags: Filter persons that have any of the specified tags.

    Returns:
        A list of person nodes that match the filter criteria.
    """
    filters = {}
    if name:
        filters['name'] = name
    
    nodes = crud.get_nodes(db=db, node_type="Person", **filters)

    if tags:
        tagged_nodes = []
        for node in nodes:
            node_tags = node.get("properties", {}).get("tags", [])
            if any(t in node_tags for t in tags):
                tagged_nodes.append(node)
        return tagged_nodes
    
    return nodes

def update_person(
    db: Session,
    vector_store: VectorStore,
    person_id: str,
    name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Updates the properties of an existing person.

    Args:
        db: The SQLAlchemy database session.
        vector_store: The vector store instance.
        person_id: The unique ID of the person to update.
        name: A new name for the person.
        tags: A new list of tags for the person.
        metadata: A new metadata dictionary.

    Returns:
        The updated person node.
    """
    properties_to_update = {
        k: v for k, v in {
            "name": name,
            "tags": tags,
            "metadata": metadata
        }.items() if v is not None
    }

    if not properties_to_update:
        raise ValueError("No properties provided to update.")

    return crud.update_node(db=db, vector_store=vector_store, node_id=person_id, properties=properties_to_update)
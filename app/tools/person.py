from typing import List, Optional, Dict, Any
from app import crud
from app.models import PersonProperties

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
    properties = PersonProperties(
        name=name,
        tags=tags or [],
        metadata=metadata or {}
    )
    return crud.create_node(node_type="Person", properties=properties.model_dump())

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
    filters = {}
    if name:
        filters['name'] = name
    
    nodes = crud.get_nodes(node_type="Person", **filters)

    if tags:
        tagged_nodes = []
        for node in nodes:
            node_tags = node.get("properties", {}).get("tags", [])
            if any(t in node_tags for t in tags):
                tagged_nodes.append(node)
        return tagged_nodes
    
    return nodes

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
    properties_to_update = {
        k: v for k, v in {
            "name": name,
            "tags": tags,
            "metadata": metadata
        }.items() if v is not None
    }

    if not properties_to_update:
        raise ValueError("No properties provided to update.")

    return crud.update_node(node_id=person_id, properties=properties_to_update)
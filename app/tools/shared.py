from typing import List, Optional, Dict, Any
from app import crud
from app.models import AnyNode

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
    return crud.create_edge(source_id=source_id, label=label, target_id=target_id)

def get_related_nodes(node_id: str, label: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Service function to find all nodes connected to a specific node.
    """
    return crud.get_connected_nodes(node_id=node_id, label=label)

def search_nodes(
    query: Optional[str] = None,
    node_type: Optional[AnyNode] = None,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Service function to search for nodes.
    """
    return crud.search_nodes(query=query, node_type=node_type, tags=tags)


def get_all_tags() -> List[str]:
    """
    Service function to retrieve all unique tags.
    """
    return crud.get_all_tags()


def delete_node(node_id: str) -> bool:
    """
    Service function to delete a node by its ID.
    """
    return crud.delete_node(node_id=node_id)


def delete_edge(source_id: str, target_id: str, label: str) -> bool:
    """
    Service function to delete an edge by its source, target, and label.
    """
    return crud.delete_edge_by_nodes(
        source_id=source_id, target_id=target_id, label=label
    )


def rename_tag(old_tag: str, new_tag: str) -> List[Dict[str, Any]]:
    """
    Service function to rename a tag across all nodes.
    """
    return crud.rename_tag(old_tag=old_tag, new_tag=new_tag)
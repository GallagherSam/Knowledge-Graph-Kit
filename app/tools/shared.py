from typing import List, Optional, Dict, Any
from app import crud

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
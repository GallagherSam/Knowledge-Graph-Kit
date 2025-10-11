from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app import crud
from app.models import AnyNode
from app.vector_store import VectorStore

def create_edge(db: Session, source_id: str, label: str, target_id: str) -> dict:
    """
    Creates a relationship (edge) between two existing nodes.

    Args:
        db: The SQLAlchemy database session.
        source_id: The unique ID of the starting node.
        label: The description of the relationship (e.g., 'part_of', 'mentions').
        target_id: The unique ID of the ending node.

    Returns:
        A dictionary representing the newly created edge.
    """
    return crud.create_edge(db=db, source_id=source_id, label=label, target_id=target_id)

def get_related_nodes(db: Session, node_id: str, label: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Service function to find all nodes connected to a specific node.
    """
    return crud.get_connected_nodes(db=db, node_id=node_id, label=label)

def search_nodes(
    db: Session,
    query: Optional[str] = None,
    node_type: Optional[AnyNode] = None,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Service function to search for nodes.
    """
    return crud.search_nodes(db=db, query=query, node_type=node_type, tags=tags)


def get_all_tags(db: Session) -> List[str]:
    """
    Service function to retrieve all unique tags.
    """
    return crud.get_all_tags(db=db)


def delete_node(db: Session, vector_store: VectorStore, node_id: str) -> bool:
    """
    Service function to delete a node by its ID.
    """
    return crud.delete_node(db=db, vector_store=vector_store, node_id=node_id)


def delete_edge(db: Session, source_id: str, target_id: str, label: str) -> bool:
    """
    Service function to delete an edge by its source, target, and label.
    """
    return crud.delete_edge_by_nodes(
        db=db, source_id=source_id, target_id=target_id, label=label
    )


def rename_tag(db: Session, old_tag: str, new_tag: str) -> List[Dict[str, Any]]:
    """
    Service function to rename a tag across all nodes.
    """
    return crud.rename_tag(db=db, old_tag=old_tag, new_tag=new_tag)


def semantic_search(
    db: Session,
    vector_store: VectorStore,
    query: str,
    node_type: Optional[AnyNode] = None,
) -> List[Dict[str, Any]]:
    """
    Service function to perform a semantic search for nodes.
    """
    node_ids = vector_store.semantic_search(query=query, node_type=node_type)

    if not node_ids:
        return []

    # Retrieve the full node data for the given IDs
    return crud.get_nodes_by_ids(db=db, node_ids=node_ids)
import datetime
from typing import Any, Dict, List, Optional, Type

from sqlalchemy import String
from sqlalchemy.orm import Session

from app.database import EdgeModel, NodeModel
from app.models import (
    AnyNode,
    Edge,
    Node,
    NoteProperties,
    PersonProperties,
    ProjectProperties,
    TaskProperties,
)
from app.vector_store import VectorStore

# A mapping from the string representation of a node type to its Pydantic model class.
PROPERTIES_MODELS: Dict[AnyNode, Type[TaskProperties | NoteProperties | PersonProperties | ProjectProperties]] = {
    "Task": TaskProperties,
    "Note": NoteProperties,
    "Person": PersonProperties,
    "Project": ProjectProperties,
}

def create_node(db: Session, vector_store: VectorStore, node_type: AnyNode, properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new node, validates its properties, and saves it to the database.

    Args:
        db: The SQLAlchemy database session.
        vector_store: The vector store instance.
        node_type: The type of the node to create.
        properties: A dictionary of properties for the node.

    Returns:
        The created node as a dictionary.
    """
    PropertiesModel = PROPERTIES_MODELS[node_type]
    validated_properties = PropertiesModel(**properties).model_dump(mode="json")
    new_node = Node(type=node_type, properties=validated_properties)
    node_data = new_node.model_dump(mode="json")

    db_node = NodeModel(**node_data)
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    created_node = {"id": db_node.id, "type": db_node.type, "properties": db_node.properties}
    
    vector_store.add_node(created_node)
    return created_node

def get_nodes(db: Session, node_type: Optional[AnyNode] = None, **kwargs) -> List[Dict[str, Any]]:
    """
    Retrieves nodes from the state, with optional filtering by type and properties.

    Args:
        db: The SQLAlchemy database session.
        node_type: The type of nodes to filter by.
        **kwargs: Arbitrary keyword arguments to filter node properties by.

    Returns:
        A list of nodes that match the filter criteria.
    """
    query = db.query(NodeModel)
    
    if node_type:
        query = query.filter(NodeModel.type == node_type)
        
    all_nodes = [{"id": n.id, "type": n.type, "properties": n.properties} for n in query.all()]

    if not kwargs:
        return all_nodes

    filtered_nodes = []
    for node in all_nodes:
        properties = node.get("properties", {})
        if all(properties.get(key) == value for key, value in kwargs.items()):
            filtered_nodes.append(node)
    return filtered_nodes

def get_nodes_by_ids(db: Session, node_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Retrieves nodes from the state by their IDs.

    Args:
        db: The SQLAlchemy database session.
        node_ids: A list of node IDs to retrieve.

    Returns:
        A list of nodes that match the given IDs.
    """
    nodes = db.query(NodeModel).filter(NodeModel.id.in_(node_ids)).all()
    return [{"id": n.id, "type": n.type, "properties": n.properties} for n in nodes]

def update_node(db: Session, vector_store: VectorStore, node_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates the properties of a specific node.

    Args:
        db: The SQLAlchemy database session.
        vector_store: The vector store instance.
        node_id: The ID of the node to update.
        properties: A dictionary of properties to update.

    Returns:
        The updated node as a dictionary.
        
    Raises:
        ValueError: If the node with the given ID is not found.
    """
    db_node = db.query(NodeModel).filter(NodeModel.id == node_id).first()

    if not db_node:
        raise ValueError(f"Node with id '{node_id}' not found.")

    updated_properties = db_node.properties.copy()
    updated_properties.update(properties)
    
    updated_properties["modified_at"] = datetime.datetime.now(datetime.timezone.utc)
    node_type = db_node.type
    PropertiesModel = PROPERTIES_MODELS[node_type]
    validated_properties = PropertiesModel(**updated_properties).model_dump(mode="json")
    
    db_node.properties = validated_properties
    db.commit()
    db.refresh(db_node)
    updated_node = {"id": db_node.id, "type": db_node.type, "properties": db_node.properties}

    vector_store.update_node(updated_node)
    return updated_node

def delete_node(db: Session, vector_store: VectorStore, node_id: str) -> bool:
    """
    Deletes a node from the database.

    Args:
        db: The SQLAlchemy database session.
        vector_store: The vector store instance.
        node_id: The ID of the node to delete.
    
    Returns:
        True if the node was deleted, False otherwise.
    """
    db_node = db.query(NodeModel).filter(NodeModel.id == node_id).first()
    if db_node:
        db.delete(db_node)
        # Also delete connected edges
        db.query(EdgeModel).filter((EdgeModel.source_id == node_id) | (EdgeModel.target_id == node_id)).delete(synchronize_session=False)
        db.commit()
        vector_store.delete_node(node_id)
        return True
    return False

def create_edge(db: Session, source_id: str, target_id: str, label: str) -> Dict[str, Any]:
    """
    Creates a new edge between two nodes and saves it to the database.

    Args:
        db: The SQLAlchemy database session.
        source_id: The ID of the source node.
        label: The label describing the relationship.
        target_id: The ID of the target node.

    Returns:
        The created edge as a dictionary.
        
    Raises:
        ValueError: If either the source or target node does not exist.
    """
    source_node = db.query(NodeModel).filter(NodeModel.id == source_id).first()
    if not source_node:
        raise ValueError(f"Source node with id '{source_id}' not found.")

    target_node = db.query(NodeModel).filter(NodeModel.id == target_id).first()
    if not target_node:
        raise ValueError(f"Target node with id '{target_id}' not found.")

    new_edge = Edge(source_id=source_id, label=label, target_id=target_id)
    edge_data = new_edge.model_dump(mode="json")

    db_edge = EdgeModel(**edge_data)
    db.add(db_edge)
    db.commit()
    db.refresh(db_edge)
    return {"id": db_edge.id, "source_id": db_edge.source_id, "target_id": db_edge.target_id, "label": db_edge.label}

def delete_edge(db: Session, edge_id: str) -> bool:
    """
    Deletes an edge from the database.

    Args:
        db: The SQLAlchemy database session.
        edge_id: The ID of the edge to delete.

    Returns:
        True if the edge was deleted, False otherwise.
    """
    db_edge = db.query(EdgeModel).filter(EdgeModel.id == edge_id).first()
    if db_edge:
        db.delete(db_edge)
        db.commit()
        return True
    return False

def get_connected_nodes(
    db: Session, node_id: str, label: Optional[str] = None, depth: int = 1
) -> List[Dict[str, Any]]:
    """
    Retrieves all nodes connected to a given node up to a specified depth.

    Args:
        db: The SQLAlchemy database session.
        node_id: The ID of the starting node.
        label: An optional edge label to filter the relationships by.
        depth: The maximum depth to traverse the graph.

    Returns:
        A list of node dictionaries that are connected to the starting node.
    """
    if depth <= 0:
        return []

    # BFS traversal implementation
    # The queue stores tuples of (node_id, depth)
    queue = [(node_id, 0)]
    # Keep track of visited nodes to avoid cycles
    visited_node_ids = {node_id}
    connected_nodes = {}

    while queue:
        current_node_id, current_depth = queue.pop(0)

        if current_depth >= depth:
            continue

        query = db.query(EdgeModel).filter(
            (EdgeModel.source_id == current_node_id) | (EdgeModel.target_id == current_node_id)
        )
        if label:
            query = query.filter(EdgeModel.label == label)

        edges = query.all()

        neighbor_ids = set()
        for edge in edges:
            if edge.source_id == current_node_id:
                neighbor_ids.add(edge.target_id)
            else:
                neighbor_ids.add(edge.source_id)

        # Fetch node details for the neighbors
        nodes = db.query(NodeModel).filter(NodeModel.id.in_(list(neighbor_ids))).all()

        for node in nodes:
            if node.id not in visited_node_ids:
                visited_node_ids.add(node.id)
                connected_nodes[node.id] = {"id": node.id, "type": node.type, "properties": node.properties}
                queue.append((node.id, current_depth + 1))

    return list(connected_nodes.values())

def search_nodes(
    db: Session,
    query: Optional[str] = None,
    node_type: Optional[AnyNode] = None,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Searches for nodes based on a query string, type, and tags.

    Args:
        db: The SQLAlchemy database session.
        query: A string to search for in the relevant fields of the nodes.
        node_type: The type of nodes to filter by.
        tags: A list of tags to filter by.

    Returns:
        A list of nodes that match the search criteria.
    """
    db_query = db.query(NodeModel)

    if node_type:
        db_query = db_query.filter(NodeModel.type == node_type)

    nodes = [{"id": n.id, "type": n.type, "properties": n.properties} for n in db_query.all()]

    if tags:
        nodes = [
            node
            for node in nodes
            if any(tag in node.get("properties", {}).get("tags", []) for tag in tags)
        ]

    if query:
        query = query.lower()
        filtered_nodes = []
        for node in nodes:
            props = node.get("properties", {})
            node_type = node.get("type")
            
            if node_type == "Task" and query in props.get("description", "").lower():
                filtered_nodes.append(node)
            elif node_type == "Note" and (
                query in props.get("title", "").lower()
                or query in props.get("content", "").lower()
            ):
                filtered_nodes.append(node)
            elif node_type == "Person" and query in props.get("name", "").lower():
                filtered_nodes.append(node)
            elif node_type == "Project" and (query in props.get("name", "").lower() or query in props.get("description")):
                filtered_nodes.append(node)
        return filtered_nodes

    return nodes

def get_all_tags(db: Session) -> List[str]:
    """
    Retrieves a sorted list of all unique tags from all nodes.

    Args:
        db: The SQLAlchemy database session.

    Returns:
        A list of unique tag strings.
    """
    nodes = db.query(NodeModel).all()
    all_tags = set()

    for node in nodes:
        tags = node.properties.get("tags", [])
        if tags:
            all_tags.update(tags)

    return sorted(list(all_tags))


def delete_edge_by_nodes(db: Session, source_id: str, target_id: str, label: str) -> bool:
    """
    Deletes an edge based on its source, target, and label.

    Args:
        db: The SQLAlchemy database session.
        source_id: The ID of the source node.
        target_id: The ID of the target node.
        label: The label of the edge.

    Returns:
        True if the edge was found and deleted, False otherwise.
    """
    edge_to_delete = db.query(EdgeModel).filter_by(source_id=source_id, target_id=target_id, label=label).first()

    if edge_to_delete:
        db.delete(edge_to_delete)
        db.commit()
        return True
    return False


def rename_tag(db: Session, old_tag: str, new_tag: str) -> List[Dict[str, Any]]:
    """
    Renames a tag on all nodes that have it.

    Args:
        db: The SQLAlchemy database session.
        old_tag: The tag to be renamed.
        new_tag: The new tag name.

    Returns:
        A list of nodes that were updated.
    """
    nodes_to_update = db.query(NodeModel).filter(NodeModel.properties.cast(String).like(f'%"{old_tag}"%')).all()
    updated_nodes = []

    for node in nodes_to_update:
        properties = node.properties
        tags = properties.get("tags", [])

        if old_tag in tags:
            # Create a new list of tags with the old tag replaced
            new_tags = [new_tag if tag == old_tag else tag for tag in tags]
            # Remove duplicates if new_tag was already present
            new_tags = sorted(list(set(new_tags)))

            # Update the node's properties
            updated_properties = properties.copy()
            updated_properties["tags"] = new_tags

            # Validate and save the updated node
            PropertiesModel = PROPERTIES_MODELS[node.type]
            validated_properties = PropertiesModel(**updated_properties).model_dump(mode="json")

            node.properties = validated_properties
            db.add(node)
            updated_nodes.append({"id": node.id, "type": node.type, "properties": validated_properties})

    if updated_nodes:
        db.commit()

    return updated_nodes
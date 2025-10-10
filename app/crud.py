from typing import List, Dict, Any, Optional, Type

from app.state import state_manager
from app.models import (
    Node,
    Edge,
    TaskProperties,
    NoteProperties,
    PersonProperties,
    ProjectProperties,
    AnyNode,
)

# A mapping from the string representation of a node type to its Pydantic model class.
PROPERTIES_MODELS: Dict[AnyNode, Type[TaskProperties | NoteProperties | PersonProperties | ProjectProperties]] = {
    "Task": TaskProperties,
    "Note": NoteProperties,
    "Person": PersonProperties,
    "Project": ProjectProperties,
}

def create_node(node_type: AnyNode, properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new node, validates its properties, and saves it to the database.

    Args:
        node_type: The type of the node to create.
        properties: A dictionary of properties for the node.

    Returns:
        The created node as a dictionary.
    """
    PropertiesModel = PROPERTIES_MODELS[node_type]
    validated_properties = PropertiesModel(**properties).model_dump(mode="json")
    new_node = Node(type=node_type, properties=validated_properties)
    node_data = new_node.model_dump(mode="json")
    return state_manager.add_node(node_data)

def get_nodes(node_type: Optional[AnyNode] = None, **kwargs) -> List[Dict[str, Any]]:
    """
    Retrieves nodes from the state, with optional filtering by type and properties.

    Args:
        node_type: The type of nodes to filter by.
        **kwargs: Arbitrary keyword arguments to filter node properties by.

    Returns:
        A list of nodes that match the filter criteria.
    """
    nodes = state_manager.read_nodes()
    
    if node_type:
        nodes = [node for node in nodes if node.get("type") == node_type]
        
    if kwargs:
        filtered_nodes = []
        for node in nodes:
            properties = node.get("properties", {})
            if all(properties.get(key) == value for key, value in kwargs.items()):
                filtered_nodes.append(node)
        nodes = filtered_nodes
        
    return nodes

def update_node(node_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates the properties of a specific node.

    Args:
        node_id: The ID of the node to update.
        properties: A dictionary of properties to update.

    Returns:
        The updated node as a dictionary.
        
    Raises:
        ValueError: If the node with the given ID is not found.
    """
    nodes = state_manager.read_nodes()
    node_to_update = next((n for n in nodes if n["id"] == node_id), None)

    if not node_to_update:
        raise ValueError(f"Node with id '{node_id}' not found.")

    updated_properties = node_to_update["properties"]
    updated_properties.update(properties)
    
    node_type = node_to_update["type"]
    PropertiesModel = PROPERTIES_MODELS[node_type]
    validated_properties = PropertiesModel(**updated_properties).model_dump(mode="json")
    
    updated_node = state_manager.update_node_in_db(node_id, validated_properties)
    if updated_node is None:
        raise ValueError(f"Node with id '{node_id}' could not be updated.")

    return updated_node

def delete_node(node_id: str) -> bool:
    """
    Deletes a node from the database.

    Args:
        node_id: The ID of the node to delete.
    
    Returns:
        True if the node was deleted, False otherwise.
    """
    return state_manager.delete_node(node_id)

def create_edge(source_id: str, label: str, target_id: str) -> Dict[str, Any]:
    """
    Creates a new edge between two nodes and saves it to the database.

    Args:
        source_id: The ID of the source node.
        label: The label describing the relationship.
        target_id: The ID of the target node.

    Returns:
        The created edge as a dictionary.
        
    Raises:
        ValueError: If either the source or target node does not exist.
    """
    nodes = state_manager.read_nodes()
    node_ids = {node["id"] for node in nodes}
    
    if source_id not in node_ids:
        raise ValueError(f"Source node with id '{source_id}' not found.")
    if target_id not in node_ids:
        raise ValueError(f"Target node with id '{target_id}' not found.")

    new_edge = Edge(source_id=source_id, label=label, target_id=target_id)
    edge_data = new_edge.model_dump(mode="json")
    return state_manager.add_edge(edge_data)

def delete_edge(edge_id: str) -> bool:
    """
    Deletes an edge from the database.

    Args:
        edge_id: The ID of the edge to delete.

    Returns:
        True if the edge was deleted, False otherwise.
    """
    return state_manager.delete_edge(edge_id)

def get_connected_nodes(node_id: str, label: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves all nodes connected to a given node by an edge.

    Args:
        node_id: The ID of the starting node.
        label: An optional edge label to filter the relationships by.

    Returns:
        A list of node dictionaries that are connected to the starting node.
    """
    nodes = state_manager.read_nodes()
    edges = state_manager.read_edges()
    
    connected_node_ids = set()
    
    for edge in edges:
        if label and edge.get("label") != label:
            continue

        if edge.get("source_id") == node_id:
            connected_node_ids.add(edge.get("target_id"))
        elif edge.get("target_id") == node_id:
            connected_node_ids.add(edge.get("source_id"))
            
    return [node for node in nodes if node.get("id") in connected_node_ids]

def search_nodes(
    query: Optional[str] = None,
    node_type: Optional[AnyNode] = None,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Searches for nodes based on a query string, type, and tags.

    Args:
        query: A string to search for in the relevant fields of the nodes.
        node_type: The type of nodes to filter by.
        tags: A list of tags to filter by.

    Returns:
        A list of nodes that match the search criteria.
    """
    nodes = state_manager.read_nodes()

    if node_type:
        nodes = [node for node in nodes if node.get("type") == node_type]

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

def get_all_tags() -> List[str]:
    """
    Retrieves a sorted list of all unique tags from all nodes.

    Returns:
        A list of unique tag strings.
    """
    nodes = state_manager.read_nodes()
    all_tags = set()

    for node in nodes:
        tags = node.get("properties", {}).get("tags", [])
        if tags:
            all_tags.update(tags)

    return sorted(list(all_tags))
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
# This allows for dynamic validation based on the 'type' field.
PROPERTIES_MODELS: Dict[AnyNode, Type[TaskProperties | NoteProperties | PersonProperties | ProjectProperties]] = {
    "Task": TaskProperties,
    "Note": NoteProperties,
    "Person": PersonProperties,
    "Project": ProjectProperties,
}

def create_node(node_type: AnyNode, properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new node, validates its properties, and saves it to the state.

    Args:
        node_type: The type of the node to create (e.g., "Task", "Note").
        properties: A dictionary of properties for the node.

    Returns:
        The created node as a dictionary.
    """
    # Validate the provided properties against the corresponding Pydantic model.
    PropertiesModel = PROPERTIES_MODELS[node_type]
    validated_properties = PropertiesModel(**properties).model_dump(mode="json")

    # Create the main Node object.
    new_node = Node(type=node_type, properties=validated_properties)
    
    # Read the current nodes, add the new one, and write back to the state.
    nodes = state_manager.read_nodes()
    nodes.append(new_node.model_dump(mode="json"))
    state_manager.write_nodes(nodes)
    
    return new_node.model_dump(mode="json")

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
    
    # Filter by node type if provided.
    if node_type:
        nodes = [node for node in nodes if node.get("type") == node_type]
        
    # Filter by any other property kwargs.
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
        HTTPException: If the node with the given ID is not found.
    """
    nodes = state_manager.read_nodes()
    node_to_update = None
    node_index = -1

    # Find the node and its index.
    for i, node in enumerate(nodes):
        if node.get("id") == node_id:
            node_to_update = node
            node_index = i
            break
            
    if not node_to_update:
        raise Exception(status_code=404, detail=f"Node with id '{node_id}' not found.")

    # Update the existing properties with the new ones.
    updated_properties = node_to_update["properties"]
    updated_properties.update(properties)
    
    # Re-validate the updated properties.
    node_type = node_to_update["type"]
    PropertiesModel = PROPERTIES_MODELS[node_type]
    validated_properties = PropertiesModel(**updated_properties).model_dump(mode="json")
    
    node_to_update["properties"] = validated_properties
    
    # Write the modified list of nodes back to the state.
    nodes[node_index] = node_to_update
    state_manager.write_nodes(nodes)
    
    return node_to_update

def create_edge(source_id: str, label: str, target_id: str) -> Dict[str, Any]:
    """
    Creates a new edge between two nodes and saves it to the state.

    Args:
        source_id: The ID of the source node.
        label: The label describing the relationship.
        target_id: The ID of the target node.

    Returns:
        The created edge as a dictionary.
        
    Raises:
        HTTPException: If either the source or target node does not exist.
    """
    nodes = state_manager.read_nodes()
    node_ids = {node["id"] for node in nodes}
    
    if source_id not in node_ids:
        raise Exception(status_code=404, detail=f"Source node with id '{source_id}' not found.")
    if target_id not in node_ids:
        raise Exception(status_code=404, detail=f"Target node with id '{target_id}' not found.")

    new_edge = Edge(source_id=source_id, label=label, target_id=target_id)
    
    edges = state_manager.read_edges()
    edges.append(new_edge.model_dump(mode="json"))
    state_manager.write_edges(edges)
    
    return new_edge.model_dump(mode="json")

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
        # Filter by label if one is provided
        if label and edge.get("label") != label:
            continue

        # Check if the edge involves our target node
        if edge.get("source_id") == node_id:
            connected_node_ids.add(edge.get("target_id"))
        elif edge.get("target_id") == node_id:
            connected_node_ids.add(edge.get("source_id"))
            
    # Return the full node objects for the connected IDs
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

    # Filter by node type if provided.
    if node_type:
        nodes = [node for node in nodes if node.get("type") == node_type]

    # Filter by tags if provided.
    if tags:
        nodes = [
            node
            for node in nodes
            if any(tag in node.get("properties", {}).get("tags", []) for tag in tags)
        ]

    # Filter by query string if provided.
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

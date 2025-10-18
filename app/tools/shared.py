from typing import Any, Dict, List, Optional

from app import crud
from app.models import AnyNode


class Shared:
    def __init__(self, mcp_instance, provider):
        self.provider = provider
        mcp_instance.tool(self.create_edge)
        mcp_instance.tool(self.get_related_nodes)
        mcp_instance.tool(self.search_nodes)
        mcp_instance.tool(self.get_all_tags)
        mcp_instance.tool(self.delete_node)
        mcp_instance.tool(self.delete_edge)
        mcp_instance.tool(self.rename_tag)
        mcp_instance.tool(self.semantic_search)

    def create_edge(self, source_id: str, label: str, target_id: str) -> dict:
        """
        Creates a relationship (edge) between two existing nodes.

        Args:
            source_id: The unique ID of the starting node.
            label: The description of the relationship (e.g., 'part_of', 'mentions').
            target_id: The unique ID of the ending node.

        Returns:
            A dictionary representing the newly created edge.
        """
        with self.provider.get_db() as db:
            return crud.create_edge(db=db, source_id=source_id, target_id=target_id, label=label)

    def get_related_nodes(
        self, node_id: str, label: Optional[str] = None, depth: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Finds all nodes connected to a given node, up to a specified depth.

        Args:
            node_id: The unique ID of the node to start from.
            label: An optional relationship label to filter by.
            depth: The maximum depth to traverse the graph (default: 1).

        Returns:
            A list of connected node dictionaries.
        """
        with self.provider.get_db() as db:
            return crud.get_connected_nodes(db=db, node_id=node_id, label=label, depth=depth)

    def search_nodes(
        self,
        query: Optional[str] = None,
        node_type: Optional[AnyNode] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Searches for nodes based on a query string, type, and tags.

        Args:
            query: A string to search for in the relevant fields of the nodes.
            node_type: The type of nodes to filter by (e.g., "Task", "Note").
            tags: A list of tags to filter by.

        Returns:
            A list of nodes that match the search criteria.
        """
        with self.provider.get_db() as db:
            return crud.search_nodes(db=db, query=query, node_type=node_type, tags=tags)

    def get_all_tags(self) -> List[str]:
        """
        Retrieves a sorted list of all unique tags from all nodes.

        Returns:
            A list of unique tag strings.
        """
        with self.provider.get_db() as db:
            return crud.get_all_tags(db=db)

    def delete_node(self, node_id: str) -> bool:
        """
        Deletes a node by its unique ID.

        Args:
            node_id: The ID of the node to delete.

        Returns:
            True if the node was successfully deleted, False otherwise.
        """
        with self.provider.get_db() as db:
            return crud.delete_node(db=db, vector_store=self.provider.vector_store, node_id=node_id)

    def delete_edge(self, source_id: str, target_id: str, label: str) -> bool:
        """
        Deletes an edge between two nodes.

        Args:
            source_id: The ID of the source node.
            target_id: The ID of the target node.
            label: The label of the edge to delete.

        Returns:
            True if the edge was successfully deleted, False otherwise.
        """
        with self.provider.get_db() as db:
            return crud.delete_edge_by_nodes(db=db, source_id=source_id, target_id=target_id, label=label)

    def rename_tag(self, old_tag: str, new_tag: str) -> List[Dict[str, Any]]:
        """
        Renames a specific tag on all nodes where it is present.

        Args:
            old_tag: The current name of the tag.
            new_tag: The new name for the tag.

        Returns:
            A list of the node objects that were updated.
        """
        with self.provider.get_db() as db:
            return crud.rename_tag(db=db, old_tag=old_tag, new_tag=new_tag)

    def semantic_search(
        self,
        query: str,
        node_type: Optional[AnyNode] = None,
    ) -> List[Dict[str, Any]]:
        """
        Performs a semantic search for nodes based on a query string.

        Args:
            query: The query string to search for.
            node_type: The type of nodes to filter by (e.g., "Task", "Note").

        Returns:
            A list of nodes that are semantically similar to the query,
            ordered by relevance.
        """
        with self.provider.get_db() as db:
            vector_store = self.provider.vector_store
            search_results = vector_store.semantic_search(query=query, node_type=node_type)
            
            if not search_results:
                return []

            # The results from ChromaDB are in a list of lists, one for each query.
            # Since we only send one query, we take the first list of IDs.
            node_ids = search_results["ids"][0]
            
            # Fetch the full node objects from the database
            nodes = crud.get_nodes_by_ids(db=db, node_ids=node_ids)

            # Create a dictionary for quick lookups of nodes by their ID
            nodes_by_id = {node['id']: node for node in nodes}

            # Reorder the nodes based on the semantic search results order
            ordered_nodes = [nodes_by_id[id] for id in node_ids if id in nodes_by_id]
            
            return ordered_nodes
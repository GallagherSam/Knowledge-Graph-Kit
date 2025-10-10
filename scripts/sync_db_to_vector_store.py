import sys
import os
from typing import List, Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.crud import get_nodes
from app.vector_store import vector_store_manager

def sync_db_to_vector_store():
    """
    Synchronizes the main database with the vector store.

    This script retrieves all nodes from the main database and adds them
    to the vector store, generating embeddings for each node.
    """
    print("Starting database to vector store synchronization...")

    # Retrieve all nodes from the main database
    all_nodes: List[Dict[str, Any]] = get_nodes()

    if not all_nodes:
        print("No nodes found in the database. Synchronization is not needed.")
        return

    print(f"Found {len(all_nodes)} nodes to synchronize.")

    # Add each node to the vector store
    for node in all_nodes:
        try:
            vector_store_manager.add_node(node)
            print(f"Successfully added node {node['id']} to the vector store.")
        except Exception as e:
            print(f"Failed to add node {node['id']} to the vector store: {e}")

    print("Synchronization complete.")

if __name__ == "__main__":
    sync_db_to_vector_store()
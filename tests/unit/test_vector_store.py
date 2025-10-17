import pytest
from unittest.mock import patch, MagicMock

from app.vector_store import VectorStore
from app.crud import create_node, get_nodes, delete_node
from app.models import NoteProperties

@pytest.fixture(scope="module")
def vector_store_manager_instance():
    """
    Provides a singleton instance of the VectorStore for testing.
    This ensures that the ChromaDB client is initialized only once per test module.
    """
    with patch('chromadb.PersistentClient') as mock_persistent_client:
        # Mock the ChromaDB client to avoid actual database interactions
        mock_collection = MagicMock()
        mock_persistent_client.return_value.get_or_create_collection.return_value = mock_collection

        # Yield the VectorStore instance with the mocked client
        vector_store = VectorStore(
            chroma_data_path="test_chroma_data",
            embedding_model="all-MiniLM-L6-v2"
        )
        yield vector_store, mock_collection

def test_semantic_search(vector_store_manager_instance):
    """
    Tests the semantic search functionality of the VectorStore.
    """
    vector_store, mock_collection = vector_store_manager_instance

    # Mock the query results from ChromaDB
    mock_collection.query.return_value = {
        "ids": [["note_1"]],
        "documents": [["some document"]],
        "metadatas": [[{"type": "Note"}]],
        "distances": [[0.1]]
    }

    # Perform a semantic search
    results = vector_store.semantic_search(query="test query")

    # Assert that the correct node ID is returned
    assert results['ids'][0] == ["note_1"]
    mock_collection.query.assert_called_once()

def test_add_node_to_vector_store(vector_store_manager_instance):
    """
    Tests that a node is correctly added to the vector store.
    """
    vector_store, mock_collection = vector_store_manager_instance

    # Create a sample node
    node_data = {
        "id": "note_2",
        "type": "Note",
        "properties": {"title": "Test Note", "content": "This is a test."}
    }

    # Add the node to the vector store
    vector_store.add_node(node_data)

    # Assert that the collection's add method was called with the correct parameters
    mock_collection.add.assert_called_once()
    args, kwargs = mock_collection.add.call_args
    assert kwargs["ids"] == ["note_2"]
    assert "Type: Note. Title: Test Note. Content: This is a test." in kwargs["documents"]

def test_delete_node_from_vector_store(vector_store_manager_instance):
    """
    Tests that a node is correctly deleted from the vector store.
    """
    vector_store, mock_collection = vector_store_manager_instance

    # Delete a node from the vector store
    vector_store.delete_node("note_3")

    # Assert that the collection's delete method was called with the correct ID
    mock_collection.delete.assert_called_once_with(ids=["note_3"])
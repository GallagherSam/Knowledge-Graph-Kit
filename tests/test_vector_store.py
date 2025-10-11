import pytest
from unittest.mock import patch, MagicMock, ANY
from app.vector_store import VectorStore
from app.config import Settings

@patch('chromadb.PersistentClient')
def test_vector_store_initialization_local(mock_persistent_client):
    """
    Tests that the VectorStore initializes with a PersistentClient for local ChromaDB.
    """
    mock_collection = MagicMock()
    mock_persistent_client.return_value.get_or_create_collection.return_value = mock_collection
    config = Settings(CHROMA_TYPE='local', CHROMA_DATA_PATH='/tmp/chroma')

    with patch('app.vector_store.config', config):
        vs = VectorStore()
        mock_persistent_client.assert_called_once_with(
            path='/tmp/chroma',
            settings=ANY
        )
        assert vs.collection is not None

@patch('chromadb.HttpClient')
def test_vector_store_initialization_hosted(mock_http_client):
    """
    Tests that the VectorStore initializes with an HttpClient for hosted ChromaDB.
    """
    mock_collection = MagicMock()
    mock_http_client.return_value.get_or_create_collection.return_value = mock_collection
    config = Settings(CHROMA_TYPE='hosted', CHROMA_HOST='localhost', CHROMA_PORT=8008)

    with patch('app.vector_store.config', config):
        vs = VectorStore()
        mock_http_client.assert_called_once_with(
            host='localhost',
            port=8008,
            settings=ANY
        )
        assert vs.collection is not None

@pytest.fixture
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
        yield VectorStore(), mock_collection

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
    assert results == ["note_1"]
    mock_collection.query.assert_called_once_with(
        query_texts=["test query"],
        n_results=10
    )

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
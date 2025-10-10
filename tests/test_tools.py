import pytest
from unittest.mock import patch, MagicMock

from app.tools import shared as shared_service

@patch('app.tools.shared.vector_store_manager')
def test_semantic_search_tool(mock_vector_store_manager):
    """
    Tests the semantic_search tool in the shared service layer.
    """
    # Mock the vector store manager's semantic_search to return a list of node IDs
    mock_vector_store_manager.semantic_search.return_value = ["note_1"]

    # Mock the crud.get_nodes_by_ids to return a list of nodes
    with patch('app.crud.get_nodes_by_ids') as mock_get_nodes_by_ids:
        mock_get_nodes_by_ids.return_value = [
            {"id": "note_1", "type": "Note", "properties": {"title": "Test Note", "content": "Content"}}
        ]

        # Call the semantic_search tool
        results = shared_service.semantic_search(query="test query")

        # Assert that the correct node is returned
        assert len(results) == 1
        assert results[0]["id"] == "note_1"
        assert results[0]["properties"]["title"] == "Test Note"

        # Verify that the mocks were called correctly
        mock_vector_store_manager.semantic_search.assert_called_once_with(
            query="test query", node_type=None
        )
        mock_get_nodes_by_ids.assert_called_once_with(["note_1"])
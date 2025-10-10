import pytest
from unittest.mock import patch

from app.tools import shared

@pytest.fixture
def mock_crud():
    """Fixture to mock the crud module."""
    with patch("app.tools.shared.crud", autospec=True) as mock_crud_module:
        yield mock_crud_module

def test_create_edge(mock_crud):
    """Test that create_edge calls the corresponding crud function."""
    shared.create_edge(source_id="1", label="connects", target_id="2")
    mock_crud.create_edge.assert_called_once_with(source_id="1", label="connects", target_id="2")

def test_get_related_nodes(mock_crud):
    """Test that get_related_nodes calls the corresponding crud function."""
    shared.get_related_nodes(node_id="1", label="friends")
    mock_crud.get_connected_nodes.assert_called_once_with(node_id="1", label="friends")

def test_search_nodes(mock_crud):
    """Test that search_nodes calls the corresponding crud function."""
    shared.search_nodes(query="test", node_type="Note", tags=["tag1"])
    mock_crud.search_nodes.assert_called_once_with(query="test", node_type="Note", tags=["tag1"])

def test_get_all_tags(mock_crud):
    """Test that get_all_tags calls the corresponding crud function."""
    shared.get_all_tags()
    mock_crud.get_all_tags.assert_called_once()
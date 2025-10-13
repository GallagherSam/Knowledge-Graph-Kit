import pytest
from unittest.mock import patch, MagicMock
from app.tools.shared import Shared

@pytest.fixture
def mock_crud():
    """Fixture to mock the crud module."""
    with patch("app.tools.shared.crud", autospec=True) as mock_crud_module:
        yield mock_crud_module

@pytest.fixture
def shared_instance(mock_mcp, mock_provider):
    """Fixture to create an instance of the Shared class for testing."""
    return Shared(mock_mcp, mock_provider)

def test_shared_init(shared_instance, mock_mcp):
    """Test that the Shared class registers its tools on initialization."""
    assert mock_mcp.tool.call_count == 8  # Count of tools in Shared class
    mock_mcp.tool.assert_any_call(shared_instance.create_edge)
    mock_mcp.tool.assert_any_call(shared_instance.delete_node)
    # Add other tool registration checks as needed

def test_create_edge(shared_instance, mock_crud, mock_db_session):
    """Test that create_edge calls the corresponding crud function."""
    shared_instance.create_edge(source_id="1", label="connects", target_id="2")
    mock_crud.create_edge.assert_called_once_with(db=mock_db_session, source_id="1", label="connects", target_id="2")

def test_get_related_nodes(shared_instance, mock_crud, mock_db_session):
    """Test that get_related_nodes calls the corresponding crud function."""
    shared_instance.get_related_nodes(node_id="1", label="friends")
    mock_crud.get_connected_nodes.assert_called_once_with(db=mock_db_session, node_id="1", label="friends")

def test_search_nodes(shared_instance, mock_crud, mock_db_session):
    """Test that search_nodes calls the corresponding crud function."""
    shared_instance.search_nodes(query="test", node_type="Note", tags=["tag1"])
    mock_crud.search_nodes.assert_called_once_with(db=mock_db_session, query="test", node_type="Note", tags=["tag1"])

def test_get_all_tags(shared_instance, mock_crud, mock_db_session):
    """Test that get_all_tags calls the corresponding crud function."""
    shared_instance.get_all_tags()
    mock_crud.get_all_tags.assert_called_once_with(db=mock_db_session)

def test_delete_node(shared_instance, mock_crud, mock_db_session, mock_vector_store_instance):
    """Test that delete_node calls the crud delete_node function."""
    shared_instance.delete_node(node_id="test_id")
    mock_crud.delete_node.assert_called_once_with(db=mock_db_session, vector_store=mock_vector_store_instance, node_id="test_id")

def test_delete_edge(shared_instance, mock_crud, mock_db_session):
    """Test that delete_edge calls the crud delete_edge_by_nodes function."""
    shared_instance.delete_edge(source_id="s_id", target_id="t_id", label="label")
    mock_crud.delete_edge_by_nodes.assert_called_once_with(
        db=mock_db_session, source_id="s_id", target_id="t_id", label="label"
    )

def test_rename_tag(shared_instance, mock_crud, mock_db_session):
    """Test that rename_tag calls the crud rename_tag function."""
    shared_instance.rename_tag(old_tag="old", new_tag="new")
    mock_crud.rename_tag.assert_called_once_with(db=mock_db_session, old_tag="old", new_tag="new")

def test_semantic_search(shared_instance, mock_crud, mock_db_session, mock_vector_store_instance):
    """Tests the semantic_search tool."""
    mock_vector_store_instance.semantic_search.return_value = ["note_1"]
    mock_crud.get_nodes_by_ids.return_value = [
        {"id": "note_1", "type": "Note", "properties": {"title": "Test Note", "content": "Content"}}
    ]

    results = shared_instance.semantic_search(query="test query")

    assert len(results) == 1
    assert results[0]["id"] == "note_1"
    mock_vector_store_instance.semantic_search.assert_called_once_with(query="test query", node_type=None)
    mock_crud.get_nodes_by_ids.assert_called_once_with(db=mock_db_session, node_ids=["note_1"])
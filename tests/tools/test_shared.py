import pytest
from unittest.mock import patch, MagicMock

from app.tools import shared

@pytest.fixture
def mock_crud():
    """Fixture to mock the crud module."""
    with patch("app.tools.shared.crud", autospec=True) as mock_crud_module:
        yield mock_crud_module

@pytest.fixture
def mock_db():
    """Fixture to mock the db session."""
    return MagicMock()

@pytest.fixture
def mock_vector_store():
    """Fixture to mock the vector store."""
    return MagicMock()

def test_create_edge(mock_crud, mock_db):
    """Test that create_edge calls the corresponding crud function."""
    shared.create_edge(db=mock_db, source_id="1", label="connects", target_id="2")
    mock_crud.create_edge.assert_called_once_with(db=mock_db, source_id="1", label="connects", target_id="2")

def test_get_related_nodes(mock_crud, mock_db):
    """Test that get_related_nodes calls the corresponding crud function."""
    shared.get_related_nodes(db=mock_db, node_id="1", label="friends")
    mock_crud.get_connected_nodes.assert_called_once_with(db=mock_db, node_id="1", label="friends")

def test_search_nodes(mock_crud, mock_db):
    """Test that search_nodes calls the corresponding crud function."""
    shared.search_nodes(db=mock_db, query="test", node_type="Note", tags=["tag1"])
    mock_crud.search_nodes.assert_called_once_with(db=mock_db, query="test", node_type="Note", tags=["tag1"])

def test_get_all_tags(mock_crud, mock_db):
    """Test that get_all_tags calls the corresponding crud function."""
    shared.get_all_tags(db=mock_db)
    mock_crud.get_all_tags.assert_called_once_with(db=mock_db)


def test_delete_node(mock_crud, mock_db, mock_vector_store):
    """Test that the shared delete_node function calls the crud delete_node function."""
    shared.delete_node(db=mock_db, vector_store=mock_vector_store, node_id="test_id")
    mock_crud.delete_node.assert_called_once_with(db=mock_db, vector_store=mock_vector_store, node_id="test_id")


def test_delete_edge(mock_crud, mock_db):
    """Test that the shared delete_edge function calls the crud delete_edge_by_nodes function."""
    shared.delete_edge(db=mock_db, source_id="s_id", target_id="t_id", label="label")
    mock_crud.delete_edge_by_nodes.assert_called_once_with(
        db=mock_db, source_id="s_id", target_id="t_id", label="label"
    )


def test_rename_tag(mock_crud, mock_db):
    """Test that the shared rename_tag function calls the crud rename_tag function."""
    shared.rename_tag(db=mock_db, old_tag="old", new_tag="new")
    mock_crud.rename_tag.assert_called_once_with(db=mock_db, old_tag="old", new_tag="new")
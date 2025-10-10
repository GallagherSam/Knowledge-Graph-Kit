import pytest
from unittest.mock import MagicMock, patch, ANY
from pydantic import ValidationError
import datetime

from app import crud
from app.models import TaskProperties, NoteProperties, PersonProperties, ProjectProperties

@pytest.fixture
def mock_state_manager():
    """Fixture to mock the state_manager."""
    with patch("app.crud.state_manager", autospec=True) as mock_state:
        yield mock_state

def test_create_node_success(mock_state_manager):
    """Test successful creation of a node."""
    properties = {"description": "Test Task", "status": "todo"}

    # Mock the return value of the state_manager's add_node method
    mock_state_manager.add_node.return_value = {
        "id": "some-uuid",
        "type": "Task",
        "properties": properties
    }

    new_node = crud.create_node(node_type="Task", properties=properties)

    assert new_node["type"] == "Task"
    assert new_node["properties"]["description"] == "Test Task"
    mock_state_manager.add_node.assert_called_once()

def test_create_node_invalid_properties(mock_state_manager):
    """Test creating a node with invalid properties raises ValidationError."""
    with pytest.raises(ValidationError):
        crud.create_node(node_type="Task", properties={"invalid_prop": "value"})

def test_get_nodes_no_filter(mock_state_manager):
    """Test retrieving all nodes without any filters."""
    mock_nodes = [{"id": "1", "type": "Task", "properties": {}}]
    mock_state_manager.read_nodes.return_value = mock_nodes

    nodes = crud.get_nodes()
    assert nodes == mock_nodes

def test_get_nodes_by_type(mock_state_manager):
    """Test filtering nodes by type."""
    mock_nodes = [
        {"id": "1", "type": "Task", "properties": {}},
        {"id": "2", "type": "Note", "properties": {}},
    ]
    mock_state_manager.read_nodes.return_value = mock_nodes

    nodes = crud.get_nodes(node_type="Task")
    assert len(nodes) == 1
    assert nodes[0]["type"] == "Task"

def test_get_nodes_by_property(mock_state_manager):
    """Test filtering nodes by a specific property."""
    mock_nodes = [
        {"id": "1", "type": "Task", "properties": {"status": "done"}},
        {"id": "2", "type": "Task", "properties": {"status": "todo"}},
    ]
    mock_state_manager.read_nodes.return_value = mock_nodes

    nodes = crud.get_nodes(node_type="Task", status="done")
    assert len(nodes) == 1
    assert nodes[0]["properties"]["status"] == "done"

def test_update_node_success(mock_state_manager):
    """Test successfully updating a node."""
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    mock_nodes = [{"id": "1", "type": "Note", "properties": {"title": "Old", "content": "Content", "created_at": created_at, "modified_at": created_at, "tags": []}}]
    mock_state_manager.read_nodes.return_value = mock_nodes

    updated_properties = {"title": "New", "content": "Content", "created_at": created_at, "modified_at": created_at, "tags": []}
    mock_state_manager.update_node_in_db.return_value = {"id": "1", "type": "Note", "properties": updated_properties}


    updated_node = crud.update_node(node_id="1", properties={"title": "New"})
    assert updated_node["properties"]["title"] == "New"

    mock_state_manager.update_node_in_db.assert_called_once_with("1", ANY)

def test_update_node_not_found(mock_state_manager):
    """Test that updating a non-existent node raises an exception."""
    mock_state_manager.read_nodes.return_value = []
    with pytest.raises(ValueError) as exc_info:
        crud.update_node(node_id="1", properties={"title": "New"})
    assert "not found" in str(exc_info.value)

def test_delete_node_success(mock_state_manager):
    """Test successful deletion of a node."""
    crud.delete_node("1")
    mock_state_manager.delete_node.assert_called_once_with("1")

def test_create_edge_success(mock_state_manager):
    """Test successful creation of an edge."""
    mock_nodes = [{"id": "1", "type": "Task"}, {"id": "2", "type": "Project"}]
    mock_state_manager.read_nodes.return_value = mock_nodes

    mock_state_manager.add_edge.return_value = {"id": "e1", "source_id": "1", "target_id": "2", "label": "part_of"}

    new_edge = crud.create_edge(source_id="1", target_id="2", label="part_of")
    assert new_edge["source_id"] == "1"
    assert new_edge["target_id"] == "2"
    mock_state_manager.add_edge.assert_called_once()

def test_delete_edge_success(mock_state_manager):
    """Test successful deletion of an edge."""
    crud.delete_edge("e1")
    mock_state_manager.delete_edge.assert_called_once_with("e1")


def test_create_edge_node_not_found(mock_state_manager):
    """Test creating an edge with a non-existent source or target node."""
    mock_state_manager.read_nodes.return_value = [{"id": "1", "type": "Task"}]
    with pytest.raises(ValueError) as exc_info:
        crud.create_edge(source_id="1", target_id="2", label="part_of")
    assert "not found" in str(exc_info.value)

def test_get_connected_nodes(mock_state_manager):
    """Test retrieving connected nodes."""
    mock_nodes = [
        {"id": "1", "type": "Task"},
        {"id": "2", "type": "Project"},
        {"id": "3", "type": "Person"},
    ]
    mock_edges = [
        {"id": "e1", "source_id": "1", "target_id": "2", "label": "part_of"},
        {"id": "e2", "source_id": "3", "target_id": "1", "label": "assigned_to"},
    ]
    mock_state_manager.read_nodes.return_value = mock_nodes
    mock_state_manager.read_edges.return_value = mock_edges

    connected = crud.get_connected_nodes(node_id="1")
    assert len(connected) == 2
    connected_ids = {node["id"] for node in connected}
    assert "2" in connected_ids
    assert "3" in connected_ids

def test_search_nodes(mock_state_manager):
    """Test searching for nodes with various criteria."""
    mock_nodes = [
        {"id": "1", "type": "Note", "properties": {"title": "My Note", "content": "About cats", "tags": ["personal"]}},
        {"id": "2", "type": "Task", "properties": {"description": "A task about dogs", "tags": ["work"]}},
    ]
    mock_state_manager.read_nodes.return_value = mock_nodes

    # Test search by query
    results = crud.search_nodes(query="cats")
    assert len(results) == 1
    assert results[0]["id"] == "1"

    # Test search by type
    results = crud.search_nodes(node_type="Task")
    assert len(results) == 1
    assert results[0]["id"] == "2"

    # Test search by tags
    results = crud.search_nodes(tags=["work"])
    assert len(results) == 1
    assert results[0]["id"] == "2"

def test_get_all_tags(mock_state_manager):
    """Test retrieving all unique, sorted tags."""
    mock_nodes = [
        {"id": "1", "properties": {"tags": ["work", "urgent"]}},
        {"id": "2", "properties": {"tags": ["personal"]}},
        {"id": "3", "properties": {"tags": ["work", "review"]}},
    ]
    mock_state_manager.read_nodes.return_value = mock_nodes

    tags = crud.get_all_tags()
    assert tags == ["personal", "review", "urgent", "work"]
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


def test_delete_edge_by_nodes_success(mock_state_manager):
    """Test successful deletion of an edge by source, target, and label."""
    mock_edges = [
        {"id": "e1", "source_id": "1", "target_id": "2", "label": "part_of"},
        {"id": "e2", "source_id": "3", "target_id": "1", "label": "assigned_to"},
    ]
    mock_state_manager.read_edges.return_value = mock_edges
    mock_state_manager.delete_edge.return_value = True

    result = crud.delete_edge_by_nodes(source_id="1", target_id="2", label="part_of")

    assert result is True
    mock_state_manager.delete_edge.assert_called_once_with("e1")


def test_delete_edge_by_nodes_not_found(mock_state_manager):
    """Test that trying to delete a non-existent edge by nodes fails."""
    mock_state_manager.read_edges.return_value = []
    result = crud.delete_edge_by_nodes(source_id="1", target_id="2", label="part_of")
    assert result is False
    mock_state_manager.delete_edge.assert_not_called()


def test_rename_tag_success(mock_state_manager):
    """Test successfully renaming a tag on multiple nodes."""
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    mock_nodes = [
        {
            "id": "1",
            "type": "Note",
            "properties": {"title": "Note 1", "content": "c1", "tags": ["old_tag", "other"], "created_at": created_at, "modified_at": created_at},
        },
        {
            "id": "2",
            "type": "Task",
            "properties": {"description": "Task 1", "tags": ["old_tag"], "created_at": created_at, "modified_at": created_at},
        },
        {"id": "3", "type": "Project", "properties": {"name": "p1", "description": "d1", "tags": ["another_tag"], "created_at": created_at, "modified_at": created_at}},
    ]
    mock_state_manager.read_nodes.return_value = mock_nodes

    # Create a dictionary to map node IDs to their types for the mock
    node_type_map = {node["id"]: node["type"] for node in mock_nodes}

    # Mock the update call to return a value to confirm it was called
    mock_state_manager.update_node_in_db.side_effect = lambda node_id, props: {
        "id": node_id,
        "properties": props,
        "type": node_type_map.get(node_id),
    }


    updated_nodes = crud.rename_tag(old_tag="old_tag", new_tag="new_tag")

    assert len(updated_nodes) == 2
    assert mock_state_manager.update_node_in_db.call_count == 2

    # Check the call for the first node
    call_args_1 = mock_state_manager.update_node_in_db.call_args_list[0]
    assert call_args_1.args[0] == "1"
    assert sorted(call_args_1.args[1]["tags"]) == ["new_tag", "other"]

    # Check the call for the second node
    call_args_2 = mock_state_manager.update_node_in_db.call_args_list[1]
    assert call_args_2.args[0] == "2"
    assert call_args_2.args[1]["tags"] == ["new_tag"]
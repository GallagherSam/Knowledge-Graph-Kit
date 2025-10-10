import pytest
from unittest.mock import patch, MagicMock

from app.tools import task

@pytest.fixture
def mock_crud():
    """Fixture to mock the crud module."""
    with patch("app.tools.task.crud", autospec=True) as mock_crud_module:
        yield mock_crud_module

def test_create_task(mock_crud):
    """Test creating a task successfully."""
    mock_crud.create_node.return_value = {"id": "1", "type": "Task", "properties": {"description": "New Task"}}

    result = task.create_task(description="New Task", status="todo", tags=["work"])

    assert result["properties"]["description"] == "New Task"
    mock_crud.create_node.assert_called_once()
    # We don't need to assert the exact properties dict because Pydantic model details are tested elsewhere.
    # Just checking the call is enough.

def test_get_tasks_no_filters(mock_crud):
    """Test getting all tasks when no filters are provided."""
    mock_crud.get_nodes.return_value = [{"id": "1", "type": "Task"}]

    result = task.get_tasks()

    assert len(result) == 1
    mock_crud.get_nodes.assert_called_once_with(node_type="Task")

def test_get_tasks_with_status_filter(mock_crud):
    """Test filtering tasks by status."""
    task.get_tasks(status="done")
    mock_crud.get_nodes.assert_called_once_with(node_type="Task", status="done")

def test_get_tasks_with_tags_filter(mock_crud):
    """Test filtering tasks by tags."""
    mock_nodes = [
        {"id": "1", "properties": {"tags": ["a", "b"]}},
        {"id": "2", "properties": {"tags": ["b", "c"]}},
    ]
    mock_crud.get_nodes.return_value = mock_nodes

    result = task.get_tasks(tags=["c"])

    assert len(result) == 1
    assert result[0]["id"] == "2"
    mock_crud.get_nodes.assert_called_once_with(node_type="Task")


def test_update_task(mock_crud):
    """Test updating a task successfully."""
    mock_crud.update_node.return_value = {"id": "1", "properties": {"status": "done"}}

    result = task.update_task(task_id="1", status="done")

    assert result["properties"]["status"] == "done"
    mock_crud.update_node.assert_called_once_with(
        node_id="1",
        properties={"status": "done"}
    )

def test_update_task_no_properties(mock_crud):
    """Test that updating a task with no properties raises a ValueError."""
    with pytest.raises(ValueError):
        task.update_task(task_id="1")

    mock_crud.update_node.assert_not_called()
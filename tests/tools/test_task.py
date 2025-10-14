import pytest
from unittest.mock import patch, MagicMock
from app.tools.task import Tasks

@pytest.fixture
def mock_crud():
    """Fixture to mock the crud module."""
    with patch("app.tools.task.crud", autospec=True) as mock_crud_module:
        yield mock_crud_module

@pytest.fixture
def tasks_instance(mock_mcp, mock_provider):
    """Fixture to create an instance of the Tasks class for testing."""
    return Tasks(mock_mcp, mock_provider)

def test_tasks_init(tasks_instance, mock_mcp):
    """Test that the Tasks class registers its tools on initialization."""
    assert mock_mcp.tool.call_count == 3
    mock_mcp.tool.assert_any_call(tasks_instance.create_task)
    mock_mcp.tool.assert_any_call(tasks_instance.get_tasks)
    mock_mcp.tool.assert_any_call(tasks_instance.update_task)

def test_create_task(tasks_instance, mock_crud, mock_db_session, mock_vector_store_instance):
    """Test creating a task successfully."""
    mock_crud.create_node.return_value = {"id": "1", "type": "Task", "properties": {"description": "New Task"}}

    result = tasks_instance.create_task(description="New Task", status="todo", tags=["work"])

    assert result["properties"]["description"] == "New Task"
    mock_crud.create_node.assert_called_once()
    call_args, call_kwargs = mock_crud.create_node.call_args
    assert call_kwargs["db"] == mock_db_session
    assert call_kwargs["vector_store"] == mock_vector_store_instance
    assert call_kwargs["node_type"] == "Task"
    assert call_kwargs["properties"]["description"] == "New Task"

def test_get_tasks_no_filters(tasks_instance, mock_crud, mock_db_session):
    """Test getting all tasks when no filters are provided."""
    mock_crud.get_nodes.return_value = [{"id": "1", "type": "Task"}]

    result = tasks_instance.get_tasks()

    assert len(result) == 1
    mock_crud.get_nodes.assert_called_once_with(db=mock_db_session, node_type="Task")

def test_get_tasks_with_status_filter(tasks_instance, mock_crud, mock_db_session):
    """Test filtering tasks by status."""
    tasks_instance.get_tasks(status="done")
    mock_crud.get_nodes.assert_called_once_with(db=mock_db_session, node_type="Task", status="done")

def test_get_tasks_with_tags_filter(tasks_instance, mock_crud, mock_db_session):
    """Test filtering tasks by tags."""
    mock_crud.get_nodes.return_value = [
        {"id": "1", "properties": {"tags": ["a", "b"]}},
        {"id": "2", "properties": {"tags": ["b", "c"]}},
        {"id": "3", "properties": {"tags": ["a", "c"]}},
    ]

    result = tasks_instance.get_tasks(tags=["c"])

    assert len(result) == 2
    assert result[0]["id"] == "2"
    assert result[1]["id"] == "3"
    mock_crud.get_nodes.assert_called_once_with(db=mock_db_session, node_type="Task")

def test_get_tasks_with_status_and_tags_filter(tasks_instance, mock_crud, mock_db_session):
    """Test filtering tasks by both status and tags."""
    mock_crud.get_nodes.return_value = [
        {"id": "1", "properties": {"status": "done", "tags": ["a", "b"]}},
        {"id": "2", "properties": {"status": "done", "tags": ["b", "c"]}},
    ]

    result = tasks_instance.get_tasks(status="done", tags=["c"])

    assert len(result) == 1
    assert result[0]["id"] == "2"
    mock_crud.get_nodes.assert_called_once_with(db=mock_db_session, node_type="Task", status="done")


def test_update_task(tasks_instance, mock_crud, mock_db_session, mock_vector_store_instance):
    """Test updating a task successfully."""
    mock_crud.update_node.return_value = {"id": "1", "properties": {"status": "done"}}

    result = tasks_instance.update_task(task_id="1", status="done")

    assert result["properties"]["status"] == "done"
    mock_crud.update_node.assert_called_once_with(
        db=mock_db_session,
        vector_store=mock_vector_store_instance,
        node_id="1",
        properties={"status": "done"}
    )

def test_update_task_no_properties(tasks_instance):
    """Test that updating a task with no properties raises a ValueError."""
    with pytest.raises(ValueError, match="No properties provided to update"):
        tasks_instance.update_task(task_id="1")

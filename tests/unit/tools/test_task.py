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

def test_get_tasks_by_status(tasks_instance, mock_crud):
    """Test retrieving tasks and filtering them by status."""
    # 1. Arrange: Mock the return value of search_nodes to include tasks with various statuses.
    mock_tasks = [
        {"id": "1", "type": "Task", "properties": {"description": "Task 1", "status": "done"}},
        {"id": "2", "type": "Task", "properties": {"description": "Task 2", "status": "todo"}},
        {"id": "3", "type": "Task", "properties": {"description": "Task 3", "status": "done"}},
        {"id": "4", "type": "Task", "properties": {"description": "Task 4", "status": "in_progress"}},
    ]
    mock_crud.search_nodes.return_value = mock_tasks

    # 2. Act: Call the method to get tasks with the 'done' status.
    result = tasks_instance.get_tasks_by_status(status="done")

    # 3. Assert
    # Verify that search_nodes was called to fetch all tasks.
    mock_crud.search_nodes.assert_called_once_with(db=tasks_instance.provider.get_db().__enter__(), node_type="Task")
    
    # Verify that the result is correctly filtered.
    assert len(result) == 2
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "3"
    assert all(task["properties"]["status"] == "done" for task in result)

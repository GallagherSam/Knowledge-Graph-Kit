import pytest
from unittest.mock import patch, MagicMock

from app.tools import project

@pytest.fixture
def mock_crud():
    """Fixture to mock the crud module."""
    with patch("app.tools.project.crud", autospec=True) as mock_crud_module:
        yield mock_crud_module

@pytest.fixture
def mock_db():
    """Fixture to mock the db session."""
    return MagicMock()

@pytest.fixture
def mock_vector_store():
    """Fixture to mock the vector store."""
    return MagicMock()

def test_create_project(mock_crud, mock_db, mock_vector_store):
    """Test creating a project successfully."""
    mock_crud.create_node.return_value = {"id": "1", "type": "Project", "properties": {"name": "New Project"}}

    result = project.create_project(db=mock_db, vector_store=mock_vector_store, name="New Project", description="A test project.", tags=["test"])

    assert result["properties"]["name"] == "New Project"
    mock_crud.create_node.assert_called_once_with(
        db=mock_db,
        vector_store=mock_vector_store,
        node_type="Project",
        properties={"name": "New Project", "description": "A test project.", "status": "active", "tags": ["test"]}
    )

def test_get_projects_no_filter(mock_crud, mock_db):
    """Test getting all projects when no filters are provided."""
    mock_crud.get_nodes.return_value = [{"id": "1", "type": "Project"}]

    result = project.get_projects(db=mock_db)

    assert len(result) == 1
    mock_crud.get_nodes.assert_called_once_with(db=mock_db, node_type="Project")

def test_get_projects_with_status_filter(mock_crud, mock_db):
    """Test filtering projects by status."""
    project.get_projects(db=mock_db, status="archived")
    mock_crud.get_nodes.assert_called_once_with(db=mock_db, node_type="Project", status="archived")

def test_get_projects_with_tags_filter(mock_crud, mock_db):
    """Test filtering projects by tags."""
    mock_nodes = [
        {"id": "1", "properties": {"tags": ["a", "b"]}},
        {"id": "2", "properties": {"tags": ["b", "c"]}},
    ]
    mock_crud.get_nodes.return_value = mock_nodes

    result = project.get_projects(db=mock_db, tags=["c"])

    assert len(result) == 1
    assert result[0]["id"] == "2"

def test_update_project(mock_crud, mock_db, mock_vector_store):
    """Test updating a project successfully."""
    mock_crud.update_node.return_value = {"id": "1", "properties": {"status": "archived"}}

    result = project.update_project(db=mock_db, vector_store=mock_vector_store, project_id="1", status="archived")

    assert result["properties"]["status"] == "archived"
    mock_crud.update_node.assert_called_once_with(
        db=mock_db,
        vector_store=mock_vector_store,
        node_id="1",
        properties={"status": "archived"}
    )

def test_update_project_no_properties(mock_crud, mock_db, mock_vector_store):
    """Test that updating a project with no properties raises a ValueError."""
    with pytest.raises(ValueError):
        project.update_project(db=mock_db, vector_store=mock_vector_store, project_id="1")

    mock_crud.update_node.assert_not_called()
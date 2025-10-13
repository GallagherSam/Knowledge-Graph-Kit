import pytest
from unittest.mock import patch, MagicMock
from app.tools.project import Projects

@pytest.fixture
def mock_crud():
    """Fixture to mock the crud module."""
    with patch("app.tools.project.crud", autospec=True) as mock_crud_module:
        yield mock_crud_module

@pytest.fixture
def projects_instance(mock_mcp, mock_provider):
    """Fixture to create an instance of the Projects class for testing."""
    return Projects(mock_mcp, mock_provider)

def test_projects_init(projects_instance, mock_mcp):
    """Test that the Projects class registers its tools on initialization."""
    assert mock_mcp.tool.call_count == 3
    mock_mcp.tool.assert_any_call(projects_instance.create_project)
    mock_mcp.tool.assert_any_call(projects_instance.get_projects)
    mock_mcp.tool.assert_any_call(projects_instance.update_project)

def test_create_project(projects_instance, mock_crud, mock_db_session, mock_vector_store_instance):
    """Test creating a project successfully."""
    mock_crud.create_node.return_value = {"id": "1", "type": "Project", "properties": {"name": "New Project"}}

    result = projects_instance.create_project(name="New Project", description="A test project.", tags=["test"])

    assert result["properties"]["name"] == "New Project"
    mock_crud.create_node.assert_called_once_with(
        db=mock_db_session,
        vector_store=mock_vector_store_instance,
        node_type="Project",
        properties={"name": "New Project", "description": "A test project.", "status": "active", "tags": ["test"]}
    )

def test_get_projects_no_filter(projects_instance, mock_crud, mock_db_session):
    """Test getting all projects when no filters are provided."""
    mock_crud.get_nodes.return_value = [{"id": "1", "type": "Project"}]

    result = projects_instance.get_projects()

    assert len(result) == 1
    mock_crud.get_nodes.assert_called_once_with(db=mock_db_session, node_type="Project")

def test_get_projects_with_status_filter(projects_instance, mock_crud, mock_db_session):
    """Test filtering projects by status."""
    projects_instance.get_projects(status="archived")
    mock_crud.get_nodes.assert_called_once_with(db=mock_db_session, node_type="Project", properties={"status": "archived"})

def test_get_projects_with_tags_filter(projects_instance, mock_crud, mock_db_session):
    """Test filtering projects by tags."""
    projects_instance.get_projects(tags=["c"])
    mock_crud.get_nodes.assert_called_once_with(db=mock_db_session, node_type="Project", tags=["c"])

def test_update_project(projects_instance, mock_crud, mock_db_session, mock_vector_store_instance):
    """Test updating a project successfully."""
    mock_crud.update_node.return_value = {"id": "1", "properties": {"status": "archived"}}

    result = projects_instance.update_project(project_id="1", status="archived")

    assert result["properties"]["status"] == "archived"
    mock_crud.update_node.assert_called_once_with(
        db=mock_db_session,
        vector_store=mock_vector_store_instance,
        node_id="1",
        properties={"status": "archived"}
    )

def test_update_project_no_properties(projects_instance):
    """Test that updating a project with no properties raises a ValueError."""
    with pytest.raises(ValueError, match="No properties provided to update"):
        projects_instance.update_project(project_id="1")

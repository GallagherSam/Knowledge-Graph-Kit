from unittest.mock import patch

import pytest

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


def test_create_project(projects_instance, mock_crud, mock_db_session, mock_vector_store_instance):
    """Test creating a project successfully."""
    mock_crud.create_node.return_value = {
        "id": "1",
        "type": "Project",
        "properties": {"name": "New Project"},
    }

    result = projects_instance.create_project(
        name="New Project", description="A test project.", tags=["test"]
    )

    assert result["properties"]["name"] == "New Project"
    # Check that create_node was called with the right parameters
    # Verify datetime fields are auto-generated
    call_args = mock_crud.create_node.call_args
    assert call_args[1]["db"] == mock_db_session
    assert call_args[1]["vector_store"] == mock_vector_store_instance
    assert call_args[1]["node_type"] == "Project"
    assert call_args[1]["properties"]["name"] == "New Project"
    assert call_args[1]["properties"]["description"] == "A test project."
    assert call_args[1]["properties"]["status"] == "active"
    assert call_args[1]["properties"]["tags"] == ["test"]
    assert "created_at" in call_args[1]["properties"]
    assert "modified_at" in call_args[1]["properties"]


def test_update_project(projects_instance, mock_crud, mock_db_session, mock_vector_store_instance):
    """Test updating a project successfully."""
    mock_crud.update_node.return_value = {"id": "1", "properties": {"status": "archived"}}

    result = projects_instance.update_project(project_id="1", status="archived")

    assert result["properties"]["status"] == "archived"
    mock_crud.update_node.assert_called_once_with(
        db=mock_db_session,
        vector_store=mock_vector_store_instance,
        node_id="1",
        properties={"status": "archived"},
    )


def test_update_project_no_properties(projects_instance):
    """Test that updating a project with no properties raises a ValueError."""
    with pytest.raises(ValueError, match="No properties provided to update"):
        projects_instance.update_project(project_id="1")

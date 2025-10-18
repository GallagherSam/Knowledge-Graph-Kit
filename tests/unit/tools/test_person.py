from unittest.mock import patch

import pytest

from app.tools.person import Persons


@pytest.fixture
def mock_crud():
    """Fixture to mock the crud module."""
    with patch("app.tools.person.crud", autospec=True) as mock_crud_module:
        yield mock_crud_module

@pytest.fixture
def persons_instance(mock_mcp, mock_provider):
    """Fixture to create an instance of the Persons class for testing."""
    return Persons(mock_mcp, mock_provider)

def test_create_person(persons_instance, mock_crud, mock_db_session, mock_vector_store_instance):
    """Test creating a person successfully."""
    mock_crud.create_node.return_value = {"id": "1", "type": "Person", "properties": {"name": "John Doe"}}

    result = persons_instance.create_person(name="John Doe", tags=["friend"])

    assert result["properties"]["name"] == "John Doe"
    # Check that create_node was called with the right parameters
    # Use ANY for datetime fields since they're auto-generated
    call_args = mock_crud.create_node.call_args
    assert call_args[1]["db"] == mock_db_session
    assert call_args[1]["vector_store"] == mock_vector_store_instance
    assert call_args[1]["node_type"] == "Person"
    assert call_args[1]["properties"]["name"] == "John Doe"
    assert call_args[1]["properties"]["tags"] == ["friend"]
    assert call_args[1]["properties"]["metadata"] == {}
    assert "created_at" in call_args[1]["properties"]
    assert "modified_at" in call_args[1]["properties"]

def test_update_person(persons_instance, mock_crud, mock_db_session, mock_vector_store_instance):
    """Test updating a person successfully."""
    mock_crud.update_node.return_value = {"id": "1", "properties": {"name": "Jane Doe"}}

    result = persons_instance.update_person(person_id="1", name="Jane Doe")

    assert result["properties"]["name"] == "Jane Doe"
    mock_crud.update_node.assert_called_once_with(
        db=mock_db_session,
        vector_store=mock_vector_store_instance,
        node_id="1",
        properties={"name": "Jane Doe"}
    )

def test_update_person_no_properties(persons_instance):
    """Test that updating a person with no properties raises a ValueError."""
    with pytest.raises(ValueError, match="No properties provided to update"):
        persons_instance.update_person(person_id="1")

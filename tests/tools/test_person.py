import pytest
from unittest.mock import patch, MagicMock

from app.tools import person

@pytest.fixture
def mock_crud():
    """Fixture to mock the crud module."""
    with patch("app.tools.person.crud", autospec=True) as mock_crud_module:
        yield mock_crud_module

def test_create_person(mock_crud):
    """Test creating a person successfully."""
    mock_crud.create_node.return_value = {"id": "1", "type": "Person", "properties": {"name": "John Doe"}}

    result = person.create_person(name="John Doe", tags=["friend"])

    assert result["properties"]["name"] == "John Doe"
    mock_crud.create_node.assert_called_once_with(
        node_type="Person",
        properties={"name": "John Doe", "tags": ["friend"], "metadata": {}}
    )

def test_get_persons_no_filter(mock_crud):
    """Test getting all persons when no filters are provided."""
    mock_crud.get_nodes.return_value = [{"id": "1", "type": "Person"}]

    result = person.get_persons()

    assert len(result) == 1
    mock_crud.get_nodes.assert_called_once_with(node_type="Person")

def test_get_persons_with_name_filter(mock_crud):
    """Test filtering persons by name."""
    person.get_persons(name="John Doe")
    mock_crud.get_nodes.assert_called_once_with(node_type="Person", name="John Doe")

def test_get_persons_with_tags_filter(mock_crud):
    """Test filtering persons by tags."""
    mock_nodes = [
        {"id": "1", "properties": {"tags": ["a", "b"]}},
        {"id": "2", "properties": {"tags": ["b", "c"]}},
    ]
    mock_crud.get_nodes.return_value = mock_nodes

    result = person.get_persons(tags=["c"])

    assert len(result) == 1
    assert result[0]["id"] == "2"

def test_update_person(mock_crud):
    """Test updating a person successfully."""
    mock_crud.update_node.return_value = {"id": "1", "properties": {"name": "Jane Doe"}}

    result = person.update_person(person_id="1", name="Jane Doe")

    assert result["properties"]["name"] == "Jane Doe"
    mock_crud.update_node.assert_called_once_with(
        node_id="1",
        properties={"name": "Jane Doe"}
    )

def test_update_person_no_properties(mock_crud):
    """Test that updating a person with no properties raises a ValueError."""
    with pytest.raises(ValueError):
        person.update_person(person_id="1")

    mock_crud.update_node.assert_not_called()
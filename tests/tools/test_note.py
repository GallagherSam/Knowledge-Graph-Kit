import pytest
from unittest.mock import patch, MagicMock

from app.tools import note

@pytest.fixture
def mock_crud():
    """Fixture to mock the crud module."""
    with patch("app.tools.note.crud", autospec=True) as mock_crud_module:
        yield mock_crud_module

def test_create_note(mock_crud):
    """Test creating a note successfully."""
    mock_crud.create_node.return_value = {"id": "1", "type": "Note", "properties": {"title": "Test", "content": "Content"}}

    result = note.create_note(title="Test", content="Content", tags=["tag1"])

    assert result["properties"]["title"] == "Test"

    mock_crud.create_node.assert_called_once()
    call_args, call_kwargs = mock_crud.create_node.call_args
    assert call_kwargs["node_type"] == "Note"
    assert call_kwargs["properties"]["title"] == "Test"
    assert call_kwargs["properties"]["content"] == "Content"
    assert call_kwargs["properties"]["tags"] == ["tag1"]
    assert "created_at" in call_kwargs["properties"]
    assert "modified_at" in call_kwargs["properties"]

def test_get_notes_no_tags(mock_crud):
    """Test getting all notes when no tags are provided."""
    mock_crud.get_nodes.return_value = [{"id": "1", "type": "Note"}]

    result = note.get_notes()

    assert len(result) == 1
    mock_crud.get_nodes.assert_called_once_with(node_type="Note")

def test_get_notes_with_tags(mock_crud):
    """Test filtering notes by tags."""
    mock_notes = [
        {"id": "1", "properties": {"tags": ["a", "b"]}},
        {"id": "2", "properties": {"tags": ["b", "c"]}},
        {"id": "3", "properties": {"tags": ["d"]}},
    ]
    mock_crud.get_nodes.return_value = mock_notes

    result = note.get_notes(tags=["a", "c"])

    assert len(result) == 2
    result_ids = {n["id"] for n in result}
    assert "1" in result_ids
    assert "2" in result_ids

def test_update_note(mock_crud):
    """Test updating a note successfully."""
    mock_crud.update_node.return_value = {"id": "1", "properties": {"title": "New Title"}}

    result = note.update_note(note_id="1", title="New Title")

    assert result["properties"]["title"] == "New Title"

    mock_crud.update_node.assert_called_once()
    call_args, call_kwargs = mock_crud.update_node.call_args
    assert call_kwargs["node_id"] == "1"
    assert call_kwargs["properties"] == {"title": "New Title"}

def test_update_note_no_properties(mock_crud):
    """Test that updating a note with no properties raises a ValueError."""
    with pytest.raises(ValueError):
        note.update_note(note_id="1")

    mock_crud.update_node.assert_not_called()
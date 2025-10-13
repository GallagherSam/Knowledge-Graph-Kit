import pytest
from unittest.mock import patch, MagicMock
from app.tools.note import Notes

@pytest.fixture
def mock_crud():
    """Fixture to mock the crud module."""
    with patch("app.tools.note.crud", autospec=True) as mock_crud_module:
        yield mock_crud_module

@pytest.fixture
def notes_instance(mock_mcp, mock_provider):
    """Fixture to create an instance of the Notes class for testing."""
    return Notes(mock_mcp, mock_provider)

def test_notes_init(notes_instance, mock_mcp):
    """Test that the Notes class registers its tools on initialization."""
    assert mock_mcp.tool.call_count == 3
    mock_mcp.tool.assert_any_call(notes_instance.create_note)
    mock_mcp.tool.assert_any_call(notes_instance.get_notes)
    mock_mcp.tool.assert_any_call(notes_instance.update_note)

def test_create_note(notes_instance, mock_crud, mock_provider, mock_db_session, mock_vector_store_instance):
    """Test creating a note successfully."""
    mock_crud.create_node.return_value = {"id": "1", "type": "Note", "properties": {"title": "Test", "content": "Content"}}

    result = notes_instance.create_note(title="Test", content="Content", tags=["tag1"])

    assert result["properties"]["title"] == "Test"
    mock_crud.create_node.assert_called_once()
    call_args, call_kwargs = mock_crud.create_node.call_args
    assert call_kwargs["db"] == mock_db_session
    assert call_kwargs["vector_store"] == mock_vector_store_instance
    assert call_kwargs["node_type"] == "Note"
    assert call_kwargs["properties"]["title"] == "Test"
    assert call_kwargs["properties"]["content"] == "Content"
    assert call_kwargs["properties"]["tags"] == ["tag1"]

def test_get_notes_no_tags(notes_instance, mock_crud, mock_db_session):
    """Test getting all notes when no tags are provided."""
    mock_crud.get_nodes.return_value = [{"id": "1", "type": "Note"}]

    result = notes_instance.get_notes()

    assert len(result) == 1
    mock_crud.get_nodes.assert_called_once_with(db=mock_db_session, node_type="Note")

def test_get_notes_with_tags(notes_instance, mock_crud, mock_db_session):
    """Test filtering notes by tags."""
    mock_crud.get_nodes.return_value = [{"id": "1", "type": "Note"}]

    notes_instance.get_notes(tags=["a", "c"])
    mock_crud.get_nodes.assert_called_once_with(db=mock_db_session, node_type="Note", tags=["a", "c"])

def test_update_note(notes_instance, mock_crud, mock_provider, mock_db_session, mock_vector_store_instance):
    """Test updating a note successfully."""
    mock_crud.update_node.return_value = {"id": "1", "properties": {"title": "New Title"}}

    result = notes_instance.update_note(note_id="1", title="New Title")

    assert result["properties"]["title"] == "New Title"
    mock_crud.update_node.assert_called_once()
    call_args, call_kwargs = mock_crud.update_node.call_args
    assert call_kwargs["db"] == mock_db_session
    assert call_kwargs["vector_store"] == mock_vector_store_instance
    assert call_kwargs["node_id"] == "1"
    assert call_kwargs["properties"] == {"title": "New Title"}

def test_update_note_no_properties(notes_instance):
    """Test that updating a note with no properties raises a ValueError."""
    with pytest.raises(ValueError, match="No properties provided to update"):
        notes_instance.update_note(note_id="1")

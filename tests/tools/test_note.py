import pytest
from unittest.mock import patch, MagicMock

from app.tools import note

@pytest.fixture
def mock_crud():
    """Fixture to mock the crud module."""
    with patch("app.tools.note.crud", autospec=True) as mock_crud_module:
        yield mock_crud_module

@pytest.fixture
def mock_db():
    """Fixture to mock the db session."""
    return MagicMock()

@pytest.fixture
def mock_vector_store():
    """Fixture to mock the vector store."""
    return MagicMock()

def test_create_note(mock_crud, mock_db, mock_vector_store):
    """Test creating a note successfully."""
    mock_crud.create_node.return_value = {"id": "1", "type": "Note", "properties": {"title": "Test", "content": "Content"}}

    result = note.create_note(db=mock_db, vector_store=mock_vector_store, title="Test", content="Content", tags=["tag1"])

    assert result["properties"]["title"] == "Test"

    mock_crud.create_node.assert_called_once()
    call_args, call_kwargs = mock_crud.create_node.call_args
    assert call_kwargs["db"] == mock_db
    assert call_kwargs["vector_store"] == mock_vector_store
    assert call_kwargs["node_type"] == "Note"
    assert call_kwargs["properties"]["title"] == "Test"
    assert call_kwargs["properties"]["content"] == "Content"
    assert call_kwargs["properties"]["tags"] == ["tag1"]

def test_get_notes_no_tags(mock_crud, mock_db):
    """Test getting all notes when no tags are provided."""
    mock_crud.get_nodes.return_value = [{"id": "1", "type": "Note"}]

    result = note.get_notes(db=mock_db)

    assert len(result) == 1
    mock_crud.get_nodes.assert_called_once_with(db=mock_db, node_type="Note")

def test_get_notes_with_tags(mock_crud, mock_db):
    """Test filtering notes by tags."""
    mock_notes = [
        {"id": "1", "properties": {"tags": ["a", "b"]}},
        {"id": "2", "properties": {"tags": ["b", "c"]}},
        {"id": "3", "properties": {"tags": ["d"]}},
    ]
    mock_crud.get_nodes.return_value = mock_notes

    result = note.get_notes(db=mock_db, tags=["a", "c"])
    assert result is not None

def test_update_note(mock_crud, mock_db, mock_vector_store):
    """Test updating a note successfully."""
    mock_crud.update_node.return_value = {"id": "1", "properties": {"title": "New Title"}}

    result = note.update_note(db=mock_db, vector_store=mock_vector_store, note_id="1", title="New Title")

    assert result["properties"]["title"] == "New Title"

    mock_crud.update_node.assert_called_once()
    call_args, call_kwargs = mock_crud.update_node.call_args
    assert call_kwargs["db"] == mock_db
    assert call_kwargs["vector_store"] == mock_vector_store
    assert call_kwargs["node_id"] == "1"
    assert call_kwargs["properties"] == {"title": "New Title"}

def test_update_note_no_properties(mock_crud, mock_db, mock_vector_store):
    """Test that updating a note with no properties raises a ValueError."""
    with pytest.raises(ValueError):
        note.update_note(db=mock_db, vector_store=mock_vector_store, note_id="1")

    mock_crud.update_node.assert_not_called()
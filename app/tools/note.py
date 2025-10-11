from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app import crud
from app.models import NoteProperties
from app.vector_store import VectorStore

def create_note(
    db: Session,
    vector_store: VectorStore,
    title: str,
    content: str,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Creates a new note with the given properties.

    Args:
        db: The SQLAlchemy database session.
        vector_store: The vector store instance.
        title: The title of the note.
        content: The markdown content of the note.
        tags: A list of tags to categorize the note.

    Returns:
        A dictionary representing the newly created note node.
    """
    properties = NoteProperties(
        title=title,
        content=content,
        tags=tags or []
    )
    return crud.create_node(db=db, vector_store=vector_store, node_type="Note", properties=properties.model_dump())

def get_notes(
    db: Session,
    tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of notes, optionally filtering by tags.

    Args:
        db: The SQLAlchemy database session.
        tags: Filter notes that have any of the specified tags.

    Returns:
        A list of note nodes that match the filter criteria.
    """
    if tags:
        return crud.get_nodes(db=db, node_type="Note", tags=tags)

    return crud.get_nodes(db=db, node_type="Note")

def update_note(
    db: Session,
    vector_store: VectorStore,
    note_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Updates the properties of an existing note.

    Args:
        db: The SQLAlchemy database session.
        vector_store: The vector store instance.
        note_id: The unique ID of the note to update.
        title: A new title for the note.
        content: New content for the note.
        tags: A new list of tags for the note.

    Returns:
        The updated note node.
    """

    properties_to_update = {
        k: v for k, v in {
            "title": title,
            "content": content,
            "tags": tags,
        }.items() if v is not None
    }

    if not properties_to_update:
        raise ValueError("No properties provided to update.")

    return crud.update_node(db=db, vector_store=vector_store, node_id=note_id, properties=properties_to_update)
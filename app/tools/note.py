from typing import List, Optional, Dict, Any
from app import crud
from app.models import NoteProperties

def create_note(
    title: str,
    content: str,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Creates a new note with the given properties.

    Args:
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
    return crud.create_node(node_type="Note", properties=properties.model_dump())

def get_notes(
    tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of notes, optionally filtering by tags.

    Args:
        tags: Filter notes that have any of the specified tags.

    Returns:
        A list of note nodes that match the filter criteria.
    """
    if tags:
        all_nodes = crud.get_nodes(node_type="Note")
        tagged_nodes = []
        for node in all_nodes:
            node_tags = node.get("properties", {}).get("tags", [])
            if any(t in node_tags for t in tags):
                tagged_nodes.append(node)
        return tagged_nodes

    return crud.get_nodes(node_type="Note")

def update_note(
    note_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Updates the properties of an existing note.

    Args:
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

    return crud.update_node(node_id=note_id, properties=properties_to_update)
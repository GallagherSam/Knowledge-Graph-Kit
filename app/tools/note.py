from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app import crud
from app.models import NoteProperties
from app.vector_store import VectorStore

class Notes:
    def __init__(self, mcp_instance, provider):
        self.provider = provider
    
        # Register tools
        mcp_instance.tool(self.create_note)
        mcp_instance.tool(self.update_note)


    def create_note(
        self,
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
        with self.provider.get_db() as db:
            return crud.create_node(db=db, vector_store=self.provider.vector_store, node_type="Note", properties=properties.model_dump())

    def update_note(
        self,
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
        with self.provider.get_db() as db:
            properties_to_update = {
                k: v for k, v in {
                    "title": title,
                    "content": content,
                    "tags": tags,
                }.items() if v is not None
            }

            if not properties_to_update:
                raise ValueError("No properties provided to update.")

            return crud.update_node(db=db, vector_store=self.provider.vector_store, node_id=note_id, properties=properties_to_update)
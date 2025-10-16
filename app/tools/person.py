from typing import List, Optional, Dict, Any
from app import crud
from app.models import PersonProperties

class Persons:
    def __init__(self, mcp_instance, provider):
        self.provider = provider
        mcp_instance.tool(self.create_person)
        mcp_instance.tool(self.update_person)

    def create_person(
        self,
        name: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Creates a new person node.

        Args:
            name: The full name of the person.
            tags: A list of tags to categorize the person.
            metadata: A dictionary for additional data like contact info or role.

        Returns:
            A dictionary representing the newly created person node.
        """
        with self.provider.get_db() as db:
            properties = PersonProperties(
                name=name,
                tags=tags or [],
                metadata=metadata or {}
            )
            return crud.create_node(
                db=db,
                vector_store=self.provider.vector_store,
                node_type="Person",
                properties=properties.model_dump()
            )

    def update_person(
        self,
        person_id: str,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Updates the properties of an existing person.

        Args:
            person_id: The unique ID of the person to update.
            name: A new name for the person.
            tags: A new list of tags for the person.
            metadata: A new metadata dictionary.

        Returns:
            The updated person node.
        """
        with self.provider.get_db() as db:
            properties_to_update = {
                k: v for k, v in {
                    "name": name,
                    "tags": tags,
                    "metadata": metadata,
                }.items() if v is not None
            }

            if not properties_to_update:
                raise ValueError("No properties provided to update.")

            return crud.update_node(
                db=db,
                vector_store=self.provider.vector_store,
                node_id=person_id,
                properties=properties_to_update
            )

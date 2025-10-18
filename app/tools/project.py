from typing import Any, Literal

from app import crud
from app.models import ProjectProperties


class Projects:
    def __init__(self, mcp_instance, provider):
        self.provider = provider
        mcp_instance.tool(self.create_project)
        mcp_instance.tool(self.update_project)

    def create_project(
        self,
        name: str,
        description: str,
        status: Literal["active", "archived"] = "active",
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Creates a new project node.

        Args:
            name: The name of the project.
            description: A description of the project.
            status: The current status of the project ('active' or 'archived').
            tags: A list of tags to categorize the project.

        Returns:
            A dictionary representing the newly created project node.
        """
        with self.provider.get_db() as db:
            properties = ProjectProperties(
                name=name, description=description, status=status, tags=tags or []
            )
            return crud.create_node(
                db=db,
                vector_store=self.provider.vector_store,
                node_type="Project",
                properties=properties.model_dump(),
            )

    def update_project(
        self,
        project_id: str,
        name: str | None = None,
        description: str | None = None,
        status: Literal["active", "archived"] | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Updates the properties of an existing project.

        Args:
            project_id: The unique ID of the project to update.
            name: A new name for the project.
            description: A new description for the project.
            status: A new status for the project.
            tags: A new list of tags for the project.

        Returns:
            The updated project node.
        """
        with self.provider.get_db() as db:
            properties_to_update = {
                k: v
                for k, v in {
                    "name": name,
                    "description": description,
                    "status": status,
                    "tags": tags,
                }.items()
                if v is not None
            }

            if not properties_to_update:
                raise ValueError("No properties provided to update.")

            return crud.update_node(
                db=db,
                vector_store=self.provider.vector_store,
                node_id=project_id,
                properties=properties_to_update,
            )

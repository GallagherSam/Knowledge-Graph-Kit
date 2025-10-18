import datetime
from typing import Any, Dict, List, Literal, Optional

from app import crud
from app.models import TaskProperties


class Tasks:
    def __init__(self, mcp_instance, provider):
        self.provider = provider
        mcp_instance.tool(self.create_task)
        mcp_instance.tool(self.update_task)
        mcp_instance.tool(self.get_tasks_by_status)

    def create_task(
        self,
        description: str,
        status: Literal['todo', 'in_progress', 'in_review', 'cancelled', 'done'] = 'todo',
        tags: Optional[List[str]] = None,
        due_date: Optional[datetime.datetime] = None,
    ) -> Dict[str, Any]:
        """
        Creates a new task with the given properties.

        Args:
            description: The main description of the task.
            status: The current status ('todo', 'in_progress', 'done', etc.).
            tags: A list of tags to categorize the task.
            due_date: An optional due date in ISO format (e.g., '2025-10-07T10:00:00').

        Returns:
            A dictionary representing the newly created task node.
        """
        with self.provider.get_db() as db:
            properties = TaskProperties(
                description=description,
                status=status,
                tags=tags or [],
                due_date=due_date
            )
            return crud.create_node(
                db=db,
                vector_store=self.provider.vector_store,
                node_type="Task",
                properties=properties.model_dump()
            )

    def update_task(
        self,
        task_id: str,
        description: Optional[str] = None,
        status: Optional[Literal['todo', 'in_progress', 'in_review', 'cancelled', 'done']] = None,
        tags: Optional[List[str]] = None,
        due_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Updates the properties of an existing task.

        Args:
            task_id: The unique ID of the task to update.
            description: A new description for the task.
            status: A new status for the task.
            tags: A new list of tags for the task.
            due_date: A new due date for the task.

        Returns:
            The updated task node.
        """
        with self.provider.get_db() as db:
            properties_to_update = {
                k: v for k, v in {
                    "description": description,
                    "status": status,
                    "tags": tags,
                    "due_date": due_date,
                }.items() if v is not None
            }

            if not properties_to_update:
                raise ValueError("No properties provided to update.")

            return crud.update_node(
                db=db,
                vector_store=self.provider.vector_store,
                node_id=task_id,
                properties=properties_to_update
            )

    def get_tasks_by_status(
        self,
        status: Literal['todo', 'in_progress', 'in_review', 'cancelled', 'done'],
    ) -> List[Dict[str, Any]]:
        """
        Retrieves tasks filtered by their status.

        Args:
            status: The status to filter by (e.g., 'todo', 'done').

        Returns:
            A list of task nodes matching the status.
        """
        with self.provider.get_db() as db:
            all_tasks = crud.search_nodes(db=db, node_type="Task")
            return [
                task for task in all_tasks
                if task.get("properties", {}).get("status") == status
            ]

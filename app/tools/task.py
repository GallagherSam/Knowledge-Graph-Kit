from typing import List, Optional, Dict, Any
from app import crud
from app.models import TaskProperties

class Tasks:
    def __init__(self, mcp_instance, provider):
        self.provider = provider
        mcp_instance.tool(self.create_task)
        mcp_instance.tool(self.get_tasks)
        mcp_instance.tool(self.update_task)

    def create_task(
        self,
        description: str,
        status: str = 'todo',
        tags: Optional[List[str]] = None,
        due_date: Optional[str] = None,
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

    def get_tasks(
        self,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves a list of tasks, optionally filtering by status or tags.

        Args:
            status: Filter tasks by their status.
            tags: Filter tasks that have any of the specified tags.

        Returns:
            A list of task nodes that match the filter criteria.
        """
        with self.provider.get_db() as db:
            if status:
                return crud.get_nodes(db=db, node_type="Task", properties={"status": status})
            if tags:
                return crud.get_nodes(db=db, node_type="Task", tags=tags)
            return crud.get_nodes(db=db, node_type="Task")

    def update_task(
        self,
        task_id: str,
        description: Optional[str] = None,
        status: Optional[str] = None,
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

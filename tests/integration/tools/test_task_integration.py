import datetime

from app.models import TaskProperties


def test_create_task_integration(tools_instance):
    """
    Integration test for the create_task tool.
    Verifies that a task is created in the database with the correct properties.
    """
    # 1. Arrange
    description = "Implement the new authentication feature."
    status = "in_progress"
    tags = ["feature", "security", "backend"]
    due_date_obj = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)

    # 2. Act
    created_task = tools_instance.tasks.create_task(
        description=description, status=status, tags=tags, due_date=due_date_obj
    )

    # 3. Assert
    assert created_task is not None
    assert "id" in created_task
    assert created_task["type"] == "Task"

    properties = created_task["properties"]
    assert properties["description"] == description
    assert properties["status"] == status
    assert properties["tags"] == tags

    # 4. Verify directly in the database
    with tools_instance.get_db() as db:
        from app.database import NodeModel

        db_node = db.query(NodeModel).filter(NodeModel.id == created_task["id"]).first()

        assert db_node is not None
        assert db_node.type == "Task"

        db_properties = db_node.properties
        assert db_properties["description"] == description
        assert db_properties["status"] == status
        assert db_properties["tags"] == tags

        # Verify Pydantic model validation
        validated_props = TaskProperties(**db_properties)
        assert validated_props.description == description


def test_update_task_integration(tools_instance):
    """
    Integration test for the update_task tool.
    Verifies that a task's properties are correctly updated in the database,
    and that unchanged properties are preserved.
    """
    # 1. Arrange: Create an initial task to be updated.
    initial_description = "Write the API documentation."
    initial_tags = ["docs", "api"]
    created_task = tools_instance.tasks.create_task(
        description=initial_description, tags=initial_tags, status="todo"
    )
    task_id = created_task["id"]

    # Define the updates
    new_status = "done"
    new_description = "Write and publish the API documentation."

    # 2. Act: Update the task with new properties.
    updated_task = tools_instance.tasks.update_task(
        task_id=task_id, description=new_description, status=new_status
    )

    # 3. Assert: Check the dictionary returned by the tool.
    assert updated_task is not None
    assert updated_task["id"] == task_id

    updated_properties = updated_task["properties"]
    assert updated_properties["description"] == new_description
    assert updated_properties["status"] == new_status
    assert updated_properties["tags"] == initial_tags  # Should remain unchanged

    # 4. Verify: Check the state directly in the database.
    with tools_instance.get_db() as db:
        from app.database import NodeModel

        db_node = db.query(NodeModel).filter(NodeModel.id == task_id).first()

        assert db_node is not None
        db_properties = db_node.properties

        assert db_properties["description"] == new_description
        assert db_properties["status"] == new_status
        assert db_properties["tags"] == initial_tags


def test_task_search_integration(tools_instance):
    """
    Integration test for the search_nodes tool, focusing on tasks.
    Verifies that the search correctly finds tasks by description and tags.
    """
    # 1. Arrange: Create a set of diverse tasks to search through.
    task1 = tools_instance.tasks.create_task(
        description="Refactor the user authentication module.", tags=["backend", "refactor"]
    )
    task2 = tools_instance.tasks.create_task(
        description="Design the new dashboard layout.", tags=["frontend", "design"]
    )

    # 2. Act & Assert: Perform various search queries.

    # Test searching by a unique description keyword
    results_auth = tools_instance.shared.search_nodes(query="authentication", node_type="Task")
    assert len(results_auth) == 1
    assert results_auth[0]["id"] == task1["id"]

    # Test searching by a shared tag
    results_design = tools_instance.shared.search_nodes(node_type="Task", tags=["design"])
    assert len(results_design) == 1
    assert results_design[0]["id"] == task2["id"]

    # Test searching with a query that matches nothing
    results_nothing = tools_instance.shared.search_nodes(query="nonexistent", node_type="Task")
    assert len(results_nothing) == 0


def test_get_tasks_by_status_integration(tools_instance):
    """
    Integration test for the get_tasks_by_status tool.
    Verifies that tasks are correctly filtered by their status property.
    """
    # 1. Arrange: Create a set of tasks with different statuses.
    task_done_1 = tools_instance.tasks.create_task(description="Completed task 1", status="done")
    tools_instance.tasks.create_task(description="A task to be done", status="todo")
    task_done_2 = tools_instance.tasks.create_task(description="Completed task 2", status="done")
    task_in_progress = tools_instance.tasks.create_task(
        description="A task currently in progress", status="in_progress"
    )

    # 2. Act: Retrieve tasks with the 'done' status.
    done_tasks = tools_instance.tasks.get_tasks_by_status(status="done")

    # 3. Assert: Verify the results for 'done' tasks.
    assert len(done_tasks) == 2
    done_task_ids = {task["id"] for task in done_tasks}
    assert {task_done_1["id"], task_done_2["id"]} == done_task_ids
    for task in done_tasks:
        assert task["properties"]["status"] == "done"

    # 4. Act & Assert: Verify for another status.
    in_progress_tasks = tools_instance.tasks.get_tasks_by_status(status="in_progress")
    assert len(in_progress_tasks) == 1
    assert in_progress_tasks[0]["id"] == task_in_progress["id"]

    # 5. Act & Assert: Verify for a status with no tasks.
    cancelled_tasks = tools_instance.tasks.get_tasks_by_status(status="cancelled")
    assert len(cancelled_tasks) == 0

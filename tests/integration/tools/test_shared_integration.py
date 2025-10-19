def test_create_edge_integration(tools_instance):
    """
    Integration test for the create_edge tool.
    Verifies that an edge is created in the database between two nodes.
    """
    # 1. Arrange: Create two nodes
    task = tools_instance.tasks.create_task(
        description="Implement feature",
        status="todo",
        tags=["backend"],
    )
    project = tools_instance.projects.create_project(
        name="Main Project",
        description="The main project",
        status="active",
    )

    # 2. Act: Create an edge between the task and project
    created_edge = tools_instance.shared.create_edge(
        source_id=task["id"],
        label="part_of",
        target_id=project["id"],
    )

    # 3. Assert: Check the returned edge
    assert created_edge is not None
    assert "id" in created_edge
    assert created_edge["source_id"] == task["id"]
    assert created_edge["target_id"] == project["id"]
    assert created_edge["label"] == "part_of"

    # 4. Verify directly in the database
    with tools_instance.get_db() as db:
        from app.database import EdgeModel

        db_edge = db.query(EdgeModel).filter(EdgeModel.id == created_edge["id"]).first()

        assert db_edge is not None
        assert db_edge.source_id == task["id"]
        assert db_edge.target_id == project["id"]
        assert db_edge.label == "part_of"


def test_edit_edge_integration(tools_instance):
    """
    Integration test for the edit_edge tool.
    Verifies that an edge's label is correctly updated in the database.
    """
    # 1. Arrange: Create two nodes and an edge between them
    task = tools_instance.tasks.create_task(
        description="Write documentation",
        status="todo",
    )
    project = tools_instance.projects.create_project(
        name="Documentation Project",
        description="Project for documentation",
        status="active",
    )
    created_edge = tools_instance.shared.create_edge(
        source_id=task["id"],
        label="part_of",
        target_id=project["id"],
    )

    # 2. Act: Update the edge label
    updated_edge = tools_instance.shared.edit_edge(
        source_id=task["id"],
        target_id=project["id"],
        old_label="part_of",
        new_label="belongs_to",
    )

    # 3. Assert: Check the returned edge
    assert updated_edge is not None
    assert updated_edge["id"] == created_edge["id"]
    assert updated_edge["source_id"] == task["id"]
    assert updated_edge["target_id"] == project["id"]
    assert updated_edge["label"] == "belongs_to"

    # 4. Verify directly in the database
    with tools_instance.get_db() as db:
        from app.database import EdgeModel

        db_edge = db.query(EdgeModel).filter(EdgeModel.id == created_edge["id"]).first()

        assert db_edge is not None
        assert db_edge.label == "belongs_to"


def test_edit_edge_not_found_integration(tools_instance):
    """
    Integration test that verifies edit_edge raises an error when the edge doesn't exist.
    """
    # 1. Arrange: Create two nodes but no edge
    task = tools_instance.tasks.create_task(description="Some task", status="todo")
    project = tools_instance.projects.create_project(
        name="Some project",
        description="A project",
        status="active",
    )

    # 2. Act & Assert: Try to edit a non-existent edge
    import pytest

    with pytest.raises(ValueError) as exc_info:
        tools_instance.shared.edit_edge(
            source_id=task["id"],
            target_id=project["id"],
            old_label="nonexistent_label",
            new_label="new_label",
        )

    assert "not found" in str(exc_info.value)


def test_get_related_nodes_with_edge_integration(tools_instance):
    """
    Integration test for get_related_nodes after creating edges.
    Verifies that related nodes can be found through their connections.
    """
    # 1. Arrange: Create a network of nodes and edges
    task1 = tools_instance.tasks.create_task(description="Task 1", status="todo")
    task2 = tools_instance.tasks.create_task(description="Task 2", status="todo")
    project = tools_instance.projects.create_project(
        name="Project",
        description="A project",
        status="active",
    )

    # Create edges
    tools_instance.shared.create_edge(
        source_id=task1["id"],
        label="part_of",
        target_id=project["id"],
    )
    tools_instance.shared.create_edge(
        source_id=task2["id"],
        label="part_of",
        target_id=project["id"],
    )

    # 2. Act: Get related nodes from the project
    related_nodes = tools_instance.shared.get_related_nodes(
        node_id=project["id"],
        label="part_of",
        depth=1,
    )

    # 3. Assert: Should find both tasks
    assert len(related_nodes) == 2
    related_ids = {node["id"] for node in related_nodes}
    assert task1["id"] in related_ids
    assert task2["id"] in related_ids


def test_delete_edge_integration(tools_instance):
    """
    Integration test for the delete_edge tool.
    Verifies that an edge is properly deleted from the database.
    """
    # 1. Arrange: Create two nodes and an edge
    task = tools_instance.tasks.create_task(description="Task", status="todo")
    project = tools_instance.projects.create_project(
        name="Project",
        description="A project",
        status="active",
    )
    created_edge = tools_instance.shared.create_edge(
        source_id=task["id"],
        label="part_of",
        target_id=project["id"],
    )

    # 2. Act: Delete the edge
    result = tools_instance.shared.delete_edge(
        source_id=task["id"],
        target_id=project["id"],
        label="part_of",
    )

    # 3. Assert: Check the result
    assert result is True

    # 4. Verify: Edge should no longer exist in the database
    with tools_instance.get_db() as db:
        from app.database import EdgeModel

        db_edge = db.query(EdgeModel).filter(EdgeModel.id == created_edge["id"]).first()
        assert db_edge is None


def test_get_node_edges_integration(tools_instance):
    """
    Integration test for the get_node_edges tool.
    Verifies that edges can be retrieved for a node with different direction filters.
    """
    # 1. Arrange: Create nodes and edges
    task = tools_instance.tasks.create_task(description="Write code", status="todo")
    project = tools_instance.projects.create_project(
        name="Software Project", description="A software project", status="active"
    )
    person = tools_instance.persons.create_person(name="Bob Smith")

    # Create edges: task -> project (outgoing), person -> task (incoming)
    edge1 = tools_instance.shared.create_edge(
        source_id=task["id"], label="part_of", target_id=project["id"]
    )
    edge2 = tools_instance.shared.create_edge(
        source_id=person["id"], label="assigned_to", target_id=task["id"]
    )

    # 2. Act & Assert: Get all edges (both directions)
    all_edges = tools_instance.shared.get_node_edges(node_id=task["id"])
    assert len(all_edges) == 2
    all_edge_ids = {edge["id"] for edge in all_edges}
    assert edge1["id"] in all_edge_ids
    assert edge2["id"] in all_edge_ids

    # 3. Act & Assert: Get only outgoing edges
    outgoing_edges = tools_instance.shared.get_node_edges(node_id=task["id"], direction="outgoing")
    assert len(outgoing_edges) == 1
    assert outgoing_edges[0]["id"] == edge1["id"]
    assert outgoing_edges[0]["label"] == "part_of"
    assert outgoing_edges[0]["source_id"] == task["id"]
    assert outgoing_edges[0]["target_id"] == project["id"]

    # 4. Act & Assert: Get only incoming edges
    incoming_edges = tools_instance.shared.get_node_edges(node_id=task["id"], direction="incoming")
    assert len(incoming_edges) == 1
    assert incoming_edges[0]["id"] == edge2["id"]
    assert incoming_edges[0]["label"] == "assigned_to"
    assert incoming_edges[0]["source_id"] == person["id"]
    assert incoming_edges[0]["target_id"] == task["id"]


def test_edge_workflow_integration(tools_instance):
    """
    Integration test for a complete workflow: create edge, edit edge, query, delete edge.
    """
    # 1. Create nodes
    note = tools_instance.notes.create_note(
        title="Meeting Notes",
        content="Notes from the team meeting",
    )
    person = tools_instance.persons.create_person(name="Alice Johnson")

    # 2. Create edge
    edge = tools_instance.shared.create_edge(
        source_id=note["id"],
        label="written_by",
        target_id=person["id"],
    )
    assert edge["label"] == "written_by"

    # 3. Use get_node_edges to see the edge information
    edges = tools_instance.shared.get_node_edges(node_id=note["id"])
    assert len(edges) == 1
    assert edges[0]["label"] == "written_by"
    assert edges[0]["source_id"] == note["id"]
    assert edges[0]["target_id"] == person["id"]

    # 4. Edit edge label
    updated_edge = tools_instance.shared.edit_edge(
        source_id=note["id"],
        target_id=person["id"],
        old_label="written_by",
        new_label="authored_by",
    )
    assert updated_edge["label"] == "authored_by"

    # 5. Query related nodes
    related = tools_instance.shared.get_related_nodes(node_id=note["id"], depth=1)
    assert len(related) == 1
    assert related[0]["id"] == person["id"]

    # 6. Verify edge label was updated
    edges_after = tools_instance.shared.get_node_edges(node_id=note["id"])
    assert len(edges_after) == 1
    assert edges_after[0]["label"] == "authored_by"

    # 7. Delete edge
    result = tools_instance.shared.delete_edge(
        source_id=note["id"],
        target_id=person["id"],
        label="authored_by",
    )
    assert result is True

    # 8. Verify no more relations
    related_after = tools_instance.shared.get_related_nodes(node_id=note["id"], depth=1)
    assert len(related_after) == 0

    # 9. Verify no more edges
    edges_final = tools_instance.shared.get_node_edges(node_id=note["id"])
    assert len(edges_final) == 0

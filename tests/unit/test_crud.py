from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import crud
from app.database import Base


@pytest.fixture
def db_session():
    """Fixture to create a new database session for each test."""
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def mock_vector_store():
    """Fixture to mock the vector store."""
    return MagicMock()


def test_create_node_success(db_session, mock_vector_store):
    """Test successful creation of a node."""
    properties = {"description": "Test Task", "status": "todo", "due_date": None, "tags": []}
    new_node = crud.create_node(
        db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties
    )

    assert new_node["type"] == "Task"
    assert new_node["properties"]["description"] == "Test Task"
    mock_vector_store.add_node.assert_called_once()


def test_create_node_invalid_properties(db_session, mock_vector_store):
    """Test creating a node with invalid properties raises ValidationError."""
    with pytest.raises(ValidationError):
        crud.create_node(
            db=db_session,
            vector_store=mock_vector_store,
            node_type="Task",
            properties={"invalid_prop": "value"},
        )


def test_get_nodes_no_filter(db_session, mock_vector_store):
    """Test retrieving all nodes without any filters."""
    properties = {"description": "Test Task", "status": "todo", "due_date": None, "tags": []}
    crud.create_node(
        db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties
    )

    nodes = crud.get_nodes(db=db_session)
    assert len(nodes) == 1


def test_get_nodes_by_type(db_session, mock_vector_store):
    """Test filtering nodes by type."""
    properties_task = {"description": "Test Task", "status": "todo", "due_date": None, "tags": []}
    crud.create_node(
        db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties_task
    )
    properties_note = {"title": "Test Note", "content": "Test content", "tags": []}
    crud.create_node(
        db=db_session, vector_store=mock_vector_store, node_type="Note", properties=properties_note
    )

    nodes = crud.get_nodes(db=db_session, node_type="Task")
    assert len(nodes) == 1
    assert nodes[0]["type"] == "Task"


def test_get_nodes_by_property(db_session, mock_vector_store):
    """Test filtering nodes by a specific property."""
    properties1 = {"description": "Test Task 1", "status": "done", "due_date": None, "tags": []}
    crud.create_node(
        db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties1
    )
    properties2 = {"description": "Test Task 2", "status": "todo", "due_date": None, "tags": []}
    crud.create_node(
        db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties2
    )

    nodes = crud.get_nodes(db=db_session, node_type="Task", status="done")
    assert len(nodes) == 1
    assert nodes[0]["properties"]["status"] == "done"


def test_update_node_success(db_session, mock_vector_store):
    """Test successfully updating a node."""
    properties = {"title": "Old", "content": "Content", "tags": []}
    created_node = crud.create_node(
        db=db_session, vector_store=mock_vector_store, node_type="Note", properties=properties
    )

    updated_node = crud.update_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_id=created_node["id"],
        properties={"title": "New"},
    )
    assert updated_node["properties"]["title"] == "New"
    mock_vector_store.update_node.assert_called_once()


def test_update_node_not_found(db_session, mock_vector_store):
    """Test that updating a non-existent node raises an exception."""
    with pytest.raises(ValueError) as exc_info:
        crud.update_node(
            db=db_session, vector_store=mock_vector_store, node_id="1", properties={"title": "New"}
        )
    assert "not found" in str(exc_info.value)


def test_delete_node_success(db_session, mock_vector_store):
    """Test successful deletion of a node."""
    properties = {"description": "Test Task", "status": "todo", "due_date": None, "tags": []}
    created_node = crud.create_node(
        db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties
    )

    crud.delete_node(db=db_session, vector_store=mock_vector_store, node_id=created_node["id"])
    mock_vector_store.delete_node.assert_called_once_with(created_node["id"])


def test_create_edge_success(db_session, mock_vector_store):
    """Test successful creation of an edge."""
    properties1 = {"description": "Test Task", "status": "todo", "due_date": None, "tags": []}
    node1 = crud.create_node(
        db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties1
    )
    properties2 = {
        "name": "Test Project",
        "description": "A test project.",
        "status": "active",
        "tags": [],
    }
    node2 = crud.create_node(
        db=db_session, vector_store=mock_vector_store, node_type="Project", properties=properties2
    )

    new_edge = crud.create_edge(
        db=db_session, source_id=node1["id"], target_id=node2["id"], label="part_of"
    )
    assert new_edge["source_id"] == node1["id"]
    assert new_edge["target_id"] == node2["id"]


def test_create_edge_node_not_found(db_session):
    """Test creating an edge with a non-existent source or target node."""
    with pytest.raises(ValueError) as exc_info:
        crud.create_edge(db=db_session, source_id="1", target_id="2", label="part_of")
    assert "not found" in str(exc_info.value)


def test_update_edge_success(db_session, mock_vector_store):
    """Test successfully updating an edge's label."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Test Task", "status": "todo", "due_date": None, "tags": []},
    )
    node2 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Project",
        properties={
            "name": "Test Project",
            "description": "A test project.",
            "status": "active",
            "tags": [],
        },
    )
    edge = crud.create_edge(
        db=db_session, source_id=node1["id"], target_id=node2["id"], label="part_of"
    )

    updated_edge = crud.update_edge(
        db=db_session,
        source_id=node1["id"],
        target_id=node2["id"],
        old_label="part_of",
        new_label="belongs_to",
    )

    assert updated_edge["id"] == edge["id"]
    assert updated_edge["label"] == "belongs_to"
    assert updated_edge["source_id"] == node1["id"]
    assert updated_edge["target_id"] == node2["id"]


def test_update_edge_not_found(db_session, mock_vector_store):
    """Test updating a non-existent edge raises ValueError."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Test Task", "status": "todo", "due_date": None, "tags": []},
    )
    node2 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Project",
        properties={
            "name": "Test Project",
            "description": "A test project.",
            "status": "active",
            "tags": [],
        },
    )

    with pytest.raises(ValueError) as exc_info:
        crud.update_edge(
            db=db_session,
            source_id=node1["id"],
            target_id=node2["id"],
            old_label="nonexistent_label",
            new_label="new_label",
        )
    assert "not found" in str(exc_info.value)


def test_get_node_edges_all_directions(db_session, mock_vector_store):
    """Test getting all edges connected to a node in both directions."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task 1", "status": "todo", "tags": []},
    )
    node2 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task 2", "status": "todo", "tags": []},
    )
    node3 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Project",
        properties={"name": "Project", "description": "Desc", "status": "active", "tags": []},
    )

    # Create edges: node1 -> node2, node3 -> node1
    edge1 = crud.create_edge(
        db=db_session, source_id=node1["id"], target_id=node2["id"], label="next"
    )
    edge2 = crud.create_edge(
        db=db_session, source_id=node3["id"], target_id=node1["id"], label="contains"
    )

    # Get all edges for node1 (both incoming and outgoing)
    edges = crud.get_node_edges(db=db_session, node_id=node1["id"])

    assert len(edges) == 2
    edge_ids = {edge["id"] for edge in edges}
    assert edge1["id"] in edge_ids
    assert edge2["id"] in edge_ids


def test_get_node_edges_outgoing_only(db_session, mock_vector_store):
    """Test getting only outgoing edges from a node."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task 1", "status": "todo", "tags": []},
    )
    node2 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task 2", "status": "todo", "tags": []},
    )
    node3 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Project",
        properties={"name": "Project", "description": "Desc", "status": "active", "tags": []},
    )

    # Create edges: node1 -> node2, node3 -> node1
    edge1 = crud.create_edge(
        db=db_session, source_id=node1["id"], target_id=node2["id"], label="next"
    )
    crud.create_edge(db=db_session, source_id=node3["id"], target_id=node1["id"], label="contains")

    # Get only outgoing edges for node1
    edges = crud.get_node_edges(db=db_session, node_id=node1["id"], direction="outgoing")

    assert len(edges) == 1
    assert edges[0]["id"] == edge1["id"]
    assert edges[0]["source_id"] == node1["id"]
    assert edges[0]["target_id"] == node2["id"]
    assert edges[0]["label"] == "next"


def test_get_node_edges_incoming_only(db_session, mock_vector_store):
    """Test getting only incoming edges to a node."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task 1", "status": "todo", "tags": []},
    )
    node2 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task 2", "status": "todo", "tags": []},
    )
    node3 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Project",
        properties={"name": "Project", "description": "Desc", "status": "active", "tags": []},
    )

    # Create edges: node1 -> node2, node3 -> node1
    crud.create_edge(db=db_session, source_id=node1["id"], target_id=node2["id"], label="next")
    edge2 = crud.create_edge(
        db=db_session, source_id=node3["id"], target_id=node1["id"], label="contains"
    )

    # Get only incoming edges for node1
    edges = crud.get_node_edges(db=db_session, node_id=node1["id"], direction="incoming")

    assert len(edges) == 1
    assert edges[0]["id"] == edge2["id"]
    assert edges[0]["source_id"] == node3["id"]
    assert edges[0]["target_id"] == node1["id"]
    assert edges[0]["label"] == "contains"


def test_get_node_edges_no_edges(db_session, mock_vector_store):
    """Test getting edges for a node with no connections."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Isolated task", "status": "todo", "tags": []},
    )

    edges = crud.get_node_edges(db=db_session, node_id=node1["id"])
    assert len(edges) == 0


def test_get_connected_nodes(db_session, mock_vector_store):
    """Test retrieving connected nodes."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Test Task", "status": "todo", "due_date": None, "tags": []},
    )
    node2 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Project",
        properties={
            "name": "Test Project",
            "description": "A test project.",
            "status": "active",
            "tags": [],
        },
    )
    node3 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Person",
        properties={"name": "Test Person", "tags": [], "metadata": {}},
    )
    crud.create_edge(db=db_session, source_id=node1["id"], target_id=node2["id"], label="part_of")
    crud.create_edge(
        db=db_session, source_id=node3["id"], target_id=node1["id"], label="assigned_to"
    )

    connected = crud.get_connected_nodes(db=db_session, node_id=node1["id"])
    assert len(connected) == 2
    connected_ids = {node["id"] for node in connected}
    assert node2["id"] in connected_ids
    assert node3["id"] in connected_ids


def test_search_nodes(db_session, mock_vector_store):
    """Test searching for nodes with various criteria."""
    crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Note",
        properties={"title": "My Note", "content": "About cats", "tags": ["personal"]},
    )
    crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={
            "description": "A task about dogs",
            "status": "todo",
            "due_date": None,
            "tags": ["work"],
        },
    )

    # Test search by query
    results = crud.search_nodes(db=db_session, query="cats")
    assert len(results) == 1
    assert results[0]["properties"]["content"] == "About cats"

    # Test search by type
    results = crud.search_nodes(db=db_session, node_type="Task")
    assert len(results) == 1
    assert results[0]["type"] == "Task"

    # Test search by tags
    results = crud.search_nodes(db=db_session, tags=["work"])
    assert len(results) == 1
    assert results[0]["properties"]["tags"] == ["work"]


def test_get_all_tags(db_session, mock_vector_store):
    """Test retrieving all unique, sorted tags."""
    crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Note",
        properties={"title": "Note 1", "content": "c1", "tags": ["work", "urgent"]},
    )
    crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={
            "description": "Task 1",
            "status": "todo",
            "due_date": None,
            "tags": ["personal"],
        },
    )
    crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Project",
        properties={
            "name": "p1",
            "description": "d1",
            "status": "active",
            "tags": ["work", "review"],
        },
    )

    tags = crud.get_all_tags(db=db_session)
    assert tags == ["personal", "review", "urgent", "work"]


def test_delete_edge_by_nodes_success(db_session, mock_vector_store):
    """Test successful deletion of an edge by source, target, and label."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Test Task", "status": "todo", "due_date": None, "tags": []},
    )
    node2 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Project",
        properties={
            "name": "Test Project",
            "description": "A test project.",
            "status": "active",
            "tags": [],
        },
    )
    crud.create_edge(db=db_session, source_id=node1["id"], target_id=node2["id"], label="part_of")

    result = crud.delete_edge_by_nodes(
        db=db_session, source_id=node1["id"], target_id=node2["id"], label="part_of"
    )
    assert result is True


def test_delete_edge_by_nodes_not_found(db_session):
    """Test that trying to delete a non-existent edge by nodes fails."""
    result = crud.delete_edge_by_nodes(db=db_session, source_id="1", target_id="2", label="part_of")
    assert result is False


def test_rename_tag_success(db_session, mock_vector_store):
    """Test successfully renaming a tag on multiple nodes."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Note",
        properties={"title": "Note 1", "content": "c1", "tags": ["old_tag", "other"]},
    )
    crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={
            "description": "Task 1",
            "status": "todo",
            "due_date": None,
            "tags": ["old_tag"],
        },
    )
    crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Project",
        properties={"name": "p1", "description": "d1", "status": "active", "tags": ["another_tag"]},
    )

    updated_nodes = crud.rename_tag(db=db_session, old_tag="old_tag", new_tag="new_tag")
    assert len(updated_nodes) == 2

    # Check the call for the first node
    updated_node1 = crud.get_nodes_by_ids(db=db_session, node_ids=[node1["id"]])[0]
    assert sorted(updated_node1["properties"]["tags"]) == ["new_tag", "other"]


def test_get_nodes_by_ids(db_session, mock_vector_store):
    """Test retrieving nodes by a list of IDs."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task 1", "status": "todo", "tags": []},
    )
    node2 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Note",
        properties={"title": "Note 1", "content": "Content", "tags": []},
    )

    # Test retrieving both
    nodes = crud.get_nodes_by_ids(db=db_session, node_ids=[node1["id"], node2["id"]])
    assert len(nodes) == 2
    assert {n["id"] for n in nodes} == {node1["id"], node2["id"]}

    # Test retrieving one
    nodes = crud.get_nodes_by_ids(db=db_session, node_ids=[node1["id"]])
    assert len(nodes) == 1

    # Test with non-existent ID
    nodes = crud.get_nodes_by_ids(db=db_session, node_ids=["nonexistent"])
    assert len(nodes) == 0


def test_update_node_invalid_merge(db_session, mock_vector_store):
    """Test that updating a node with invalid merged properties raises ValidationError."""
    # Create a task with valid status
    created_node = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Test", "status": "todo", "tags": []},
    )

    # Try to update with an invalid status (merged properties will be invalid)
    with pytest.raises(ValidationError):
        crud.update_node(
            db=db_session,
            vector_store=mock_vector_store,
            node_id=created_node["id"],
            properties={"status": "invalid_status"},
        )


def test_delete_node_cascades_edges(db_session, mock_vector_store):
    """Test that deleting a node also deletes its connected edges."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task", "status": "todo", "tags": []},
    )
    node2 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Project",
        properties={"name": "Project", "description": "Desc", "status": "active", "tags": []},
    )

    edge = crud.create_edge(
        db=db_session, source_id=node1["id"], target_id=node2["id"], label="part_of"
    )

    # Delete node1
    crud.delete_node(db=db_session, vector_store=mock_vector_store, node_id=node1["id"])

    # Verify edge is also deleted
    from app.database import EdgeModel

    remaining_edge = db_session.query(EdgeModel).filter(EdgeModel.id == edge["id"]).first()
    assert remaining_edge is None


def test_get_connected_nodes_with_depth(db_session, mock_vector_store):
    """Test graph traversal with different depths."""
    # Create chain: node1 -> node2 -> node3
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task 1", "status": "todo", "tags": []},
    )
    node2 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task 2", "status": "todo", "tags": []},
    )
    node3 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task 3", "status": "todo", "tags": []},
    )

    crud.create_edge(db=db_session, source_id=node1["id"], target_id=node2["id"], label="next")
    crud.create_edge(db=db_session, source_id=node2["id"], target_id=node3["id"], label="next")

    # Depth 1: should only find node2
    connected = crud.get_connected_nodes(db=db_session, node_id=node1["id"], depth=1)
    assert len(connected) == 1
    assert connected[0]["id"] == node2["id"]

    # Depth 2: should find node2 and node3
    connected = crud.get_connected_nodes(db=db_session, node_id=node1["id"], depth=2)
    assert len(connected) == 2
    assert {n["id"] for n in connected} == {node2["id"], node3["id"]}

    # Depth 0: should find nothing
    connected = crud.get_connected_nodes(db=db_session, node_id=node1["id"], depth=0)
    assert len(connected) == 0


def test_get_connected_nodes_with_label_filter(db_session, mock_vector_store):
    """Test that label filtering works in graph traversal."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task", "status": "todo", "tags": []},
    )
    node2 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Project",
        properties={"name": "Project", "description": "Desc", "status": "active", "tags": []},
    )
    node3 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Person",
        properties={"name": "Person", "tags": [], "metadata": {}},
    )

    crud.create_edge(db=db_session, source_id=node1["id"], target_id=node2["id"], label="part_of")
    crud.create_edge(
        db=db_session, source_id=node1["id"], target_id=node3["id"], label="assigned_to"
    )

    # Filter by "part_of" label
    connected = crud.get_connected_nodes(db=db_session, node_id=node1["id"], label="part_of")
    assert len(connected) == 1
    assert connected[0]["id"] == node2["id"]

    # Filter by "assigned_to" label
    connected = crud.get_connected_nodes(db=db_session, node_id=node1["id"], label="assigned_to")
    assert len(connected) == 1
    assert connected[0]["id"] == node3["id"]


def test_search_nodes_combined_filters(db_session, mock_vector_store):
    """Test searching with combined query, type, and tags filters."""
    crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Note",
        properties={"title": "Apple Note", "content": "About apples", "tags": ["fruit", "food"]},
    )
    crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Note",
        properties={"title": "Banana Note", "content": "About bananas", "tags": ["fruit"]},
    )
    crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Buy apples", "status": "todo", "tags": ["food"]},
    )

    # Search for "apple" in Notes with "fruit" tag
    results = crud.search_nodes(db=db_session, query="apple", node_type="Note", tags=["fruit"])
    assert len(results) == 1
    assert "Apple" in results[0]["properties"]["title"]

    # Search for "apple" with "food" tag (should match both Note and Task)
    results = crud.search_nodes(db=db_session, query="apple", tags=["food"])
    assert len(results) == 2


def test_rename_tag_with_duplicates(db_session, mock_vector_store):
    """Test that renaming a tag removes duplicates if new_tag already exists."""
    crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Note",
        properties={"title": "Note", "content": "Content", "tags": ["old_tag", "existing_tag"]},
    )

    # Rename old_tag to existing_tag (should result in single "existing_tag")
    updated_nodes = crud.rename_tag(db=db_session, old_tag="old_tag", new_tag="existing_tag")

    assert len(updated_nodes) == 1
    # Should have deduplicated tags
    assert updated_nodes[0]["properties"]["tags"] == ["existing_tag"]


def test_search_nodes_case_insensitive(db_session, mock_vector_store):
    """Test that search is case-insensitive."""
    crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Note",
        properties={"title": "UPPERCASE", "content": "Content", "tags": []},
    )

    # Search with lowercase should still find it
    results = crud.search_nodes(db=db_session, query="uppercase")
    assert len(results) == 1

    results = crud.search_nodes(db=db_session, query="UPPERCASE")
    assert len(results) == 1

    results = crud.search_nodes(db=db_session, query="UpperCase")
    assert len(results) == 1


def test_get_connected_nodes_prevents_cycles(db_session, mock_vector_store):
    """Test that BFS doesn't infinitely loop on cycles."""
    node1 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task 1", "status": "todo", "tags": []},
    )
    node2 = crud.create_node(
        db=db_session,
        vector_store=mock_vector_store,
        node_type="Task",
        properties={"description": "Task 2", "status": "todo", "tags": []},
    )

    # Create a cycle: node1 -> node2 -> node1
    crud.create_edge(db=db_session, source_id=node1["id"], target_id=node2["id"], label="next")
    crud.create_edge(db=db_session, source_id=node2["id"], target_id=node1["id"], label="prev")

    # Should not hang and should return only node2
    connected = crud.get_connected_nodes(db=db_session, node_id=node1["id"], depth=5)
    assert len(connected) == 1
    assert connected[0]["id"] == node2["id"]

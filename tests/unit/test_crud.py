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
    new_node = crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties)

    assert new_node["type"] == "Task"
    assert new_node["properties"]["description"] == "Test Task"
    mock_vector_store.add_node.assert_called_once()

def test_create_node_invalid_properties(db_session, mock_vector_store):
    """Test creating a node with invalid properties raises ValidationError."""
    with pytest.raises(ValidationError):
        crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties={"invalid_prop": "value"})

def test_get_nodes_no_filter(db_session, mock_vector_store):
    """Test retrieving all nodes without any filters."""
    properties = {"description": "Test Task", "status": "todo", "due_date": None, "tags": []}
    crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties)

    nodes = crud.get_nodes(db=db_session)
    assert len(nodes) == 1

def test_get_nodes_by_type(db_session, mock_vector_store):
    """Test filtering nodes by type."""
    properties_task = {"description": "Test Task", "status": "todo", "due_date": None, "tags": []}
    crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties_task)
    properties_note = {"title": "Test Note", "content": "Test content", "tags": []}
    crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Note", properties=properties_note)

    nodes = crud.get_nodes(db=db_session, node_type="Task")
    assert len(nodes) == 1
    assert nodes[0]["type"] == "Task"

def test_get_nodes_by_property(db_session, mock_vector_store):
    """Test filtering nodes by a specific property."""
    properties1 = {"description": "Test Task 1", "status": "done", "due_date": None, "tags": []}
    crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties1)
    properties2 = {"description": "Test Task 2", "status": "todo", "due_date": None, "tags": []}
    crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties2)

    nodes = crud.get_nodes(db=db_session, node_type="Task", status="done")
    assert len(nodes) == 1
    assert nodes[0]["properties"]["status"] == "done"

def test_update_node_success(db_session, mock_vector_store):
    """Test successfully updating a node."""
    properties = {"title": "Old", "content": "Content", "tags": []}
    created_node = crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Note", properties=properties)

    updated_node = crud.update_node(db=db_session, vector_store=mock_vector_store, node_id=created_node["id"], properties={"title": "New"})
    assert updated_node["properties"]["title"] == "New"
    mock_vector_store.update_node.assert_called_once()

def test_update_node_not_found(db_session, mock_vector_store):
    """Test that updating a non-existent node raises an exception."""
    with pytest.raises(ValueError) as exc_info:
        crud.update_node(db=db_session, vector_store=mock_vector_store, node_id="1", properties={"title": "New"})
    assert "not found" in str(exc_info.value)

def test_delete_node_success(db_session, mock_vector_store):
    """Test successful deletion of a node."""
    properties = {"description": "Test Task", "status": "todo", "due_date": None, "tags": []}
    created_node = crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties)

    crud.delete_node(db=db_session, vector_store=mock_vector_store, node_id=created_node["id"])
    mock_vector_store.delete_node.assert_called_once_with(created_node["id"])

def test_create_edge_success(db_session, mock_vector_store):
    """Test successful creation of an edge."""
    properties1 = {"description": "Test Task", "status": "todo", "due_date": None, "tags": []}
    node1 = crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties=properties1)
    properties2 = {"name": "Test Project", "description": "A test project.", "status": "active", "tags": []}
    node2 = crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Project", properties=properties2)

    new_edge = crud.create_edge(db=db_session, source_id=node1["id"], target_id=node2["id"], label="part_of")
    assert new_edge["source_id"] == node1["id"]
    assert new_edge["target_id"] == node2["id"]

def test_delete_edge_success(db_session):
    """Test successful deletion of an edge."""
    # This test is not valid anymore as we don't have a direct `delete_edge` by id in the crud module
    pass

def test_create_edge_node_not_found(db_session):
    """Test creating an edge with a non-existent source or target node."""
    with pytest.raises(ValueError) as exc_info:
        crud.create_edge(db=db_session, source_id="1", target_id="2", label="part_of")
    assert "not found" in str(exc_info.value)

def test_get_connected_nodes(db_session, mock_vector_store):
    """Test retrieving connected nodes."""
    node1 = crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties={"description": "Test Task", "status": "todo", "due_date": None, "tags": []})
    node2 = crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Project", properties={"name": "Test Project", "description": "A test project.", "status": "active", "tags": []})
    node3 = crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Person", properties={"name": "Test Person", "tags": [], "metadata": {}})
    crud.create_edge(db=db_session, source_id=node1["id"], target_id=node2["id"], label="part_of")
    crud.create_edge(db=db_session, source_id=node3["id"], target_id=node1["id"], label="assigned_to")

    connected = crud.get_connected_nodes(db=db_session, node_id=node1["id"])
    assert len(connected) == 2
    connected_ids = {node["id"] for node in connected}
    assert node2["id"] in connected_ids
    assert node3["id"] in connected_ids

def test_search_nodes(db_session, mock_vector_store):
    """Test searching for nodes with various criteria."""
    crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Note", properties={"title": "My Note", "content": "About cats", "tags": ["personal"]})
    crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties={"description": "A task about dogs", "status": "todo", "due_date": None, "tags": ["work"]})

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
    crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Note", properties={"title": "Note 1", "content": "c1", "tags": ["work", "urgent"]})
    crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties={"description": "Task 1", "status": "todo", "due_date": None, "tags": ["personal"]})
    crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Project", properties={"name": "p1", "description": "d1", "status": "active", "tags": ["work", "review"]})

    tags = crud.get_all_tags(db=db_session)
    assert tags == ["personal", "review", "urgent", "work"]

def test_delete_edge_by_nodes_success(db_session, mock_vector_store):
    """Test successful deletion of an edge by source, target, and label."""
    node1 = crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties={"description": "Test Task", "status": "todo", "due_date": None, "tags": []})
    node2 = crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Project", properties={"name": "Test Project", "description": "A test project.", "status": "active", "tags": []})
    crud.create_edge(db=db_session, source_id=node1["id"], target_id=node2["id"], label="part_of")

    result = crud.delete_edge_by_nodes(db=db_session, source_id=node1["id"], target_id=node2["id"], label="part_of")
    assert result is True

def test_delete_edge_by_nodes_not_found(db_session):
    """Test that trying to delete a non-existent edge by nodes fails."""
    result = crud.delete_edge_by_nodes(db=db_session, source_id="1", target_id="2", label="part_of")
    assert result is False

def test_rename_tag_success(db_session, mock_vector_store):
    """Test successfully renaming a tag on multiple nodes."""
    node1 = crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Note", properties={"title": "Note 1", "content": "c1", "tags": ["old_tag", "other"]})
    crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Task", properties={"description": "Task 1", "status": "todo", "due_date": None, "tags": ["old_tag"]})
    crud.create_node(db=db_session, vector_store=mock_vector_store, node_type="Project", properties={"name": "p1", "description": "d1", "status": "active", "tags": ["another_tag"]})

    updated_nodes = crud.rename_tag(db=db_session, old_tag="old_tag", new_tag="new_tag")
    assert len(updated_nodes) == 2

    # Check the call for the first node
    updated_node1 = crud.get_nodes_by_ids(db=db_session, node_ids=[node1["id"]])[0]
    assert sorted(updated_node1["properties"]["tags"]) == ["new_tag", "other"]
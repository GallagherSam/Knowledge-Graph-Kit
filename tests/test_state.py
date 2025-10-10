import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.state import State

@pytest.fixture
def state_manager(monkeypatch):
    """Fixture to create a State instance with an in-memory SQLite database."""
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    # Monkeypatch the session local in the state module to use the in-memory database
    monkeypatch.setattr("app.state.SessionLocal", TestingSessionLocal)

    state = State()
    yield state

    Base.metadata.drop_all(bind=engine)

def test_initialize_state(state_manager):
    """Test that the database tables are created on initialization."""
    with state_manager._db_session() as db:
        assert "nodes" in Base.metadata.tables
        assert "edges" in Base.metadata.tables

def test_add_and_read_nodes(state_manager):
    """Test adding and reading nodes from the database."""
    node_data = {"id": "1", "type": "Task", "properties": {"description": "Test"}}
    created_node = state_manager.add_node(node_data)

    assert created_node["id"] == "1"

    nodes = state_manager.read_nodes()
    assert len(nodes) == 1
    assert nodes[0]["id"] == "1"
    assert nodes[0]["type"] == "Task"
    assert nodes[0]["properties"]["description"] == "Test"

def test_update_node(state_manager):
    """Test updating a node in the database."""
    node_data = {"id": "1", "type": "Task", "properties": {"description": "Old"}}
    state_manager.add_node(node_data)

    updated_node = state_manager.update_node_in_db("1", {"description": "New"})

    assert updated_node["properties"]["description"] == "New"

    nodes = state_manager.read_nodes()
    assert len(nodes) == 1
    assert nodes[0]["properties"]["description"] == "New"

def test_delete_node(state_manager):
    """Test deleting a node and its connected edges."""
    node1 = {"id": "1", "type": "Task", "properties": {}}
    node2 = {"id": "2", "type": "Project", "properties": {}}
    state_manager.add_node(node1)
    state_manager.add_node(node2)
    edge1 = {"id": "e1", "source_id": "1", "target_id": "2", "label": "connects"}
    state_manager.add_edge(edge1)

    result = state_manager.delete_node("1")
    assert result is True

    nodes = state_manager.read_nodes()
    assert len(nodes) == 1

    edges = state_manager.read_edges()
    assert len(edges) == 0

def test_delete_edge(state_manager):
    """Test deleting an edge from the database."""
    node1 = {"id": "1", "type": "Task", "properties": {}}
    node2 = {"id": "2", "type": "Project", "properties": {}}
    state_manager.add_node(node1)
    state_manager.add_node(node2)
    edge_data = {"id": "e1", "source_id": "1", "target_id": "2", "label": "connects"}
    state_manager.add_edge(edge_data)

    result = state_manager.delete_edge("e1")
    assert result is True

    edges = state_manager.read_edges()
    assert len(edges) == 0

def test_add_and_read_edges(state_manager):
    """Test adding and reading edges from the database."""
    node1 = {"id": "1", "type": "Task", "properties": {}}
    node2 = {"id": "2", "type": "Project", "properties": {}}
    state_manager.add_node(node1)
    state_manager.add_node(node2)

    edge_data = {"id": "e1", "source_id": "1", "target_id": "2", "label": "connects"}
    created_edge = state_manager.add_edge(edge_data)

    assert created_edge["id"] == "e1"

    edges = state_manager.read_edges()
    assert len(edges) == 1
    assert edges[0]["id"] == "e1"
    assert edges[0]["source_id"] == "1"
    assert edges[0]["target_id"] == "2"
    assert edges[0]["label"] == "connects"

def test_read_nodes_empty(state_manager):
    """Test reading nodes when the table is empty."""
    nodes = state_manager.read_nodes()
    assert nodes == []

def test_read_edges_empty(state_manager):
    """Test reading edges when the table is empty."""
    edges = state_manager.read_edges()
    assert edges == []
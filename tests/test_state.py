import json
import pytest
from app.state import State

@pytest.fixture
def state_manager(tmp_path, monkeypatch):
    """Fixture to create a State instance with a temporary data directory."""
    data_dir = tmp_path / "data"
    nodes_file = data_dir / "nodes.json"
    edges_file = data_dir / "edges.json"

    # Monkeypatch the file paths in the state module
    monkeypatch.setattr("app.state.DATA_DIR", data_dir)
    monkeypatch.setattr("app.state.NODES_FILE", nodes_file)
    monkeypatch.setattr("app.state.EDGES_FILE", edges_file)

    yield State()

def test_initialize_state(state_manager, tmp_path):
    """Test that the data directory and files are created on initialization."""
    data_dir = tmp_path / "data"
    assert data_dir.exists()
    nodes_file = data_dir / "nodes.json"
    edges_file = data_dir / "edges.json"
    assert nodes_file.exists()
    assert edges_file.exists()

    with open(nodes_file, "r") as f:
        assert json.load(f) == []
    with open(edges_file, "r") as f:
        assert json.load(f) == []

def test_write_and_read_nodes(state_manager):
    """Test writing to and reading from the nodes file."""
    nodes_data = [{"id": "1", "type": "Task", "properties": {}}]
    state_manager.write_nodes(nodes_data)
    read_data = state_manager.read_nodes()
    assert read_data == nodes_data

def test_write_and_read_edges(state_manager):
    """Test writing to and reading from the edges file."""
    edges_data = [{"source_id": "1", "target_id": "2", "label": "connects"}]
    state_manager.write_edges(edges_data)
    read_data = state_manager.read_edges()
    assert read_data == edges_data

def test_read_nodes_empty(state_manager):
    """Test reading the nodes file when it's empty."""
    read_data = state_manager.read_nodes()
    assert read_data == []

def test_read_edges_empty(state_manager):
    """Test reading the edges file when it's empty."""
    read_data = state_manager.read_edges()
    assert read_data == []
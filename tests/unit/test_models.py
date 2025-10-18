import pytest
from pydantic import ValidationError

from app.models import (
    Edge,
    Node,
    NoteProperties,
    PersonProperties,
    ProjectProperties,
    TaskProperties,
)


def test_node_creation():
    """Test creating a Node with valid data."""
    node = Node(type="Task", properties={"description": "Test task"})
    assert node.id is not None
    assert node.type == "Task"
    assert node.properties == {"description": "Test task"}

def test_task_properties_creation():
    """Test creating TaskProperties with valid data."""
    properties = TaskProperties(description="A new task")
    assert properties.description == "A new task"
    assert properties.status == "todo"
    assert properties.tags == []
    assert properties.due_date is None

def test_task_properties_invalid_status():
    """Test that an invalid status raises a validation error."""
    with pytest.raises(ValidationError):
        TaskProperties(description="Invalid task", status="invalid_status")

def test_note_properties_creation():
    """Test creating NoteProperties with valid data."""
    properties = NoteProperties(title="Test Note", content="This is a test.")
    assert properties.title == "Test Note"
    assert properties.content == "This is a test."
    assert properties.tags == []

def test_person_properties_creation():
    """Test creating PersonProperties with valid data."""
    properties = PersonProperties(name="John Doe")
    assert properties.name == "John Doe"
    assert properties.tags == []
    assert properties.metadata == {}

def test_project_properties_creation():
    """Test creating ProjectProperties with valid data."""
    properties = ProjectProperties(name="New Project", description="A test project.")
    assert properties.name == "New Project"
    assert properties.description == "A test project."
    assert properties.status == "active"
    assert properties.tags == []

def test_project_properties_invalid_status():
    """Test that an invalid status for a project raises a validation error."""
    with pytest.raises(ValidationError):
        ProjectProperties(
            name="Invalid Project",
            description="Test",
            status="invalid_status",
        )

def test_edge_creation():
    """Test creating an Edge with valid data."""
    edge = Edge(source_id="123", target_id="456", label="connects_to")
    assert edge.source_id == "123"
    assert edge.target_id == "456"
    assert edge.label == "connects_to"